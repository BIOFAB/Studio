/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices;

import com.google.gson.Gson;
import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.commons.fileupload.FileItem;
import org.apache.commons.fileupload.FileUploadException;
import org.apache.commons.fileupload.disk.DiskFileItemFactory;
import org.apache.commons.fileupload.servlet.ServletFileUpload;
import org.apache.commons.io.IOUtils;
import org.biofab.webservices.annotations.WebAccessible;
import org.biofab.webservices.protocol.BouncedFileResponseItem;
import org.biofab.webservices.protocol.UploadSequenceResponse;
import org.biojava.bio.BioException;
import org.biojavax.Namespace;
import org.biojavax.RichObjectFactory;
import org.biojavax.bio.seq.RichSequence;
import org.biojavax.bio.seq.RichSequenceIterator;


@WebServlet(name="Upload", urlPatterns={"/Upload/*"})
public class Upload extends BiofabServlet {


    // sends the file contents right back as JSON
    @WebAccessible
    public void classicBouncer(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

        if(!ServletFileUpload.isMultipartContent(request)) {
             jsonError(response, "no file uploaded, form is not multipart");
             return;
        }



        // TODO should be in settings file somewhere
        int maxSize = 1024 * 1024; // limit to 1 meg

         // Create a factory for disk-based file items
        DiskFileItemFactory factory = new DiskFileItemFactory();

        factory.setSizeThreshold(maxSize); // max size to keep in memory
        factory.setRepository(new File("/tmp")); // where to store files larger than that

        ServletFileUpload upload = new ServletFileUpload(factory);

        upload.setSizeMax(maxSize); // max upload size

        ArrayList<BouncedFileResponseItem> responseItems = new ArrayList<BouncedFileResponseItem>();
        BouncedFileResponseItem responseItem;

        try {
            List<FileItem> fileItems = upload.parseRequest(request);

            Iterator iter = fileItems.iterator();
            while (iter.hasNext()) {
                FileItem fileItem = (FileItem) iter.next();
                if (!fileItem.isFormField()) {
                    String fieldName = fileItem.getFieldName();
                    System.out.println("fieldName = " + fieldName);

                    responseItem = new BouncedFileResponseItem();
                    responseItem.fileName = fileItem.getName();
                    responseItem.contentType = fileItem.getContentType();
                    responseItem.size = fileItem.getSize();
                    responseItem.content = fileItem.getString();
                    responseItems.add(responseItem);
                }
            }

        } catch (FileUploadException ex) {
            Logger.getLogger(Upload.class.getName()).log(Level.SEVERE, null, ex);
        }

        if(responseItems.isEmpty()) {
            jsonError(response, "no files included in request");
            return;
        }

        Gson gson = new Gson();

        String json = gson.toJson(responseItems.toArray());

        response.setStatus(400);

        response.setContentType("text/plain;charset=UTF-8");
        PrintWriter out = response.getWriter();
        try {
            out.println(json);
        } finally {
            out.close();
        }

    }

// sends the file contents right back as JSON
    @WebAccessible
    public void xhrBouncer(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

        BufferedReader reader = request.getReader();

        String content = "";
        String line;
        for(;;) {
            line = reader.readLine();
            if(line == null) {
                break;
            }
            content += line;
        }

        BouncedFileResponseItem responseItem = new BouncedFileResponseItem();

        String contentType = request.getHeader("Content-Type");
        if(contentType == null) {
            contentType = "text/plain";
        }

        String fileName = request.getHeader("X-File-Name");
        if(fileName == null) {
            fileName = "unnamed";
        }

        responseItem.size = (long) content.getBytes("UTF8").length; // TODO the "UTF8-LE" may be needed to get rid of the byte order mark
        responseItem.contentType = contentType;
        responseItem.content = content;
        responseItem.fileName = fileName;

        Gson gson = new Gson();

        String json = gson.toJson(responseItem);

        response.setStatus(200);

        response.setContentType("text/plain;charset=UTF-8");
        PrintWriter out = response.getWriter();
        try {
            out.println(json);
        } finally {
            out.close();
        }

    }


    @WebAccessible
    public void sequence(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {

        ServletContext context = getServletConfig().getServletContext();

        // TODO change back to text/plain
        response.setContentType("text/html;charset=UTF-8");
        PrintWriter out = response.getWriter();

        if(!ServletFileUpload.isMultipartContent(request)) {
             response.sendError(response.SC_BAD_REQUEST, "no file uploaded, form is not multipart");
             return;
        }

        int maxSize = 256 * 1024; // limit to 256 kbytes

         // Create a factory for disk-based file items
        DiskFileItemFactory factory = new DiskFileItemFactory();

        factory.setSizeThreshold(maxSize); // max size to keep in memory
        factory.setRepository(new File("/tmp")); // where to store files larger than that

        ServletFileUpload upload = new ServletFileUpload(factory);

        upload.setSizeMax(maxSize); // max upload size

        boolean gotFile = false;

        InputStream fileStream = null;
        String fileName = null;
        String contentType = null;
        long sizeInBytes = -1;

        try {
            List<FileItem> items = upload.parseRequest(request);


            Iterator iter = items.iterator();
            while (iter.hasNext()) {
                FileItem item = (FileItem) iter.next();
                if (!item.isFormField()) {
                    String fieldName = item.getFieldName();
                    if(fieldName.equals("sequence_file")) {
                        fileName = item.getName();
                        contentType = item.getContentType();
                        sizeInBytes = item.getSize();
                        fileStream = item.getInputStream();
                        gotFile = true;
                    }

                }
            }

        } catch (FileUploadException ex) {
            Logger.getLogger(Upload.class.getName()).log(Level.SEVERE, null, ex);
        }

        if(!gotFile) {
             response.sendError(response.SC_BAD_REQUEST, "no file with field name 'sequence_file' uploaded");
             return;
        }
/*
        StringWriter writer = new StringWriter();
        IOUtils.copy(fileStream, writer);
        String sequence = writer.toString();
*/

        String sequence = readFASTA(fileStream);
        if(sequence == null) {
             response.sendError(response.SC_BAD_REQUEST, "could not read file: only FASTA files supported");
             return;
        }

        UploadSequenceResponse resp = new UploadSequenceResponse(sequence, fileName);

        Gson gson = new Gson();

        String json_resp = gson.toJson(resp);

        try {
            // TODO dirty hack, fix this
            out.println("<html>");
            out.println("<head>");
            out.println("<style type='text/css'>body, html {font-family: sans-serif}</style>");
            out.println("<script type='text/javascript'>");
            out.println("var json_str = '" + json_resp + "';");
            out.println("parent.on_file_uploaded(json_str);");
            out.println("</script>");
            out.println("</head>");
            out.println("<body></body>");
            out.println("</html>");

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
                out.println("<title>File upload</title>");
                out.println("</head>");
                out.println("<body>");
                out.println("<h2>Choose file to upload</h2>");
                out.println("<p>Supported file formats: *.fasta</p>");
                out.println("<form action='/java/Galapagos_Method/Upload/sequence' method='post' enctype='multipart/form-data'>");
                out.println("<p>File: <input type='file' name='sequence_file' /></p>");
                out.println("<p><input type='submit' value='Upload' /></p>");
                out.println("</form>");
                out.println("</body>");
                out.println("</html>");

            } finally {
                out.close();
            }
        }
    }


    private String readFASTA(InputStream stream) {

        ServletContext context = getServletConfig().getServletContext();

        RichSequence sequence = null;

        BufferedReader reader = null;

        try {
            reader = new BufferedReader(new InputStreamReader(stream));

            Namespace ns = RichObjectFactory.getDefaultNamespace();

            RichSequenceIterator sequences = RichSequence.IOTools.readFastaDNA(reader, ns);

            while (sequences.hasNext()) {
                sequence = sequences.nextRichSequence();
                return sequence.seqString();
            }

        } catch (NoSuchElementException ex) {
            context.log("No FASTA data contained in file");
            return null;
        } catch (BioException ex) {
            context.log("FASTA data could not be read from file.\nAre you sure this is a FASTA file containing DNA?");
            return null;
        } finally {
            if(reader != null) {
                try {
                    reader.close();
                } catch (IOException ex) {
                    context.log("Error closing stream");
                    return null;
                }
            }

        }
        return null;
    }

    /**
     * Returns a short description of the servlet.
     * @return a String containing servlet description
     */
    @Override
    public String getServletInfo() {
        return "Upload handler";
    }// </editor-fold>

}
