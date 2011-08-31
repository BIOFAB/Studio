//
//  RefinementControllerFactory.java
//  BIOFAB Wetware Studio
//
//  Created by Cesar A. Rodriguez
//
//  Copyright 2010 University of California at Berkeley. All rights reserved.
//

package org.biofab.studio.canvas.part.refiner;


public class RefinementControllerFactory extends Object
{
    public RefinementControllerFactory()
    {
	super();
    }
		
    public RefinementController createController(String standardID)
    {   
        RefinementController controller = null;
        
	if(standardID.equalsIgnoreCase("BBF10"))
	{
	    controller = new BBFTenController();
	}
	
	if(standardID.equalsIgnoreCase("BBF12"))
        {
            controller = new BBFTwelveController();
        }
	
	if(standardID.equalsIgnoreCase("BBF21"))
        {
            controller = new BBFTwentyOneController();
        }
	
	if(standardID.equalsIgnoreCase("BBF23"))
        {
            //controller = new BBFTwentyThreeController();
        }
	
	if(standardID.equalsIgnoreCase("BBF25"))
        {
            controller = new BBFTwentyFiveController();
        }
	
	if(standardID.equalsIgnoreCase("BBF28"))
        {
            //controller = new BBFTwentyEightController();
        }
			
	return controller;
    }
}
