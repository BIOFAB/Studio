/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.studio;

/**
 *
 * @author root
 */
public class UploadSequenceResponse {

    public String sequence = "";
    public String filename = "";

    public UploadSequenceResponse(String seq, String filename) {
        this.sequence = seq;
        this.filename = filename;
    }


}
