/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.studio;

import com.google.gson.Gson;

import java.io.IOException;
import java.io.PrintWriter;
import java.sql.Statement;
import java.sql.DriverManager;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.logging.Level;
import java.util.logging.Logger;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
 
import org.biofab.studio.JSONResponse;


public class DataAccessServlet extends HttpServlet
{
    String                  _jdbcDriver = "jdbc:postgresql://localhost:5432/biofab";
    String                  _user = "biofab";
    String                  _password = "fiobab";
    Connection              _connection = null;
    String                  _schema = "private";
    String                  _format;
    HttpServletRequest      _request;
    HttpServletResponse     _response;


    
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException 
    {
       
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException 
    {
      
    }

    
    //
    // Utility Methods
    //
    
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

    
    protected void textError(HttpServletResponse response, String msg)
    {
        response.setContentType("text/plain;charset=UTF-8");
        response.setStatus(400);
        PrintWriter out = null;

        try
        {
            out = response.getWriter();
            out.println(msg);
        }
        catch (IOException ex)
        {
            Logger.getLogger(DataAccessServlet.class.getName()).log(Level.SEVERE, null, ex);
        }
        finally
        {
            out.close();
        }
    }

    protected void jsonError(HttpServletResponse response, String msg)
    {
        Gson gson = new Gson();
        JSONResponse jsonResponse = new JSONResponse("error", msg);

        response.setContentType("text/plain;charset=UTF-8");
        response.setStatus(400);
        PrintWriter out = null;

        try
        {
            out = response.getWriter();
            out.println(gson.toJson(jsonResponse));
        }
        catch (IOException ex)
        {
            Logger.getLogger(DataAccessServlet.class.getName()).log(Level.SEVERE, null, ex);
        }
        finally
        {
            out.close();
        }
    }

    protected void textSuccess(HttpServletResponse response, String msg)
    {
        response.setContentType("text/plain;charset=UTF-8");
        response.setStatus(200);
        PrintWriter out = null;

        try
        {
            out = response.getWriter();
            out.println(msg);
        }
        catch (IOException ex)
        {

            Logger.getLogger(DataAccessServlet.class.getName()).log(Level.SEVERE, null, ex);
        }
        finally
        {
            out.close();
        }
    }

    protected void jsonSuccess(HttpServletResponse response, String msg)
    {
        Gson gson = new Gson();
        JSONResponse jsonReponse = new JSONResponse("success", msg);
        response.setContentType("text/plain;charset=UTF-8");
        response.setStatus(200);
        PrintWriter out = null;

        try
        {
            out = response.getWriter();
            out.println(gson.toJson(jsonReponse));
        }
        catch (IOException ex)
        {
            
            Logger.getLogger(DataAccessServlet.class.getName()).log(Level.SEVERE, null, ex);
        }
        finally
        {
            out.close();
        }
    }

    protected String generateJSON(Object object)
    {
        Gson    gson;
        String  responseString;

        gson = new Gson();
        responseString = gson.toJson(object);

        if(responseString == null || responseString.length() == 0)
        {
            //Throw exception
        }

        return responseString;
    }
}