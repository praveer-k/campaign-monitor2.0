# from pygments.formatters import HtmlFormatter
# from pygments.lexers import get_lexer_by_name
# from pygments import highlight
# from bs4 import BeautifulSoup

from tabulate import tabulate
import helper
import os, sys, re, pickle

def findVariables(text):
    variables = []
    while len(text)>1:
        start = text.find("<<")
        end = text.find(">>")
        if start!=-1 and end!=-1:
            variables.append(text[start:end+2])
        text = text[end+3:]
    return variables

def escape(text):
    text = text.replace("\\","\\\\")
    text = text.replace("#"," \#")
    text = text.replace("_","\_")
    text = text.replace("\\\\_","\_")
    text = text.replace("\\\\item","\\item")
    return text

path = sys.argv[1]
with open(path) as f:
    keys = f.readlines()
    KEYWORD1 = keys[0].rstrip()
    KEYWORD2 = keys[1].rstrip()
    SINCE    = keys[2].rstrip()
    UNTIL    = keys[3].rstrip()
    DBName   = keys[4].rstrip()
    COUNTRY  = keys[5].rstrip()

filepath = "public_html/output/"+DBName
# ------- Apply the heading of markdown as following ----------
if not os.path.exists("data/"+DBName+"/dataMap.pkl"):
    print("Loading template...")
    f = open("config/dummy.tex","r")
    text = f.read()
    f.close()
else:
    print("Loading dataMap...")
    f = open("data/"+DBName+"/dataMap.pkl","rb")
    dataMap = pickle.load(f)
    f.close()
    print("Loading template...")
    f = open("config/report_template.tex","r")
    text = f.read()
    f.close()
    variables = sorted(list(set(findVariables(text))))
    for v in variables:
        if v[2:-2] in dataMap.keys():
            if v[2:-2]!="modelSummary":
                if v[2:-2]=="listOfComments" and dataMap[v[2:-2]]=="":
                    text = re.sub(v, "\\item No comments.", text)
                else:
                    text = re.sub(v, escape(dataMap[v[2:-2]]), text)
            else:
                text = re.sub(v, dataMap[v[2:-2]], text)

print("Writing the report tex file...")
f = open(filepath+"/"+DBName+".tex","w")
f.write(text)
f.close()
