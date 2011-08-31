/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.studio.hibernate;

import java.util.List;

/**
 *
 * @author juul
 */
public class Tester {

    public static void main(String args[]) {
        TestHibernate t = new TestHibernate();
        List l = t.executeHQLQuery("from DNAMolecule");
        t.printResultList(l);
    }
}
