/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

package org.biofab.studio.canvas.part.refiner;

import org.biojava.bio.seq.DNATools;
import org.biojava.bio.seq.RNATools;
import org.biojava.bio.symbol.BasisSymbol;
import org.biojava.bio.symbol.CodonPref;
import org.biojava.bio.symbol.CodonPrefTools;
import org.biojava.bio.symbol.IllegalAlphabetException;
import org.biojava.bio.symbol.IllegalSymbolException;
import org.biojava.bio.symbol.Symbol;
import org.biojava.bio.symbol.SymbolList;

/**
 *
 * @author juul
 */
public class CodonChange {

    private SymbolList _oldCodon;
    private SymbolList _newCodon;
    private Integer _position;
    private Double _frequencyDifference;


    public CodonChange(SymbolList oldCodon, SymbolList newCodon, Integer position) throws IllegalAlphabetException, IllegalSymbolException {
        _oldCodon = oldCodon;
        _newCodon = newCodon;
        _position = position;
        
        CodonPref codonPref = CodonPrefTools.getCodonPreference(CodonPrefTools.ECOLI);
        SymbolList oldRNATriplet = DNATools.toRNA(oldCodon);
        SymbolList newRNATriplet = DNATools.toRNA(newCodon);
        Symbol aminoAcid = RNATools.translate(oldRNATriplet).symbolAt(1);

        BasisSymbol oldCodonBas = (BasisSymbol) RNATools.getCodonAlphabet().getSymbol(oldRNATriplet.toList());
        BasisSymbol newCodonBas = (BasisSymbol) RNATools.getCodonAlphabet().getSymbol(newRNATriplet.toList());

        Double oldFreq = codonPref.getFrequencyForSynonyms(aminoAcid).getWeight((Symbol) oldCodonBas);
        Double newFreq = codonPref.getFrequencyForSynonyms(aminoAcid).getWeight((Symbol) newCodonBas);

        _frequencyDifference = Math.abs(oldFreq - newFreq);

    }

    public SymbolList getOldCodon() {
        return _oldCodon;
    }

    public SymbolList getNewCodon() {
        return _newCodon;
    }

    public Integer getPosition() {
        return _position;
    }

    public Double getFrequencyDifference() {
        return _frequencyDifference;
    }


}
