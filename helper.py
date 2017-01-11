from progress.bar import IncrementalBar
import os, json, re, html, time
import pickle, datetime
import yaml

BASE_DATE_FORMAT = "%a %b %d %H:%M:%S %Y"
# get all countires, its code and its subdivisions
def get_all_countries():
    f = open("config/countries.json","r")
    countries = json.loads(f.read())
    f.close()
    return countries

def containsAny(keywords, text):
    flag = False
    for keyword in keywords.split(" "):
        if text.lower().find(keyword.lower())>-1:
            flag = True
    return flag

def wait_to_recover(func):
    def wrapper(*args, **kargs):
        result = None
        try:
            result = func(*args, **kargs)
        except Exception as e:
            print("\nError: ", e)
            time.sleep(120)
        return result
    return wrapper

@wait_to_recover
def find_place_ids(api, country_code, subdivision):
    res = api.geo_search(query=subdivision, granularity="city")
    place_ids = []
    for place in res:
        if place.country_code==country_code and place.id not in place_ids:
            place_ids.append(place.id)
    return place_ids

def download_place_ids(api, country):
    bar = IncrementalBar("Downloading ", max=len(country["subdivisions"]))
    places = {}
    i = 0
    while i<len(country["subdivisions"]):
        place_ids = find_place_ids(api, country["code"], country["subdivisions"][i])
        if place_ids!=None: # implies there was no error while downloading data from twitter.
            places[country["subdivisions"][i]] = place_ids
            i += 1
            bar.next()
    bar.finish()
    return places

@wait_to_recover
def find_user_ids(api, keyword, country_code, place_id):
    tweets = api.search(q=keyword+" place:"+place_id, lang="en", count=1000)
    user_ids = []
    for tweet in tweets:
        if tweet.place.country_code==country_code and tweet.user.id_str not in user_ids:
            user_ids.append(tweet.user.id_str)
    return user_ids

def download_user_ids(api, keyword, country):
    place_ids = [place for subdivision in country["places"].keys() for place in country["places"][subdivision]]
    place_ids = list(set(place_ids))
    bar = IncrementalBar("Downloading ", max=len(place_ids))
    users = {}
    i = 0
    while i<len(place_ids):
        user_ids = find_user_ids(api, keyword, country["code"], place_ids[i])
        if user_ids!=None: # implies there was no error while downloading data from twitter.
            users[ place_ids[i] ] = user_ids
            i += 1
            bar.next()
    bar.finish()
    return users

@wait_to_recover
def download_users_timeline(api, data):
    statuses = { "user": None, "timeline" : [] }
    since = datetime.datetime.strptime(data["since"],"%Y-%m-%d").strftime(BASE_DATE_FORMAT)
    since = datetime.datetime.strptime(since,BASE_DATE_FORMAT)
    until = datetime.datetime.strptime(data["until"],"%Y-%m-%d").strftime(BASE_DATE_FORMAT)
    until = datetime.datetime.strptime(until,BASE_DATE_FORMAT)
    i = 0
    res = api.user_timeline(id=data["id"], count=1000)
    for status in res:
        text = clean( status.text )
        urls = re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text)
        text = re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", "", text)
        text = clean(text)
        url  = urls[0] if len(urls)>0 else ""
        source = re.sub("<[A-Za-z\/][^>]*>","", status.source)
        dt = status.created_at.strftime(BASE_DATE_FORMAT)
        dt = datetime.datetime.strptime(dt,BASE_DATE_FORMAT)
        # print("status",i,"and user",status.user.id_str)
        # print(dt>=since, dt<=until, until>since, containsAny(data["keyword"], text))
        if dt>=since and dt<=until and until>since and containsAny(data["keyword"], text):
            statuses["timeline"].append({# ----------- Tweet Info ----------
                                         "tweet_id"       : status.id,
                                         "created_at"     : status.created_at,
                                         "lang"           : status.lang,
                                         "retweeted"      : status.retweeted,
                                         "text"           : text,
                                         "links"          : url,
                                         "retweet_count"  : status.retweet_count,
                                         # --------- Author Info ----------
                                         "author_id"      : status.author.id_str,
                                         "author_screen_name": status.author.screen_name,
                                         # --------- Source Info ----------
                                         "source"         : source
                                        })
        if i==0:
            statuses["user"] =  { # --------- User Info -----------
                                  "user_id"              : status.user.id_str,
                                  "name"                 : status.user.name,
                                  "screen_name"          : status.user.screen_name,
                                  "user_created_at"      : status.user.created_at,
                                  "description"          : status.user.description,
                                  "friends_count"        : status.user.friends_count,
                                  "statuses_count"       : status.user.statuses_count,
                                  "followers_count"      : status.user.followers_count,
                                  "favourites_count"     : status.user.favourites_count,
                                  "contributors_enabled" : status.user.contributors_enabled,
                                  # ----------- Place Info -----------
                                  "place_id"             : data["place_id"],
                                  "subdivision"          : data["subdivision"],
                                  "location"             : status.user.location
                                }
        i+=1
    # --- end of for loop ---
    if len(statuses["timeline"])!=0 and statuses["user"]!=None:
        f = open(data["path"]+"/@"+data["id"]+".pkl", "wb")
        pickle.dump(statuses, f)
        f.close()
        return True
    else:
        return False
#
#
#
#
dictfilt = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
addtabs = lambda table, count=1: "\n"+"\n".join(["\t"*count+line for line in table.split("\n")])+"\n"

def get_all_dbs():
    dbpath = "data/"
    res = []
    for root, dirs, files in os.walk(dbpath):
        for adir in dirs:
            if os.path.exists(os.path.join(root,adir,"input.in")):
                with open(os.path.join(root,adir,"input.in")) as f:
                    params = f.read().splitlines()
                    obj = { "country"  : params[5],
                            "keyword1" : params[0],
                            "keyword2" : params[1],
                            "fromDate" : params[2],
                            "toDate"   : params[3],
                            "dbname"   : params[4],
                            "ready"    : os.path.exists("public_html/output/"+params[4]+"/"+params[4]+".pdf") }
                    res.append(obj)
    return res

def search(keyword):
    keyword = re.sub(r"[^a-zA-Z0-9 \"\:\,\-\.\!\_\(\)\?\"\;\#\@]+", "", keyword)
    keyword = keyword.replace("  "," ")
    keyword = keyword.rstrip().lstrip()
    res = []
    f = open("config/metadata.json","r")
    mydict = json.loads(f.read())
    f.close()
    if keyword.lower()=="filetype: pdf":
        for obj in get_all_dbs():
            if obj["ready"]==True:
                res.append({ "title": obj["dbname"],
                             "desc" : "A match found for "+obj["dbname"]+" in the databases.",
                             "link" : "output/"+obj["dbname"]+"/"+obj["dbname"]+"_report.pdf"
                           })
        #find in about, documentation, dissertation
        for k, v in mydict.items():
            if v[1].find(".pdf")>=0:
                res.append({ "title": v[0][0],
                             "desc" : "A match found for in "+k+" section for the search.",
                             "link" : v[1] })
    else:
        for obj in get_all_dbs():
            if obj["ready"]==True:
                for k,v in obj.items():
                    if type(v)==str and v.lower().find(keyword.lower())>=0:
                        res.append({ "title": v,
                                     "desc" : "A match found for "+k+" in the databases.",
                                     "link" : "output/"+obj["dbname"]+"/"+obj["dbname"]+"_report.pdf"
                                   })
                        break
        #find in about, documentation, dissertation
        for k, v in mydict.items():
            for key in v[0]:
                if key.find(keyword.lower())>=0:
                    res.append({ "title": key,
                                 "desc" : "A match found for in "+k+" section for the search.",
                                 "link" : v[1] })
                    break
    return res

#Remove those from the formula which is not in dataframe columns
def removeUnwanted(formula, columns):
    y = formula[:formula.find("~")].rstrip().lstrip()
    X = formula[formula.find("~")+1:].rstrip().lstrip()
    X = [o.rstrip().lstrip() for l in X.split("+") for m in l.split(":") for o in m.split("*")]
    for col in X:
        if col not in columns:
            formula = formula.replace(col,"")
    while formula.find(" ")!=-1 or formula.find("++")!=-1 or \
          formula.find("**")!=-1 or formula.find("::")!=-1 or \
          formula.find("+:")!=-1 or formula.find(":+")!=-1 or \
          formula.find("+*")!=-1 or formula.find("*+")!=-1:
        formula = formula.replace(" ","")
        formula = formula.replace("++","+")
        formula = formula.replace("**","*")
        formula = formula.replace("::",":")
        formula = formula.replace("+:","+")
        formula = formula.replace(":+","+")
        formula = formula.replace("+*","+")
        formula = formula.replace("*+","+")
    if formula[-1]==":" or formula[-1]=="*" or formula[-1]=="+":
        formula = formula[:-1]
    formula = formula.replace("+"," + ")
    formula = formula.replace("~"," ~ ")
    return formula
# get the dictionary of predictors map
def getPreDict(xcols):
    pdict = {}
    for col in xcols:
        lookfor = "[T." if col.find("[T.")!=-1 else "["
        if col.find(lookfor)!=-1 and col.find(":")==-1 and col.find("*")==-1:
            key = col[:col.find(lookfor)]
            if key in pdict.keys():
                pdict[key].append(col[col.find(lookfor)+len(lookfor):-1])
            else:
                pdict[key] = [col[col.find(lookfor)+len(lookfor):-1]]
        else:
            pdict[col] = []
    return pdict
# get Reference variable from the given formula
def getRefDict(xcols, df):
    pdict = getPreDict(xcols)
    refdict = {}
    for col in pdict.keys():
        if pdict[col]!=[]:
            refdict[col] = list(set(df[col].values)-set(pdict[col]))[0]
    return refdict
# prettyjoin
def prettyjoin(xcols, dfcols):
    pdict = getPreDict(xcols)
    mainstr = ""
    i = 1
    for col in pdict.keys():
        sep = ""
        if i==len(pdict.keys())-1:
            sep = " and, "
        elif i!=len(pdict.keys()):
            sep = ", "
        if len(pdict[col])==0:
            mainstr += col + sep
        elif len(pdict[col])==1:
            mainstr += col + " - " + pdict[col][0] + sep
        else:
            mainstr += col + " - " + ", ".join(pdict[col][:len(pdict[col])-1]) + " and, " + pdict[col][-1] + sep
        i += 1
    return mainstr

def clean(text):
    text = re.sub(r"[^a-zA-Z0-9 \"\:\,\-\.\!\_\(\)\?\"\;\/\\\#\@]+", "", text)
    text = text.replace("  "," ")
    text = text.rstrip().lstrip()
    return text

def reverse_map(mydict):
    values = [value for key in mydict.keys() for value in mydict[key]]
    values = list(set(values))
    newdict = {}
    for value in values:
        if value not in newdict.keys():
            newdict[value] = [key for key in mydict.keys() if value in mydict[key]]
    return newdict

def get_variables(path):
    f = open(path)
    var = yaml.load(f)
    return var
