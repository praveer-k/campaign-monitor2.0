#!/usr/bin/env python
import cgi, json, dbstatus
import cgitb; cgitb.enable()  # for troubleshooting
#-------------------------------------------------------------------------------
print("Content-Type: application/json;charset=acsii\n\n")

try:
    # Create instance of FieldStorage
    form = cgi.FieldStorage()
    # Get data from fields
    res = None
    if form.getvalue("db"):
        res = dbstatus.is_available(form.getvalue("db"))
    print(json.dumps(res))
except Exception as e:
    print(e)
