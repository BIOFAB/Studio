package org.biofab.studio.canvas.part.refiner;

import java.util.Hashtable;

import org.biojavax.SimpleComment;
import org.biojavax.bio.seq.RichSequence;

public class BBFTwentyFiveController extends RefinementController
{

    public BBFTwentyFiveController()
    {
        super();

        _standardName = "Biobrick Foundation Assembly Standard 25"; 
        _isCodingRegion = true;
        _refinementOK = true;

        _sites = new Hashtable<String, String>();
        _sites.put("EcoRI", "GAATTC");
        _sites.put("XbaI", "TCTAGA");
        _sites.put("SpeI", "ACTAGT");
        _sites.put("PstI", "CTGCAG");
        _sites.put("NotI", "GCGGCCGC");
        _sites.put("AgeI", "ACCGGT");
        _sites.put("NgoMIV", "GCCGGC");

        _prefix = new String("GAATTCCGCGGCCGCTTCTAGATGGCCGGC");
        _suffix = new String("ACCGGTTAATACTAGTAGCGGCCGCTGCAG");
        
    }

    @Override
    public RichSequence refine(RichSequence seq)
    {
        _start = 1;
        _end = seq.length();
        _isCodingRegion = true;
        _refinementOK = true;
        _seq = RichSequence.Tools.createRichSequence(seq.getName() + "_refined", seq.subList(1, seq.length()));

        if(checkPrefixAndSuffix() == false) {
            return null;
        }

        if (_refinementOK)
        {
            removeRestrictionSites();
        }
       
        if (_refinementOK)
        {
            addSuffix();
        }
        
        if (_refinementOK)
        {
            addPrefix();
        }
       
        generateComment();

        return _seq;
    }
}
