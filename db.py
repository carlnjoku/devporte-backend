from pymongo import MongoClient
from bson.objectid import ObjectId

db_name = 'devporte'
db_host_mongo = '0.0.0.0'
db_port_mongo = '27017'
mongo_uri = "mongodb://{db_host}:{db_port_mongo}/{db_name}".format(
    #username=username, password=password, db_host=db_host_mongo,
    db_host=db_host_mongo,
    db_port_mongo=db_port_mongo, db_name=db_name)
client = MongoClient(mongo_uri)
database = client[db_name]

rooms_collection = database['rooms']
room_members_collection = database['room_members']
messages_collection = database['messages']

def add_room(room, created_on, room_members_data):
    room_id = rooms_collection.insert_one({'room':room, 'created_on':created_on }).inserted_id
    add_room_members(room_id,room, room_members_data)
    return room_id

# Add single room member
def add_room_member(room_id, room, projectId, project_title, userId, avatar, firstname, lastname, email, created_on, isRoomAdmin=False):
    room_members_collection.insert_one({'room_id':room_id, 'room':room, 'project_title':project_title, 'userId':userId, 'avatar': avatar,  'firstname': firstname, 'lastname': lastname, 'email':email, 'created_on': created_on, 'isRoomAdmin':isRoomAdmin, })

# Add multiple room members
def add_room_members(room_id,room, room_members_data): 
    #Update incoming member data by adding room_id and room to member_data
    room_members_data[0].update(room = room, room_id = room_id)
    room_members_data[1].update(room = room, room_id = room_id)
   
    room_members_collection.insert_many(room_members_data)

def save_message(room_id, text, sender, created_on):
    messages_collection.insert_one({'room_id':room_id, 'text':text, 'sender':sender, 'created_on':created_on})

def get_messages(room_id):
    return list(messages_collection.find({'room_id':room_id}))