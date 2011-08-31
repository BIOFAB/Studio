package org.biofab.studio.model;

public class Part
{
    protected String    _id;
    protected String    _description;
    protected String    _seq;
    
    public Part(String id, String description, String sequence)
    {
        _id = id;
        _description = description;
        _seq = sequence;
    }

    public String getDescription()
    {
        return _description;
    }

    public String getID()
    {
        return _id;
    }

    public String getSequence()
    {
        return _seq;
    }

}
