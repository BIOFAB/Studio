/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.studio.hibernate;

import java.util.Iterator;
import java.util.List;
import java.util.Vector;
import org.biofab.model.Design;
import org.hibernate.HibernateException;
import org.hibernate.Query;
import org.hibernate.Session;

/**
 *
 * @author juul
 */
public class TestHibernate {

    public List executeHQLQuery(String hql) {
        List resultList = null;
        try {
            Session session = HibernateUtil.getSessionFactory().openSession();
            session.beginTransaction();
            Query q = session.createQuery(hql);
            resultList = q.list();
            session.getTransaction().commit();
        } catch (HibernateException he) {
            he.printStackTrace();
        }
        return resultList;
    }

    public void printResultList(List list) {
        for (Object o : list) {
            Design dna_molecule = (Design) o;
            System.out.println("====================================================");
            System.out.println("dna_molecule id = " + dna_molecule.getId().toString());
            System.out.println("dna_molecule seq = " + dna_molecule.getDna_sequence());
            System.out.println("type = " + dna_molecule.getType());
/*
            Iterator iter = dna_molecule.getFeatures().iterator();
            Feature curFeature;
            while(iter.hasNext()) {
                curFeature = (Feature) iter.next();
                System.out.println("    feature = " + curFeature.getId().toString());
            }
            iter = dna_molecule.getRBSs().iterator();
            RBS curRBS;
            while(iter.hasNext()) {
                curRBS = (RBS) iter.next();
                System.out.println("    RBS = " + curRBS.getSeq());
                Iterator iter2 = curRBS.getDNAMolecules().iterator();
                while(iter2.hasNext()) {
                    Design cur_dnamolecule = (Design) iter2.next();
                    System.out.println("        dnamolecule seq = " + cur_dnamolecule.getSeq());
                }
            }
 * */
        }

    }
}
