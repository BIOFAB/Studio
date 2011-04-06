/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices.config;

/**
 *
 * @author juul
 */
public class ProxyAllowedHost {

    public String hostname;
    public Integer[] ports;

    public ProxyAllowedHost(String hostname, Integer[] ports) {
        this.hostname = hostname;
        this.ports = ports;
    }

    public boolean matches(String hostname, Integer port) {

        if(!hostname.equals(this.hostname)) {
            return false;
        }

        for(Integer curPort : this.ports) {
            if(port == curPort) {
                return true;
            }
        }
        return false;
    }

}

