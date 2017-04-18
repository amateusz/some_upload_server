#!./server_env/bin/python3
# my venv path

from flask import Flask, render_template, request, flash, url_for, redirect, send_from_directory
from flask_humanize import Humanize
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
humanize = Humanize(app)

app.config['JSON_SORT_KEYS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # file size limit 50 MiB
app.secret_key = 'super secret key'  # whatever it is


# app.config['SESSION_TYPE'] = 'filesystem'


@app.route('/')
def upload():  # main page with file upload functionality
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    # print(request.files)
    if 'file' not in request.files:
        flash('Co ty robisz..?', 'error')  # what are you doing..?
        return redirect('/')
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('Nie wybrano żadnego pliku!', 'warning')  # there is no file!
        return redirect('/')

    filename = secure_filename(file.filename)  # user input sanitization
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    flash(filename, 'info')  # let them know they uploaded a file succesfully
    return redirect(url_for('get_uploads'))  # why "upload", which is THIS endpoint works??


@app.route('/upload', methods=['GET'])
def get_uploads():
    try:
        files = [[_] for _ in os.listdir(app.config['UPLOAD_FOLDER'])]
        # add some data to filenames in a object-like manner. namely datetime and size gathered from os.
        for file in files:
            file_stats = os.stat(os.path.join(app.config['UPLOAD_FOLDER'], file[0]))
            from datetime import datetime
            date_and_time = datetime.fromtimestamp(file_stats.st_mtime)
            size = file_stats.st_size
            file.append({'datetime': date_and_time, 'size': size})
        files.sort(key=lambda r: r[1]['datetime'], reverse=True)  # sort by datetime from the newest
    except Exception as e:
        # flash('Bład serwera. Nie można znaleźć plików', 'error')
        return (render_template('get_uploads.html', error=str(
            e.strerror) + ' \"' + e.filename + '\"'))  # this likely will be FileNotFound Exception
    return (render_template('get_uploads.html', files_list=files))


# this should be decorated by some access verification guard. now it is {{ jak jest po angielsku "głębokie ukrycie" ? }}
@app.route('/upload/<filename>')
def get_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# a novelty. experimental method copyied from here: http://html5demos.com/dnd-upload
@app.route('/drop', methods=['GET'])
def upload_file_drag_and_drop():
    return (render_template('upload_drag_and_drop.html'))


# only for Flask-humanize
@humanize.localeselector
def get_locale():
    return 'pl_PL'


# if __name__ == '__main__': # commented because `flask run` doesn't like this. for production if main not needed
app.run(host='0.0.0.0', port=5000)
