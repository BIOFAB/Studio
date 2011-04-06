/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices;

import com.google.gson.Gson;
import java.io.IOException;
import java.io.PrintWriter;
import java.lang.annotation.Annotation;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.biofab.webservices.protocol.JSONResponse;


public class BiofabServlet extends HttpServlet {

    
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {
            processRequest(request, response);
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {
            processRequest(request, response);
    }

    /** 
     * Processes requests for both HTTP <code>GET</code> and <code>POST</code> methods.
     * @param request servlet request
     * @param response servlet response
     * @throws ServletException if a servlet-specific error occurs
     * @throws IOException if an I/O error occurs
     */
    protected void processRequest(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {

        ServletContext context = getServletConfig().getServletContext();

//        context.log("CLASSNAME: " + this.getClass().getSimpleName());

        String path = stripServletNameFromPath(request.getRequestURI());
        Method methods[] = this.getClass().getDeclaredMethods();

//        context.log("Get request for: " + path);
//        context.log("Full path: " + request.getRequestURI());

        boolean found_method = false;

        int i, j;
        Method method;
        boolean web_accessible;
        for(i=0; i < methods.length; i++) {
            method = methods[i];

            if(!path.equals(method.getName())) {
//                context.log("  --Trying: " + method.getName());
                continue;
            }

//            context.log("  --FOUND MATCH: " + method.getName());

            web_accessible = false;
            if((method.getModifiers() & Modifier.PUBLIC) > 0) {
                Annotation[] annots = method.getDeclaredAnnotations();
                for(j=0; j < annots.length; j++) {
                    String annot_name = annots[j].annotationType().getSimpleName();
                    if(annot_name.equals("WebAccessible")) {
                        web_accessible = true;
                        break;
                    }
                }
            }

            if(web_accessible) {
                try {
                    method.invoke(this, request, response);
                    found_method = true;
                    context.log("Invoking!");
                } catch (Exception ex) {
                    Logger.getLogger(BiofabServlet.class.getName()).log(Level.SEVERE, null, ex);
                }
            } else {
                context.log("Not web accessible");
            }

        }


        if(!found_method) {
            response.sendError(response.SC_NOT_FOUND, request.getRequestURI());
        }

    }

    protected String[] getPathParams(String path) {

        String endPart = stripServletNameFromPath(path);

        return endPart.split("/");

    }

    protected String stripServletNameFromPath(String path) {


        Pattern pattern = Pattern.compile(".*/" + this.getClass().getSimpleName() + "/");
        Matcher matcher = pattern.matcher(path);

        String out = matcher.replaceFirst("");

        return out;
    }

    // send a json error
    protected void jsonError(HttpServletResponse response, String msg) throws IOException {

        Gson gson = new Gson();
        JSONResponse jsonResponse = new JSONResponse("error", msg);

        response.setContentType("text/plain;charset=UTF-8");
        response.setStatus(400);

        PrintWriter out = response.getWriter();
        try {
            out.println(gson.toJson(jsonResponse));
        } finally {
            out.close();
        }

    }

    // send a json success response
    protected void jsonSuccess(HttpServletResponse response, String msg) throws IOException {

        Gson gson = new Gson();
        JSONResponse jsonReponse = new JSONResponse("success", msg);

        response.setContentType("text/plain;charset=UTF-8");
        response.setStatus(200);

        PrintWriter out = response.getWriter();
        try {
            out.println(gson.toJson(jsonReponse));
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
        return "Servlet for various web services related to the BIOFAB Galapagos Method ";
    }// </editor-fold>

}
