#!/usr/bin/env python
import cgi, json
import cgitb; cgitb.enable()  # for troubleshooting
#-------------------------------------------------------------------------------
print("Content-Type: application/json;charset=acsii\n\n")
# # get all countires, its code and its subdivisions
def get_all_countries():
    f = open("../../config/countries.json","r")
    countries = json.loads(f.read())
    f.close()
    return countries

print(json.dumps(get_all_countries()))
