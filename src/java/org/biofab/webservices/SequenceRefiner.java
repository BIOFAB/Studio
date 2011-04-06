/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices;

import com.google.gson.Gson;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.biofab.refiner.controllers.RefinementController;
import org.biofab.refiner.controllers.RefinementControllerFactory;
import org.biofab.webservices.annotations.WebAccessible;
import org.biofab.webservices.protocol.OligoDesignResponse;
import org.biofab.webservices.protocol.SequenceRefinerRequest;
import org.biofab.webservices.protocol.SequenceRefinerResponse;
import org.biojava.bio.seq.DNATools;
import org.biojava.bio.symbol.IllegalAlphabetException;
import org.biojava.bio.symbol.IllegalSymbolException;
import org.biojava.bio.symbol.SymbolList;
import org.biojavax.bio.seq.RichSequence;


@WebServlet(name="SequenceRefiner", urlPatterns={"/SequenceRefiner/*"})
public class SequenceRefiner extends BiofabServlet {

    
    @WebAccessible
    public void refine(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {

        response.setContentType("text/plain;charset=UTF-8");
        

        String json_req = request.getParameter("json");

        if((json_req == null) || (json_req.equals(""))) {
             response.sendError(response.SC_BAD_REQUEST, "no json received");
             return;
        }

        Gson gson = new Gson();

        SequenceRefinerRequest req = gson.fromJson(json_req, SequenceRefinerRequest.class);

        if(!req.validate()) {
             response.sendError(response.SC_BAD_REQUEST, "request invalid");
             return;
        }

        RefinementController refiner = new RefinementControllerFactory().createController("BBF10");
        refiner.setCodonPreference("TRNA"); // Is this correct?

        RichSequence seq = null;

        try {
            SymbolList seq_sym = DNATools.createDNA(req.sequence);
            seq = RichSequence.Tools.createRichSequence("sequence", seq_sym);
        } catch (IllegalSymbolException ex) {
           response.sendError(response.SC_BAD_REQUEST, "illegal character encountered: are you sure this is a valid DNA sequence?");
           return;
        }


        RichSequence refined_seq = refiner.refine(seq);

        SequenceRefinerResponse resp = new SequenceRefinerResponse(refined_seq.seqString());

        String json_resp = gson.toJson(resp);

        PrintWriter out = response.getWriter();
        try {
            out.println(json_resp);
        } finally {
            out.close();
        }
    }

    @WebAccessible
    public void oligo_design(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {

        response.setContentType("text/plain;charset=UTF-8");

        String json_req = request.getParameter("json");

        if((json_req == null) || (json_req.equals(""))) {
             response.sendError(response.SC_BAD_REQUEST, "no json received");
             return;
        }

        Gson gson = new Gson();

        String json_resp = null;

        try {
            ArrayList<OligoDesignResponse> results = OligoDesign.design_for_json(json_req);
            json_resp = gson.toJson(results);
            
        } catch (IllegalSymbolException ex) {
           response.sendError(response.SC_BAD_REQUEST, "illegal character encountered: are you sure this is a valid DNA sequence?");
           return;
        } catch (IllegalAlphabetException ex) {
           response.sendError(response.SC_BAD_REQUEST, "illegal character encountered: are you sure this is a valid DNA sequence?");
           return;
        }

        PrintWriter out = response.getWriter();
        try {
            out.println(json_resp);
        } finally {
            out.close();
        }

    }


    @WebAccessible
    public void show(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {

        response.setContentType("text/html;charset=UTF-8");
        PrintWriter out = response.getWriter();

        if(request.getMethod().equals("GET")) {

            try {

                out.println("<html>");
                out.println("<head>");
                out.println("<title>Sequence Refiner</title>");
                out.println("</head>");
                out.println("<body>");
                out.println("<h1>Enter DNA sequence</h1>");
                out.println("<form action='/java/Galapagos_Method/SequenceRefiner/refine' method='post'>");
                out.println("<p>JSON:<textarea name='json' rows='7' cols='30'></textarea></p>");
                out.println("<p><input type='submit' value='Refine!' /></p>");
                out.println("</form>");
                out.println("</body>");
                out.println("</html>");

            } finally {
                out.close();
            }
        }
    }


    /** 
     * Returns a short description of the servlet.
     * @return a String containing servlet description
     */
    @Override
    public String getServletInfo() {
        return "Short description";
    }// </editor-fold>

}
