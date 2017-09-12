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


authorized = False

def AuthLoop():
    while(True):
        #authCond.wait()
        print('Authorizing')
        #saetter authorized til false
        authorized.clear()
        tinder_api.get_auth_token(config.fb_access_token, config.fb_user_id)
        #authorized = true
        authorized.set()
        timeToNextAuth = time.time() * 1000 + 1800000
        tinder_api.change_preferences(age_filter_min=18, age_filter_max=22, distance_filter=30)
        features.sleep(random.randint(1000,2000))

def ChatLoop():

    while(True):
        #venter paa vi er authorized
        authorized.wait()

        if len(UpdateMatches()) == 0:
            print("Chat loop is waiting for matches... we currently have none :(")
        else:
            print("WE HAVE A MATCH")
        features.sleep(random.randint(30,90))



def SwipeLoop():
    ids=[]
    pause = False

    timeToNextAuth = 0
    timeToNextLike = 0
    while True:
        #vi venter paa vi er authorized
        authorized.wait()
        #hvis vi ikke har flere at swipe
        if (len(ids) == 0):
            #faar vi da bare nogle flere XD
            ids = GetIds()
        #randomness for ikke kun at swipe hoejre
        if(random.randint(0,15)!=0):
            #gaar igennem arrayet bagfra
            returndata = tinder_api.like(ids[len(ids)-1])
            print("Liked " + str(ids[len(ids) - 1]))
            numberofswipes = int(returndata['likes_remaining'])
            timeToNextLike = returndata['rate_limited_until']
            print("Number of swipes remaining: " + str(numberofswipes))
        else:
            returndata = tinder_api.dislike(ids[len(ids) - 1])
            print("Dislked " + str(ids[len(ids) - 1]))
        ids = ids[1:len(ids)-2]
        #checker hvornaar vi kan swipe igen
        if(timeToNextLike>time.time()*1000):
            pause = True
            breaktime = random.randint(60,600)
            print("Taking a break for " +str(breaktime) + " seconds.. Im on a cooldown for " + str(int(GetWaitSeconds(timeToNextLike))//3600)+" hours and " + str(int((int((GetWaitSeconds(timeToNextLike))))/60%60))+ " minutes")
            features.sleep(breaktime)
        features.sleep(random.randrange(1,2))

def UpdateMatches():
    return features.get_match_info()

def GetWaitSeconds(t):
    return (t-(time.time()*1000))/1000

def GetIds():
    recommendationData = tinder_api.get_recs_v2()
    ids = findIDs(recommendationData)
    return ids

def findIDs(data):
    gizdata = data['data']['results']
    gizid = []
    for giz in gizdata:
        gizid.append((giz['user']['_id']))

    return gizid



if __name__ == "__main__":
    try:
        authorized = threading.Event()
        #vi er ikke authorized
        authorized.clear()

        #vores threads
        authThread = Thread(target = AuthLoop)
        authThread.daemon = True
        swipeThread = Thread(target=SwipeLoop)
        swipeThread.daemon = True
        chatThread = Thread(target=ChatLoop)
        chatThread.daemon = True
        authThread.start()
        swipeThread.start()
        chatThread.start()
        while threading.active_count() > 1:
            features.sleep(1)

    except KeyboardInterrupt:
        print("WHY DO YOU LEAVE ME??")
        sys.exit(0)




