import os
import logging
from datetime import datetime
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "super_secret_key" 

logging.basicConfig(
    filename='server.log', 
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DOWNLOAD_PASSWORD = "password123!"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        password = request.form.get('password')
        client_ip = request.remote_addr

        if password != DOWNLOAD_PASSWORD:
            logging.warning(f"업로드 실패: 비밀번호 불일치 (IP: {client_ip})")
            return "Invalid Password", 403

        if 'file' not in request.files:
            return "No file part", 400
        
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
            
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            logging.info(f"파일 업로드 성공: {filename} (IP: {client_ip})")
            return "Success", 200
            
    return render_template('upload.html')

@app.route('/download', methods=['GET'])
def download_list():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('download_list.html', files=files)

@app.route('/download/<filename>', methods=['GET', 'POST'])
def download_file(filename):
    client_ip = request.remote_addr
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password == DOWNLOAD_PASSWORD:
            logging.info(f"파일 다운로드 시작: {filename} (IP: {client_ip})")
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        else:
            logging.warning(f"다운로드 거부: 비밀번호 불일치 - 파일: {filename} (IP: {client_ip})")
            flash('비밀번호가 틀렸습니다.')
            return redirect(request.url)
            
    return render_template('download_auth.html', filename=filename)

if __name__ == '__main__':
    logging.info("--- 서버 시작 ---")
    app.run(port=5150, debug=True)