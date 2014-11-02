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
import Cookie,os,uuid,sys

########User Imports########
import handlers
import profileUtils

#mock class for cgi debugging from terminal
class MockArguments:
    def __init__(self,args): self.data = args
    def getvalue(self, key):
        return self.data.get(key)


#read in cookie info
cookie=Cookie.SimpleCookie()
if 'HTTP_COOKIE' in os.environ:
    cookie_string=os.environ.get('HTTP_COOKIE')
    cookie.load(cookie_string)
#generate new id if no cookie sent by browser
if "id" not in cookie:cookie["id"]= uuid.uuid1();




if (os.environ.get("REQUEST_URI")):
    arguments=cgi.FieldStorage()
    
#DEBUG PURPOSES ONLY - READ INPUT FROM STDIN
else:
    data = {}
    for arg in sys.stdin:
        pair = arg.strip().split(" ")
        data[pair[0]] = pair[1]
    arguments=MockArguments(data)

#boiler plate html strings
print "Content-type: text/html"
print cookie
print '\n<html>\n  <head>\n    <meta charset=\"UTF-8\">\n    <title>\n      Love 2041\n    </title>\n    <link rel=\"stylesheet\" href=\"ionic/css/ionic.min.css\">\n <link rel=\"stylesheet\" href=\"custom.css\">    <link href="http://fonts.googleapis.com/css?family=Lobster" rel="stylesheet" type="text/css">\n    <script src=\"ionic/js/ionic.bundle.js\"></script>\n <script src=\"custom.js\"></script>\n </head>\n  <body ng-app="main" style=\"background:#FFA9C3; color:#444\">\n'

(users,userKeys) = profileUtils.readAllProfiles()
handlers.users = users
handlers.userKeys = userKeys
handlers.arguments = arguments
handlers.cookieID = cookie["id"].value
html = handlers.navHandler()

print html

print '</body>\n</html>'


