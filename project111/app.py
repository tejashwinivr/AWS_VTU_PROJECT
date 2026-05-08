from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import boto3
from botocore.config import Config

app = Flask(__name__)

app.secret_key = 'secret123'

# DATABASE CONFIG

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

# AWS CONFIG

s3 = boto3.client(
    's3',
    aws_access_key_id='YOUR_ACCESS_KEY',
aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='eu-north-1',
    config=Config(signature_version='s3v4')
)

BUCKET_NAME = 'my-file-upload-project111'

# DATABASE MODEL

class File(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    filename = db.Column(db.String(200))

    category = db.Column(db.String(100))

    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    file_url = db.Column(db.String(500))

# LOGIN PAGE

@app.route('/')
def login():

    return render_template('login.html')

# LOGIN FUNCTION

@app.route('/login', methods=['POST'])
def do_login():

    username = request.form['username']

    password = request.form['password']

    if username == 'admin' and password == 'admin123':

        session['user'] = username

        return redirect('/upload-page')

    return "Invalid Username or Password"

# DASHBOARD

@app.route('/upload-page')
def upload_page():

    if 'user' not in session:

        return redirect('/')

    files = File.query.all()

    return render_template(
        'upload.html',
        files=files
    )

# UPLOAD

@app.route('/upload', methods=['POST'])
def upload():

    if 'user' not in session:

        return redirect('/')

    file = request.files['file']

    category = request.form['category']

    if file:

        s3.upload_fileobj(file, BUCKET_NAME, file.filename)

        file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file.filename}"

        new_file = File(
            filename=file.filename,
            category=category,
            file_url=file_url
        )

        db.session.add(new_file)

        db.session.commit()

        return render_template(
            'success.html',
            filename=file.filename,
            bucket_name=BUCKET_NAME
        )

    return "Upload Failed"

# DELETE

@app.route('/delete/<int:file_id>')
def delete_file(file_id):

    if 'user' not in session:

        return redirect('/')

    file = File.query.get(file_id)

    if file:

        s3.delete_object(
            Bucket=BUCKET_NAME,
            Key=file.filename
        )

        db.session.delete(file)

        db.session.commit()

    return redirect('/upload-page')

# LOGOUT

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/')

# CREATE DATABASE

with app.app_context():

    db.create_all()

# RUN

if __name__ == '__main__':

    app.run(debug=True)