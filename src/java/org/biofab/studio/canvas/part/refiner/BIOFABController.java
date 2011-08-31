/*
 *
 * 
 */

package org.biofab.studio.canvas.part.refiner;

import com.google.gson.Gson;

import java.util.ArrayList;

//import org.biofab.model.Oligo;
import org.biojava.bio.seq.DNATools;
import org.biojava.bio.symbol.IllegalAlphabetException;
import org.biojava.bio.symbol.IllegalSymbolException;
import org.biojava.bio.symbol.SymbolList;
import org.biojavax.bio.seq.RichSequence;


public class BIOFABController {
    
//    public static Oligo design(String[] sequences, String forward_concat_5p, String forward_concat_3p, String reverse_concat_5p, String reverse_concat_3p) throws IllegalSymbolException, IllegalAlphabetException {
//
//        Oligo result = new Oligo();
//
//        for(String seq : sequences) {
////            result.add(design(seq, forward_concat_5p, forward_concat_3p, reverse_concat_5p, reverse_concat_3p));
//        }
//
//        return result;
//    }
//
//    public static Oligo design(String seq, String forward_concat_5p, String forward_concat_3p, String reverse_concat_5p, String reverse_concat_3p) throws IllegalSymbolException, IllegalAlphabetException {
//
//
//        SymbolList seq_sym = DNATools.createDNA(seq);
//        RichSequence rseq = RichSequence.Tools.createRichSequence("sequence", seq_sym);
//
//        Oligo result = new Oligo();
////        result.forward = forward_concat_5p.toUpperCase() + seq.toUpperCase() + forward_concat_3p.toUpperCase();
////        result.reverse = reverse_concat_5p.toUpperCase() + DNATools.reverseComplement(rseq).seqString().toUpperCase() + reverse_concat_3p.toUpperCase();
//
//        return result;
//    }
}
