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

@app.route('/new_developer', methods=['POST'])
def add_applicant():
    
    try:
        
        req_data = request.get_json()
        email = req_data["email"]
        print(email)
        member = database['developers'].find_one({"email": email}, {"_id": 0})
        if member is not None:
            return jsonify({"data": {"message": "Applicant already exisits"}})
        else:
            #req_data['_id'] = str(ObjectId())
            
            #pw = str(req_data['password'])
            #pw = pw.encode('UTF-8')
            #req_data['password'] = hashlib.md5(pw).hexdigest()
            
            
            x = database["developers"].insert_one(req_data)
            return jsonify({"msg": email})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/update_developer', methods=['PUT'])
def update_developer():
    
    try:
        
        req_data = request.get_json()
        
        position = req_data['position']
        id = req_data['_id']
        company_name = req_data['company_name']
        job_description = req_data['job_description']
        start_month = req_data['start_month']
        start_year = req_data['start_year']
        end_month = req_data['end_month']
        end_year = req_data['end_year']
    

        data = {
            "_id":id,
            "position":position,
            "company_name": company_name,
            "job_description":job_description,
            "start_month" : start_month,
            "start_year" : start_year,
            "end_month" : end_month,
            "end_year" : end_year
        }

        dev = database['developers'].find_one({"_id": id})
        if dev is not None:
            database['developers'].update_one({"_id": id}, {"$push":{"experience":data}  },
                                                        upsert=True)
            return jsonify({"data": {"msg": "Developer experience successfully updated"}})
        else:
            return jsonify({"msg": "developer does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/list_applicants', methods=['GET'])
def list_applicants():
    try:
        dev = database['applicants'].find({})
        print(dev.count())
        #return jsonify({"data": candidates.count()})
        return jsonify({"data": list(dev), "developer_count":dev.count()})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_timezones', methods=['GET'])
def get_timezones():
    try:
        tzone = database['timezone'].find({}, {"_id": 0})
        return jsonify({"data": list(tzone)})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_applicant', methods=['GET'])
def get_applicant():
    try:
        dev_id = request.args.get('_id')
        print(dev_id)
        dev = database['applicants'].find_one({"_id": dev_id})
        if dev is not None:
            return jsonify({"data": dev})
        else:
            return jsonify({"data": {"message": "Developer not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/delete_applicant', methods=['GET'])
def delete_applicant():
    try:
        exp_id = request.args.get('_id')
        print(exp_id)
        exp = database['applicants'].find_one({"_id": exp_id})
        if exp is not None:
            database['applicants'].remove({"_id": exp_id})
            return jsonify({"data": {"msg": "Developer was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Developer not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5007, debug=True)
