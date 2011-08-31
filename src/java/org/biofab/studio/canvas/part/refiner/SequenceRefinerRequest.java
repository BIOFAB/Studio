/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.studio.canvas.part.refiner;

import org.biofab.studio.JSONRequest;

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
