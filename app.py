import os
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "super_secret_key" 

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 * 1024  # 32GB 제한
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'mp4', 'avi', 'mkv'}

DOWNLOAD_PASSWORD = "password123!"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 1. 암호 확인 먼저 수행
        password = request.form.get('password')
        if password != DOWNLOAD_PASSWORD:
            flash('업로드 비밀번호가 틀렸습니다.')
            return redirect(request.url)

        # 2. 파일 존재 확인
        if 'file' not in request.files:
            flash('파일이 선택되지 않았습니다.')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('선택된 파일이 없습니다.')
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f"'{filename}' 파일이 성공적으로 업로드되었습니다.")
            return redirect(url_for('index'))
            
    return render_template('upload.html')

@app.route('/download', methods=['GET'])
def download_list():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('download_list.html', files=files)

@app.route('/download/<filename>', methods=['GET', 'POST'])
def download_file(filename):
    if request.method == 'POST':
        password = request.form.get('password')
        
        if password == DOWNLOAD_PASSWORD:
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        else:
            flash('비밀번호가 틀렸습니다. 다시 시도해 주세요.')
            return redirect(request.url)
            
    return render_template('download_auth.html', filename=filename)

if __name__ == '__main__':
    app.run(port=5150, debug=True)