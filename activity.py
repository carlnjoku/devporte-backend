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

@app.route('/add_activity', methods=['POST'])
def add_activity():
    
    try:
        
        req_data = request.get_json()

        req_data['_id'] = str(ObjectId())
        x = database["activity"].insert_one(req_data)
        return jsonify({"msg": ""})

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





if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5005, debug=True)












    