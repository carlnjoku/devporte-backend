from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit,send, join_room
from flask_cors import CORS
from db import database
from bson.objectid import ObjectId


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

users = []
@app.route('/')
def index():
    return 'Hello world !'

@socketio.on('message')
def message(data):
    #send(data)
    print(data)

@socketio.on('username', namespace='/chat')
def get_username(username):
    users.append({username: request.sid})
    print(users)

@socketio.on('send_message', namespace='/chat')
def send_message(payload):
    recipient_sid = request.sid
    message = payload['message']
    room = recipient_sid
    #emit('new_message', message, room, broadcast=True)
    #print('This should be the room' +room)

    users.append(request.sid)

    #room = recipient_sid
    #join_room(room)
    
    emit('new_message', message, room=recipient_sid)


@app.route('/create_room')
def create_room():
    try:
        req_data = request.get_json()

        req_data['_id'] = str(ObjectId())
        x = database["rooms"].insert_one(req_data)
        return jsonify({"result": "room successfully created"})

    except Exception as e:
        return jsonify({"result": {"error_msg": str(e)}})




if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)