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


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


ALLOWED_EXTENSIONS_ALL = set(['png', 'jpg', 'jpeg', 'gif', 'mp4'])

UPLOAD_FOLDER = 'media/'
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


@app.route('/list_expertise', methods=['GET'])
def list_expertise():
    try:
        exp = database['expertise'].find({}, {'_id': 0})
        print(exp.count())
        #return jsonify({"data": candidates.count()})
        return jsonify({"result": list(exp)})
    except Exception as e:
        return jsonify({"result": {"error_msg": str(e)}})

@app.route('/get_expertise', methods=['GET'])
def get_expertise():
    try:
        exp_id = request.args.get('_id')
        print(exp_id)
        exp = database['expertise'].find_one({"_id": exp_id})
        if exp is not None:
            return jsonify({"data": exp})
        else:
            return jsonify({"data": {"message": "Expertise not Found"}})
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


@app.route('/post_images', methods=['POST'])
def post_images():
    res = {}

    file = request.files['image']
    if 'image' in request.files and allowed_file(file.filename) and 'body' in request.form :
    
        body = request.form['body'] 
        print(body)
        get_filename = secure_filename(file.filename)
        filename, file_extension = os.path.splitext(get_filename)
    
        #title = request.form['title']
        today = datetime.date.today() 
        today = str(today) 
        encodedBytes = base64.b64encode(today.encode("utf-8"))
        encodedStr = str(encodedBytes, "utf-8")

        print(encodedStr)

        print(get_filename)
        
        
        filename = encodedStr+file_extension
    else:
        if not 'image' in request.files :res["error"] = "No Image"
        if not allowed_file(file.filename):res["error"] = "File type not supported"
    
        
        return jsonify({"data": res})

    filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    temp_file = os.path.join(app.config['UPLOAD_FOLDER'], "temp.jpg")
    
    file.save(temp_file)
    
    #res["msg"] = "Valid_Image"
    shutil.copy(temp_file,filename)
    file = request.files['image']
   
    res["media"] = filename

    #memberID = request.form['memberID']
    #database['users'].update({'_id': memberID}, {"$set": {'profile_bg':profile_bg}})

    os.remove(temp_file)

    return jsonify({"data": res})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001, debug=True)