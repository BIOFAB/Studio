package org.biofab.studio;



/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

import java.io.IOException;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Time;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.ArrayList;

import org.biojava.bio.BioException;
import org.biojava.bio.seq.DNATools;
import org.biojava.bio.seq.Feature;
import org.biojava.bio.seq.StrandedFeature;
import org.biojava.bio.symbol.RangeLocation;

import org.biojavax.Namespace;
import org.biojavax.RichObjectFactory;
import org.biojavax.SimpleComment;
import org.biojavax.SimpleNote;
import org.biojavax.SimpleRichAnnotation;
import org.biojavax.bio.seq.RichSequence;

//import org.biofab.model.Plasmid;
//import org.biofab.model.ConstructPerformance;
//import org.biofab.model.Read;
//import org.biofab.model.CytometerRead;
//import org.biofab.model.Instrument;
//import org.biofab.model.Measurement;
//import org.biofab.model.CytometerMeasurement;


//import org.sbolstandard.libSBOLj.SBOLutil;
//import org.sbolstandard.libSBOLj.DnaComponent;
//import org.sbolstandard.libSBOLj.Library;
//import org.sbolstandard.libSBOLj.SBOLservice;


@WebServlet(name="PlasmidsServlet", urlPatterns={"/plasmids/*"})
public class PlasmidsServlet extends DataAccessServlet
{
    String                  _plasmidId;
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
        _plasmidId = request.getParameter("id");
        _format = request.getParameter("format");
        _request = request;
        _response = response;
        
        //TODO stronger validation of plasmidId
        
        if(_plasmidId == null)
        {
            fetchPlasmids();
        }
        else
        {
            fetchPlasmidDesign();
        }

    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException
    {
        textError(response, "Post requests are not serviced by the Constructs web service");
    }

    @Override
    protected void doPut(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException
    {
        textError(response, "Put requests are not serviced by the Constructs web service");
    }

    // Utility Functions
    protected void fetchPlasmids()
    {
        String              responseString = null;
        String              query = null;
        ResultSet           resultSet;
        String              biofabId;
        String              description;
        ArrayList<Plasmid>  plasmids = null;
        Plasmid             plasmid = null;
        
        plasmids = new ArrayList<Plasmid>();
        query = "SELECT * FROM private.plasmid_view";
        resultSet = fetchResultSet(query);
        
        try
        {
            while (resultSet.next())
            {
                biofabId = resultSet.getString("biofab_id");
                description = resultSet.getString("description");
            
                plasmid = new Plasmid(biofabId, description);
                plasmids.add(plasmid);
            }

            if(_format == null || _format.equalsIgnoreCase("json"))
            {
               responseString = generateJSON(plasmids.toArray());
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
    
    protected void fetchPlasmidDesign()
    {
        Statement       statement = null;
        String          responseString = null;
        RichSequence    richSequence = null;
        Feature         feature = null;
        String          newID;
        String          componentID;
        Namespace       ns = RichObjectFactory.getDefaultNamespace();
        ResultSet       resultSet = null;
        Statement       featuresStatement;
        ResultSet       annotationsResultSet;
        String          biofabId;
        String          dnaSequence;
        String          query;

        if(_plasmidId != null && _plasmidId.length() > 0)
        {
            query = "SELECT * FROM private.plasmid_sequence_view WHERE UPPER(biofab_id) = '" + _plasmidId.toUpperCase() + "'";
            resultSet = fetchResultSet(query);
            
            try
            {
                while (resultSet.next())
                {
                    biofabId = resultSet.getString("biofab_id");
                    dnaSequence = resultSet.getString("nucleotides");
                    query = "SELECT * FROM private.plasmid_annotation_view WHERE plasmid_biofab_id = '" + biofabId + "'";
                    
                    try
                    {
                        richSequence = RichSequence.Tools.createRichSequence(biofabId, DNATools.createDNA(dnaSequence));
                        annotationsResultSet = fetchResultSet(query);
                        addFeatures(richSequence, annotationsResultSet);
                        richSequence.setCircular(true);
                        
                        if(_format == null || _format.equalsIgnoreCase("genbank"))
                        {
                            _response.setContentType("text/plain");
                            RichSequence.IOTools.writeGenbank(_response.getOutputStream(), richSequence, ns);
                        }
                        else
                        {
                        
                            if(_format.equalsIgnoreCase("insd"))
                            {
                                _response.setContentType("text/xml");
                                RichSequence.IOTools.writeINSDseq(_response.getOutputStream(), richSequence, ns);
                            }
                            else
                            {
                               _response.setContentType("text/plain");
                                RichSequence.IOTools.writeGenbank(_response.getOutputStream(), richSequence, ns);
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        textError(_response, "Error while fetching data: " + ex.getMessage());
                    }
                }
            }
            catch (SQLException ex)
            {
                textError(_response, "Error while fetching data: " + ex.getMessage());
            }
        }
    }
    
    protected ResultSet fetchResultSet(String query)
    {
        Statement           statement = null;
        ResultSet           resultSet = null;
  
        try
        {
            _connection = DriverManager.getConnection(_jdbcDriver, _user, _password);
            statement = _connection.createStatement();
            resultSet = statement.executeQuery(query);
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
        finally
        {
            try
            {
                if(_connection != null)
                {
                    _connection.close();
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
        
        return resultSet;
    }



    protected void addComment(RichSequence seq, String comment)
    {
        seq.addComment(new SimpleComment(comment, 0));
    }

    protected void addFeatures(RichSequence sequence, ResultSet features) throws SQLException, BioException
    {
        String featureType;
        String noteType;
        String noteValue;
        int start;
        int stop;

        while (features.next())
        {
            featureType = features.getString("feature_type");
            noteValue = features.getString("feature_description");
            start = features.getInt("start");
            stop = features.getInt("stop");

            if(featureType.equalsIgnoreCase("CDS"))
            {
                noteType = "gene";
            }
            else
            {
                noteType = "label";
            }

            SimpleRichAnnotation annotation = new SimpleRichAnnotation();

            annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm(noteType), noteValue, 0));
            StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
            featureTemplate.annotation = annotation;
            featureTemplate.location = new RangeLocation(start, stop);
            featureTemplate.source = "BIOFAB";
            featureTemplate.strand = StrandedFeature.POSITIVE;
            featureTemplate.type = featureType;
            sequence.createFeature(featureTemplate);
        }
    }
}
