'''
Created on Feb 9, 2011

@author: cambray
'''

from mod_python import apache
from mod_python import util
from checkseq import *
import sys
import json
import commands
import re

def handler(req):

#    sys.stdout = req
#    execfile(req.filename)

    form = util.FieldStorage(req, keep_blank_values=1)
    req.content_type = "text/plain"

    traces = form.get('traces', None)
    start = form.get('start', None)
    stop = form.get('stop', None)
    response = {}
    
    
#    vars['traces'] = traces
#    vars['start'] = start
#    vars['stop'] = stop
#    vars['success'] = True
#    vars['msg'] = "These are the variables I recieved"
#
#    req.write(json.dumps(vars))


    req.content_type = "text/html"
    html = "<html><body>"
#    req.write("<html><body>")
#    try:
    log = open('/home/biofabsftp/files/web/foo/log','w')
    log.write("vhdchjvdc")
    get_parameters()

    html = html + "Out: " + str(output_folder)
    response['success'] = True
    response['msg'] = "The sequence check was successful."
    response['html'] = html
    req.write(json.dumps(response))
    #req.write("Out: " + str(output_folder))


#    return apache.OK

    log.write(output_folder)

    ruler = get_ruler(10000)
    data = Sequencing(trace_path    = trace_path,
                      ref_path      = ref_path,
                      output_folder = output_folder,
                      parse_phrase  = parse_phrase,
                      starts        = starts,
                      stops         = stops,
                      oligo_path    = oligo_path,
                      mapping_path  = mapping_path
                      )
    data.analyse()
    data.reorganize(all=exhaustive)
    data.output_better(all=exhaustive)
    log.close()
    return apache.OK

#    except Exception as e:
#        req.write("<h1>Exception</h1>")
#        req.write("<p>")

#        req.write(str(e).replace("\n", "<br/>\n"))


#        req.write("</p>")
#        req.write("</body></html>")
        
#        return apache.OK
