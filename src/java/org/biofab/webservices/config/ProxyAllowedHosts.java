/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices.config;

import java.util.ArrayList;

/**
 *
 * @author juul
 */
public class ProxyAllowedHosts {

    private ArrayList<ProxyAllowedHost> allowedHosts;

    public ProxyAllowedHosts() {
        // TODO get rules from JSON file and allow them to be regexes
        this.allowedHosts = new ArrayList<ProxyAllowedHost>();
        Integer[] ports = {80};
        this.allowedHosts.add(new ProxyAllowedHost("google.com", ports));
        this.allowedHosts.add(new ProxyAllowedHost("www.google.com", ports));
    }


    public boolean is_allowed(String hostname, Integer port) {
        if(port <= 0) {
            port = 80;
        }
        for(ProxyAllowedHost curHost : allowedHosts) {
            if(curHost.matches(hostname, port)) {
                return true;
            }
        }
        return false;
    }


}
