#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import Cookie
import glob


print "Content-type: text/html"
print '\n<html>\n  <head>\n    <meta charset=\"UTF-8\">\n    <title>\n      Love 2041\n    </title>\n    <link rel=\"stylesheet\" href=\"ionic/css/ionic.min.css\">\n <link rel=\"stylesheet\" href=\"custom.css\">    <link href="http://fonts.googleapis.com/css?family=Lobster" rel="stylesheet" type="text/css">\n    <script src=\"ionic/js/ionic.bundle.js\">\n    </script>\n  </head>\n  <body style=\"background:linear-gradient(#FF2A68,#FF5E3A); color:#444\">\n'

pageList={"login":"index.html","register":"register.html"}

arguments=cgi.FieldStorage()
page=arguments.getvalue("page")

if not page: page="login"


if page in  pageList:
    with open(pageList[page],'r') as file:
        html = file.read()
        print html
else:
    print "Error"

print '</body>\n</html>'

#def processPage(html):

#def authenticate(user,pw):
