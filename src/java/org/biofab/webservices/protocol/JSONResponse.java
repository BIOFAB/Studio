/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices.protocol;

/**
 *
 * @author juul
 */
public class JSONResponse {

    public String status = null;
    public String msg = null;

    public JSONResponse(String status, String msg) {
        this.status = status;
        this.msg = msg;
    }

}
