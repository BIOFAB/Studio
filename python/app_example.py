from mod_python import apache
from test import *

def handler(req):
  req.content_type = "text/html"
  req.write("<html><body>")
  req.write("<h1>Hello World!</h1>")
  req.write("<p>The manual for <a href='http://www.modpython.org/live/mod_python-3.2.8/doc-html/modpython.html'>mod_python</a> has more info.</p>")
  req.write("<p>The test module's foo function says: " + foo() + "</p>")
  req.write("</body></html>")
  return apache.OK
