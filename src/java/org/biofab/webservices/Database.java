/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices;

import com.aetrion.activesupport.Inflection;
import com.google.gson.ExclusionStrategy;
import com.google.gson.FieldAttributes;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonPrimitive;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.annotation.Annotation;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.biofab.hibernate.HibernateUtil;
import org.biofab.model.Base;
import org.biofab.model.DNAMolecule;
import org.biofab.webservices.annotations.WebAccessible;
import org.biofab.webservices.protocol.DatabaseParamHash;
import org.biofab.webservices.protocol.DatabaseParamHashDeserializer;
import org.biofab.webservices.protocol.DatabaseParams;
import org.biofab.webservices.protocol.JSONResponse;
import org.hibernate.Criteria;
import org.hibernate.FetchMode;
import org.hibernate.HibernateException;
import org.hibernate.Query;
import org.hibernate.Session;
import org.hibernate.criterion.Restrictions;

/**
 *
 * @author juul
 */
@WebServlet(name="Database", urlPatterns={"/Database/*"})
public class Database extends BiofabServlet {

    private String model_package_name = "org.biofab.model";
    Session session = null;

    @Override
    public void init() {
        session = HibernateUtil.getSessionFactory().openSession();
    }

    @Override 
    public void destroy() {
        session.close();
    }

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {

        String[] pathParams = getPathParams(request.getRequestURI());
        if(pathParams.length == 0) {
            jsonError(response, "no model specified");
            return;
        }
        String modelName = pathParams[0];
        Long id = null;
        if(pathParams.length >= 2) {
            id = Long.valueOf(pathParams[1]);
        }

        Class modelClass;
        try {
            modelClass = getClass(request, modelName);
        } catch (ClassNotFoundException ex) {
            jsonError(response, "unknown model");
            return;
        }

        modelName = modelClass.getSimpleName();

        String json_params = request.getParameter("json");
        DatabaseParams params = null;

        if((json_params != null) && (!json_params.equals(""))) {

            GsonBuilder gsonb = new GsonBuilder();
            gsonb.registerTypeAdapter(DatabaseParamHash.class, new DatabaseParamHashDeserializer());
            Gson gson = gsonb.create();
            params = (DatabaseParams) gson.fromJson(json_params, DatabaseParams.class);

        }

        String json;
        List<Field> includedFields = null;
        List<Field> includedRelationFields = null;

        Criteria crit = session.createCriteria(modelClass);

        // create query criteria based on json parameters

        if(params == null) {
            params = new DatabaseParams();
        }

        includedFields = findIncludedFields(modelClass, params, false);
        includedRelationFields = findIncludedFields(modelClass, params, true);
        addRestrictions(crit, includedRelationFields, params);


        if(id != null) {
            crit.setMaxResults(1);
            crit.add(Restrictions.eq("id", id));
            json = query(crit, includedFields, true);
        } else {
            json = query(crit, includedFields, false);
        }
        

        PrintWriter out = response.getWriter();
        try {
            out.print(json);
        } finally {
            out.close();
        }

    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {
        String[] pathParams = getPathParams(request.getRequestURI());
        if(pathParams.length == 0) {
            jsonError(response, "no model specified");
            return;
        }
        String modelName = pathParams[0];


        Class modelClass;
        try {
            modelClass = getClass(request, modelName);
        } catch (ClassNotFoundException ex) {
            jsonError(response, "unknown model");
            return;
        }

        modelName = modelClass.getSimpleName();

        String input = request.getParameter("json");

        if((input == null) || (input.equals(""))) {
             jsonError(response, "no valid json received");
             return;
        }
        
        Gson gson = new Gson();

        session.save(gson.fromJson(input, modelClass));
        
        jsonSuccess(response, "new object successfully saved to database");

    }

    @Override
    protected void doPut(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {
        String[] pathParams = getPathParams(request.getRequestURI());
        if(pathParams.length == 0) {
            jsonError(response, "no model specified");
            return;
        }
        String modelName = pathParams[0];

        Class modelClass;
        try {
            modelClass = getClass(request, modelName);
        } catch (ClassNotFoundException ex) {
            jsonError(response, "unknown model");
            return;
        }

        if(pathParams.length < 2) {
            jsonError(response, "cannot update when no id specified");
            return;
        }
        Long id = Long.valueOf(pathParams[1]);

        modelName = modelClass.getSimpleName();

        String input = request.getParameter("json");

        if((input == null) || (input.equals(""))) {
             jsonError(response, "no valid json received");
             return;
        }

        Gson gson = new Gson();

        // update exiting object
        Base jsonObj = (Base) gson.fromJson(input, modelClass);
        Object newObj = session.merge(jsonObj);
        session.save(newObj);

        jsonSuccess(response, "object in database successfully updated");
    }


    @Override
    protected void doDelete(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {
        String[] pathParams = getPathParams(request.getRequestURI());
        if(pathParams.length == 0) {
            jsonError(response, "no model specified");
            return;
        }
        String modelName = pathParams[0];

        Class modelClass;
        try {
            modelClass = getClass(request, modelName);
        } catch (ClassNotFoundException ex) {
            jsonError(response, "unknown model");
            return;
        }

        if(pathParams.length < 2) {
            jsonError(response, "cannot delete when no id specified");
            return;
        }
        Long id = Long.valueOf(pathParams[1]);

        modelName = modelClass.getSimpleName();

        Object obj = session.get(modelClass, id);
        session.delete(obj);

        jsonSuccess(response, "object in database successfully deleted!");
    }

    private List<Field> findIncludedFields(Class modelClass, DatabaseParams params, boolean relationsOnly) {

        // All the code below just serves to enable/disable lazy loading for join fields

        List<Field> includedFields = new ArrayList<Field>();

        String joinAnnotations[] = {
          "OneToOne",
          "OneToMany",
          "ManyToOne",
          "ManyToMany"
        };


        // Get all of the fields that map to database columns
        int mods;
        for(Field f : modelClass.getDeclaredFields()) {
            mods = f.getModifiers();

            // Ignore fields that hibernate ignores
            // TODO not sure this is 100%. need to figure out exactly which fields hibernate gets
            if(Modifier.isAbstract(mods) ||
               Modifier.isFinal(mods) ||
               Modifier.isInterface(mods) ||
               Modifier.isNative(mods) ||
               Modifier.isPublic(mods) ||
               Modifier.isStatic(mods)) {
                continue;
            }

            String fieldName = f.getName();

            // should the field be included in the result
            boolean shouldInclude = false;

            // find out if this is a join field
            boolean isJoinField = false;
            Annotation[] annos = f.getAnnotations();
            for(Annotation anno : annos) {
                for(String annoName : joinAnnotations) {
                    if(anno.annotationType().getSimpleName().equals(annoName)) {
                        isJoinField = true;
                    }
                }
            }
            if(relationsOnly) {
                if(!isJoinField) {
                    continue;
                }
            }



            if(params.include_default == null) {
                // default is to include all non relation fields
                // unless we're working on relation fields only
                if(!relationsOnly && !isJoinField) {
                    shouldInclude = true;
                } 
            } else if(params.include_default.equals("include")) {
                shouldInclude = true;
            } else if(params.include_default.equals("exclude")) {
                shouldInclude = false;
            }

            // Is the field specifically included?
            if(params.include != null) {
                for(String inc : params.include) {
                    String inc_singular = Inflection.singularize(inc);
                    if(inc.equalsIgnoreCase(fieldName) || inc_singular.equalsIgnoreCase(fieldName)) {
                        shouldInclude = true;
                    }
                }
            }

            // Is the field specifically excluded?
            if(params.exclude != null) {
                for(String ex : params.exclude) {
                    String ex_singular = Inflection.singularize(ex);
                    if(ex.equalsIgnoreCase(fieldName) || ex_singular.equalsIgnoreCase(fieldName)) {
                        shouldInclude = false;
                    }
                }
            }
            if(shouldInclude) {
                includedFields.add(f);
            }
        }
        return includedFields;
    }

    private Criteria addRestrictions(Criteria crit, List<Field> includedFields, DatabaseParams params) {

        if((params.offset != null) && (params.offset > 0)) {
            crit.setFirstResult(params.offset);
        }

        if((params.limit != null) && (params.limit > 0)) {
            crit.setMaxResults(params.limit);
        }

        // Set fetch-mode to JOIN, disabling lazy fetching for the fields to be included
        Field f;
        Iterator it = includedFields.iterator();
        while(it.hasNext()) {
            f = (Field) it.next();
            //System.out.println("Setting fetch mode for: " + f.getName());
            crit.setFetchMode(f.getName(), FetchMode.JOIN);
        }

        // set match criteria based on the json parameters
        it = params.matching.entrySet().iterator();
        while(it.hasNext()) {
            Entry<String, JsonPrimitive> en = (Entry<String, JsonPrimitive>) it.next();

            String propPath = en.getKey();

            System.out.println("orig prop path: " + propPath);

            String aliasName;
            String propName;
            String lastAlias = null;
            String[] parts = propPath.split("[.]");
            if(parts.length > 1) {
                int count = 0;
                for(String part : parts) {
                    // for every part except the last
                    if(count >= parts.length - 1) {
                        break;
                    }

                    aliasName = part+"_alias";

                    if(count == 0) {
                        propName = part;
                    } else {
                        propName = lastAlias + "." + part;
                    }

                    System.out.println("creating alias: " + propName + " to " + aliasName);
                    crit.createAlias(propName, aliasName);
                    lastAlias = aliasName;
                    count += 1;
                }
                propPath = lastAlias + "." + parts[parts.length-1];

            }
            System.out.println("prop path: " + propPath);

//            crit.add(Restrictions.eq("feat.id", en.getValue().getAsLong()));


            if(en.getValue().isNumber()) {
                crit.add(Restrictions.eq(propPath, en.getValue().getAsLong()));
            } else if(en.getValue().isBoolean()) {
                // TODO fix this!
                System.out.println("ERROR! Don't know what to do with boolean");
            } else if(en.getValue().isString()) {
                crit.add(Restrictions.eq(propPath, en.getValue().getAsString()));
            }

        }


        return crit;
    }

    private String query(String hql, List<Field> includedFields, boolean single) {
        return runHQLQuery(hql, null, includedFields, single);
    }

    private String query(Criteria crit, List<Field> includedFields, boolean single) {
        return runHQLQuery(null, crit, includedFields, single);
    }

    private String runHQLQuery(String hql, Criteria crit, List<Field> includedFields, boolean single) {

        StringWriter out = new StringWriter();
        PrintWriter writer = new PrintWriter(out);

        List resultList = null;
        try {

            if(hql != null) {
                Query q = session.createQuery(hql);
                session.beginTransaction();
                resultList = q.list();
                session.getTransaction().commit();
            } else {
                session.beginTransaction();
                resultList = crit.list();
                session.getTransaction().commit();
            }
            
        } catch (HibernateException he) {
            he.printStackTrace(writer);
            return out.toString();
        }

        // create gson serializer with custom inclusion strategy
        Gson gson = new GsonBuilder().setExclusionStrategies(new CustomGsonInclusionStrategy(includedFields)).serializeNulls().create();


        String json;
        if(single == true) {
            if(resultList.isEmpty()) {
                json = ""; // TODO return something better
            } else {
                json = gson.toJson(resultList.get(0));
            }
        } else {
            json = gson.toJson(resultList);
        }
        return json;

    }

    private Class getClass(HttpServletRequest request, String model_name) throws ClassNotFoundException {

        Class model_class;
        try {
            model_class = Class.forName(model_package_name + "." + model_name);
        } catch(ClassNotFoundException e) {
            model_name = Inflection.singularize(model_name); // if plural given
            model_class = Class.forName(model_package_name + "." + model_name);
        }
        if(!model_class.getPackage().equals(Package.getPackage(model_package_name))) {
            throw new ClassNotFoundException();
        }
        return model_class;
    }

    @WebAccessible
    public void test(HttpServletRequest request, HttpServletResponse response)
    throws ServletException, IOException {

        String json_req = request.getParameter("json");

        if((json_req == null) || (json_req.equals(""))) {
             response.sendError(response.SC_BAD_REQUEST, "no valid json received");
             return;
        }

        Gson gson = new Gson();

        response.setContentType("text/plain;charset=UTF-8");

        PrintWriter out = response.getWriter();
        try {

            List resultList = null;
            try {
                // TODO should be moved to web app init function
                Session session = HibernateUtil.getSessionFactory().openSession();
                session.beginTransaction();
                Query q = session.createQuery("from DNAMolecule");
                q.setMaxResults(10);
                resultList = q.list();
                session.getTransaction().commit();
                session.close();
            } catch (HibernateException he) {
                he.printStackTrace(out);
            }

            String txt = "";

            Iterator iter = resultList.iterator();
            DNAMolecule cur;
            while(iter.hasNext()) {
                cur = (DNAMolecule) iter.next();
                txt += cur.toJSON() + "\n";
            }

            out.println(txt);
        } finally {
            out.close();
        }
    }



    // TODO
    // Doesn't deal with nested fields correctly!
    private static class CustomGsonInclusionStrategy implements ExclusionStrategy {

        private List<Field> includedFields = null;

        public CustomGsonInclusionStrategy(List<Field> includedFields) {
            this.includedFields = includedFields;
        }

        @Override
        public boolean shouldSkipField(FieldAttributes fa) {

            Field f;
            Iterator it = includedFields.iterator();
            while(it.hasNext()) {
                f = (Field) it.next();
                if(f.getName().equals(fa.getName())) {
                    return false;
                }
            }
            return true;
        }

        @Override
        public boolean shouldSkipClass(Class<?> type) {
            return false;
        }


    }

}
