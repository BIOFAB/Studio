/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.webservices;

import com.google.gson.Gson;
import java.util.ArrayList;
import org.biojava.bio.seq.DNATools;
import org.biojava.bio.symbol.IllegalAlphabetException;
import org.biojava.bio.symbol.IllegalSymbolException;
import org.biojava.bio.symbol.SymbolList;
import org.biojavax.bio.seq.RichSequence;
import org.biofab.webservices.protocol.OligoDesignRequest;
import org.biofab.webservices.protocol.OligoDesignResponse;

/**
 *
 * @author juul
 */
public class OligoDesign {

    /*
     * Takes a JSON object like:
     * {
     *      "sequences": ["gatta", "tacca"],
     *      "forward_concat_5p": "gaa",
     *      "forward_concat_3p": "ggg",
     *      "reverse_concat_5p": "ccc",
     *      "reverse_concat_3p": "tta"
     * }
     */

    public static ArrayList<OligoDesignResponse> design_for_json(String json) throws IllegalSymbolException, IllegalAlphabetException {

        Gson gson = new Gson();

        OligoDesignRequest input = gson.fromJson(json, OligoDesignRequest.class);

        return design(input.sequences, input.forward_concat_5p, input.forward_concat_3p, input.reverse_concat_5p, input.reverse_concat_3p);

    }

    public static ArrayList<OligoDesignResponse> design(String[] sequences, String forward_concat_5p, String forward_concat_3p, String reverse_concat_5p, String reverse_concat_3p) throws IllegalSymbolException, IllegalAlphabetException {

        ArrayList<OligoDesignResponse> result = new ArrayList<OligoDesignResponse>();

        for(String seq : sequences) {
            result.add(design(seq, forward_concat_5p, forward_concat_3p, reverse_concat_5p, reverse_concat_3p));
        }

        return result;
    }

    public static OligoDesignResponse design(String seq, String forward_concat_5p, String forward_concat_3p, String reverse_concat_5p, String reverse_concat_3p) throws IllegalSymbolException, IllegalAlphabetException {


        SymbolList seq_sym = DNATools.createDNA(seq);
        RichSequence rseq = RichSequence.Tools.createRichSequence("sequence", seq_sym);

        OligoDesignResponse result = new OligoDesignResponse();
        result.forward = forward_concat_5p.toUpperCase() + seq.toUpperCase() + forward_concat_3p.toUpperCase();
        result.reverse = reverse_concat_5p.toUpperCase() + DNATools.reverseComplement(rseq).seqString().toUpperCase() + reverse_concat_3p.toUpperCase();

        return result;
    }


}
