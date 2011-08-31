package org.biofab.studio.canvas.device;

import org.biojavax.bio.seq.RichSequence;

public class Assembly
{
    protected RichSequence      _construct;
    protected String            _feedback;
    protected Boolean           _isCorrect;
    
    public Assembly(RichSequence construct, String feedback, Boolean isCorrect)
    {
        _construct = construct;
        _feedback = feedback;
        _isCorrect = isCorrect;
    }

    public RichSequence getConstruct()
    {
        return _construct;
    }

    public String getFeedback()
    {
        return _feedback;
    }

    public Boolean isCorrect()
    {
        return _isCorrect;
    } 
}
