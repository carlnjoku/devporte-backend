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
from functools import wraps
import jwt




app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SECRET_KEY'] = 'thisismysecretkey'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
          
        if not token:
            return jsonify({'message':'Token missing!'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = database['users'].find_one({"_id": data['userId']})

        except :
            #return jsonify({'msg':'Token is not valid'})
            #return jsonify({"data": {"error_msg": str(e)}})
            return make_response('Token is not valid', 401, {'WWW-Authenticate' : 'Basic realm = "Login required"'})
            
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/get_user', methods=['GET'])
def get_employer():
    try:
        dev_id = request.args.get('_id')
        print(dev_id)
        dev = database['users'].find_one({"_id": dev_id})
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
            
            x = database["users"].insert_one(req_data)
            return jsonify({"result": req_data})

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
        token = jwt.encode({'userId':user['_id'], 'email':user['email'], 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8'), 'user_type' : user['user_type'], 'userId':user['_id']})
    
    #return jsonify({'message':'Could not verify account'})
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm = "Login required"'})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5010, debug=True)