import os
import subprocess

from flask import Blueprint, current_app, render_template, request, flash, url_for, redirect, send_from_directory, session
from flask_login import login_required, current_user

from .automation_script import overlay  # Import the function

views = Blueprint('views', __name__)
DOWNLOAD_FOLDER = os.path.join('website', 'static', 'downloads')  # Define the download folder


@views.route('/downloads/<filename>')
def download_file(filename, directory):
    """
    Sends file contents from requested directory

    Parameters:
        filename: the name of teh file we are trying to get
        directory: the name of the director ythe file is in

    Returns:
        file we are getting
    """
    try:
        #directly sends file contents from requested directory (no URL)
        return send_from_directory(directory, filename)
    except Exception as e:
        #if there is no file in directory
        print(f"Error sending file: {e}", flush=True)
        return "File not found", 404


@views.route('/', methods=['GET', 'POST']) #home route
@login_required
def home():
    # Retrieve the output image and watermark logo URL from the session
    #default is set to false if not stored in session yet
    output_image_url = session.pop('output_image_url', None)  
    watermark_logo_url = session.pop('watermark_logo_url', None)
    
    #if watermark logo ,
    if (watermark_logo_url==None):
        input_image_url, watermark_logo_url = create_user_folder(current_user.get_preference().user_id)

    #getting the current bool state of "Add text" and "Add logo" buttons
    #default is set to false
    is_watermark_text = session.get('is_watermark_text', False)
    is_watermark_logo = session.get('is_watermark_logo', False)

    if request.method == 'POST': 
        #deals with chich button is visible
        if (request.form['action'] == 'text-options'):
            is_watermark_text = not is_watermark_text
            is_watermark_logo = False
            session['is_watermark_text'] = is_watermark_text  # Store the updated value in the session
            session['is_watermark_logo'] = is_watermark_logo

        if (request.form['action'] == 'logo-options'):
            is_watermark_logo = not is_watermark_logo
            is_watermark_text = False
            session['is_watermark_text'] = is_watermark_text  # Store the updated value in the session
            session['is_watermark_logo'] = is_watermark_logo
        # print(f"\n\n\n action is {request.form['action']} and logo state is {is_watermark_logo} \n\n\n")

        # Handles the image upload and processing
        if request.form['action'] == 'apply':
            file = request.files['input_file']
            watermark_image = request.files["input_logo"]

            # Check if no new orginal file is uploaded
            if file.filename == '':
                # Retrieve the current image from the user's folder
                existing_files = os.listdir(input_image_url)  # List files in the user folder
                if existing_files:
                    # Assume the first file in the folder is the current image
                    file_path = os.path.join(input_image_url, existing_files[0])
                else:
                    # No file in the folder and no new file uploaded
                    flash('No file uploaded or found in your folder.', category='error')
                    return redirect(request.url)

            else:
                file.filename = "input.png"
                
                file_path = os.path.join(input_image_url, file.filename)
                file.save(file_path)
            
            #check if no new original logo is uploaded
            if watermark_image.filename == '':
                # Retrieve the current image from the user's folder
                existing_watermark_image = os.listdir(watermark_logo_url)  # List files in the user folder
                if existing_watermark_image:
                    # Assume the first file in the folder is the current image
                    logo_path = os.path.join(watermark_logo_url, existing_watermark_image[0])
                else:
                    # No file in the folder and no new file uploaded
                    flash('No file uploaded or found in your folder.', category='error')
                    return redirect(request.url)

            else:
                watermark_image.filename = "watermark_logo.png"
                
                logo_path = os.path.join(watermark_logo_url, watermark_image.filename)
                watermark_image.save(logo_path)


            output_path = os.path.join(DOWNLOAD_FOLDER, 'output.png')

            # Apply image manipulation (AI disturbance overlay, watermark, etc.)
            # print(f"\n\n\n {is_watermark_logo} \n\n\n")
            apply_ai_overlay(file_path, output_path)
            if(is_watermark_text):
                apply_watermark_text(file_path, output_path)
            elif(is_watermark_logo):
                # print(f"\n\n\n {is_watermark_logo} \n\n\n")
                apply_watermark_logo(file_path, output_path, logo_path)

            output_image_url = url_for('views.download_file', filename='output.png', directory='DOWNLOADS')
            session['output_image_url'] = output_image_url  # Store the URL in the session

            watermark_logo_url = url_for('views.download_file', filename='output.png', directory='logo_path')
            session['watermark_logo_url'] = watermark_logo_url  # Store the URL in the session

            # Save user preferences
            current_user.update_preference(
                overlay_opacity=request.form.get('ai-opacity'),
                watermark_opacity=request.form.get('watermark-opacity'),
                watermark_label=request.form.get('watermark-label'),
                font_size=request.form.get('font-size'),
                font_style=request.form.get('font-style')
            )
            flash('Preferences updated!', category='success')
            return redirect(url_for('views.home'))
            
    return render_template('home.html', user=current_user, output_image_url=output_image_url, is_watermark_logo=is_watermark_logo, is_watermark_text=is_watermark_text)


@views.route('/run-script', methods=['POST'])
def run_script():
    # Call the external Python script
    result = subprocess.run(['python', 'website/testing.py'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Script executed successfully")
        print("stdout:", result.stdout)
    else:
        print("Script execution failed")
        print("stderr:", result.stderr)
    return redirect(url_for('views.home'))


def create_user_folder(user_id):
    """
    Function to create a user-specific folder 
    user folder contains subfolders for input image and logo

    Parameters:
        user_id

    Returns:
        URL to user folder, URL to image folder, URL to logo folder
    """
    # Create main user folder path based on user ID
    user_folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
    
    # Paths for the subfolders 'image' and 'logo'
    input_image_url = os.path.join(user_folder_path, 'image')
    watermark_logo_url = os.path.join(user_folder_path, 'logo')
    
    # Check if the parent user folder exists; if not, create parent and subfolders
    if not os.path.exists(user_folder_path):
        os.makedirs(input_image_url)  
        os.makedirs(watermark_logo_url)  

    return input_image_url, watermark_logo_url

def apply_ai_overlay(file_path, output_path):
    """
    Function to gather parameters and apply the AI disturbance
    overlay function from overlay.py
    """
    ai_opacity = request.form.get('ai-opacity')
    overlay.add_AI_disturbance_overlay(file_path, output_path, ai_opacity)

def apply_watermark_text(file_path, output_path):
    """
    Function to gather parameters and apply the watermark 
    text function from overlay.py
    """
    watermark_opacity = request.form.get('watermark-opacity')
    watermark_label = request.form.get('watermark-label')
    font_size = request.form.get('watermark-size')
    font_style = request.form.get('watermark-style')
    overlay.add_watermark(file_path, output_path, watermark_label, watermark_opacity, font_size, font_style)

def apply_watermark_logo(file_path, output_path, logo_path):
    """
    Function to gather parameters and apply the watermark 
    logo function from overlay.py
    """
    watermark_opacity = request.form.get('watermark-opacity')
    overlay.add_watermark_logo(file_path, output_path, watermark_opacity, logo_path)









        if request.form['action'] == 'apply':
            output_path = os.path.join(DOWNLOAD_FOLDER, 'output.png')

            file = request.files['input_file']
            file_path, error = update_image_path(file, input_image_url, "input")
            if error:
                flash('No file uploaded or found in your folder.', category='error')
                return redirect(request.url)

            if(is_watermark_logo):
                watermark_image = request.files["input_logo"]
                logo_path, error = update_image_path(watermark_image, watermark_logo_url, "watermark_logo")
                if error:
                    flash('No file uploaded or found in your folder.', category='error')
                    return redirect(request.url)
                
                apply_watermark_logo(file_path, output_path, logo_path)
                overlay.show_it(output_path)
                print(f"\n\n\n{output_path} \n\n\n")

            
            elif(is_watermark_text):
                print("\n\n\n im doing watermark text \n\n\n")
                apply_watermark_text(file_path, output_path)

            apply_ai_overlay(file_path, output_path)

            output_image_url = url_for('views.download_file', filename='output.png', directory='DOWNLOADS')
            session['output_image_url'] = output_image_url  # Store the URL in the session

            watermark_logo_url = url_for('views.download_file', filename='output.png', directory='logo_path')
            session['watermark_logo_url'] = watermark_logo_url  # Store the URL in the session
