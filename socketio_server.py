from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit,send, join_room
from flask_cors import CORS
from db import database, add_room, add_room_members
from bson.objectid import ObjectId
from bson import json_util
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")


users = []

@app.route('/')
def index():
    return 'Hello world !'

# connect to websocket
@socketio.on('message', namespace='/private')
def message(data):
    x = database["users"].update({'_id':data}, {'$set':{'online':True}})
    join_room(data['userId'])
    response = 'true'
    emit('user_connected_annoucement', response, broadcast=True)
    print(data)

@socketio.on('disconnect', namespace='/private')
def disconnect(data):
    x = database["users"].update({'_id':data}, {'$set':{'online':False}})
    response = 'false'
    emit('user_disconnected_annoucement', response)
    print(data)
    disconnect(request.sid, namespace='/private')
    print(request.sid+ 'yep')




# initiate sending messages 
# ( This is called when the sender clicks on receiver avatar to initiate chatting)
# userId is the room here
@socketio.on('initiate', namespace='/private')
def message(data):
    join_room(data['room'])
    emit('initiated_annoucement', data, room=data['room'])
    print(data['room'])


# user enters the room 
@socketio.on('message', namespace='/private')
def message(data):
    join_room(data['room'])
    emit('join_room_annoucement', data, room=data['room'])
    print(data)


@socketio.on('send_message', namespace='/private')
def handle_send_message(payload):
    message = payload['message_body']
    room = payload['room']
    print(message)
    print(room)
    emit('new_message', message, room=room)


@app.route('/create_room',  methods = ['GET', 'POST'])
def create_room():
    try:
        req_data = request.get_json()
        req_data['_id'] = str(ObjectId())
        usernames = ['flavoursoft@yahoo.com', 'info@flavoursoft.com', 'carlnjoku@yahoo.com']
        x = database["rooms"].insert_one(req_data)
        if len(usernames):
            for username in usernames: 
                add_room_members(username) 
        return jsonify({"result": "room successfully created"})

    except Exception as e:
        return jsonify({"result": {"error_msg": str(e)}})

@app.route('/list_room_members', methods=['GET'])
def list_room_members():
    try:
        userId = request.args.get('id')
        rooms = database['room_members'].find({"userId":userId}, {'_id': 0}).sort('created_on', -1)
        rooms = json.loads(json_util.dumps(rooms))
        return jsonify({"result": list(rooms)})

    except Exception as e:
        return jsonify({"result":{"error_msg": str(e)}})



if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)