from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect, send_from_directory, session
from flask_login import login_required, current_user 
import json
import subprocess
import os

from werkzeug.utils import secure_filename

from . import db
from .models import User, Preferences
from .automation_script import overlay  # Import the function

views = Blueprint('views', __name__)

# Define the upload folder
UPLOAD_FOLDER = os.path.join('website', 'uploads')
DOWNLOAD_FOLDER = os.path.join('website', 'static', 'downloads')  # Define the download folder


# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
    output_image_url = session.pop('output_image_url', None)  # <--- No change
    original_image_path = session.get('original_image_path', None)  # <--- NEW: Retrieve the original image path from session

    if request.method == 'POST': 
        if not current_user.get_preference():
            # Initialize default preferences for the user if not present
            new_preference = Preferences(
                overlay_opacity="0.000",
                watermark_opacity="0.000",
                watermark_label="Enter Text",
                font_size="30",
                user_id=current_user.id
            )
            db.session.add(new_preference)
            db.session.commit()

        # if request.form['action'] == 'save_preferences':
        #     # Save user preferences
        #     current_user.update_preference(
        #         overlay_opacity=request.form.get('ai-opacity'),
        #         watermark_opacity=request.form.get('watermark-opacity'),
        #         watermark_label=request.form.get('watermark-label'),
        #         font_size=request.form.get('font-size')
        #     )
        #     flash('Preferences updated!', category='success')

        # Handles the image upload and processing
        elif (request.form['action'] == 'apply'): #and ('input_file' in request.files)
            # print("Input file received")  # Debug statement
            file = request.files['input_file']
            
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            else:
                # print(f"Processing file: {file.filename}")  # Debug statement
                # creates a filepath to downloads and save the file to the desired location
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)
                output_path = os.path.join(DOWNLOAD_FOLDER, 'output.png')

                # AI part
                ai_opacity = request.form.get('ai-opacity')
                overlay.add_AI_disturbance_overlay(file_path, output_path, ai_opacity)
                # print(f"Received opacity: {ai_opacity}")  # Debug statement

                # Watermark part
                watermark_opacity = request.form.get('watermark-opacity')
                watermark_label = request.form.get('watermark-label')
                font_size = request.form.get('watermark-font')
                overlay.add_watermark(output_path, output_path, watermark_label, watermark_opacity, font_size)
                # print(f"\n\n\n{watermark_opacity, watermark_label}\n\n\n")

                # Process the input URL or the uploaded file with the specified opacity
                
                
                flash('AI disturbance overlay added!', category='success')
                output_image_url = url_for('views.download_file', filename='output.png')
                # print(f"Generated URL: {output_image_url}")  # Debug statement
                session['output_image_url'] = output_image_url  # Store the URL in the session
                os.remove(file_path)

                # Save user preferences
                current_user.update_preference(
                    overlay_opacity=request.form.get('ai-opacity'),
                    watermark_opacity=request.form.get('watermark-opacity'),
                    watermark_label=request.form.get('watermark-label'),
                    font_size=request.form.get('font-size')
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

