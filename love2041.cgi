#!/usr/bin/python
##########LOVE2041#########################################################################
# A CGI Scipt for a simple dating website 
# Written by Jeffrey Shen
##########Overview##########################################################################
#
#when run the cgi script:
#1.Builds up a dict of all user profiles stored to speed up detail look up times
#
#2.Checks to see if it has recieved a cookie from browser
#if so the cgi script checks to see if an active session  exists on server for that cookie id
#if so, then the user is considered logged in
#
#3.the cgi script than looks at the page variable and passes it to the navHandler function
#if the page is valid and the user is logged in the navHandler calls the specific pageHandler
#to perform page specific logic and outputs the desired html page.
#Otherwise the navHandler calls the loginHandler and displays a login screen to the user
#
#############################################################################################




import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import Cookie,glob,re,os,uuid,json,shutil,sys
from string import Template
from datetime import date
from subprocess import Popen,STDOUT,PIPE
listKeys = ["favourite_movies","favourite_books","courses","favourite_bands","favourite_TV_shows","favourite_hobbies"]
undisclosed = ["name","height","weight","birthdate","gender","hair_colour","degree","profiletext","age"]
pageVars = {"template":"","error":"","currUser":""}
template={"login":"index.html","register":"register.html","nav":"nav.html"}
userKeys=[]
matchPages=["detail","browse","search","match"]
STUD_DIR = "students/"
users ={}
cardTemplate = open("templates/card.html",'r').read()

#mock class for cgi debugging from terminal
class MockArguments:
    def __init__(self,args):
        self.data = args
    def getvalue(self, key):
        return self.data.get(key)

#Match Making Algorithm generates a score for each user based on preferences
def matchMake(profile):
    currUser = pageVars["currUser"]
    loginProf = users[currUser]
    match = 0
    if currUser == profile["username"]:return "0"
    for key in listKeys:
       set1 = set(loginProf.get(key,[]))
       set2 = set(profile.get(key,[]))
       match += len(set1 & set2)*10
    
    pref = readUserPreferences(currUser)
    criteria = pref.keys()
    if "age" in criteria:
        if int(pref["age"][0]) <= int(profile["age"]) <= int(pref["age"][1]):match+=50
        else:
            age = profile["age"]
            match += 50 - min(abs(int(pref["age"][0])-age),abs(int(pref["age"][1])-age))
    else:
        try:
            match += max (50 - abs(loginProf["age"] - profile["age"]) ,0)
        except:
            match = match
    if "height" in criteria:
        if float(pref["height"][0]) <= float(profile.get("height",0)) <= float(pref["height"][1]):match+=50
    if "hair_colours" in criteria:
            if profile.get("hair_colour","") in pref["hair_colours"]: match+= 50 
    if "gender" in criteria:
        if profile.get("gender") in pref["gender"]:match +=400
        elif not profile.get("gender"): match +=50
        else: match = 0
    if match <0: match=0 
    return match

#Alter data for display to be human readable
def postProcess():
    for key in users:
        profile = users[key]
        try:
            datestr = profile["birthdate"].split("/")
            (year,month,day) = map(int,datestr)
            born = date(year,month,day)
            today = date.today()
            profile["age"] = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        except:
            profile["age"] = -1
        
        profile["match"] = matchMake(profile)
         
        for key in undisclosed:
            if key not in profile:profile[key] = "Not Provided"
    
        profile["gender"] = profile["gender"][0].upper() + profile["gender"][1:]
        profile["hair_colour"] = profile["hair_colour"].capitalize()
        
        if profile["age"] < 0:profile["age"] = "Not Provided";

#read in all user profiles and store as dict
def readUserProfile(username):
    dir = STUD_DIR+username+"/"
    profile = {"avatar":dir+"profile.jpg" ,"photos":[],}
    for file in glob.glob(dir+"photo*"):
        profile["photos"].append(file)
    with open(dir+"profile.txt","r") as info:
        profile.update(readDataFormat(info.readlines()))
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
            tempStore.append(info)
            x+=1
        if key not in listKeys:
            data[key] = tempStore.pop()
        else:
            data[key] = tempStore
    if "birthdate" in data:
        datestr = data["birthdate"].split("/")
        (year,month,day) = map(int,datestr)
        if day > 31:
            data["birthdate"] = str(day) +"/" + str(month) +"/" +str(year)
    if "height" in data:data["height"] = data["height"][:-1]
    if "weight" in data:data["weight"] = data["weight"][:-2]
    return data

#read in user preferences
def readUserPreferences(username):
    data={}
    with open(STUD_DIR+username+"/preferences.txt","r") as pref:
        lines = pref.readlines()
        x=0 
        while (x<len(lines)):
            key = lines[x].strip()[:-1]
            x+=1
            tempStore = list()
            while (x < len(lines)) and (lines[x].startswith("\t")):
                info = lines[x].strip().replace("'","&39;").replace('"','&#quot;')
                if info != "min:" and info != "max:":
                    tempStore.append(info)
                x+=1
            data[key] = tempStore
    if "height" in data:
        data["height"][0] = data["height"][0][:-1]
        data["height"][1] = data["height"][1][:-1]
    if "weight" in data:
        data["weight"][0] = data["weight"][0][:-2]
        data["weight"][1] = data["weight"][1][:-2]
    return data

def writePreferences(obj, out):
    for key in obj:
       
        out.write(key+":\n")
        unit = ""
        if key == "height" or key == "age":
            if key == "height":unit = "m"
            if key == "weight": unit ="kg"
            out.write("\tmin:\n")
            out.write("\t\t"+obj[key][0] +unit+"\n")
            out.write("\tmax:\n")
            out.write("\t\t"+obj[key][1]+unit+"\n")
        else:
            for data in obj[key]:
                out.write("\t"+data+"\n")

def writeFormat(data,fileHandle):
    for key in data:
        unit =""
        if data[key]:
            if key == "height": unit="m"
            if key == "weight": unit="kg"
            fileHandle.write(key+":\n")
            if type(data[key]) == str :
                fileHandle.write("\t"+data[key]+unit+"\n")
            else:
                for entry in data[key]:
                    fileHandle.write("\t"+entry+"\n")
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
    pageVars["page"] = arguments.getvalue("page")
    if pageVars["page"] == "logout":
        pageVars["page"] = "login"
    pageVars["profile"] = arguments.getvalue("user")
    user = arguments.getvalue("username")
    pw = arguments.getvalue("loginpassword")
    if (user and pw):
        if(authenticate(user,pw)):
            for cookieid, username in activeSess.items():
                if username == user:
                    del activeSess[cookieid]
            activeSess[cookie["id"].value]=user
            json.dump(activeSess,open("sessions","w"))
            pageVars["currUser"] = user
            print (navHandler(arguments.getvalue("page")))
            return
        else:
           pageVars["user"] = user
           pageVars["error"]="Invalid username or password"
    else:
        pageVars["user"] = ""
    return "login"
def imagesHandler():
    pageVars["title"] = "My Images"
    currUser = pageVars["currUser"]
    loginProf = users[currUser]
    upload = arguments.getvalue("upload")
    delete = arguments.getvalue("delete")

    if upload == "avatar":
        upfile = arguments["image"]
        if upfile.file:
           avatar = open(loginProf["avatar"],"w+")
           avatar.write(upfile.file.read())
        else:
            pageVars["error"] = "No File Uploaded"
    elif upload == "photo":
        if upfile and upfile.file:
            last = loginProf["photos"].lastIndex 
            n = re.match("photo(.*)",last).group(0)
            photoname = "photo"+str(int(n)+1).zfill(len(n))+".jpg"
            avatar = open(photoname,"w+")
            avatar.write(upfile.file.read())
        else:
            pageVars["error"] = "No File Uploaded"
    elif delete:
        deleted = loginProf["photos"][delete]
        del loginProf["photos"][delete]
        os.remove(deleted)


    with open("templates/images.html") as template:
        pageVars["template"] += Template(template.read()).safe_substitute(loginProf)
    return "nav"

def aboutHandler():
    pageVars["title"] = "Edit Profile"
    currUser = pageVars["currUser"]
    loginProf = users[currUser]
    action = arguments.getvalue("action")
    if action:
        if action == "delete":
            shutil.rmtree(STUD_DIR+currUser)
            return logoutHandler()
        elif action == "suspend":
            loginProf["suspend"] = "True"
        elif action == "unsuspend":
            loginProf["suspend"] = "False"
        elif action == "update":
            for key in undisclosed: 
                if arguments.getvalue(key):
                    value = arguments.getvalue(key)
                    if key == "birthdate":
                        loginProf[key] = value.replace("-","/")
                    elif key == "profiletext":
                        loginProf[key] = re.sub("<\s*/?\s*[^bip]\s+.*?>","",value).replace("\n","")
                    else:
                        loginProf[key]=value

            if arguments.getvalue("password"):
                value = arguments.getvalue("password")
                print value
                if value != arguments.getvalue("confirmpass"):
                    pageVars["error"] = "Passwords do not match!"
                elif 8<=len(value)<=16:
                    loginProf["password"]=value
                else: 
                    pageVars["error"] = "Password is wrong format!"

        profile = open(STUD_DIR+pageVars["currUser"]+"/profile.txt","w")
        writeProf = loginProf.copy()
        del writeProf["photos"]
        del writeProf["avatar"]
        writeFormat(writeProf, profile)    
                
    for key in undisclosed:   
        if key not in loginProf:
            loginProf[key] =""
        elif key == "birthdate":
            loginProf["birthdate"] = loginProf["birthdate"].replace("/","-")
    with open("templates/about.html","r") as template:
        pageVars["template"] += Template(template.read()).safe_substitute(loginProf)
    return "nav"
def preferencesHandler():
    pageVars["title"] = "My Match Preferences"
    currUser = pageVars["currUser"]
    pref = readUserPreferences(currUser)
    update = arguments.getvalue("update")
    if update:
        mini = arguments.getvalue("min")
        maxi = arguments.getvalue("max")
        if mini and maxi and mini <= maxi:
            if not pref.get(update): pref[update] = [0,0];
            pref[update][0] = mini
            pref[update][1] = maxi
        else:
            pageVars["error"] = "Invalid Range"

    for key in ["hair_colours","gender"]:
        if arguments.getvalue(key) == "add":
            try:
                toAdd = arguments.getvalue("add")
                if toAdd and toAdd not in pref[key]:
                    pref[key].append(toAdd.lower())
            except:
                pref[key] = [arguments.getvalue("add")]
        elif arguments.getvalue(key):
            try:
                del pref[key][int(arguments.getvalue(key))]
            except:
                pageVars["error"] = "Please delete a valid item"
    prefFile = open(STUD_DIR+pageVars["currUser"]+"/preferences.txt","w")
    writePreferences(pref, prefFile) 
    if "age" in pref: 
        pref["agemin"] = pref["age"][0]
        pref["agemax"] = pref["age"][1]
    if "height" in pref:
        pref["heightmin"] = pref["height"][0]
        pref["heightmax"] = pref["height"][1]
    if "weight" in pref:
        pref["weightmin"] = pref["weight"][0]
        pref["weightmax"] = pref["weight"][1]

    with open("templates/preferences.html","r") as template:
        pageVars["template"] += Template(template.read()).safe_substitute(pref)
    return "nav"




def interestHandler():
    pageVars["title"] = "My Interests"
    loginProf = users[pageVars["currUser"]]
    for key in listKeys:
        if arguments.getvalue(key):
            if arguments.getvalue(key) == "add":
                try:
                    toAdd = arguments.getvalue("add")
                    if toAdd and toAdd not in loginProf[key]:
                        loginProf[key].append(toAdd)
                except:
                    loginProf[key] = [arguments.getvalue("add")]
            else:
                del loginProf[key][int(arguments.getvalue(key))]
            profile = open(STUD_DIR+pageVars["currUser"]+"/profile.txt","w")
            writeProf = loginProf.copy()
            del writeProf["photos"]
            del writeProf["avatar"]
            writeFormat(writeProf, profile) 
            break
    with open("templates/interests.html","r") as template:
        pageVars["template"] += Template(template.read()).safe_substitute(loginProf)
    return "nav"
def registerHandler():
    user=arguments.getvalue("username")
    pw = arguments.getvalue("password")
    email = arguments.getvalue("email")
    name = arguments.getvalue("name")
    pwconfirm = arguments.getvalue("pwconfirm")
    if user and email and pw and pwconfirm and name:
        if not (6<=len(pw)<=18):
            pageVars["error"] = "Invalid Password"
        elif pw != pwconfirm:
            pageVars["error"] = "Passwords Do No Match"
        elif re.match(r'[^A-Z0-9]',user,re.IGNORECASE):
            pageVars["error"] = "Username may only contain alphanumeric characters"
        elif len(user)<4:
            pageVars["error"] = "Username must be atleast 4 characters"
        elif re.match('''[<|"'>]''',name):
            pageVars["error"] = "Invalid or mistyped name"
        else:
            d = ""+user+"/"
            if not os.path.exists(d):
               os.makedirs(d)
               profile = open(d+"profile.txt","w+")
               data = {"username":user,"password":pw,"email":email,"name":name}
               writeFormat(data,profile)
               open(d+"preferences.txt","w+")
               print '<b style="text-align:center">Please Check Your Email For Confirmation Email</b>'
               return loginHandler()
            else:
               pageVars["error"] = "Username already taken"
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
    if start >= end:
        start = end-1
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

        message = "<div>"+pageVars["currUser"]+" said:</div><p>" + message + '</p><a href="'+os.environ.get("SCRIPT_URI")+'?page=detail&user='+pageVars["currUser"]+'">Reply Back!</a>'
        subject="LOVE2041:"+pageVars["currUser"] +"Sent You A Message\nContent-Type:text/html" 
        to=user["email"]
        with open("error","w") as error:
            p1 = Popen(["mail","-s" ,subject,to],stdin=PIPE,stdout=error,stderr=error)
            p1.communicate(input=message)
    return "nav"

def browseHandler():
    pageVars["template"]+='<form action="love2041.cgi?page=browse" method="post">'
    return listHandler()
def matchHandler():
    pageVars["title"] = "Matches"
    pageVars["template"]+= '<form action="love2041.cgi?page=match" method="post">'
    global userKeys
    userKeys = sorted(userKeys,key=lambda key: users[key]["match"],reverse=True)
    return listHandler()
def searchHandler():
    pageVars["title"] = "Search"
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
          <input type="search" name="search" placeholder="Search For User" value="{0}">
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
        if (not page or page == "register" or page == "login"):
            page="browse";
    elif page != "register":
        page="login"

    if pageVars["currUser"] and page in matchPages:
        postProcess()
    page = pageHandler[page]()
    if page in template:
        with open("templates/"+template[page],'r') as file:
            html = Template(file.read()).safe_substitute(pageVars)
            return html
    return ""

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


pageHandler={"images":imagesHandler,"interests":interestHandler,"preferences":preferencesHandler,"about":aboutHandler,"match":matchHandler, "search":searchHandler, "login":loginHandler,"register":registerHandler,"browse":browseHandler,"detail":detailHandler,"logout":logoutHandler}

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
print '\n<html>\n  <head>\n    <meta charset=\"UTF-8\">\n    <title>\n      Love 2041\n    </title>\n    <link rel=\"stylesheet\" href=\"ionic/css/ionic.min.css\">\n <link rel=\"stylesheet\" href=\"custom.css\">    <link href="http://fonts.googleapis.com/css?family=Lobster" rel="stylesheet" type="text/css">\n    <script src=\"ionic/js/ionic.bundle.js\"></script>\n <script src=\"custom.js\"></script>\n </head>\n  <body ng-app="main" style=\"background:#FFA9C3; color:#444\">\n'


for folder in glob.glob(STUD_DIR+"*"):
    username = re.sub(STUD_DIR,"",folder)
    users[username] = readUserProfile(username)

for user in users:
    if users[user].get("suspend") != "True":
        userKeys.append(user)

html = navHandler(page)

print html

print '</body>\n</html>'


