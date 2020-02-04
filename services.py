from flask import Flask, request, jsonify
import shutil
import os
from db import database
import datetime
import base64
from flask_cors import CORS
from bson.objectid import ObjectId
import hashlib 
from users import token_required


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/newAdmin', methods=['POST'])
def newUser():
    
    try:
        
        req_data = request.get_json()
        email = req_data['email']
        
        member = database['users'].find_one({"email": email}, {"_id": 0})
        if member is not None:
            return jsonify({"data": {"message": "User already exisits"}})
        else:
            req_data['_id'] = str(ObjectId())
            
            pw = str(req_data['password'])
            pw = pw.encode('UTF-8')
            req_data['password'] = hashlib.md5(pw).hexdigest()
            
            
            x = database["users"].insert_one(req_data)
            return jsonify({"msg": "User successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/edit_user', methods=['POST'])
def edit_user():
    
    try:
        
        req_data = request.get_json()
        email = req_data['email']
        
        member = database['users'].find_one({"email": email}, {"_id": 0})
        if member is not None:
            return jsonify({"data": {"message": "User already exisits"}})
        else:
            x = database["users"].insert_one(req_data)
            return jsonify({"msg": "User successfully created"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001, debug=True)