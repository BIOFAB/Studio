

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


    public Plasmid(String biofabId, String description)
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
    }


    /**
     * @return the biofabId
     */
    public String getBiofabId()
    {
        return biofabId;
    }

    /**
     * @param biofabId the biofabId to set
     */
//    public void setBiofabId(String biofabId)
//    {
//        this.biofabID = biofabID;
//    }

    /**
     * @return the description
     */
    public String getDescription()
    {
        return description;
    }

    /**
     * @param performance the performance to set
     */
//    public void setPerformance(ConstructPerformance performance)
//    {
//        this.performance = performance;
//    }
}
