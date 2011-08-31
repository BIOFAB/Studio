package org.biofab.studio.model;

import java.io.Serializable;
import java.util.HashSet;
import java.util.Set;
import javax.persistence.*;
//import org.hibernate.annotations.Fetch;
//import org.hibernate.annotations.FetchMode;

/**
 *
 * 
 */

@Entity
public class Feature extends Base implements Serializable
{
    @Id
    Long id;

    String description;
    String dna_sequence;
    String genbank_type;
    String biofab_type;

    @ManyToMany(mappedBy="features")
//    @Fetch(FetchMode.JOIN)
    Set<Design> designs;

    public Set<Design> getDesigns()
    {
        return designs;
    }

    public void setDesigns(Set<Design> designs)
    {
        this.designs = designs;
    }
 
    public String getBiofab_type()
    {
        return biofab_type;
    }

    public void setBiofab_type(String biofab_type)
    {
        this.biofab_type = biofab_type;
    }

    public String getDescription()
    {
        return description;
    }

    public void setDescription(String description)
    {
        this.description = description;
    }

    public String getGenbank_type()
    {
        return genbank_type;
    }

    public void setGenbank_type(String genbank_type)
    {
        this.genbank_type = genbank_type;
    }

    public Long getId()
    {
        return id;
    }

    public void setId(Long id)
    {
        this.id = id;
    }

    public String getDna_sequence()
    {
        return dna_sequence;
    }

    public void setDna_sequence(String seq)
    {
        this.dna_sequence = seq;
    }
}
