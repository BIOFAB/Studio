//
//  BBFTenController.java
//  BIOFAB Sequence Refiner
//
//  Created by Cesar A. Rodriguez
//
//  Contributions by Alexander Castro and David Sachs
//
//  Copyright 2010 University of California at Berkeley. All rights reserved.
//

package org.biofab.studio.canvas.part.refiner;

import java.util.*;

import org.biojavax.SimpleComment;
import org.biojavax.bio.seq.*;

public class BBFTenController extends RefinementController
{
    protected Boolean _nonCodingPrefix;

    BBFTenController()
    {
        super();

        _standardName = "Biobrick Foundation Assembly Standard 10"; 
        _isCodingRegion = true;
        _refinementOK = true;

        _sites = new Hashtable<String, String>();
        _sites.put("EcoRI", "GAATTC");
        _sites.put("XbaI", "TCTAGA");
        _sites.put("SpeI", "ACTAGT");
        _sites.put("PstI", "CTGCAG");
        _sites.put("NotI", "GCGGCCGC");

        _suffix = new String("TACTAGTAGCGGCCGCTGCAG");
        _prefix = new String("GAATTCGCGGCCGCTTCTAG");

    }

    public RichSequence refine(RichSequence seq)
    {
        _start = 1;
        _end = seq.length();
        _isCodingRegion = true;
        _refinementOK = true;
        _seq = RichSequence.Tools.createRichSequence(seq.getName() + "_refined", seq.subList(1, seq.length()));

        // this.determineCodingRegion()

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

    // protected function determineCodingRegion():void
    // {
    // if(_window.isCodingRegionCheckbox.selected == true)
    // {
    // _isCodingRegion = true;
    // }
    // else
    // {
    // _isCodingRegion = false;
    // }
    // }

   

    // protected function checkStartCodon():void
    // {
    //			
    // }

    
// protected function mutate(siteName:String, site:String,
    // position:uint):void
    // {
    // var randomIndex:uint;
    // var feature:Feature = new Feature();
    // var nucleotides:Array = ["A", "G", "T", "C"];
    // var mutatedSite:Array = new Array(site.length);
    //			
    // for(var i:uint = 0; i < site.length; ++i)
    // {
    // mutatedSite.push(site.charAt(i));
    // }
    //			
    // while(mutatedSite.toString() == site)
    // {
    // randomIndex = Math.round((Math.random() * 1000)) % site.length;
    // mutatedSite = site.r
    // }
    //			
    // _featuredSequence.insertSequence(new DNASequence(mutatedSite, false),
    // position - 1, false);
    // _featuredSequence.removeSequence(position + site.length - 1, position +
    // site.length - 1 + site.length, false);
    //									
    // //Add Feature
    // feature = new Feature();
    // feature.strand = Feature.POSITIVE;
    // feature.type = "misc_feature";
    // feature.start = position - 1;
    // feature.end = position + site.length - 2;
    // feature.notes = new Array();
    // feature.notes.push(new FeatureNote("label", "Prior "+ siteName +
    // " site"));
    // _featuredSequence.addFeature(feature,false);
    // }
}