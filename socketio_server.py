from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit,send
from flask_cors import CORS


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

users = {}
@app.route('/')
def index():
    return 'Hello world !'

@socketio.on('message')
def message(data):
    #send(data)
    print(data)

@socketio.on('username', namespace='/chat')
def get_username(username):
    users[username] = request.sid
    print(users)

@socketio.on('send_message', namespace='/chat')
def send_message(payload):
    recipient_sid = payload[users['username']]
    message = payload['message']
    room = recipient_sid
    emit('new_message', message)
    print('This should be the room' +room)






if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)