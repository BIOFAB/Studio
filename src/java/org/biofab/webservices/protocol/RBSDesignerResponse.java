/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices.protocol;

/**
 *
 * @author root
 */
public class RBSDesignerResponse {


    public String output = "";
    public String error = null;
    public String stack_trace = null;


    public RBSDesignerResponse(String output) {

        this.output = output;

    }


}
