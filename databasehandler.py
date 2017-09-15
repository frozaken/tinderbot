import config
from pymongo import MongoClient
from pymongo import errors
from collections import namedtuple
import pymongo
import json
import urllib.parse
from main import UpdateMatches
from bson.objectid import ObjectId




def ConnectToDB():
    global collection
    try:
        print("Connecting to " + 'mongodb://%s:%s@%s' % (config.dbUser,config.dbPass,config.dbHost))
        client = MongoClient('mongodb://%s:%s@%s' % (config.dbUser,config.dbPass,config.dbHost))
        collection = client[config.dbName][config.dbCollection]
        print("Connection to database succeeded")
    except errors.ServerSelectionTimeoutError as err:
        print("Database connection failed")

def InsertPair(first,second):
    global collection
    insertionObj = {'users':[{'uid':first},{'uid':second}]}
    collection.insert_one(insertionObj)
    print("Inserted %s"%(insertionObj))

def FindPartnerID(findid):
    global collection
    result = collection.find_one({'users':{'uid':findid}})
    if result != None:
        for user in result['users']:
            if(user['uid'] != findid):
                return user['uid']
    return result

def RemoveEntry(_id):
    global collection
    try:
        collection.delete_one({'_id':_id['_id']})
        print("Successfully deleted %s"%(_id['_id']))
    except:
        print("Error deleting")



def GetAll():
    global collection
    entries = []
    returndata = collection.find({})
    for entry in returndata:
        entries.append(entry)
    return entries

def HasMatch(uid):
    global collection
    result = collection.find_one({'users': {'uid': uid}})
    if(result != None):
        return True
    return False

def GetUnmatched():
    data = UpdateMatches()
    unmatched = []
    for key,value in data.items():
        if(not HasMatch(value['match_id'])):
            unmatched.append(value['match_id'])
    return unmatched


if __name__ == "__main__":
    ConnectToDB()
