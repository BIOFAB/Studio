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
import os
import math
#try:
#    import MySQLdb
#except:
#    print 'COMMON.MySQL failed'
    
import time

#abs_path = os.path.abspath( os.path.dirname( __file__ ) )

INF = 1e20
PRECALCULATED_ENERGY_UPPER_LIMIT = 100000
PRECALCULATED_ENERGY_UPPER_LIMIT_STR = 'UPPER_LIMIT'

STATUS_QUEUE = 'QUEUE'
STATUS_RUNNING = 'RUNNING'
STATUS_DONE = 'DONE'
STATUS_FAILED = 'FAILED'
STATUS_DELETED = 'DELETED'

TABLE_ID = 'ID'
TABLE_QUERY_SEQUENCE = 'QUERY_SEQ'
TABLE_INFO = 'INFO'
TABLE_EMAIL = 'EMAIL'
TABLE_SEQ_NAME = 'SEQ_NAME'
TABLE_DATE_SUBMITTED = 'DATE_SUBMITTED'
TABLE_STATUS = 'STATUS'
TABLE_UTR = 'UTR_SEQUENCE'
TABLE_OPTIMIZED_SEQUENCE = 'OPTIMIZED_SEQ'
TABLE_DATE_FINISHED = 'DATE_FINISHED'
TABLE_CDS = 'CDS_SEQUENCE'
TABLE_MANUAL_INPUT_OR_NOT = 'MANUAL_INPUT_OR_NOT'
TABLE_TARGET_SCORE = 'TARGET_SCORE'
TABLE_TRIAL = 'TRIAL'
TABLE_OPTIMIZE_CODON_OR_NOT = 'OPTIMIZE_CODON_OR_NOT'
TABLE_SD_START_INDEX = 'SD_INDEX'
TABLE_SD_LENGTH = 'SD_LENGTH'
TABLE_PROB_METHOD='PROB_METHOD'
TABLE_SPACER_LENGTH='SPACER_LENGTH'
TABLE_SPACER_RANGE='SPACER_RANGE'
TABLE_TARGET_SCORES='TARGET_SCORES'  #  :score,:score:  .
TABLE_aSD_SEQUENCE = 'ASD_SEQUENCE'
TABLE_SD_SEQUENCE='SD_SEQUENCE'
TABLE_ATG_INDEX = 'ATG_INDEX'
TABLE_FIND_SD = 'FIND_SD'
TABLE_STOP_CODON='STOPCODON'
#LOG_FILE = abs_path + '/log.txt'
LOG_FILE = "./log.txt"


CONFIDENCE_THRESHOLD = 0.8
LOWER_CONFIDENCE_THRESHOLD = 0.4

MYSQL_BUG_FIXED = False    
    
    
class CODON_TABLE:
    
    nt_to_aa = {}
    aa_to_nt = {}
    
    
    def __init__(self):
        self.loadCodonTable()
    
    def getCodon(self, aa):
        return self.aa_to_nt[aa.upper()]
    
    def getAminoAcid(self, codon):
        return self.nt_to_aa[codon.upper()]
        
    def loadCodonTable(self):
        
        self.aa_to_nt[ 'F' ] = [ 'TTT', 'TTC' ]
        self.aa_to_nt['L'] = [ 'TTA', 'TTG', 'CTT', 'CTC', 'CTA' , 'CTG' ]
        self.aa_to_nt['I']=['ATT', 'ATC', 'ATA' ]
        self.aa_to_nt['M'] = ['ATG' ]
        self.aa_to_nt['V'] = ['GTT', 'GTC', 'GTA', 'GTG' ]
        self.aa_to_nt['S'] = ['TCT', 'TCC', 'TCA' , 'TCG', 'AGT','AGC' ]
        self.aa_to_nt['P'] = [ 'CCT', 'CCC', 'CCA', 'CCG' ]
        self.aa_to_nt['T'] = ['ACT', 'ACC', 'ACA', 'ACG' ]
        self.aa_to_nt['A'] = ['GCT', 'GCC', 'GCA', 'GCG' ]
        self.aa_to_nt['Y'] = ['TAT', 'TAC' ]
        self.aa_to_nt['H'] = ['CAT', 'CAC' ]
        self.aa_to_nt['Q'] = ['CAA', 'CAG' ]
        self.aa_to_nt['N']=['AAT','AAC' ]
        self.aa_to_nt['K']=['AAA', 'AAG' ]
        self.aa_to_nt['D']=['GAT', 'GAC' ]
        self.aa_to_nt['E']=['GAA', 'GAG' ]
        self.aa_to_nt['C']= ['TGT', 'TGC' ]
        self.aa_to_nt['W']=['TGG']
        self.aa_to_nt['R']=['CGT','CGC','CGA','CGG', 'AGA', 'AGG']
        self.aa_to_nt['G']=['GGT', 'GGC', 'GGA' ,'GGG' ]
        
    
        for c in self.aa_to_nt.keys():
            
            nts = self.aa_to_nt[c]
            for n in nts:
                self.nt_to_aa[n] = c
    
    
class BASIC_INFO:
    
    mid = ''
    score = -1
    utr = ''
    email = ''
    cds = ''
    query_sequence = ''
    optimized_sequence = ''
    sequence_name = ''
    manual_input_or_not = -1
    date_submitted = ''
    date_finished = ''
    atg_index = -1
    info = ''
    status = ''
    target_score = 1.0
    averaged_confidence_score = -1
    transformed_score = -1.0
    trial = 0
    optimize_codon = 1
    sd_start_position_index = -1
    sd_length = 6
    confidence = -1
    prob_method='E'
    spacer_length = 10
    spacer_range=0
    target_scores = '' # '37:1.0'   #  simulation condition .   .
    aSD_sequence =  'CUCCUU' # 'UCACCUCCU'   # E. coli   .
    SD_sequence = ''
    find_sd = 1
    stopcodon = ''
    
    pre_energy = {}
    
    #   .
    SD_sequence = ''
    spacer_length = -1
    optimize_or_not = 1
    
    
    #   
    stop_codon = ''
    
    
    
    def __init__(self):
        pass
    
    
    def open(self, fname):
        
        # read basic info class content from a file
        f=open(fname,'r')
        
        for s in f.readlines():
            s = s.replace('\n', '').strip()
            if len(s)>0:
                if s.find('=')>0:
                    
                    
                    x = s.split('=')
                    
                    tag = x[0].upper().strip()
                    value = x[1].strip()
                    
                    if tag == TABLE_ATG_INDEX:
                        self.setATGIndex( eval(value) )
                    elif tag == TABLE_CDS:
                        self.setCDSSequence( value )
                    elif tag == TABLE_aSD_SEQUENCE.upper():
                        self.setAntiSDSequence( value )
                    elif tag == TABLE_FIND_SD:
                        self.setFindSD( eval(value) )
                    elif tag == TABLE_MANUAL_INPUT_OR_NOT:
                        self.setManualInputOrNot( eval(value) )
                    elif tag == TABLE_OPTIMIZE_CODON_OR_NOT:
                        self.setOptimizeCodonOrNot( eval(value) )
                    elif tag == TABLE_PROB_METHOD:
                        self.setProbMethod( value )
                    elif tag == TABLE_SD_LENGTH:
                        self.setSDLength( eval(value) )
                    elif tag == TABLE_SD_SEQUENCE:
                        self.setSDSequence( value )
                    elif tag == TABLE_SD_START_INDEX:
                        self.setSDStartPositionIndex( eval(value) )
                    elif tag == TABLE_SPACER_LENGTH:
                        self.setSpacerLength( eval(value) )
                    elif tag == TABLE_SPACER_RANGE:
                        self.setSpacerRange( eval(value) )
                    elif tag == TABLE_STOP_CODON:
                        self.setStopCodon( value )
                    elif tag == TABLE_TARGET_SCORES:
                        self.setTargetTempAndScores( value )
                    elif tag == TABLE_TRIAL:
                        self.setTrial( eval(value) )
                    elif tag == TABLE_UTR:
                        self.setUTRsequence( value )
                        #print 'val = ', value
                    
                    else:
                        print 'Unknown command: ', s
                        import sys
                        sys.exit(1)
        f.close()
    
    def toString(self):
        
        
        print '>>',self.aSD_sequence
        print '>>', self.SD_sequence
        
        s = 'ID = ' + repr(self.mid) + '\n' 
        s = s +'UTR sequence = ' + self.utr + '\n' 
        s = s +'Email = ' + self.email + '\n' 
        s = s +'CDS sequence = ' + self.cds + '\n' 
        s = s +'Optimized Sequence = '+ repr(self.optimized_sequence) + '\n' 
        s = s +'Sequence Name = ' + self.sequence_name + '\n' 
        s = s +'Target temperature(s) and score(s) = ' + self.target_scores + '\n' 
        s = s +'Probability Measure = ' + self.prob_method + '\n' 
        s = s +'Spacer Length and Range = ' + str(self.spacer_length) + ' to ' + str(self.spacer_range) + '\n' 
        s = s +'Date submitted = ' + self.date_submitted + '\n' 
        s = s +'Date finished = ' + self.date_finished + '\n' 
        s = s +'Status = ' + self.status + '\n' 
        s = s +'Optimize codon or not = ' + str(self.optimize_codon) + '\n' 
        s = s +'Trial = ' + str( self.trial) + '\n' 
        s = s +'SD start position = ' + str(self.sd_start_position_index ) + '\n' 
        s = s +'SD length = ' + str(self.sd_length) + '\n'  
        s = s +'SD Sequence = ' + self.SD_sequence + '\n' 
        s = s +'aSD Sequence = '+ self.aSD_sequence + '\n' 
        s = s +'FIND_SD = ' + str(self.find_sd) + '\n' 
        s = s +'ATG_INDEX = ' + repr(self.atg_index) + '\n'
        
         
        '''
          'Confidence = ' + eval( self.confidence ) + '\n' + \
        '''
        
        return s
        
    def setStopCodon(self, codon):
        self.stopcodon = codon
    def getStopCodon(self):
        return self.stopcodon
    def setID(self, id): self.mid = id
    def getID(self): return self.mid
    def setScore(self, score): self.score = score
    def getScore(self): return self.score
    def setUTRsequence(self, utr): 
        '''
        if config.getTrimSequenceOrNot():
            if len(utr)>config.getTrimUTRLength():
                utr=utr[ -config.getTrimUTRLength(): ]
        '''
        self.utr= clearSequence( utr )

    def getUTRsequence(self): return self.utr
    def setEmail(self, email): self.email = email
    def getEmail(self): return self.email
    def setCDSSequence(self, cds): 
        '''
        if config.getTrimSequenceOrNot():
            if len(cds)>config.getTrimCDSLength():
                cds=cds[ : config.getTrimCDSLength() ]  
        '''
        self.cds = clearSequence(cds)
        

    def getCDSSequence(self): return self.cds
    def setQuerySequence(self, q_seq): self.query_sequence = q_seq
    def getQuerySequence(self): return self.query_sequence
    def setOptimizedSequence(self, o_seq): self.optimized_sequence = o_seq
    def getOptimizedSequence(self): return self.optimized_sequence
    def setSequenceName(self, seq_name): self.sequence_name = seq_name
    def getSequenceName(self): return self.sequence_name
    def setManualInputOrNot(self, manual_or_not): self.manual_input_or_not = manual_or_not
    def getManualInputOrNot(self): return self.manual_input_or_not
    def setDateSubmitted(self, date): self.date_submitted = date
    def getDateSubmitted(self): return self.date_submitted
    def setDateFinished(self, date): self.date_finished = date
    def getDateFinished(self): return self.date_finished
    def setInfo (self, info ): self.info = info
    def getInfo(self): return self.info
    def setATGPosition(self, atg): self.atg=atg
    def getATGPosition(self): return self.atg
    def setStatus(self, status): self.status = status
    def getStatus(self): return self.status
    def setTransformedScore(self, transformed_score): self.transformed_score = transformed_score
    def getTransformedScore(self): return self.transformed_score
    def setTrial(self, trial): self.trial=trial
    def getTrial(self): return self.trial
    def getOptimizeCodonOrNot(self): return self.optimize_codon
    def setOptimizeCodonOrNot(self, value): self.optimize_codon = value
    def setSDStartPositionIndex(self, index): self.sd_start_position_index=index
    def getSDStartPositionIndex(self): return self.sd_start_position_index
    def setSDLength(self, length): self.sd_length = length
    def getSDLength(self): return self.sd_length
    def setATGIndex(self, index): self.atg_index=index
    def getATGIndex(self): return self.atg_index
    def setSDSequence(self, seq): 
        if seq == None:
            seq=''
        self.SD_sequence=clearSequence( seq )
    
    def getSDSequence(self): return self.SD_sequence
    def setProbMethod(self, m): self.prob_method=m
    def getProbMethod(self): return self.prob_method
    def setSpacerLength(self, length): self.spacer_length=length
    def getSpacerLength(self): return self.spacer_length
    def setSpacerRange(self, rang): self.spacer_range=rang
    def getSpacerRange(self): return self.spacer_range
    def setTargetTempAndScores(self, s): self.target_scores = s
    def getTargetTempAndScores(self): return self.target_scores
    def setOptimizeOrNot(self, op): self.optimize_or_not=op
    def getOptimizeOrNot(self): return self.optimize_or_not
    def setFindSD(self, v): self.find_sd = v
    def getFindSD(self): return self.find_sd
        
    '''
    def parseTempAndScores(self, s):
        c = []
        #  , score  .
        for x in s.split(','):
            a = x.split(':')
            b = [ val(a[0]), val(a[1]) ]
            c.tr_target_scores.append(b)
        return  c
    '''
    def setAntiSDSequence(self, aSD): 
        if aSD==None:
            aSD=''
        aSD = clearSequence(aSD)
        self.aSD_sequence=aSD
    def getAntiSDSequence(self): return self.aSD_sequence
        
    def setPrecalculatedEnergy(self, energy):
        self.pre_energy = energy
    
    def getPrecalculatedEnergy(self):
        return self.pre_energy
    
    def clone(self):
        
        n = BASIC_INFO()
        
        n.setID( self.getID() )
        
        n.setPrecalculatedEnergy( self.getPrecalculatedEnergy() )
        n.setUTRsequence( self.getUTRsequence() )
        n.setEmail( self.getEmail () )
        n.setCDSSequence( self.getCDSSequence() )
        n.setQuerySequence( self.getQuerySequence() )
        n.setOptimizedSequence( self.getOptimizedSequence() )
        n.setSequenceName( self.getSequenceName() )
        n.setManualInputOrNot( self.getManualInputOrNot() )
        n.setDateSubmitted( self.getDateSubmitted() )
        n.setDateFinished( self.getDateFinished() )
        n.setInfo( self.getInfo() )
        
        n.setStatus( self.getStatus() )
        n.setTransformedScore( self.getTransformedScore())

        n.setTrial( n.getTrial() )
        
        n.setOptimizeCodonOrNot( self.getOptimizeCodonOrNot() )        
        n.setSDStartPositionIndex( self.getSDStartPositionIndex() )
        n.setSDLength( self.getSDLength() )
        
        n.setProbMethod( self.getProbMethod() )
        n.setSpacerLength( self.getSpacerLength() )
        n.setSpacerRange( self.getSpacerRange() )
        n.setTargetTempAndScores( self.getTargetTempAndScores() )
        n.setAntiSDSequence( self.getAntiSDSequence() )
        n.setSDSequence( self.getSDSequence() )

        n.setATGIndex( self.getATGIndex() )
        n.setFindSD( self.getFindSD() )
        
        return n
    
class CONFIG:
    
    host = 'HOST'
    user = 'USER'
    passwd = 'PASSWD'
    db = 'DB'
    table = 'TABLE'
    CONFIG_FILE = 'config.cfg'
    CPU = 'CPU'
    INCLUDE_SD = 'SD'
    DEBUG = 'DEBUG'
    THREAD_PER_SEQUENCE='THREAD_PER_SEQUENCE'
    RBSDESIGNER_FOLDER = 'RBSDESIGNER_FOLDER'
    MODE = 'MODE'
    TRIAL = 'TRIAL'
    MODE_RANK = 'MODE_RANK'
    ADDITIONAL_MACHINE = 'ADDITIONAL_MACHINE'
    PROCESS_SEQUENCE = 'PROCESS_SEQUENCE'
    LEN_UTR = 'LEN_UTR'
    LEN_DTR = 'LEN_DTR'
    NUCLEOTIDES = 'NUCLEOTIDES'
    TRIM_SEQUENCE='TRIM_SEQUENCE'
    TRIM_UTR_LEN='TRIM_UTR_LEN'
    TRIM_CDS_LEN='TRIM_CDS_LEN'
    PERL_INSTALLED = 'PERL_INSTALLED'
    SD_ENERGY_PROGRAM='SD_ENERGY_PROGRAM'
    SD_ENERGY_FILE='SD_ENERGY_FILE'
    SMTP_SERVER='SMTP_SERVER'
    SMTP_PORT='SMTP_PORT'
    EMAIL_SENDER='EMAIL_SENDER'
    
    values = {}
    
    def __init__(self):
        
        self.values[ self.host ] = 'localhost'
        self.values[ self.SD_ENERGY_FILE ] =''
        self.values[ self.SD_ENERGY_PROGRAM ] = '1' # mfold .
        self.values[ self.user ] = 'RBS'
        self.values[ self.passwd ] = 'rbs'
        self.values[ self.db ] = 'seq'
        self.values[ self.table ] = 'rbs'
        self.values[ self.CPU ] = '1'
        self.values[ self.DEBUG ] = 'False'
        self.values[ self.INCLUDE_SD] = 'False'
        self.values[ self.THREAD_PER_SEQUENCE ] = '10'
        self.values[ self.RBSDESIGNER_FOLDER ] = '.'
        self.values[ self.TRIAL ] = '1'
        self.values[ self.MODE ] = '1'
        self.values[ self.MODE_RANK ] = '10'
        self.values[ self.ADDITIONAL_MACHINE ] = 'False'
        self.values[ self.PROCESS_SEQUENCE ] = '1'
        self.values[ self.LEN_UTR ] = '0'
        self.values[ self.LEN_DTR ] = '30'
        self.values[ self.NUCLEOTIDES ] = 'A, T, G, C'
        self.values[ self.TRIM_SEQUENCE ] = '1'
        self.values[ self.TRIM_UTR_LEN ] ='100'
        self.values[ self.TRIM_CDS_LEN ] ='200'
        self.values[ self.PERL_INSTALLED ] ='True'
        self.values[ self.SMTP_SERVER ] = 'localhost'
        self.values[ self.SMTP_PORT ] = '25'
        self.values[ self.EMAIL_SENDER ] = 'rbsdesigner@localhost'
        
        self.load( self.CONFIG_FILE )
    
    def getThreadNumberPerSequence(self):
        return eval (self.values[ self.THREAD_PER_SEQUENCE ] )

    def getUTRLength(self):
        return eval( self.values[ self.LEN_UTR ] )
    
    def getDTRLength(self):
        return eval( self.values[ self.LEN_DTR] )
    
    def getSDEnergyFile(self):
        return self.values[ self.SD_ENERGY_FILE ]
    
    def getSDHybridizingProgram(self):
        return eval( self.values[ self.SD_ENERGY_PROGRAM ] )
    

    
    def getProcessSequenceOrNot(self):
        if self.values[ self.PROCESS_SEQUENCE ] == '1':
            return True
        else:
            return False
    
    def getPerlInstalledOrNot(self):
        if self.values[ self.PERL_INSTALLED ].upper()=='TRUE':
            return True
        else:
            return False
        
    def getNucleotidesSmall(self):
        x = self.values[ self.NUCLEOTIDES ].split(',')
        r = []
        for i in x:
            r.append( i.strip().lower() )
        return r
        
    def getTrimSequenceOrNot(self):
        if self.values[ self.TRIM_SEQUENCE ] =='1':
            return True
        else:
            return False
        
    def getTrimUTRLength(self):
        return eval(self.values[ self.TRIM_UTR_LEN ] )
    
    def getTrimCDSLength(self):
        return eval( self.values[ self.TRIM_CDS_LEN] )
    
    def getNucleotidesLarge(self):
        x = self.values[ self.NUCLEOTIDES ].split(',')
        r = []
        for i in x:
            r.append( i.strip().upper() )
        return r
        
    def addKeyNValue(self, k, v):
        self.values[ k ] = v
        
    def getHostName(self):
        return self.values[ self.host ]
    
    def getCPU(self):
        return eval( self.values[ self.CPU ] )
    
    def getPassword(self):
        return self.values[ self.passwd ]
    
    def getDebugOrNot(self):
        return eval( self.values[ self.DEBUG ] )
    
    def getUserName(self):
        return self.values[ self.user ]
    
    def getDBName(self):
        return self.values[ self.db ]
    
    def getTableName(self):
        return self.values[ self.table]
    
    def getIncludeSD(self):
        if self.values[ self.INCLUDE_SD ]:
            return 1
        else:
            return 0

    def getRBSdesignerFolder(self):
        return self.values[ self.RBSDESIGNER_FOLDER ]
    
    def getMode(self):
        return eval( self.values[ self.MODE ]  )
    
    def getTrial(self):
        return eval ( self.values[ self.TRIAL] )
    
    def getModeRank(self):
        return eval( self.values[ self.MODE_RANK] )
    
    def getAdditionalMachineOrNot(self):
        return eval( self.values[ self.ADDITIONAL_MACHINE ] )
    
    def getSMTPHost(self):
        return self.values[ self.SMTP_SERVER ]
    
    def getSMTPPort(self):
        return eval( self.values[ self.SMTP_PORT ] )
    
    def getEmailSender(self):
        return self.values[ self.EMAIL_SENDER ]
    
    def load(self, ffile):
        
        #global abs_path
        
        try:
            
            if os.path.exists(ffile):
                #f = open( os.path.join( abs_path, ffile ) )
                f=open(ffile,'r')
                
                for s in f.readlines():
                    
                    s = s.replace('\n','').strip()
                    
                    if len(s)>0:
                        
                        if s[0] != '#':
                        
                            x = s.split('=')
                            
                            if len(x)==2:
                                
                                key = x[0].strip().upper()
                                v = x[1].strip()
                                
                                self.addKeyNValue(key, v)
                
                f.close()
        
        except Exception, ex:
            log('Error in CONFIG class : ' + repr(ex) )
            
            
            
def getHtmlForShow(binfo, structure_info, comment):
    
    ninfo = BASIC_INFO()
    ninfo = binfo
    
    
    id = ninfo.getID()
    score = ninfo.getScore()
    conf_score = ninfo.getConfidenceScore()
    status = ninfo.getStatus()
    email = ninfo.getEmail()
    seq_name = ninfo.getSequenceName()
    date_submitted = ninfo.getDateSubmitted()
    date_finished = ninfo.getDateFinished()
    
    query_seq = ninfo.getQuerySequence()
    utr = ninfo.getUTRsequence()
    cds = ninfo.getCDS()
    opt_seq = ninfo.getOptimizedSequence()
    manual_input_or_not = ninfo.getManualInputOrNot()
    optimize_codon_or_not_str = 'YES'
    if ninfo.getOptimizeCodonOrNot()==0:
        optimize_codon_or_not_str = 'NO'
    target_score = ninfo.getTargetScore()
    
    sd_loc = ninfo.getSDStartPositionIndex()
    sd_len = ninfo.getSDLength()
    
    
    
    '''
    comment = ''
    if score >= 0.01:
        comment = 'This optimized sequence would be definitely over-expressed'
    elif score >= 1e-4:
        comment = 'This optimized sequence would be well-expressed'
    elif score >= 1e-6:
        comment = 'This optimized sequence would not be expressed well'
    elif score == -1:
        comment = ''
    else:
        comment = "This sequence failed for optimization.<br>Please resubmit manually.<br>Please see the document for manual input."
    '''
    
    if status == STATUS_RUNNING:
        status = '<font color = #FF0033>'+ status + '</font>'
        pass
    elif status == STATUS_QUEUE:
        status = '<font color = #CCCCCC>' + status + '</font>'
        pass
    elif status == STATUS_DONE:
        pass
    
            
    info = ''
    info = info + '<table style=border-collapse:collapse; cellpadding=3 border = 2 bordercolor=#6699CC frame=hsides  rules=rows>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Job ID</b></td><td>' + id + '</td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Status</b></td><td><b>' + status + '</b></td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Email</b></td><td><i>' + email + '</i></td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Sequence Name</b></td><td><b>'+seq_name+'</b></td></tr>'
    info = info +  "<tr><td align=CENTER bgcolor=#CCCCFF><b>Optimize 5' codons</b></td><td><b>"+optimize_codon_or_not_str+"</b></td></tr>"
    
    
    
    if score != -1:
        info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Score</b></td><td><font color = #336699>' + str(score) +'</font></td></tr>'
    else:
        info = info + '</tr><td align=CENTER bgcolor=#CCCCFF><b>Score</b></td><td>' + '' +'</td></tr>'
        
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Target score</b></td><td>' + str( target_score ) + '</td></tr>'
    
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Confidence score</b></td><td>' + str( conf_score ) + '</td></tr>'
    
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Comment on result<b></td><td>' + comment + '</td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Date Submitted</b></td><td>' + date_submitted + '</td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Date Finished</b></td><td>' + date_finished + '</td></tr>'
    
    
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>SD sequence Location</b></td><td>' + str(sd_loc) + '</td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>SD sequence Length</b></td><td>' + str(sd_len) + '</td></tr>'
    
    if manual_input_or_not==1:
        info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Input Sequence</b><br>(Manual input)</td><td><textarea rows=5 cols=72>' + \
             query_seq + \
             '</textarea></td></tr>'
    else:
        info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Input Sequence</b></td><td><table><tr><td width=148 align=CENTER><b>' + "5' Sequence</b></td><td><textarea rows=1 cols=50 >" + utr + '</textarea></td></tr>'
        info = info + '<tr><td align=CENTER width=148 ><b>CDS</b></td><td><textarea rows=5 cols=50 >'+cds+'</textarea></td></tr>'
        info = info + '<tr><td align=CENTER width=148 ><b>Input for RBS designer</b></td><td><textarea rows=5 cols=50 >'+ query_seq + '</textarea></td></tr></table>'
    
    

    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Optimized sequence<br>(Partial)</b></td><td><textarea rows=10 cols=72 >'+ opt_seq + '</textarea></td></tr>'
    
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Predicted structures</b></td><td>' + structure_info+ '</td></tr>'
    
    info = info + '</table>'
    
    return info
 


def getHtmlForShow2(binfo, x_info):
    
    ninfo = BASIC_INFO()
    ninfo = binfo
    
    
    id = ninfo.getID()
    score = ninfo.getScore()
    conf_score = ninfo.getAveragedConfidenceScore()
    status = ninfo.getStatus()
    email = ninfo.getEmail()
    seq_name = ninfo.getSequenceName()
    date_submitted = ninfo.getDateSubmitted()
    date_finished = ninfo.getDateFinished()
    
    query_seq = ninfo.getQuerySequence()
    utr = ninfo.getUTRsequence()
    cds = ninfo.getCDS()
    opt_seq = ninfo.getOptimizedSequence()
    manual_input_or_not = ninfo.getManualInputOrNot()
    optimize_codon_or_not_str = 'YES'
    if ninfo.getOptimizeCodonOrNot()==0:
        optimize_codon_or_not_str = 'NO'
    target_score = ninfo.getTargetScore()
    
    sd_loc = ninfo.getSDStartPositionIndex()
    sd_len = ninfo.getSDLength()
    
    
    if status == STATUS_RUNNING:
        status = '<font color = #FF0033>'+ status + '</font>'
        pass
    elif status == STATUS_QUEUE:
        status = '<font color = #CCCCCC>' + status + '</font>'
        pass
    elif status == STATUS_DONE:
        pass
    
            
    info = ''
    info = info + '<table style=border-collapse:collapse; cellpadding=3 border = 2 bordercolor=#6699CC frame=hsides  rules=rows>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Job ID</b></td><td>' + id + '</td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Status</b></td><td><b>' + status + '</b></td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Email</b></td><td><i>' + email + '</i></td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Sequence Name</b></td><td><b>'+seq_name+'</b></td></tr>'
    #info = info +  "<tr><td align=CENTER bgcolor=#CCCCFF><b>Optimize 5' codons</b></td><td><b>"+optimize_codon_or_not_str+"</b></td></tr>"
        
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Target score</b></td><td>' + str( target_score ) + '</td></tr>'

    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Date Submitted</b></td><td>' + date_submitted + '</td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Date Finished</b></td><td>' + date_finished + '</td></tr>'
    
    
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>SD sequence Location</b></td><td>' + str(sd_loc) + '</td></tr>'
    info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>SD sequence Length</b></td><td>' + str(sd_len) + '</td></tr>'
    
    if manual_input_or_not==1:
        info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Input Sequence</b><br>(Manual input)</td><td><textarea rows=5 cols=72>' + \
             query_seq + \
             '</textarea></td></tr>'
    else:
        info = info + '<tr><td align=CENTER bgcolor=#CCCCFF><b>Input Sequence</b></td><td><table><tr><td width=148 align=CENTER><b>' + "5' Sequence</b></td><td><textarea rows=1 cols=50 >" + utr + '</textarea></td></tr>'
        info = info + '<tr><td align=CENTER width=148 ><b>Coding Sequence</b></td><td><textarea rows=5 cols=50 >'+cds+'</textarea></td></tr>'
        #info = info + '<tr><td align=CENTER width=148 ><b>Input for RBS designer</b></td><td><textarea rows=5 cols=50 >'+ query_seq + '</textarea></td></tr></table>'
    
    info = info + '</table><br>'
    info = info + x_info
    
    
    
    return info

class DBConnection:
    
    
    db_conn = None
    db_cursor = None
    db_conf = CONFIG()
    
    def __init__(self):
        pass
    
    def connect(self, config):
        
        self.db_conf = config
        self.db_conn = MySQLdb.connect( host = config.getHostName(), user = config.getUserName(), passwd = config.getPassword(), db=config.getDBName() )
        self.db_cursor = self.db_conn.cursor()
    
    def __getPercent(self, num):
        s = ''
        
        for i in range(num):
            
            if len(s)>0:
                s = s + ','
            
            s = s + '"%s"'
            
        return s
    
    def insert(self, info_class):
        
        global MYSQL_BUG_FIXED
        
        o = BASIC_INFO()
        o = info_class
        
        #print '#' + str(  o.getFindSD() )
        #print '$', str(o.getATGIndex() )
        
        
        #print o.toString()
        
        '''
        st = 'insert into ' + self.db_conf.getTableName() + \
           ' (' + TABLE_ID + ', ' + \
           TABLE_EMAIL + ',' + \
           TABLE_SEQ_NAME + ',' + \
           TABLE_DATE_SUBMITTED + ',' + \
           TABLE_INFO + ',' + \
           TABLE_MANUAL_INPUT_OR_NOT + ',' + \
           TABLE_CDS + ',' + \
           TABLE_UTR + ',' + \
           TABLE_TRIAL + ',' + \
           TABLE_SD_START_INDEX + ',' + \
           TABLE_SD_LENGTH + ',' + \
           TABLE_PROB_METHOD + ',' + \
           TABLE_SPACER_LENGTH + ',' + \
           TABLE_SPACER_RANGE + ',' + \
           TABLE_TARGET_SCORES +',' + \
           TABLE_SD_SEQUENCE + ',' + \
           TABLE_aSD_SEQUENCE + ',' + \
           TABLE_ATG_INDEX + ',' + \
           TABLE_FIND_SD + \
           ') VALUES(  ' +  self.__getPercent(19)   +   ' )'  % \
           ( o.getID() , o.getEmail() , o.getSequenceName() , \
             o.getDateSubmitted(),  o.getInfo(), \
             o.getManualInputOrNot(), o.getCDSSequence(), \
             o.getUTRsequence(), str(o.getTrial()), \
             str(o.getSDStartPositionIndex()), str(o.getSDLength()) , \
             o.getProbMethod(), str (o.getSpacerLength() ) ,\
             str( o.getSpacerRange() ) , o.getTargetTempAndScores() , \
             o.getSDSequence(), o.getAntiSDSequence(), \
             str( o.getATGIndex()) , str(o.getFindSD() ) )
        '''
        
        st = 'insert into ' + self.db_conf.getTableName() + \
           ' (' + TABLE_ID + ', ' + \
           TABLE_EMAIL + ',' + \
           TABLE_SEQ_NAME + ',' + \
           TABLE_DATE_SUBMITTED + ',' + \
           TABLE_INFO + ',' + \
           TABLE_MANUAL_INPUT_OR_NOT + ',' + \
           TABLE_CDS + ',' + \
           TABLE_UTR + ',' + \
           TABLE_TRIAL + ',' + \
           TABLE_SD_START_INDEX + ',' + \
           TABLE_SD_LENGTH + ',' + \
           TABLE_PROB_METHOD + ',' + \
           TABLE_SPACER_LENGTH + ',' + \
           TABLE_SPACER_RANGE + ',' + \
           TABLE_TARGET_SCORES +',' + \
           TABLE_SD_SEQUENCE + ',' + \
           TABLE_aSD_SEQUENCE + ',' + \
           TABLE_ATG_INDEX + ',' + \
           TABLE_FIND_SD + ',' + \
           TABLE_STOP_CODON + \
           ') VALUES(  ' 
        
        
        st = st + '"' + o.getID() + '",' 
        st = st + '"' + o.getEmail() + '",' 
        st = st + '"' + o.getSequenceName() + '",' 
        st = st + '"' + o.getDateSubmitted() + '",' 
        st = st + '"' + o.getInfo()+ '",' 
        st = st + '"' + str(o.getManualInputOrNot()) + '",' 
        st = st + '"' + o.getCDSSequence() + '",' 
        st = st + '"' + o.getUTRsequence() + '",' 
        st = st + '"' + str(o.getTrial()) + '",' 
        st = st + '"' + str(o.getSDStartPositionIndex()) + '",' 
        st = st + '"' + str(o.getSDLength()) + '",' 
        st = st + '"' + o.getProbMethod() + '",' 
        st = st + '"' + str(o.getSpacerLength() )+ '",' 
        st = st + '"' + str(o.getSpacerRange() ) + '",' 
        st = st + '"' + o.getTargetTempAndScores() + '",' 
        st = st + '"' + o.getSDSequence() + '",' 
        st = st + '"' + o.getAntiSDSequence() + '",' 
        st = st + '"' + str( o.getATGIndex())  + '",' 
        st = st + '"' + str(o.getFindSD() ) + '",'  
        st = st + '"' + o.getStopCodon( ) + '"'  
        st = st +         ' )'  

        #print st
        
        
        self.db_cursor.execute(st)
        
        # ----------------------------------------------------------------------------------------
        if not MYSQL_BUG_FIXED:
            # since this version of mysqldb does not store long texts, info data is stored as a file.
            id_path = config.getRBSdesignerFolder() + '/data/' + o.getID()
            self.makeFolder(id_path)
            
            file = config.getRBSdesignerFolder() + '/data/' + o.getID() + '/info.txt'  
            f = open(file,'w')
            f.write( o.getInfo() )            
            f.close()
    
            
    def makeFolder(self, path):
        # if folder does not exist, make it.
        if not os.path.exists( path ):
            os.mkdir( path )
            
        
    def update(self, info_class, id):
        
        o = BASIC_INFO()
        o = info_class
        
        global MYSQL_BUG_FIXED
        
        # MySQL TEXT  info   .
        #   . ID...
        
        if MYSQL_BUG_FIXED:
            # TABLE_OPTIMIZED_SEQUENCE + ' = "'  + o.getOptimizedSequence()  + '", ' + \

            st = 'UPDATE ' + self.db_conf.getTableName() + \
               ' SET ' + \
               TABLE_STATUS + ' = " ' + STATUS_DONE + '" , ' + \
               TABLE_DATE_FINISHED + ' = "'  +  o.getDateFinished()  +   '", ' + \
               TABLE_INFO + ' = "'  + o.getInfo()  +  '"' + \
               TABLE_TRIAL + ' = ' + str(o.getTrial() ) + \
               ' WHERE ' + TABLE_ID + ' = "'  + id +   '"' 
            
            
            #log(st)
            self.db_cursor.execute(st)

        else:
            # -------------------------------------------------------------------------------------------
            #print 'opt = ', o.getOptimizedSequence()
            #print 'trial = ', o.getTrial()
            #print 'id = ', id
            
            st = 'UPDATE ' + self.db_conf.getTableName() + \
               ' SET ' + \
               TABLE_STATUS + ' = " ' + STATUS_DONE + '" , ' + \
               TABLE_OPTIMIZED_SEQUENCE + ' = "'  + o.getOptimizedSequence()  + '", ' + \
               TABLE_DATE_FINISHED + ' = "'  +  o.getDateFinished()  +   '", ' + \
               TABLE_TRIAL + ' = ' + str(o.getTrial() ) + \
               ' WHERE ' + TABLE_ID + ' = "'  + id +   '"' 
            
            #log(st)
            self.db_cursor.execute(st)
            
            #   .
            self.makeFolder( config.getRBSdesignerFolder() + '/data/' + id ) 
            
            # since this version of mysqldb does not store long texts, info data is stored as a file.
            fi = config.getRBSdesignerFolder() + '/data/' + id + '/info.txt'  
            f = open(fi,'w')
            f.write( o.getInfo() )
            f.close()
            # --------------------------------------------------------------------------------------------
        
        
        
    def selectAll(self):
        ''' Returns all records '''
        return self.select()
    
    def select(self, id=None, status=None, email = None):
        
        where = ''
        if id != None:
            where = 'ID = "' + id + '"'
        
        if status != None:
            if len(where)>0:
                where = where + ' AND '
            
            where = where + ' STATUS = "' + status + '"'
        
        if email != None:
            if len(where)>0:
                where = where + ' AND '
            where = where + ' EMAIL = "' + email + '"'
        
        st = 'SELECT ' + TABLE_ID + ',' + \
           TABLE_INFO + ',' + \
           TABLE_EMAIL + ',' + \
           TABLE_SEQ_NAME + ',' + \
           TABLE_DATE_SUBMITTED + ',' + \
           TABLE_STATUS + ',' + \
           TABLE_UTR + ',' + \
           TABLE_OPTIMIZED_SEQUENCE + ',' +\
           TABLE_DATE_FINISHED + ',' + \
           TABLE_CDS + ',' + \
           TABLE_MANUAL_INPUT_OR_NOT + ',' +  \
           TABLE_TRIAL + ',' + \
           TABLE_SD_START_INDEX + ',' + \
           TABLE_SD_LENGTH + ',' + \
           TABLE_PROB_METHOD + ',' + \
           TABLE_SPACER_LENGTH + ',' + \
           TABLE_SPACER_RANGE + ',' + \
           TABLE_TARGET_SCORES + ',' + \
           TABLE_aSD_SEQUENCE + ',' + \
           TABLE_SD_SEQUENCE + ',' + \
           TABLE_ATG_INDEX + ',' + \
           TABLE_FIND_SD +',' +  \
           TABLE_STOP_CODON + \
           '  FROM ' +  self.db_conf.getTableName() 
        
        
        
        if len(where)>0:
            st = st + ' WHERE ' + where
            
        st = st + ' ORDER BY ' + TABLE_DATE_SUBMITTED + ' DESC'
       
        #log(st)
 
        self.db_cursor.execute(st)
        
        ret = []
        results = self.db_cursor.fetchall()
        
        
        
        
        for r in results:
            
            #print repr(r)
            
            binfo = BASIC_INFO()
            binfo.setID( r[0] )
            binfo.setInfo( r[1] )
            binfo.setEmail( r[2] )
            binfo.setSequenceName( r[3] )
            binfo.setDateSubmitted( r[4] )
            binfo.setStatus( r[5] )
            binfo.setUTRsequence( r[6] )
            binfo.setOptimizedSequence( r[7] )
            binfo.setDateFinished( r[8] )
            binfo.setCDSSequence( r[9] )
            binfo.setManualInputOrNot( eval(r[10]) )
            binfo.setTrial(  eval(r[11])  )

            binfo.setSDStartPositionIndex( eval( r[12] ) )
            binfo.setSDLength( eval( r[13] ) )
            
            binfo.setProbMethod( r[14] )
            binfo.setSpacerLength( eval( r[15] ) )
            binfo.setSpacerRange( eval( r[16] ) )
            
            binfo.setTargetTempAndScores( r[17] )
            binfo.setAntiSDSequence( r[18] )
            
            binfo.setSDSequence( r[19] )
            binfo.setATGIndex( eval(r[20] ))
            binfo.setFindSD( eval(r[21] ) )
            binfo.setStopCodon( r[22] )

            ret.append(binfo)
            
            #print '>>',r[6]
            #print '>>',r[9]
        
        # MYSQL_BUG_FIX probelm ----------------------------------------------------------------
        global MYSQL_BUG_FIXED
        
        if not MYSQL_BUG_FIXED:
            
            if id != None:
                file = config.getRBSdesignerFolder() + '/data/'+id+'/info.txt'
                #file = config.getRBSdesignerFolder() + '/data/'+id+'.txt'
                
                if os.path.exists(file):
                    r = ''
                    f = open(file,'r')
                    for x in f.readlines():
                        r = r + x
                    f.close()
                    
                    binfo.setInfo(r)
        
        #-----------------------------------------------------------------------------------------
        
        return ret
    
    
    def getQueuedJobs(self):
        return self.select( status =   STATUS_QUEUE)
    
    def getRunningJobs(self):
        return self.select( status = STATUS_RUNNING )
    
    def getDoneJobs(self):
        return self.select( status = STATUS_DONE )
    
    def close(self):
        self.db_conn.close()
        
    def changeStatus(self, id, status):
        
        st = 'UPDATE ' + self.db_conf.getTableName() + ' SET ' + TABLE_STATUS + ' = "' + status + '" WHERE ' + TABLE_ID + ' = "' + id + '"'
        self.db_cursor.execute(st)
    
        
    def delete(self, id):
        
        st = 'DELETE from ' + self.db_conf.getTableName() + ' WHERE ' + TABLE_ID + ' = "' + id + '"' 
        self.db_cursor.execute(st)
        


# COMMON METHODS=============================================
def extendString( alignment = 'LEFT', width = 20, msg = ''):
    
    ret = ''
    
    
    if len(msg)>0 and len(msg)  < width:
        
        space = width - len(msg)
        
        if alignment == 'LEFT':
            ret = msg +( ' ' * space)
        elif alignment == 'CENTER':
            
            left_spae = int( space / 2.0 )
            right_space = space - left_spae
            
            ret = (' ' * left_spae ) + msg + ( ' ' * right_space )
            
        else:
            ret = (' ' * spae) + msg 
        
    else:
        ret = msg
    
    return ret


def getTimeAsString():
    
    import time
    year, month, day, hr, min, sec, x, y, z = time.gmtime()
    s = ("%2d/%2d/%4d %2d:%2d:%2d" % (year, month, day, hr, min, sec )).strip()
    return s

def parseDateRecord(date):
    
    date = date.strip()
    
    #if len(date)>0:
    x = date.split('/')
    year = eval(x[0])
    month = eval(x[1])
    
    y = x[2][ : 4]
    day = eval(y)
    
    z = x[2][4:].strip().split(':')
    hr= eval(z[0])
    min = eval(z[1])
    sec = eval(z[2])
    
    return year, month, day, hr, min, sec
    #else:
    #    return 0,0,0,0,0,0

def isNumeric( st ):
    
    try:
        x = eval(st)
        return True
    except:
        return False
    
    
    
def getFileAsOneString(ffile):
    
    s = ''
    
    f = open ( ffile, 'r' )
    
    for sx in f.readlines():
        s = s + sx
        
        
    f.close()
    
    return s



def transformRawScore(score):
    
    if score == 0 or score == -1:
        return INF
    else:
        return math.log10(score)
        

    
    
    
def clearSequence(seq):
    
    NT = [ 'A', 'T', 'U', 'G', 'C' , '.', '*', '/', 'D', 'E' , 'F', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'V', 'W', 'Y']
    
    n_seq = ''
    for c in seq:
        if c.upper() in NT:
            n_seq=n_seq+c
    return n_seq
    


# -------------------------------------------------------
config=CONFIG()


def initlog():
    
    if config.getDebugOrNot():
        f = open(LOG_FILE, 'w')
        f.close()
    

def log(msg):

    return

    
    #if config.getDebugOrNot():
    if True:
    
        trx = 0
        
        #print msg
        
        while(trx<5):
            try:
                f = open(LOG_FILE, 'a')
                x = time.ctime()
                f.write(x + '\t' + msg + '\n')
                f.close()
                return
            except:
                time.sleep(1)
                trx=trx+1
         
