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

/*
 *
 *
 *
 */

@Entity
@Table(name="design_type")
public class DesignType extends Base implements Serializable
{

    @Id
    Long id;

    String name;
    String prefix; // prefix

    @OneToOne(mappedBy="type")
//    @Fetch(FetchMode.JOIN)
    Design design;

    public String getName()
    {
        return name;
    }

    public void setName(String name)
    {
        this.name = name;
    }

    public String getPrefix()
    {
        return prefix;
    }

    public void setPrefix(String prefix)
    {
        this.prefix = prefix;
    }
}
