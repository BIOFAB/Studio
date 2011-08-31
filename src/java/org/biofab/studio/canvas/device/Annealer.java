/*
 * 
 * 
 */

package org.biofab.studio.canvas.device;


import java.util.logging.Level;
import java.util.logging.Logger;
import org.biojava.bio.alignment.NeedlemanWunsch;
import org.biojava.bio.alignment.SequenceAlignment;
import org.biojava.bio.alignment.SubstitutionMatrix;
import org.biojava.bio.symbol.AlphabetManager;
import org.biojava.bio.symbol.FiniteAlphabet;
import org.biojava.bio.symbol.Alignment;
import org.biojava.bio.symbol.IllegalAlphabetException;
import org.biojavax.bio.seq.RichSequence;
import org.biojava.bio.seq.DNATools;
import org.biojava.bio.symbol.SymbolList;
import org.biojava.bio.seq.StrandedFeature;

public class Annealer {

    protected SequenceAlignment _seqAlignment;

    public Annealer() {
    }

    public String anneal(RichSequence fwdSeq, RichSequence revSeq) {
        SymbolList revSeq3to5Prime = null;
        String annealingString = null;

        try {
            revSeq3to5Prime = DNATools.complement(DNATools.flip(revSeq, StrandedFeature.NEGATIVE));
        } catch (IllegalAlphabetException ex) {
            Logger.getLogger(Annealer.class.getName()).log(Level.SEVERE, null, ex);
        }
        if (fwdSeq != null && revSeq != null) {
            try {
                FiniteAlphabet alphabet = (FiniteAlphabet) AlphabetManager.alphabetForName("DNA");
// SubstitutionMatrix matrix = new SubstitutionMatrix(alphabet, (short) 5, (short) 0);

                SubstitutionMatrix matrix = new SubstitutionMatrix(alphabet, "#\n# Lowest score = -4, Highest score = 5\n#\n A T G C\nA -4 4 -4 -4\nT 4 -4 -4 -4\nG -4 -4 -4 5\nC -4 -4 5 -4", "AnnealingMatrix");
                _seqAlignment = new NeedlemanWunsch(
                        (short) 0, // match
                        (short) 3, // replace
                        (short) 2, // insert
                        (short) 2, // delete
                        (short) -2, // gapExtend
                        matrix // SubstitutionMatrix
                        );


// SequenceAlignment alignment = new NeedlemanWunsch(
// (short) 3, // match
// (short) 3, // replace
// (short) 2, // insert
// (short) 2, // delete
// (short) 1, // gapExtend
// matrix // SubstitutionMatrix
// );
                _seqAlignment.pairwiseAlignment(fwdSeq, revSeq3to5Prime);
                Alignment alignment = _seqAlignment.getAlignment(fwdSeq, revSeq3to5Prime);
                annealingString = generateAnnealingString(alignment);
                return annealingString;
            } catch (Exception e) {
                return e.getMessage();
            }
        } else {
            return "Invalid parameters were submitted.";


        }
    }

    protected String generateAnnealingString(Alignment alignment) {
        String annealingString = null;


        //TODO Use the alignment object



        try {
            SymbolList forwardSymbolList = alignment.symbolListForLabel(alignment.getLabels().get(0));
            SymbolList reverseSymbolList = alignment.symbolListForLabel(alignment.getLabels().get(1));
            //SymbolList complementedReverseSymbolList = DNATools.complement(DNATools.flip(reverseSymbolList, StrandedFeature.NEGATIVE)); //Generates the complement of the bottom sequence
            //Can't generate reverse complement symbol list for some reason
            String matchCharString = "";
            //Will contain all of the | characters


            if (forwardSymbolList.length() == reverseSymbolList.length()) {
                for (int n = 1; n
                        <= forwardSymbolList.length(); n++) {
                    if (!forwardSymbolList.symbolAt(n).getName().equals("gap") && !reverseSymbolList.symbolAt(n).getName().equals("gap") && !forwardSymbolList.symbolAt(n).getName().equals("[]") && !reverseSymbolList.symbolAt(n).getName().equals("[]")) {
                        //Checks to make sure that there is not a gap symbol at point of comparison
                        if (forwardSymbolList.symbolAt(n).equals(DNATools.complement(reverseSymbolList.symbolAt(n)))) {
                            matchCharString = matchCharString + "|";
                            //If there is a match, insert a | character


                        } else {
                            matchCharString = matchCharString + "_";
                            //Adds a blank space if there is no match


                        }
                    } else {
                        matchCharString = matchCharString + "_";
                        //Adds a blank space if there is no match


                    }
                }
                annealingString = alignment.symbolListForLabel(alignment.getLabels().get(0)).seqString() + "\n" + matchCharString + "\n" + alignment.symbolListForLabel(alignment.getLabels().get(1)).seqString();
//The code, gets the job done, but I'm not using the iterator properly because I don't known how to work with the objects returned by the iterator, which are of the class class org.biojava.bio.symbol.AlphabetManager$WellKnownAtomicSymbol


            } else {
                return "the SymbolLists generated by the alignment have unequal lengths. Severe error in alignment is likely.";



            }

        } catch (Exception ex) {
            Logger.getLogger(Annealer.class.getName()).log(Level.SEVERE, null, ex);
        }



        return annealingString;

    }
}