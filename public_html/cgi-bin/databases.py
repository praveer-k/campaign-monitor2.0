#!/usr/bin/env python
import cgi, json, dbstatus
import cgitb; cgitb.enable()  # for troubleshooting
#-------------------------------------------------------------------------------
print("Content-Type: application/json;charset=acsii\n\n")

print(json.dumps(dbstatus.get_all_dbs()))
