
from mod_python import apache
from mod_python import util
import json
import commands
import re


def handler(req):

    form = util.FieldStorage(req,keep_blank_values=1)

    req.content_type = "text/plain"

    bar = form.get('bar', None)

    vars = {}
    vars['bar'] = bar

    if bar == None:
        req.write("no bar variable: try adding ?bar=test at the end of the url")
    else:
        req.write("json: " + json.dumps(vars))

    return apache.OK



