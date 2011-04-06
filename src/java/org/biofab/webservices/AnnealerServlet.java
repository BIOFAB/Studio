package org.biofab.webservices;


import java.io.IOException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.*;

import org.biojavax.SimpleNamespace;
import org.biojava.bio.seq.DNATools;
import org.biojava.bio.symbol.SymbolList;

import org.biofab.assembler.Annealer;
import org.biofab.model.Oligo;

@SuppressWarnings("serial")
@WebServlet(name="annealer", urlPatterns={"/annealer/*"})
public class AnnealerServlet extends HttpServlet
{
    protected Annealer  _annealer;
    protected Oligo     _forwardOligo;
    protected Oligo     _reverseOligo;
    
    public AnnealerServlet()
    {
       _annealer = new Annealer();
    }
    
    public void doGet(HttpServletRequest req, HttpServletResponse response) throws IOException
    {
        response.getWriter().println("You have contacted the Annealer Service!");
    }
    
    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException
    {
        String          forwardOligoID;
        String          forwardOligoSeq;
        String          reverseOligoID;
        String          reverseOligoSeq;
        SymbolList      forwardOligoSymList = null;
        SymbolList      reverseOligoSymList = null;
        String          resultText;
        
        forwardOligoID = request.getParameter("FwdSeqID");
        forwardOligoSeq = request.getParameter("FwdSeq");
        reverseOligoID = request.getParameter("RevSeqID");
        reverseOligoSeq = request.getParameter("RevSeq");
        
        if((forwardOligoID != null && forwardOligoID.length() > 0) && (forwardOligoSeq != null && forwardOligoSeq.length() > 0) && (reverseOligoID != null && reverseOligoID.length() > 0) && (reverseOligoSeq != null && reverseOligoSeq.length() > 0))
        {
            try
            {
                forwardOligoSymList = DNATools.createDNA(forwardOligoSeq);
                reverseOligoSymList = DNATools.createDNA(reverseOligoSeq);
                _forwardOligo = new Oligo(new SimpleNamespace("biofab"), "", forwardOligoID, forwardOligoID, 1, forwardOligoSymList, 1.0);
                _reverseOligo = new Oligo(new SimpleNamespace("biofab"), "", reverseOligoID, reverseOligoID, 1, reverseOligoSymList, 1.0);
                resultText = _annealer.anneal(_forwardOligo, _reverseOligo);
                
                if (resultText != null && resultText.length() > 0)
                {
                    response.setContentType("text/plain");
                    response.getWriter().println(resultText);
                }
                else
                {
                    response.getWriter().println("There was an error while attempting to anneal the oligonucleotides.");
                }
           } 
           catch (Exception exc) 
           {
               response.setContentType("text/plain");
               response.getWriter().println(exc.getMessage());
           }
            
        }
        else
        {
            response.setContentType("text/plain");
            response.getWriter().println("Invalid parameters were submitted.");
        }
    }
}
