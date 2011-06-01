'''
Created on Mar 25, 2011

@author: cambray
'''

from string import maketrans

def complement(seq_list):
    if seq_list.__class__ == list:
        for i in range(len(seq_list)):
            seq_list[i] = seq_list[i].translate(maketrans('atgcATGC', 'tacgTACG'))
        return seq_list
    elif seq_list.__class__ == str:
        return seq_list.translate(maketrans('atgcATGC', 'tacgTACG'))

def reverse(seq_list):
    if seq_list.__class__ == list:
        for i in range(len(seq_list)):
            seq_list[i] = seq_list[i][::-1]
        return seq_list
    elif seq_list.__class__ == str:
        return seq_list[::-1]

def revcomp(seq_list):
    seq_list = complement(seq_list)
    seq_list = reverse(seq_list)
    return seq_list

def primerize(seq_list, overhang5, overhang3, blunt=True):
    overhang5 = overhang5.lower()
    overhang3 = revcomp(overhang3.lower())
    if blunt:
        fw_primers = ['%s%s%s' % (overhang5,seq,revcomp(overhang3)) for seq in seq_list]
        rv_primers = ['%s%s%s' % (overhang3,seq,revcomp(overhang5)) for seq in revcomp(seq_list[:])]
    else:
        fw_primers = ['%s%s' % (overhang5,seq) for seq in seq_list]
        rv_primers = ['%s%s' % (overhang3,seq) for seq in revcomp(seq_list[:])]
    return fw_primers, rv_primers

def primerize_w_extension():
    input = '../Data/try'
    prime_fw = 'ggcgtgagaccTGTGCCAGTCTCCGTTATCG'
    prime_rw = 'atcatgagaccTGCACCACCGGGTAAAGTTC'
    names = []
    seq_rw = []
    seq_fw = []
    h = open(input)
    for l in h:
        l = l.strip()
        name, seqr, seqf = l.split(',')
        names.append(name)
        seq_rw.append(seqr)
        seq_fw.append(seqf)
    h.close()
    fab=1015
    for i in range(len(names)):
        print "oFAB%s_%s_fw\t%s%s" % (fab,names[i], seq_fw[i].upper(), prime_fw)
        fab+=1
        print "oFAB%s_%s_rw\t%s%s" % (fab,names[i], revcomp(seq_rw[i].upper()), prime_rw)
        fab+=1

if __name__ == '__main__':
    input = '../Data/try'
    prime_fw = 'ggcgtgagaccTGTGCCAGTCTCCGTTATCG'
    prime_rw = 'atcatgagaccTGCACCACCGGGTAAAGTTC'
    names = []
    seqs = []
    h = open(input)
    for l in h:
        l = l.strip()
        name, seq = l.split('\t')
        names.append(name)
        seqs.append(seq[:-2])
    h.close()
    id = 1
    fw,rw = primerize(seqs, "TAAC", "GAAC", blunt=False)
    for i in range(len(names)):
        print "P%i_%s_fw\t%s" % (id,names[i], fw[i].upper())
        print "P%i_%s_rw\t%s" % (id,names[i], rw[i].upper())
        id+=1

        