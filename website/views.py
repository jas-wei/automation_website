from flask import Blueprint, current_app, render_template, request, flash, jsonify, url_for, redirect, send_from_directory, session
from flask_login import login_required, current_user 
import json
import subprocess
import os

# from werkzeug.utils import secure_filename
import shutil

from . import db
from .models import User, Preferences
from .automation_script import overlay  # Import the function

views = Blueprint('views', __name__)

DOWNLOAD_FOLDER = os.path.join('website', 'static', 'downloads')  # Define the download folder

# Function to create a user-specific folder
def create_user_folder(user_id):
    user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))  # Create folder path based on user ID
    if not os.path.exists(user_folder):  # Check if the folder already exists
        os.makedirs(user_folder)  # Create the folder
    return user_folder


@views.route('/downloads/<filename>')
def download_file(filename):
    try:
        print(f"Sending file from: {DOWNLOAD_FOLDER}, filename: {filename}", flush=True)  # Debug statement
        return send_from_directory(DOWNLOAD_FOLDER, filename)
    except Exception as e:
        print(f"Error sending file: {e}", flush=True)
        return "File not found", 404

@views.route('/', methods=['GET', 'POST']) #home route
@login_required
def home():
    # Retrieve the output image URL and original image path from the session
    output_image_url = session.pop('output_image_url', None)  
    user_folder = create_user_folder(current_user.get_preference().user_id)
    
    # print(f"\n\n\n ITS REPEATING \n\n\n")

    if request.method == 'POST': 

        # Handles the image upload and processing
        if request.form['action'] == 'apply':
            file = request.files['input_file']

            # Check if no new file is uploaded
            if file.filename == '':
                # Retrieve the current image from the user's folder
                existing_files = os.listdir(user_folder)  # List files in the user folder
                if existing_files:
                    # Assume the first file in the folder is the current image
                    file_path = os.path.join(user_folder, existing_files[0])
                    flash('Using existing file in your folder.', category='info')
                else:
                    # No file in the folder and no new file uploaded
                    flash('No file uploaded or found in your folder.', category='error')
                    return redirect(request.url)
            else:
                # Save the newly uploaded file
                # Clear the user's folder first
                shutil.rmtree(user_folder)
                os.makedirs(user_folder)  # Recreate the empty folder
                
                file_path = os.path.join(user_folder, file.filename)
                file.save(file_path)

            output_path = os.path.join(DOWNLOAD_FOLDER, 'output.png')

            # Apply image manipulation (AI disturbance overlay, watermark, etc.)
            apply_image_manipulation(file_path, output_path)

            output_image_url = url_for('views.download_file', filename='output.png')
            session['output_image_url'] = output_image_url  # Store the URL in the session

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
            
    # print(f"\n\n\nRendering with URL: {output_image_url}\n\n\n")  # Debug statement
    return render_template('home.html', user=current_user, output_image_url=output_image_url)


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


def apply_image_manipulation(file_path, output_path):
    # AI part
    ai_opacity = request.form.get('ai-opacity')
    overlay.add_AI_disturbance_overlay(file_path, output_path, ai_opacity)

    # Watermark part
    watermark_opacity = request.form.get('watermark-opacity')
    watermark_label = request.form.get('watermark-label')
    font_size = request.form.get('watermark-size')
    font_style = request.form.get('watermark-style')
    overlay.add_watermark(output_path, output_path, watermark_label, watermark_opacity, font_size, font_style)
