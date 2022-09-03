from http import server
import re
import pymongo
import datetime
import json
from bson import json_util

#Entry var
con = 'mongodb://localhost:27017/'

#MongoDB config
client = pymongo.MongoClient(con)
db = client['chatApp']
users = db['users']
convo = db['convo']
msg = db['messages']
global_convo_id = '630cef3f8e7b79f4e19bd539'
reserved_names = ['Server', 'server', 'Admin', 'admin']

def deploy_db():
    add_user('oNix', 'kurwa123')
    add_user('Rozakin', 'kurwa123')

def user_log_in(user, password):

    entry = users.find_one({'login':user}) # returns None if no match
    
    if entry is not None:
        return entry['password'] == password
    else:
        return False

def convo_check(userA, userB): #konwersacje są tworzone po id, gdzie większe id jest pierwsze (jako user_one)
    
    checkA = users.find_one({'login':userA})
    checkB = users.find_one({'login':userB})

    if checkA is None or checkB is None:
        print(userA, userB)
    
    
    if checkA['user_id'] > checkB['user_id']: #sprawdzamy kolejność zapisu
        user_one = userA
        user_two = userB
    else:
        user_one = userB
        user_two = userA
    
    entry = convo.find_one({'user_one':user_one, 'user_two':user_two})
    
    if entry is None: #this is a new converastion, create new and return it's id
        convo.insert_one({'user_one':user_one,'user_two':user_two, 'last_activity':0})
        return convo.find_one({'user_one':user_one, 'user_two':user_two})['_id']
    else: #conversation exists, return its id
        return entry['_id']

def add_message(sender, reciver, message):
    now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
    if reciver == 'Server':
        msg.insert_one({'convo':global_convo_id, 'sender':sender, 'data':int(now), 'messages':message})
    else:
        convo_id = convo_check(sender, reciver)
        msg.insert_one({'convo':convo_id, 'sender':sender, 'date':int(now), 'message':message})
        convo.update_one({'_id':convo_id}, {'$set' : {'last_activity':int(now)}})

def add_user(login, password):
    new_user = {'user_id':users.count_documents({}),'login':login,'password':password}
    

    if login in reserved_names:
        print('zastrzeżona nazwa')
        return False
    else:
        pass

    if users.find_one({'login':login}) is None: #check if user with login exists
        users.insert_one(new_user)
        print('dodawnie')
        return True
    else:
        print('już jest')
        return False

    
def get_messages(userA, userB): #userA can be a Server, which means it's a global req
    
    if userA == 'Server':
        convo_id = global_convo_id
    else:
        convo_id = convo_check(userA, userB)
    
    data = msg.find({'convo':convo_id})
    j_data = json.loads(json_util.dumps(data))

    return j_data


"""
CONVO
_id
user_one
user_two
last_activity

MSG
_id
convo
sender
date
message

USER
_id

"""