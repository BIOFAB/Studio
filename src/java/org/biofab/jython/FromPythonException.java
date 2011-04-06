/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.jython;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.io.Writer;
import org.python.core.PyException;

/**
 *
 * @author juul
 */
public class FromPythonException extends Exception {

    public String message = null;
    public String stackTrace = null;

    public static FromPythonException fromPyException(PyException e) {

        FromPythonException ret = new FromPythonException();

        // Get python-originated exception message
        ret.message = e.value.__getitem__(0).toString();

        // Get stack trace as string
        Writer strWriter = new StringWriter();
        PrintWriter printWriter = new PrintWriter(strWriter);
        e.printStackTrace(printWriter);

        ret.stackTrace = strWriter.toString();

        return ret;
    }


}
