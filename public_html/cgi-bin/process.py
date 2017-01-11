#!/usr/bin/env python
import cgi, os, json, dbstatus, html
import datetime, subprocess
import cgitb; cgitb.enable()  # for troubleshooting
import urllib
#-------------------------------------------------------------------------------
print("Content-Type: text/html;charset=acsii\n\n")

def register_request(data):
    os.chdir("../../")
    if not os.path.exists("data/"+data["DBName"]):
        os.mkdir("data/"+data["DBName"])
        os.chmod("data/"+data["DBName"], 0o777)
    f = open("data/"+data["DBName"]+"/input.in", "w")
    os.chmod("data/"+data["DBName"]+"/input.in", 0o777)
    f.write(data["KEYWORD1"]+"\n")
    f.write(data["KEYWORD2"]+"\n")
    f.write(data["SINCE"]+"\n")
    f.write(data["UNTIL"]+"\n")
    f.write(data["DBName"]+"\n")
    f.write(data["COUNTRY"]+"\n")
    f.close()
    return 'True'
    
def generate_report(form):
    since = urllib.unquote(form.getvalue("fromDate"))
    since = since[:since[:since.find(":")].rfind(" ")]
    since = datetime.datetime.strptime(since,"%a %b %d %Y").strftime("%Y-%m-%d")
    
    until = urllib.unquote(form.getvalue("toDate"))
    until = until[:until[:until.find(":")].rfind(" ")]
    until = datetime.datetime.strptime(until,"%a %b %d %Y").strftime("%Y-%m-%d")
    
    data = { "COUNTRY" : urllib.unquote(form.getvalue("country")),
             "KEYWORD1": urllib.unquote(form.getvalue("keyword1")),
             "KEYWORD2": urllib.unquote(form.getvalue("keyword2")),
             "SINCE"   : since,
             "UNTIL"   : until,
             "DBName"  : urllib.unquote(form.getvalue("dbname")) }
    info = dbstatus.is_available(data["DBName"])

    if info["available"]==True:
        res = {"message": register_request(data)}
    else:
        res = {"message": "database already in use !"}
    return json.dumps(res)


try:
    form = cgi.FieldStorage()
    print(generate_report(form))
except Exception as e:
    print(json.dumps({"message": e}))
