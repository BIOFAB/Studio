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

import random
import threading
import glob
import os
import copy
import math
import time
import sys
import COMMON    
import SDENERGY_EFFECT
import STOPCODONEFFECT
import sympy

#import nzmath.real
#import real


COMPILED_OR_NOT=True


class RESULT_HELIX:
    
    sequence = ''
    structure = []
    
    
    def __init__(self):
        self.sequence = ''
        self.structure = []
        
    def setSequence(self, seq):
        self.sequence = seq
        
    def getSequence(self):
        return self.sequence
    
    def addStructure( self, str_info, energy ):
        self.structure.append( [str_info, energy ] )
        
    def getStructureSize(self):
        return len(self.structure)
    
    def getStructureEnergy(self, index):
        return self.structure[index][1]
    
    def getHelixSize(self, structure_index):
        return len( self.structure[structure_index][0] )
    
    def getHelixEnergyByIndex(self, structure_index, helix_index):
        x = self.structure[structure_index][0]
        #print repr(x)
        y = x[helix_index]
        z = y[0]
        return z
    
    def getHelixPositionByIndex(self, structure_index, helix_index):
        return self.structure[structure_index][0][helix_index][1]
    
    def toString(self):
        
        
        r = ''
        r = r + 'Structure Total # = ' + str(len(self.structure))+ '\n'
        for i in range( self.getStructureSize() ):
            r = r + 'Index = '+str(i) + '\n'
            r = r + 'dG = ' + str( self.getStructureEnergy(i) )+ '\n'
            
            for j in range( self.getHelixSize(i) ):
                
                r = r + 'Helix E = ' + str( self.getHelixEnergyByIndex(i,j) ) + '\n'
                r = r + 'Helix bp = ' + str( self.getHelixPositionByIndex(i, j) )+ '\n'
        
        return r
            
class RESULT:
    
    sequence = None
    structure = []
    structure_energy = []
    save_seq = []
    confidence_scores = []
    averaged_confidence_score = -2
    result2 = RESULT_HELIX()
    
    #infoNT = [ helix_id, paired_or_not, energy, nearby_energy ]
        
    '''
    infoNT = [ helix_id, paired_or_not, energy, nearby_energy, paired_bp ] #1208
    '''
    
    HELIX_ID_INDEX=0
    PAIRING_INDEX=1
    ENERGY_INDEX=2
    NEARBY_ENERGY_INDEX=3
    PAIRED_BP_INDEX=4 #1208, to provide another paired base position 
    
    
    
    def setResultForInternalStructure(self, info):
        self.result2 = info
        
    def getHelixInformationForInternalStructure(self):
        return self.result2
    
    def getAveragedConfidenceScore(self):
        
        # BRS structure  confidence score .
        
        scores = self._getConfidenceScoreOfEachUpperNucleotide()
        
        #    % score 0.9  (, 0.9   pair or unpair ) .
        # , %    .
        
        
        #seq_len = self.getSequenceLength()
        
        threshold=0.8 # 80% of pairs are sustained.
        
        
        if len(scores)!=0:
        
            cnt = 0
            for s in scores:
                
                if s>=threshold:
                    cnt = cnt + 1
                    
            score = float(cnt)/float( len(scores) )
            
            self.averaged_confidence_score = score
        
        else:
            score = -1
            self.averaged_confidence_score = score
            
            
        return score
        
    
    def _getConfidenceScoreOfEachUpperNucleotide(self):
        
        structure_size = self.getStructureSize()
        seq_len = self.getSequenceLength()
        
        conf_score = []
        
        for nt in range( seq_len ):
            
            
            if self.isNucleotideUppercase(nt):
            
                tmp = {}
                
                
                
                for s in range(structure_size):
                    
                    pos = str(self.getPairedBpPosition(s,nt)).strip()
                    
                    if tmp.has_key(pos):
                        tmp[pos]=tmp[pos]+1
                    else:
                        tmp[pos]=1
                        
                    #print str(nt)+' ' + self.getNucleotideAt(nt) + '->' + pos + ' ' + self.getNucleotideAt( eval(pos) ) + ' = ' + str(tmp[pos])
                
                #      .
                mx = -1
                
                for x in tmp.keys():
    
                    if tmp[x]>mx:
                        mx = tmp[x]
                
                #print 'max case = ', mx
                
                score = float(mx)/float( structure_size )
                
                #print 'score = ',  score
                
                conf_score.append( score )
        
        # global variable .
        self.confidence_scores = conf_score
    
        return self.confidence_scores
    
    
    
    
    def __init__(self):
        
        self.sequence = ''
        self.structure = []
        self.structure_energy = []
        self.save_seq = []
    
    def __clearSequence(self, seq):
        
        seq = seq.replace( ' ','' )
        x = seq.split('\n')
        r = ''
        for i in x:
            r = r + i
        return r
    
    def setSequence(self, sequence):
        self.sequence = self.__clearSequence(sequence)
        
    def getStructureSize(self):
        '''
        Returns the number of predicted folds
        '''
        return len(self.structure)
    
    def getSequence(self):
        return self.sequence
    
    def getSequenceLength(self):
        '''
        returns the length of the sequence
        '''
        return len(self.sequence)
    
    def getEnergyOf(self, structure_index, nt_index):
        '''
        returns the engery of helix including any loops in which a nucleotide is involved.
        '''
        return self.structure[structure_index] [nt_index] [ self.ENERGY_INDEX ]
        
    def isNucleotidePaired(self, structure_index, nt_index):
        '''
        Returns True if the nucleotide is paired, otherwise False
        '''
        
        return self.structure[structure_index] [nt_index] [ self.PAIRING_INDEX ]
    
    def getEnergyWithLoopOf(self, structure_index, nt_index):
        
        h = self.structure[structure_index] [nt_index] [ self.ENERGY_INDEX ]
        l = self.structure[structure_index] [nt_index] [ self.NEARBY_ENERGY_INDEX][1]
        
        #print h,l 
        return h+l
    
    
    
    def getHelixIDof(self, structure_index, nt_index):
        return self.structure[structure_index] [nt_index] [ self.HELIX_ID_INDEX ]
        
    def getNucleotideAt(self, nt_index):
        return self.sequence[nt_index]
    
    def isNucleotideUppercase(self, nt_index):
        return self.sequence[nt_index].isupper()
    
    def getNearbyEnergy(self, structure_index, nt_index):
        '''
        returns loop energies around a helix. return value is a 'list'.
        '''
        
        return self.structure[structure_index] [nt_index] [ self.NEARBY_ENERGY_INDEX ]
    
    def getPairedBpPosition(self, structure_index,nt_index):
        return self.structure[structure_index] [nt_index] [ self.PAIRED_BP_INDEX ]
    
    
    #def addNucleotideInformation( self, structure_index, helix_id, paired_or_not, energy , nearby_energy):
    def addNucleotideInformation( self, structure_index, helix_id, paired_or_not, energy , nearby_energy, paired_bp): #1208
        
        if structure_index >= self.getStructureSize():
            self.structure.append( [] )
        
        #ntInfo = [helix_id, paired_or_not, energy, nearby_energy ]
        ntInfo = [helix_id, paired_or_not, energy, nearby_energy, paired_bp ] #1208
        
        
        
        self.structure[structure_index].append( ntInfo )
        #print 'RESULT: ' , structure_index, 'nt = ', len( self.structure[structure_index] )

        
    def setStructureEnergy(self, structure_index, structure_energy):
        
        if structure_index >= len(self.structure_energy):
            self.structure_energy.append( [ 0, 0 ] )
        
        self.structure_energy [ structure_index ][0] =  structure_energy 
    
    def setRBSEnergy(self, structure_index, rbs_energy):
        if structure_index >= len(self.structure_energy):
            self.structure_energy.append( [ 0, 0 ] )
        
        self.structure_energy [ structure_index ][1] =  rbs_energy
        
    
    def getStructureEnergy(self, structure_index):
        return self.structure_energy [ structure_index ][0]
    
    def getRBSEnergy(self, structure_index):
        return self.structure_energy [ structure_index ][1]
    
    
    def __analyzeData(self):

        nt_length = self.getSequenceLength()
        
        r = ''
        
        for x in range( len(self.structure) ):
            
            if len( self.structure[x] ) != nt_length:
                r = r + '\nStructure ' + str(x) + ' has ' + str(len(self.structure[x])) + ' [ '+str(nt_length) + ']' 
        
        if len(self.structure) != len(self.structure_energy):
            r = r + '\n You have '+str(len(self.structure))+' structures, but have only '+str(len(self.structure_energy))+' energy terms'
        return r.strip()
        
        
    def checkConsistency(self):
        '''
        Checks whether stored information is correct or not. Returns True if correct, otherwise, False.
        '''
        
        r = self.__analyzeData()
        
        if len(r)==0:
            return True
        else:
            return False
        
        
    def __repr__(self):

        '''
        Returns result information
        '''
        
        r = 'Sequence : ' + self.sequence + '\n'
        r = r + 'Consistency check : '
        
        x=self.__analyzeData()
        if len(x)==0:
            r = r + 'Correct'
        else:
            r = r + 'Incorrect\n'
            r = r + x
        
        return r
        
        
    def find_unpaired_portion(self):      
        for k in range(len(self.structure)):
            temp_seq = ''
            for l in range(len(self.structure[k])):
                if self.structure[k][l][1] == False:
                    temp_seq += self.sequence[l]
                else:
                    temp_seq += '_'
            self.save_seq.append (temp_seq)
        return self.save_seq
            
        

class SCORE:
    
    
    STORE_K_VALUE=False
    
    
    MIN_SD_LENGTH = 6  #   SD site . AAGGAG.      aSD, rRNA_SEQUENCE    .
    #aSD = 'CTCCTT' # used for calculating the hybridization energy b/w rRNA and SD
    aSD = ''
    sd = ''
    result = RESULT()
    helix_result = RESULT_HELIX()
    info_class = COMMON.BASIC_INFO()
    
    sequence = ''
    stopcodon = ''
    nt_probability = [ ]
    error = False
    score = 0.0
    temp = 37
    start_codon = ''
    atg_index = -1
    
    k_value = []
    
    CONST_METHOD = 2    # 0 - parining-based calculation, 1 - energy-based calculation
    CONST_PAIRING_BASED_METHOD = 0
    CONST_ENERGY_BASED_METHOD = 1
    CONST_PARING_AND_ENERGY = 2
    
    spacer_length = -1
    
    SIM_GENE_COPY_NUMBER = 100.0
    SIM_RNA_SYNTHESIS_RATE = 20.0  # /min
    SIM_RIBOSOMES_PER_RNA = 20.0  # polysome  
    #SIM_RIBOSOMES_PER_RNA = 1.0  # polysome   ( )
    SIM_FREE_RIBOSOME_NUMBER = 57000.0 # .
    SIM_RNA_HALF_LIFE = 2.0   # /min

    
    
    # mfold Gibbs free energy, kcal/mol
    CONST_R = 1.98722e-3 # Gas constant, kcal/(mol K)
    CONST_T = 273.15 + 37.0 # Absolute temperature (K)
    
    CONST_CELL_AQUEOUS_VOLUME = 7.0e-16 # litre
    #CONST_CELL_VOLUME = 1.0e-15 # ~ 1.0e-18
    CONST_CELL_VOLUME = 1.0e-18

    
    
    #        mRNA .
    SIM_mRNA_AMOUNT = -1
    
    default_filename=''
    
    perl_installed = False
    
    hybridizing_program=1
    precalculated_hybrid_energy = {}
    
    def __init__(self, default_id='00000'):
        
        #self.result = result_class
        self.sequence = ''
        self.nt_probability = []
        self.score = 0.0
        self.default_filename = default_id
        self.perl_installed = False
        
        '''
        if result_class == None:
            self.error = True
        else:
            self.__calculateScore()
        '''

    def setBasicInfo( self, info ):
        self.info_class = info
        
    def setPerl(self, flag):
        self.perl_installed = flag
    def setHybridizingProgram(self, program):
        self.hybridizing_program = program
    
    def setRNAamount(self, amount, ribomsomes_per_RNA, total_free_ribosomes):
        # mRNA    .
        self.SIM_FREE_RIBOSOME_NUMBER = total_free_ribosomes
        self.SIM_RIBOSOMES_PER_RNA = ribomsomes_per_RNA        
        self.SIM_mRNA_AMOUNT = amount
        
    def setRibosomeComplexCondition(self, gene_copy_number, RNA_synthesis_rate, RNA_half_life, ribomsomes_per_RNA, total_free_ribosomes):
        # ----------------------------------------------------
        
        #  ribosome complex       .
        self.SIM_GENE_COPY_NUMBER = gene_copy_number
        self.SIM_FREE_RIBOSOME_NUMBER = total_free_ribosomes
        self.SIM_RIBOSOMES_PER_RNA = ribomsomes_per_RNA
        self.SIM_RNA_SYNTHESIS_RATE = RNA_synthesis_rate
        self.SIM_RNA_HALF_LIFE = RNA_half_life
        
        # -------------------------------------------------------     
    
    def setPrecalculatedHybridEnergy(self, energy):
        self.precalculated_hybrid_energy = energy
        
    def setAll(self, sequence, SD, aSD, spacer_length, temp, start_codon, atg_index, stopcodon):
        
        self.sequence = sequence
        self.sd = SD
        self.aSD = aSD
        self.spacer_length = spacer_length
        self.temp = temp
        self.start_codon = start_codon
        self.atg_index = atg_index
        self.stopcodon = stopcodon
        
        '''
        print 'SEQ=', sequence
        print 'SD=', SD
        print 'aSD=',aSD
        print 'SP_LEN=', spacer_length
        print 'Temp=', temp
        '''
    
        
    def run(self):

        pe = -1
        pc = -1
        pr = -1
        se = -1
        start = self.getStartCodonEfficiency( self.start_codon )  # start codon efficiency
        sd_effect2 = -1
        
        # Exposure probability
        r = FOLD(  self.default_filename  )
        r.setAll( self.sequence , self.temp )
        r.setPerl( self.perl_installed )
        
        self.result = r.fold( )
        
        #if self.result == None:
        #    print 'None SCORE'
        
        
        #pe = self.__calculateRBSExposureProbabilityOld()
        pe = self.__calculateRBSExposureProbability()
        #pe = self.__calculateRBSExposureProbability2()
        
        # print'Pe=',pe
        # Hybrid energy:  SD-aSD
        
        gibbs = -1
        
        s_temp = str(self.temp)

        
        # SD    .
        # sd_len = 6
        # self.sd = self.sd[: sd_len]
        # self.aSD = self.aSD[ len(self.aSD) - sd_len :]
        
        # print self.sd, self.aSD
        
        # print 'run hybrid program'
        h = HYBRID( self.default_filename )
        h.setAll (self.sd, self.aSD, self.temp )
        h.setHybridizingProgram( self.hybridizing_program )
        h.setPerl( self.perl_installed )
        h.setPrecalculateEnergy( self.precalculated_hybrid_energy )
        
        
        
        
        
        gibbs = h.runHybridToGetEnergy()

        # Ribosome complex fraction
        if gibbs != COMMON.INF:  # 0 .
            [pc, pr] = self.__calculateRibosomeComplexFraction( pe, gibbs, self.temp )
            #print 'Pe, Pc=',pe, pc
        else:
            pc = -1
            pr = -1

        # spacer effect: 8, Max.
        se = self.__getSDandSpacerCoefficient( self.spacer_length )
        
        
        
        st = 'A: Exposure Probability = ' + str(pe) + '\n' + \
           'B: Ribosome complex fraction = ' + str(pc) + '\n' + \
           'C: SD-aSD Hybrid Energy = ' + str(gibbs) + '\n' + \
           'D: Spacer Effect (Max: 1) = ' + str( se ) + '\n' + \
           'TOTAL SCORE (B*D) = ' + str(pc*se)
        st = 'XXXXXXXXXXXX'
        # SD hybrid     .
        
        sd_effect2 = SDENERGY_EFFECT.getSDEnergyEffect( gibbs )
        
        # st   .
        
        stopcodonEffect = STOPCODONEFFECT.calculateStopCodonEffect( self.stopcodon)
        
        #  Translational Efficiency  .
        
        #translationEfficiency = pc * se * sd_effect2 * start * stopcodonEffect
        translationEfficiency = self.Pc2TE(pc ) * se * start * stopcodonEffect
        
        
        # calculate the internal structure effect
       
        
        '''
        gibbs_set, internal_sd_count = INTERNAL_STRUCTURE_EFFECT.findSDNumberInCDS( \
            self.sequence, self.atg_index, self.aSD, self.temp )
        '''
        # .  .
        gibbs_set = []
        internal_sd_count = 0.0
        
        
        # ================================================
        
        return [ pe, pc, gibbs, se, st, start, sd_effect2 , translationEfficiency, stopcodonEffect, internal_sd_count, pr, self.spacer_length ]
    
    def Pc2TE(self, pc):
        
        # Pc Exp  
        #   . 
        #   .
        # 
        
        
        te = pc
        
        '''
        # y = a + bx^2
        a = -0.4447
        b = -0.021
        
        sx =a + b * math.log10(pc) ** 2.0
        te = 10.0 ** sx
        '''
        
        '''
        # y =a*bx^3
        a = -0.5516
        b = 0.00293
        
        sx = a + b*math.log10(pc) ** 3.0
        te = 10.0 ** sx
        '''
        
        
        return te
    
        
    def convertToMolarity(self, number):
        
        CONST_MOL = 6.02e23
        CONST_VOL = self.CONST_CELL_VOLUME 
        #CONST_CELL_VOLUME = 1.0e-15 # ~ 1.0e-18
        #CONST_CELL_AQUEOUS_VOLUME = 7.0e-16 # litre
        n = float(number) / (CONST_MOL * CONST_VOL)
        return n
        
    def __calculateRibosomeComplexFraction(self, pe, gibbs, temp):
        
        '''
        if pe<=1e-13:
            #   python     .
            #    TE=0  .
            return [0.0, 1.0]
        '''
        
        
        s_C1 = sympy.Symbol('s_C1')
        s_C2 = sympy.Symbol('s_C2')
        s_C3 = sympy.Symbol('s_C3')
        s_C4 = sympy.Symbol('s_C4')
        
        s_pe = sympy.Symbol('s_pe')
        s_K = sympy.Symbol('s_K')
        s_Mt = sympy.Symbol('s_Mt')
        s_Rt = sympy.Symbol('s_Rt')
        s_n = sympy.Symbol('s_n')
        
        s_Call = sympy.Symbol('s_Call')
        
        n_len = 50
        
        # =================================
        #   .
        
        #   transcript    .
        a = self.SIM_GENE_COPY_NUMBER # plasmid copy number
        s = self.SIM_RNA_SYNTHESIS_RATE # /min , luxR mRNA synthesis rate
        d=math.log(2.0)/ self.SIM_RNA_HALF_LIFE # mRNA decay, half-life=2min
        Mt=a*s/d # produced luxR mRNAs
        
        
        #v = self.CONST_CELL_VOLUME
        #v = self.CONST_CELL_AQUEOUS_VOLUME
        
        #  transcript       .
        if self.SIM_mRNA_AMOUNT > 0:
            COMMON.log("mRNA   = "+str(self.SIM_mRNA_AMOUNT))
            Mt = self.SIM_mRNA_AMOUNT
        
        #mt=Mt*pe # open-mRNAs
        m= self.SIM_RIBOSOMES_PER_RNA  # ribosomes per mRNA
        n=1.0 # no meaning
        Rt= float( self.SIM_FREE_RIBOSOME_NUMBER ) / float( m ) # free ribosomes. polysome  polysome 1 ribosome .
        
        # =============================================================
        # Mt = Mt 
        # Rt = Rt  #* float(m) # no polysome
        # =============================================================
        
        #print Mt, Rt
        
        # ==================================
        
        
        # Mt, Rt  M  .
        Mt = self.convertToMolarity( Mt )  # polysome 
        Rt = self.convertToMolarity( Rt )
        
        #print Mt, Rt
        
        # ==================================
        
        #CONST_R = 1.98722e-3 # Gas constant, kcal/(mol K)
        CONST_R = 1.9858775e-3 # Gas constant, kcal/(mol K) : http://en.wikipedia.org/wiki/Gas_constant
        CONST_T = 273.15 + temp # Absolute temperature (K)
        
        #print 'GIBBS = ', gibbs
        
        K=math.exp( - gibbs / (CONST_R* CONST_T) ) # eq constant
        
        #s_K = sympy.Symbol('s_K')
        #s_pe = sympy.Symbol('s_pe')

        s_Mt = sympy.N( Mt , n_len)
        s_Rt = sympy.N( Rt, n_len)
        s_n = sympy.N(n, n_len)
    
        s_pe = sympy.N(pe, n_len)
        s_K = sympy.N(K, n_len)
        
        
        s_X1 = sympy.Symbol('s_X1')
        s_X2 = sympy.Symbol('s_X2')
        s_X3 = sympy.Symbol('s_X3')
        
        s_X1 = sympy.N(1.0,n_len)
        s_X2 = sympy.N(s_K*s_pe*s_n*s_Mt,n_len)
        s_X3 = sympy.N(s_K*s_pe*s_Rt, n_len)
        
        s_C1 = sympy.N(s_X1 + s_X2 + s_X3, n_len)
        s_C2 = sympy.N(4.0 * s_n*s_K**2*s_pe**2*s_Mt*s_Rt , n_len)
        s_C3 = sympy.N(2.0 * s_n*s_K*s_pe, n_len)
        
        #mRNA-ribosome complex
        
        s_C4 = sympy.N ( (s_C1 - sympy.sqrt( s_C1 ** 2.0 - s_C2 ) )/s_C3, n_len )

        s_Call = sympy.N( s_C4/s_Mt, n_len)        
        
        
        #C=(1.0 + K*pe*n*Mt + K*pe*Rt) - \
        #           math.sqrt( \
        #                   (1.0 + K*pe*n*Mt + K*pe*Rt)**2.0 \
        #                                 - 4.0*n*K**2*pe**2*Mt*Rt )
        #C=C/(2.0*n*K*pe)
        
        
        f=s_Call  # RIbosome-mRNA complex 
        
        rf = 1.0000 - s_Call # fraction of ribosome
        
        
        if f + rf > 1.0 or f<0 or rf<0:
            #f = 0.0
            #rf = 0.0
            
            
            print ('Exceeding limits: '. f, rf )
            
            
            
        #  
        # ki : translation initiation
        # kt : translation
        '''
        kt = 1.0  # about 1 protein/min
        ki = 1.0
        
        kf = 1
        
        Q = kf/(kr+ki) * pe
        #Q = K * pe
        N = 1.0 + ki/kt
        C = ( N*Q*Mt + Q*Rt*1.0)
        D = math.sqrt(  (N*Q*Mt + Q*Rt + 1.0)**2.0 - 4.0 * N *Rt *Mt*Q**2   )
        C1 = C - D
        C1 = C1 / (2.0*N*Q)
        C2 = C + D
        C2 = C2 / (2.0*N*Q)
        
        f = C2/ Mt
        rf = C2/Rt
        '''
        
        '''
        print '-=-----------------------------'
        print 'copy num = ', a
        print 'RNA syn = ', s
        print 'half life = ', self.SIM_RNA_HALF_LIFE
        print 'Free ribosome = ', self.SIM_FREE_RIBOSOME_NUMBER
        print 'pol;ysome = ', m
        print 'Total  mRNA = ', Mt
        print 'Exposure P = ', pe
        print 'Complex abs. number = ', C
        print 'Fraction of mRNA-ribosome complex = ', f
        print 'Fraction of complex/ribosome ', rf
        '''
        
        return [f, rf]

    def __getSDandSpacerCoefficient(self, spacer_length):
        
        #spacer_length = spacer_length + 1
        #  AGGAGG SD 
        # Ringui..  AGGA SD .
        # 
        
        '''
        SpaceEffectFactor={ '0': 0.046926326,
                           '1':0.051618958,
                           '2':0.02889381,
                           '3':0.103263523,
                           '4':0.471521653,
                           '5':0.697921281,
                           '6':0.771125091,
                           '7':1.0,
                           '8': 0.951435442 ,
                           '9':0.77884062,
                           '10':0.624064672,
                           '11':0.463624744,
                           '12':0.337752346,
                           '13':0.131393712,
                           '14':0.096668231,
                           '15':0.06194275,
                           '16':0.079774754,
                           '17':0.076020648,
                           '18':0.072266542,
                           '19':0.056311591,
                           '20':0.029704364,
                           '21':0.003097137
                           }
        
        #data form average of literature data(Ringquist, Vellanoweth)
        
        
        x = str(spacer_length).strip()
        ret = 0.0
        
        if not SpaceEffectFactor.has_key(x):
            COMMON.log("Out of range, spacer length = "+x + " => 0 ")
            ret = 0.0
        else:
            ret = SpaceEffectFactor[ x ]
        '''
            
        # gaussian curve .
        '''
        Amplitude = 1.024
        Mean = 7.762
        SD=2.966

        ret =Amplitude*math.exp(-0.5*(( spacer_length - Mean)/SD) ** 2)
        '''
        
        Amplitude = 1.026
        center = 7.436
        width = 0.3601
        
        # if spacer length is zero, it causes error
        # so, plus 3 to all constants
        if spacer_length <= 0:
            
            
            COMMON.log("THe spacer length is too short = " + str(spacer_length) )
            
            cont = abs(spacer_length)+1
            spacer_length = cont
            
            center = center + cont
            
            Amplitude = Amplitude 
            width = width
            
            COMMON.log("SPACER LENGTH is OUT OF RANGE : "+ str(spacer_length) )
            COMMON.log("ADD to the center CONSTANT : +"+str(cont))
        
        a = math.log( float(spacer_length) /center) 
        b = (a/width)** 2
        c = -0.5*b
        ret = Amplitude * math.exp( c )

        if ret>1.0:
            ret=1.0
        
        #ret = Amplitude * math.exp( -0.5 * ( math.log(  float(spacer_length) / center ) / width ) ** 2 )
        
            
        return ret
    
    def getStartCodonEfficiency(self, codon):
        
        codon=codon.upper().replace('U','T')
        
        if codon == 'ATG':
            return 1.0
        elif codon=='TTG':
            return 0.28
        elif codon =='GTG':
            return 0.31
        else:
            raise Exception("Unknown start codon: " + codon)
        
    def isNucleotideInUppercase(self, nt_index):
        return self.result.isNucleotideUppercase( nt_index )
        
        
    def getNucleotideAt(self, nt_index):
        '''
        returns a nucletotide at position 'nt_index'
        '''
        return self.result.getNucleotideAt(nt_index)
        
        
    def getSequenceLength(self):
        '''
        returns the length of the input sequence.
        '''
        return self.result.getSequenceLength()
    
    def getSequence(self):
        '''
        returns the input sequence.
        '''
        return self.result.getSequence()
    
    def __initialiseProbabilityVariable(self):
        
        self.probability = []
        for index in range( self.result.getSequenceLength() ):
            self.probability.append( 0.0 )
        
    def __calculateStructureEnergies(self):
        
        
        k = 1.0
        
        for i in range( self.result.getStructureSize() ):
            
            if self.STORE_K_VALUE:
                k = k + self.k_value[i]
            else:
                k = k + self.__getK( self.result.getStructureEnergy(i) )
        
        return k
    

    
    
    def __calculateStructureProbability(self):
        
        base = self.__calculateStructureEnergies()
        # the last index represents 'UNFOLDED' RNA.
        
        p = []
        
        for i in range( self.result.getStructureSize() ):
            k=0
            
            if self.STORE_K_VALUE:
                k = self.k_value[i]
            else:
                k = self.__getK( self.result.getStructureEnergy(i) )
                
            p.append( k/base )
            
        # the last, unfoled RNA.
        p.append( 1.0/base )
        
        return p
        
    def __calculateStructureProbability2(self):
        

        #base_dG = 1.0
        
        #for i in range( self.result.getStructureSize() ):
        #    base_dG = base_dG * self.result.getStructureEnergy(i)
        
        
        p = []
        
        for i in range( self.result.getStructureSize() ):
            
            p_tmp = 0.0
            
            i_dG = - self.result.getStructureEnergy(i) / (self.CONST_R * self.CONST_T)
            
            for j in range( self.result.getStructureSize() ):
                j_dG = - self.result.getStructureEnergy(j)/ (self.CONST_R * self.CONST_T)
                
                p_tmp = p_tmp + math.exp( ( j_dG - i_dG) )

            # calculate when j-dG=0
            # 0    unfolded RNA  dG=0 .
            #  K 1 .
            #  unfolded mRNA   ...
            #      .
            # --------------------------------------------------------------
            # p_tmp = p_tmp + math.exp( (  0.0 -  i_dG)  )
            # --------------------------------------------------------------
            
            p_tmp = 1.0 / p_tmp
            
            
            #print 'dG = ', 
            #print 'Base dG = ', base_dG
            
            p.append( p_tmp )
            
        # the last, unfoled RNA.
        # if dG is too low, there seems to be no unfolded RNA structure.
        # Therefore, the probability of unfolded RNA is assumed to be zero.
        
        #if abs(base_dG) > 500:
        #    p.append( 0 )
        #else:
        #p.append( 1.0 / self.__getK( base_dG ) )
        p.append( 0.0 ) # <- the probability of unfolded RNA. We ignore it.

        
        return p
    
    
    def _calculateKOnce(self):
        # calculate all K in one time save store it.
        self.k_value = []
        for i in range( self.result.getStructureSize() ):
            k = self.__getK( self.result.getStructureEnergy(i) )
            self.k_value.append( k )
    
        
    def _calculateScore_EnergyBased(self):
        
        '''
        Calculate the probability of nucleotides to be exposed.
        '''
        
        
        
        '''
        P(structure i) = Ki/(1+K1+K2+....+Kn)
        P(unfolded RNA)= 1/(1+K1+K2+....+Kn)
        '''
        
        
        
        self.__initialiseProbabilityVariable()
        str_p = None
        v=self.__getMultipliedValueOfGibbsFreeEnergiesWithRandT()
        
        #print "...", v
        if  abs(v) >= 700:
            #COMMON.log( "The value is too large. Use a slow method (energy): "+str(v))
            str_p = self.__calculateStructureProbability2()
        else:
            #COMMON.log( "The value is proper. Use a fast method")
            str_p = self.__calculateStructureProbability()
        
        # str_p [-1] means the probability of 'unfolded RNA'
        
        
        
        
        nt_p = []
        
        
        score = str_p[-1] # the probability of unfolded structure.
        
        
        for s_index in range( self.result.getStructureSize() ):
            
            p_cur_str = str_p [ s_index ]
            
            dG_rbs = self.result.getRBSEnergy( s_index )
            p_cur_rbs_unfolded = 1.0 / ( 1.0 + self.__getK( dG_rbs ) )
            
            p_rbs_score = p_cur_str * p_cur_rbs_unfolded
            
            score = score + p_rbs_score
           
            '''
            print 'Str P = ', p_cur_str
            print 'RBS dG = ', dG_rbs
            print 'RBS unfolded p =', p_cur_rbs_unfolded
            print 'RBS p = ', p_rbs_score
            '''
            
       
        return score



    def __calculateScore_PairingBased(self):
        
        '''
        Calculate the probability of nucleotides to be exposed.
        '''
        
        
        
        '''
        P(structure i) = Ki/(1+K1+K2+....+Kn)
        P(unfolded RNA)= 1/(1+K1+K2+....+Kn)
        '''
        
        
        
        self.__initialiseProbabilityVariable()


        str_p = None
        v=self.__getMultipliedValueOfGibbsFreeEnergiesWithRandT()
        
        #print "...", v
        if  abs(v) >= 700:
            #COMMON.log( "The value is too large. Use a slow method: Paring-based : " +str(v))
            str_p = self.__calculateStructureProbability2()
        else:
            #COMMON.log( "The value is proper. Use a fast method")
            str_p = self.__calculateStructureProbability()
        
        # str_p [-1] means the probability of 'unfolded RNA'
        
        
        

        
        nt_p = []
        
        for s_index in range( self.result.getStructureSize() ):
             
            helix_counter = self.__getNucleotideNumbersInAHelix( s_index )
            
            
            for nt_index in range( self.result.getSequenceLength() ):
                
                if s_index == 0:
                    nt_p.append( str_p[-1] ) # the probability to be unfoled
                
                if not self.result.isNucleotidePaired( s_index, nt_index ):
                    nt_p [ nt_index ] = nt_p [nt_index] + str_p[s_index] * 1.0
                else:
                    '''
                    Here, only the stacking energies are considered for calculating the nt probabilities to be exposed.
                    To consider nearby loops (bulge, internal, or external loops), replace the line 'p=....' to the following long line (just below the line).
                    '''
                    
                    
                    h_id = str( self.result.getHelixIDof( s_index, nt_index ) )
                    energy = self.result.getEnergyOf( s_index, nt_index )
                    #energy = energy + self.__arraySum( self.result.getNearbyEnergy(s_index, nt_index))
                  
                    K = self.__getK(  energy )
                    
                    p = (1.0 / ( 1.0 + K )) ** (1.0/ float( helix_counter[ h_id ] ) )
                    
                    nt_p[nt_index]=nt_p[nt_index]+str_p[s_index]* (p)
                    
        
        self.nt_probability=nt_p
    

        # from the accessiblities of each nucleotide, the probability of RBS region to be exposed can be derived.
        score = 1.0
        for index in range( self.getSequenceLength() ):
            if self.isNucleotideInUppercase(index):
                score *= self.getAccessibilityProbability(index)
        
        return score
        
        
    def __calculateScore(self):
        
        #if self.STORE_K_VALUE:
        #    self._calculateKOnce()
        
        
        if self.CONST_METHOD == self.CONST_ENERGY_BASED_METHOD:
            self.score = self._calculateScore_EnergyBased()
        elif self.CONST_METHOD == self.CONST_PAIRING_BASED_METHOD:
            self.score = self.__calculateScore_PairingBased()
        elif self.CONST_METHOD == self.CONST_PARING_AND_ENERGY:
            self.score = self.__calculateScore_PairingAndEnergyBasedMethod()
        else:
            print "Unknown method for RBS exposure calculation"
            sys.exit(1)
            
    def __getMultipliedValueOfGibbsFreeEnergiesWithRandT(self):
        
        dG = 1.0
        for i in range( self.result.getStructureSize()):
            dG = dG * self.result.getStructureEnergy(i)
        return - dG/( self.CONST_R * self.CONST_T)

    
    
    
    def __calculateRBSExposureProbability(self):
        # Pe, exposure probability

        '''
        Calculate the probability of nucleotides to be exposed.
 
        P(structure i) = Ki/(1+K1+K2+....+Kn)
        P(unfolded RNA)= 1/(1+K1+K2+....+Kn)
        '''
        
        
        str_p = None
        self.__initialiseProbabilityVariable()
        
        # if the number of predicted structures exceed 20, it shoud divide all the calculation into small parts thus increases computational load.
        # if not, to reduce the burden, it uses the original method.
        
        v=self.__getMultipliedValueOfGibbsFreeEnergiesWithRandT()
        
        #print "...", v
        if  abs(v) >= 700:
            #COMMON.log( "The value is too large. Use a slow method (paring+energy) : " +str(v))
            str_p = self.__calculateStructureProbability2()
        else:
            #COMMON.log( "The value is proper. Use a fast method")
            str_p = self.__calculateStructureProbability()
        
        # str_p [-1] means the probability of 'unfolded RNA'
        score = str_p[-1] # unfolding  
        pe = 0.0
        sum_str_p = 0.0
        
        
        helix_ID = -1
        
        ####
        #### NEW_HELIX_METHOD helix    .
        ####           False    nt  .
        ####           True  RBS  helix   helix    .   .
        
        
        NEW_HELIX_METHOD = True
        
        
       
        # RBS    .
        #   nt  .
        # =====================================================================================
        # calculate exposure probability
        
        
        


        
        '''
        #print str_p
        for s_index in range(self.result.getStructureSize() ):
            
            RBSenergy = self.result.getRBSEnergy(s_index)
            K_rna = self.__getK( RBSenergy )
            
            s_pe = 1.0 / (1.0 + K_rna )
            
            pe = pe + str_p[s_index] * s_pe
            
            #print RBSenergy, '==>', s_pe, K_rna
            
        #print ' --> pe = ', pe
        score = pe
        # =========================================================================================
        '''
        
        
        # if want to consider only one structure with the minimum energy
        # use s_index=0 and do not use str_p[] for score
        
        
        ##======================================================================================
        
        for s_index in range( self.result.getStructureSize() ):
             
            helix_counter = self.__getNucleotideNumbersInAHelix( s_index )
            
            calculated_helix_id={}            
            
            s_score = 1.0 # structure s_index    unfolding   .
            
            '''
            sum_str_p = sum_str_p + str_p[s_index]
            if sum_str_p>=1.0:
                # mRNA str prob   1.0 .
                #    .
                print '>>>>', s_index, '/', self.result.getStructureSize()
                
                break
            '''
            
            
            for nt_index in range( self.result.getSequenceLength() ):
                
                
                if self.isNucleotideInUppercase(nt_index): # .    .
                    
                    #  nucleotide    .
                
                    if not self.result.isNucleotidePaired( s_index, nt_index ):
                        # inside a free loop
                        s_score = s_score * 1.0 
                        helix_ID = -1
                        
                    else:
                        # stem nucleotide  . stem dG    .
                        #                       Here, only the stacking energies are considered for calculating the nt probabilities to be exposed.
                        # To consider nearby loops (bulge, internal, or external loops), replace the line 'p=....' to the following long line (just below the line).
                        
                        h_id = self.result.getHelixIDof( s_index, nt_index ) 
                        paired_nt = self.result.getPairedBpPosition( s_index, nt_index )
                        
                        
                        if NEW_HELIX_METHOD:
                            # consider nucleotides in a same helix as one
                            
                            # only for printing................
                            # energy <- sum of stack energies in a helix, not including an internal loop energy
                            #energy = self.result.getEnergyOf( s_index, nt_index )
                            #energy = self.result.getEnergyWithLoopOf( s_index, nt_index )
                            
                            
                            helix_len = helix_counter[ str(h_id) ]
                            #print 'str_iondex=', s_index, 'ID=',h_id,'prev id=', helix_ID,' nt_index=', nt_index, 'paired_index=', paired_nt, 'dG=', energy,'helix len=', helix_len
                            # .....................................
                            
                            #print energy

                            if not str(h_id) in calculated_helix_id.keys():
                                #print 'not calculated nt_index'
                                
                                # -------------------------------------------------
                                #    ,
                                ## helix stack  2 .
                                
                                calculated_helix_id[ str(h_id) ] = ''
                                
                                ## -------------------------------------------------------
                                
                                
                                
                                if h_id <> helix_ID:
                                    
                                    helix_ID = h_id 
                                    
                                    
                                    #energy = self.result.getEnergyOf( s_index, nt_index )
                                    energy = self.result.getEnergyWithLoopOf( s_index, nt_index )
                                    
                                    
                                    #energy = energy + self.__arraySum( self.result.getNearbyEnergy(s_index, nt_index))
                                    K = self.__getK(  energy )
                                    p = (1.0 / ( 1.0 + K )) #  ** (1.0/ float( helix_counter[ h_id ] ) )
                                    s_score = s_score * p 
                                else:                                    
                                    pass
                            else:
                                #print 'already calculated nt_index'
                                pass

                            """
                            if h_id <> helix_ID:
                                print 'different helix id'
                                helix_ID = h_id 
                                energy = self.result.getEnergyOf( s_index, nt_index )
                                #energy = energy + self.__arraySum( self.result.getNearbyEnergy(s_index, nt_index))
                                K = self.__getK(  energy )
                                p = (1.0 / ( 1.0 + K )) #  **  (1.0/ float( helix_counter[ h_id ] ) )
                                s_score = s_score * p 
                            else:
                                print 'skip helix id'
                                pass
                            """
                            
                            
                        else:
                                helix_ID = h_id 
                                energy = self.result.getEnergyOf( s_index, nt_index )
                                K = self.__getK(  energy )
                                p = (1.0 / ( 1.0 + K )) ** (1.0/ float( helix_counter[ h_id ] ) )
                                s_score = s_score * p 
                            
            
                            
            
            score = score + str_p[s_index] * s_score
            ## ========================================================================
            
        
        return score        

    def __calculateRBSExposureProbability2(self):
        
        # Pe, exposure probability

        '''
        Calculate the probability of nucleotides to be exposed.
 
        P(structure i) = Ki/(1+K1+K2+....+Kn)
        P(unfolded RNA)= 1/(1+K1+K2+....+Kn)
        '''
        
        
        str_p = None
        self.__initialiseProbabilityVariable()
        
        # if the number of predicted structures exceed 20, it shoud divide all the calculation into small parts thus increases computational load.
        # if not, to reduce the burden, it uses the original method.
        
        v=self.__getMultipliedValueOfGibbsFreeEnergiesWithRandT()
        
        #print "...", v
        if  abs(v) >= 700:
            #COMMON.log( "The value is too large. Use a slow method (paring+energy) : " +str(v))
            str_p = self.__calculateStructureProbability2()
        else:
            #COMMON.log( "The value is proper. Use a fast method")
            str_p = self.__calculateStructureProbability()
        
        # str_p [-1] means the probability of 'unfolded RNA'
        score = str_p[-1] # unfolding  
        
        pe = 0.0
        score = 0.0
        
        for s_index in range(self.result.getStructureSize() ):
            
            RBSenergy = self.result.getEnergyWithLoopOf(s_index)
            K_rna = self.__getK( RBSenergy )
            
            s_pe = 1.0 / (1.0 + K_rna )
            
            pe = pe + str_p[s_index] * s_pe
            
            print RBSenergy, '==>', s_pe, K_rna
            
        #print ' --> pe = ', pe
        score = pe
        
        
        return score        
    
            
    def __calculateRBSExposureProbabilityOld(self):
    

        '''
        Calculate the probability of nucleotides to be exposed.
        '''
        
        
        
        '''
        P(structure i) = Ki/(1+K1+K2+....+Kn)
        P(unfolded RNA)= 1/(1+K1+K2+....+Kn)
        '''
        
        
        
        self.__initialiseProbabilityVariable()
        #str_p = self.__calculateStructureProbability()
        
        
        # if the number of predicted structures exceed 20, it shoud divide all the calculation into small parts thus increases computational load.
        # if not, to reduce the burden, it uses the original method.
        str_p = None
        v=self.__getMultipliedValueOfGibbsFreeEnergiesWithRandT()
        
        #print "...", v
        if  abs(v) >= 700:
            #COMMON.log( "The value is too large. Use a slow method (paring+energy) : " +str(v))
            str_p = self.__calculateStructureProbability2()
        else:
            #COMMON.log( "The value is proper. Use a fast method")
            str_p = self.__calculateStructureProbability()
        
        # str_p [-1] means the probability of 'unfolded RNA'
        
        
        
        
        
        
        
        score = str_p[-1] # unfolding  
        
        for s_index in range( self.result.getStructureSize() ):
             
            helix_counter = self.__getNucleotideNumbersInAHelix( s_index )
            
            
            s_score = 1.0 # structure s_index    unfolding   .
            
            
            for nt_index in range( self.result.getSequenceLength() ):
                
                
                if self.isNucleotideInUppercase(nt_index): # .    .
                    #  nucleotide    .
                
                    if not self.result.isNucleotidePaired( s_index, nt_index ):
                        s_score = s_score * 1.0 
                    else:
                        # stem nucleotide  . stem dG    .
                        '''
                        Here, only the stacking energies are considered for calculating the nt probabilities to be exposed.
                        To consider nearby loops (bulge, internal, or external loops), replace the line 'p=....' to the following long line (just below the line).
                        '''
                        
                        
                        h_id = str( self.result.getHelixIDof( s_index, nt_index ) )
                        energy = self.result.getEnergyOf( s_index, nt_index )
                        #energy = energy + self.__arraySum( self.result.getNearbyEnergy(s_index, nt_index))
                      
                        K = self.__getK(  energy )
                        
                        p = (1.0 / ( 1.0 + K )) ** (1.0/ float( helix_counter[ h_id ] ) )
                        
                        s_score = s_score * p 
            
            score = score + str_p[s_index] * s_score
        
        return score        
        
    def __arraySum(self, array):
        
        t = 0.0
        for x in array:
            t = t + x
            
        return t
        
    def __getNucleotideNumbersInAHelix(self, structure_index):
        
        helix={}
        for nt_index in range( self.result.getSequenceLength() ):
            helix_id = self.result.getHelixIDof( structure_index, nt_index )
            
            helix_id_str = str(helix_id)
            
            if not helix.has_key( helix_id_str ):
                helix[helix_id_str]=0
                
            helix[helix_id_str]=helix[helix_id_str]+1
            
        return helix
            
    
    def __getK(self, gibbs_free_energy ):
        '''
        Convert Gibbs free energy to equilibrium constant
        '''
        
        # dG = - R*T*lnK
        
        x = - gibbs_free_energy / (self.CONST_R * self.CONST_T)
        #print gibbs_free_energy
        #print self.CONST_R
        #print self.CONST_T
        #print ' -> ', x
        #print x
        
        return math.exp( x )
        
    
    def __getSequenceExposureScore(self):
        '''
        returns the score
        '''
        
        if self.error or self.result == None:
            return -1
        else:
            #try:
            self.__calculateScore()
            #except:
            #   self.score = -1
            #       COMMON.log ('****** Error while calculating scores in SCORE class' )
            
            return self.score
           
            
            
    
class HYBRID(threading.Thread):
    
    '''
    calculates the gibbs free energy of short two different RNA sequences.
    '''
    
    CONST_mFOLD = 1
    CONST_RNACoFOLD=2
    
    sequence1 = None
    sequence2 = None
    seqlen1 = None
    seqlen2 = None
    ATGPos = None
    RBSPos = None
    
    perl_installed = False
    
    id = None
    sequence_file = None
    over = False
    
    temp = 37
    
    program = CONST_mFOLD  # 1 mfold. 2 RNAcofold
    precalculated_energy = {}
    
    def __init__(self, default_id='00000'):
        threading.Thread.__init__(self)
        
        self.sequence1 = ''
        self.sequence2 = ''
        self.id = default_id + '_' + str(random.randint(0, 100000))+'h'
        self.sequence_file1 = self.id + '1.seq'
        self.sequence_file2 = self.id + '2.seq'
        self.over = False
        self.perl_installed = False
    
    def setPerl( self, flag ):
        self.perl_installed = flag
        
    def setAll(self, seq1, seq2, temp):
        self.sequence1 = seq1
        self.sequence2 = seq2
        self.temp = temp
    
    def setPrecalculateEnergy(self, energy):
        self.precalculated_energy = energy

    def setSequences2(self, ATGPos, RBSStartPos, seq1, seq2):

        self.ATGPos = ATGPos
        self.RBSPos = RBSStartPos
        
        self.sequence1 = seq1
        self.sequence2 = seq2
        
        self.seqlen1 = len(seq1)
        self.seqlen2 = len(seq2)

    def runHybridToGetEnergy(self):
        
        # if precalculated energy exists
        # generate an ID
        st_temp = str(self.temp).strip()
        pid = ''
        if self.sequence1 < self.sequence2:
            pid = self.sequence1+'_'+self.sequence2
        else:
            pid = self.sequence2+'_'+self.sequence1
        pid = pid.strip().upper().replace('U','T')
        
        
        if self.precalculated_energy.has_key(st_temp):
            tx = self.precalculated_energy[st_temp]
            #
            if tx.has_key(pid):
                #print pid, tx[pid]
                return tx[pid]
            #else:
            #    print 'Nope'
        # if there is no precalculated energy,
        # do the following codes
        
        gibbs = COMMON.INF
        if self.program == self.CONST_mFOLD :
            gibbs = self.runmfold()
        elif self.program ==  self.CONST_RNACoFOLD:
            gibbs = self.runRNAcofold()
        else:
            print 'Unknown RNA hybridizing Program = ', self.program
            sys.exit(1)
        
        
        # save the hybridization result
        if not self.precalculated_energy.has_key(COMMON.PRECALCULATED_ENERGY_UPPER_LIMIT_STR):
            self.precalculated_energy[COMMON.PRECALCULATED_ENERGY_UPPER_LIMIT_STR]=0
        
        if self.precalculated_energy[COMMON.PRECALCULATED_ENERGY_UPPER_LIMIT_STR]<COMMON.PRECALCULATED_ENERGY_UPPER_LIMIT:
            if not self.precalculated_energy.has_key(st_temp):
                dx = {}
                self.precalculated_energy[st_temp]=dx
                
            di = self.precalculated_energy[st_temp]
            di[ pid ] = gibbs
            
            self.precalculated_energy[COMMON.PRECALCULATED_ENERGY_UPPER_LIMIT_STR] = \
                self.precalculated_energy[COMMON.PRECALCULATED_ENERGY_UPPER_LIMIT_STR] + 1
            
        return gibbs

    def runmfold(self):
        
        self.__removePreviousFiles()
        
        self.sequence1 = self.__clearSequence(self.sequence1)  # make a sequence pretty
        #print self.sequence1
        self.sequence2 = self.__clearSequence(self.sequence2)  # make a sequence pretty
        #print self.sequence2
        
        
        self.__saveSequences(self.sequence1, self.sequence_file1) # save the sequence into a file
        self.__saveSequences(self.sequence2, self.sequence_file2) # save the sequence into a file
        
        self.__execute() # run the mfold

        
        x = self.__parseResult()
        #x = self.__parseResult2() #to obtain the spacing between ATG AND SD
        
        # if x (dG) is equal to zero. there might be an error.
        
        self.__removePreviousFiles()
        
        #print 'SD. ', self.sequence1, ' : ', self.sequence2, ' -> ', x
        return x
        
    def runRNAcofold(self):
        
        self.__removeResultFilesWithCondition( self.id + '*.fa' )
        self.__removeResultFilesWithCondition( self.id + '*.out' )
        
        
        self.__saveSequenceFile4Cofold( self.id + '.fa' , self.sequence1, self.sequence2 )
        
        self.__executeCofold()
        
        time.sleep(1)
        
        x = self.__parseCofoldResult()
        
        time.sleep(1)
        
        self.__removeResultFilesWithCondition( self.id + '*.fa' )
        self.__removeResultFilesWithCondition( self.id + '*.out' )
        
        return x
        
    def __saveSequenceFile4Cofold(self, fname, seq1, seq2):
        
        f=open(fname,'w')
        f.write( seq1 + '&' + seq2)
        f.close()
        
    def run(self):
        
        
        self.__removePreviousFiles()
        
        self.sequence1 = self.__clearSequence(self.sequence1)  # make a sequence pretty
        #print self.sequence1
        self.sequence2 = self.__clearSequence(self.sequence2)  # make a sequence pretty
        #print self.sequence2
        
        
        self.__saveSequences(self.sequence1, self.sequence_file1) # save the sequence into a file
        self.__saveSequences(self.sequence2, self.sequence_file2) # save the sequence into a file
        
        self.__execute() # run the mfold

        time.sleep(1)
        #x = self.__parseResult()
        x = self.__parseResult2() #to obtain the spacing between ATG AND SD
        
        # if x (dG) is equal to zero. there might be an error.
        time.sleep(1)
        self.__removePreviousFiles()
        
        
        #print 'SD. ', self.sequence1, ' : ', self.sequence2, ' -> ', x
        return x

    def __execute(self):
        
        cmd1 = ''
        
        if self.perl_installed:
            cmd1 = 'perl hybrid-2s.pl -E '
        else:
            cmd1 = 'hybrid-2s_pl.exe '
        
        # 37 default,    . .
        #   37'C  A.
        # ....................
        if self.temp != 37:
            cmd1=cmd1+'--tmin='+str(self.temp)+' --tmax='+str(self.temp)+' --temperature=' + str(self.temp)+ ' ' 
        else:
            cmd1=cmd1+'--tmin=37 --tmax=37 '
        #cmd1=cmd1+'--tmin=37 --tmax=37 '
        #...........................
        
        cmd1=cmd1+self.sequence_file1 + ' ' + self.sequence_file2
        
        global COMPILED_OR_NOT
        if COMPILED_OR_NOT:
            process = os.popen4(cmd1)
        else:
            os.system(cmd1 + ' > ' + self.id + '_hybrid.log') 
        
    
    def  __executeCofold(self):

        cmd1 = 'RNAcofold '
        
        if self.temp != 37:
            cmd1 = cmd1 + ' -T ' + str(self.temp)
        
        cmd1= cmd1+ ' -p -d2 -noLP < ' + self.id+'.fa > ' + self.id + '.out'

        #print cmd1
        #os.system(cmd1) 
        process = os.popen4(cmd1)
        
    def __parseCofoldResult(self):
        
        dG = 100.0
        
        s = ''
        
        fi = self.id + '.out'
        f=open(fi,'r')
        for i in f.readlines():
            s = i.replace('\n','')
            
        f.close()
        
        x = s.split('=')
        
        dG = eval ( x[1].strip() )
        return dG
        
    def __parseResult(self):
        
        '''
        get Gibbs free energy from result files
        '''
        
        
        try:
            dG = COMMON.INF
            
        
            fi = self.sequence_file1.replace('.seq', '') + '-' + self.sequence_file2.replace('.seq','')+'.ct'
            
            #print 'RESULT: ', fi
            
            f= open(fi,'r')
            
            x = f.readlines()
            
            try:
                dG_energy = x[0].split('\t') [1]
                #print 'dG energy section = ', dG_energy
                
                dG = eval(  dG_energy.split('=')[1].strip()  )
            except:
                # there might be an error such as "no hybridization"
                COMMON.log("there might be an error such as no hybridization")
                dG = 11  # 11  .
                
            
            f.close()
        except:
            COMMON.log("mfold parsing error: file= "+fi)
            
            dG = COMMON.INF
       
        return dG
    
    def setHybridizingProgram(self, program):
        self.program = program
        
    def __parseResult2(self):
       
        
        #print self.ATGPos, self.RBSPos, self.seqlen1, self.seqlen2
        '''
        get Gibbs free energy from result files
        '''       
        rRNA_save = 0
        template_save = 0
        
        space = 0
            
        try:
            
            dG=100 
           
            fi = self.sequence_file1.replace('.seq', '') + '-' + self.sequence_file2.replace('.seq','')+'.ct'
            
            #print 'RESULT: ', fi
            
            f= open(fi,'r')
            print fi
            try:
                #print "open"
                x = f.readline()
                temp = x.split('\t')[1].strip()
                temp = temp.split('=')[1]
                dG = eval(temp)    
                #print "temp", temp             
            
                print self.seqlen1
                for i in range(self.seqlen1):
                    x = f.readline()
                    print "gggg"
                    comp_rRNA = eval(x.split('\t')[4])
                    if comp_rRNA != 0:
                        rRNA_save = i+1
                        template_save = comp_rRNA
                        break
                    
                #print self.ATGPos, self.RBSPos, rRNA_save, template_save, self.seqlen1
            
                ref = 5 # reference number ex) rightmost G of UAAGGAG is reference. then its distance from start is 5 
                # ATCACCTCCTTA: ref=6
                # CTCCTT : ref=5
                print "ATGPos", self.ATGPos
                space = self.ATGPos - (self.RBSPos+(rRNA_save+template_save-self.seqlen1)-(self.seqlen1-ref))
                #print 'space', space
           
                f.close()
            
            except:
                space=-1
                COMMON.log("there might be an error such as no hybridization")
                
                
            
            f.close()
        except:
            dG = 0
        
       
        return dG, space
        
        
    def clearFiles(self):
        id = self.id 
        self.id = ''
        self.__removePreviousFiles()
        self.id = id
        
    def __saveSequences(self, seq, sfile):
        
        fo=open(sfile,'w')
        fo.write(seq)
        fo.close()

    def __clearSequence(self, seq):
        
        seq = seq.replace( ' ','' )
        x = seq.split('\n')
        r = ''
        for i in x:
            r = r + i
        return r
    
    def __removePreviousFiles(self):
        
        
        self.__removeResultFilesWithCondition(self.id + '*.log')
        self.__removeResultFilesWithCondition(self.id + '*.asc')
        self.__removeResultFilesWithCondition(self.id + '*.ct')
        self.__removeResultFilesWithCondition(self.id+ '*.dG')
        self.__removeResultFilesWithCondition(self.id+ '*.plot')
        self.__removeResultFilesWithCondition(self.id+ '*.run')
        self.__removeResultFilesWithCondition(self.id+ '*.det')
        self.__removeResultFilesWithCondition(self.id+ '*.seq')
        self.__removeResultFilesWithCondition(self.id+ '*.png')
        self.__removeResultFilesWithCondition(self.id+ '*.ps')    
        self.__removeResultFilesWithCondition(self.id+ '*.ss')
        self.__removeResultFilesWithCondition(self.id+ '*.ps')    
        self.__removeResultFilesWithCondition(self.id+ '*.gifdat')
        self.__removeResultFilesWithCondition(self.id+ '*.ss-count')    
        self.__removeResultFilesWithCondition(self.id+ '*.h-num')    
        self.__removeResultFilesWithCondition(self.id+ '*.rnaml')
        self.__removeResultFilesWithCondition(self.id+ '*.ext')
    
    def __removeResultFilesWithCondition(self, fi):

        
        try:
            lll=glob.glob('./'+fi)
            for i in lll:
                #print 'Removing ', i
                # sometimes, the file 'i' is removed by other program. (curious!)
                
                # mfold      .
                #   .
                
                if os.path.exists(i) and i[5].isdigit():
                    
                    max_del_trial=5
                    counter=0
                    
                    #print 'HYBRID DEL ', i
                    #if i.find('.det')>0:
                    #    time.sleep(1)
                    
                    while(counter<max_del_trial):
                        try:
                            if os.access(i, os.W_OK):
                                    os.remove(i)
                                    break
                        except:
                            COMMON.log("Error while deleting " + i +" file in FOLD CLASS, " + str(counter))
                        
                        counter=counter+1
                        time.sleep(1)

        except:
            COMMON.log("Error in deleting temperary files")
            print 'Error in deleting temperary files'
                
class FOLD(threading.Thread):
    
    sequence = None
    ids = None
    sequence_file = None
    over=False
    result = None
    temp = 37
    perl_flag = False
    
    def __init__(self, default_id='00000'):
        
        # initialize this thread
        threading.Thread.__init__(self)
                
        # initialize variables
        self.sequence = ''
        self.ids = default_id + '_' + str(random.randint(0, 10000000))+'x'
        self.sequence_file = self.ids + '.seq'
        self.over = False
        self.result = RESULT()
        self.perl_flag = False
    
        
    def setPerl(self, flag_true_or_false ):
        self.perl_flag = flag_true_or_false
        
    def setAll(self, sequence, temperature ):
        self.sequence = sequence
        self.temp = temperature
    
    '''
    def clearFiles(self):
        id = self.id
        self.id=''
        self.__removePreviousFiles()
        self.id = id
    '''
   
    def isOver(self):
        return self.over

    
    def Width(self,plus) :
        Start = False
        seqLen = len(self.sequence)
        StartPosition = 0
        EndPosition = 0
        
        for x in range(seqLen):
            if Start == False : 
                if self.sequence[x].isupper() :
                    Start = True
                    StartPosition = x
            if Start == True :
                if x+1 in range(seqLen):
                    if self.sequence[x+1].islower():
                        EndPosition = x
                        break
                   
        
        if StartPosition- plus <0 :
            StartPosition = 0
        else:
            StartPosition = StartPosition - plus
            
        if EndPosition+plus >= seqLen-1:
            EndPosition = seqLen-1
        else:
            EndPosition = EndPosition + plus
            
        return [StartPosition,EndPosition]
    
    def run(self):
        '''
        Runs mfold within a thread. If done, you can get a True using .isOver().
        '''
        
        self.over = False
        try:
            self.result = self.__fold()
        except:
            self.result = None
            #print 'Error'
            COMMON.log( 'Error in FOLD class, esp. in running mfold' )
          
        self.over = True
        
        return self.result
        
    def fold(self):
        
        self.__removePreviousFiles()   # remove previous files
        
        self.sequence = self.__clearSequence(self.sequence)  # make a sequence pretty
        self.__saveSequence(self.sequence) # save the sequence into a file
        self.__execute() # run the mfold

        time.sleep(1)
        x  = self.__parseResult()
        
        PLUS = 0
        RBS_RANGE =  self.Width(PLUS)

        y = self.__parseForEnergyOfPortion(RBS_RANGE)
       
        for s_index in range( len(y) ):
            x.setRBSEnergy( s_index, y[s_index] )
        
        time.sleep(1)
        self.__removePreviousFiles()
        
        return x
        
    def __execute(self):
        
        cmd1 = ''
        if self.perl_flag:
            cmd1 = 'UNAFold.pl'
        else:
            cmd1 = 'UNAFold_pl.exe'
        
        cmd1 =  cmd1 + ' --window=0  --maxbp=40 '
        #cmd1='perl ./UNAFold3.pl --window=0  --maxbp=40 '
        
        # ................
        if self.temp != 37:
            cmd1=cmd1 + '--temp=' + str(self.temp) + ' '
        
        cmd1= cmd1 + self.sequence_file            
        
        
        #cmd1='perl ./UNAFold3.pl -t 42 --window=0  --maxbp=40 '+ self.sequence_file            
        #cmd1='perl ./UNAFold3.pl --percent=90 '+ self.sequence_file            
        #cmd1='perl ./UNAFold3.pl --window=0 --maxbp=100 '+ self.sequence_file            
        #cmd1='perl ./UNAFold3.pl -t 42 '+ self.sequence_file            
        #print 'FOLD: ', cmd1
        
        global COMPILED_OR_NOT
        if COMPILED_OR_NOT:
            process = os.popen4(cmd1)
        else:
            os.system(cmd1 + ' > ' + self.ids+ '_folding.log' )
        
        
        
        '''
        cmd1='./hybrid-ss-min ' + self.sequence_file
        cmd2='./ct-energy --verbose ' + self.sequence_file.replace('.seq','.ct')+' | perl ct-energy-det.pl --mode=text > ' + self.sequence_file.replace('.seq','.det')
    
        os.system(cmd1)
        os.system(cmd2)
        '''
        
    def __saveSequence(self, sequence):
        
        fo=open(self.sequence_file,'w')
        fo.write(sequence)
        fo.close()

    def __clearSequence(self, seq):
        
        seq = seq.replace( ' ','' )
        x = seq.split('\n')
        r = ''
        for i in x:
            r = r + i
        return r

    def __removePreviousFiles(self):
        

        self.__removeResultFilesWithCondition(self.ids + '*.log')
        self.__removeResultFilesWithCondition(self.ids + '*.ann')
        self.__removeResultFilesWithCondition(self.ids + '*.ct')
        self.__removeResultFilesWithCondition(self.ids+ '*.dG')
        self.__removeResultFilesWithCondition(self.ids+ '*.plot')
        self.__removeResultFilesWithCondition(self.ids+ '*.run')
        self.__removeResultFilesWithCondition(self.ids+ '*.det')
        self.__removeResultFilesWithCondition(self.ids+ '*.seq')
        self.__removeResultFilesWithCondition(self.ids+ '*.png')
        self.__removeResultFilesWithCondition(self.ids+ '*.ps')    
        self.__removeResultFilesWithCondition(self.ids+ '*.ss')
        self.__removeResultFilesWithCondition(self.ids+ '*.ps')    
        self.__removeResultFilesWithCondition(self.ids+ '*.gifdat')
        self.__removeResultFilesWithCondition(self.ids+ '*.ss-count')    
        self.__removeResultFilesWithCondition(self.ids+ '*.h-num')    
        self.__removeResultFilesWithCondition(self.ids+ '*.rnaml')
        self.__removeResultFilesWithCondition(self.ids+ '*.pdf')
        self.__removeResultFilesWithCondition(self.ids+ '*.log')
        self.__removeResultFilesWithCondition(self.ids+ '*.asc')
        self.__removeResultFilesWithCondition(self.ids+ '*.ext')
    
    def __removeResultFilesWithCondition(self, fi):

        
        try:
            lll=glob.glob('./'+fi)
            for i in lll:
                #print 'Removing ', i
                # sometimes, the file 'i' is removed by other program. (curious!)
                
                # mfold      .
                #   .
                if os.path.exists(i) and i[5].isdigit():
                    
                    max_del_trial=5
                    counter=0
                    
                    #if i.find('.det')>0:
                    #    time.sleep(1)
                    #print 'FOLD DEL ', i
                    while(counter<max_del_trial):
                        try:
                            if os.access(i, os.W_OK):
                                    os.remove(i)
                                    break
                        except:
                            COMMON.log("Error while deleting " + i +" file in FOLD CLASS, " + str(counter))
                        
                        counter=counter+1
                        time.sleep(1)
        except:
            COMMON.log("Error in deleting temperary files")
            print 'Error in deleting temperary files'            
       
    
    def __parseResult(self):
        '''
        Parsing
        '''

        IN_HELIX = False
        
        # check result files. If any file is missing, returns null
        if not (os.path.exists( self.sequence_file.replace('.seq','.ct') ) and os.path.exists( self.sequence_file.replace('.seq','.det') ) ):
            return None
                
        #r = RESULT()
        r = self.result
        r.setSequence(self.sequence)
        #print self.sequence
        
        #print "CONSISTENCY : "
        #print r.checkConsistency()
        #print repr(r)
        
        
        # exposure/complex score 
        ff=open( self.sequence_file.replace('.seq','') + '.ct','r')
        try:
            temp = ff.readline()
            temp = temp.split()
            LEN = eval(temp[0])
        except:
            #    .
            COMMON.log("ct  ")
            ff.close()
            return None
        ff.close()
        
        # Obtain the length of sequence                
        stSet = []
        try:
            fxx=open( self.sequence_file.replace('.seq','') + '.det','r')
            while(True):
                stxx = fxx.readline()
                if len(stxx)==0:
                    break
                else:
                    stSet.append( stxx.replace('\n', '' ) )
            fxx.close()
        except:
            
            COMMON.log("det   ")
            fxx.close()
            return None
        
        
        # ------------------------
        HelixResult = RESULT_HELIX()
        Structure4Helix = [ [], -1 ]  # Helix[], Energy
        #Helix_Structure = [ -1, -1 ] # Energy, position
        Stack_Flag = False
        Stack_bp = -1
        Stack_Helix_Energy = -1
        FirstLoop=True
        # ------------------------
        
        SNumber = 0
        HNumber = 0        
    
        Hstart1 = 0
        Hend1 = 0
        
        Hstart2 = LEN
        Hend2 = LEN
        
        Hon = True
        HPon = False
        
        Near = []
        rg1 = []
        rg2 = []
        InfoNt = []            
          
        for k in range(LEN) :
            #InfoNt.append([0,0,False,0,[0,0]])          
            InfoNt.append([0,0,False,0,[0,0],-1])#1208          
        
        
        HelixEnergy = 0
        NearEnergyFoward = 0
        NearEnergyBackward = 0
        
        MLInfo = [[0,0,0]] #stack        
         
        for s in stSet :
            #print s
            #s = s.replace(' ','')
            line = s.split(':')
            #print line
          
            #print 'line[0] '+line[0]

            if 'Structure' in line[0]:
     
                
                
                '''    
                print''
                
                for k in range(LEN) :
                    print k,
                    print InfoNt[k]
                '''    
                if SNumber != 0 :
                    
                    for k in range(LEN) :
                        m = copy.deepcopy(InfoNt[k])
                        r.addNucleotideInformation(m[0],m[1],m[2],m[3],m[4],m[5])
                        
                    # add previous structure info
                    #Structure4Helix[0]=copy.deepcopy(Helix_Structure)
                    HelixResult.addStructure( copy.deepcopy(Structure4Helix[0] ), Structure4Helix[1] )
                    Structure4Helix = [ [], -1 ]
                    #Helix_Structure = [ -1, -1 ]
                    Stack_bp = -1
                    Stack_Flag = False
                    Stack_Helix_Energy = -1
                    FirstLoop = True
                 
                
                SNumber += 1   
                
                line[1] = line[1].replace('\n','')
                line[1] = line[1].split('=')
                line[1][1] =line[1][1].replace('dH','')
                #print line[1]
                r.setStructureEnergy(SNumber-1, eval(line[1][1]))
                
                Hstart1 = 0
                Hend1 = 0
                
                Hstart2 = LEN
                Hend2 = LEN
                
                rg1 = []
                rg2 = []
                
                InfoNt = []
                
                for k in range(LEN) :
                    InfoNt.append([SNumber-1,0,False,0,[0,0],-1])
                
                HelixEnergy = 0
                NearEnergyFoward = 0
                NearEnergyBackward = 0
 
                MLInfo = [[0,0,0]] 
                # initialize
                   
                # helix
                # add structure energy
                # -----------------------------------------------
                Structure4Helix[1]= eval( line[1][1] )
                # -----------------------------------------------
                
            if line[0] == 'Stack':
                
                
                #yx = line[1]
                line[1] = line[1].replace(' ','').strip()
                line[1] = line[1].replace('(',')')
                line[1] = line[1].split(')')
                Base1 = eval(line[1][1])
                Base2 = eval(line[1][3])
                
                if Hon == True :
                    Hstart1 = Base1
                    Hend1 = Base1
                    Hstart2 = Base2
                    Hend2 = Base2
                    Hon = False
                else :
                    Hend1 = Base1
                    Hend2 = Base2
                    
                # ---------------------------------------
                if Stack_Flag == False:
                    Stack_Flag = True
                    Stack_bp = Base1
                # ---------------------------------------
            
            if line[0] == 'Helix' :
                
                HNumber += 1
                
                #line[1] = line[1].replace('b','=')
                #line[1] = line[1].split('=')
                tx = line[1].split('=')[1]
                
                HelixEnergy = eval( tx[:8].strip() )
                
                rg1 = range(Hstart1,Hend1+1+1)
                rg2 = range(Hend2-1, Hstart2+1)
                rg2 = rg2[::-1]
              
                Hon = True
            
                
                # -------------------
                Stack_Helix_Energy = HelixEnergy
                Structure4Helix[0].append ( [ Stack_Helix_Energy, Stack_bp ] )
                Stack_bp = -1
                Stack_Flag = False
                Stack_Helix_Energy = -1
                # --------------------
                
            if 'loop' in line[0] :
                
                #  --------------------------------
                Stack_bp = -1
                Stack_Flag = False
                Stack_Helix_Energy = -1
                # ------------------------------
                #
                if 'External' in line[0] :
                    #line[1] = line[1].replace('s','=')
                    #line[1] = line[1].split('=')
                    tx = line[1].split('=')[1]
                    tx2 = tx[:8]
                    NearEnergyFoward = eval( tx2 )
                   
               
                else :
                    MLon = False
                    if 'Multi' in line[0] :
                        MLon = True
                        MLsave = line[1]
                    
                    if 'Hairpin' in line[0]:
                        HPon = True
                        HPsave  = line[1]
                        
                    line[1] = line[1].replace('E','=')
                    line[1] = line[1].replace('C','=')
                    line[1] = line[1].split('=')
                    NearEnergyBackward = eval(line[1][1])
                    
                    # ---------------------------------
                    # add the backward loop energy to the helix
                    if IN_HELIX:
                        #    .
                        # Internal helix E   IN_HELIX Truue.
                        if FirstLoop==False:
                            #print repr(Helix_Structure)
                            hx = Structure4Helix[0][-1]
                            hx[0] = hx[0] + NearEnergyBackward
                        else:
                            FirstLoop=False
                    # ----------------------------------
                    
                    #print rg1
                    #print rg2
                    
                    
                    for i in range(len(rg1)):
                        #print rg1[i]-1
                        InfoNt[rg1[i]-1] = [SNumber-1,HNumber,True,HelixEnergy,[NearEnergyFoward,NearEnergyBackward],rg2[len(rg1)-1-i-1]-1]#1208
                        
                    for i in range(len(rg2)):
                        #print rg2[i]-1
                        InfoNt[rg2[i]-1] = [SNumber-1,HNumber,True,HelixEnergy,[NearEnergyFoward,NearEnergyBackward],rg1[len(rg2)-1-i]-1]#1208
                    
                    
                    '''    
                    for k in rg1:
                        print k
                        InfoNt[k-1] = [SNumber-1,HNumber,True,HelixEnergy,[NearEnergyFoward,NearEnergyBackward]]
                    for k in rg2:
                        print k 
                        InfoNt[k-1] = [SNumber-1,HNumber,True,HelixEnergy,[NearEnergyFoward,NearEnergyBackward]]
                    '''
                    
                    if MLon :
                        MLsave = MLsave.replace(')','(')
                        MLsave = MLsave.split('(')
                        start = eval(MLsave[1])
                        end = eval(MLsave[3])
                        MLInfo.append([NearEnergyBackward,start,end])
                        MLon = False
                        
                    NearEnergyFoward = NearEnergyBackward
                    
                    if HPon :
                        HPsave = HPsave.replace(')','(')
                        HPsave = HPsave.split('(')
                        hstart = eval(HPsave[1])
                        hend = eval(HPsave[3])
                        
                        if len(MLInfo) > 1 :
                            Temp = MLInfo.pop()
                            if (Temp[1] > hstart) or (Temp[2] < hend) :
                                NearEnergyFoward = 0
                            else :
                                NearEnergyFoward = Temp[0]
                                MLon = True
                                MLInfo.append(copy.deepcopy(Temp))
                        else :
                            NearEnergyFoward = 0
                        
                        HPon = False
                            
                      
                    
        #
        # encode here for parsing results
        #
        
        HelixResult.addStructure( copy.deepcopy(Structure4Helix[0] ), Structure4Helix[1]  )
        HelixResult.setSequence( self.sequence)
        r.setResultForInternalStructure( HelixResult )
        '''
        print ''
        for k in range(LEN):
            print k ,
            print InfoNt[k]
        '''
        
        #print LEN
        
        #print 'INFONT'
        #print len(InfoNt) 
            
        
        for k in range(LEN) :
            #m = copy.deepcopy(InfoNt[k])
            #r.addNucleotideInformation(m[0],m[1],m[2],m[3],m[4])
            r.addNucleotideInformation(InfoNt[k][0],InfoNt[k][1],InfoNt[k][2],InfoNt[k][3],InfoNt[k][4],InfoNt[k][5])
            
        #for k in range(LEN) :
        #    print r.getNearbyEnergy(1,k)
        
        
        #fxx.close()

        return r
    
    
    

    
    def __parseForEnergyOfPortion(self,portion) :
        
        #portion = [0,100]
        Width = range(portion[0]-1,portion[1])
        IKnowFlag = False
        
        AllEnergy = []
        
        r = self.result
        
        #print self.result
        
        for x in range(r.getStructureSize()):
            
            helixStructure  = []
            helixStructure.append([0,0])
            
            loopStructure = []
            
            
            for y in Width :
                helixStructure.sort()

                Test = False
                                
                if r.getHelixIDof(x,y) != 0: 
           
                    Test = True
                    for z in range(len(helixStructure)) :
                        
                        if r.getHelixIDof(x,y) == helixStructure[z][0]:
                            Test = False
                
                        
                if Test == True :
                    helixStructure.append([r.getHelixIDof(x,y),r.getEnergyOf(x,y)])
                    #print helixStructure
                        
                    '''
                    if helixStructure[len(helixStructure)-1][0] != r.getHelixIDof(x,y) :
                        helixStructure.append([r.getHelixIDof(x,y),r.getEnergyOf(x,y)])
                        print helixStructure
                    '''
            
            for y in Width:
                if IKnowFlag == False :
                    if r.getHelixIDof(x,y) != 0 :
                        IKnowFlag = True
                        loopStructure.append(r.getNearbyEnergy(x,y)[0])
                            
                if IKnowFlag == True :
                    if r.getHelixIDof(x,y) != 0:
                        if y+1 in Width:
                            if r.getHelixIDof(x,y+1) == 0:
                                loopStructure.append(r.getNearbyEnergy(x,y)[1])
            
            
            #if IKnowFlag == False:
                
            #    #    . UNAfold ...
            #    return 0
       
            Sum = 0
            
            for y in range(len(helixStructure)) :
                #print 'helix'
                #print helixStructure[y][1]
                Sum += helixStructure[y][1]
            #print 'Sum1' , Sum
            
            for y in range(len(loopStructure)) :
                #print 'loop'
                #print loopStructure[y]
                Sum += loopStructure[y]
                
            AllEnergy.append(Sum)
            #print 'Sum2', Sum
            #print
            
        
        '''
        print 'helix'
        print helixStructure
        '''
        '''
       
        print 'loop'
        print loopStructure
         
        for x in range(r.getStructureSize()) :
            print 'Structure ', x
            Sum = 0
            for y in range(len(helixStructure)) :
                #print 'helix'
                #print helixStructure[y][1]
                Sum += helixStructure[y][1]
            print 'Sum1' , Sum
            
            for y in range(len(loopStructure)) :
                #print 'loop'
                #print loopStructure[y]
                Sum += loopStructure[y]
            AllEnergy.append(Sum)
            print 'Sum2', Sum
            print
        '''   
        '''
        print 'All Energy'
        print
        print AllEnergy
        print
        print 'End'
        print
        '''
        
        #print '*** ', AllEnergy
        return AllEnergy
    
    

    
    

    
    
class FASTA:
    
    sequences = []
    
    
    GENENAME='GENENAME'
    RBSSEQUENCE='SDPOS'   # : . 
    aSD_SEQUENCE='ASDSEQUENCE'
    SPACER_LENGTH='SPACERLENGTH'
    AUTOMATIC_PROCESS_OR_NOT="AUTO"
    TEMPERATURE='TEMP'
    SPACER_RANGER = 'SPACERRANGE'
    ATGINDEX='ATGPOS'
    STOPCODON='STOPCODON'
    
    def __init__(self):
        
        self.sequences = []
        
    def open(self, filename):
        
        f=open(filename,'r')
        
        seq = ''
        info = ''
        
        for s in f.readlines():
            s=s.replace('\n','').strip()
            
            if len(s)>0:
                
                if s[0]=='>':
                    
                    if len(seq)>0:
                        self.sequences.append( [seq, info] )
                    
                    seq = ''
                    info = s[1:].upper().strip()
                    
                elif s[0] != '#' :
                    seq = seq + s.replace(' ','')
        
        if len(seq)>0:
            self.sequences.append( [seq, info ] )
            
        
        f.close()
    
    def getSequenceSize(self):
        return len(self.sequences)
    
    def getSequenceAt(self, index):
        return self.sequences[index][0]
    
    def getSequenceInformationAt(self, index):
        return self.sequences[index][1]

    def getSequenceInformationByDictAt(self, index):
        
        r={}
        s = self.getSequenceInformationAt(index).strip().split(',')
        
        
        r[ self.TEMPERATURE ] = 37
        
        
        
        for j in s:
            
            x = j.split('=')
            key = x[0].strip()
            value = x[1].strip()
            r[key]=value
        
        #  range  .
        #r[ self.SPACER_RANGER ] = r[ self.SPACER_LENGTH ]
        
        return r

    
    def writeData(self, output):
        
        f=open(output,'w')
        f.close()
        
        for index in range( self.getSequenceSize() ):
            info = self.getSequenceInformationByDictAt(index)
            seq = self.getSequenceAt(index)
            
            
            title = ''
            if info.has_key[ self.GENENAME ]:
                title = self.GENENAME + '=' + info[self.GENENAME]
            
            if info.has_key[ self.RBSSEQUENCE]:
                if len(title)>0:
                    title = title + ','
                title = self.RBSSEQUENCE + '=' + info[self.RBSSEQUENCE]
            
            if info.has_key[ self.ATGPOSITION]:
                if len(title)>0:
                    title = title + ','
                title = self.ATGPOSITION+ '=' + info[self.ATGPOSITION]
            
            if len(title)==0:
                title = self.getSequenceInformationAt(index)
                if len(title)==0:
                    title = 'Nope'
            
            f = open(output,'a')
            f.write('> ' + title + '\n')
            f.write( seq + '\n')
            f.close()
        


        
if __name__=='__main__':



    print 'This file cannot be run due to the change of sequence file format.'
    import sys
    sys.exit(1)

    print 'test'
    rnd = FOLD()
    ret = RESULT()

    tt = []
    rr = []

    
    fasta=FASTA()
    fasta.open( sys.argv[1] )
    
    tt=[]
    ex=[]
    for x in range(fasta.getSequenceSize()):
        rr.append(1)
        tt.append( fasta.getSequenceAt(x) )
        #ex.append( eval( fasta.getSequenceInformationAt(x) ) )
        
   
    print 'Gene Name\tw/o SD\tw/ SD\tConfidence Score'
    for k in range( fasta.getSequenceSize() ):
        
        # W/o SD        
        
        rnd=FOLD()
        ret = RESULT()
        
        ret = rnd.fold (tt[k])
        #print rnd.__parseForEnergyOfPortion([10,20])
        
        #print repr(ret)
        s=SCORE(ret)
        
        score = s.getSequenceExposureScore()
        
        '''
        for g in range(ret.getStructureSize()):
            print "Structure : ",g
            for h in range(ret.getSequenceLength()):
                print h, " ", ret.getPairedBpPosition(g,h)
        '''
                
        
        
        
        
        # W/ SD
        import RBS_GA
        s = RBS_GA.SEQUENCE( fasta.getSequenceAt(k), 0 )
        
        s.current_sequence = fasta.getSequenceAt(k)
        
        # options
        s.INCLUDE_RIBOSOME = 1
        
        score_sd = s.calculateScore()
        conf_score = s.getAveragedConfidenceScore()
        
        
        #gene_name = fasta.getSequenceInformationByDictAt(k) [ fasta.GENENAME ]
        gene_name = fasta.getSequenceInformationAt(k)
        print gene_name, '\t', score, '\t', score_sd, '\t', conf_score
    
    print 'DONE'
    
    
    
    
    
    
    
