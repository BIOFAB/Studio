'''
Created on Apr 13, 2011

@author: cambray
'''

import os
import re
from basic_seq_manip import revcomp

def parse_features(file="/Users/cambray/Dropbox/BIOFAB/Wet Lab/APE/Features/Default_Features.txt"):
    """
    parse txt file containing name and sequence of features
    for now, tab separated
    """
    h = open(file, 'r')
    features = []
    for l in h:
        tabs = l.split("\t")
        features.append((tabs[0], tabs[1].lower()))
    h.close()
    return features
    
def find_features(sequences, features, direction="+/-",internal=False):
    """
    find only complete features
    Does not take gap or incomplete features into account
    - sequence can be a simple sequence or a list of sequences
    - features is a list of (name, sequence) 2-uple
    """
    isstring=False
    if isinstance(sequences, str):
        isstring=True
        sequences=[sequences]
    # compile feature pattern for efficiency
    nfeatures=[]
    for i in range(len(features)):
        if "+" in direction:
            nfeatures.append(('%s'%features[i][0], features[i][1], re.compile(features[i][1])))
        if "-" in direction:
            revcompfeat = revcomp(features[i][1])
            nfeatures.append(('(-)%s'%features[i][0], revcompfeat, re.compile(revcompfeat)))
    # find position of all occurences
    mapping = []
    for seq in sequences:
        matches = []
        seq = seq.lower()
        for feat in nfeatures:
            for match in feat[2].finditer(seq):
                matches.append((match.start(), match.end(), feat[0]))
        rm = []
        if not internal:
        # get rid of internal features
            for i in range(len(matches)-1):
                if not i in rm:
                    for j in range(i+1, len(matches)):
                        if not j in rm:
                            # feature j inside i
                            if  matches[j][0] >= matches[i][0]\
                            and matches[j][1] <= matches[i][1]:
                                rm.append(j)
                            # feature i inside j
                            elif matches[i][0] >= matches[j][0]\
                            and  matches[i][1] <= matches[j][1]:
                                rm.append(i)
                                break
        mapping.append([])
        for i in range(len(matches)):
            if not i in rm:
                mapping[-1].append(matches[i])
        mapping[-1] = sorted(mapping[-1], key=lambda matches: matches[0])
    if isstring:
        mapping = mapping[0]
    return mapping

def format_annotation(mapping, html=True):
    """
    generate formated string to print
    """    
    transform=False
    if isinstance(mapping[0], tuple):
        mapping = [mapping]
        transform=True
    lines=[]
    for map in mapping:
        # populate sublists according to overlap
        lines.append([])
        topass = []
        while len(topass)!=len(map):
            current_stop=0
            lines[-1].append('')
            for i in range(len(map)):
                if i in topass:
                    continue
                if map[i][0]>=current_stop:
                    feature_len = map[i][1]-map[i][0]-2
                    if len(map[i][2]) <= feature_len:
                        feature_len -= len(map[i][2])
                        feature_str='='*(feature_len/2)+map[i][2]+'='*(feature_len/2+feature_len%2)
                    else:
                        feature_str=map[i][2][:feature_len]
                    if html:
                        lines[-1][-1]+="""%s<a title="%s">&#60;%s&#62;</a>""" % (" "*(map[i][0]-current_stop), map[i][2], feature_str)
                    else:
                        lines[-1][-1]+="%s<%s>" % (" "*(map[i][0]-current_stop), feature_str)
                    topass.append(i)
                    current_stop = map[i][1]
            lines[-1][-1]+="\n"
    if transform:
        lines = lines[0]
    return lines
          
def annotate(seq_path, feat_path):
    """
    extract and annotate sequences in a folder
    """
    seq_files = [file for file in os.listdir(seq_path) if (re.search("\.seq$", file))]
    sequences = []
    for file in seq_files:
        sequences.append("")
        h = open("%s/%s" %(seq_path,file), "r")
        for l in h:
            if not ">" in l:
                sequences[-1] += l.strip("\n\s").lower()
        h.close()
    features = parse_features(feat_path)
    mapping = find_features(sequences, features)
    for i in range(len(seq_files)):
        print seq_files[i]
        for j in range(len(mapping[i])):
            print "\t%s..%s\t%s" % (mapping[i][j][0],mapping[i][j][1],mapping[i][j][2])
    return

if __name__ == '__main__':
    s= "ATATCATTTAAAATTTATCAAAAAGAGTATTGACTTAAAGTCTAACCTATAGGATACTTACAGCCATCGAGAGTTTGGAATTCATTAAAGAGGAGAAAGGTACCATGAGCAAA"
    feat = find_features(s, parse_features(), internal=True)
    f = format_annotation(feat, html=False)
    print s 
    for l in f:
        print l 