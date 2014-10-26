#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import Cookie,glob,re,os,uuid,json
from string import Template
import pprint

#read in all user profiles and store as dict
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

#parse data format of txt files and convert to dict
def readDataFormat(fileHandle):
    data={}
    lines = fileHandle.readlines()
    x=0
    while (x < len(lines)):
        key = lines[x].strip()[:-1]
        x+=1
        tempStore = set()
        while (x < len(lines)) and (lines[x].startswith("\t")):
            tempStore.add(lines[x].strip())
            x+=1
        if len(tempStore) == 1:
            data[key] = tempStore.pop()
        else:
            data[key] = tempStore
    return data

#return true if user and pw combination is valid 
def authenticate(user,pw):
    profile = users.get(user)
    print (profile)
    if profile and profile["info"]["password"] == pw:
        return True
    return False

def loginHandler():
    user = arguments.getvalue("username")
    pw = arguments.getvalue("password")
    print "here!!!!"
    print user
    if (user):
        print "here i am!"
        if(authenticate(user,pw)):
           activeSess[user]=cookie["id"].value
           json.dump(activeSess,open("sessions","w"))
           return homeHandler()
        else:
           pageVars["error"]="Invalid username or password"

    return "login"
def registerHandler():
    user=arguments.getvalue("username")
    pw = arguments.getvalue("password")
    return "register"
def homeHandler():
    return "browse"
#handles navigation and page logic
def navigationHandler(page):
    if not page:page="login";

    if page in pageHandler:
        page = pageHandler[page]()
        with open("templates/"+template[page],'r') as file:
            print(template[page])
            html = Template(file.read()).substitute(pageVars)
    else:
        html="Error"
    return html

#read in cookie info
cookie=Cookie.SimpleCookie()
if 'HTTP_COOKIE' in os.environ:
    cookie_string=os.environ.get('HTTP_COOKIE')
    cookie.load(cookie_string)
if "id" not in cookie:cookie["id"]= uuid.uuid1();

activeSess={}
with open("sessions","r") as sessions:
    activeSess=json.load(sessions)

#static data declared here
STUD_DIR = "students/"
users ={}
template={"login":"index.html","register":"register.html","home":"home.html","browse":"browse.html"}
pageHandler={"login":loginHandler,"register":registerHandler,"home":homeHandler}
pageVars={"error":"", "hideError":"1"}
arguments=cgi.FieldStorage()
page=arguments.getvalue("page")

#boiler plate html strings
print "Content-type: text/html"
print cookie
print '\n<html>\n  <head>\n    <meta charset=\"UTF-8\">\n    <title>\n      Love 2041\n    </title>\n    <link rel=\"stylesheet\" href=\"ionic/css/ionic.min.css\">\n <link rel=\"stylesheet\" href=\"custom.css\">    <link href="http://fonts.googleapis.com/css?family=Lobster" rel="stylesheet" type="text/css">\n    <script src=\"ionic/js/ionic.bundle.js\"></script>\n <script src=\"custom1.js\"></script>\n </head>\n  <body ng-app="main" style=\"background:linear-gradient(#FF2A68,#FF5E3A); color:#444\">\n'


for folder in glob.glob(STUD_DIR+"*"):
    username = re.sub(STUD_DIR,"",folder)
    users[username] = readUserProfile(username)

html = navigationHandler(page)

print html

print '</body>\n</html>'


