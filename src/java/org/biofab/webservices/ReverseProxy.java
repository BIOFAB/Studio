/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.net.URLDecoder;
import org.biofab.webservices.annotations.WebAccessible;
import org.biofab.webservices.config.ProxyAllowedHost;
import org.biofab.webservices.config.ProxyAllowedHosts;

@WebServlet(name="ReverseProxy", urlPatterns={"/ReverseProxy/*"})
public class ReverseProxy extends BiofabServlet {

    private ProxyAllowedHosts allowedHosts = null;

    
    @WebAccessible
    public void request(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {

        response.setContentType("text/plain;charset=UTF-8");

        String url = request.getParameter("forward_url");

        if((url == null) || (url.equals(""))) {
             response.sendError(response.SC_BAD_REQUEST, "no forward_url specified");
             return;
        }

        url = URLDecoder.decode(url, "UTF-8");

        try {
                String reqURL = request.getRequestURI();
/*
                if (reqURL.endsWith("/")) {
                        reqURL = reqURL + "index.htm";
                }
*/
                URL fwdURL = new URL(url);

                // Only allow certain hosts
                if(!allowedHosts.is_allowed(fwdURL.getHost(), fwdURL.getPort())) {
                    response.sendError(response.SC_FORBIDDEN, "host not allowed");
                    return;
                }

//                System.out.println("Yay!");

                HttpURLConnection fwdConnection =
                        (HttpURLConnection) fwdURL.openConnection();
/*
                System.out.println("fwdConnection = " + fwdConnection.toString());
                System.out.println("url = " + url.toString());
*/
                for (String key : fwdConnection.getHeaderFields().keySet()) {
                    if(key == null) {
                        continue;
                    }
                    response.setHeader(key, fwdConnection.getHeaderField(key));
                }

                copy(fwdConnection.getInputStream(), response.getOutputStream());
                
        } catch (Exception e) {
                response.sendError(response.SC_NOT_FOUND, "java exception");
                e.printStackTrace();
        }



    }

    @Override
    public void init() {
        this.allowedHosts = new ProxyAllowedHosts();
    }


    private void copy(InputStream in, OutputStream out) throws IOException {
            int len = 0;
            byte[] buf = new byte[1024];

            while ((len = in.read(buf)) > 0) {
                    out.write(buf, 0, len);
            }

            in.close();
    }

    /** 
     * Returns a short description of the servlet.
     * @return a String containing servlet description
     */
    @Override
    public String getServletInfo() {
        return "The reverse proxy";
    }// </editor-fold>

}
