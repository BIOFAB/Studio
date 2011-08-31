package org.biofab.studio.canvas.device;

//import java.util.Hashtable;
import java.util.ArrayList;

//import org.biojava.bio.seq.DNATools;
//import org.biojava.bio.seq.StrandedFeature;
import org.biojava.bio.seq.DNATools;
import org.biojava.bio.symbol.Edit;
//import org.biojava.bio.symbol.RangeLocation;
//import org.biojavax.RichObjectFactory;
//import org.biojavax.SimpleNote;
//import org.biojavax.SimpleRichAnnotation;
import org.biojavax.bio.seq.RichSequence;

//import org.biofab.model.Part;
//import org.biojava.bio.seq.DNATools;
//import org.biojava.bio.seq.Feature;
//import org.biojava.bio.seq.StrandedFeature;
//import org.biojava.bio.symbol.Edit;
//import org.biojava.bio.symbol.IllegalSymbolException;
//import org.biojava.bio.symbol.RangeLocation;
//
//import org.biojavax.Namespace;
//import org.biojavax.RichObjectFactory;
//import org.biojavax.SimpleComment;
//import org.biojavax.SimpleNote;
//import org.biojavax.SimpleRichAnnotation;
//import org.biojavax.bio.seq.*;


//import org.biofab.model.Part;


public class Construct
{
    protected ArrayList<Insert>         _inserts;
    protected RichSequence              _backbone;
    protected RichSequence              _fwdSeq;
    protected RichSequence              _revSeq;
    protected boolean                   _isCorrect;
    protected ArrayList<String>         _feedback;
    protected String                    _description;
    protected String                    _status;
    
    public Construct()
    {
        _isCorrect = false;
        _fwdSeq = null;
        _revSeq = null;
        _feedback = new ArrayList<String>();
        _inserts = new ArrayList<Insert>();
    }
    
    public Construct(ArrayList<Insert> inserts)
    {
        _isCorrect = false;
        _fwdSeq = null;
        _revSeq = null;
        _feedback = new ArrayList<String>();
        _inserts = inserts;
        assemble();
    }
    
    public RichSequence getForwardSequence()
    {
        return _fwdSeq;
    }

//    public void setForwardSequence(RichSequence fwdSeq)
//    {
//        _fwdSeq = fwdSeq;
//    }

    public RichSequence getReverseSequence()
    {
        return _revSeq;
    }

//    public void setReverseSequence(RichSequence revSeq)
//    {
//        _revSeq = revSeq;
//    }
    
    public boolean isCorrect()
    {
        return _isCorrect;
    }
    
    public ArrayList<Insert> getInserts()
    {
        return (ArrayList<Insert>) _inserts.clone();
    }
    
    public void add(Insert insert)
    {
        _inserts.add(insert);
        _fwdSeq = null;
        _revSeq = null;
        assemble();
    }
    
    public String getDescription()
    {
        String description = "";
        
        for(Insert insert : _inserts)
        {
            if(description.equalsIgnoreCase(""))
            {
                description = insert.getDescription();
            }
            else
            {
                description = description + " | " + insert.getDescription();
            }
        }
        
        description = description + " in backbone (pending)";
        
        return description;
    }
    
    protected void assemble()
    {
        for(Insert insert : _inserts)
        { 
            if(_fwdSeq == null)
            {
                _fwdSeq = RichSequence.Tools.createRichSequence("Forward Strand", insert.getForwardSequence().getInternalSymbolList());
                _revSeq = RichSequence.Tools.createRichSequence("Reverse Strand", insert.getReverseSequence().getInternalSymbolList());
            }
            else
            {
//                ligate(_fwdSeq, insert.getForwardSequence(), true);
//                ligate(_revSeq, insert.getReverseSequence(), false);
                
                ligate(insert, true);
                
            }
        }
    }
        
//    protected void ligate(RichSequence leftSeq, RichSequence rightSeq, boolean annotate)
//    {
//        Edit edit;
////        int start;
////        int end;
////        
////        start = leftSeq.getInternalSymbolList().length() + 1;
////        end = sequence.length() + subSeq.length();
//        
//        try
//        {
//            edit = new Edit(leftSeq.length() + 1, 0, rightSeq.getInternalSymbolList());
//            leftSeq.edit(edit);
//        }
//        catch (Exception e)
//        {
//
//        }
//        
////        SimpleRichAnnotation annotation = new SimpleRichAnnotation();
////        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm(noteKey),noteValue,0));
////        
////        StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
////        featureTemplate.annotation = annotation;
////        featureTemplate.location = new RangeLocation(start,end);
////        featureTemplate.source = "BIOFAB";
////        featureTemplate.strand = StrandedFeature.POSITIVE;
////        featureTemplate.type = featureKey;
////        
////        try 
////        {
////          sequence.createFeature(featureTemplate);
////        }
////        catch (Exception ex) 
////        {
////          //ex.printStackTrace();
////        }
//    }
    
    protected void ligate(Insert insert, boolean annotate)
    {
        Edit    edit;
        String  newSeq;
//        int start;
//        int end;
//        
//        start = leftSeq.getInternalSymbolList().length() + 1;
//        end = sequence.length() + subSeq.length();
        
        try
        {
//            edit = new Edit(_fwdSeq.length() + 1, 0, insert.getForwardSequence().getInternalSymbolList());
//            _fwdSeq.edit(edit);
            
//            edit = new Edit(0, insert.getReverseSequence().length(), insert.getReverseSequence().getInternalSymbolList());
//            _revSeq.edit(edit);
            
            newSeq =  _fwdSeq.seqString() + insert.getForwardSequence().seqString();
            _fwdSeq = RichSequence.Tools.createRichSequence("Forward Strand", DNATools.createDNA(newSeq));
            
            newSeq = insert.getReverseSequence().seqString() + _revSeq.seqString();
            _revSeq = RichSequence.Tools.createRichSequence("Reverse Strand", DNATools.createDNA(newSeq));
            
        }
        catch (Exception e)
        {

        }
    }
 }
