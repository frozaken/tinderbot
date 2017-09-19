import config
from pymongo import MongoClient
from pymongo import errors
from collections import namedtuple
import pymongo
import json
import urllib.parse
from main import UpdateMatches
from bson.objectid import ObjectId
import sys
import threading



def ConnectToDB():
    global collection
    print("Connecting to %s"%("127.0.0.1"))

    client = MongoClient("127.0.0.1", 27017)
    try:
        if client[config.dbName].authenticate(config.dbUser,config.dbPass):
            collection = client[config.dbName][config.dbCollection]
            print("Connection to database succeeded")
            return True
    except pymongo.errors.OperationFailure as e:
        print("Check credits %s"%e)
        return False
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print("Could not connect through localhost, using config...")
        client = MongoClient(config.dbHost, 27017)
        try:
            if client[config.dbName].authenticate(config.dbUser, config.dbPass):
                collection = client[config.dbName][config.dbCollection]
                print("Connection to database succeeded")
                return True
        except pymongo.errors.OperationFailure as e:
            print("Check credits %s" % e)
            return False
        except pymongo.errors.ServerSelectionTimeoutError as e:
            print("Could not connect through config either, check your settings: %s"%e)
            return False


def InsertBulk(bulk):
    global collection
    if(len(bulk) == 0):
        return
    toInsert = []
    for obj in bulk:
        toInsert.append({'users':[{'uid':obj[0]},{'uid':obj[1]}]})
    collection.insert_many(toInsert)
    print("Inserted %s pair(s)!"%str(len(toInsert)))

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

def GetUnmatched(data):
    print("Getting unmatched")
    if(data == None):
        data = UpdateMatches()
    unmatched = []
    for key,value in data.items():
        if(not HasMatch(value['match_id'])):
            unmatched.append(value['match_id'])
    return unmatched


if __name__ == "__main__":
    ConnectToDB()
