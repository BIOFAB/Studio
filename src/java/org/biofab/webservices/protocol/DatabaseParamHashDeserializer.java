/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices.protocol;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import java.lang.reflect.Type;
import java.util.Iterator;
import java.util.Map.Entry;
import java.util.Set;

/**
 *
 * @author juul
 */
public class DatabaseParamHashDeserializer implements JsonDeserializer<DatabaseParamHash> {

    @Override
    public DatabaseParamHash deserialize(JsonElement json, Type typeOfT, JsonDeserializationContext context) {
        DatabaseParamHash h = new DatabaseParamHash();

        Set<Entry<String, JsonElement>> entries = json.getAsJsonObject().entrySet();
        Entry<String, JsonElement> entry;
        Iterator it = entries.iterator();
        while(it.hasNext()) {
            entry = (Entry<String, JsonElement>) it.next();
            h.put(entry.getKey(), entry.getValue().getAsJsonPrimitive());
        }
        
        return h;
    }

}
