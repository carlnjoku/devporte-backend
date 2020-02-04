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
from users import token_required

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/new_campaign', methods=['POST'])
def new_campaign():
    
    try:
        req_data = request.get_json()

        req_data['_id'] = str(ObjectId())
        x = database["campaign"].insert_one(req_data)
        return jsonify({"msg": "Campaign successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/send_test_invite', methods=['POST'])
def send_test_invite():
    
    try:
        
        req_data = request.get_json()
        test_name = request.form['test_name']
        data = {
            "test_name" : request.form['test_name'],
            "campaign_id" : request.form['campaign_id'],
            "candidate_id" : request.form['candidate_id'],
            "candidate_name" : request.form['candidate_name'],
            "candidate_email" : request.form['candidate_email'],
            "recruiter_email" : request.form['recruiter_email'],
            "send_invitation_email" : True,
            "tags" : request.form['tags'],
            "test_url" : request.form['test_url'],
            "status" : request.form['status']
            


        }
        #print(test_name)
        data['_id'] = str(ObjectId())
        x = database["sent_test"].insert_one(data)
        return jsonify({"msg": "Campaign successfully created", "res":{"test_url":request.form['test_url'], "id": request.form['candidate_id']}})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/get_candidate_test', methods=['GET'])
def get_candidate_test():
    try:
        candidate_id = request.args.get('candidate_id')
        print(candidate_id)
        exp = database['sent_test'].find({"candidate_id": candidate_id})
        if exp is not None:
            return jsonify({"data": list(exp)})
        else:
            return jsonify({"data": {"message": "Tests not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/edit_campaign', methods=['PUT'])
def edit_campaign():
    
    try:
        
        req_data = request.get_json()
        
        id = req_data['_id']

        print(req_data)
        member = database['campaign'].find_one({"_id": id})
        if member is not None:
            
            database['campaign'].update({"_id": id}, {"$set": req_data},
                                                        upsert=True)
            return jsonify({"result": {"msg": "Campaign successfully updated"}})
        else:
            return jsonify({"msg": "Campaign does not exist"})
            
    except Exception as e:
        return jsonify({"result": {"error_msg": str(e)}})


@app.route('/get_campaigns', methods=['GET'])
def list_expertise():
    try:
        exp = database['campaign'].find({})
        print(exp.count())
        #return jsonify({"data": candidates.count()})
        return jsonify({"result": list(exp)})
    except Exception as e:
        return jsonify({"result": {"error_msg": str(e)}})

@app.route('/get_campaign', methods=['GET'])
def get_expertise():
    try:
        exp_id = request.args.get('_id')
        print(exp_id)
        exp = database['campaign'].find_one({"_id": exp_id})
        if exp is not None:
            return jsonify({"data": exp})
        else:
            return jsonify({"data": {"message": "Campaign not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/delete_campaign', methods=['GET'])
def delete_expertise():
    try:
        exp_id = request.args.get('_id')
        print(exp_id)
        exp = database['campaign'].find_one({"_id": exp_id})
        if exp is not None:
            database['campaign'].remove({"_id": exp_id})
            return jsonify({"data": {"msg": "Campaign was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Campaign not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})





if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5006, debug=True)