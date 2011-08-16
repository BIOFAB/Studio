

package org.biofab.studio.model;

/**
 *
 * @author cesarr
 * 
 */

public class Feature
{
    protected int       index;
    protected String    biofabId;
    protected String    genbankType;
    protected String    biofabType;
    protected String    description;
    protected String    dnaSequence;
    
    
    public Feature(int index, String biofabId, String genbankType, String biofabType, String description, String dnaSequence)
    {
        //TODO: manage the boundary cases

        this.index = index;
        
        if(biofabId != null && biofabId.length() > 0)
        {
            this.biofabId = biofabId;
        }
        else
        {
            //Throw exception
        }

        if(description != null && description.length() > 0)
        {
            this.description = description;
        }
        else
        {
            this.description = "No description is available.";
        }
        
        if(genbankType != null && genbankType.length() > 0)
        {
            this.genbankType = genbankType;
        }
        else
        {
            // Throw exception
        }
        
        if(biofabType != null && biofabType.length() > 0)
        {
            this.biofabType = biofabType;
        }
        else
        {
            // Throw exception
        }
        
        if(dnaSequence != null && dnaSequence.length() > 0)
        {
            this.dnaSequence = dnaSequence;
        }
        else
        {
            // Throw exception
        } 
    }

    /**
     * @return the index
     */
    public int getIndex()
    {
        return index;
    }
    
    /**
     * @return the biofabId
     */
    public String getBiofabId()
    {
        return biofabId;
    }

    /**
     * @return the biofabType
     */
    public String getBiofabType() 
    {
        return biofabType;
    }

    /**
     * @return the genbankType
     */
    public String getGenbankType() 
    {
        return genbankType;
    }
    
    /**
     * @return the description
     */
    public String getDescription()
    {
        return description;
    }
    
    
    /**
     * @return the dnaSequence
     */
    public String getDnaSequence()
    {
        return dnaSequence;
    }
}
