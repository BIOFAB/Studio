/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.studio.model;

import java.io.Serializable;
import java.util.HashSet;
import java.util.Set;
import javax.persistence.*;
//import org.hibernate.annotations.Fetch;
//import org.hibernate.annotations.FetchMode;

@Entity
@Table(name="design")
public class Design extends Base implements Serializable
{

    // TODO changed some of the columns to allow null. should reset that
    // TODO figure out how to get e.g. dna_molecule_type_id to receive data from gson
    //      probably it's as simple as creating a local var with same name
    //      unless hibernate dislikes that

    @Id
    Long id;
    String dna_sequence;
    String biofab_id;

    @OneToOne
    @JoinColumn(name="design_type_id")
//    @Fetch(FetchMode.JOIN)
    DesignType type;

    @ManyToMany
//    @Fetch(FetchMode.JOIN)
    Set<Feature> features;

    public String getBiofab_id()
    {
        return biofab_id;
    }

    public void setBiofab_id(String biofab_id)
    {
        this.biofab_id = biofab_id;
    }

    public Set<Feature> getFeatures()
    {
        return features;
    }

    public void setFeatures(Set<Feature> features)
    {
        this.features = features;
    }

    public DesignType getType()
    {
        return type;
    }

    public Long getId()
    {
        return id;
    }

    public void setId(Long id)
    {
        this.id = id;
    }

    public void setType(DesignType type)
    {
        this.type = type;
    }

    public String getDna_sequence()
    {
        return dna_sequence;
    }

    public void setDna_sequence(String seq)
    {
        dna_sequence = seq;
    }
}
