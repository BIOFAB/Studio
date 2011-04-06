/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices.protocol;

/**
 *
 * @author root
 */
public class SequenceRefinerRequest implements JSONRequest {


    public String sequence = "";


    public SequenceRefinerRequest() {

    }

    public boolean validate() {
        if((this.sequence == null) || (this.sequence.equals(""))) {
            return false;
        }
        return true;
    }

}
