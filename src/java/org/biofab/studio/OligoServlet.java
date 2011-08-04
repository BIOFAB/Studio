package org.biofab.studio;



/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

import org.biofab.studio.model.Oligo;
import java.io.IOException;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.DriverManager;
import java.sql.ResultSet;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.ArrayList;


@WebServlet(name="OligosServlet", urlPatterns={"/oligos/*"})
public class OligoServlet extends DataAccessServlet
{
    String                  _biofabId;
    String                  _format;
    String                  _queryString;
    HttpServletRequest      _request;
    HttpServletResponse     _response;
    
    
    @Override
    public void init()
    {

    }

    @Override 
    public void destroy()
    {
        
    }

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException
    {
        _biofabId = request.getParameter("id");
        _format = request.getParameter("format");
        _request = request;
        _response = response;
        
        //TODO stronger validation of plasmidId
        
        if(_biofabId == null)
        {
            fetchOligos();
        }
        else
        {
            fetchOligos();
        }

    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException
    {
        textError(response, "Post requests are not serviced by the Oligos web service");
    }

    @Override
    protected void doPut(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException
    {
        textError(response, "Put requests are not serviced by the Oligos web service");
    }

    // Utility Functions
    protected void fetchOligos()
    {
        String              responseString = null;
        String              query = null;
        ResultSet           resultSet;
        String              biofabId;
        String              description;
        int                 index;
        String              dnaSequence;
        ArrayList<Oligo>    oligos = null;
        Oligo               oligo = null;
        
        oligos = new ArrayList<Oligo>();
        query = "SELECT * FROM private.oligo_view";
        resultSet = fetchResultSet(query);
        
        try
        {
            while (resultSet.next())
            {
                index = resultSet.getInt("index");
                biofabId = resultSet.getString("biofab_id");
                description = resultSet.getString("description");
                dnaSequence = resultSet.getString("dna_sequence");
                
                oligo = new Oligo(index, biofabId, description, dnaSequence);
                oligos.add(oligo);
            }

            if(_format == null || _format.equalsIgnoreCase("json"))
            {
               responseString = generateJSON(oligos.toArray());
               this.textSuccess(_response, responseString);
            }
            else
            {
//                if(format.equalsIgnoreCase("csv"))
//                {
//                   responseString = generateCSV(dnaComponents);
//                   this.textSuccess(response, responseString);
//                }
//                else
//                {
//                   responseString = generateJSON(dnaComponents.toArray());
//                   this.textSuccess(response, responseString);
//                }
            }
        }
        catch (SQLException ex)
        {
            if(_format != null && _format.length() > 0)
            {
                if(_format.equalsIgnoreCase("json"))
                {
                    jsonError(_response, "Error while fetching data: " + ex.getMessage());

                }
                else
                {
                    textError(_response, "Error while fetching data: " + ex.getMessage());
                }
            }
            else
            {
                textError(_response, "Error while fetching data: " + ex.getMessage());
            }
        }
    }
}
