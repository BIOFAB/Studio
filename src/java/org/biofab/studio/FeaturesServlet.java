package org.biofab.studio;



/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

import org.biofab.studio.model.Feature;
import java.io.IOException;
import java.sql.SQLException;
import java.sql.ResultSet;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.ArrayList;


@WebServlet(name="FeatureServlet", urlPatterns={"/features/*"})
public class FeaturesServlet extends StudioServlet
{
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
        _request = request;
        _response = response;
        
        fetchFeatures(); 
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException
    {
        textError(response, "Post requests are not serviced by the Features web service");
    }

    @Override
    protected void doPut(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException
    {
        textError(response, "Put requests are not serviced by the Features web service");
    }

    // Utility Functions
    protected void fetchFeatures()
    {
        String              responseString = null;
        String              query = null;
        ResultSet           resultSet;
        String              biofabId;
        String              genbankType;
        String              biofabType;
        String              description;
        int                 index;
        String              dnaSequence;
        ArrayList<Feature>  features = null;
        Feature             feature = null;
        
        features = new ArrayList<Feature>();
        query = "SELECT * FROM private.feature_view";
        resultSet = fetchResultSet(query);
        
        try
        {
            while (resultSet.next())
            {
                index = resultSet.getInt("index");
                biofabId = resultSet.getString("biofab_id");
                description = resultSet.getString("description");
                dnaSequence = resultSet.getString("dna_sequence");
                genbankType = resultSet.getString("genbank_type");
                biofabType = resultSet.getString("biofab_type");
                feature = new Feature(index, biofabId, genbankType, biofabType, description, dnaSequence);
                features.add(feature);
            }

            if(_format == null || _format.equalsIgnoreCase("json"))
            {
               responseString = generateJSON(features.toArray());
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
