#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import Cookie,glob,re,os,uuid,json
from string import Template
import pprint
import sys
from datetime import date
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
    data["gender"] = data["gender"][0].upper() + data["gender"][1:]
    if not data.get("profiletext"):data["profiletext"] = "About Me"
    try:
        datestr = data["birthdate"].split("/")
        (year,month,day) = map(int,datestr)
        born = date(year,month,day)
        today = date.today()
        data["age"] = today.year - born.year - ((today.month, today.day) < (born.month, born.day)) 
    except:
        data["age"] = "Undisclosed"
    return data

#return true if user and pw combination is valid 
def authenticate(user,pw):
    profile = users.get(user)
    if profile and profile["info"]["password"] == pw:
        return True
    return False

def loginHandler():
    user = arguments.getvalue("username")
    pw = arguments.getvalue("password")
    if (user):
        if(authenticate(user,pw)):
           activeSess[user]=cookie["id"].value
           json.dump(activeSess,open("sessions","w"))
           return BrowseHandler()
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
def browseHandler():
    rng = arguments.getvalue("range")
    try:
        rng = int(rng)
    except:
        rng = 0
    
    start = rng*15
    end = start+15 if start + 15 < len(userKeys) else len(userKeys)
    template = ""
    for x in range(start,end):
        if x > len(userKeys):break;
        key = userKeys[x]
        users[key]["url"] = "?page=detail&user="+key
        template += Template(cardTemplate).safe_substitute(users[key]) 
    nextrng = str(rng +1) if rng<len(userKeys) else str(rng)
    prevrng = str(rng-1) if rng>1 else str(rng)
    template += '''
    <div style="padding:10 120; width:100%; height:10%">
    <a class="button glass" href="?page=browse&range='''+prevrng +'''" style="float:left; width:25%">
    <i class="icon ion-chevron-left"></i>&nbsp;Prev
    </a>
    <a class="button glass" href="?page=browse&range='''+nextrng +'''" style="float:right; width:25%">
    Next&nbsp;<i class="icon ion-chevron-right"></i>
    </a>
    </div>
    '''
    pageVars["template"] = template
    pageVars["title"] = "Browse"
    return "nav"
def detailHandler():
    try:
        user=users[arguments.getvalue("user")]
    except:
        pageVars["error"] = "No Such User"
        return browseHandler()
    with open("templates/detail.html","r") as detail:
        pageVars["title"] = user["name"]
        pageVars["template"] = Template(detail.read()).safe_substitute(user)
    return "nav" 
#handles navigation and page logic
def navigationHandler(page):
    if not page:page="browse";

    if page in pageHandler:
        page = pageHandler[page]()
        with open("templates/"+template[page],'r') as file:
            html = Template(file.read()).safe_substitute(pageVars)
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
cardTemplate = "" 
with open("templates/card.html",'r') as card:
    cardTemplate = card.read()
pageVars = {"error":""}
template={"login":"index.html","register":"register.html","nav":"nav.html"}
pageHandler={"login":loginHandler,"register":registerHandler,"browse":browseHandler,"detail":detailHandler}
listKeys = ["favourite_movies","favourite_books","courses","favourite_bands","favourite_TV_shows","favourite_hobbies"]
if (os.environ.get("REQUEST_URI")):
    arguments=cgi.FieldStorage()
else:
    data = {}
    for arg in sys.stdin:
        pair = arg.strip().split(" ")
        data[pair[0]] = pair[1]
    arguments=MockArguments(data)       
page=arguments.getvalue("page")
userKeys=[]

#boiler plate html strings
print "Content-type: text/html"
print cookie
print '\n<html>\n  <head>\n    <meta charset=\"UTF-8\">\n    <title>\n      Love 2041\n    </title>\n    <link rel=\"stylesheet\" href=\"ionic/css/ionic.min.css\">\n <link rel=\"stylesheet\" href=\"custom.css\">    <link href="http://fonts.googleapis.com/css?family=Lobster" rel="stylesheet" type="text/css">\n    <script src=\"ionic/js/ionic.bundle.js\"></script>\n <script src=\"custom.js\"></script>\n </head>\n  <body ng-app="main" style=\"background:linear-gradient(#FF4981,#FF4981); color:#444\">\n'


for folder in glob.glob(STUD_DIR+"*"):
    username = re.sub(STUD_DIR,"",folder)
    users[username] = readUserProfile(username)
    userKeys = sorted(users.keys())

html = navigationHandler(page)

print html

print '</body>\n</html>'


