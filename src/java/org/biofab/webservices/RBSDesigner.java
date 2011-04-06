/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices;

import com.google.gson.Gson;
import java.io.IOException;
import java.io.PrintWriter;
import javax.ejb.EJB;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.biofab.bean.RBSDesignerBean;
import org.biofab.jython.FromPythonException;
import org.biofab.webservices.annotations.WebAccessible;
import org.biofab.webservices.protocol.RBSDesignerRequest;
import org.biofab.webservices.protocol.RBSDesignerResponse;


@WebServlet(name="RBSDesigner", urlPatterns={"/RBSDesigner/*"})
public class RBSDesigner extends BiofabServlet {
   
    @EJB
    private RBSDesignerBean bean;

    
    @WebAccessible
    public void calculate(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {

        response.setContentType("text/plain;charset=UTF-8");

        String json_req = request.getParameter("json");

        if((json_req == null) || (json_req.equals(""))) {
             response.sendError(response.SC_BAD_REQUEST, "no json received");
             return;
        }

        Gson gson = new Gson();

        RBSDesignerRequest req = gson.fromJson(json_req, RBSDesignerRequest.class);

        if(!req.validate()) {
             response.sendError(response.SC_BAD_REQUEST, "request invalid");
             return;
        }

        PrintWriter out = response.getWriter();
        try {

            RBSDesignerResponse resp;
            
            try {
                String output = bean.design(this.getServletContext(), req.sequence, req.start_codon_offset);
                resp = new RBSDesignerResponse(output);
            } catch(FromPythonException e) {
                resp = new RBSDesignerResponse("");
                resp.error = e.message;
                resp.stack_trace = e.stackTrace;
            }

            String json_resp = gson.toJson(resp);
 
            out.println(json_resp);
        } finally {
            out.close();
        }

    }


    /** 
     * Returns a short description of the servlet.
     * @return a String containing servlet description
     */
    @Override
    public String getServletInfo() {
        return "The RBS Designer web service";
    }// </editor-fold>

}
