

package org.biofab.studio.model;

/**
 *
 * @author cesarr
 */

public class Oligo
{
    protected int       index;
    protected String    biofabId;
    protected String    description;
    protected String    dnaSequence;
    
    
    public Oligo(int index, String biofabId, String description, String dnaSequence)
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

        if(description != null)
        {
            this.description = description;
        }
        else
        {
            this.description = "No description is available.";
        }
        
        if(dnaSequence != null)
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
