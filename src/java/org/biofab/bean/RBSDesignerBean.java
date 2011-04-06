/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.bean;

import javax.ejb.Stateless;
import javax.servlet.ServletContext;
import org.biofab.jython.FromPythonException;
import org.biofab.jython.RBSDesignerInterface;
import org.python.core.PyException;
import org.python.core.PyObject;
import org.python.util.PythonInterpreter;

/**
 *
 * @author root
 */
@Stateless
public class RBSDesignerBean {
    

    public String design(ServletContext context, String dnaseq, Integer start_codon_offset) throws FromPythonException {

        String pythonLibPath = context.getRealPath("/") + "/python";
        String pythonPath = context.getRealPath("/") + "/WEB-INF/classes/org/biofab/python/rbs_designer";
        
        PythonInterpreter interpreter = new PythonInterpreter();

        interpreter.exec("import sys");
        interpreter.exec("sys.path.append('" + pythonLibPath + "')");
        interpreter.exec("sys.path.append('" + pythonPath + "')");
        interpreter.exec("from RBSDesigner import RBSDesigner");

        PyObject pyClass = interpreter.get("RBSDesigner");

        PyObject pyObject = pyClass.__call__();

        RBSDesignerInterface rbs_designer = (RBSDesignerInterface) pyObject.__tojava__(RBSDesignerInterface.class);

        String seq = dnaseq.toUpperCase();

        String ret;
        try {
            ret = rbs_designer.rbs_design(seq, start_codon_offset);
        } catch (PyException e) {
            throw FromPythonException.fromPyException(e);
        }

        return ret;

    }
 
}
