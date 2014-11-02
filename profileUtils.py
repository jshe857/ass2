import glob,re

import static

STUD_DIR = "students/"



def readAllProfiles():
    users = {}
    userKeys = []
    for folder in glob.glob(STUD_DIR+"*"):
        username = re.sub(STUD_DIR,"",folder)
        users[username] = readUserProfile(username)

    for user in users:
        if users[user].get("suspend") != "True":
            userKeys.append(user)
    return (users,userKeys) 

#Match Making Algorithm generates a score for each user based on preferences
def matchMake(profile):
    currUser = pageVars["currUser"]
    loginProf = users[currUser]
    match = 0
    if currUser == profile["username"]:return "0"
    for key in static.listKeys:
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
def postProcess(users):
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
        return users
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
        if key not in static.listKeys:
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


