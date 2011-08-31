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
import RBS_sj
import random





class SDFINDER:
    
    __CONST_SEARCH_RANGE_FROM = -27
    __CONST_SEARCH_RANGE_TO = - 6
    #__CONST_rRNA = 'UCACCUCCUU'
    __CONST_rRNA = 'CCUCCU'
    __CONST_SD_LEN = 6
    
    __atg_index = -1
    
    __sd_sequence = ''
    __sd_index = ''
    __spacer_len = -1
    __sequence = ''
    __aSD = ''
    __temperature = ''
    
    __perl_installed = False
    
    __pre_energy = {}
    __program = 1
    
    __reliableSD=False
    
    def __init__(self):
        pass
    
    def setPreDefinedEnergy(self, energy):
        self.__pre_energy = energy
        
    def setPerl(self, flag):
        self.__perl_installed = flag
        
        
    def setAll(self, sequence, aSD, atg_index, temperature, program ):
        
        
        
        if aSD == '':
            self.__aSD = self.__CONST_rRNA.strip().upper().replace('T','U')
        else:
            self.__aSD = aSD.strip().upper().replace('T','U')
        
            
        #print 'SD Finder : = ', self.__aSD
            
        self.__sequence = sequence
        self.__atg_index = atg_index
        self.__temperature = temperature
        self.__program = program
        
        
    def find(self):

        #after running this method,
        #SDStartIndex() and SpacerLength may be changed.
        
        FROM = self.__CONST_SEARCH_RANGE_FROM
        TO = self.__CONST_SEARCH_RANGE_TO
        SD_LEN = len( self.__aSD )  # AGGAGG  <- hybrid this 9bp
        
        stored = 100.0
        stored_index = -1
        stored_sd = ''
        
        st_temp = str( self.__temperature ).strip()
        
        # UTR    .
        if self.__atg_index + FROM <0:
            FROM = - self.__atg_index
        
            
            
        for index in range(FROM, TO + 1, 1):
            
            here = self.__atg_index + index
            
            
            p_sd = self.__sequence [ \
                here : here + SD_LEN ]
            
            gibbs = 0.0

            p_sd = p_sd.upper().replace('U','T')
            
            # AGGAGG  AGGAG    .
            #       .
            
            
            if p_sd [:7]== 'AAGGAGG':
                gibbs = -100.0
            
            elif p_sd [ 1:7 ] == 'AGGAGG':
                gibbs = -50.0
            
            #  AGGA 4bp   .
            elif p_sd [ 1:5 ] == 'AGGA':
                gibbs = -20
                
            
            id = '2_' + str(random.randint(0, 10000000))+'u' 
            h = RBS_sj.HYBRID( id )
            h.setAll( p_sd, self.__aSD, self.__temperature )
            h.setPerl( self.__perl_installed )
            h.setHybridizingProgram( self.__program )
            h.setPrecalculateEnergy( self.__pre_energy )
            
            #print 'SD '
            tgibss = h.runHybridToGetEnergy()
            gibbs = gibbs + tgibss
            
            
            
            if gibbs < stored:
                stored = gibbs
                stored_index = here
                stored_sd = p_sd
            
                '''
                print 'SD=', p_sd
                print 'aSD=',self.__aSD
                print 'dG = ', gibbs
                print 'index =', here
                '''
            
        # spacer len 
        # sp_len = self.__atg_index - (stored_index + SD_LEN ) 
        sp_len = self.__atg_index - (stored_index + 6 ) 
        # AAGGAG____ATG   : aaggag  atg  .
        
        #   dG 100 
        #  SD  .
        if stored>0:
            self.__reliableSD = False
        else:
            self.__reliableSD = True
        
        self.__sd_index = stored_index
        self.__sd_sequence = stored_sd
        
        self.__sd_gibbs = stored
        self.__spacer_len = sp_len
        
        #print 'Found SD = ', stored_sd, '=', self.__aSD, ' index = ', stored_index
        #a=raw_input('Enter')
        
    def getFoundSDIndex(self):
        return self.__sd_index
    def getFoundSDSequence(self):
        return self.__sd_sequence
    def getFoundSpacerLen(self):
        return self.__spacer_len
    def getFoundSDEnergy(self):
        return self.__sd_gibbs
    
    def isReliableSD(self):
        return self.__reliableSD
        
    
