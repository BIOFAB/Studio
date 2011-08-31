package org.biofab.studio.canvas.device;

import org.biojavax.bio.seq.RichSequence;

public class Insert
{
    protected RichSequence     _fwdSeq;
    protected RichSequence     _revSeq;
    

    public Insert(RichSequence fwdSeq, RichSequence revSeq)
    {
        super();
        
        if(fwdSeq != null && revSeq!= null)
        {
            _fwdSeq = fwdSeq;
            _revSeq = revSeq;
        }
        else
        {
            // TODO Handle NULL case
        }
    }
    
    public Insert()
    {
        super();
        
        _fwdSeq = null;
        _revSeq = null;
    }


    public RichSequence getForwardSequence()
    {
        return _fwdSeq;
    }

    public void setforwardSequence(RichSequence fwdSeq)
    {
        if (fwdSeq != null)
        {
            _fwdSeq = fwdSeq;
        }
        else
        {
            // TODO Handle NULL case
        }
    }

    public RichSequence getReverseSequence()
    {
        return _revSeq;
    }

    public void setReverseSequence(RichSequence revSeq)
    {
        if (revSeq != null)
        {
            _revSeq = revSeq;
        }
        else
        {
            // TODO Handle NULL case
        }
    }
    
    public String getDescription()
    {
        String description = _fwdSeq.getName() + "/" + _revSeq.getName();
        
        return description;
    }
}
