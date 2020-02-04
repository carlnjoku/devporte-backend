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


ALLOWED_EXTENSIONS_ALL = set(['png', 'jpg', 'jpeg', 'gif', 'mp4'])

UPLOAD_FOLDER = 'media'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_ALL

@app.route('/add_expertise', methods=['POST'])
def new_expertise():
    
    try:
        
        req_data = request.get_json()

        req_data['_id'] = str(ObjectId())
        x = database["expertise"].insert_one(req_data)
        return jsonify({"msg": "Expertise successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/edit_expertise', methods=['PUT'])
def edit_expertise():
    
    try:
        
        req_data = request.get_json()
        
        id = req_data['_id']

        print(req_data)
        member = database['expertise'].find_one({"_id": id})
        if member is not None:
            
            database['expertise'].update({"_id": id}, {"$set": req_data},
                                                        upsert=True)
            return jsonify({"result": {"msg": "Admin successfully updated"}})
        else:
            return jsonify({"msg": "Admin does not exist"})
            
    except Exception as e:
        return jsonify({"result": {"error_msg": str(e)}})


@app.route('/list_blog', methods=['GET'])
def list_expertise():
    try:
        exp = database['blog'].find({})
        print(exp.count())
        #return jsonify({"data": candidates.count()})
        return jsonify({"result": list(exp)})
    except Exception as e:
        return jsonify({"result": {"error_msg": str(e)}})

@app.route('/get_user_article', methods=['GET'])
def get_user_article():
    try:
        exp_id = request.args.get('uid')
        print(exp_id)
        exp = database['blog'].find({"uid": exp_id})
        if exp is not None:
            print(exp.count())
            return jsonify({"data": list(exp)})
        else:
            return jsonify({"data": {"message": "No post Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_article', methods=['GET'])
def get_expertise():
    try:
        exp_id = request.args.get('_id')
        print(exp_id)
        exp = database['blog'].find_one({"_id": exp_id})
        if exp is not None:
            return jsonify({"data": exp})
        else:
            return jsonify({"data": {"message": "Post not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})



@app.route('/delete_expertise', methods=['GET'])
def delete_expertise():
    try:
        exp_id = request.args.get('_id')
        print(exp_id)
        exp = database['expertise'].find_one({"_id": exp_id})
        if exp is not None:
            database['expertise'].remove({"_id": exp_id})
            return jsonify({"data": {"msg": "Expertise was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Expertise not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/new_post_original', methods=['POST'])
def new_post_original():
    res = {}

   
    file = request.files['image']
    if 'image' in request.files and allowed_file(file.filename) and 'body' in request.form and 'title' in request.form and 'author' in request.form and 'uid' in request.form :
    
        
        body = request.form['body']
        title = request.form['title']
        uid = request.form['uid']
      
        get_filename = secure_filename(file.filename)
        filename, file_extension = os.path.splitext(get_filename)

        

        today = datetime.date.today() 
        today = str(today) 
        #encodedBytes = base64.b64encode(today.encode("utf-8"))
        #encodedStr = str(encodedBytes, "utf-8")

        
        filename = today+'-'+title+file_extension

        filename = filename.replace(' ', '-').lower()

        print(filename)

        
    else:
        if not 'image' in request.files :res["error"] = "No Image"
        if not allowed_file(file.filename):res["error"] = "File type not supported"
    
        
        return jsonify({"data": res})

    filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    #Cropp image
    #img = Image.open(filename)
    #area =(200, 100, 700,400)
    #new_sizeed_file = img.crop(area)
    #new_sizeed_file.show(new_sizeed_file)
    
    
    print(filename)

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    

    temp_file = os.path.join(app.config['UPLOAD_FOLDER'], "temp.jpg")
    
    file.save(temp_file)
    
    storage.child(filename).put(temp_file)
    
    # Get image url from firebase
    img_url = storage.child(filename).get_url(None)
   
    #res["msg"] = "Valid_Image"
    shutil.copy(temp_file,filename)
    file = request.files['image']

    
    res["media"] = filename

    print(request.files)

    req_data = request.get_json()
    print(req_data)

    data = {
        'body':body,
        'title':title,
        'thumbnail':img_url,
        'uid': uid
    }

    data['_id'] = str(ObjectId())
    x = database["blog"].insert_one(data)


    #memberID = request.form['memberID']
    #database['users'].update({'_id': memberID}, {"$set": {'profile_bg':profile_bg}})

    os.remove(temp_file)

    return jsonify({"data": res})



@app.route('/new_post', methods=['POST'])
def new_post():
    res = {}

    file = request.files['image']
    if 'image' in request.files and allowed_file(file.filename) and 'firstname' in request.form and 'lastname' in request.form :
    
        
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        
      
        get_filename = secure_filename(file.filename)
        filename, file_extension = os.path.splitext(get_filename)

        

        today = datetime.date.today() 
        today = str(today) 
        #encodedBytes = base64.b64encode(today.encode("utf-8"))
        #encodedStr = str(encodedBytes, "utf-8")

        
        filename = today+'-'+firstname+file_extension

        filename = filename.replace(' ', '-').lower()

        print(filename)


        
        
    else:
        if not 'image' in request.files :res["error"] = "No Image"
        if not allowed_file(file.filename):res["error"] = "File type not supported"
    
        
        return jsonify({"data": res})

    filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    #Cropp image
    #img = Image.open(filename)
    #area =(200, 100, 700,400)
    #new_sizeed_file = img.crop(area)
    #new_sizeed_file.show(new_sizeed_file)
    
    
    print(filename)

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    

    temp_file = os.path.join(app.config['UPLOAD_FOLDER'], "temp.jpg")
    
    file.save(temp_file)
    
    storage.child(filename).put(temp_file)
    
    # Get image url from firebase
    img_url = storage.child(filename).get_url(None)
   
    #res["msg"] = "Valid_Image"
    shutil.copy(temp_file,filename)
    file = request.files['image']

    
    res["media"] = filename

    print(request.files)

    req_data = request.get_json()
    print(req_data)

    data = {
        'firstname':firstname,
        'lastname':lastname,
        'avatar_thumbnail':img_url
    }

    data['_id'] = str(ObjectId())
    x = database["blog"].insert_one(data)


    #memberID = request.form['memberID']
    #database['users'].update({'_id': memberID}, {"$set": {'profile_bg':profile_bg}})

    os.remove(temp_file)

    return jsonify({"data": res})

    

    



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5003, debug=True)