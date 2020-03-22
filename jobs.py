from flask import Flask, request, jsonify
import shutil
import os
from db import database, add_room, send_notification
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
from bson import json_util
from itertools import groupby



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
ALLOWED_EXTENSIONS_ALL_PROFILE = set(['png', 'jpg', 'jpeg', 'gif'])

UPLOAD_FOLDER = 'media'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_ALL

def allowed_file_profile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_ALL_PROFILE

@app.route('/new_project_post', methods=['POST'])
def new_job_post():
    
    try:
        
        req_data = request.get_json()

        data = {
            'employerId': req_data['employerId'],
            'employer_name': req_data['employer_name'],
            'firstname': req_data['firstname'],
            'lastname': req_data['lastname'],
            'email': req_data['email'],
            'title': req_data['title'],
            'job_description': req_data['job_description'],
            'project_type': req_data['project_type'],
            'expertise': req_data['expertise'],
            'team_number': req_data['team_number'],
            'experience_level': req_data['experience_level'],
            'payment_type': req_data['payment_type'],
            'project_time': req_data['project_time'],
            'created_on': req_data['created_on']   
        }

        experience_level = req_data['experience_level']
        skills = req_data['expertise']

        
     
        data['_id'] = str(ObjectId())
        x = database["jobs"].insert_one(data)

        usrs = database.users.aggregate([
            {
                "$match":{'primary_skills': { '$elemMatch': {'title': '12 Angry Men', 'year': 1957, 'title':'Fight Club', 'year':1999}}, 'experience_Level': experience_level},
                
            },
            {
                "$project": {"_id":1}
            },
            {
                "$count": "firstname"
            }
            
        ])

        

        if usrs is not None:
            return jsonify({"data": list(usrs)})
        else:
            return jsonify({"data": {"message": "users"}})

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
        job = database['jobs'].find({}).sort('created_on', -1)
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
        status = request.args.get('status')
        print(employerId)
        projects = database['jobs'].find({"employerId": employerId, "status":status})
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


@app.route('/new_proposal_old', methods=['POST'])
def new_proposal_old():
    
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

            proposal_id = database["proposal"].insert_one(req_data).inserted_id
            
            #print(list(proposal))
            # Create a chat room using the proposalId
            #database['room'].insert_one({'room':proposal_id, 'project_title':req_data['project_title'], 'userId':developerId, 'avatar': req_data['avatar'],  'firstname': req_data['firstname'], 'lastname': req_data['lastname'], 'email':req_data['email'], 'created_on': req_data['created_on'] })
            add_room(proposal_id, req_data['project_title'], developerId, req_data['avatar'],  req_data['firstname'], req_data['lastname'], req_data['email'], req_data['created_on'])
            return jsonify({"result": 'proposal successfully sent'})

    except Exception as e:
        return jsonify({"result": {"error_msg": str(e)}})

@app.route('/new_proposal', methods=['POST'])
def new_proposal():
    res={}
  
    developerId = request.form['developerId']
    employerId = request.form['employerId']
    projectId= request.form['projectId']
    project_title  = request.form['project_title']
    firstname  = request.form['firstname']
    lastname  = request.form['lastname']
    employer_lastname = request.form['employer_lastname']
    employer_firstname = request.form['employer_firstname']
    email = request.form['email']
    bid  = request.form['bid']
    estimated_finish_time  = request.form['estimated_finish_time']
    cover_letter  = request.form['cover_letter']
    created_on  = request.form['created_on']
    avatar = request.form['avatar']
    room_members = json.loads(request.form['room_members'])
    
      
   
    data =  {
        'developerId': developerId,
        'employerId': employerId,
        'projectId' : projectId,
        'project_title'  : project_title,
        'firstname'  : firstname,
        'lastname'  : lastname,
        'email' : email,
        'bid'  : bid,
        'estimated_finish_time' : estimated_finish_time,
        'cover_letter'  : cover_letter,
        'created_on'  : created_on,
        'avatar':avatar
    }

    
    """
    member_data = []

    member_data.append({
        'developerId': developerId,
        'projectId' : projectId,
        'project_title'  : project_title,
        'firstname'  : firstname,
        'lastname'  : lastname,
        'email' : email,
        'created_on'  : created_on,
        'avatar':avatar,
        'isRoomAdmin': True
    })

    member_data.append({
        'developerId': developerId,
        'projectId' : projectId,
        'project_title'  : project_title,
        'firstname'  : firstname,
        'lastname'  : lastname,
        'email' : email,
        'created_on'  : created_on,
        'avatar':avatar,
        'isRoomAdmin': True
    })
    
"""
    member = database['proposal'].find_one({"developerId": developerId, "projectId":projectId }, {"_id": 0})
    if member is not None:
        return jsonify({"data": {"message": "Already sent a proposal for this project"}})
    else:
        data['_id'] = str(ObjectId())

        proposal_id = database["proposal"].insert_one(data).inserted_id
        
        # Create new chat room
        add_room(proposal_id, employerId, developerId, created_on, room_members, firstname, lastname, avatar, employer_firstname, employer_lastname)

    return jsonify({"result": 'proposal successfully sent'})


"""
@app.route('/new_proposal', methods=['POST'])
def new_proposal():
    res={}
    file = request.files['image']
    if 'image' in request.files and allowed_file_profile(file.filename) and 'firstname' in request.form and 'lastname' in request.form and 'email' in request.form and 'developerId' in request.form :
    
        developerId = request.form['developerId']
        projectId= request.form['projectId']
        project_title  = request.form['project_title']
        firstname  = request.form['firstname']
        lastname  = request.form['lastname']
        email = request.form['email']
        bid  = request.form['bid']
        hourly_rate  = request.form['hourly_rate']
        cover_letter  = request.form['cover_letter']
        created_on  = request.form['created_on']
      
        get_filename = secure_filename(file.filename)
        filename, file_extension = os.path.splitext(get_filename)

        # Generate new file name
        filename = developerId+'-'+firstname+file_extension

        filename = filename.replace(' ', '-').lower()

        
    else:
        if not 'image' in request.files :res["error"] = "No Image"
        
        if not allowed_file_profile(file.filename):res["error"] = "File type not supported"
        
        
        return jsonify({"result": 'what'})

    filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    
    
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

    
   
    data = {
        'developerId': developerId,
        'projectId' : projectId,
        'project_title'  : project_title,
        'firstname'  : firstname,
        'lastname'  : lastname,
        'avatar' : img_url,
        'email' : email,
        'bid'  : bid,
        'hourly_rate' : hourly_rate,
        'cover_letter'  : cover_letter,
        'created_on'  : created_on,
    }

    member = database['proposal'].find_one({"developerId": developerId, "projectId":projectId }, {"_id": 0})
    if member is not None:
        return jsonify({"data": {"message": "Already sent a proposal for this project"}})
    else:
        data['_id'] = str(ObjectId())

        proposal_id = database["proposal"].insert_one(data).inserted_id
        
        #print(list(proposal))
        # Create a chat room using the proposalId
        #database['room'].insert_one({'room':proposal_id, 'project_title':req_data['project_title'], 'userId':developerId, 'avatar': req_data['avatar'],  'firstname': req_data['firstname'], 'lastname': req_data['lastname'], 'email':req_data['email'], 'created_on': req_data['created_on'] })
        add_room(proposal_id, data['project_title'], developerId, data['avatar'],  data['firstname'], data['lastname'], data['email'], data['created_on'])
    
    
    


    os.remove(temp_file)

    return jsonify({"result": 'proposal successfully sent'})

"""
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

@app.route('/get_one_proposal')
def get_one_proposal():
    try:
        proposalId = request.args.get('proposalId')
        proposal = database['proposal'].find_one({'_id':proposalId})

        return jsonify({'result': proposal})
    except Exception as e:
        return jsonify({'data': {'error_msg':str(e)}})

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


@app.route('/get_chat_messages', methods=['GET'])
def get_chat_messages():
    try:
        room = request.args.get('room')
        messages = database['chatmessages'].find({"room": room})
        if messages is not None:
            return jsonify({"data": list(json.loads(json_util.dumps(messages)))}) 
            
        else:
            return jsonify({"data": {"message": "No messages found"}})
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

@app.route('/list_room_members', methods=['GET'])
def list_room_members():
    try:
        userId = request.args.get('id')
        rooms = database['room_members'].find({"userId":userId}, {'_id': 0}).sort('created_on', -1)
        rooms = json.loads(json_util.dumps(rooms))
        return jsonify({"result": list(rooms)})

    except Exception as e:
        return jsonify({"result":{"error_msg": str(e)}})


@app.route('/get_rooms_by_user', methods=['GET'])
def get_rooms_by_user():
    try:
    
        userId = request.args.get('_id')
  
        rooms = database['rooms'].find({'developerId': userId})
       
        return jsonify({"data": list(json.loads(json_util.dumps(rooms)))})         
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_rooms_by_user_employer', methods=['GET'])
def get_rooms_by_user_employer():
    try:
    
        userId = request.args.get('_id')
  
        rooms = database['rooms'].find({'employerId': userId})
       
        return jsonify({"data": list(json.loads(json_util.dumps(rooms)))})         
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_single_room_details', methods=['GET'])
def get_single_room_details():
    try:
    
        roomy = request.args.get('_id')
  
        room = database['rooms'].find_one({'room': roomy})
       
        return jsonify({"data": json_util.dumps(room)})         
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

    

@app.route('/get_rooms_by_employer', methods=['GET'])
def get_rooms_by_employer():
    try:
    
        userId = request.args.get('_id')
  
        rooms = database['rooms'].find({'employerId': userId})
       
        return jsonify({"data": list(json.loads(json_util.dumps(rooms)))})         
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


"""
@app.route('/get_rooms_by_user', methods=['GET'])
def get_rooms_by_user():
    try:
    
        userId = request.args.get('_id')
  
        results = database.rooms.aggregate([
            {
            "$match": { 'developerId': userId}
            },
            {
                "$lookup": {
                "from": 'chatmessages',
                "foreignField": 'room',
                "localField": 'room',
                "as": 'chatmessage'
                }
            },
            {
                "$unwind":"$chatmessage"
            }  
        ])
       
       
        
     
        return jsonify({"data": list(json.loads(json_util.dumps(results)))})         
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5008, debug=True)
