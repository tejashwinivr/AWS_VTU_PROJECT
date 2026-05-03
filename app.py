from flask import Flask, request, render_template
import boto3
import os
from botocore.config import Config

app = Flask(__name__)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY'),,
    region_name='eu-north-1',
    config=Config(signature_version='s3v4')
)

BUCKET_NAME = 'my-file-upload-project111'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload-page')
def upload_page():
    # Get list of files
    files = s3.list_objects_v2(Bucket=BUCKET_NAME)
    file_list = []

    if 'Contents' in files:
        for obj in files['Contents']:
            file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{obj['Key']}"
            file_list.append(file_url)

    return render_template('upload.html', files=file_list)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        s3.upload_fileobj(file, BUCKET_NAME, file.filename)
        
        return render_template(
            'success.html',
            filename=file.filename,
            bucket_name=BUCKET_NAME
        )

    return "Upload failed"

if __name__ == '__main__':
    app.run(debug=True)