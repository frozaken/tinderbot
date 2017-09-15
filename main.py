# This Python file uses the following encoding: utf-8
import fb_auth_token;
import config;
import tinder_api;
import features;
import json
from collections import namedtuple
import random
import time
from threading import Thread
import threading
import sys;
import datetime as dt
import databasehandler as dbHandler



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def AuthLoop():
    while(True):
        awake.wait()

        print('Authorizing')
        #saetter authorized til false
        authorized.clear()
        tinder_api.get_auth_token(config.fb_access_token, config.fb_user_id)
        self=tinder_api.get_self()
        config.myTinderID = self['_id']
        config.myTinderName = self['name']
        authorized.set()
        tinder_api.change_preferences(age_filter_min=18, age_filter_max=22, distance_filter=30)
        features.sleep(random.randint(1000,2000))

def SleepLoop():

    while(True):
        #server er 2 timer bagud
        if True:#int(dt.datetime.now().hour) >= 5:
            print(bcolors.OKBLUE + "We are awake" + bcolors.ENDC)
            awake.set()
        else:
            print(bcolors.FAIL + "Sleeping ZzZZz, waking up at 7!" + bcolors.ENDC)
            awake.clear()

        features.sleep(30*60)

def ChatLoop():

    while(True):
        #venter paa vi er authorized
        authorized.wait()
        awake.wait()

        if len(UpdateMatches()) == 0:
            print(bcolors.OKBLUE+ "Chat loop is waiting for matches... we currently have none :(" + bcolors.ENDC)
        else:


            unmatched = dbHandler.GetUnmatched()
            matches = []
            if(len(unmatched)>=2):
                for i in range(0,(len(unmatched)//2)*2,2):
                    matches.append([unmatched[i],unmatched[i+1]])
            else:
                print(bcolors.OKGREEN + "No new matches to be made this time" +bcolors.ENDC)
            for match in matches:
                print("Its a match!")
                dbHandler.InsertPair(match[0],match[1])

            allInternalMatches = dbHandler.GetAll()
            matches = UpdateMatches()
            for internal in allInternalMatches:
                for i in range(0,2):
                    users = internal['users']

                    msgFromUs = GetOurMessages(users[i]['uid'],matches)
                    #print("Msg from us %s"%msgFromUs)
                    msgFromThem = GetForeignMessages(users[(i+1)%2]['uid'],matches)

                    if(msgFromThem == "unmatch" or msgFromUs == "unmatch"):
                        tinder_api.unmatch(users[0]['uid'])
                        tinder_api.unmatch(users[1]['uid'])
                        dbHandler.RemoveEntry(internal)
                        break
                    else:
                        #print("Msg from them %s"%msgFromThem)
                        msgToSend = GetDiffrenceArray(msgFromThem,msgFromUs)
                        for msg in msgToSend:
                            msg = InputSanitizer(msg,users[i]['uid'],matches)
                            print("Sending: %s to %s"%(msg,users[i]['uid']))
                            tinder_api.send_msg(users[i]['uid'],msg)
                features.sleep(0.5)


        sleeptime = random.randint(10,30)
        print(bcolors.OKBLUE+ "Checking messages in "+(str(int(sleeptime//60)))+" minutes and "+str(int(sleeptime%60))+ " seconds.."+bcolors.ENDC)
        features.sleep(sleeptime)


def InputSanitizer(input, match, matches):
    input = str(input).replace(config.myTinderName,matches[MatchIDToUID(match)]['name'])
    return input

def MatchIDToUID(matchID):
    info=tinder_api.match_info(matchID)
    if(info == None):
        return None
    participants = info['results']['participants']
    for participant in participants:
        if(participant != config.myTinderID):
            return participant


def SendMessages(match):
    msgarray = match['messages']
    if(len(msgarray) == 0):
        tinder_api.send_msg(match['match_id'], "Er du et kamera? for jeg smiler hver gang jeg kigger på dig")
        print("SENT " + match['name'] + ": " + "Er du et kamera? for jeg smiler hver gang jeg kigger på dig")
    #If we didn't send the message
    elif( msgarray[len(msgarray)-1]['from'] != config.myTinderID):
        print(bcolors.OKGREEN+"I should respond to "+ match['name']+ " who sent me: " + str(msgarray[len(msgarray)-1]['message']+bcolors.ENDC))
    else:
        print(bcolors.FAIL+"Waiting for "+match['name']+" to respond.."+bcolors.ENDC)


def GetForeignMessages(mid,matches):
    uid = MatchIDToUID(mid)

    if(len(matches) == 0):
        return
    theirmsgs = []
    try:
        for msg in matches[uid]['messages']:
            if msg['from'] != config.myTinderID:
                theirmsgs.append(msg['message'])
    except KeyError:
        print("Should unmatch")
        return "unmatch"
    return theirmsgs

def GetOurMessages(mid,matches):
    uid = MatchIDToUID(mid)

    if(len(matches) == 0):
        return
    ourmsgs = []
    try:
        for msg in matches[uid]['messages']:
            if msg['from'] == config.myTinderID:
                ourmsgs.append(msg['message'])
    except KeyError:
        print("Should unmatch")
        return "unmatch"
    return ourmsgs

def GetDiffrenceArray(A,B):
    diff = []
    for a in A:
        if(not Search(B,a)):
            diff.append(a)
    return diff



def Search(A,x):
    for a in A:
        if a == x:
            return True
    return False

def SwipeLoop():
    ids=[]

    numberofswipes = 1
    timeToNextLike = 0
    while True:
        #vi venter paa vi er authorized
        authorized.wait()
        awake.wait()
        #hvis vi ikke har flere at swipe
        if (len(ids) == 0):
            #faar vi da bare nogle flere XD
            ids = GetRecs()
        if(numberofswipes > 0 or GetWaitSeconds(timeToNextLike)< 0):
            if(random.randint(0,15)>2):
                #gaar igennem arrayet bagfra
                returndata = tinder_api.like(ids[len(ids)-1]['_id'])
                print(bcolors.OKBLUE + "Liked " + str(ids[len(ids) - 1]['name'])+bcolors.ENDC)
                numberofswipes = int(returndata['likes_remaining'])
                timeToNextLike = returndata.get('rate_limited_until',0)
                print(bcolors.OKBLUE + "Number of swipes remaining: " + str(numberofswipes)+bcolors.ENDC)
            else:
                returndata = tinder_api.dislike(ids[len(ids) - 1])
                print(bcolors.OKBLUE + "Dislked " + str(ids[len(ids) - 1]['name']) + bcolors.ENDC)
            ids = ids[1:len(ids)-2]
        #checker hvornaar vi kan swipe igen
        if(timeToNextLike>time.time()*1000):

            print(bcolors.OKBLUE+ "Taking a break for " + str(int(GetWaitSeconds(timeToNextLike))//3600)+" hours and " + str(int((int((GetWaitSeconds(timeToNextLike))))/60%60))+ " minutes" + bcolors.ENDC)
            features.sleep(GetWaitSeconds(timeToNextLike))
        features.sleep(random.randrange(1,2))

def UpdateMatches():
    return features.get_match_info()

def GetWaitSeconds(t):
    return (t-(time.time()*1000))/1000

def GetRecs():
    while(True):
        try:
            recommendationData = tinder_api.get_recs_v2()
        except KeyError:
            print("Could not get recommendation data, retrying")
            continue
        break

    ids = FindUsers(recommendationData)
    return ids

def FindUsers(data):
    gizdata = data['data']['results']
    gizid = []
    for giz in gizdata:
        gizid.append((giz['user']))

    return gizid

if __name__ == "__main__":
    try:


        dbHandler.ConnectToDB()
        authorized = threading.Event()
        awake = threading.Event()

        #vi er ikke authorized
        authorized.clear()
        awake.clear()
        #vores threads
        authThread = Thread(target = AuthLoop)
        authThread.daemon = True
        swipeThread = Thread(target=SwipeLoop)
        swipeThread.daemon = True
        chatThread = Thread(target=ChatLoop)
        chatThread.daemon = True
        bedThread = Thread(target=SleepLoop)
        bedThread.daemon = True
        authThread.start()
        bedThread.start()
        swipeThread.start()
        chatThread.start()

        while threading.active_count() > 1:
            features.sleep(1)

    except KeyboardInterrupt:
        print("\n" + bcolors.FAIL+"WHY DO YOU LEAVE ME??"+bcolors.ENDC)
        sys.exit(0)
