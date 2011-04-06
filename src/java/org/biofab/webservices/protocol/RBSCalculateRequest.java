/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices.protocol;

/**
 *
 * @author juul
 */
/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */


/**
 *
 * @author root
 */
public class RBSCalculateRequest implements JSONRequest {


    public String sequence = "";
    //public Integer start_codon_offset = null;


    public RBSCalculateRequest() {

    }

    public boolean validate() {
        if((this.sequence == null) || (this.sequence.equals(""))) {
            return false;
        }
        return true;
    }

}

