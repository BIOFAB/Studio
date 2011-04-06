package org.biofab.webservices;

import java.io.*;
import java.util.ArrayList;
//import java.util.Hashtable;
import javax.servlet.http.*;

import com.google.gson.Gson;
import javax.servlet.annotation.WebServlet;

import org.biofab.assembler.AssemblyController;
import org.biofab.assembler.Construct;
//import org.biofab.model.Oligo;
//import org.biofab.model.Part;

//import org.biojavax.bio.seq.*;
//import org.biojavax.Namespace;
//import org.biojavax.RichObjectFactory;


@SuppressWarnings("serial")
@WebServlet(name="assembler", urlPatterns={"/assembler/*"})
public class AssemblerServlet extends HttpServlet
{
    protected AssemblyController        _controller;
    protected Gson                      _gson; 
    
    public AssemblerServlet()
    {
       _controller = new AssemblyController();
       _gson = new Gson();
    }
    
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException
    {   
        response.getWriter().println("You have contacted the Assembler Web Service!");
    }
    
    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException
    {
        
        String binsJSON = request.getParameter("bins");
        String partsJSON = request.getParameter("parts");
        ArrayList<Construct> constructs = null;
        String constructsJSON = null;
        
        if(binsJSON != null && binsJSON.length() > 0)
        {
            String[][] bins  = _gson.fromJson(binsJSON, String[][].class);
            String[][] parts = _gson.fromJson(partsJSON, String[][].class);            

            constructs = _controller.combine(bins, parts);
            constructsJSON = generateJSONString(constructs);
            
            response.setContentType("text/plain");
            response.getWriter().println(constructsJSON);
        }
        else
        {
            // TODO Deal with null or empty bins string
        }
    }
    
    protected String generateJSONString(ArrayList<Construct> constructs)
    {
        int constructCount = constructs.size();
        Object[][] constructsInfo = new Object[constructCount][5];
        int i = 0;
        
        for(Construct construct : constructs)
        {
            constructsInfo[i][0] = i;
            constructsInfo[i][1] = construct.getDescription();
            constructsInfo[i][2] = construct.getForwardSequence().seqString();
            constructsInfo[i][3] = construct.getReverseSequence().seqString();
            constructsInfo[i][4] = "Undefined";
            ++i;
        }
        
        String constructsJSON = _gson.toJson(constructsInfo);
        
        return constructsJSON;
    }
}
