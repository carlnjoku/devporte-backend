from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit,send, join_room
from flask_cors import CORS
from db import database, add_room, add_room_members
from bson.objectid import ObjectId


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

users = []


@socketio.on('message', namespace='/')
def message(data):
    x = database["users"].update({'_id':data}, {'$set':{'online':True}})
    response = 'true'
    emit('user_connected_annoucement', response)
    print(data)


@app.route('/')
def index():
    return 'Hello world !'

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




if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)