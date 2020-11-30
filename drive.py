import functools
import os
import flask
from authlib.integrations.requests_client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
from auth import getAuth
from werkzeug.utils import secure_filename
import tempfile
from apiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

app = flask.Blueprint('drive', __name__)

EXTENSIONS = ['.jpg','.png','.jpeg']

def getDriveCred():
    credentials = getAuth()
    return googleapiclient.discovery.build('drive','v3',credentials=credentials)

#save image to drive
def saveToDrive(fileName,mimeType,fileData):
    drive = getDriveCred()

    #generate ID for the new file (Not necessary)
    generate_ids_result = drive.files().generateIds(count=1).execute()
    fileId = generate_ids_result['ids'][0]

    file_metadata = {'id':fileId,'name':fileName,'mimeType': mimeType, 'parents': ['12HHw_uH0ClV035xB3ojyXAAjWd3cXSkc']}
    media = MediaIoBaseUpload(fileData,mimetype=mimeType,resumable=True)
    file =drive.files().create(body=file_metadata,media_body=media,fields='webContentLink').execute()
    print('Done')
    return file["webContentLink"]

@app.route('/google/drive',methods=['GET','POST'])
def upload():
    if 'file' not in flask.request.files:
        return flask.redirect('/')
    
    file = flask.request.files['file']
    if(not file):
        return flask.redirect('/')
    
    filename = secure_filename(file.filename)
    #validate extension
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in EXTENSIONS :
            return flask.render_template('index.html',error='Invalid Type')
    fp = tempfile.TemporaryFile()
    ch = file.read()
    fp.write(ch)
    fp.seek(0)

    mime_type = flask.request.headers['Content-Type']
    link = saveToDrive(filename,mime_type,fp)

    return flask.render_template('index.html',success='File Added Successfully !',link=link)
