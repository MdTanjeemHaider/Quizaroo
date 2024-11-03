from flask import Flask, redirect, request, jsonify, render_template, session, url_for
import pyrebase
import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Initialize the firebase app
config = {
  "apiKey": os.getenv("FIREBASE_API_KEY"),
  "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
  "projectId": os.getenv("FIREBASE_PROJECT_ID"),
  "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
  "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
  "appId": os.getenv("FIREBASE_APP_ID"),
  "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
  "databaseURL": ""
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

@app.route('/')
def home():
    if ('user' in session):
        return redirect(url_for('dashboard'))
    else:
        return render_template('loginregister.html')
    
@app.route('/dashboard')
def dashboard():
    if ('user' not in session):
        return redirect(url_for('home'))
    return render_template('dashboard.html')
        

@app.route('/login', methods=['POST'])
def login_user():
    # Extract the data from the request
    data = request.form
    email = data.get('email')
    password = data.get('password')

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        session['user'] = user['idToken'] # Save the user token in the session
    except:
        return jsonify({'error': 'User not found'}), 400
    
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['POST'])
def register_user():
    # Extract the data from the request
    data = request.form
    email = data.get('email')
    password = data.get('password')
    password_repeat = data.get('password-repeat')

    # Check if the passwords match
    if password != password_repeat:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    try:
        # Create a new user
        auth.create_user_with_email_and_password(email, password)

        # login the user
        user = auth.sign_in_with_email_and_password(email, password)
        session['user'] = user['idToken'] # Save the user token in the session
    except Exception as e:
        print(e)
        return jsonify({'error': 'User already exists'}), 400
    
    return redirect(url_for('dashboard'))
    
@app.route('/logout')
def logout_user():
    session.pop('user') # Remove the user token from the session
    return redirect(url_for('home'))
    
if __name__ == '__main__':
    app.run(debug=True)