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

@app.route('/new_employer', methods=['POST'])
def new_employer():
    
    try:
        
        req_data = request.get_json()
        email = req_data["email"]
        print(email)
        member = database['employers'].find_one({"email": email}, {"_id": 0})
        if member is not None:
            return jsonify({"data": {"message": "Employer already exisits"}})
        else:
            req_data['_id'] = str(ObjectId())
            
            pw = str(req_data['password'])
            pw = pw.encode('UTF-8')
            req_data['password'] = hashlib.md5(pw).hexdigest()
            
            
            x = database["employers"].insert_one(req_data)
            return jsonify({"msg": email})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/edit_employer', methods=['PUT'])
def edit_employer():
    
    try:
        
        req_data = request.get_json()
        
        skills = req_data['expertise']
        uid = req_data['uid']
        timezone = req_data['tzone']
        linkedin = req_data['linkedin']
        github = req_data['github']
        website = req_data['website']
        past_projects = req_data['pastprojects']
        about = req_data['about']

        data = {
            "expertise":skills,
            "timezone": timezone,
            "linkedin" : req_data['linkedin'],
            "github" : req_data['github'],
            "website" : req_data['website'],
            "past_projects" : req_data['pastprojects'],
            "about" : req_data['about'],
            "experience":[],
            "education":[],
            "other_skills":[],
            "portfolio":[],
            "status" : "new",
            "vetted":False
        }

        dev = database['employers'].find_one({"_id": uid})
        if dev is not None:
            database['employers'].update_one({"_id": uid}, {"$set": data},
                                                        upsert=True)
            return jsonify({"data": {"msg": "Developer profile successfully updated"}})
        else:
            return jsonify({"msg": "Admin does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/list_employers', methods=['GET'])
def list_employers():
    try:
        dev = database['employers'].find({})
        print(dev.count())
        #return jsonify({"data": candidates.count()})
        return jsonify({"data": list(dev), "developer_count":dev.count()})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})



@app.route('/get_employer', methods=['GET'])
def get_employer():
    try:
        dev_id = request.args.get('_id')
        print(dev_id)
        dev = database['employers'].find_one({"_id": dev_id})
        if dev is not None:
            return jsonify({"data": dev})
        else:
            return jsonify({"data": {"message": "Developer not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/delete_employer', methods=['GET'])
def delete_employer():
    try:
        exp_id = request.args.get('_id')
        print(exp_id)
        exp = database['employers'].find_one({"_id": exp_id})
        if exp is not None:
            database['employers'].remove({"_id": exp_id})
            return jsonify({"data": {"msg": "Developer was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Developer not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5009, debug=True)


