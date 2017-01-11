import sys, os, json
import pickle, zipfile
import tweepy
import helper

path = sys.argv[1]
with open(path) as f:
    keys = f.readlines()
    KEYWORD1 = keys[0].rstrip()
    KEYWORD2 = keys[1].rstrip()
    SINCE    = keys[2].rstrip()
    UNTIL    = keys[3].rstrip()
    DBName   = keys[4].rstrip()
    COUNTRY  = keys[5].rstrip()

if __name__ == "__main__":
    KEYWORD = KEYWORD1 + " " + KEYWORD2
    # -----------------------------------------------------------
    dirpath = "data/"+DBName
    if not (os.path.exists(dirpath) and os.path.isdir(dirpath)):
        print("Creating pickling folders ...")
        os.mkdir(dirpath)
    # -----------------------------------------------------------
    print("Loading Configuration ...")
    f = open("config/config.json")
    config = json.load(f)
    f.close()
    # -----------------------------------------------------------
    print("Fetching Country's information ...")
    countries = helper.get_all_countries()
    country = countries[COUNTRY]
    # -----------------------------------------------------------
    print("Initiallising Twitter API ...")
    config = config["twitter"]
    auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
    auth.secure = True
    auth.set_access_token(config["access_key"], config["access_secret"])
    api = tweepy.API(auth)
    # -----------------------------------------------------------
    print("Downloading place ids from twitter ...")
    filename = dirpath+"/places.pkl"
    country["places"] = helper.download_place_ids(api, country)
    f = open(filename, "wb")
    pickle.dump(country, f)
    f.close()
    # f = open(dirpath+"/places.pkl", "rb")
    # country = pickle.load(f)
    # f.close()
    # -----------------------------------------------------------
    print("Downloading user ids from twitter ...")
    filename = dirpath+"/users.pkl"
    users = helper.download_user_ids(api, KEYWORD, country)
    f = open(filename, "wb")
    pickle.dump(users, f)
    f.close()
    # f = open(dirpath+"/users.pkl", "rb")
    # users = pickle.load(f)
    # f.close()
    # -----------------------------------------------------------
    print("Revese map place ids and user ids to subdivisions ... ")
    places = helper.reverse_map(country["places"])
    users  = helper.reverse_map(users)
    user_ids = list(sorted(users.keys()))
    # -----------------------------------------------------------
    print("Downloading users timeline ...")
    bar = helper.IncrementalBar("Downloading ", max=len(users))
    for user_id in user_ids:
        data = {"id" : user_id,
                "place_id" : users[user_id][0],
                "subdivision" : places[users[user_id][0]][0],
                "keyword" : KEYWORD,
                "since" : SINCE,
                "until" : UNTIL,
                "path" : dirpath
               }
        bar.next()
        helper.download_users_timeline(api, data)
    print("Done.")
