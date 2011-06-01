'''
Created on Feb 9, 2011

@author: cambray
'''

from mod_python import apache
from checkseq import *
import sys

def handler(req):

#    sys.stdout = req
#    execfile(req.filename)

    req.content_type = "text/html"
    req.write("<html><body>")
#    try:
    log = open('/home/biofabsftp/files/web/python/log','w')
    log.write("vhdchjvdc")
    get_parameters()

    req.write("Out: " + str(output_folder))


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
