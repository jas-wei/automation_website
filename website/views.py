from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect, send_from_directory, session
from flask_login import login_required, current_user 
import json
import subprocess
import os

from . import db
from .models import User, Note
from .automation_script import overlay  # Import the function

views = Blueprint('views', __name__)

# Define the upload folder
UPLOAD_FOLDER = os.path.join('website', 'uploads')
DOWNLOAD_FOLDER = os.path.join('website', 'static', 'downloads')  # Define the download folder

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
    output_image_url = session.pop('output_image_url', None)  # Retrieve and remove the URL from the session

    if request.method == 'POST': 
        if 'note' in request.form:
            note = request.form.get('note')#Gets the note from the HTML 

            if len(note) < 1:#if note is too short, flash error
                flash('Note is too short!', category='error') 
            else:
                new_note = Note(data=note, user_id=current_user.id)  #providing the scheme for the note 
                db.session.add(new_note) #adding and committing the note to the database. just like how user was in auth.py
                db.session.commit()
                flash('Note added!', category='success')
        # handles the inputted image and the opacity post request from the viewer
        elif 'input_file' in request.files:
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
                # watermark_font_size = request.form.get('font-size')

                # Process the input URL or the uploaded file with the specified opacity
                
                
                flash('AI disturbance overlay added!', category='success')
                output_image_url = url_for('views.download_file', filename='output.png')
                # print(f"Generated URL: {output_image_url}")  # Debug statement
                session['output_image_url'] = output_image_url  # Store the URL in the session
                return redirect(url_for('views.home'))

    # print(f"\n\n\nRendering with URL: {output_image_url}\n\n\n")  # Debug statement
    return render_template('home.html', user=current_user, output_image_url=output_image_url)

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})

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
