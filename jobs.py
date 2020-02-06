from flask import Flask, request, jsonify
import shutil
import os
from db import database, add_room
import datetime
import base64
from flask_cors import CORS
from bson.objectid import ObjectId
import hashlib 
import json
from PIL import Image
from werkzeug.utils import secure_filename
import jwt
import pandas as pd
import numpy as np



from firbase_storage import firebase
import pyrebase

from users import token_required


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


ALLOWED_EXTENSIONS_ALL = set(['png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'docx', 'doc'])

UPLOAD_FOLDER = 'media'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_ALL

@app.route('/new_project_post', methods=['POST'])
def new_job_post():
    
    try:
        
        req_data = request.get_json()

        data = {
            'employerId': req_data['employerId'],
            'employer_name': req_data['employer_name'],
            'title': req_data['title'],
            'job_description': req_data['job_description'],
            'project_type': req_data['project_type'],
            'expertise': req_data['expertise'],
            'team_number': req_data['team_number'],
            'experience_level': req_data['experience_level'],
            'payment_type': req_data['payment_type'],
            'project_time': req_data['project_time']
        }

        
     
        data['_id'] = str(ObjectId())
        x = database["jobs"].insert_one(data)
        return jsonify({"msg": "Job successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/edit_job', methods=['PUT'])
def edit_job():
    
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

        dev = database['jobs'].find_one({"_id": uid})
        if dev is not None:
            database['jobs'].update_one({"_id": uid}, {"$set": data},
                                                        upsert=True)
            return jsonify({"data": {"msg": "Job profile successfully updated"}})
        else:
            return jsonify({"msg": "Job does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/list_jobs', methods=['GET'])
def list_jobs():
    try:
        job = database['jobs'].find({})
        print(job.count())
        #return jsonify({"data": candidates.count()})
        return jsonify({"data": list(job), "job_count":job.count()})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/get_project', methods=['GET'])
def get_project():
    try:
        projectId = request.args.get('_id')
        print(projectId)
        project = database['jobs'].find_one({"_id": projectId})
        if project is not None:
            return jsonify({"data": project})
        else:
            return jsonify({"data": {"message": "Project post not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/get_project_empId', methods=['GET'])
@token_required
def get_project_empId(current_user):
    try:
        employerId = request.args.get('id')
        print(employerId)
        projects = database['jobs'].find({"employerId": employerId})
        if projects is not None:
            return jsonify({"data": list(projects)})
        else:
            return jsonify({"data": {"message": "No project found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/delete_job', methods=['GET'])
def delete_applicant():
    try:
        job_id = request.args.get('_id')
        print(job_id)
        job = database['jobs'].find_one({"_id": job_id})
        if job is not None:
            database['jobs'].remove({"_id": job_id})
            return jsonify({"data": {"msg": "Job post was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Job not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/new_proposal', methods=['POST'])
def new_proposal():
    
    try:
        
        req_data = request.get_json()
        developerId = req_data["developerId"]
        projectId = req_data["projectId"]
        print(developerId)
        member = database['proposal'].find_one({"developerId": developerId, "projectId":projectId }, {"_id": 0})
        if member is not None:
            return jsonify({"data": {"message": "Already sent a proposal for this project"}})
        else:
            req_data['_id'] = str(ObjectId())

            proposal = database["proposal"].insert_one(req_data)
            
            # Create a chat room using the proposalId
            add_room(proposal['proposalId'], developerId, req_data['avatar'],  req_data['firstname'], req_data['lastname'], req_data['email'], req_data['created_on'])
            return jsonify({"result": 'proposal successfully sent'})

    except Exception as e:
        return jsonify({"result": {"error_msg": str(e)}})


@app.route('/get_proposal_projectId_0', methods=['GET'])
def get_proposal_projectId_0():
    try:
        res = []
        projectId = request.args.get('_id')
        #projectId = '5e123102abe2c53ede1acbb4'
        #print(projectId)
        proposals = list(database['proposal'].find({"projectId": projectId}))
        #print(proposals)
        for proposal in proposals:
            prop = database['users'].find_one({"_id": proposal['developerId']})
            res.append(prop)

        return jsonify({"data": res})         
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/get_proposal_projectId', methods=['GET'])
def get_proposal_projectId():
    try:
    
        projectId = request.args.get('_id')
  
        proposals = list(database['jobs'].find({"projectId": projectId}))
        
        #print(proposals)

        #prop = list(database['users'].find({}))

        results = database.proposal.aggregate([
            {
            "$match": { 'projectId': projectId}
            },
            {
                "$lookup": {
                "from": 'users',
                "foreignField": '_id',
                "localField": 'developerId',
                "as": 'user'
                }
            },
            {
                "$unwind":"$user"
            }
        ])
       
        #print(list(results))
     
        return jsonify({"data": list(results)})         
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/get_proposal_projectId_old', methods=['GET'])
def get_proposal_projectId_old():
    try:
        
        projectId = request.args.get('_id')
        print(projectId)
        proposals = database['proposal'].find({"projectId": projectId})
        if proposals is not None:
            return jsonify({"data": list(proposals)})
        else:
            return jsonify({"data": {"message": "No proposals found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/new_contract', methods=['POST'])
def new_contract():
    
    try:
        
        req_data = request.get_json()
        
        req_data['_id'] = str(ObjectId())
        x = database["contracts"].insert_one(req_data)
        return jsonify({"msg": "Contract successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_chat_session_by_projectId', methods=['GET'])
def get_chat_session_by_projectId():
    try:
        
        projectId = request.args.get('projectId')
        developerId = request.args.get('developerId')
        print(projectId)
        print(developerId)
        proposals = database['chat_sessions'].find_one({"projectId": projectId, 'ouserId':developerId})
        if proposals is not None:
            print(proposals)
            return jsonify({"data": proposals})
        else:
            return jsonify({"data": {"message": "No proposals found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/add_file', methods=['POST'])
def add_file():
    res = {}

    file = request.files['image']
    if 'image' in request.files and allowed_file(file.filename) and 'employerId' in request.form and 'developerId' in request.form and 'projectId' in request.form  :
    
        employerId = request.form['employerId']
        developerId = request.form['developerId']
        projectId = request.form['projectId']

        get_filename = secure_filename(file.filename)
        filename, file_extension = os.path.splitext(get_filename)
        
    
    else:
        if not 'image' in request.files :res["error"] = "No Image"
        if not allowed_file(file.filename):res["error"] = "File type not supported"
    
        
        return jsonify({"data": res})

    filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)


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

    #initiate as array
    developerId = [developerId]
    data = {
        'employerId':employerId,
        'developerId':developerId,
        'projectId':projectId,
        'file_url':img_url
    }

    data['_id'] = str(ObjectId())
    x = database["files"].insert_one(data)


    #memberID = request.form['memberID']
    #database['users'].update({'_id': memberID}, {"$set": {'profile_bg':profile_bg}})

    os.remove(temp_file)

    return jsonify({"data": res})

@app.route('/get_project_file_projectId', methods=['GET'])
def get_project_file_projectId():
    try:
        projectId = request.args.get('_id')
        print(projectId)
        proposals = database['files'].find({"projectId": projectId})
        if proposals is not None:
            return jsonify({"data": list(proposals)})
        else:
            return jsonify({"data": {"message": "No file found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/new_task', methods=['POST'])
def new_tast():
    
    try:
        
        #convert form data to json
        req_data = request.form.to_dict(flat=True)
        

        print(req_data)
        
        req_data['_id'] = str(ObjectId())
        x = database["tasks"].insert_one(req_data)
        return jsonify({"msg": "Task successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/edit_task', methods=['PUT'])
def edit_task():
    
    try:
        
        req_data = request.get_json()

        print(req_data)
        
        id = req_data['_id']
       
        member = database['tasks'].find_one({"_id": id})
        if member is not None:
            
            database['tasks'].update_one({"_id": id}, {"$set": req_data},
                                                        upsert=True)
            return jsonify({"data": {"msg": "Task successfully updated"}})
        else:
            return jsonify({"msg": "Task does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})



@app.route('/get_task_projectId', methods=['GET'])
@token_required
def get_task_projectId(current_user):

    try:
        #print(current_user)
        #if not current_user.userInfo.user_type == 'employer':
            #return jsonify({"data":"you are not autorized to access the page"})
       
        projectId = request.args.get('id')
        print(projectId)
        tasks = database['tasks'].find({"projectId": projectId})
        if tasks is not None:
            return jsonify({"data": list(tasks)})
        else:
            return jsonify({"data": {"message": "No task found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})



@app.route('/get_task', methods=['GET'])
def get_task():
    try:
        taskId = request.args.get('_id')
        print(taskId)
        task = database['tasks'].find_one({"_id": taskId})
        if task is not None:
            return jsonify({"data": task})
        else:
            return jsonify({"data": {"message": "Task post not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/delete_task', methods=['GET'])
def delete_task():
    try:
        taskId = request.args.get('_id')
        
        task = database['tasks'].find_one({"_id": taskId})
        if task is not None:
            database['tasks'].remove({"_id": taskId})
            return jsonify({"data": {"msg": "Task was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Job not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/new_milestone', methods=['POST'])
def new_milestone():
    
    try:
        
        #convert form data to json
        req_data = request.get_json()
        

        print(req_data)
        
        req_data['_id'] = str(ObjectId())
        x = database["milestones"].insert_one(req_data)
        return jsonify({"msg": "Task successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/get_milestones_projectId', methods=['GET'])
def get_milestones_projectId():

    try:
        
        projectId = request.args.get('id')
        print(projectId)
        tasks = database['milestones'].find({"projectId": projectId})
        if tasks is not None:
            return jsonify({"data": list(tasks)})
        else:
            return jsonify({"data": {"message": "No milestone found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/new_chat_message', methods=['POST'])
def new_chat_message():
    
    try:
        
        req_data = request.get_json()
        
        req_data['_id'] = str(ObjectId())
        x = database["chatmessages"].insert_one(req_data)
        return jsonify({"msg": "Message successfully sent"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5008, debug=True)
