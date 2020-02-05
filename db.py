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
room_member_collection = database['room_members']
message_collection = database['messages']

def add_room(username, email):
    rooms_collection.inset_one({})


def add_room_members(username, email):
    room_member_collection.inset_one({})

def save_message(room_id, text, sender):
    message_collection.inset_one({'room_id':room_id, 'text':text, 'sender':sender})




