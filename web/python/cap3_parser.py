#!/usr/bin/python
###########################################
# Author: Brian Chan (birdchan@ucdavis.edu)
# Supervisor: Alexander Kozik (akozik@atgc.org)
# Date: February 27 2004
# Description:
#
#
# This python script extracts data from the contigs input
#    data file. It can produce output file(s) in two ways.
#
# Notation: [something]* means "something" can appear many times.
#      {something}* means the same.
#
# ====================================================
#
# Input file format:
#
#    [comment lines]*
#    {
#     ********* Contig i **********
#     seqA
#           [seq1 is in seqA]*
#     seqB
#           [seq5 is in seqB]*
#    }*
#
#    DETAILED DISPLAY OF CONTIGS
#    {
#     ********** Contig i **********
#      {
#                  .    :    .    :    .     :
#       [seq_j     ATGAAATGACCCAGATATGGGGGGGCC...]*
#       -------------------------------------------
#       consensus  ATGAAATGACCCAGATATGGGGGGGCC...
#      }*
#    }*
#
# ====================================================
#
#  Input file Example
#
#    ******** Contig 1 ************
#    seqA
#         seq1 is in seqA
#         seq2 is in seqA
#    seqB
#         seq5 is in seqB
#         seq6 is in seqB
#         seq7 is in seqB
#
#    DETAILED DISPLAY OF CONTIGS
#
#    ********* Contig 1 ***********
#                .    :    .    :    .
#    seq1        ATGAAAAAAAAAAAAAAAAAGTTT
#    seq2        ATGAAAAAAAAAAAAAAAAAGTTTT
#    -------------------------------------
#    consensus   ATGAAAAAAAAAAAAAAAAAGTTTT
#
#    ********* Contig 2 ***********
#                .    :    .    :    .
#    seq5        GGGGGGGGGATTTTTCCCCC
#    seq6                 ATTTTTCCCCCCCCCA
#    -------------------------------------
#    consensus   GGGGGGGGGATTTTTCCCCCCCCCA
#
#                .    :    .    :    .
#    seq6        AAAATTTTTTTT
#    seq7          AATTTTTTTTTTTGGGG
#    --------------------------------------
#    consensus   AAAATTTTTTTTTTTGGGG
#
#
# ====================================================
#
#  Notice: In this script, everything before the line
#    "DETAILED DISPLAY OF CONTIGS" will be skipped.
#
# ====================================================
#
#  First output option:
#    One output file will be generated with the following format
#
#    [Contig_i   numOfSeq   [seqName(start_index,end_index)]*  ]*
#
#    The seqName's are separated by "|"
#
#    From the sample input file, the output would be
#
#    Contig1  2   seq1(1,24)|seq2(1,26)
#    Contig2  3   seq5(1,20)|seq6(10,37)|seq7(28,44)
#
# ====================================================
#
#  Second output option:
#    Files will be generated according to each contig. Users are
#      asked to provide file prefix, file extension, and the directory
#      name which all the files will be stored under.
#
#    Suppose the user inputs "con" for file prefix, "align" for
#      file extension, and "tmp_dir" for directory name.
#
#    After running this script with the sample input file, these are the
#      files under directory "tmp_dir"
#
#    con1.align
#    con2.align
#
#    In con1.align,
#
#                .    :    .    :    .
#    seq1        ATGAAAAAAAAAAAAAAAAAGTTT
#    seq2        ATGAAAAAAAAAAAAAAAAAGTTTT
#    -------------------------------------
#    Contig_1    ATGAAAAAAAAAAAAAAAAAGTTTT
#
#    In con2.align,
#                .    :    .    :    .    :    .     :     .
#    seq5        GGGGGGGGGATTTTTCCCCC
#    seq6                 ATTTTTCCCCCCCCCAAAAATTTTTTTT
#    seq7                                   AATTTTTTTTTTTGGGG
#    --------------------------------------------------------
#    Contig_2    GGGGGGGGGATTTTTCCCCCCCCCAAAAATTTTTTTTTTTGGGG
#
#    Notice the name "consensus" becomes "Contig_i". This "i" is the
#      same as the one in the file name.
#
#
############################################

import sys
import string
from string import *
from string import rstrip
import re
from os import makedirs
from os.path import isdir
from os import chdir

############################################
# global
seqNameMaxLength = 22

############################################

class seqClass:

    def __init__(self, name, start):
        self.name = name
        self.start = start
        self.seq = ""
    def append(self, start, subSeq):
        # I assume "start" is valid... (the seq is not broken)
        self.seq = self.seq + subSeq
    def getName(self):
        return self.name
    def print_info(self):
        print self.name, self.start, self.seq
    def output_info_1(self, bar):
        output_string(self.name)
        startStr = "%d" % (self.start + 1)  # since index starts at 1
        endStr = "%d" % (self.start + len(self.seq))
        if bar == 1:
            output_string("(" + startStr + "," + endStr + ")|")
        else:
            output_string("(" + startStr + "," + endStr + ")")
    def output_info_2_consensus(self, contig_ID):
        self.output_info_2_x(contig_ID)
    def output_info_2_uncond(self):
        self.output_info_2_x(" ")
    def output_info_2_x(self, contig_ID):
        global contig_prefix
        name = ""
        if contig_ID == " ":
            name = self.name
        else:
            # name = "Contig_" + contig_ID
            # name = "Contig" + contig_ID
            name = contig_prefix + contig_ID
        output_string(name)
        i = len(name)
        global seqNameMaxLength
        while i < self.start + seqNameMaxLength:
            output_string(" ")
            i = i + 1
        output_string(self.seq + "\n")
    def output_info_2(self):
        if find(self.name, "consensus") == -1:
            self.output_info_2_uncond()

#------------------------------

class seqHeapClass:

    def __init__(self):
        self.seqList = []
        self.seqNum = 0
    def set_contig_ID(self, lines, i):
        line = get_line(lines, i)
        star1, contig_str, ID, start2 = split(line)
        self.contig_ID = ID
    def get_contig_ID(self):
        return self.contig_ID
    def find_seq_index(self, name):
        for i in range(len(self.seqList)):
            if self.seqList[i].getName() == name:
                return i
        return -1
    def readinSeq(self, name, start, subSeq):
        i = self.find_seq_index(name)
        if i != -1:   # if seq exists
            # append it to the existing seq
            subSeqStr = split(subSeq)
            subSeqStr = subSeqStr[0]       # take out the white sp
            self.seqList[i].append(start, subSeqStr)
        else:
            # insert a new seq
            newSeq = seqClass(name, start) # make a new empty seq
            subSeqStr = split(subSeq)
            subSeqStr = subSeqStr[0]       # take out the white sp
            newSeq.append(start, subSeqStr)   # put stuff into it
            self.seqList.append(newSeq)
            self.seqNum = self.seqNum + 1
    def clear(self):
        self.seqList = []
        self.seqNum = 0
    def print_info(self):
        print self.get_contig_ID()
        for l in self.seqList:
            l.print_info()
    def output_info_1(self):
        global contig_prefix
        # output_string("Contig" + self.get_contig_ID())
        output_string(contig_prefix + self.get_contig_ID())
        numOfSeqStr = "%d" % (self.seqNum - 1)
        output_string("\t" + numOfSeqStr + "\t")
        myList = []    # a list without the consensus seq
        for l in range(len(self.seqList)):  # build this list
            if find(self.seqList[l].getName(), "consensus") == -1:
                myList.append(self.seqList[l])
        for l in range(len(myList)):  # output this list
            if l != len(myList) - 1:
                myList[l].output_info_1(1)
            else:
                myList[l].output_info_1(0)
        output_string("\n")
    def output_dot_line(self, con_i):
        global seqNameMaxLength
        dotLen = len(self.seqList[con_i].seq)
        for i in range(seqNameMaxLength):
            output_string(" ")
        for i in range(dotLen):
            if (i+1) % 10 == 0:
                output_string(":")
            elif (i+1) % 5 == 0:
                output_string(".")
            else:
                output_string(" ")
        output_string("\n")
    def output_underscored_line_and_consensus(self, con_i):
        # output the underscored line
        global seqNameMaxLength
        conLen = len(self.seqList[con_i].seq)
        for i in range(seqNameMaxLength):
            output_string(" ")
        for i in range(conLen):
            output_string("-")
        output_string("\n")
        # output the consensus line
        self.seqList[con_i].output_info_2_consensus( self.get_contig_ID() )
    def output_info_2(self):
        global contig_prefix
        global output_suffix
        output_filename = contig_prefix + self.contig_ID + "." + output_suffix
        global fp_out
        fp_out = open(output_filename, "wb")
        # find where consensus is
        con_i = -1   # index of consensus
        for i in range(self.seqNum):
            if find(self.seqList[i].name, "consensus") != -1:
                con_i = i
        if con_i == -1:
            print "No consensus found in", self.get_contig_ID()
            sys.exit(0)
        # output the dot line
        self.output_dot_line(con_i)
        # output the seq's
        for i in range(self.seqNum):
            self.seqList[i].output_info_2()
        # output the underscored line and the consensus seq
        self.output_underscored_line_and_consensus(con_i)
        fp_out.close()
        
    def get_aln(self):
        global all_aln
        all_aln.append({}) 
        max_length = 0
        for i in range(self.seqNum):
            all_aln[-1][self.seqList[i].name] = '-'*self.seqList[i].start+self.seqList[i].seq
            length = len(all_aln[-1][self.seqList[i].name])
            if length > max_length:
                max_length = length
        for name in all_aln[-1].keys():
            length = len(all_aln[-1][name])
            if length < max_length:
                all_aln[-1][name] += '-'*(max_length-length)

############################################
# global

debug_01 = 0       # print out line info

fp_in = 0          # file pointer for input
fp_out = 0         # file pointer for output
output_format = 0  # what kind of output

seqRow = 0         # which row are we at in each contig
seqNameLength = 22 # constant, length of a seq name
seqLength = 60     # constant, length of a seq line excluding the seq name
lineLength = seqNameLength + seqLength  # constant, length of a seq line
seqHeap = seqHeapClass()  # the obj that stores everything within a contig

contig_dirname = "CAP3_Alignments"
contig_prefix = "Contig"
output_suffix = "aln"

############################################

def read_contigs_info():
    global fp_in
    lines = fp_in.readlines()
    if not lines:
        print "No input in the input file"
        sys.exit("No input in the input file")   # if no input, exit
    i = 0  # the line index

    # jump to the start line
    i = line_num_string(lines, i, "DETAILED DISPLAY OF CONTIGS")

    # jump to the next contig section
    # i = line_num_string(lines, i, "Contig")
    # next_contig_index = line_num_string(lines, i+1, "Contig")
    i = line_num_string(lines, i, " Contig ")
    next_contig_index = line_num_string(lines, i+1, " Contig ")

    while i < len(lines)-1:

        global seqRow
        global seqHeap
        seqRow = 0
        seqHeap.clear()
        seqHeap.set_contig_ID(lines, i)

        while i < next_contig_index:
            i = i + 1   # the line after the contig line
            line = get_line(lines, i)
            if is_seq_data_line(line) == 1:
                if debug_01 == 1:
                    # print "line ", i, " is a seq_data_line"
                    print `i`
                do_seq_data(line)
            elif is_consensus_line(line) == 1:
                if debug_01 == 1:
                    # print "line ", i, " is a consensus_line"
                    print "  -- C -- ", i
                do_consensus(line)
            elif is_blank_line(line) == 1:
                if debug_01 == 1:
                    # print "line ", i, " is a blank line"
                    print `i`

        # show what we got
        #seqHeap.print_info()
        # output data into output file
        if output_format == 1:
            seqHeap.output_info_1()
        elif output_format == 2:
            seqHeap.output_info_2()
        else:
            seqHeap.get_aln()

        # jump to the next contig section
        # i = line_num_string(lines, i, "Contig")
        i = line_num_string(lines, i, " Contig ")
        next_contig_index = line_num_string(lines, i+1, "*****")


# -----------------------------------------

def get_line(lines, index):
    line = lines[index]
    line = rstrip(line)   # get rid of \n
    return line

def line_num_string(lines, index, pattern):   # stop at the matched line
    i = index
    while 1:
        if i >= len(lines):
            return len(lines)-1
        line = get_line(lines, i)
        if find(line, pattern) != -1:
            break
        i = i + 1
    return i

def output_string(str):
    global fp_out
    fp_out.write(str)

def is_x_line(line, x):
    if find(line, x) != -1:
        return 1
    return 0

def is_seq_data_line(line):
    if not is_consensus_line(line) and not is_x_line(line, "*****") and len(line) > 0 and line[0] != " ":
        return 1
    else:
        return 0

def is_consensus_line(line):
    return is_x_line(line, "consensus")

def is_blank_line(line):
    if len(line) == 0:
        return 1
    return 0

def get_start_of_seq_index(seq):
    for i in range(len(seq)):
        if seq[i] != " ":
            return i
    print "Error in get_start_of_seq_index, i =", i
    sys.exit(0)

def do_seq_data(line):
    global seqHeap
    # the index factors row-wise
    global seqRow
    global lineLength
    global seqLength
    # the seq name and the whole seq
    global seqNameMaxLength
    seqName = line[0:seqNameMaxLength]
    seqName = split(seqName)
    seqName = seqName[0]
    seq = line[seqNameMaxLength:lineLength]
    # the index factor column-wise
    j = get_start_of_seq_index(seq)
    seqHeap.readinSeq(seqName, seqRow * seqLength + j, seq)

def do_consensus(line):
    # increment the seqRow counter
    global seqRow
    seqRow = seqRow + 1
    # read consensus line
    global seqHeap
    global seqNameMaxLength
    seqName = line[0:seqNameMaxLength]   # better be "consensus" ...
    seq = line[seqNameMaxLength:lineLength]
    seqHeap.readinSeq(seqName, 0, seq)

def parse_cap3(input):
    global output_format
    global all_aln
    global fp_in
    output_format = None
    all_aln = []
    if isinstance(input, file):
        fp_in = input
    else:
        fp_in = open(input, "rb")
    read_contigs_info()
    fp_in.close()
    return all_aln
    

############################################

if __name__ == "__main__":
    
    # My modifs
    all_aln = parse_cap3('/Users/cambray/out')
    print all_aln
    
    # Normal program
    ## what output?
    #s = raw_input("What type of output do you want? (1/2): ")
    #if s != "1" and s!= "2":
    #    print "Unknown output style"
    #    sys.exit(0)
    #if s == "1":
    #    output_format = 1
    #if s == "2":
    #    output_format = 2
    #
    ## ask for input
    #s = raw_input("Enter the SOURCE file name: ")
    #input_filename = s
    #
    #if output_format == 1:
    #    s = raw_input("Enter the DESTINATION file name: ")
    #    output_filename = s
    #
    #    # checking input
    #    if input_filename == output_filename:
    #        print "input file is the same as output file"
    #        sys.exit(0)
    #
    #        print "Default contig file name prefix is", contig_prefix
    #        s = raw_input("Enter the contig file name prefix:")
    #        if s != "":
    #                contig_prefix = s
    #        else:
    #                contig_prefix = "Contig"
    #
    #if output_format == 2:
    #    # s = sys.argv[1]
    #    # if s != "":
    #    # contig_dirname = s
    #    # else:
    #    # contig_dirname = "CAP3_Alignments"
    #    contig_dirname = raw_input("Enter the DESTINATION directory with alignments: ")
    #
    #    print "Default contig file extension is", output_suffix
    #    s = raw_input("Enter the contig file extension :")
    #    if s != "":
    #        output_suffix = s
    #    else:
    #        output_suffix = "aln"
    #
    #    print "Default contig file name prefix is", contig_prefix
    #    s = raw_input("Enter the contig file name prefix:")
    #    if s != "":
    #        contig_prefix = s
    #    else:
    #        contig_prefix = "Contig"
    #
    #
    ## open the input and output file
    #print "read data from the input file", input_filename, "..."
    #fp_in = open(input_filename, "rb")
    #if output_format == 1:
    #    fp_out = open(output_filename, "wb")
    #else:
    #    if not isdir(contig_prefix):
    #        makedirs(contig_dirname, 0755)   # for the output files
    #    chdir(contig_dirname)    # go into the output dir
    #read_contigs_info()
    #fp_in.close()
    #if output_format == 1:
    #    fp_out.close()
    #else:
    #    chdir("..")
    

