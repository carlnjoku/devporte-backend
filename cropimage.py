from flask import Flask, request, jsonify
import shutil
import os
from db import database
import datetime
import base64
from flask_cors import CORS
from bson.objectid import ObjectId
import hashlib 
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


ALLOWED_EXTENSIONS_ALL = set(['png', 'jpg', 'jpeg', 'gif', 'mp4'])

UPLOAD_FOLDER = 'media/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_ALL

@app.route('/post_images', methods=['POST'])
def post_images():
    res = {}

    file = request.files['image']
    if 'image' in request.files and allowed_file(file.filename) :
    
        

        img = Image.open(file)
        #heightwidth = 350
        #wpercent = int(heightwidth / img.height * img.width)
        #hsize = int((float(img.size[1]) * float(wpercent)))
        area =(100, 0, 700,350)
        #cropped = img.crop(basewidth, hsize)
        #img.show()
        #cropped.show('newimage.png')
        #new_size = img.crop((0, 0, wpercent, heightwidth))
        new_size = img.crop(area)

        
        #new_size.show()
        #print(wpercent)
        print(img.width)

        #imagefit = ImageOps.fit(file, (150, 170), Image.ANTIALIAS, 0, (0.5, 0))

        #imagefit.show()
        
    else:
        if not 'image' in request.files :res["error"] = "No Image"
        if not allowed_file(file.filename):res["error"] = "File type not supported"
    
        
        return jsonify({"data": res})

    

    return jsonify({"data": res})

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001, debug=True)