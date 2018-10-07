import os
import pickle
import hashlib
from flask import Flask, flash, request, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# check whether file directory is there or not
cur_dir = os.path.dirname(os.path.realpath('__file__'))
file_path = (cur_dir + "/" + "file_uploads")
if not os.path.exists(file_path):
    os.makedirs(file_path)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = file_path


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # check if the post request has the file part
        if 'file' not in request.files:
            raise InvalidUsage('The file is not available', 
                                    status_code=410)

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            raise InvalidUsage('File uploaded was unsuccessful!', 
                                    status_code=410)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 
                                    filename))
            upload_file = (app.config['UPLOAD_FOLDER'] + '/' + filename)
            # save pickle file
            pickle_path = (cur_dir + "/" + "save.p")
            if os.path.exists(pickle_path):
                pickle_content = pickle.load( open( pickle_path, "rb" ) )
                _md5sum = hashlib.md5(open(upload_file,'rb')
                                    .read()).hexdigest()
                if _md5sum in pickle_content:
                    raise InvalidUsage('The file content is already available', 
                                    status_code=410)
                pickle_content[_md5sum] = filename
                pickle.dump( pickle_content, open( pickle_path, "wb" ) )
            else:
                _md5sum = hashlib.md5(open(upload_file,'rb')
                                    .read()).hexdigest()
                pickle.dump( {_md5sum:filename}, open( pickle_path, "wb" ) )
                
            return "File uploaded successfully!"
        else:
            raise InvalidUsage('File type is not allowded', 
                                    status_code=410)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/delete', methods=['GET', 'POST'])
def delete_file():
    if request.method == 'POST':
        values = request.values.to_dict()
        if 'file_name' in values:
            try:
                del_file = (app.config['UPLOAD_FOLDER'] \
                            + "/" + values['file_name'])
                os.remove(del_file)
            except OSError:
                raise InvalidUsage('The file is not available', 
                                    status_code=410)
        else:
            raise InvalidUsage('Please provide a file name', 
                                    status_code=410)

        return "File Deleted Successfully!"
    return '''
    <!DOCTYPE html>
    <html>
    <body>

    <form method=post enctype=multipart/form-data>
    File Name: <input type="text" name="file_name" value=""><br>
    <input type="submit" value="Submit">
    </form>

    </body>
    </html>
    '''

@app.route('/retrieve_file', methods=['GET', 'POST'])
def retrieve_file():
    if request.method == 'POST':
        values = request.values.to_dict()
        if 'file_name' in values:
            try:
                file_full_path = (app.config['UPLOAD_FOLDER'] \
                            + "/" + values['file_name'])
                if os.path.exists(file_full_path):
                    return send_file(file_full_path)
                else:
                    raise InvalidUsage('The file is not available', 
                                    status_code=410)
            except OSError:
                raise InvalidUsage('The file deleted unsucessfully', 
                                    status_code=410)
        else:
            raise InvalidUsage('Please provide a file name', 
                                    status_code=410)

        return "File Deleted Successfully!"
    return '''
    <!DOCTYPE html>
    <html>
    <body>

    <form method=post enctype=multipart/form-data>
    File Name: <input type="text" name="file_name" value=""><br>
    <input type="submit" value="Submit">
    </form>

    </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
