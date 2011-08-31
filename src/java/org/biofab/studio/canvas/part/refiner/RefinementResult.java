package org.biofab.studio.canvas.part.refiner;

import org.biojavax.bio.seq.RichSequence;

public class RefinementResult
{
    protected RichSequence      _seq;
    protected String            _feedback;
    
    RefinementResult()
    {
        super();
    }
        
    public void setRichSequence(RichSequence seq)
    {
        if(seq != null)
        {
            _seq = seq;
        }
        else
        {
            //throw exception
        }
    }
    
    public RichSequence getRichSequence()
    {
        return _seq;
    }
    
    public void addFeedback(String feedback)
    {
        _feedback = _feedback + "\n" + feedback;
    }
    
    public String getfeedback()
    {
        return _feedback;
    }
}
