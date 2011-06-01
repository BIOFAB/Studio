'''
Created on Sep 7, 2010

@author: Cambray Guillaume

---

This script is for batch checking of sequence traces against reference sequences

'''

import os
import subprocess
from shutil import rmtree
import re
import json
import getopt
import sys
import annotator
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
from Bio import AlignIO
from Bio.Align import MultipleSeqAlignment
from cap3_parser import parse_cap3
from abi_parser import get_trim
from checkseq_config import *

###

class Sequencing:
    def __init__(self, trace_path, ref_path, output_folder, ref_format='csv', parse_phrase='(\d+)\.(\d+)', starts=[0], stops=[0], oligo_path='', mapping_path=''):
        self.trace_path = trace_path
        self.parse_phrase = parse_phrase
        self.ref_path = ref_path
        self.ref_format = ref_format
        self.constructs = {}
        self.references = []
        self.oligo_path = oligo_path
        self.oligo_starts = {}
        self.oligo_stops = {}
        self.mapping_path = mapping_path
        self.starts = starts
        self.stops  = stops
        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        self._init_traces()
        if not self.constructs:
            raise(IOError, "No trace file found")
        self._init_ref()
        return
    
    def __getitem__(self, item):
        return self.constructs[item]
    
    def __contains__(self, item):
        return item in self.constructs.keys()
    
    def _init_traces(self):
        """
        if mapping path, read mapping of trace file to construct in a csv file (comma separated, text field can be w/ "")
        columns are: ref_name    clone#    folder    trace_id 
        """
        print 'Reading traces files...'
        if self.mapping_path:
            trace_files = {}
            h = open(self.mapping_path, "r")
            h.readline()
            for l in h:
                l = l.strip()
                l = l.replace('"','')
                l = l.split(',')
                if len(l) == 4:
                    ref_id, clone_id, subfolder, id = l
                else:
                    ref_id, clone_id, subfolder, id, note = l
                #ref_id = re.findall('\d+', ref_id)[0].lower()
                ref_id = ref_id.lower()
                ref_id = ref_id.replace('pfab', '')
                if not clone_id:
                    clone_id = 1
                clone_id = int(clone_id)
                if subfolder:
                    subfolder+='/'
                if not trace_files.has_key(subfolder):
                    trace_files[subfolder] = os.listdir('%s/%s' % (self.trace_path, subfolder))
                good_traces = []
                print "Traces in input folder"
                for trace_file in trace_files[subfolder]:
                    print trace_file
                    if re.findall('.*%s.*\.ab.$' % id.lower(), trace_file.lower()):
                        good_traces.append(trace_file)
                #if len(good_traces) > 1:
                #    print "Potentially ambiguous trace names: %s" % '; '.join(good_traces)
                if not good_traces:
                    print "No traces found with identifier '%s' : sequence will be ignored" % id
                    continue
                if not ref_id in self:
                    self.new_construct('', ref_id)
                if not clone_id in self[ref_id]:
                    self[ref_id].new_clone(clone_id, self.constructs[ref_id], location=id)
                for trace in good_traces:
                    quality, seq = get_trim('%s/%s%s' % (self.trace_path, subfolder, trace), quality_cutoff=15, lowquality_base_count=2, window_size=5, trim5=1, trim3=1, exclude=1)
                    if seq:
                        self[ref_id][clone_id].new_trace(''.join(seq), quality, trace[:-4])                
        else:
            trace_files = os.listdir(self.trace_path)
            for trace_file in trace_files:
                if not self.parse_phrase:
                    parse = re.findall("^([^_]*?)_??(\D*?\d+)\.??(\d)*.+\.ab.$", trace_file.lower())
                else:
                    parse = re.findall("%s.+\.ab.$" % self.parse_phrase, trace_file.lower())
                if not parse:
                    print "%s not parsed" % trace_file
                else:
                    #location, ref_id, clone_id = parse[0]
                    if len(parse[0]) == 2:
                        ref_id, clone_id = parse[0]
                    else:
                        ref_id = parse[0]
                        clone_id = 1
                    location = ''
                    ref_id = ref_id.lower()
                    if clone_id == '':
                        clone_id = 1
                    clone_id = int(clone_id)
                    if not ref_id in self:
                        self.new_construct('', ref_id)
                    if not clone_id in self[ref_id]:
                        self[ref_id].new_clone(clone_id, location)
                    quality, seq = get_trim('%s/%s' % (self.trace_path, trace_file), quality_cutoff=30, lowquality_base_count=2, window_size=10, trim5=1, trim3=1, exclude=1)
                    if seq:
                        self[ref_id][clone_id].new_trace(''.join(seq), quality, trace_file[:-4])        
    
    def _init_ref(self):
        print 'Reading reference sequences...'
        self.references = self.constructs.keys()
        self.references.sort()
        if self.ref_format == 'csv':
            h = open(self.ref_path)
            for l in h:
                l = l.strip("\n")
                l = l.replace('"','')
                parse = l.split(',')
                #print parse
                if len(parse) == 2:
                    ref, seq = parse
                else:
                    #print "Skipped reference entry: %s" % l
                    continue
                ref = ref.lower()
                ref = ref.replace('pfab', '')
                if ref in self.references:
                    if self[ref].seq:
                        raise IOError("Ambiguous construct name %s" % ref)
                    self[ref].update_seq(seq.upper())
            h.close()
        elif self.ref_format == 'genbank':
            #ref_files   = os.listdir(self.ref_path)
            print 'Genbank support not implemented yet'
        for ref in self.references:
            if not self[ref].seq:
                print "No reference sequence found for %s" % ref
                #self.constructs.pop(ref)
        return
        
    def new_construct(self, sequence, id):
        self.constructs[id] = Construct(sequence, id, iscircular=True, parent=self)
        return
    
    def analyse(self):
        total_nbr = len(self.constructs)
        done_nbr = 0.0
        next     = 5
        print 'Analysing data...\n|'+'-'*41+'|\n|',
        for construct in self.constructs:
            self[construct].get_boundaries()
            for clone in self[construct].clones:
                self[construct][clone].write_fasta(self.output_folder)
                self[construct][clone].align(cap3_to_alns, cap3_path, output_folder, construct, clone)
                self[construct][clone].analyse_aln()
                #self[construct][clone].summarize_errors()
                self[construct][clone].write_aln(self.output_folder)
            self[construct].set_validity()        
            done_nbr += 1
            progress = int(100*done_nbr/total_nbr) 
            if progress>=next:
                print '*',
                next+=5
        print '|' 
        return
    
    def output(self, html=True):
        good = ''
        bad = ''
        constructs = self.constructs.keys()
        constructs.sort()
        valid_nbr = 0
        for construct in constructs:
            if self[construct].isvalid:
                valid_nbr += 1
                if html:
                    good += '* %s:\t' % self[construct].id
                    for clone in self[construct].valid:
                        good += ' <a href="%s/%s.%s.html" target="_blank">clone#%s</a> (%s) %s;\t' % ('.', self[construct].id, clone.id, clone.id, clone.location, ' / '. join(clone.comments))
                    good += '<br />\n'
                else:
                    good += ' %s: clone%s\n' % (self[construct].id, '; clone#'.join([str(clone) for clone in self[construct].valid]))
            else:
                if html:
                    bad += ' <h2>%s</h2>\n' % self[construct].id
                    for clone in self[construct].nonvalid:
                        if clone.alns:
                            #bad += '<a href="%s/%s.%s.html" target="_blank">clone#%s</a> %s<br />\nerrors:<br /><iframe src ="%s/%s.%s.html" width="80%" height="300"></iframe>\n' % ('.', self[construct].id, clone.id, clone.id, ' / '. join(clone.comments), self[construct].id, clone.id, clone.id)
                            #bad += '%sclone#%s<br /><div style="width:5%%;Text-align:left;float:left;"><pre>bla\nbli\nblou</pre></div><div style="width:95%%;Text-align:left;float:right;"><iframe src ="./%s.%s.html" width="100%%" frameborder="0"></iframe></div>\n' % (self[construct].id, clone.id, self[construct].id, clone.id)
                            bad += ' <h3>%s.%s</h3>\n' % (self[construct].id, clone.id)
                            frame_name = 'frame%s.%s' % (self[construct].id, clone.id)
                            src_name = './BAD/%s/%s.%s.html' % (self[construct].id, self[construct].id, clone.id)
                            bad += '<iframe name="%s" src="%s" width="100%%" frameborder="0">Sorry, your browser does not support iFrames...</iframe><br />\n' % (frame_name, src_name)
                            for error_type in ('substitution','insertion','deletion','arrangement','coverage'):
                                if clone.errors_range[error_type]['nbr'] == 1:
                                    bad += '1 %s error: <a href="%s#error%i-%i" target="%s">%i-%i</a>' % (error_type, src_name, clone.errors_range[error_type]['bg'][0]+1, clone.errors_range[error_type]['end'][0], frame_name, clone.errors_range[error_type]['bg'][0]+1, clone.errors_range[error_type]['end'][0])
                                elif clone.errors_range[error_type]['nbr']:
                                    bad += '%i %s errors :' % (clone.errors_range[error_type]['nbr'], error_type)
                                    for i in range(clone.errors_range[error_type]['nbr']):
                                        bad += ' <a href="%s#error%i-%i" target="%s">%i-%i</a>' % (src_name, clone.errors_range[error_type]['bg'][i]+1, clone.errors_range[error_type]['end'][i], frame_name, clone.errors_range[error_type]['bg'][i]+1, clone.errors_range[error_type]['end'][i])
                        else:
                            bad +=  '<p>No alignments available...</p>\n'
                else:
                    bad += '%s\n' % self[construct].id
                    for clone in self[construct].nonvalid:
                        bad += 'clone%s (%s)\n' % (clone.id, '; '.join(clone.errors))
                    bad += '<br />\n'
        if html:
            h = open('%s/summary.html' % output_folder, 'w')
            h.write("""<head>
<title>Sequence Checker Summary</title>
<style type="text/css">
body {background-color:#F0F0F0}
h1 {margin:0px 0px 0px 0px;font-size:2em; font-weight:bold; color:white; background-color:#000000}
h2 {margin:3em 0px 0px 0px; padding: 0px 0px 0px 0px; font-size:1.5em; font-weight:bold; color:white; background-color:#413839; border-color:black;}
h3 {margin:0px 0px 0px 0px; padding: 0px 0px 0px 0px; font-size:1.25em; font-weight:bold; color:white; background-color:#6D7B8D; border-color:black;}
</style>
</head>
<body>
<pre>
""")
            h.write('<h1> :-) GOOD (%s/%s)</h1>\n%s\n\n<h1> :-( BAD (%s/%s)</h1>\n%s\n' % (valid_nbr, len(self.constructs), good, len(self.constructs)-valid_nbr, len(self.constructs), bad))
        else:
            h = open('%s/summary.txt' % output_folder, 'w')
            h.write('GOOD (%s/%s)\n%s\n\nBAD (%s/%s)\n%s\n</pre></body>' % (valid_nbr, len(self.constructs), good, len(self.constructs)-valid_nbr, len(self.constructs), bad))
        h.close()
        return
        
    def output_better(self, all=False):
        h = open('%s/welcome_aln.html' % output_folder, 'w')
        h.write('Click on the links below to see alignments.')
        h.close()
        h = open('%s/welcome_error.html' % output_folder, 'w')
        h.write('Click on the links below to see errors.')
        h.close()
        h = open('%s/GOOD/no_error.html' % output_folder, 'w')
        h.write('No error.')
        h.close()
        header = """<head>
 <title>Sequence Checker - Good Sequences</title>
 <style type="text/css">
  body {background-color:#F0F0F0}
  A:link {text-decoration: none; color: black}
  A:visited {text-decoration: none; color: purple}
  A:active {text-decoration: none}
  A:hover {text-decoration: underline; color: red;}
 </style>
 <script language="javascript">
  function loadTwo(aln2URL, errorURL)
  {
    parent.alnFRAME.location.href=aln2URL
    parent.errorFRAME.location.href=errorURL
  }
 </script>
</head>
<body>
 <pre>
"""
        constructs = self.constructs.keys()
        constructs.sort()
        valid_nbr = 0
        good = header
        bad  = header
        for construct in constructs:
            if self[construct].isvalid:
                valid_nbr += 1
                good += '%s - ' % self[construct].id
                offset = '\n'+' '*len(self[construct].id)+' - '
                path_error = './no_error.html'
                good_list = []
                for clone in self[construct].valid:
                    path_aln = './%s/%s.%s_1.html' % (self[construct].id, self[construct].id, clone.id)
                    good_list.append("""<a href="javascript:loadTwo('%s', '%s') "target="_self">%s.%s</a> [%s]""" % (path_aln, path_error, self[construct].id, clone.id, clone.location))
                good += offset.join(good_list) + '\n\n'
            if all or not self[construct].isvalid:
                if self[construct].nonvalid:
                    bad += '%s - ' % self[construct].id
                    offset1 = '\n'+' '*len(self[construct].id)+' - '
                    bad_list = []
                else:
                    continue
                for clone in self[construct].nonvalid:
                    errors_summary = ''
                    errors_local = '%s.%s : ' % (self[construct].id, clone.id)
                    offset2 = errors_local
                    path_error = '%s.%s_error.html' % (self[construct].id, clone.id)
                    if clone.alns:
                        location = " [%s]" % clone.location
                        offset3 = "\n"+" "*(len(offset1)-1+len(offset2)-3+len(location))
                        for index in range(len(clone.alns)):
                            path_aln = '%s.%s_%s.html' % (self[construct].id, clone.id, index+1)
                            if len(clone.alns) == 1:
                                bad_list.append("""<a href="javascript:loadTwo('./%s/%s', './%s/%s') "target="_self">%s.%s</a>%s : """ % (self[construct].id, path_aln, self[construct].id, path_error, self[construct].id, clone.id, location))
                            elif index == 0:
                                bad_list.append("""%s.%s%s * <a href="javascript:loadTwo('./%s/%s', './%s/%s') "target="_self">aln #%s</a> : """ % (self[construct].id, clone.id, location, self[construct].id, path_aln, self[construct].id, path_error, index+1))
                                errors_local += """<a href="./%s" target="alnFRAME">aln #1</a> - """ % path_aln
                            else:
                                errors_summary += """%s * <a href="javascript:loadTwo('./%s/%s', './%s/%s') "target="_self">aln #%s</a> : """ % (offset3, self[construct].id, path_aln, self[construct].id, path_error, index+1)
                                errors_local += """\n%s<a href="./%s" target="alnFRAME">aln #%s</a> - """ % (' '*len(offset2), path_aln, index+1)
                            if not index in clone.errors_range['arrangement']['aln_id']:
                                errors_summary_l1 = []
                                errors_local_l1 = []
                                for error_type in ('substitution','insertion','deletion','coverage'):
                                    if clone.errors_range[error_type]['nbr'] == 1:
                                        errors_summary_l1.append("""1 %s error (<a href="javascript:loadTwo('./%s/%s#error%i-%i', './%s/%s')">%i-%i</a>)""" % (error_type, self[construct].id, path_aln, clone.errors_range[error_type]['bg'][0]+1, clone.errors_range[error_type]['end'][0], self[construct].id, path_error, clone.errors_range[error_type]['bg'][0]+1, clone.errors_range[error_type]['end'][0]))
                                        errors_local_l1.append("""1 %s error: <a href="./%s#error%i-%i" target="alnFRAME">%i-%i</a>""" % (error_type, path_aln, clone.errors_range[error_type]['bg'][0]+1, clone.errors_range[error_type]['end'][0], clone.errors_range[error_type]['bg'][0]+1, clone.errors_range[error_type]['end'][0]))
                                    elif clone.errors_range[error_type]['nbr']:
                                        errors_summary_l2 = []
                                        errors_local_l2 = []
                                        for i in range(clone.errors_range[error_type]['nbr']):
                                            errors_summary_l2.append("""<a href="javascript:loadTwo('./%s/%s#error%i-%i', './%s/%s')">%i-%i</a>""" % (self[construct].id, path_aln, clone.errors_range[error_type]['bg'][i]+1, clone.errors_range[error_type]['end'][i], self[construct].id, path_error, clone.errors_range[error_type]['bg'][i]+1, clone.errors_range[error_type]['end'][i]))
                                            errors_local_l2.append("""<a href="./%s#error%i-%i" target="alnFRAME">%i-%i</a>""" % (path_aln, clone.errors_range[error_type]['bg'][i]+1, clone.errors_range[error_type]['end'][i], clone.errors_range[error_type]['bg'][i]+1, clone.errors_range[error_type]['end'][i]))
                                        errors_summary_l1.append('%i %s errors (%s)' % (clone.errors_range[error_type]['nbr'], error_type, ', '.join(errors_summary_l2)))
                                        errors_local_l1.append('%i %s errors (%s)' % (clone.errors_range[error_type]['nbr'], error_type, ', '.join(errors_local_l2)))
                                errors_summary += ' / '.join(errors_summary_l1)
                                errors_local += ' / '.join(errors_local_l1)
                            else:
                                errors_summary += """<a href="javascript:loadTwo('./%s/%s', './%s/%s')">Assembly error</a>""" % (self[construct].id, path_aln, self[construct].id, path_error)
                                errors_local   += """<a href="./%s" target="alnFRAME">Assembly error</a>""" % (path_aln)
                    else:
                        path_aln = '%s.%s_1.html' % (self[construct].id, clone.id)
                        errors_summary += 'No alignments..'
                        errors_local += 'No alignments..'
                    bad_list[-1] += errors_summary
                    h = open('%s/BAD/%s/%s.%s_error.html' % (output_folder, self[construct].id, self[construct].id, clone.id), 'w')
                    h.write("""<head>
 <style>
  A:link {text-decoration: none; color: black}
  A:visited {text-decoration: none; color: purple}
  A:active {text-decoration: none}
  A:hover {text-decoration: underline; color: red;}
 </style>
</head>
<body><pre>
%s
</pre></body>""" % errors_local)
                    h.close()
                bad += offset1.join(bad_list) + '\n\n'
        
        ###
        
        h = open('%s/GOOD/good.html' % output_folder, 'w')
        h.write('%s\n</pre>\n</body>' % good)
        h.close()
        h = open('%s/BAD/bad.html' % output_folder, 'w')
        h.write('%s\n</pre>\n</body>' % bad)
        h.close()
        h = open('%s/summary.html' % output_folder, 'w')
        h.write("""<head>
<title>Sequence Checker Summary</title>
<style type="text/css">
body {background-color:#F0F0F0}
h1 {margin:0px 0px 0px 0px;font-size:2em; font-weight:bold; color:white; background-color:#000000}
h2 {margin:3em 0px 0px 0px; padding: 0px 0px 0px 0px; font-size:1.5em; font-weight:bold; color:white; background-color:#413839; border-color:black;}
h3 {margin:0px 0px 0px 0px; padding: 0px 0px 0px 0px; font-size:1.25em; font-weight:bold; color:white; background-color:#6D7B8D; border-color:black;}
</style>
</head>
<body>
<iframe name="alnFRAME" src="./welcome_aln.html" width="100%%" frameborder="0">Sorry, your browser does not support iFrames...</iframe>
<iframe name="errorFRAME" src="./welcome_error.html" height="5%%" width="100%%" frameborder="0">Sorry, your browser does not support iFrames...</iframe>
<pre>
<h1> :-) GOOD (%s/%s)</h1>
<iframe name="good" src="./GOOD/good.html" height="30%%" width="100%%" frameborder="1" border-color="black">Sorry, your browser does not support iFrames...</iframe><br />
<h1> :-( BAD (%s/%s)</h1>
<iframe name="good" src="./BAD/bad.html"  height="30%%" width="100%%" frameborder="1" border-color="black">Sorry, your browser does not support iFrames...</iframe>
""" % (valid_nbr, len(self.constructs), len(self.constructs)-valid_nbr, len(self.constructs)))
        h.close()
        return
    
    def output_json(self):
        """
        Generates output in JSON format
        """
        output = {'seqcheck_json':[]}
        output_clones = []
        constructs = self.constructs.keys()
        constructs.sort()
        valid_nbr = 0
        for construct in constructs:
            output['seqcheck_json'].append({"construct_id":self[construct].id,
                                            "construct_status":self[construct].isvalid,
                                            "clone_nbr":len(self[construct].clones),
                                            "clones":[]})
            for clone_id in self[construct].clones:
                output['seqcheck_json'][-1]["clones"].append({"clone_id":clone_id,
                                                              "clone_status":self[construct][clone_id].isvalid,
                                                              "clone location":self[construct][clone_id].location,
                                                              "error_nbr":0,
                                                              "errors":[]})
                if not self[construct][clone_id].isvalid:
                    if not self[construct][clone_id].alns:
                        output['seqcheck_json'][-1]["clones"][-1]["clone_status"] = "N/A"
                    else:
                        for error_type in ('substitution','insertion','deletion','arrangement','coverage'):
                            output['seqcheck_json'][-1]["clones"][-1]["error_nbr"] = self[construct][clone_id].errors_range[error_type]['nbr']
                            ## TODO: n'arrive pas jusqu'ici
                            for i in range(self[construct][clone_id].errors_range[error_type]['nbr']):
                                output['seqcheck_json'][-1]["clones"][-1]["errors"].append({"error_type":error_type,
                                                                                            "error_start":self[construct][clone_id].errors_range[error_type]['bg'][i]+1,
                                                                                            "error_stop":self[construct][clone_id].errors_range[error_type]['end'][i]})
        return output
        
    def cleanup(self):
        for file in os.listdir(self.output_folder):
            if '.cap.' in file:
                os.remove('%s/%s' % (self.output_folder, file))
        return
    
    def reorganize(self, all=False):
        print 'Re-organizing files...'
        self.cleanup()
        good_output = '%s/%s' % (output_folder, 'GOOD')
        bad_output  = '%s/%s' % (output_folder, 'BAD') 
        rmtree(good_output, ignore_errors=True)
        rmtree(bad_output, ignore_errors=True)
        if not os.path.exists(good_output):
            os.mkdir(good_output)
        if not os.path.exists(bad_output):
            os.mkdir(bad_output)        
        for construct in self.constructs:
            if self[construct].valid:
                construct_output = '%s/%s' % (good_output, construct)
                if not os.path.exists(construct_output):
                    os.mkdir(construct_output)
                for clone in self[construct].valid:
                    for file in clone.files:
                        os.system ('mv "%s/%s" "%s/%s"' % (output_folder, file, construct_output, file))
                    for trace in clone.traces:
                        os.system ('cp "%s/%s.seq" "%s/%s.seq"' % (output_folder, clone[trace].description, construct_output, clone[trace].description))
                        os.system ('cp "%s/%s.ab1" "%s/%s.ab1"' % (output_folder, clone[trace].description, construct_output, clone[trace].description))
            if all or not self[construct].valid:
                if self[construct].nonvalid:
                    construct_output = '%s/%s' % (bad_output, construct)
                    if not os.path.exists(construct_output):
                        os.mkdir(construct_output)
                for clone in self[construct].nonvalid:
                    for file in clone.files:
                        os.system ('mv "%s/%s" "%s/%s"' % (output_folder, file, construct_output, file))
                    for trace in clone.traces:
                        os.system ('cp "%s/%s.seq" "%s/%s.seq"' % (output_folder, clone[trace].description, construct_output, clone[trace].description))
                        os.system ('cp "%s/%s.ab1" "%s/%s.ab1"' % (output_folder, clone[trace].description, construct_output, clone[trace].description))
        return

    
    
class Construct(SeqRecord):
    def __init__(self, sequence, id, iscircular, parent):
        SeqRecord.__init__(self, Seq(sequence), id=id, description='ref')
        self.iscircular = iscircular
        self.rearrange  = []
        self.sequencing = parent
        self.clones = {}
        self.isvalid = False
        self.valid = []
        self.nonvalid = []
        self.range = []
        self.annot = []
        self.update_annot()
        return
    
    def __getitem__(self, item):
        return self.clones[item]
    
    def __contains__(self, item):
        return item in self.clones.keys()
    
    def update_seq(self, sequence):
        if not sequence.__class__ == "Seq":
            seq = Seq(sequence)
        self.seq=seq
        self.update_annot()
        return
    
    def update_annot(self): 
        if self.seq.tostring() != '' and features_list:
            mapping    = annotator.find_features(self.seq.tostring(), features_list, internal=True)
            if mapping:
                self.annot = annotator.format_annotation(mapping)
        return
    
    def new_clone(self, id, parent, location=''):
        self.clones[id] = Clone(id, self, location)
        return
    
    def get_boundaries(self):
        # Parse start and stop positions
        starts = []
        stops  = []
        special_starts = []
        special_stops  = []
        index = -1
        for start_obj in self.sequencing.starts:
            index += 1
            # dealing w/ special positions
            if '+' in start_obj or '-' in start_obj:
                special_starts.append(index)
                starts.append(int(start_obj[1:]))
                continue
            # parsing offsets
            offset = 0
            if ':' in start_obj:
                start_obj = start_obj.split(':')
                start = start_obj[0]
                offset = int(start_obj[1])
            else:
                start = start_obj
            # start can be a simple position                
            if isinstance(start, int):
                starts.append(start+offset)
            # start can be a reference to a FAB id or a subsequence
            if isinstance(start, str):
                if 'oFAB'.lower() in start.lower():
                    if not start in self.sequencing.oligo_starts:
                        start = start.lower()
                        h = open(self.sequencing.oligo_path)
                        for l in h:
                            l = l.replace('"','').lower()
                            if re.findall('^%s,' % start, l):
                                data = l.split(',')
                                self.sequencing.oligo_starts[start] = data[5].replace(' ','')
                        h.close()
                        if not self.sequencing.oligo_starts[start]:
                            raise IOError('Primer %s does not have sequence!' % start)
                    pos = map_oligos(self.seq.tostring(), self.sequencing.oligo_starts[start], '+', offset=offset)
                    if pos == False:
                        raise IOError('No match found for %s (%s) (%)' % (start, self.sequencing.oligo_starts[start], self.id))
                    starts.append(pos)
                elif isDNA(start):
                    pos = map_oligos(self.seq.tostring(), start, '+', size=None, offset=offset)
                    if pos == False:
                        raise IOError('No match found for start %s (%s)' % (start, self.id))
                    starts.append(pos-len(start))
                else:
                    starts.append(int(start))
        index = -1
        for stop_obj in self.sequencing.stops:
            index += 1
            # dealing w/ special positions
            if '+' in stop_obj or '-' in stop_obj:
                special_stops.append(index)
                stops.append(int(stop_obj[1:]))
                continue
            # parsing offsets
            offset = 0
            if ':' in stop_obj:
                stop_obj = stop_obj.split(':')
                stop = stop_obj[0]
                offset = int(stop_obj[1])
            else:
                stop = stop_obj
            # stop can be a simple position        
            if isinstance(stop, int):
                starts.append(stop-offset)
            # stop can be a reference to a FAB id or a subsequence
            if isinstance(stop, str):
                if 'oFAB'.lower() in stop.lower():
                    if not start in self.sequencing.oligo_stops:
                        h = open(self.sequencing.oligo_path)
                        for l in h:
                            l = l.replace('"', '')
                            if re.findall('^%s,' % stop, l):
                                data = l.split(',')
                                self.sequencing.oligo_stops[stop] = data[5].replace(' ','')
                        h.close()
                    pos = map_oligos(self.seq.tostring(), Seq(self.sequencing.oligo_stops[stop]).reverse_complement().tostring(), '-', offset=offset)
                    if pos == False:
                        raise IOError('No match found for %s (%s)' % (stop, Seq(self.sequencing.oligo_stops[stop]).reverse_complement()))
                    stops.append(pos)
                elif isDNA(stop):
                    pos = map_oligos(self.seq.tostring(), stop, '+', size=None, offset=offset)
                    if pos == False:
                        raise IOError('No match found for start %s (%s)' % (stop, self.id))
                    stops.append(pos-1)
                else:
                    stops.append(int(stop))
        # Resolve special positions
        for index in special_starts:
            starts[index] = starts[index]+stops[index]
        for index in special_stops:
            stops[index] = starts[index]+stops[index]
        # Map position for circular constructs
        for start in starts:
            issue = []
            if start < 0:
                if self.iscircular:
                    start = len(self)+start
                else:
                    issue.append(start)
            elif start > len(self):
                if self.iscircular:
                    start = start-len(self)
                else:
                    issue.append(start)
        for stop in stops:
            if stop < 0:
                if self.iscircular:
                    stop = len(self)+stop
                else:
                    issue.append(start)
            elif stop > len(self):
                if self.iscircular:
                    stop = stop-len(self)
                else:
                    issue.append(start)
        if issue:
            raise IOError('Start or stop value out of range for linear construct (%s)' % ','.join(issue))
        # Modify reference according to range of interest to facilitate aln
        if self.iscircular:
            corrections = []
            for i in range(len(starts)):
                if stops[i] < starts[i]:
                    corrections.append(stops[i])
            if len(corrections) > 1:
                raise IOError('Problem dealing with rearrangement of circular reference for aln')
            if corrections:
                self.rearrange = len(self)-corrections[0]-1
                seq = self.seq.tostring()
                self.seq = Seq(seq[corrections[0]+1:]+seq[:corrections[0]+1])
                for i in range(len(starts)):
                    if starts[i] <= corrections[0]:
                        starts[i] += len(self.seq)-1 - corrections[0]
                    else:
                        starts[i] -= corrections[0]
                    if stops[i] <= corrections[0]:
                        stops[i] += len(self.seq)-1 - corrections[0]
                    else:
                        stops[i] -= corrections[0]
        # Resolve overlaps
        # Too complex for now...
#        mem_start = 0
#        mem_stop  = 0
#        for i in range(len(starts)):
#            if starts[i] < mem_stop:
#                
        # Update range
        starts.sort()
        stops.sort()
        for i in range(len(starts)):
            self.range.append(range(starts[i], stops[i]))
        if not self.range:
            self.range.append(range(len(self)))
        return
    
    def set_validity(self):
        for clone in self.clones.keys():
            if self.clones[clone].isvalid:
                self.valid.append(self.clones[clone])
                self.isvalid = True
            else:
                self.nonvalid.append(self.clones[clone])
        return


class Clone:
    def __init__(self, id, construct, location='No location'):
        self.id = id
        self.location = location
        self.construct = construct
        self.traces = {}
        self.quality = {}
        self.isvalid = False
        self.errors = {}
        self.errors_range = {'substitution':{'nbr':0, 'mem':-1, 'bg':[],'end':[]}, 
                             'coverage':{'nbr':0, 'mem':-1, 'bg':[],'end':[]},
                             'insertion':{'nbr':0, 'mem':-1, 'bg':[],'end':[]},
                             'deletion':{'nbr':0, 'mem':-1, 'bg':[],'end':[]},
                             'arrangement':{'nbr':0, 'mem':-1, 'aln_id':[]}}
        self.alns = None
        self.comments = []
        self.names = {}
        self.files = []
        return
    
    def __getitem__(self, item):
        return self.traces[item]
        
    def __repr__(self):
        return str(self.id)
    
    def new_trace(self, sequence, quality, id):
        self.traces[id] = SeqRecord(Seq(sequence), id=str(len(self.traces)), description=id)
        self.quality[id] = quality
        return
    
    def write_fasta(self, output_folder):
        self.files.append('%s.%s.fas' % (self.construct.id, self.id))
        self.names['0'] = 'ref: %s' % self.construct.id
        self.names['max'] = max(len(self.names['0']), 9)
        h=open('%s/%s' % (output_folder, self.files[-1]), 'w')
        h.write('>0_%s\n%s\n' % (self.construct.id, self.construct.seq.tostring()))
        index = 1
        for trace in self.traces:
            self.names[str(index)] = self.traces[trace].description
            if len(self.names[str(index)]) > self.names['max']:
                self.names['max'] = len(self.names[str(index)])
            h.write('>%i_%s\n%s\n' % (index, self.traces[trace].description, self.traces[trace].seq.tostring()))
            index += 1
        self.names['c'] = 'consensus'
        h.close()
        return
    
    def get_names(self):
        self.names['0'] = 'ref: %s' % self.construct.id
        index = 1
        self.names['max'] = max(len(self.names['0']), 9)
        self.names['c'] = 'consensus'
        for trace in self.traces:
            self.names[str(index)] = self.traces[trace].description
            if len(self.names[str(index)]) > self.names['max']:
                self.names['max'] = len(self.names[str(index)])
                index += 1
        return
    
    def align(self, method, *kwd):
        self.alns = (method(*kwd))
        return
    
    def analyse_aln(self):
        if not self.alns:
            print "No alignments for %s.%s" % (self.construct.id, self.id)
            return
        index = -1
        for aln in self.alns:
            #print aln.format('clustal')
            index += 1
            map = AlnMap(aln)
            ## identify aln not containing the reference sequence : problem in the construct
            if not "0_%s" % self.construct.id in ''.join(map.names):
                self.comments.append("Trace assembly not similar enough to reference to form a contig")
                self.errors_range['arrangement']['nbr'] +=1
                self.errors_range['arrangement']['aln_id'].append(index)
            ## correct alignments
            else:
                for span in self.construct.range:
                    for seq_pos in span:
                        match_flag = False
                        ref_base = aln[0][seq_pos]
                        deletion = 0
                        insertion = ''
                        substitution = ''
                        coverage = 0 
                        for seq_index in range(1,len(aln)-1):
                            if map.start[seq_index] <= seq_pos <= map.stop[seq_index]:
                            # reference is covered by trace
                                coverage += 1
                                if aln[seq_index][seq_pos] == ref_base:
                                # Trace match reference
                                    match_flag = True
                                elif ref_base == '-':
                                # Trace is an insertion
                                    insertion += aln[seq_index][seq_pos]
                                elif aln[seq_index][seq_pos] == '-':
                                # Trace is a deletion
                                    deletion += 1
                                else:
                                # Trace is a substitution
                                    substitution += aln[seq_index][seq_pos]
                        if match_flag:
                        # At least one of the sequence match the reference: no mutation
                            pass
                        else:
                        # None of the covering trace match the reference: real mutation
                            if not coverage:
                                self.errors[seq_pos] = 'coverage'
                                if self.errors_range['coverage']['mem'] == -1:
                                    self.errors_range['coverage']['bg'].append(seq_pos)
                                    self.errors_range['coverage']['nbr'] += 1
                                elif seq_pos != self.errors_range['coverage']['mem']+1:
                                    self.errors_range['coverage']['end'].append(self.errors_range['coverage']['mem']+1)
                                    self.errors_range['coverage']['bg'].append(seq_pos)
                                    self.errors_range['coverage']['nbr'] += 1
                                self.errors_range['coverage']['mem'] = seq_pos
                            elif deletion and not insertion and not substitution:
                                self.errors[seq_pos] = 'deletion'
                                if self.errors_range['deletion']['mem'] == -1:
                                    self.errors_range['deletion']['bg'].append(seq_pos)
                                    self.errors_range['deletion']['nbr'] += 1
                                elif seq_pos != self.errors_range['deletion']['mem']+1:
                                    self.errors_range['deletion']['end'].append(self.errors_range['deletion']['mem']+1)
                                    self.errors_range['deletion']['bg'].append(seq_pos)
                                    self.errors_range['deletion']['nbr'] += 1
                                self.errors_range['deletion']['mem'] = seq_pos
                            elif insertion and not deletion  and not substitution:
                                self.errors[seq_pos] = 'insertion'
                                if self.errors_range['insertion']['mem'] == -1:
                                    self.errors_range['insertion']['bg'].append(seq_pos)
                                    self.errors_range['insertion']['nbr'] += 1
                                elif seq_pos != self.errors_range['insertion']['mem']+1:
                                    self.errors_range['insertion']['end'].append(self.errors_range['insertion']['mem']+1)
                                    self.errors_range['insertion']['bg'].append(seq_pos)
                                    self.errors_range['insertion']['nbr'] += 1
                                self.errors_range['insertion']['mem'] = seq_pos
                            elif substitution and not deletion  and not insertion:
                                self.errors[seq_pos] = 'substitution'
                                if self.errors_range['substitution']['mem'] == -1:
                                    self.errors_range['substitution']['bg'].append(seq_pos)
                                    self.errors_range['substitution']['nbr'] += 1
                                elif seq_pos != self.errors_range['substitution']['mem']+1:
                                    self.errors_range['substitution']['end'].append(self.errors_range['substitution']['mem']+1)
                                    self.errors_range['substitution']['bg'].append(seq_pos)
                                    self.errors_range['substitution']['nbr'] += 1
                                self.errors_range['substitution']['mem'] = seq_pos
                             #Not necessary for now: arrangments do not have positions
#                            else:
#                                self.errors[seq_pos] = 'arrangements'
#                                if self.errors_range['arrangements']['mem'] == -1:
#                                    self.errors_range['arrangements']['bg'].append(seq_pos)
#                                    self.errors_range['arrangements']['nbr'] += 1
#                                elif seq_pos != self.errors_range['arrangements']['mem']+1:
#                                    self.errors_range['arrangements']['end'].append(self.errors_range['arrangements']['mem']+1)
#                                    self.errors_range['arrangements']['bg'].append(seq_pos)
#                                    self.errors_range['arrangements']['nbr'] += 1
#                                self.errors_range['arrangements']['mem'] = seq_pos
                for type in ('substitution','coverage','insertion','deletion'):
                    if len(self.errors_range[type]['bg']) == len(self.errors_range[type]['end'])+1:
                        self.errors_range[type]['end'].append(self.errors_range[type]['mem']+1)
                    elif len(self.errors_range[type]['bg']) != len(self.errors_range[type]['end']):
                        raise IOError('Problem while annotating mutations: %s.%s' % (self.construct.id, self.id))
            if not self.errors and not self.errors_range["arrangement"]["nbr"]:
                self.isvalid = True
        return 
        
    
    def write_aln(self, outpout_folder):
        if not self.alns:
            print "No alignments for %s.%s" % (self.construct.id, self.id)
            self.files.append('%s.%s_1.html' % (self.construct.id, self.id))
            h = open('%s/%s' % (output_folder,self.files[-1]), 'w')
            h.write("No alignments for %s.%s" % (self.construct.id, self.id))
            h.close()
            return
        if not self.errors_range:
            print "No mutation analysis... Lauching analysis"
            self.analyse_aln()
        ### 
        index = -1
        for aln in self.alns:
            index += 1
            self.files.append('%s.%s_%s.html' % (self.construct.id, self.id, index+1))
            h = open('%s/%s' % (output_folder, self.files[-1]), 'w')
            h.write("""<head>
<title>%s.%s Alignment</title>
<style type="text/css">
body {font-family:"Courier New"; background-color:white;}
f.substitution {background-color:red;color:white;type:bold}
f.insertion {background-color:red;color:white;type:bold}
f.deletion {background-color:red;color:white;type:bold}
f.arrangement {background-color:red;color:white;type:bold}
f.coverage {background-color:green;color:white;type:bold}
f.range {background-color:#FFF8C6;}
</style>
</head>
<body>
<pre>
""" % (self.construct.id, self.id))
            errors = [[],[]]
            to_print_html = ''
            offset = ' '*(self.names['max']+3)
            updated_ruler = offset
            # Good aln against reference
            if not index in self.errors_range['arrangement']['aln_id']:
                for seq_index in range(len(aln)-1):
                    to_print_html += self.names[aln[seq_index].id[0]].ljust(self.names['max']) +'   '
                    for pos in range(len(aln[0])):
                        for type in ('substitution','insertion','deletion','coverage'):
                            if pos in self.errors_range[type]['bg']:
                                to_print_html += '<f class="%s">' % type
                                i = self.errors_range[type]['bg'].index(pos)
                                errors[0].append('%s-%s' % (pos+1, self.errors_range[type]['end'][i]))
                                errors[1].append((pos + self.errors_range[type]['end'][i])/2)
                            if pos in self.errors_range[type]['end']:
                                to_print_html += '</f>'
                        to_print_html += aln[seq_index][pos]
                        if not seq_index:
                            for span in self.construct.range:
                                if pos == span[0]:
                                    updated_ruler += '<f class="range">'
                                elif pos == span[-1]:
                                    updated_ruler += '</f>'
                            if pos in errors[1]:
                                updated_ruler +='<a name="error%s"></a>' % errors[0][errors[1].index(pos)]
                            updated_ruler += ruler[pos]
                    to_print_html += '\n'
                # Annotations
                for line in self.construct.annot:
                    to_print_html += offset + line
            # Aln but no against reference
            else:
                self.files.append('%s.%s_%s.fas' % (self.construct.id, self.id, index+1))
                h2 = open('%s/%s' % (output_folder, self.files[-1]), 'w')
                h2.write(">%s.%s assembly %s\n%s" % (self.construct.id, self.id, index+1, aln[-1].seq.tostring()))
                h2.close()
                updated_ruler += ruler[:len(aln[0])]
                for seq_index in range(len(aln)-1):
                    to_print_html += self.names[aln[seq_index].id[0]].ljust(self.names['max']) +'   '+aln[seq_index].seq.tostring()
                    to_print_html += '\n'
                # Annotations
                if features_list:
                    mapping = annotator.find_features(aln[-1].seq.tostring(), features_list, internal=True)
                    if mapping:
                        annotations = annotator.format_annotation(mapping)
                        for line in annotations:
                            to_print_html += offset + line
#            if len(errors) > 1:
#                to_print_html += ' '*(self.names['max']+3)
#                last_pos = 0
#                for pos in errors[1:]:
#                    to_print_html += '<a href="#%s" target="_self">>> Next error >></a>%s' % (pos, ' '*(pos-last_pos))
#                    last_pos = pos 
#                to_print_html += '\n'
            h.write('%s\n%s</pre></body>' % (updated_ruler, to_print_html))
        h.close()
    
    def summarize_errors(self):
        positions = self.errors.keys()
        positions.sort()
        mem_position = positions[0]
        mem_type = self.errors[mem_position][0]
        bg = mem_position
        self.error_summary += '\t'
        for position in positions:
            if position == mem_position+1 and self.errors[position][0] == mem_type:
                mem_position = position
            else:
                if bg != mem_position:
                    self.error_summary += '%s-%s %s\n\t' % (bg, mem_position, self.errors[mem_position][0])
                else:
                    self.error_summary += '%s %s\n\t' % (bg, self.errors[bg][0])
                bg = position
                mem_position = position
                mem_type = self.errors[mem_position][0]
    ## ...To implement


class AlnMap:
    def __init__(self, aln):
        self.parent = aln
        self.ref_aln = []
        self.aln_ref = []
        self.start = []
        self.stop  = []
        self.names = []
        self.orientation = []
        for seq in aln:
            self.names.append(seq.id[:-1])
            self.orientation.append(seq.id[-1])
            self.ref_aln.append({})
            self.aln_ref.append({})
            real_position = -1
            stop = 0
            for index in range(len(seq)):
                if not seq[index] == '-':
                    real_position += 1
                    stop = index
                    self.ref_aln[-1][real_position] = index
                    self.aln_ref[-1][index] = real_position
            self.start.append(self.ref_aln[-1][0])
            self.stop.append(stop)
        return



###############################
###############################    



def cap3_to_alns(cap3_path, folder, construct, clone):
    option = '-z 1' # z=coverage depth for clipping #'-y 6' y=range for clipping
    path   = "%s/%s.%s.fas" % (folder, construct, clone)
    p = subprocess.Popen('%s "%s" %s' % (cap3_path, path, option), shell=True, stdout=subprocess.PIPE)
    alns = parse_cap3(p.stdout)
    alns_obj = []
    # process alignments (sequence direction...)
    for aln in alns:
        reverse = False
        records = []
        for name in aln.keys():
            if re.findall('^0_.+-$', name):
                reverse = True
            records.append(SeqRecord(Seq(aln[name]), id=name))
        if reverse:
            for record in records:
                record.seq = record.seq.reverse_complement()
        alns_obj.append(MultipleSeqAlignment(records))
        alns_obj[-1].sort()
    # also include singletons (as aln for simplicity)
    if os.path.getsize('%s.cap.singlets' % path):
        h = open('%s.cap.singlets' % path, 'r')
        records = list(SeqIO.parse(h, "fasta"))
        h.close()
        for record in records:
            alns_obj.append(MultipleSeqAlignment([record,record]))
    return alns_obj

#def muscle_to_aln(muscle_path, input, output):
#    os.system('%s -in %s -fastaout %s.aln -htmlout %s.html' % (muscle_path, input, output, output))
#    alns = AlignIO.parse(output+'.aln', "fasta")
#    for aln in alns:
#        aln.sort()
#    return aln

def map_oligos(ref, oligo, orientation, size=15, offset=30):
    ref = ref.lower()
    oligo = oligo.lower()
    if orientation == '+':
        if size:
            oligo = oligo[max(0,len(oligo)-size):]
        pos = ref.find(oligo)
        if pos == -1:
            return False
        return pos+len(oligo)+offset
    else:
        if size:
            oligo = oligo[:-max(0,len(oligo)-size)]
        pos = ref.rfind(oligo)
        if pos == -1:
            return False
        return pos-1-offset

def isDNA(seq):
    for l in seq.lower():
        if not l in 'atgc':
            return False
    return True

def get_ruler(size):
    ruler = ''
    length = len(ruler)
    while length < size:
        if length%10 == 9:
            ruler+=str(length+1)
        else:
            ruler+=' '
        length = len(ruler)
    return ruler

def get_parameters():
    # Declare parameters from config file
    global starts
    global stops
    global oligo_path
    global mapping_path
    global ref_path
    global trace_path
    global parse_phrase
    global output_folder
    global cap3_path
    global exhaustive
    global feat_path
    # Get input arguments (override configuration)
    o, a = getopt.getopt(sys.argv[1:], 'a:ehm:o:p:r:s:t:z:')                            
    opts = {}
    for k,v in o:                                                             
        opts[k] = v
    if opts.has_key('-h'):                                                   
        usage(); sys.exit(0)                                                         
    ## Check required arguments
    if not trace_path:
        if not opts.has_key('-t'):
            usage(); sys.exit("Please specify a folder containing the sequencing traces")
        trace_path = opts['-t']
    if not ref_path:
        if not opts.has_key('-r'):
            usage(); sys.exit("Please specify a .csv file containing the reference sequences")
        ref_path = opts['-r']
    if opts.has_key('-o'):
        output_folder = opts['-o']
    elif not output_folder:
        output_folder = trace_path
    ## Assign optional arguments
    all = False
    if opts.has_key('-e'):
        exhaustive= True
    if opts.has_key('-a'):
        starts = opts['-a'].split(',')
    if opts.has_key('-z'):
        stops = opts['-z'].split(',')
    oligo_path = ''
    if opts.has_key('-s'):
        oligo_path = opts['-s']
    if opts.has_key('-m'):
        mapping_path = opts['-m']
    if opts.has_key('-f'):
        feat_path = opts['-f']
    if opts.has_key('-p'):
        parse_phrase = opts['-p']
    # Check arguments consistency
    for elt in starts+stops:
        if isinstance(elt, str) and not isDNA(elt.split(':')[0]):
            if not oligo_path:
                usage(); sys.exit("Elements specifying boundaries of analysis contains primers: please specify a primer file.")
    if len(starts) != len(stops):
        usage(); sys.exit("Starts (-a) and stops (-e) should match. Not the same number of items (%s vs %s)." % (starts, stops))
    if not output_folder:
        output_folder = "%s/checkseq_output" % trace_path
    # Other
    if feat_path:
        global features_list
        features_list = annotator.parse_features(feat_path)
    global ruler
    ruler = get_ruler(10000)

def usage():                                            
    print """
seq_check : align sequencing traces against references sequences and check for consistency  

 seq_check  [-h] [-e] [-p <parse_regexp>] [-a <starts>] [-z <stops>] [-s <primers_file>] [-m <mapping>] [-f <features>] -t <input_traces_folder> -r <input_reference_seq> -o <output_folder>
 
 -a <starts>                 A list of starts to delimit the region(s) of the reference to analyse. Must match the number of stops (-z).
                             A start can be a primer name (then a primer file to look up must be specified with -r), an actual DNA string or a position.
                             Elements must be separated by coma and can be followed by ':x' for x is an integer specifying an offset from the specified position.
 
 -e                          exhaustive: output alignments for all clones ie show bad ones even if there are good ones 
 
 -f <features>               Path to a tab-separated annotation file (name /tab/ sequence)          
 
 -h                          print this message 
 
 -m <mapping>                path to a mapping file between reference sequence and sequencing traces
                             Tab separated with a header and the folllowing columns:
                             reference_sequence_name    clone_number    subfolder_in_input_traces_folder    id_in_traces_file_name
 
 -o <output_folder>          Path to the output folder (created, if does not exist)
 
 -p <parse_regexp>           Regular expression to parse ref name and clone number from the sequencing traces filenames
 
 -r <input_reference_seq>    Path to a csv file specifying name,sequence of the references (coma separated)
 
 -s <primers_file>           Path to a file containing oligo sequences
 
 -t <input_traces_folder>    Output sequences file
 
 -z <stops>                  A list of stops to delimit the region(s) of the reference to analyse. Must match the number of starts (-a).
                             A Stop can be a primer name (then a primer file to look up must be specified with -r), an actual DNA string or a position.
                             Elements must be separated by coma and can be followed by ':x' for x is an integer specifying an offset from the specified position.
"""

if __name__ == '__main__':
    ### INPUT
    get_parameters()
    ###
    ruler = get_ruler(10000)
    data = Sequencing(trace_path    = trace_path,
                      ref_path      = ref_path,
                      output_folder = output_folder,
                      #ref_format    = ref_format,
                      parse_phrase  = parse_phrase, 
                      starts        = starts, 
                      stops         = stops,
                      oligo_path    = oligo_path,
                      mapping_path  = mapping_path
                      )
    data.analyse()
    data.reorganize(all=exhaustive)
    data.output_better(all=exhaustive)
    #print json.dumps(data.output_json())
    print 'All set !'
    
#    ref_format = 'csv'
#    ref_path = '/Users/cambray/Downloads/MPL_Vivek_4Guillaume.csv'
#    trace_path = '/Users/cambray/Downloads/vivek_seq'
#    parse_phrase = '^(\d+)\.(\d)'
#    output_folder = '/Users/cambray/seq_check_out'
#    oligo_path = '/Users/cambray/Dropbox/BIOFAB/Wet Lab/Data/sequencing_oligos.csv'
#    starts = ['soFAB1:25']
#    stops  = ['soFAB2:25']
#    muscle_path = '/applications/Muscle'
#    cap3_path = '/applications/Cap3'
    ###
    #seq_folder = '/Users/cambray/Dropbox/BIOFAB/Wet Lab/Data/PLASMIDS_pFAB#'
#    ref_path = './seq_check_data/MPL_Vivek_4Guillaume.csv'
#    ref_format = 'csv'
#    trace_path = './seq_check_data' #'/Users/cambray/Dropbox/BIOFAB/Wet Lab/Data/SequencingResults_QuintaraFILES/test'
#    parse_phrase = '^(\d+)\.(\d)'
#    output_folder = './seq_ckeck_out'
#    oligo_path = './seq_check_data/sequencing_oligos.csv'
#    starts = ['soFAB1:25']
#    stops  = ['soFAB2:25']
#    #muscle_path = '/applications/Muscle'
#    cap3_path = '/applications/Cap3'
    ###


        
        
        

