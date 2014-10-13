#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()  # for troubleshooting


arguments=cgi.FieldStorage()


print "Content-type: text/html"
print """
<html>
  <head>
    <meta charset="UTF-8">
    <title>
      Love 2041
    </title>
    <link rel="stylesheet" href="ionic/css/ionic.min.css">
    <link href='http://fonts.googleapis.com/css?family=Lobster' rel='stylesheet' type='text/css'>
    <script src="ionic/js/ionic.bundle.js">
    </script>
  </head>
  <body style="background:#FFAAAA">
    <div style="text-align:center; padding-top:10%">      
      <h1 style="display:inline-block;margin: 0 auto; font-family: 'Lobster', cursive; font-size:60px; color:#444">
        love2
      </h1>
      <i class="icon ion-heart assertive" style="font-size:60px;">
      </i>
      <h1 style="display:inline-block;margin: 0 auto; font-family: 'Lobster', cursive; font-size:60px; color:#444; margin-left:-15px">
        41
      </h1>
      <form action="" method="post">
      <div class="card" style="padding:60px; width:50%; margin:20px auto; border-radius:5px; background:#fafafa">
        <label style="background:#fafafa" class="item item-input">
          <input  type="text" name="username" placeholder="Username">
        </label>
        <label style="background:#fafafa" class="item item-input">
          <input  type="password" name="username" placeholder="Password">
        </label>
      </div>
    </div>
    <button class="button button-assertive" style="display:block; width:50%; margin:0 auto; background:#D46A6A;border:0;  border-radius:5px">
      Login
    </button>
    </form>
    <a href="#" style="display:block; text-align:center; padding-top:20px; color:white">
      Register
    </a>

  </body>
</html>
"""