'''
Created on Oct 2, 2010

@author: Quintara 
'''
#!python

# User Manual
#
# Conversion of ABIF data types to Python types (see struct.unpack method):
# type 1 = byte -> integer
# type 2 = char -> string
# type 3 = word -> long
# type 4 = short -> integer
# type 5 = long -> integer
# type 7 = float -> float
# type 8 = double -> float
# type 10 = date -> datetime.date instance
# type 11 = time -> datetime.time instance
# type 12 = thumb -> tuple
# type 13 = bool -> True or False
# type 18 = pString -> string
# type 19 = cString -> string
# type = 1024+ = user -> NotImplemented: to be overwritten in user's code in ABIFReader.readNextUserData method
# type = other -> NotImplemented
#
# from ABIFReader import *
# reader = ABIFReader(<filename>) # creates an instance of ABIFReader
# reader.version # version of ABIF file
# reader.showEntries() # print all entries of ABIF file "<name> (<num>) / <type> (<size>)"
# data = reader.getData(<name>[, <num>]) # read data for entry named <name> with number <num>, by default <num> is 1
# reader.close() # close the file, since it is kept open
#

import struct, sys
import datetime

ABIF_TYPES = {1: 'byte', 2: 'char', 3: 'word', 4: 'short', 5: 'long', 7: 'float', 8: 'double',\
        10: 'date', 11: 'time', 12: 'thumb', 13: 'bool', 18: 'pString', 19: 'cString'}

class ABIFReader:
    def __init__(self, fn):
        self.filename = fn
        self.file = open(fn, 'rb')
        self.type = self.readNextString(4)
        if self.type != 'ABIF':
            self.close()
            raise SystemExit("error: No ABIF file '%s'" % fn)
        self.version = self.readNextShort()
        dir = DirEntry(self)
        self.seek(dir.dataoffset)
        self.entries = [DirEntry(self) for i in range(dir.numelements)]

    def getData(self, name, num = 1):
        entry = self.getEntry(name, num)
        if not entry:
            raise SystemExit("error: Entry '%s (%i)' not found in '%s'" % (name, num, self.filename))
        self.seek(entry.mydataoffset())
        data = self.readData(entry.elementtype, entry.numelements)
        if data != NotImplemented and len(data) == 1:
            return data[0]
        else:
            return data

    def showEntries(self):
        print 'NAME (NUMBER) / TYPE (NUMBER_OF_ELEMENTS)'
        for e in self.entries:
            print e

    def getEntry(self, name, num):
        for e in self.entries:
            if e.name == name and e.number == num:
                return e
        return None

    def readData(self, type, num):
        if type == 1:
            return [self.readNextByte() for i in range(num)]
        elif type == 2:
            return self.readNextString(num)
        elif type == 3:
            return [self.readNextUnsignedInt() for i in range(num)]
        elif type == 4:
            return [self.readNextShort() for i in range(num)]
        elif type == 5:
            return [self.readNextLong() for i in range(num)]
        elif type == 7:
            return [self.readNextFloat() for i in range(num)]
        elif type == 8:
            return [self.readNextDouble() for i in range(num)]
        elif type == 10:
            return [self.readNextDate() for i in range(num)]
        elif type == 11:
            return [self.readNextTime() for i in range(num)]
        elif type == 12:
            return [self.readNextThumb() for i in range(num)]
        elif type == 13:
            return [self.readNextBool() for i in range(num)]
        elif type == 18:
            return self.readNextpString()
        elif type == 19:
            return self.readNextcString()
        elif type >= 1024:
            return self.readNextUserData(type, num)
        else:
            return NotImplemented

    def readNextBool(self):
        return readNextByte(self) == 1

    def readNextByte(self):
        return self.primUnpack('B', 1)

    def readNextChar(self):
        return self.primUnpack('c', 1)

    def readNextcString(self):
        chars = []
        while True:
            c = self.readNextChar()
            if ord(c) == 0:
                return ''.join(chars)
            else:
                chars.append(c)

    def readNextDate(self):
        return datetime.date(self.readNextShort(), self.readNextByte(), self.readNextByte())

    def readNextDouble(self):
        return self.primUnpack('>d', 8)

    def readNextInt(self):
        return self.primUnpack('>i', 4)

    def readNextFloat(self):
        return self.primUnpack('>f', 4)

    def readNextLong(self):
        return self.primUnpack('>l', 4)

    def readNextpString(self):
        nb = self.readNextByte()
        chars = [self.readNextChar() for i in range(nb)]
        return ''.join(chars)

    def readNextShort(self):
        return self.primUnpack('>h', 2)

    def readNextString(self, size):
        chars = [self.readNextChar() for i in range(size)]
        return ''.join(chars)
    
    def readNextThumb(self):
        return (self.readNextLong(), self.readNextLong(), self.readNextByte(), self.readNextByte())

    def readNextTime(self):
        return datetime.time(self.readNextByte(), self.readNextByte(), self.readNextByte(), self.readNextByte())

    def readNextUnsignedInt(self):
        return self.primUnpack('>I', 4)
    
    def readNextUserData(self, type, num):
        # to be overwritten in user's code
        return NotImplemented

    def primUnpack(self, format, nb):
        x = struct.unpack(format, self.file.read(nb))
        return x[0]
    
    def close(self):
        self.file.close()

    def seek(self, pos):
        self.file.seek(pos)

    def tell(self):
        return self.file.tell()

class DirEntry:
    def __init__(self, reader):
        self.name = reader.readNextString(4)
        self.number = reader.readNextInt()
        self.elementtype = reader.readNextShort()
        self.elementsize = reader.readNextShort()
        self.numelements = reader.readNextInt()
        self.datasize = reader.readNextInt()
        self.dataoffsetpos = reader.tell()
        self.dataoffset = reader.readNextInt()
        self.datahandle = reader.readNextInt()

    def __str__(self):
        return "name:%s (nubmer:%i) / type:%s (numberelements:%i)" % (self.name, self.number, self.mytype(), self.numelements)

    def mydataoffset(self):
        if self.datasize <= 4:
            return self.dataoffsetpos
        else:
            return self.dataoffset

    def mytype(self):
        if self.elementtype < 1024:
            return ABIF_TYPES.get(self.elementtype, 'unknown')
        else:
            return 'user'

class AB1Seq:
    def __init__(self, ab1file):
        self.reader = ABIFReader(ab1file)
        r = self.reader
        # sequencing plate
        self.plateid = r.getData('CTID', 1)
        # sequence well location
        self.well = r.getData('TUBE', 1)
        # sequencing sample name
        self.samplename = r.getData('SMPL', 1)
        self.signal2noice = r.getData('S/N%',1)

        # list of bases
        self.bases = list(r.getData('PBAS', 1)) # get unedit base

        # get quality values
        e = r.getEntry('PCON', 1) # un-edit value
        r.seek(e.mydataoffset())
        self.quals = [r.readNextByte() for i in range(e.numelements)]

        if len(self.bases) != len(self.quals):
            print "ERROR: ab1 file (%s) parsing error, count of bases != count of quality value" % r.filename
            sys.exit()


    def getSeqInfo(self):
        trimscores, trimbases = self.trim_by_quality()

        avg_trimscore = None
        if trimscores:
            avg_trimscore = sum(trimscores)/len(trimscores)

        trimseq = None
        if trimbases:
            trimseq = "".join(trimbases)

        avg_score = None
        if self.quals:
            avg_score = sum(self.quals)/len(self.quals)

        seq = None
        if self.bases:
            seq = "".join(self.bases)

        return (self.plateid, self.well, self.samplename, self.signal2noice, avg_score, seq, avg_trimscore, trimseq)
    """
    quality_cutoff: the low limit of quality score
    lowquality_base_count:  the number of low quality (<20) bases within a window
    window_size:  default is 20
    trim5 : trim from 5' end
    trim3 : trim from 3' end
    exclude: if set to 1, also remove the part that contains the low quality bases from both ends
    """
    def trim_by_quality(self, quality_cutoff=20, lowquality_base_count=4, window_size=20, trim5=1, trim3=1, exclude=0):
        quals = [x/quality_cutoff for x in self.quals]
        trimstart=0
        trimend = len(self.quals)

        if trim5:
            for i in range(0, len(quals)):
                w_quals = quals[i:i+window_size]
                lowq_count = w_quals.count(0) 
                if lowq_count < lowquality_base_count:
                    if exclude:
                        trimstart = min(len(quals), i+window_size)
                        for j in range(1, len(w_quals)):
                            if w_quals[-j] < 1:
                                trimstart = trimstart-j+1
                                break
                    else:
                        trimstart = i

                    break

        if trim3:
            for i in range(0, len(quals)):
                _3e = len(quals) -i  
                _3s = _3e - window_size-1
                w_quals = quals[_3s:_3e]
                lowq_count = w_quals.count(0)
                if lowq_count < lowquality_base_count:
                    if exclude:
                        trimend = _3s
                        for j in range(0, len(w_quals)):
                            if w_quals[j] < 1:
                                trimend = trimend+j
                                break
                    else:
                        trimend = _3e
                    break
        trimbases = self.bases[trimstart:trimend]
        trimscores = self.quals[trimstart:trimend]
        return (trimscores, trimbases)

    def fasta(self):
        return """>%s,%sbp\n%s""" % (self.reader.filename,len(self.bases), "".join(self.bases) )
        
    def trim_fasta(self, quality_cutoff=20, lowquality_base_count=4, window_size=20, trim5=1, trim3=1, exclude=0):
        trimscores, trimbases = self.trim_by_quality(quality_cutoff=quality_cutoff, lowquality_base_count=lowquality_base_count,\
                window_size=window_size, trim5=trim5, trim3=trim3, exclude=exclude)

        if len(trimbases) == 0:
            return None
        return """>%s,%sbp,trimmed\n%s""" % (self.reader.filename,len(trimbases), "".join(trimbases) )

def test(f):
    s = AB1Seq(f)
    print "----------- Fasta Seqeucne -------------"
    print s.fasta()
    print "----------- Trimmed Fasta Seqeucne 1-------------"
    print s.trim_fasta()
    print "----------- Trimmed Fasta Seqeucne 2-------------"
    print s.trim_fasta(exclude=1, quality_cutoff=50, lowquality_base_count=5, window_size=10)

    #plateid, well, samplename, signal2noice[G,A,T,C], avg_score, seq, avg_trimscore, trimseq
    print "--- plateid, well, samplename, signal2noice[G,A,T,C], avg_score, seq, avg_trimscore, trimseq ---"
    print s.getSeqInfo()

def get_trim(f, quality_cutoff=30, lowquality_base_count=2, window_size=10, trim5=1, trim3=1, exclude=1):
    s = AB1Seq(f)
    return s.trim_by_quality(quality_cutoff, lowquality_base_count, window_size, trim5, trim3, exclude)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: %s <ab1 file>" % sys.argv[0]
        print "This script convert a AB1 file to a fasta sequence"
        sys.exit()
    test(sys.argv[1])
