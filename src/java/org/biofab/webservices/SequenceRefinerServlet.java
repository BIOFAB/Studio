package org.biofab.webservices;

import java.io.*;
import java.util.NoSuchElementException;

import javax.servlet.http.*;

//import org.biofab.model.OligoPair;
import org.biofab.refiner.controllers.RefinementController;
import org.biofab.refiner.controllers.RefinementControllerFactory;
import org.biofab.refiner.model.JsonOligoDesignInput;
import org.biofab.refiner.model.RefinementResult;
import org.biojava.bio.BioException;
import org.biojava.bio.symbol.IllegalAlphabetException;
import org.biojava.bio.symbol.IllegalSymbolException;
import org.biojavax.bio.seq.*;
//import org.biojava.bio.alignment.*;
//import org.biojava.bio.seq.DNATools;
import org.biojavax.Namespace;
import org.biojavax.RichObjectFactory;

import com.google.gson.Gson;


@SuppressWarnings("serial")
public class SequenceRefinerServlet extends HttpServlet
{
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException
    {
        response.getWriter().println("You have contacted the Refiner Service!");
    }
    
    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException
    {
        String                          inputFile;
        String                          standardID;
        String                          codonChangePref;
        RichSequence                    refinedSequence;
        RefinementControllerFactory     factory;
        RefinementController            refiner;
        RichSequence                    sequence;
        
        factory = new RefinementControllerFactory();
        Namespace ns = RichObjectFactory.getDefaultNamespace();
        sequence = null;
        refinedSequence = null;
        
        inputFile = request.getParameter("file");
    
        if(inputFile != null && inputFile.length() > 0)
        {
            standardID = request.getParameter("standard");
        
            if(standardID != null && standardID.length() > 0)
            {
//              RichSequenceIterator sequences = RichSequence.IOTools.readGenbankDNA(new BufferedReader (new StringReader(sequenceFile)), ns);
                RichSequenceIterator sequences = RichSequence.IOTools.readINSDseqDNA(new BufferedReader (new StringReader(inputFile)), ns);
                refiner = factory.createController(standardID);
                codonChangePref = request.getParameter("condonpref");
               
                if(codonChangePref != null && codonChangePref.length() > 0)
                {
                    refiner.setCodonPreference(codonChangePref);
                }

                while (sequences.hasNext())
                {
                    try
                    {
                        sequence = sequences.nextRichSequence();
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
                    
                    refinedSequence = refiner.refine(sequence);
                }
                
//                response.setContentType("text/xml");
//                RichSequence.IOTools.writeINSDseq(response.getOutputStream(), refinedSequence, ns);
                
                response.setContentType("text/plain");
                RichSequence.IOTools.writeGenbank(response.getOutputStream(), refinedSequence, ns);
            }
            else
            {
                //TODO Deal with a missing standard
            }
        }
        else
        {
            //TODO Deal with a missing file
        }
    }
    
//    protected OligoPair design_for_json(String json) throws IllegalSymbolException, IllegalAlphabetException {
//        Gson gson = new Gson();
//        
//        JsonOligoDesignInput input = gson.fromJson(json, JsonOligoDesignInput.class);
////      design(input.sequences, input.forward_concat_5p, input.forward_concat_3p, input.reverse_concat_5p, input.reverse_concat_3p);
//        
//        return null;
//    }
}
