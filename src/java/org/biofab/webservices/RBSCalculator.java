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
import org.biofab.bean.RBSCalculatorBean;
import org.biofab.webservices.annotations.WebAccessible;
import org.biofab.webservices.protocol.RBSCalculateRequest;
import org.biofab.webservices.protocol.RBSCalculateResponse;


@WebServlet(name="RBSCalculator", urlPatterns={"/RBSCalculator/*"})
public class RBSCalculator extends BiofabServlet {
   
    @EJB
    private RBSCalculatorBean fooBean;

    
    @WebAccessible
    public void calculate(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {

        response.setContentType("text/html;charset=UTF-8");

        String json_req = request.getParameter("json");

        if((json_req == null) || (json_req.equals(""))) {
             response.sendError(response.SC_BAD_REQUEST, "no json received");
             return;
        }

        Gson gson = new Gson();

        RBSCalculateRequest req = gson.fromJson(json_req, RBSCalculateRequest.class);

        if(!req.validate()) {
             response.sendError(response.SC_BAD_REQUEST, "request invalid");
             return;
        }

        String output = fooBean.jythonFoo(this.getServletContext(), req.sequence);

        RBSCalculateResponse resp = new RBSCalculateResponse(output);

        String json_resp = gson.toJson(resp);

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
                out.println("<title>RBS calculator</title>");
                out.println("</head>");
                out.println("<body>");
                out.println("<p>query string: " + request.getQueryString() + "</p>");
                out.println("<p>request URI: " + request.getRequestURI() + "</p>");
                out.println("<p>request URL: " + request.getRequestURL() + "</p>");
                out.println("<h1>Enter DNA sequence</h1>");
                out.println("<form action='/java/Galapagos_Method/RBSCalculator/calculate' method='post'>");
                out.println("<p>Sequence:<textarea name='dnaseq' rows='7' cols='30'></textarea></p>");
                out.println("<p><input type='submit' value='Calculate!' /></p>");
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
        return "The RBS Calculator web service";
    }// </editor-fold>

}
