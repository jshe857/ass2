#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()  # for troubleshooting
import Cookie
import json

arguments=cgi.FieldStorage()
page=arguments.getvalue("page")
if not page: page="login"
print "Content-type: text/html"

print '\n<html>\n  <head>\n    <meta charset=\"UTF-8\">\n    <title>\n      Love 2041\n    </title>\n    <link rel=\"stylesheet\" href=\"ionic/css/ionic.min.css\">\n    <link href="http://fonts.googleapis.com/css?family=Lobster" rel="stylesheet" type="text/css">\n    <script src=\"ionic/js/ionic.bundle.js\">\n    </script>\n  </head>\n  <body style=\"background:#FFAAAA\">\n'

pageList={}
with open('pages.json','rw') as data:
    pageList=json.load(data)
if pageList[page]:
    print pageList[page]
else:
    print "Error"
print '</body>\n</html>'

