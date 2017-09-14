import config
from pymongo import MongoClient
from pymongo import errors
from collections import namedtuple
import pymongo
import json
import urllib.parse
from main import UpdateMatches



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
    for match in data:
        if(not HasMatch(match)):
            unmatched.append(match)
    return unmatched


if __name__ == "__main__":
    ConnectToDB()
