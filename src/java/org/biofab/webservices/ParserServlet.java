package org.biofab.webservices;

import java.io.*;
import javax.servlet.http.*;

import org.biojavax.bio.seq.*;
//import org.biojava.bio.seq.DNATools;
import org.biojavax.Namespace;
import org.biojavax.RichObjectFactory;


@SuppressWarnings("serial")
public class ParserServlet extends HttpServlet
{
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException
    {
        response.getWriter().println("You have contacted the Genbank File Parser Service!");
    }
    
    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException
    {
        RichSequence                    sequence;
        String                          fileString;
        String                          informat;
        String                          outformat;
        RichSequenceIterator            sequences;
        
        sequence = null;
        sequences = null;
        Namespace ns = RichObjectFactory.getDefaultNamespace();
        
        try
        {
            fileString = request.getParameter("file");
            informat = request.getParameter("informat");
            outformat = request.getParameter("outformat");
            
            if(informat.equalsIgnoreCase("genbank"))
            {
                sequences = RichSequence.IOTools.readGenbankDNA(new BufferedReader (new StringReader(fileString)), ns);
            }
            
            if(informat.equalsIgnoreCase("insd"))
            {
                sequences = RichSequence.IOTools.readINSDseqDNA(new BufferedReader (new StringReader(fileString)), ns);
            }
            
            if(informat.equalsIgnoreCase("fasta"))
            {
                sequences = RichSequence.IOTools.readFastaDNA(new BufferedReader (new StringReader(fileString)), ns);
            }

            while (sequences.hasNext())
            {
                sequence = sequences.nextRichSequence();
            }
            
            if(outformat.equalsIgnoreCase("genbank"))
            {
                response.setContentType("text/plain");
                RichSequence.IOTools.writeGenbank(response.getOutputStream(), sequence, ns);
            }
            
            if(outformat.equalsIgnoreCase("insd"))
            {
                response.setContentType("text/xml");
                RichSequence.IOTools.writeINSDseq(response.getOutputStream(), sequence, ns);
            }
        }
        catch (Throwable t)
        {
            t.printStackTrace();
            System.exit(1);
        }
    }
}

