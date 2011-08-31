package org.biofab.studio.canvas.device;

import java.util.ArrayList;

import org.biojava.bio.seq.DNATools;
import org.biojava.bio.symbol.IllegalSymbolException;
import org.biojavax.bio.seq.RichSequence;

//import org.biojavax.bio.seq.RichSequence;

//import org.biofab.model.Oligo;

public class AssemblyController
{
    protected String[][]        _parts;
    
    public AssemblyController()
    {
        super();
    }
    
    public ArrayList<Construct> combine(String[][] bins, String [][] parts)
    {
        _parts = parts;
        ArrayList<Construct> constructs = new ArrayList<Construct>();
        ArrayList<Construct> newConstructs = null;
        int rowsCount = bins.length;
        int colsCount = bins[0].length;
        String binContent;
        Insert insert;
        Construct newConstruct;
//        Construct priorConstruct;
        
        for(int i = 0; i < colsCount; ++i)
        {
            if(newConstructs == null || newConstructs.size() > 0)
            {
                newConstructs = new ArrayList<Construct>();
            }
            
            for(int j = 0; j < rowsCount; ++j)
            {
                binContent = bins[j][i];
                
                if(binContent != null && binContent.length() > 0)
                {
                    insert = this.parseBinContent(binContent);
                    
                    if(constructs.isEmpty())
                    {
                        newConstruct = new Construct();
                        newConstruct.add(insert);
                        newConstructs.add(newConstruct);
                    }
                    else
                    {
                        for(Construct construct : constructs)
                        {
                            //Have to create a new ArrayList
                            newConstruct = new Construct(construct.getInserts());
                            newConstruct.add(insert);
                            newConstructs.add(newConstruct);
                        }
                    }
                }
            }
            
            if(newConstructs.size() > 0)
            {
                constructs = null;
                constructs = newConstructs;
            }
        }
        
        return constructs;
    }
    
    protected Insert parseBinContent(String binContent)
    {
        String[] seqIDs = null;
        String fwdSeqID = null;
        String fwdSeqString = null;
        String revSeqID = null;
        String revSeqString = null;
        RichSequence fwdSeq = null;
        RichSequence revSeq = null;
        Insert insert = null;

        seqIDs = binContent.split("/");
        
        if(seqIDs.length == 2)
        {
            fwdSeqID = seqIDs[0].trim();
            fwdSeqString = fetchSequence(fwdSeqID);
            revSeqID = seqIDs[1].trim();
            revSeqString = fetchSequence(revSeqID);
           
            try
            {
                fwdSeq = RichSequence.Tools.createRichSequence(fwdSeqID, DNATools.createDNA(fwdSeqString));
                revSeq = RichSequence.Tools.createRichSequence(revSeqID, DNATools.createDNA(revSeqString));
            }
            catch (IllegalSymbolException e)
            {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
            
            insert = new Insert(fwdSeq, revSeq);
        }
        else
        {
            // TODO Deal with case where the insert string has more than two tokens
        }
        
        return insert;
    }
    
    protected String fetchSequence(String partID)
    {
        int partCount = _parts.length;
        String partSeq = null;
        
        for(int i = 0; i < partCount; ++i)
        {
            if(_parts[i][0].equalsIgnoreCase(partID))
            {
                partSeq = _parts[i][1];
            }
        }
        
        return partSeq;
    }
    
//    public RichSequence assemble(Insert[] inserts, RichSequence backbone)
//    {
//        return null;
//    }
}
