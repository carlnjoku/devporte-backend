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

@app.route('/add_developer', methods=['POST'])
def add_developer():
    
    try:
        
        req_data = request.get_json()
        email = req_data['email']
        
        member = database['developers'].find_one({"email": email}, {"_id": 0})
        if member is not None:
            return jsonify({"data": {"message": "Developer already exisits"}})
        else:
            req_data['_id'] = str(ObjectId())
            
            pw = str(req_data['password'])
            pw = pw.encode('UTF-8')
            req_data['password'] = hashlib.md5(pw).hexdigest()
            
            
            x = database["developers"].insert_one(req_data)
            return jsonify({"msg": "Developer account successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/edit_developer', methods=['PUT'])
def edit_developer():
    
    try:
        
        req_data = request.get_json()
        
        id = req_data['_id']

        dev = database['developers'].find_one({"_id": id})
        if dev is not None:
            
            database['developers'].update_one({"_id": id}, {"$set": req_data},
                                                        upsert=True)
            return jsonify({"data": {"msg": "Developer profile successfully updated"}})
        else:
            return jsonify({"msg": "Admin does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/list_developers', methods=['GET'])
def list_developers():
    try:
        dev = database['developers'].find({}, {'_id': 0})
        print(dev.count())
        #return jsonify({"data": candidates.count()})
        return jsonify({"data": list(dev), "developer_count":dev.count()})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_developer', methods=['GET'])
def get_developer():
    try:
        dev_id = request.args.get('_id')
        print(dev_id)
        dev = database['developers'].find_one({"_id": dev_id})
        if dev is not None:
            return jsonify({"data": dev})
        else:
            return jsonify({"data": {"message": "Developer not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/delete_developer', methods=['GET'])
def delete_developer():
    try:
        exp_id = request.args.get('_id')
        print(exp_id)
        exp = database['developers'].find_one({"_id": exp_id})
        if exp is not None:
            database['developers'].remove({"_id": exp_id})
            return jsonify({"data": {"msg": "Developer was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Developer not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})



##############################
# Add or update projects     #
##############################

@app.route('/add_project', methods=['POST'])
def add_project():
    
    try:
        
        req_data = request.get_json()

        req_data['_id'] = str(ObjectId())
        x = database["projects"].insert_one(req_data)
        return jsonify({"msg": "Project successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/edit_project', methods=['PUT'])
def edit_project():
    
    try:
        
        req_data = request.get_json()
        
        id = req_data['_id']

        proj = database['projects'].find_one({"_id": id})
        if proj is not None:
            
            database['projects'].update_one({"_id": id}, { "$set":req_data},
                                                                upsert=True)
            return jsonify({"data": {"msg": "Project successfully updated"}})
        else:
            return jsonify({"msg": "Project does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

        

@app.route('/list_projects', methods=['GET'])
def list_projects():
    try:
        proj = database['projects'].find({}, {'_id': 0})
        print(proj.count())
        #return jsonify({"data": candidates.count()})
        return jsonify({"data": list(proj)})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_project', methods=['GET'])
def get_project():
    try:
        proj_id = request.args.get('_id')
        print(proj_id)
        proj = database['projects'].find_one({"_id": proj_id})
        if proj is not None:
            return jsonify({"data": proj})
        else:
            return jsonify({"data": {"message": "Developer not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/delete_project', methods=['GET'])
def delete_project():
    try:
        proj_id = request.args.get('_id')
        proj = database['projects'].find_one({"_id": proj_id})
        if proj is not None:
            database['projects'].remove({"_id": proj_id})
            return jsonify({"data": {"msg": "Developer was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Developer not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


















@app.route('/add_skills', methods=['PUT'])
def add_skills():
    
    try:
        
        req_data = request.get_json()
        
        id = req_data['_id']
        
        #remove id from data before updating
        del req_data['_id']

        dev = database['developers'].find_one({"_id": id})
        if dev is not None:
            
            database['developers'].update_one({"_id": id}, { "$push":{"skills":req_data}},
                                                                                upsert=True)
            return jsonify({"data": {"msg": "Skill successfully updated"}})
        else:
            return jsonify({"msg": "Skill does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})






@app.route('/add_language', methods=['PUT'])
def add_language():
    
    try:
        
        req_data = request.get_json()
        
        id = req_data['_id']
        
        #remove id from data before updating
        del req_data['_id']

        print(req_data)
        dev = database['developers'].find_one({"_id": id})
        if dev is not None:
            
            database['developers'].update_one({"_id": id}, { "$push":req_data},
                                                                                upsert=True)
            return jsonify({"data": {"msg": "Language successfully updated"}})
        else:
            return jsonify({"msg": "Language does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})



@app.route('/remove_project', methods=['PUT'])
def remove_project():
    
    try:
        
        req_data = request.get_json()
        
        id = req_data['_id']
        
        #remove id from data before updating
        del req_data['_id']
        
        dev = database['developers'].find_one({"_id": id})
        if dev is not None:
            
            database['developers'].update_one({"_id": id}, { "$pull":{"projects":req_data}},
                                                                                upsert=True)
            return jsonify({"data": {"msg": "Project successfully updated"}})
        else:
            return jsonify({"msg": "Project does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001, debug=True)