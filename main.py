import fb_auth_token;
import config;
import tinder_api;
import features;
import json
from collections import namedtuple
import random
import time


def main():
    auth = tinder_api.get_auth_token(config.fb_access_token,config.fb_user_id)
    timeToNextAuth = time.time() * 1000 + 1800000
    features.sleep(1)
    tinder_api.reset_real_location()
    features.sleep(1)
    tinder_api.change_preferences(age_filter_min = 18,age_filter_max = 22,distance_filter=30)
    print("Updated age settings")
    features.sleep(1)
    matches = len(features.get_match_info())
    ids=[]
    numberofswipes = 1
    pause = False

    timeToNextAuth = 0
    timeToNextLike = 0

    while True:
        if(timeToNextAuth < time.time()*1000):
            print("Reauthorizing")
            tinder_api.get_auth_token(config.fb_access_token, config.fb_user_id)
            timeToNextAuth = time.time()*1000 + 1800000

        if(not pause):
            if (len(ids) == 0):
                ids = GetIds()
            if(random.randint(0,3)!=0):
                returndata = tinder_api.like(ids[len(ids)-1])
                print("Liked " + str(ids[len(ids) - 1]))
                numberofswipes = int(returndata['likes_remaining'])
                timeToNextLike = returndata['rate_limited_until']
                print("Number of swipes remaining: " + str(numberofswipes))
            else:
                returndata = tinder_api.dislike(ids[len(ids) - 1])
                print("Dislked " + str(ids[len(ids) - 1]))
            ids = ids[1:len(ids)-2]
        if(timeToNextLike>time.time()*1000):
            pause = True
            print("Taking a break for 10 seconds.. Im on a cooldown for " + str(int(GetWaitSeconds(timeToNextLike))//3600)+" hours and " + str(int((int((GetWaitSeconds(timeToNextLike))))/60%60))+ " minutes")
            print("We have this many matches: " + str(len(UpdateMatches())))
            features.sleep(10)
        else:
            pause = False
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
    main()

