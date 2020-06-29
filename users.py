from flask import Flask, request, jsonify, make_response
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
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import jwt

from firbase_storage import firebase
import pyrebase
from  mailgun import send_confirmation_email 

from twilio.rest import Client

import random


account_sid = 'AC4f269643438bfae72f0993e99c7ae86e'
auth_token = '5dc15340a9552547c5134fa8482cdc73'
client = Client(account_sid, auth_token)




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

app.config['SECRET_KEY'] = 'thisismysecretkey'

def randomDigits(digits):
    lower = 10**(digits-1)
    upper = 10**digits - 1
    return random.randint(lower, upper)

ALLOWED_EXTENSIONS_ALL_PROFILE = set(['png', 'jpg', 'jpeg', 'gif'])

UPLOAD_FOLDER = 'media'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file_profile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_ALL_PROFILE

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message':'Token missing!'}), 403
            print(token)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = database['users'].find_one({"_id": data['userId']})

        except :
            #return jsonify({'msg':'Token is not valid'})
            #return jsonify({"data": {"error_msg": str(e)}})
            return make_response('Token is not valid', 401, {'WWW-Authenticate' : 'Basic realm = "Login required"'})
            
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/check_status', methods=['GET'])
@token_required
def user_type(current_user):
    user_type = request.args.get('user_type')
    #user_type = 'employer'
    if current_user['user_type'] != user_type:
        return jsonify({'message':'Unauthorized'})
    return jsonify({'message': 'welcome back'}), 200

@app.route('/get_user', methods=['GET'])
def get_employer():
    try:
        user_id = request.args.get('_id')
        print(user_id)
        
        user = database['users'].find_one({"_id": user_id})
        if user is not None:
            return jsonify({"data": user})
        else:
            return jsonify({"data": {"message": "User not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})     




@app.route('/do_email_confirmation', methods=['GET'])
def do_email_confirmation():
    
    try:
        
        id = request.args.get('id')

        print(id)
        member = database['users'].find_one({"_id": id})
        if member is not None:
            database['users'].update({"_id": id}, {"$set": {'confirm_email':True}})
            return jsonify({"data": {"msg": "Email successfully confirmed"}})
        else:
            return jsonify({"msg": "Users does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/get_limited_user_detail', methods=['GET'])
def get_limited_user_detail():
    try:
        dev_id = request.args.get('_id')
        print(dev_id)
        dev = database['users'].find_one({"_id": dev_id}, {'_id':1, 'firstname': 1, 'email': 1, 'confirm_email': 1, 'primary_skills': 1})
        if dev is not None:
            return jsonify({"data": dev})
        else:
            return jsonify({"data": {"message": "User not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})    

@app.route('/signup', methods=['POST'])
def newUser_old():
    
    try:
        
        req_data = request.get_json()
        email = req_data['email']
        
        member = database['users'].find_one({"email": email}, {"_id": 0})
        if member is not None:
            return jsonify({"data": {"message": "User already exisits"}})
        else:
            req_data['_id'] = str(ObjectId())
            
            req_data['password'] = generate_password_hash(req_data['password'], method='sha256')
            
            x = database["users"].insert_one(req_data).inserted_id
            new_data = {
                'userId':x, 
                'email': req_data['email'], 
                'firstname': req_data['firstname'],
                'lastname': req_data['lastname'],
                'user_type': req_data['user_type']
            }
            return jsonify({"result": new_data})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/login', methods=['POST'])
def login():
    
    auth = request.get_json()

    #auth = request.authorization
    print(auth['password'])

    if not auth or not auth['username'] or not auth['password']:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login required"'})

    user = database['users'].find_one({"email": auth['username']})
    print(auth['username'])
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login required"'})
        #return jsonify({'message':'Could not verify account'})
   
    if check_password_hash(user['password'], auth['password']):
        print( user['_id'])
        
        #generate token 
        token = jwt.encode({'userId':user['_id'], 'email':user['email'], 'exp':datetime.datetime.utcnow() + datetime.timedelta(days=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8'), 'user_type' : user['user_type'], 'email': user['email'], 'userId':user['_id'], 'loggedIn': True})
    
    #return jsonify({'message':'Could not verify account'})
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login required"'})

@app.route('/update_profile', methods=['PUT'])
def update_profile():
    
    res={}
    
    file = request.files['avatarBlob']
    if 'avatarBlob' in request.files and allowed_file_profile(file.filename) and 'firstname' in request.form and 'uid' in request.form :

        
        skills = request.form['expertise']
        uid = request.form['uid']
        professional_title = request.form['professional_title']
        firstname = request.form['firstname']
        timezone = request.form['tzone']
        linkedin = request.form['linkedin']
        github = request.form['github']
        website = request.form['website']
        pastprojects = request.form['pastprojects']
        about = request.form['about']
        updated_on = request.form['updated_on']
        calling_code = request.form['calling_code']
        phone = request.form['phone']
        updated_on = request.form['updated_on']
        geoLoc = request.form['geoLoc']
        experience_Level = request.form['experience_Level']
        availability = request.form['availability']
        project_type = request.form['project_type']
        primary_skills = request.form['primary_skills']
        secondary_skills = request.form['secondary_skills']
        

        get_filename = secure_filename(file.filename)
        filename, file_extension = os.path.splitext(get_filename)

        # Generate new file name
        filename = uid+'-'+firstname+file_extension

        filename = filename.replace(' ', '-').lower()

        
    else:
        if not 'avatarBlob' in request.files :res["error"] = "No Image"
        
        if not allowed_file_profile(file.filename):res["error"] = "File type not supported"
        
        
        return jsonify({"result": res})

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
    file = request.files['avatarBlob']

    
    res["media"] = filename

    print(request.files)
    print(json.loads(secondary_skills))

    
   
    data = {
            "expertise":skills,
            "professional_title":professional_title,
            "timezone": timezone,
            "linkedin" : linkedin,
            "github" : github,
            "website" : website,
            "pastprojects" : pastprojects,
            "about" : about,
            "avatar":img_url,
            "experience":[],
            "education":[],
            "other_skills":[],
            "portfolio":[],
            "status" : "new",
            "vetted":False,
            "updated_on": updated_on,
            "calling_code": calling_code,
            "geoLoc": json.loads(geoLoc),
            "phone": phone,
            "experience_Level":experience_Level,
            "availability": availability,
            "project_type":project_type,
            "primary_skills":json.loads(primary_skills),
            "secondary_skills":json.loads(secondary_skills)
        }

    dev = database['users'].find_one({"_id": uid})
    if dev is not None:
        database['users'].update_one({"_id": uid}, {"$set": data},
                                                    upsert=True)
        return jsonify({"data": {"msg": "Developer profile successfully updated"}})
    else:
        return jsonify({"msg": "Admin does not exist"})

    
    os.remove(temp_file)

    return jsonify({"result": 'proposal successfully sent'})




# Update Developer Experience  #

@app.route('/add_experience', methods=['POST'])
def add_experience():
    
    try:
        
        req_data = request.get_json()

        req_data['_id'] = str(ObjectId())
        x = database["experience"].insert_one(req_data)
        return jsonify({"msg": "Experience successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})
    
@app.route('/list_developer_experiences', methods=['GET'])
def list_developers_experiences():
    try:
        userId = request.args.get('_id')
        
        exp = database['experience'].find({'userId':userId}).sort([("timestamp", -1)])
        print(exp.count())
        #return jsonify({"data": candidates.count()})
        print(exp)
        return jsonify({"data": list(exp)})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_one_experience', methods=['GET'])
def get_one_experience():
    try:
        expId = request.args.get('_id')
        exp = database['experience'].find_one({'_id':expId})
        
        return jsonify({"data": exp})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/delete_one_experience', methods=['GET'])
def delete_experience():
    try:
        job_id = request.args.get('_id')
        print(job_id)
        job = database['experience'].find_one({"_id": job_id})
        if job is not None:
            database['experience'].remove({"_id": job_id})
            return jsonify({"data": {"msg": "Experience post was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Experience not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

"""
@app.route('/update_developer', methods=['PUT'])
def edit_developer():
    
    try:
        
        req_data = request.get_json()
        
        id = req_data['userId']

        dev = database['users'].find_one({"_id": id})
        if dev is not None:
            print(req_data)
            database['users'].update_one({"_id": id}, {"$push": {'experience' :req_data}},
                                                        upsert=True)
            return jsonify({"data": {"msg": "Developer profile successfully updated"}})
        else:
            return jsonify({"msg": "user does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/list_developer_experiences', methods=['GET'])
def list_developers_experiences():
    try:
        userId = request.args.get('_id')
        exp = database['users'].find({'_id':userId}, {'experience': 1, '_id':0})
        print(exp.count())
        #return jsonify({"data": candidates.count()})
        print(exp)
        return jsonify({"data": list(exp)})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

"""

@app.route('/add_portfolio', methods=['POST'])
def add_portfolio():
    
    try:
        res={}
        
        file = request.files['image']
        if 'image' in request.files and allowed_file_profile(file.filename) and 'userId' in request.form :

            userId = request.form['userId']
            skills = request.form['skills']
            description = request.form['description']
            project_title = request.form['project_title']
            

            get_filename = secure_filename(file.filename)
            filename, file_extension = os.path.splitext(get_filename)

            # Generate new file name
            filename = userId+'-'+project_title+file_extension

            filename = filename.replace(' ', '-').lower()

            
        else:
            if not 'image' in request.files :res["error"] = "No Image"
            
            if not allowed_file_profile(file.filename):res["error"] = "File type not supported"
            
            
            return jsonify({"result": res})

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
                "skills":json.loads(skills),
                "project_title":project_title,
                "description": description,
                "thumbnail_url" : img_url,
                "userId":userId
            }

        
        #dev = database['users'].find_one({"_id": userId})
        """
        if dev is not None:
            #print(data)
            database['users'].update_one({"_id": userId}, {"$push": {'portfolio' :data}},
                                                            upsert=True)
            return jsonify({"data": {"msg": "Developer profile successfully updated"}})
        else:
            return jsonify({"msg": "user does not exist"})
                
            #except Exception as e:
            #return jsonify({"data": {"error_msg": str(e)}})
        """
        data['_id'] = str(ObjectId())
        x = database["portfolio"].insert_one(data)
        return jsonify({"msg": "Portfolio successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/list_developer_portfolio', methods=['GET'])
def list_developer_portfolio():
    try:
        userId = request.args.get('_id')
        pfo = database['portfolio'].find({'userId':userId})
        print(pfo.count())
        #return jsonify({"data": candidates.count()})
        print(pfo)
        return jsonify({"data": list(pfo)})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/get_one_portfolio', methods=['GET'])
def get_one_portfolio():
    try:
        pfId = request.args.get('_id')
        portf = database['portfolio'].find_one({'_id':pfId})
        
        return jsonify({"data": portf})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/list_developer_primary_skills', methods=['GET'])
def list_developer_primary_skills():
    try:
        userId = request.args.get('_id')
        pfo = database['users'].find({'_id':userId}, {'primary_skills': 1, '_id':0})
        print(pfo.count())
        #return jsonify({"data": candidates.count()})
        print(pfo)
        return jsonify({"data": list(pfo)})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/list_developer_secondary_skills', methods=['GET'])
def list_developer_secondary_skills():
    try:
        userId = request.args.get('_id')
        pfo = database['users'].find({'_id':userId}, {'secondary_skills': 1, '_id':0})
        print(pfo.count())
        #return jsonify({"data": candidates.count()})
        print(pfo)
        return jsonify({"data": list(pfo)})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})



# Technology & tools


@app.route('/add_tool', methods=['POST'])
def new_tech():
    
    try:
        
        req_data = request.get_json()
        
        req_data['_id'] = str(ObjectId())
        x = database["technologies"].insert_one(req_data)
        return jsonify({"msg": "Technology successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/edit_tool', methods=['PUT'])
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


@app.route('/list_tool', methods=['GET'])
def list_tool():
    try:
        tech = database['technologies'].find({}, {'_id': 0})
        print(tech.count())
        #return jsonify({"data": candidates.count()})
        return jsonify({"data": list(tech)})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

# Get tools for add profile, add portfolio and new project
@app.route('/get_tools', methods=['GET'])
def get_tools():
    try:
        tech = database['technologies'].find({}, {'_id': 0, 'tool_name':1})
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


@app.route('/api/v1/create_feedback', methods = ['POST'])
def create_feedback():
    try:
        
        data = {
            "projectId": request.form["projectId"],
            "developerId": request.form["developerId"],
            "employerId": request.form["employerId"],
            "feedback": request.form["feedback"]
        }

        ratings = {
            "complete_job" : int(request.form["complete_job"]),
            "timely_delivery" : int(request.form["timely_delivery"]),
            "on_budget" : int(request.form["on_budget"]),
            "hire_again" : int(request.form["hire_again"])
        }

        complete_job = int(request.form["complete_job"])
        timely_delivery = int(request.form["timely_delivery"])
        on_budget = int(request.form["on_budget"])
        hire_again = int(request.form["hire_again"])

        overall_rating = (complete_job/4) + (timely_delivery/4) + (on_budget/4) + (hire_again/4)
        
        data['_id'] = str(ObjectId())
        data['ratings'] = ratings
        data['overall_rating'] = overall_rating
        reviewId = database['reviews'].insert_one(data).inserted_id

        if reviewId is not None:
            #reviews = database["reviews"].find({'_id':request.form["developerId"]})
            
            y =  database.reviews.aggregate([
                        {
                            "$match": {'developerId': request.form["developerId"]}
                        },
                        {
                            "$group":
                                {
                                "_id":"$developerId",
                                "count": {"$sum": 1},
                                "total_average_rating": {"$avg": "$overall_rating"}
                                
                                }
                            }
                        
                    ])
            
            for average in y:
                ratings = average['total_average_rating']
                total_average_rating = round(ratings, 1)
                count = average['count']
                print(count)
                reviews = {
                    "total_reviews":count,
                    "total_average_rating": total_average_rating
                }
            

                database["users"].update_one({"_id":request.form["developerId"]},{"$set":{"reviews": reviews}})

                """
                developer_email = request.form['developer_email']
                developer_firstname = request.form['developer_firstname']
                developer_lastname = request.form['developer_lastname']
                employer_firstname = request.form['employer_firstname']
                employer_lastname = request.form['employer_lastname']
                """
    
        return jsonify({"data":data})
    
    except Exception as e:
        return jsonify({"data":{"error_msg":str(e)}}) 

@app.route('/phone_verification', methods = ['POST'])
def phone_verification():
    req_data = request.get_json()
    
    body = randomDigits(5)

    message = client.messages.create(
        to = req_data['to'], 
        from_= req_data['from'],
        body= body 
    )
    print(message.sid)

    return message.sid

    return "hi"



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5010, debug=True)



    