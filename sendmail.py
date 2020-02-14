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
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True
#Gmail SMTP port (TLS): 587.
#SMTP port (SSL): 465.
#SMTP TLS/SSL required: yes.
app.config['MAIL_USERNAME'] = 'carlnjoku@gmail.com'
app.config['MAIL_PASSWORD'] = 'angel@4340'

mail = Mail(app)


cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def index():
    message_body = "Verify your email address to complete registration  Hi Chinedu,Thanks for your interest in joining Upwork! To complete your registration, we need you to verify your email address.Verify Email Please note that not all applications to join Upwork are accepted. We will notify you of our decision by email within 24 hours.Thanks for your time,The Upwork Team"
    msg = Message('Hello there !', sender="admin@devporte.com", recipients=['flavoursoft@gmal.com'] )
    mail.send(msg)
    return "Hello world"


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5012, debug=True)