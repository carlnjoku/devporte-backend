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
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
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

ALLOWED_EXTENSIONS_ALL = set(['png', 'jpg', 'jpeg', 'gif'])

UPLOAD_FOLDER = 'media'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_ALL

@app.route('/new_admin_old', methods=['POST'])
def newUser_old():
    
    try:
        
        req_data = request.get_json()
        email = req_data['email']
        
        member = database['admins'].find_one({"email": email}, {"_id": 0})
        if member is not None:
            return jsonify({"data": {"message": "User already exisits"}})
        else:
            req_data['_id'] = str(ObjectId())
            
            #pw = str(req_data['password'])
            #pw = pw.encode('UTF-8')
            #req_data['password'] = hashlib.md5(pw).hexdigest()
            req_data['password'] = generate_password_hash(req_data['password'], method='sha256')
            
            
            
            x = database["admins"].insert_one(req_data)
            return jsonify({"msg": "User successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})



@app.route('/add_admin', methods=['POST'])
def add_admin():
    res = {}

   
    file = request.files['image']
    if 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form and 'password' in request.form :
    
        
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        position = request.form['position']
        phone = request.form['phone']
        role = request.form['role']
        user_type = request.form['user_type']

        print(request.files['image'])
      
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

    hashed_password = generate_password_hash(request['password'], method='sha256')
    data = {
        'firstname':firstname,
        'lastname':lastname,
        'avatar_thumbnail':img_url,
        'email':email,
        'password':hashed_password,
        'position':position,
        'phone':phone,
        'role':role,
    }

    data['_id'] = str(ObjectId())
    x = database["admins"].insert_one(data)


    #memberID = request.form['memberID']
    #database['users'].update({'_id': memberID}, {"$set": {'profile_bg':profile_bg}})

    os.remove(temp_file)

    return jsonify({"data": res})

    



@app.route('/edit_admin', methods=['PUT'])
def edit_user():
    
    try:
        
        req_data = request.get_json()

        print(req_data)
        
        id = req_data['_id']
       
        member = database['admins'].find_one({"_id": id})
        if member is not None:
            
            database['admins'].update_one({"_id": id}, {"$set": req_data},
                                                        upsert=True)
            return jsonify({"data": {"msg": "Admin successfully updated"}})
        else:
            return jsonify({"msg": "Admin does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/admin_list', methods=['GET'])
def list_admin():
    try:
        candidates = database['admins'].find({})
        print(candidates.count())
        #return jsonify({"data": candidates.count()})
        
        return jsonify({"result": list(candidates)})
    except Exception as e:
        return jsonify({"result": {"error_msg": str(e)}})

@app.route('/get_admin', methods=['GET'])
def get_admin():
    try:
        admin_id = request.args.get('_id')
        print(admin_id)
        admin = database['admins'].find_one({"_id": admin_id})
        if admin is not None:
            return jsonify({"data": admin})
        else:
            return jsonify({"data": {"message": "Admin not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/delete_admin', methods=['GET'])
def delete_admin():
    try:
        admin_id = request.args.get('_id')
        print(admin_id)
        admin = database['admins'].find_one({"_id": admin_id})
        if admin is not None:
            database['admins'].remove({"_id": admin_id})
            return jsonify({"data": {"msg": "Admin was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Admin not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5002, debug=True)