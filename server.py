from bottle import route, run, get, post, request, template, static_file
import helper, json, datetime, os, re, subprocess

def is_available(v):
    v = re.sub(r"[^a-zA-Z0-9 \"\:\,\-\.\!\_\(\)\?\"\;\#\@]+", "", v)
    v = v.replace("  "," ")
    v = v.rstrip().lstrip()
    dbs = helper.get_all_dbs()
    dbnames = [db["dbname"].lower() for db in dbs]
    res = { "available" : v.lower() not in dbnames }
    return res

def spwan(data):
    if not os.path.exists("data/"+data["DBName"]):
        os.mkdir("data/"+data["DBName"])
    f = open("data/"+data["DBName"]+"/input.in", "w")
    f.write(data["KEYWORD1"]+"\n")
    f.write(data["KEYWORD2"]+"\n")
    f.write(data["SINCE"]+"\n")
    f.write(data["UNTIL"]+"\n")
    f.write(data["DBName"]+"\n")
    f.write(data["COUNTRY"]+"\n")
    f.close()
    try:
        process = subprocess.Popen("python run.py "+data["DBName"], shell=True)
        # process.pid
        return "True"
    except Exception as e:
        return e

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
@route("/")
def home():
    return static_file("index.html", root="public_html/")

@get("/cgi-bin/available.py", method="GET")
def available():
    db = request.query.get("db")
    return json.dumps(is_available(db))

@get("/cgi-bin/countries.py", method="GET")
def countries():
    return json.dumps(helper.get_all_countries())

@get("/cgi-bin/databases.py", method="GET")
def get_databases():
    return json.dumps(helper.get_all_dbs())

@get("/cgi-bin/process.py", method="GET")
def process():
    since = request.query.get("fromDate")
    since = since[:since[:since.find(":")].rfind(" ")]
    since = datetime.datetime.strptime(since,"%a %b %d %Y").strftime("%Y-%m-%d")

    until = request.query.get("toDate")
    until = until[:until[:until.find(":")].rfind(" ")]
    until = datetime.datetime.strptime(until,"%a %b %d %Y").strftime("%Y-%m-%d")
    data = { "COUNTRY" : request.query.get("country"),
             "KEYWORD1": request.query.get("keyword1"),
             "KEYWORD2": request.query.get("keyword2"),
             "SINCE"   : since,
             "UNTIL"   : until,
             "DBName"  : request.query.get("dbname")
            }
    info = is_available(request.query.get("dbname"))
    print(info["available"])
    if info["available"]==True:
        res = {"message": spwan(data)}
    else:
        res = {"message":"database already in use !"}
    return json.dumps(res)

@get("/cgi-bin/search.py", method="GET")
def query():
    keyword = request.query.get("q")
    return json.dumps(helper.search(keyword))

@route("/<filepath:path>")
def server_static(filepath):
    return static_file(filepath, root="public_html/")

run(host="localhost", port=8080, debug=True)
