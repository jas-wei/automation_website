from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect, Flask
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
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@views.route('/', methods=['GET', 'POST']) #home route
@login_required
def home():
    if request.method == 'POST': 
        if 'note' in request.form:
            note = request.form.get('note')#Gets the note from the HTML 

            if len(note) < 1:#if ntoe is too short, flash error
                flash('Note is too short!', category='error') 
            else:
                new_note = Note(data=note, user_id=current_user.id)  #providing the scheme for the note 
                db.session.add(new_note) #adding and commiting the note to the database. just like how user was in auth.py
                db.session.commit()
                flash('Note added!', category='success')
        # handles the inputted image and the opacity post request from the viewer
        elif 'input_file' in request.files :
            file = request.files['uploads']
            opacity = request.form.get('opacity')
            if file.filename != '':
                # creates a filepath to __pycache__ and save the file to the desired location
                file_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(file_path)

                print(f"\n\n\n {file_path}\n\n\n ")
                # Process the input URL or the uploaded file with the specified opacity
                overlay.add_AI_disturbance_overlay(file_path, opacity)
                flash('AI disturbance overlay added!', category='success')
                return redirect(url_for('views.home'))

    return render_template('home.html', user=current_user)

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