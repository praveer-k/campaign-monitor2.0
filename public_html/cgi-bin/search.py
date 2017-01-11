#!/usr/bin/env python
import cgi, os, json, re, dbstatus
import cgitb; cgitb.enable()  # for troubleshooting
#-------------------------------------------------------------------------------
print("Content-Type: application/json;charset=acsii\n\n")

def search(keyword):
    keyword = re.sub(r"[^a-zA-Z0-9 \"\:\,\-\.\!\_\(\)\?\"\;\#\@]+", "", keyword)
    keyword = keyword.replace("  "," ")
    keyword = keyword.rstrip().lstrip()
    res = []
    f = open("../../config/metadata.json","r")
    mydict = json.loads(f.read())
    f.close()
    if keyword.lower()=="filetype: pdf":
        for obj in dbstatus.get_all_dbs():
            if obj["ready"]==True:
                res.append({ "title": obj["dbname"],
                             "desc" : "A match found for "+obj["dbname"]+" in the databases.",
                             "link" : "/output/"+obj["dbname"]+"/"+obj["dbname"]+"_report.pdf"
                           })
        #find in about, documentation, dissertation
        for k, v in mydict.items():
            if v[1].find(".pdf")>=0:
                res.append({ "title": v[0][0],
                             "desc" : "A match found for in "+k+" section for the search.",
                             "link" : v[1] })
    else:
        for obj in dbstatus.get_all_dbs():
            if obj["ready"]==True:
                for k,v in obj.items():
                    if type(v)==str and v.lower().find(keyword.lower())>=0:
                        res.append({ "title": v,
                                     "desc" : "A match found for "+k+" in the databases.",
                                     "link" : "/output/"+obj["dbname"]+"/"+obj["dbname"]+"_report.pdf"
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

try:
    # Create instance of FieldStorage
    form = cgi.FieldStorage()
    # Get data from fields
    res = None
    if form.getvalue("q"):
        res = search(form.getvalue("q"))
    print(json.dumps(res))
except Exception as e:
    print(e)
