#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import Cookie
import glob
import re
from string import Template

def readUserProfile(username):
    dir = STUD_DIR+username+"/"
    profile = {"avatar":dir+"/profile.jpg" ,"photos":[],}
    
    for file in glob.glob(dir+"photo*"):
        profile["photos"].append(file)
    with open(dir+"profile.txt","r") as info:
        profile["info"] = readDataFormat(info)
    with open(dir+"preferences.txt","r") as pref:
        profile["pref"] = readDataFormat(pref)
    return profile

#def authenticate(user,pw):
def readDataFormat(fileHandle):
    return {}
    
STUD_DIR = "students/"

print "Content-type: text/html"
print '\n<html>\n  <head>\n    <meta charset=\"UTF-8\">\n    <title>\n      Love 2041\n    </title>\n    <link rel=\"stylesheet\" href=\"ionic/css/ionic.min.css\">\n <link rel=\"stylesheet\" href=\"custom.css\">    <link href="http://fonts.googleapis.com/css?family=Lobster" rel="stylesheet" type="text/css">\n    <script src=\"ionic/js/ionic.bundle.js\">\n    </script>\n  </head>\n  <body style=\"background:linear-gradient(#FF2A68,#FF5E3A); color:#444\">\n'

users ={}
pageList={"login":"index.html","register":"register.html"}
pageVars={"error":"", "hideError":"1"}
arguments=cgi.FieldStorage()
page=arguments.getvalue("page")

if not page: page="login"


if page in  pageList:
    for folder in glob.glob(STUD_DIR+"*"):
        username = re.sub(STUD_DIR,"",folder)
        users[username] = readUserProfile(username)
    with open("templates/"+ pageList[page],'r') as file:
        html = Template(file.read()).substitute(pageVars)

        print html
else:
    print "Error"

print '</body>\n</html>'


