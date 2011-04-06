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
public class RBSDesignerRequest implements JSONRequest {


    public String sequence = "";
    public Integer start_codon_offset = null;


    public RBSDesignerRequest() {

    }

    public boolean validate() {
        if((this.sequence == null) || (this.sequence.equals(""))) {
            return false;
        }
        if((this.start_codon_offset == null) || (this.start_codon_offset < 0)) {
            return false;
        }
        return true;
    }

}

