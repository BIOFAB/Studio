package org.biofab.webservices;

import java.io.*;
import java.util.NoSuchElementException;

import javax.servlet.http.*;

//import org.biojavax.bio.seq.*;
import org.biojava.bio.BioException;
import org.biojava.bio.alignment.*;
//import org.biojava.bio.seq.DNATools;
//import org.biojavax.Namespace;
//import org.biojavax.RichObjectFactory;


@SuppressWarnings("serial")
public class SequenceAlignmentServlet extends HttpServlet
{
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException
    {
        response.getWriter().println("You have contacted the Alignment Service!");
    }
    
    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException
    {    
        short match = 0;
        short replace = 0; 
        short insert = 0; 
        short delete = 0; 
        short gapExtend = 0;
        
        SubstitutionMatrix matrix = null ;
        
        try
        {
            matrix = new SubstitutionMatrix(new File("matrixFile"));
        }
        catch (NumberFormatException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        catch (NoSuchElementException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        catch (BioException e)
        {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        
        NeedlemanWunsch aligner = new NeedlemanWunsch(match, replace, insert, delete, gapExtend, matrix);
    }
}
