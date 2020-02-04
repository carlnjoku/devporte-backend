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


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/add_tech', methods=['POST'])
def new_tech():
    
    try:
        
        req_data = request.get_json()
        
        req_data['_id'] = str(ObjectId())
        x = database["technologies"].insert_one(req_data)
        return jsonify({"msg": "Technology successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/edit_tech', methods=['PUT'])
def edit_tech():
    
    try:
        
        req_data = request.get_json()
        
        id = req_data['_id']

        print(req_data)
        member = database['technologies'].find_one({"_id": id})
        if member is not None:
            
            database['technologies'].update({"_id": id}, {"$set": req_data},
                                                        upsert=True)
            return jsonify({"data": {"msg": "Technoloy successfully updated"}})
        else:
            return jsonify({"msg": "Technology does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/list_tech', methods=['GET'])
def list_tech():
    try:
        tech = database['technologies'].find({}, {'_id': 0})
        print(tech.count())
        #return jsonify({"data": candidates.count()})
        return jsonify({"data": list(tech)})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_tech', methods=['GET'])
def get_tech():
    try:
        tech_id = request.args.get('_id')
        print(tech_id)
        tech = database['technologies'].find_one({"_id": tech_id})
        if tech is not None:
            return jsonify({"data": tech})
        else:
            return jsonify({"data": {"message": "Technology not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/delete_tech', methods=['GET'])
def delete_tech():
    try:
        tech_id = request.args.get('_id')
        print(tech_id)
        tech = database['technologies'].find_one({"_id": tech_id})
        if tech is not None:
            database['technologies'].remove({"_id": tech_id})
            return jsonify({"data": {"msg": "Technology was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Technology not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5004, debug=True)