#!/usr/bin/python

##############handlers.py##############################
#
#Library module for page specific logic and navigation
#
#######################################################

import glob,re,os,uuid,shutil,sys
from string import Template
from subprocess import Popen,STDOUT,PIPE

#User Import
import profileUtils
import static


users={}
userKeys = []
arguments ={}
cookieID = ""

#Page variables to be injected into the html template
pageVars = {"template":"","error":"","currUser":""}


#####################################Utility functions####################################################

#return true if user and pw combination is valid 
def authenticate(user,pw):
    profile = users.get(user)
    if profile and profile["password"] == pw:
        return True
    return False

def searchCookie(ID):
    for user in users:
        if users[user].get("cookie")==ID:
            pageVars["currUser"] = user
            break
    

######################################Page Handlers Here###################################################
def logoutHandler():
    try:
        currUser = pageVars["currUser"]
        del users[currUser]["cookie"]
        profileUtils.writeFormat(users[currUser],open(static.STUD_DIR+currUser+"/profile.txt","w"))
    except:
        print ("No Active Session For Cookie")
    return loginHandler()
def loginHandler():
    pageVars["page"] = arguments.getvalue("page")
    pageVars["profile"] = arguments.getvalue("user")
    if pageVars["page"] == "logout":
        pageVars["page"] = "login"
    user = arguments.getvalue("username")
    pw = arguments.getvalue("loginpw")
    if (user and pw):
        if(authenticate(user,pw)):
            users[user]["cookie"] = cookieID 
            profileUtils.writeFormat(users[user],open(static.STUD_DIR+user+"/profile.txt","w"))
            print (navHandler())
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
            shutil.rmtree(static.STUD_DIR+currUser)
            return logoutHandler()
        elif action == "suspend":
            loginProf["suspend"] = "True"
        elif action == "unsuspend":
            loginProf["suspend"] = "False"
        elif action == "update":
            for key in static.undisclosed: 
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

        profile = open(static.STUD_DIR+pageVars["currUser"]+"/profile.txt","w")
        writeProf = loginProf.copy()
        del writeProf["photos"]
        del writeProf["avatar"]
        profileUtils.writeFormat(writeProf, profile)    
                
    for key in static.undisclosed:   
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
    pref = profileUtils.readUserPreferences(currUser)
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
                pref[key] = [arguments.getvalue("add").lower()]
        elif arguments.getvalue(key):
            try:
                del pref[key][int(arguments.getvalue(key))]
            except:
                pageVars["error"] = "Please delete a valid item"
    prefFile = open("students/"+pageVars["currUser"]+"/preferences.txt","w")
    profileUtils.writePreferences(pref, prefFile) 
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
    for key in static.listKeys:
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
            profile = open(static.STUD_DIR+pageVars["currUser"]+"/profile.txt","w")
            writeProf = loginProf.copy()
            del writeProf["photos"]
            del writeProf["avatar"]
            profileUtils.writeFormat(writeProf, profile) 
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
               profileUtils.writeFormat(data,profile)
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
        template += Template(static.cardTemplate).safe_substitute(users[key]) 
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
    userKeys.remove(pageVars["currUser"])
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


################################################END##########################################################

#handler dispatcher dict
pageHandler={"images":imagesHandler,"interests":interestHandler,"preferences":preferencesHandler,"about":aboutHandler,"match":matchHandler, "search":searchHandler, "login":loginHandler,"register":registerHandler,"browse":browseHandler,"detail":detailHandler,"logout":logoutHandler}


################handles navigation and page logic#############################################################
def navHandler():
    searchCookie(cookieID)
    currUser = pageVars["currUser"] 
    page = arguments.getvalue("page")


    if page not in pageHandler: page = None;
    
    if currUser:
        if (not page or page == "register" or page == "login"):
            page="browse";
    elif page != "register":
        page="login"
    
    #Post Process if we want to display the data
    if currUser and page in static.matchPages:
        global users
        users = profileUtils.postProcess(users,currUser)
    page = pageHandler[page]()
    if page in static.template:
        with open("templates/"+static.template[page],'r') as file:
            html = Template(file.read()).safe_substitute(pageVars)
            return html
    return ""

