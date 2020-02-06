from pymongo import MongoClient

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

def add_room(room, userId, avatar, firstname, lastname, email, created_on):
    rooms_collection.inset_one({'room':room, 'userId':userId, 'avatar': avatar,  'firstname': firstname, 'lastname': lastname, 'email':email, 'created_on': created_on })


def add_room_members(username, email):
    room_members_collection.inset_one({})

def save_message(room_id, text, sender, created_on):
    messages_collection.inset_one({'room_id':room_id, 'text':text, 'sender':sender, 'created_on':created_on})

def get_messages(room_id):
    return list(messages_collection.find({'room_id':room_id}))



