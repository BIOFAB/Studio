/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.model;

import javax.persistence.*;

/**
 *
 * @author juul
 */

@Entity
//@Table(name = "constructs")
public class Construct {

    @Id
    long id;

    @Basic
    String seq = "";



}
