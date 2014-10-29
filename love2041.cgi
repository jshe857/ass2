#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import Cookie,glob,re,os,uuid,json
from string import Template
import pprint
import sys
from datetime import date
from subprocess import Popen,STDOUT,PIPE
listKeys = ["favourite_movies","favourite_books","courses","favourite_bands","favourite_TV_shows","favourite_hobbies"]
listPref = ["hair_colours","age","height"]
undisclosed = ["height","weight","birthdate","gender","hair_colour"]
pageVars = {"template":"","error":"","currUser":""}
template={"login":"index.html","register":"register.html","nav":"nav.html"}
userKeys=[]
class MockArguments:
    def __init__(self,args):
        self.data = args
    def getvalue(self, key):
        return self.data.get(key)

def matchMake(profile):
    currUser = pageVars["currUser"]
    loginProf = users[currUser]
    match = 0
    if currUser == profile["username"]:return "0"
    for key in listKeys:
       set1 = set(loginProf.get(key,[]))
       set2 = set(profile.get(key,[]))
       match += len(set1 & set2)*10
    
    pref = loginProf["pref"]
    criteria = pref.keys()
    if "age" in criteria:
        if int(pref["age"][0]) <= int(profile["age"]) <= int(pref["age"][1]):match+=50
        else:
            age = profile["age"]
            match += 50 - min(abs(int(pref["age"][0])-age),abs(int(pref["age"][1])-age))
    else:
        match += max (50 - abs(loginProf["age"] - profile["age"]) ,0)
    if "height" in criteria:
        if float(pref["height"][0]) <= float(profile.get("height",0)) <= float(pref["height"][1]):match+=50
    if "hair_colours" in criteria:
            if profile.get("hair_colour","") in pref["hair_colours"]: match+= 50 
    if "gender" in criteria:
        if pref["gender"] == profile.get("gender") :match +=400
        elif not profile.get("gender"): match +=50
        else: match = 0
    return match
def postProcess():
    for key in users:
        profile = users[key]
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
        except:
            profile["age"] = -1
        
        profile["match"] = matchMake(profile)
         
        for key in undisclosed:
            if key not in profile:profile[key] = "Undisclosed"
    
        profile["gender"] = profile["gender"][0].upper() + profile["gender"][1:]
        profile["hair_colour"] = profile["hair_colour"].capitalize()
        
        if profile["age"] < 0:profile["age"] = "Undisclosed";
        if "profiletext" not in profile:profile["profiletext"] = "About Me";

#read in all user profiles and store as dict
def readUserProfile(username):
    dir = STUD_DIR+username+"/"
    profile = {"avatar":dir+"profile.jpg" ,"photos":[],}
    for file in glob.glob(dir+"photo*"):
        profile["photos"].append(file)
    with open(dir+"profile.txt","r") as info:
        profile.update(readDataFormat(info.readlines()))
    with open(dir+"preferences.txt","r") as pref:
        profile["pref"] = readDataFormat(pref.readlines())
    return profile

#parse data format of txt files and convert to dict
def readDataFormat(lines):
    data={}
    x=0 
    while (x<len(lines)):
        key = lines[x].strip()[:-1]
        x+=1
        tempStore = list()
        while (x < len(lines)) and (lines[x].startswith("\t")):
            info = lines[x].strip().replace("'","&39;").replace('"','&#quot;')
            
            if not info == "min:" and not info == "max:":
                tempStore.append(info)
            x+=1
        if key == "height" and len(tempStore) == 1:
            data[key] = tempStore.pop()
        elif key not in listKeys and key not in listPref:
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
    email = arguments.getvalue("email")
    pwconfirm = arguments.getvalue("pwconfirm")
    if user and email and pw and pwconfirm:
        if not (6<=len(pw)<=18):
            pageVars["error"] = "Invalid Password"
        elif pw != pwconfirm:
            pageVars["error"] = "Passwords Do No Match"
        elif re.match(r'[^A-Z0-9]',user,re.IGNORECASE):
            pageVars["error"] = "Invalid Username"
        else:
            print "made dir"


    else:
        pageVars["error"] = "Please Fill In All Form Fields"

    return 
    
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
    message = re.sub(r'["]',"",message)
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
    userKeys = sorted(userKeys,key=lambda key: users[key]["match"],reverse=True)
    userKeys.remove(pageVars["currUser"]) # dont match with yourself
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
    currUser = pageVars["currUser"]
    if currUser:
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
currUser =  activeSess.get(cookie["id"].value)
if currUser:
    pageVars["currUser"] = currUser
else:
    pageVars["currUser"] = "TenderMan52"
#static data declared here
STUD_DIR = "students/"
users ={}
cardTemplate = "" 
with open("templates/card.html",'r') as card:
    cardTemplate = card.read()
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
if pageVars["currUser"]:
    postProcess()

html = navHandler(page)

print html

print '</body>\n</html>'


