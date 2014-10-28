#!/usr/bin/python

import cgi
#import cgitb; cgitb.enable()  # for troubleshooting
import Cookie,glob,re,os,uuid,json
from string import Template
import pprint
import sys
from datetime import date
from subprocess import Popen,STDOUT,PIPE
listKeys = ["favourite_movies","favourite_books","courses","favourite_bands","favourite_TV_shows","favourite_hobbies"]
undisclosed = ["height","weight","birthdate","gender"]
userKeys=[]
class MockArguments:
    def __init__(self,args):
        self.data = args
    def getvalue(self, key):
        return self.data.get(key)




#read in all user profiles and store as dict
def readUserProfile(username):
    dir = STUD_DIR+username+"/"
    profile = {"avatar":dir+"profile.jpg" ,"photos":[],}
    for file in glob.glob(dir+"photo*"):
        profile["photos"].append(file)
    with open(dir+"profile.txt","r") as info:
        profile.update(readDataFormat(info))
    with open(dir+"preferences.txt","r") as pref:
        profile["pref"] = readDataFormat(pref)
    profile["gender"] = profile["gender"][0].upper() + profile["gender"][1:]
    
    for key in undisclosed:
        if key not in profile:profile[key] = "Undisclosed"

    if "profiletext" not in profile:profile["profiletext"] = "About Me";
    try:
        datestr = profile["birthdate"].split("/")
        (year,month,day) = map(int,datestr)
        if day > 31:
            temp = day
            day = year
            year = temp
        born = date(year,month,day)
        today = date.today()
        profile["age"] = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        if profile["age"] < 0:
            profile["age"] = "Undisclosed"
    except:
        profile["age"] = "Undisclosed"
    profile["match"] = profile["age"]


    return profile

#parse data format of txt files and convert to dict
def readDataFormat(fileHandle):
    data={}
    lines = fileHandle.readlines()
    x=0
    while (x < len(lines)):
        key = lines[x].strip()[:-1]
        x+=1
        tempStore = list()
        while (x < len(lines)) and (lines[x].startswith("\t")):
            tempStore.append(lines[x].strip().replace("'","&39;").replace('"','&#quot;'))
            x+=1
        if key not in listKeys :
            data[key] = tempStore.pop()
        else:
            data[key] = tempStore
    return data

#return true if user and pw combination is valid 
def authenticate(user,pw):
    profile = users.get(user)
    if profile and profile["password"] == pw:
        return True
    return False

#Page Handlers Here
def logoutHandler():
    try:
        del activeSess[cookie["id"].value]
        json.dump(activeSess,open("sessions","w"))
    except:
        print ("No Active Session For Cookie")
    return loginHandler()
def loginHandler():
    user = arguments.getvalue("username")
    pw = arguments.getvalue("password")
    if (user):
        if(authenticate(user,pw)):
            for cookieid, username in activeSess.items():
                if username == user:
                    del activeSess[cookieid]
            activeSess[cookie["id"].value]=user
            json.dump(activeSess,open("sessions","w"))
            pageVars["currUser"] = user
            return browseHandler()
        else:
           pageVars["user"] = user
           pageVars["error"]="Invalid username or password"
    else:
        pageVars["user"] = ""
    return "login"
def registerHandler():
    user=arguments.getvalue("username")
    pw = arguments.getvalue("password")
    return "register"
def listHandler():
    rng = arguments.getvalue("range")
    try:
        rng = int(rng)
    except:
        rng =0
    if arguments.getvalue("action") == "Next":rng+=1;
    if arguments.getvalue("action") == "Prev":rng-=1;
    start = rng*15
    end = start+15 if start + 15 < len(userKeys) else len(userKeys)
    template = ""
    for x in range(start,end):
        if x > len(userKeys) or x < 0:break;
        key = userKeys[x]
        users[key]["url"] = "?page=detail&user="+key
        template += Template(cardTemplate).safe_substitute(users[key]) 
    
    nextrng = str(rng +1) if end<len(userKeys) else str(rng)
    prevrng = str(rng-1) if start>0 else str(rng)
    nextdis = "" if end <len(userKeys) else "disabled"
    prevdis = "" if start >0 else "disabled"
    template += '''
    <div style="text-align:center;font-size:28px; padding:10 120; width:100%; height:10%">
    <input type="hidden" value={0} name="range">
    <input type="submit" name="action" value="Prev"class="button glass" {1}  style="float:left; width:25%">
    Showing Results: {3} - {4}
    <input type="submit" name="action" value="Next"class="button glass" {2} style="float:right; width:25%">
    </div>
    </form>
    '''.format(rng,prevdis,nextdis, start+1, end)
    pageVars["template"]+= template
    pageVars["title"] = "Browse"
    return "nav"
def detailHandler():
    try:
        user=users[arguments.getvalue("user")]
    except:
        pageVars["error"] = "No Such User"
        return browseHandler()
    with open("templates/detail.html","r") as detail:
        pageVars["title"] = user["username"]
        pageVars["template"] += Template(detail.read()).safe_substitute(user)
    message = arguments.getvalue("message")
    if message:
        subject="LOVE2041:"+pageVars["currUser"] +"Sent You A Message" 
        to=user["email"]
        with open("error","w") as error:
            p1 = Popen(["mail","-s" ,subject,to],stdin=PIPE,stdout=error,stderr=error)
            p1.communicate(input=message)
    return "nav"

def browseHandler():
    pageVars["template"]+='<form action="love2041.cgi?page=browse" method="post">'
    return listHandler()
def matchHandler():
    pageVars["template"]+= '<form action="love2041.cgi?page=match" method="post">'
    global userKeys
    userKeys = sorted(userKeys,key=lambda key: users[key]["match"]) 
    return listHandler()
def searchHandler():
    searchString = arguments.getvalue("searchStore")
    if not searchString: searchString=""
    if arguments.getvalue("action") == "Search":
        arguments["range"].value = 0
        searchString=arguments.getvalue("search")
        global userKeys
        if searchString:
            tempStore = []
            for key in userKeys:
                if searchString in key:
                    tempStore.append(key)
            userKeys = tempStore
    
    searchbox='''
    <form action="love2041.cgi?page=search" method="post">
    <div style="margin-left:90; margin-right:90" class="card item-input-inset">
      <label class="item-input-wrapper">
          <i class="icon ion-ios7-search placeholder-icon"></i>
          <input type="search" name="search" placeholder="Search" value="{0}">
      </label>
      <input type="hidden" name="searchStore" value="{0}">
      <input type="submit" name="action" value="Search" class="button button-light button-clear">
    </div>
    '''.format(searchString)
    pageVars["template"]+=searchbox
    return listHandler()
#handles navigation and page logic
def navHandler(page):
    if page not in pageHandler: page = None;
    currUser = activeSess.get(cookie["id"].value)
    if currUser:
        pageVars["currUser"] = currUser
        if (not page):
            page="browse";
    elif page != "register":
        page="login"

    page = pageHandler[page]()
    with open("templates/"+template[page],'r') as file:
        html = Template(file.read()).safe_substitute(pageVars)
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
cardTemplate = "" 
with open("templates/card.html",'r') as card:
    cardTemplate = card.read()
pageVars = {"template":"","error":"","currUser":""}
template={"login":"index.html","register":"register.html","nav":"nav.html"}
pageHandler={"match":matchHandler, "search":searchHandler, "login":loginHandler,"register":registerHandler,"browse":browseHandler,"detail":detailHandler,"logout":logoutHandler}
if (os.environ.get("REQUEST_URI")):
    arguments=cgi.FieldStorage()
else:
    data = {}
    for arg in sys.stdin:
        pair = arg.strip().split(" ")
        data[pair[0]] = pair[1]
    arguments=MockArguments(data)       
page=arguments.getvalue("page")

#boiler plate html strings
print "Content-type: text/html"
print cookie
print '\n<html>\n  <head>\n    <meta charset=\"UTF-8\">\n    <title>\n      Love 2041\n    </title>\n    <link rel=\"stylesheet\" href=\"ionic/css/ionic.min.css\">\n <link rel=\"stylesheet\" href=\"custom.css\">    <link href="http://fonts.googleapis.com/css?family=Lobster" rel="stylesheet" type="text/css">\n    <script src=\"ionic/js/ionic.bundle.js\"></script>\n <script src=\"custom.js\"></script>\n </head>\n  <body ng-app="main" style=\"background:linear-gradient(#FF4981,#FF4981); color:#444\">\n'


for folder in glob.glob(STUD_DIR+"*"):
    username = re.sub(STUD_DIR,"",folder)
    users[username] = readUserProfile(username)
    userKeys = sorted(users.keys())

html = navHandler(page)

print html

print '</body>\n</html>'


