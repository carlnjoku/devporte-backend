from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit,send, join_room
from flask_cors import CORS
from db import add_room, add_room_members, save_message, save_project, save_project_feeds
from db import database
from bson.objectid import ObjectId
from bson import json_util
import json
import datetime
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

@socketio.on('disconnect', namespace='/private')
def disconnect(data):
    x = database["users"].update({'_id':data}, {'$set':{'online':False}})
    response = 'false'
    emit('user_disconnected_annoucement', response)
    print(data)
    disconnect(request.sid, namespace='/private')
    print(request.sid+ 'yep')


# user enters the room 
@socketio.on('message1', namespace='/private')
def message(data):
    join_room(data['room'])
    emit('join_room_annoucement', data, broadcast=True)
    print('Carlo' + data['room'])

@socketio.on('disconnect1', namespace='/private')
def disconnect():
    
    emit('disconnect_anouncement', 'disconneted', broadcast=True)
    print('disconnected')

# proposal notification
@socketio.on('proposal_notification', namespace='/private')
def manage_notification(data):
    join_room(data['room'])
    emit('proposal_notification_annoucement', data, room=data['room'])
    print(data)


@socketio.on('send_message', namespace='/private')
def handle_send_message(payload):
    message_body = payload['message_body']
    room = payload['room']
    senderId = payload['senderId']
    created_on = payload['created_on']
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
    
    print('my room' + room)
    #Save message
    save_message(room, message_body, senderId, created_on, recepientId, recepient_avatar, recepient_fname, 
    recepient_lname, recepient_email, sender_fname, sender_lname, sender_email, sender_avatar )
    print(payload)
    
    emit('new_message', {'message':message_body, 'sender_avatar':sender_avatar, 'sender_fname':sender_fname, 'sender_lname':sender_fname, 'created_on':created_on}, room=room)

@socketio.on('typing',  namespace='/private' )
def handle_typing(data):
    emit('start_typing', data, broadcast=True)
    #print(data['message'])

@socketio.on('new_job_post')
def handle_new_job_post(payload):
    
    #room = '5e47e537c1f8d023941a76c5'
    employerId = payload['employerId']
    employer_name = payload['employer_name']
    firstname = payload['firstname']
    lastname = payload['lastname']
    email = payload['email']
    title = payload['title']
    job_description = payload['job_description']
    project_type = payload['project_type']
    expertise = payload['expertise']
    experience_level = payload['experience_level']
    payment_type = payload['payment_type']
    project_time = payload['project_time']
    created_on = payload['created_on']
    
    
    #Save project post 
    projectId = save_project(employerId, employer_name, firstname, lastname, email, title, job_description, project_type, expertise, experience_level, payment_type, project_time,created_on)

    print('ProjectId: '+ projectId)
    
    users = database.users.aggregate([
            
            {
                "$match": {'primary_skills':{'title': '12 Angry Men', 'year': 1957, 'title':'Fight Club', 'year':1999}, 'experience_Level' : 'intermediate' } 
            },
            {
                "$project": {"_id":1}
            }
            
        ])

    users = list(users)
    print(list(users))
    for user in users:
        print(user['_id'])
        msg = {'userId':user['_id'], 'jobTitile':payload['title'] }
        feed = {'_id': str(ObjectId()), 'userId':user['_id'], 'projectId': projectId, 'created_on':created_on }

        # Insert into project feeds
        save_project_feeds(feed)
        emit('new_job_post_announcement', msg, room=user['_id'])



if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)