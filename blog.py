from flask import Flask, request, jsonify
import shutil
import os
from db import database
import datetime
import base64
from flask_cors import CORS
from bson.objectid import ObjectId
import hashlib 
import json
from users import token_required


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/new_post', methods=['POST'])
def new_post():
    
    try:
        
        req_data = request.get_json()
        
        req_data['_id'] = str(ObjectId())
        x = database["blog"].insert_one(req_data)
        return jsonify({"msg": "article successfully created"})

    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/edit_article', methods=['PUT'])
def edit_article():
    
    try:
        
        req_data = request.get_json()
        
        id = req_data['_id']

        print(req_data)
        member = database['blog'].find_one({"_id": id})
        if member is not None:
            
            database['blog'].update({"_id": id}, {"$set": req_data},
                                                        upsert=True)
            return jsonify({"data": {"msg": "Article successfully updated"}})
        else:
            return jsonify({"msg": "Article does not exist"})
            
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


@app.route('/list_articles', methods=['GET'])
def list_article():
    try:
        art = database['blog'].find({}, {'_id': 0})
        print(art.count())
        #return jsonify({"data": tech.count()})
        return jsonify({"data": list(art), "article_count":art.count()})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/get_article', methods=['GET'])
def get_article():
    try:
        art_id = request.args.get('_id')
        print(art_id)
        art = database['blog'].find_one({"_id": art_id})
        if art is not None:
            return jsonify({"data": art})
        else:
            return jsonify({"data": {"message": "Article not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})

@app.route('/delete_article', methods=['GET'])
def delete_article():
    try:
        art_id = request.args.get('_id')
        tech = database['blog'].find_one({"_id": art_id})
        if tech is not None:
            database['blog'].remove({"_id": art_id})
            return jsonify({"data": {"msg": "Article was successfully removed"}})
        else:
            return jsonify({"data": {"message": "Article not Found"}})
    except Exception as e:
        return jsonify({"data": {"error_msg": str(e)}})


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001, debug=True)