from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, request, jsonify
import time


# db_name = 'devport_engine'
# db_host_mongo = '45.79.27.141'
# db_port_mongo = '27017'
# username='carlnjoku' 
# password='fuckyouasshole'
# mongo_uri = "mongodb://{username}:{password}@{db_host}:{db_port_mongo}/{db_name}".format(
# username=username, password=password,
# db_host=db_host_mongo,
# db_port_mongo=db_port_mongo, db_name=db_name)
# client = MongoClient(mongo_uri)
# database = client[db_name]

db_name = 'devporte'
db_host_mongo = 'localhost'
db_port_mongo = '27017'
#username='carlnjoku' 
#password='fuckyouasshole'
mongo_uri = "mongodb://{db_host}:{db_port_mongo}/{db_name}".format(
db_host=db_host_mongo,
db_port_mongo=db_port_mongo, db_name=db_name)
client = MongoClient(mongo_uri)
database = client[db_name]


rooms_collection = database['rooms']
room_members_collection = database['room_members']
messages_collection = database['chatmessages']
users_collection = database['users']
project_collection = database['jobs']
project_feeds_colection = database['project_feeds']



def add_room(room, employerId, developerId, created_on, room_members_data, firstname, lastname, avatar, employer_firstname, employer_lastname, project_title):
    room_id = rooms_collection.insert_one({'room':room, 'employerId': employerId, 'developerId': developerId, 'created_on':created_on, 'firstname':firstname, 'lastname':lastname, 'avatar':avatar, 'employer_firstname':employer_firstname, 'employer_lastname':employer_lastname, 'project_title':project_title }).inserted_id
    add_room_members(room_id, room, room_members_data)
    #save_message(room_id, room, message_body, senderId, created_on, recepientId, recepient_avatar, recepient_fname, recepient_lname, recepient_email)
    return room_id

# Add single room member
def add_room_member(room_id, room, projectId, project_title, userId, avatar, firstname, lastname, email, created_on, isRoomAdmin=False):
    room_members_collection.insert_one({'room_id':room_id, 'room':room, 'project_title':project_title, 'userId':userId, 'avatar': avatar,  'firstname': firstname, 'lastname': lastname, 'email':email, 'created_on': created_on, 'isRoomAdmin':isRoomAdmin, })

# Add multiple room members
def add_room_members(room_id,room, room_members_data): 
    #Update incoming member data by adding room_id and room to member_data
    room_members_data[0].update(room = room, room_id = room_id)
    room_members_data[1].update(room = room, room_id = room_id)

    for room_member in room_members_data:
        
    
        room_member['_id'] = str(ObjectId())
        room_members_collection.insert(room_member)
   
    room_members_collection.insert_many(room_members_data)

def save_message(room, message_body, message_type, senderId, recepientId, recepient_avatar, recepient_fname, recepient_lname, recepient_email, sender_fname, sender_lname, sender_email, sender_avatar, sender_type):
    message = messages_collection.insert_one({'_id': str(ObjectId()), 'room':room, 'message_body': message_body, 'message_type':message_type, 'senderId':senderId, 'created_date':int(time.time()), 'recepientId': recepientId, 'recepient_avatar':recepient_avatar, 'recepient_fname':recepient_fname, 'recepient_lname':recepient_lname, 'recepient_email':recepient_email,
    'sender_fname':sender_fname, 'sender_lname':sender_lname, 'sender_email':sender_email, 'sender_avatar':sender_avatar, 'sender_type':sender_type})

def save_message_hire_notification(room, message_body, message_type, project_title, total_milestones, offerId, senderId, recepientId, recepient_avatar, recepient_fname, recepient_lname, recepient_email, sender_fname, sender_lname, sender_email, sender_avatar, sender_type):
    message = messages_collection.insert_one({'_id': str(ObjectId()), 'room':room, 'message_body': message_body, 'message_type':message_type, 'project_title':project_title, 'total_milestones':total_milestones, 'offerId':offerId, 'senderId':senderId, 'created_date':int(time.time()), 'recepientId': recepientId, 'recepient_avatar':recepient_avatar, 'recepient_fname':recepient_fname, 'recepient_lname':recepient_lname, 'recepient_email':recepient_email,
    'sender_fname':sender_fname, 'sender_lname':sender_lname, 'sender_email':sender_email, 'sender_avatar':sender_avatar, 'sender_type':sender_type})
    
def save_message_accept_offer_notification(room, message_body, message_type, senderId, recepientId, recepient_avatar, recepient_fname, recepient_lname, recepient_email, sender_fname, sender_lname, sender_email):
    message = messages_collection.insert_one({'_id': str(ObjectId()), 'room':room, 'message_body': message_body, 'message_type':message_type, 'senderId':senderId, 'created_date':int(time.time()), 'recepientId': recepientId, 'recepient_avatar':recepient_avatar, 'recepient_fname':recepient_fname, 'recepient_lname':recepient_lname, 'recepient_email':recepient_email,
    'sender_fname':sender_fname, 'sender_lname':sender_lname, 'sender_email':sender_email})
    

    # save_message_hire_notification(room, message_body, message_type , senderId, recepient_fname, 
    # recepient_lname, recepient_email, sender_fname, sender_lname, sender_email, sender_type )
    


def get_messages(room_id):
    return list(messages_collection.find({'room_id':room_id}))

def send_notification(expertise, experience_level):
    pipeline = { 'primary_skills':expertise, 'experience_level':experience_level }
    #users = users_collection.aggregate([{"$match":pipeline}])
    #print(expertise)
    #print(list(users))
    #return list(users)

    #pipeline = { 'pri':expertise, 'experience_level':experience_level }

    #[{"$match": {'primary_skills':{'title': '12 Angry Men', 'year': 1957}, 'experience_Level' : 'intermediate' } }]
    users = users_collection.aggregate([{"$match":{ 'primary_skills': {'title': '12 Angry Men', 'year': 1957}, 'experience_level':'intermediate' }}])
    #return jsonify({"msg": "Job successfully created!!!"})
    #print('you')
    return (users)

#def save_project(employerId, employer_name, firstname, lastname, email, title, job_description, project_type, expertise, experience_level, payment_type, project_time, status, initial_route, upload_files, created_on):
    #projectId = project_collection.insert_one({'_id': str(ObjectId()), 'employerId':employerId, 'employer_name':employer_name, 'firstname':firstname, 'lastname':lastname, 'email':email, 'title':title, 'job_description':job_description, 'project_type':project_type, 'expertise':expertise, 'experience_level':experience_level, 'payment_type':payment_type, 'project_time':project_time, 'project_files':upload_files, 'status':status, 'initial_route': initial_route, 'created_on':created_on}).inserted_id
    
    #return (projectId)
    

def save_project_feeds(feed):
    feed = project_feeds_colection.insert_one(feed)

def update_project(projectId, bid):
    project_collection.update_one({'_id':projectId}, {'$addToSet':{'bid':int(bid)}})


def update_freelancer_last_in_room(room):
    rooms_collection.update_one({'room':room}, {'$set': {'freelancer_last_in_room':int(time.time())}})

def update_employer_last_in_room(room):
    rooms_collection.update_one({'room':room}, {'$set': {'employer_last_in_room':int(time.time())}})
    