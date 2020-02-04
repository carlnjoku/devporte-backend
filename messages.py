from flask import Flask, request, jsonify
import shutil
import os
from db import database
import datetime
import base64
from flask_cors import CORS
from bson.objectid import ObjectId
import hashlib 
import json
from PIL import Image
from werkzeug.utils import secure_filename
import requests

from firbase_storage import firebase
from users import token_required


import pyrebase


config = {
    
    "apiKey": "AIzaSyAIQcCsIQk3i-uIFnPnINhs6F3PJa3H418",
    "authDomain": "devporte-64919.firebaseapp.com",
    "databaseURL": "https://devporte-64919.firebaseio.com",
    "projectId": "devporte-64919",
    "storageBucket": "devporte-64919.appspot.com",
    "messagingSenderId": "943749828225",
    "appId": "1:943749828225:web:3f65bee5527a2d27098780",
    "measurementId": "G-5HH7B19XJJ"
  
}

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


ALLOWED_EXTENSIONS_ALL = set(['png', 'jpg', 'jpeg', 'gif', 'mp4', 'pdf', 'doc', 'docx'])

UPLOAD_FOLDER = 'media'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_ALL

@app.route('/new_message', methods=['POST'])
def new_message():
    res = {}

   
    file = request.files['file']
    if 'file' in request.files and allowed_file(file.filename) and 'body' in request.form and 'subject' in request.form and 'receiverId' in request.form :
    
        
        body = request.form['body']
        subject = request.form['subject']
        senderEmail = request.form['senderEmail']
        receiverEmail = request.form['receiverEmail']
        senderName = request.form['senderName']
        receiverName = request.form['receiverName']
        receiverId = request.form['receiverId']
        senderId = request.form['senderId']
        #date = request.form['date']
      
        get_filename = secure_filename(file.filename)
        filename, file_extension = os.path.splitext(get_filename)

        

        today = datetime.date.today() 
        today = str(today) 
        

        
        filename = today+'-'+subject+file_extension

        filename = filename.replace(' ', '-').lower()

 

        
    else:
        if not 'file' in request.files :res["error"] = "No Image"
        if not allowed_file(file.filename):res["error"] = "File type not supported"
    
        
        return jsonify({"data": res})

    filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    

    temp_file = os.path.join(app.config['UPLOAD_FOLDER'], "temp.jpg")
    
    file.save(temp_file)
    
    storage.child(filename).put(temp_file)
    
    # Get image url from firebase
    img_url = storage.child(filename).get_url(None)
   
    #res["msg"] = "Valid_Image"
    shutil.copy(temp_file,filename)
    file = request.files['file']

    
    res["media"] = filename

    print(request.files)

    req_data = request.get_json()
    print(req_data)

    data = {
        'body':body,
        'subject':subject,
        'senderEmail':senderEmail,
        'receiverEmail':receiverEmail,
        'senderName':senderName,
        'receiverName':receiverName,
        'attachment':img_url,
        'receiverId': receiverId,
        'senderId': senderId
    }


    # attachment name
    attachment_name = subject.replace(' ', '_')
   
    print(attachment_name)
    
    data['_id'] = str(ObjectId())
    x = database["messages"].insert_one(data)


    r = requests.post(
		 "https://api.mailgun.net/v3/no-reply.careercolony.com/messages",
            auth=("api", "key-8439b6fada7f7dde0652d5564cff0fde"),
            files = [("attachment", (attachment_name+file_extension, 
                    open(temp_file, "rb").read()))],
            data={
                    "from": "Devporte <invite@no-reply.careercolony.com>",
                    "to": "Carl Njoku <flavoursoft@yahoo.com>",
                    "cc": "Chinedu  <flavoursoft@gmail.com>",
                    "subject": subject,
                    "html": body
                }
                
        )

    os.remove(temp_file)

    print(temp_file)

    return jsonify({"data": res})

@app.route('/get_messages', methods=['GET'])
def get_applicant():
    try:
        dev_id = request.args.get('receiverId')
        print(dev_id)
        dev = database['messages'].find({"receiverId": dev_id})
        if dev is not None:
            return jsonify({"data": list(dev)})
        else:
            return jsonify({"data": {"message": "Developer not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5004, debug=True)