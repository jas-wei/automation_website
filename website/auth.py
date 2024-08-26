from .models import User # get user data from models.py
from . import db #import database
from werkzeug.security import generate_password_hash, check_password_hash # convert password to make more secure
from flask_login import login_user, login_required, logout_user, current_user 
from flask import Blueprint, render_template, request, flash, redirect, url_for
#blueprint is for routes and stuff, rendertemplate is for linking html files
# request is for GET, POST, PUT server requests
# flash is for flahsing error message when incorrect info

auth = Blueprint('auth', __name__)

# Initialize routes
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #getting email and password entered by user in login page
        email = request.form.get('email')
        password = request.form.get('password')

        #filter all users with the same email as entered and return first result
        user = User.query.filter_by(email=email).first() 
        if user: #if user found, compare entered password with database password, and redirect
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True) #flask remmebers that this user logged in when refreshing
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required #required to login before logging out
def logout():
    #maybe remove folder?
    logout_user() #from flask_login
    return redirect(url_for('auth.login')) #back to login page

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email=email).first()
        if user: #if user exists
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256')) # init new user
            db.session.add(new_user) # add (like git)
            db.session.commit() # commit to database
            login_user(new_user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)