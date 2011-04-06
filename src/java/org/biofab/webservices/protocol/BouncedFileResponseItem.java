/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices.protocol;

/**
 * Note that the actual response is sometimes a JSON array of these items
 *
 * @author juul
 */
public class BouncedFileResponseItem {

    public String fileName;
    public Long size; // in bytes
    public String contentType;
    public String content;

    public BouncedFileResponseItem() {
        
    }

}
