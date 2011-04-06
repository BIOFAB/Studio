/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices.protocol;

/**
 *
 * @author juul
 */
public class DatabaseParams {

    public String include_default = null; // can be "include" or "exclude" or null
    public DatabaseParamHash matching = new DatabaseParamHash();
    public String[] include = null;
    public String[] exclude = null;
    public Integer offset = null;
    public Integer limit = null;

    public DatabaseParams() {

    }

    /*
    public DatabaseParams mergeWith(DatabaseParams other) {
        if(include_default == null) {
            include_default = other.include_default;
        }
        if(offset == null) {
            offset = other.offset;
        }
        if(limit == null) {
            limit = other.limit;
        }

        if(other.include != null) {
            if(include == null) {
                include = other.include;
            } else {
                String cur;
                f
            }
        }
        return this;
    }
    */
}
