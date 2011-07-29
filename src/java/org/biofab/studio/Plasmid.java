

package org.biofab.studio;

/**
 *
 * @author cesarr
 */

import java.util.Date;


public class Plasmid
{
    protected String    biofabId;
    protected String    description;
    protected int       index;


    public Plasmid(String biofabId, String description, int index)
    {
        //TODO: manage the boundary cases


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
            //Throw exception
        }
        
        this.index = index;
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
     * @return the index
     */
    public int getIndex()
    {
        return index;
    }
}
