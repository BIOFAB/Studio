//
//  RefinementController.java
//
//  Created by Cesar A. Rodriguez
//
//  Contributions by Alexander Castro and David Sachs
//
//  Copyright 2010 University of California at Berkeley. All rights reserved.
//

package org.biofab.studio.canvas.part.refiner;

import java.util.*;
import org.biojava.bio.BioException;

import org.biojava.bio.seq.*;
import org.biojava.bio.search.*;
import org.biojava.bio.symbol.*;
import org.biojava.bio.dist.*;

import org.biojavax.bio.seq.*;
import org.biojavax.SimpleNote;
import org.biojavax.SimpleRichAnnotation;
import org.biojavax.RichObjectFactory;
import org.biojavax.SimpleComment;


public abstract class RefinementController extends Object
{	
    protected Hashtable<String, String> _sites;
    protected String                    _prefix;
    protected String                    _suffix;
    protected Integer                   _start;
    protected Integer                   _end;
    protected RichSequence              _seq;
    protected Boolean                   _refinementOK;
    protected Boolean                   _isCodingRegion;
    protected Integer                   _frame;
    protected String                    _codonPref;
    protected String                    _standardName;
    protected Integer                   _failCount = 0;
    
    public static String TRNACodonPref = "TRNA";
    public static String RandomCodonPref = "RAND";
		
    //Constructor
    public RefinementController()
    {
       super();
    }
                
    //Public Methods
    public abstract RichSequence refine(RichSequence seq);
    
    //Properties
    public void setCodonPreference(String codonPref)
    {
        if(codonPref != null) 
        {
            if(codonPref.equalsIgnoreCase("TRNA") || codonPref.equalsIgnoreCase("RAND"))
            {
                _codonPref = codonPref.toUpperCase();
            }
        }
        else
        {
            _codonPref = "TRNA";
        }
    }
    
    public String getCodonPreference()
    {
        return _codonPref;
    }

    private int[] findRestrictionSite(String siteSeq, RichSequence theSeq) throws IllegalSymbolException {

        KnuthMorrisPrattSearch  searchEngine;

        searchEngine = new KnuthMorrisPrattSearch(DNATools.createDNA(siteSeq));
        if(theSeq != null) {
            return searchEngine.findMatches(theSeq);
        } else {
            return searchEngine.findMatches(_seq);
        }

    }

    private RichSequence changeCodon(CodonChange change, boolean dryRun) throws IllegalAlphabetException {

        if(!dryRun) {
            System.out.println("Changing codon at " + change.getPosition() + " from " + change.getOldCodon().seqString() + " to " + change.getNewCodon().seqString());
        }

        return changeCodon(change.getPosition(), change.getNewCodon(), dryRun);
    }


    private RichSequence changeCodon(Integer siteStart, SymbolList alternativeCodon, boolean dryRun) throws IllegalAlphabetException {

        Edit edit = null;

        if(_frame == 0)
        {
            edit = new Edit(siteStart, 3, alternativeCodon);
        }

        if(_frame == 1)
        {
            edit = new Edit(siteStart - 1, 3, alternativeCodon);
        }

        if(_frame == 2)
        {
            edit = new Edit(siteStart - 2, 3, alternativeCodon);
        }

        if(dryRun) {
            SymbolList tmpList = _seq.subList(1, _seq.getInternalSymbolList().length()); // copy list
            SimpleRichSequence tmpSeq = new SimpleRichSequence(_seq.getNamespace(), _seq.getName(), _seq.getAccession(), _seq.getVersion(), tmpList, _seq.getSeqVersion()); // copy richsequence
            tmpSeq.edit(edit);
            return tmpSeq;
        } else {
            _seq.edit(edit);
            return _seq;
        }
        

    }

    private void annotateCodonChange(Integer siteStart, Integer siteEnd, String siteName) throws BioException {

        SimpleRichAnnotation annotation = new SimpleRichAnnotation();
        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("label"),"prior " + siteName + " site" ,0));

        StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
        featureTemplate.annotation = annotation;
        featureTemplate.location = new RangeLocation(siteStart,siteEnd);
        featureTemplate.source = "BIOFAB Sequence Refiner";
        featureTemplate.strand = StrandedFeature.POSITIVE;
        featureTemplate.type = "misc_feature";

        _seq.createFeature(featureTemplate);

    }

    private void annotateFailedCodonChange(Integer siteStart, Integer siteEnd, String siteName) throws BioException {

        Integer codonStart = 0;

        if(_frame == 0)
        {
            codonStart = siteStart;
        }

        if(_frame == 1)
        {
            codonStart = siteStart - 1;
        }

        if(_frame == 2)
        {
            codonStart = siteStart - 2;
        }

        SimpleRichAnnotation annotation = new SimpleRichAnnotation();
        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("label"), "No alternative codon available", 0));

        StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
        featureTemplate.annotation = annotation;
        featureTemplate.location = new RangeLocation(codonStart, codonStart + 2);
        featureTemplate.source = "BIOFAB Sequence Refiner";
        featureTemplate.strand = StrandedFeature.POSITIVE;
        featureTemplate.type = "misc_feature";


        _seq.createFeature(featureTemplate);
        _refinementOK = false;

    }

    private Integer countAllRestrictionSites(RichSequence theSeq) throws IllegalSymbolException {

        Set<String>             siteNames;
        String                  siteSeq;
        int[]                   offsets;
        int                     numTotalOffsets;

        siteNames = _sites.keySet();

        numTotalOffsets = 0;

        for(String siteName : siteNames)
        {
            siteSeq = _sites.get(siteName);

            offsets = findRestrictionSite(siteSeq, theSeq);
            numTotalOffsets += offsets.length;
        }

        return numTotalOffsets;
    }

    private CodonChange safeMutateLocation(Integer siteStart, String siteSeq, Integer offset) {

        SymbolList              originalCodon;
        SymbolList              alternativeCodon;
        ArrayList<SymbolList>   failedCodons;
        Integer                 numRestrictionSites;

        System.out.println("safeMutateLocation at " + siteStart + " with offset " + offset + " for total: " + (siteStart + offset));

        try {

            /*
             *  TODO!
             *
             *  When the codon only partially overlaps with the site
             *  at the 3' end
             *
             */


            failedCodons = new ArrayList<SymbolList>();

            numRestrictionSites = countAllRestrictionSites(null);

            while(true) {
                // returns dna triplet
                originalCodon = retrieveCodon(siteStart + offset);

                // returns dna triplet | expects rna triplet
                if(offset == 0) {
                    alternativeCodon = selectAlternativeCodon(originalCodon, failedCodons, true);
                } else {
                    alternativeCodon = selectAlternativeCodon(originalCodon, failedCodons, false);
                }
                
                // if no alternate codons could be found
                if(alternativeCodon == null)
                {
                    return null;
                }
                else
                {
                    //int[] siteOccurPre = findRestrictionSite(siteSeq, null);

                    RichSequence tmpSeq = changeCodon(siteStart + offset, alternativeCodon, true);

                    /*
                    int[] siteOccur = findRestrictionSite(siteSeq, tmpSeq);

                    if(siteOccur.length < siteOccurPre.length) {
                        System.out.println("Yes! Eliminated site!");
                    }
                     */

                    // Check if the change actually eliminated a restriction site
                    int newNumRestrictionSites = countAllRestrictionSites(tmpSeq);

                    // If there are fewer restriction sites (most likely one less), then we're happy
                    if(newNumRestrictionSites < numRestrictionSites) {
                        return new CodonChange(originalCodon, alternativeCodon, siteStart + offset);
                    } else { // the codon change did not result in the elimination of a restriction site
                        System.out.println("Codon change failed at location: " + (siteStart + offset) + " from " + originalCodon.seqString() + " to " + alternativeCodon.seqString());
                        failedCodons.add(alternativeCodon);
                    }


                }
            }
        } catch(Exception e) {
            System.out.println("safeMutateRestrictionSite failed with an exception");
            e.printStackTrace();
            return null;
        }

    }

    public Integer getFailCount() {
        return _failCount;
    }

    private boolean safeMutateRestrictionSite(Integer siteStart, String siteSeq) throws IllegalAlphabetException {

        System.out.println("SAFE MUUUUTAAAAATE!");

        // The following code calls this function for each codon
        // trying to find safe and effective mutations further and further down-stream
        // for as long as there is more restriction site left to mutate

        ArrayList<CodonChange> changes = new ArrayList<CodonChange>();
        CodonChange change;

        System.out.println("Beginning safe mutate of " + siteSeq + " at location " + siteStart);

        // Find all possible changes that gets rid of the restriction site
        Integer offset = 0;
        do {
            System.out.println("Safe-mutating sequence '" + siteSeq + "' starting at " + siteStart + " at offset " + offset);
            change = safeMutateLocation(siteStart, siteSeq, offset);
            if(change != null) {
                changes.add(change);
            }
            offset += 3;
        } while((siteSeq.length() - offset + _frame) > 0);

        if(changes.isEmpty()) {
            return false;
        }

        Double frequencyDiff;
        Double lastFrequencyDiff = Double.MAX_VALUE;
        CodonChange bestChange = null;

        // Find the codon change that will change codong usage frequency the least
        int i = 0;
        for(CodonChange curChange : changes) {
            System.out.println("Trying change " + i);

            frequencyDiff = curChange.getFrequencyDifference();
            if(frequencyDiff < lastFrequencyDiff) {
                bestChange = curChange;
                lastFrequencyDiff = frequencyDiff;
            }

        }

        if(bestChange == null) {
            return false;
        }

        changeCodon(bestChange, false);

        return true;

    }

    protected void removeRestrictionSites()
    {
        Set<String>             siteNames;
        int[]                   offsets;
        Integer                 siteStart;
        Integer                 siteEnd;
        String                  siteSeq;
        
        siteNames = _sites.keySet();
    
        _failCount = 0;

        for (String siteName : siteNames)
        {
            try
            {
                siteSeq = _sites.get(siteName);
                offsets = findRestrictionSite(siteSeq, null);
                
                for (int i = 0; i < offsets.length; ++i)
                {
                    siteStart = offsets[i];
                    siteEnd = offsets[i] + siteSeq.length() - 1;

                    if(siteStart >= _start && siteEnd <= _end)
                    {
                        if(!_isCodingRegion) // TODO this is just set to true for all current controllers (Marc)
                        {
                             //TODO - Random mutation of the restriction site
                        }
                        else
                        {
                            System.out.println("Found '" + siteSeq + "' at location: " + siteStart);
                            // Attempt a safe (non-amino-acid-changing) mutation, and annotate change or failure
                            if(!safeMutateRestrictionSite(siteStart, siteSeq)) {
                                System.out.println("Change failed!");
                                annotateFailedCodonChange(siteStart, siteEnd, siteName);
                                _failCount++;
                            } else {
                                System.out.println("Change succeeded!");
                                annotateCodonChange(siteStart, siteEnd, siteName);
                            }
                        }
                    }
                 }
            }
            catch(Exception e)
            {
                e.printStackTrace();
            }
        }
    }
    
    protected SymbolList retrieveCodon(Integer startIndex)
    {
        SymbolList      dnaTriplet = null;
        SymbolList      rnaTriplet = null;
        Integer         frame;
        
        //Checks to see if the first nucleotide of the illegal site is in the same frame as the start codon
        frame = (startIndex - _start)%3;
    
        // TODO TODO!!! Need to check which parts of codon are critical to change somehow

        try
        {
            switch(frame)
            {
                case 0:
                    dnaTriplet = _seq.subList(startIndex, startIndex + 2);
                    rnaTriplet = DNATools.toRNA(dnaTriplet);
                    _frame = 0;
                    break;
                case 1:
                    dnaTriplet = _seq.subList(startIndex - 1, startIndex + 1);
                    rnaTriplet = DNATools.toRNA(dnaTriplet);
                    _frame = 1;
                    break;
                case 2:
                    dnaTriplet = _seq.subList(startIndex - 2, startIndex);
                    rnaTriplet = DNATools.toRNA(dnaTriplet);
                    _frame = 2;
                    break;
                default:
                    break;
            }
        }
        catch(Exception e)
        {
             e.printStackTrace();   
        }
    
        return dnaTriplet;
    }
    
    protected SymbolList selectAlternativeCodon(SymbolList dnaTriplet, ArrayList<SymbolList> failedTriplets, boolean atFivePrimeEnd) throws IllegalSymbolException, IllegalAlphabetException
    {        
        BasisSymbol             originalCodon = null; // RNA
        BasisSymbol             alternativeCodon = null;
        CodonPref               codonPref = null;
        Symbol                  aminoAcid = null;
//      Distribution            codonUsageDistribution = null;
        Set                     synonymousCodons = null;
        SimpleAtomicSymbol      synonymousCodon = null;
        Double                  originalFrequency = Double.MIN_NORMAL;
        Double                  usageFrequencyDiff = null;
        Double                  priorFrequencyDiff = Double.MAX_VALUE;
        String                  codonString = null;
        List                    symbols = null;
        Symbol                  symbol = null;
        SymbolList              retDNATriplet = null;
        SymbolList              rnaTriplet = null;
        BasisSymbol                  failedCodon;

        try
        {
            rnaTriplet = DNATools.toRNA(dnaTriplet);
            aminoAcid = RNATools.translate(rnaTriplet).symbolAt(1);
            codonPref = CodonPrefTools.getCodonPreference(CodonPrefTools.ECOLI);
            synonymousCodons = codonPref.getGeneticCode().untranslate(aminoAcid);
            // this cast is safe because the symbol is actually a list of symbols
            originalCodon = (BasisSymbol) RNATools.getCodonAlphabet().getSymbol(rnaTriplet.toList());
            originalFrequency = codonPref.getFrequencyForSynonyms(aminoAcid).getWeight((Symbol) originalCodon);
        }
        catch (Exception e)
        {
            e.printStackTrace();
        }

        if(synonymousCodons.size() <= 1)
        {
            return null;
        }

        for(Object object : synonymousCodons)
        {
            synonymousCodon = (SimpleAtomicSymbol) object;


            List synSymbols = synonymousCodon.getSymbols();
            List origSymbols = originalCodon.getSymbols();

            // _frame is also the number of nucleotides, starting from the 5' end
            // that are not overlapping with the feature, and thus have no effect if changed

            Symbol nucTwoOrig = (Symbol) origSymbols.get(1);
            Symbol nucThreeOrig = (Symbol) origSymbols.get(2);
            Symbol nucTwoSyn = (Symbol) synSymbols.get(1);
            Symbol nucThreeSyn = (Symbol) synSymbols.get(2);

            boolean noDifferenceWithinOverlap = false;

            // if we're at the 5' end of the site
            // TODO we should handle this for the 3' end of the site as well
            if(atFivePrimeEnd) {

                switch(_frame) {
                    case 0:
                        // full overlap. no problem.
                        break;
                    case 1:
                        // a 3' end overlap of two nucleotides. one non-overlapping
                        if(nucTwoOrig.equals(nucTwoSyn) && nucThreeOrig.equals(nucThreeSyn)) {
                            noDifferenceWithinOverlap = true;
                        }
                        break;

                    case 2:
                        // a 3' end overlap of one nucleotide. two non-overlapping.
                        if(nucThreeOrig.equals(nucThreeSyn)) {
                            noDifferenceWithinOverlap = true;
                        }
                        break;
                }


                if(noDifferenceWithinOverlap) {
                    continue; // try the next synonymous codon
                }
            }

            // Check if the codon is in the list of previously failed codons
            boolean hasAlreadyBeenTriedAndFailed = false;

            for(SymbolList failedTriplet : failedTriplets) {

                SymbolList failedTripletRNA = DNATools.toRNA(failedTriplet);
                failedCodon = (BasisSymbol) RNATools.getCodonAlphabet().getSymbol(failedTripletRNA.toList());

                if(synonymousCodon.equals(failedCodon)) {

                    hasAlreadyBeenTriedAndFailed = true;
                    break;
                }
            }

            if(hasAlreadyBeenTriedAndFailed) {
                continue; // try the next synonymous codon
            }

            

            if(!originalCodon.equals(synonymousCodon))
            {
                try
                {
                    Double usageFrequency = codonPref.getFrequencyForSynonyms(aminoAcid).getWeight((Symbol) synonymousCodon);
                    usageFrequencyDiff = Math.abs(originalFrequency - usageFrequency);
                }
                catch (IllegalSymbolException e)
                {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }

                if(usageFrequencyDiff < priorFrequencyDiff)
                {
                    alternativeCodon = synonymousCodon;
                    priorFrequencyDiff = usageFrequencyDiff;
                }
            }
        }

        if(alternativeCodon == null) {
            return null;
        }

        // TODO: I'm sure biojava has functionality to do this in a line or two

        symbols = ((SimpleAtomicSymbol)alternativeCodon).getSymbols();
        codonString = "";

        for(Object object:symbols)
        {
            symbol = (Symbol)object;

            if(symbol.getName().equals("adenine"))
            {
                codonString = codonString + "a";
            }

            if(symbol.getName().equals("cytosine"))
            {
                codonString = codonString + "c";
            }

            if(symbol.getName().equals("guanine"))
            {
                codonString = codonString + "g";
            }

            if(symbol.getName().equals("uracil"))
            {
                codonString = codonString + "t";
            }
        }

        try
        {
            retDNATriplet = DNATools.createDNA(codonString);
        }
        catch (IllegalSymbolException e)
        {
            e.printStackTrace();
        }


        return retDNATriplet;
    }

    protected boolean checkPrefixAndSuffix() {

        // too short?
        if(_seq.length() < _prefix.length()) {
            return false; // TODO should have a way of specifying what went wrong
        }

        String originalPrefix = _seq.seqString().substring(0, _prefix.length());
        
        // prefix already added?
        if(originalPrefix.equalsIgnoreCase(_prefix)) {
            return false;
        }

        // too short?
        if(_seq.length() < _suffix.length()) {
            return false; // TODO should have a way of specifying what went wrong
        }

        Integer suffixStart = _seq.length() - _suffix.length();

        String originalSuffix = _seq.seqString().substring(suffixStart, suffixStart + _suffix.length());


        // suffix already added?
        if(originalSuffix.equalsIgnoreCase(_suffix)) {
            return false;
        }

        return true;
    }


    protected void addSuffix()
    {
        Edit edit;
        int start;
        int end;

        start = _seq.length() + 1;
        end = _seq.length() + _suffix.length();
        
        try
        {
            edit = new Edit(_seq.length() + 1, 0, DNATools.createDNA(_suffix));
            _seq.edit(edit);
        }
        catch (Exception e)
        {

        }

        SimpleRichAnnotation annotation = new SimpleRichAnnotation();
        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("label"),"Suffix",0));
        
        StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
        featureTemplate.annotation = annotation;
        featureTemplate.location = new RangeLocation(start,end);
        featureTemplate.source = "BIOFAB Sequence Refiner";
        featureTemplate.strand = StrandedFeature.POSITIVE;
        featureTemplate.type = "misc_feature";
        
        try 
        {
          _seq.createFeature(featureTemplate);
        }
        catch (Exception ex) 
        {
          ex.printStackTrace();
        }


    }
    
    protected void addPrefix()
    {
        Edit edit;



        try
        {
            edit = new Edit(1, 0, DNATools.createDNA(_prefix));
            _seq.edit(edit);
        }
        catch (Exception e)
        {

        }

        
        shiftFeatures(_prefix.length());
        
        SimpleRichAnnotation annotation = new SimpleRichAnnotation();
        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("label"),"Prefix",0));
        
        StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
        featureTemplate.annotation = annotation;
        featureTemplate.location = new RangeLocation(1, _prefix.length());
        featureTemplate.source = "BIOFAB Sequence Refiner";
        featureTemplate.strand = StrandedFeature.POSITIVE;
        featureTemplate.type = "misc_feature";
        
        try 
        {
          _seq.createFeature(featureTemplate);
        }
        catch (Exception ex) 
        {
          //ex.printStackTrace();
        }
    }
    
    protected void shiftFeatures(int shiftLength)
    {
        Location location;
        
        for(Iterator<Feature> features = _seq.features(); features.hasNext(); ) 
        {
            Feature feature = (Feature) features.next();
            location = feature.getLocation();
            feature.setLocation(new RangeLocation(location.getMin() + shiftLength, location.getMax() + shiftLength));
        }
    }
    
    protected void generateComment()
    {
        if (_refinementOK)
        {
             _seq.addComment(new SimpleComment("The refinement was completed successfully. This sequence is compliant with " + _standardName, 0));
        }
        else
        {
            _seq.addComment(new SimpleComment("This sequence is not compliant with " + _standardName + ". The refinement could not be completed.", 0));
        }
    }
}