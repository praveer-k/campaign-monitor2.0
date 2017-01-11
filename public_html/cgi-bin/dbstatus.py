import re, sys, os
def get_all_dbs():
    dbpath = "../../data/"
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
                            "ready"    : os.path.exists("../output/"+params[4]+"/"+params[4]+".pdf") }
                    res.append(obj)
    return res

def is_available(v):
    v = re.sub(r"[^a-zA-Z0-9 \"\:\,\-\.\!\_\(\)\?\"\;\#\@]+", "", v)
    v = v.replace("  "," ")
    v = v.rstrip().lstrip()
    dbs = get_all_dbs()
    dbnames = [db["dbname"].lower() for db in dbs]
    res = { "available" : v.lower() not in dbnames }
    return res
