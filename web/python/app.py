
from mod_python import apache
from mod_python import util
import json
import commands
import re


def handler(req):

    form = util.FieldStorage(req,keep_blank_values=1)

    req.content_type = "text/plain"
    
    traces = form.get('traces', None)
    start = form.get('start', None)
    stop = form.get('stop', None)

    vars = {}
    vars['traces'] = traces
    vars['start'] = start
    vars['stop'] = stop
    vars['success'] = True
    vars['msg'] = "These are the variables I recieved"
    
    req.write(json.dumps(vars))

    return apache.OK



