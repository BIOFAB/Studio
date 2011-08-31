'''
 ######################################################################### 
 #  Copyright (C) 2010 Dokyun Na <blisszen@kaist.ac.kr>                  #
 #                                                                       #
 #  This program is based on algorithms developed by researchers at      #
 #  KAIST: Korea Advanced Institute of Science and Technology, and       #
 #   published in the paper:                                             #
 #                                                                       #
 #    Mathematical modeling of translation initiation for the            #
 #    estimation of its efficiency to computationally design mRNA        #
 #    sequences with a desired expression level in prokaryotes.          #
 #                  BMC Systems Biology (2010) 4(1): 71                  #
 #                  http://www.biomedcentral.com/1752-0509/4/71          #
 #                                          -- Na et al.                 #
 #                                                                       #
 #  This program is free software; you can redistribute it and/or        #
 #  modify it under the terms of the GNU Affero General Public License   #
 #  as published by the Free Software Foundation; either version 3, or   #
 #  any later version.                                                   #
 #                                                                       #
 #  Commercial licensing of this program is also possible.               #
 #  Contact Dokyun Na <blisszen@kaist.ac.kr>                             #
 #        or Doheon Lee <dhlee@kaist.ac.kr> for information about        #
 #  commercial licensing options.                                        #
 #                                                                       #
 #  This program is distributed in the hope that it will be useful, but  #
 #  WITHOUT ANY WARRANTY; without even the implied warranty of           #
 #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU    #
 #  General Public License for more details.                             #
 #                                                                       #
 #  You should have received a copy of the GNU Affero General Public     #
 #  License along with this program (in the COPYING.txt file) if not,    #
 #  write to the Free Software Foundation, Inc.,                         #
 #  51 Franklin St, Fifth Floor, Boston, MA                              #
 #  02110-1301, USA.                                                     #
 #                                                                       #
 #########################################################################
'''

import SDFINDER
import RBS_sj
import sys
#from pylab import *
#import matplotlib.pyplot  as pyplot
import COMMON

#antiSD_Ecoli = "UCACCUCCUU"
antiSD_Ecoli = "CUCCUU"
# SD_11
#antiSD_Ecoli = "UGGA UCACCUCCUU"

# antiSD_Ecoli = "CUGCGGUUGGA UCACCUCCUU A"
# In this codes, all anti-SD sequence is determined by the above sequence
# including positions, lengths

#UTR_LEN=200
#CDS_LEN=300

#RDS_LEN = 37


# import this py file.
# use CalculateRBSScore(utr, cds)
# that's all.



config = COMMON.CONFIG()

# parameters for kinetics
GENE_COPY_NUMBER=100.0
RNA_SYNTHESIS_RATE=20.0
RIBOSOMES_PER_RNA=20.0
FREE_RIBOSOME_NUMBER=57000.0
RNA_HALF_LIFE=2.0  # /min


def findSD(seq, atg_index, aSD):
    ''' finds the index of SD'''
    
    sff = SDFINDER.SDFINDER()
    sff.setAll( seq, aSD, atg_index,  37, 1)
    sff.setPerl(True)
    sff.find()
    
    return [sff.getFoundSDIndex(), \
            sff.getFoundSpacerLen(), \
            sff.getFoundSDSequence()            ]

def trim(seq, sd_pos, atg_index):
    '''trims a sequence for optimal folding energy calculation'''
    
    
    UTR_LEN = config.getTrimUTRLength()
    CDS_LEN = config.getTrimCDSLength()
    
    RBS_LEN_BEFORE_SD = config.getUTRLength()
    RBS_LEN_AFTER_SD = config.getDTRLength()
    
    
    utr = seq[ : sd_pos ]
    cds=seq[ sd_pos: ]
    
    uL = len(utr)-UTR_LEN
    if uL>0:
        sd_pos=sd_pos-uL
        atg_index=atg_index-uL
        
    if len(utr)>UTR_LEN:
        utr= utr[-UTR_LEN:]
    if len(cds)>CDS_LEN:
        cds=cds[:CDS_LEN]
        
    seq = utr+cds
    return [seq, sd_pos, atg_index]

def markingRDS(seq, sd_pos):
    
    # from n_u bp upstream of SD and n_d bp downstream of the last of RDS_LEN
    # christ ATG  -35, +35   70bp .
    #   SD 10  36bp .     .
    # 
    RDS_LEN = 6  #config.getDTRLength()
    
    n_u = config.getUTRLength() #+ 15
    n_d = config.getDTRLength() #+ 0
    
    seq = seq [ : sd_pos - n_u ].lower() + \
        seq[ sd_pos - n_u : sd_pos + RDS_LEN + n_d ].upper()\
        + seq[ sd_pos + RDS_LEN + n_d : ].lower()
    
    
    #print seq
    
    return seq


def clearing(seq):
    seq = seq.replace(' ', '')
    return seq

def CalculateRBSScore( utr, cds, method=2 ):  #method=2 uses sympy
    '''calculates RBS scores'''
    
    atg_index = len(utr)
    start_codon=cds[:3]
    stopcodon="TAAT"
    
    seq = utr.strip() + cds.strip()
    seq = seq.lower().replace('t','u')
    seq = clearing(seq)
    
    aSD = antiSD_Ecoli # using E. coli rRNA
    
    
    # find SD
    sd_pos, sp_len, sd = findSD( seq, atg_index, aSD)
    #sp_len = atg_index - (sd_pos+6)
    
    #print 'sd_pos=', sd_pos, ' sp_len = ', sp_len, 'sd seq = ', sd
    #print 'sd_pos=', sd_pos
    
    
    # triming a sequence
    [seq, sd_pos, atg_index] = trim(seq, sd_pos, atg_index)
    
    
    # marking RDS
    seq = markingRDS( seq, sd_pos )
    #print seq
    
    
    #print seq
    
    
    
    
    score = RBS_sj.SCORE( "xxx" )
    score.setPerl(True)
    
    sd = seq[ sd_pos: sd_pos + len(aSD) ]
    
    #print "SD=" + sd
    
    
    score = RBS_sj.SCORE()
    score.CALCULUS_METHOD = method
    score.setAll( seq, sd, aSD, sp_len, 37, start_codon, atg_index, stopcodon)
    score.setPerl(True)
    x = score.run() 
    
    #print sd
    

    pe = x[0] # exposure probability
    pc = x[1] # complex probability
    gibbs = x[2] # gibbs free energy (SD-aSD)
    spaceEffect = x[3] # spacer effect on translation initiation
    comment = x[4]
    start_codon_effect = x[5] # start codon efficiency
    sd_neg_eff = x[6] # too strong SD-aSD hybridization decrease translational efficiency
    translationEfficiency=x[7] # considering all the factors above
    stopCodonEffect=x[8]

    
    #print '< Pe, Pc=', pe, pc
    
    # in order to ignore spacer , start codon, stop codon .....
    #translationEfficiency = pc # * sd_neg_eff * spaceEffect
    
    return pe, pc, gibbs, translationEfficiency, sp_len, sd, x




    
    


if __name__=='__main__':
    
    
    print ('RBS Efficiency Calculator v1.0')

    print 'Test sequence'
    utr='CACTCATTAG GCACCCCAGG CTTTACACTT TATGCTTCCG GCTCGTATGT TGTGTGG AATTGTGAGCGGATAACAATTTCACACA'

    utr2="aaggag gaggggcgg"
    cds='atggtgagcaagggcgaggagctgttcaccggggtggtgcccatcctggtcgagctggacggcgacgtaaacggccacaagttcagcgtgtccggcgagggcgagggcgatgccacctacggcaagctgaccctgaagttcatctgcaccaccggcaagctgcccgtgccctggcccaccctcgtgaccaccctgacctacggcgtgcagtgcttcagccgctaccccgaccacatgaagcagcacgacttcttcaagtccgccatgcccgaaggctacgtccaggagcgcaccatcttcttcaaggacgacggcaactacaagacccgcgccgaggtgaagttcgagggcgacaccctggtgaaccgcatcgagctgaagggcatcgacttcaaggaggacggcaacatcctggggcacaagctggagtacaactacaacagccacaacgtctatatcatggccgacaagcagaagaacggcatcaaggtgaacttcaagatccgccacaacatcgaggacggcagcgtgcagctcgccgaccactaccagcagaacacccccatcggcgacggccccgtgctgctgcccgacaaccactacctgagcacccagtccgccctgagcaaagaccccaacgagaagcgcgatcacatggtcctgctggagttcgtgaccgccgccgggatcactctcggcatggacgagctgtacaagtaa'
    
    seq = 'CGAGCCTCTA'
    t_utr = (utr + seq + utr2).replace(' ','').strip()
    [pe, pc, gibbs, te, sp_len, sd, x] = CalculateRBSScore( t_utr, cds, 2)

    print 'Exposure probability=',pe
    print 'Complex probability=',pc
    print 'Translational efficiency=',te
    print 'Ribosome binding energy=',gibbs,'kcal/mol'
    print 'SD sequence=',sd
    print 'Spacer length=', sp_len

    
    
    
     
    



