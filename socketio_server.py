from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit,send, join_room, leave_room
from flask_cors import CORS
from db import add_room, add_room_members, save_message, save_message_hire_notification, save_project_feeds, update_freelancer_last_in_room, update_employer_last_in_room
from db import database 
from jobs import upload_files
from bson.objectid import ObjectId
from bson import json_util
import json
import datetime
import time
import requests

apikey = "key-abc123456pqr456xYz"
url = "https://api.mailgun.net/vN/domainAbcdefg.mailgun.org"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


users = []

@app.route('/')
def index():
    return 'Hello world !'

# connect to websocket

@socketio.on('message')
def connect(data):
    print(data)
    x = database["users"].update({'_id':data}, {'$set':{'online':True}})
    join_room(data)
    response = 'true'
    emit('connected', response, broadcast=True)
    print(response)


# @socketio.on('disconnect', namespace='/private')
# def disconnect(data):
#     x = database["users"].update({'_id':data}, {'$set':{'online':False}})
#     response = 'false'
#     emit('user_disconnected_annoucement', response)
#     print(data)
#     disconnect(request.sid, namespace='/private')
#     print(request.sid+ 'yep')


# user enters the room 
@socketio.on('message1', namespace='/private')
def message(data):
    join_room(data['room'])
    emit('join_private_room_annoucement', data, room=data['room'])
    print('Carlo' + data['room'])

@socketio.on('freelancer_leaves_room', namespace='/private')
def freelancer_leaves_room(data):
    print(data['message'])
    leave_room(data['room'])
    update_freelancer_last_in_room(data['room'])
    emit('left_room', data, room=data['room'])
    print('Carlo left room ' + data['room'])

@socketio.on('employer_leaves_room', namespace='/private')
def employer_leaves_room(data):
    print(data['message'])
    leave_room(data['room'])
    update_employer_last_in_room(data['room'])
    emit('left_room', data, room=data['room'])
    print('Carlo left room ' + data['room'])
    
    

# @socketio.on('disconnect1', namespace='/private')
# def disconnect():
    
#     emit('disconnect_anouncement', 'disconneted', broadcast=True)
#     print('disconnected')

# proposal notification
@socketio.on('proposal_notification', namespace='/private')
def manage_notification(data):
    join_room(data['room'])
    emit('proposal_notification_annoucement', data, room=data['room'])
    print(data)

# Hired notification
@socketio.on('message', namespace='/hire')
def manage_hired(data):
    join_room(data['room'])
    emit('join_room_annoucement', data, room=data['room'])
    print(data)

# Send hired notification
@socketio.on('hired', namespace='/hire')
def hired(payload):
    message_body = payload['message']
    message_type = payload['message_type']
    project_title = payload['title']
    room = payload['room']
    senderId = payload['senderId']
    recepientId = payload['recepientId']
    recepient_avatar = payload['recepient_avatar']
    recepient_fname = payload['recepient_fname']
    recepient_lname = payload['recepient_lname']
    recepient_email = payload['recepient_email']
    senderId =  payload['senderId']
    sender_fname =  payload['sender_fname']
    sender_lname = payload['sender_lname']
    sender_email = payload['sender_email']
    sender_avatar = payload['sender_avatar']
    sender_type = payload['sender_type']
    total_milestones = payload['total_milestones']
    offerId = payload['offerId']

    join_room(payload['room'])
    emit('hired_freelancer', payload, room=payload['room'])
    print(payload)

    save_message_hire_notification(room, message_body, message_type, project_title, total_milestones,offerId, senderId, recepientId, recepient_avatar, recepient_fname, 
    recepient_lname, recepient_email, sender_fname, sender_lname, sender_email, sender_avatar, sender_type )
    print(payload)

    

# Send chat message
@socketio.on('send_message', namespace='/private')
def handle_send_message(payload):
    message_body = payload['message_body']
    message_type = payload['message_type']
    room = payload['room']
    senderId = payload['senderId']
    recepientId = payload['recepientId']
    recepient_avatar = payload['recepient_avatar']
    recepient_fname = payload['recepient_fname']
    recepient_lname = payload['recepient_lname']
    recepient_email = payload['recepient_email']
    senderId =  payload['senderId']
    sender_fname =  payload['sender_fname']
    sender_lname = payload['sender_lname']
    sender_email = payload['sender_email']
    sender_avatar = payload['sender_avatar']
    sender_type = payload['sender_type']
    
    print('my room' + room)
    #Save message
    save_message(room, message_body, message_type, senderId, recepientId, recepient_avatar, recepient_fname, 
    recepient_lname, recepient_email, sender_fname, sender_lname, sender_email, sender_avatar, sender_type )
    print(payload)
    
    emit('new_message', {'message':message_body, 'message_type':message_type,  'sender_avatar':sender_avatar, 'sender_fname':sender_fname, 'sender_lname':sender_fname}, room=room)

@socketio.on('typing',  namespace='/private' )
def handle_typing(data):
    join_room(data['room'])
    emit('start_typing', data, room=data['room'])
    print(data)

@socketio.on('new_job_post')
def handle_new_job_post(payload):
    
    #room = '5e47e537c1f8d023941a76c5'
    #employerId = payload['employerId']
    projectId = payload['projectId']
    project_type = payload['project_type']
    required_skills = payload['required_skills']
    experience_level = payload['experience_level']
    created_on = payload['created_on']
    
    
    print(required_skills)

   
    users = database.users.aggregate([
            
            {
                "$match": { 'experience' : experience_level } 
            },
            {
                "$project": {
                    "_id":"$_id",
                    "firstname":"$firtsname",
                    "lastname":"$lastname",
                    "email":"$email"
                }
            }
            
        ])

    users = list(users)
    print(users)
    
    #print(list(users))
    for user in users:
        #print(user['_id'])
        msg = {'userId':user['_id'], 'jobTitile':payload['title'] }
        feed = {'_id': str(ObjectId()), 'userId':user['_id'], 'projectId': projectId, 'created_on':created_on }

        # Insert into project feeds
        save_project_feeds(feed)
        emit('new_job_post_announcement', msg, room=user['_id'])



if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port="5001", debug=True)