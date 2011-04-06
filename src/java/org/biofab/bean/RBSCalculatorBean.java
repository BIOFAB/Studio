/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.bean;

import javax.ejb.Stateless;
import javax.servlet.ServletContext;
import org.biofab.jython.FooInterface;
import org.python.core.PyObject;
import org.python.core.PyString;
import org.python.util.PythonInterpreter;

/**
 *
 * @author root
 */
@Stateless
public class RBSCalculatorBean {
    

    public int addNumbers(int number1, int number2) {
        return number1 + number2;
    }

    public String jythonFoo(ServletContext context, String dnaseq) {

        String pythonPath = context.getRealPath("/") + "/WEB-INF/classes/org/biofab/python";

        PythonInterpreter interpreter = new PythonInterpreter();

        interpreter.exec("import sys");
        interpreter.exec("sys.path.append('" + pythonPath + "')");
        interpreter.exec("from Foo import Foo");

        PyObject fooClass = interpreter.get("Foo");

        PyObject fooObject = fooClass.__call__(new PyString("This is a horse"));

        FooInterface foo = (FooInterface) fooObject.__tojava__(FooInterface.class);

        String seq = dnaseq.toUpperCase();

        return foo.rbs_calc(seq);

    }
 
}
