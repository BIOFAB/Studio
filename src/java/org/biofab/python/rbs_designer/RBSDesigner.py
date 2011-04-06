from org.biofab.jython import RBSDesignerInterface

import RBScal
from RBScal import CalculateRBSScore
import os, math

class RBSDesigner(RBSDesignerInterface):

#        def __init__(self):



        def rbs_design(self, seq, start_codon_offset):

#                os.putenv('NUPACKHOME', '/opt/nupack')

                s = seq

                utr_seq = seq[0:(start_codon_offset + 1)]
                coding_seq = seq[start_codon_offset:len(seq)]

                [pe, pc, gibbs, te, sp_len, sd, x] = CalculateRBSScore(utr_seq, coding_seq)

                out = ""
                out += 'Exposure probability=' + str(pe) + "\n"
                out += 'Complex probability=' + str(pc) + "\n"
                out += 'Translational efficiency=' + str(te) + "\n"
                out += 'Ribosome binding energy=' + str(gibbs) + "kcal/mol\n"
                out += 'SD sequence=' + str(sd) + "\n"
                out += 'Spacer length=' + str(sp_len) + "\n"

                return out
