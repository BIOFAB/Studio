package org.biofab.webservices;


import java.io.IOException;
import java.util.Hashtable;
import javax.servlet.annotation.WebServlet;

import javax.servlet.http.*;

import org.biofab.model.Part;
import org.biojava.bio.seq.DNATools;
import org.biojava.bio.seq.Feature;
import org.biojava.bio.seq.StrandedFeature;
import org.biojava.bio.symbol.Edit;
import org.biojava.bio.symbol.IllegalSymbolException;
import org.biojava.bio.symbol.RangeLocation;

import org.biojavax.Namespace;
import org.biojavax.RichObjectFactory;
import org.biojavax.SimpleComment;
import org.biojavax.SimpleNote;
import org.biojavax.SimpleRichAnnotation;
import org.biojavax.bio.seq.*;

@SuppressWarnings("serial")
@WebServlet(name="DesignServlet", urlPatterns={"/design/*"})
public class DesignServlet extends HttpServlet
{
    protected Hashtable<String, Part>   _parts;
    
    public DesignServlet()
    {
        _parts = new Hashtable<String, Part>();
        _parts.put("BFA_1", new Part("BFA_1", "J23101", "TTTACAGCTAGCTCAGTCCTAGGTATTATGCTAGC"));
        _parts.put("BFA_2", new Part("BFA_2", "J23109", "TTTACAGCTAGCTCAGTCCTAGGGACTGTGCTAGC"));
        _parts.put("BFA_3", new Part("BFA_3", "PLTETo1", "TCCCTATCAGTGATAGAGATTGACATCCCTATCAGTGATAGAGATACTGAGCACATCAGCAGGACGCACTGACC"));
        _parts.put("BFA_4", new Part("BFA_4", "galP1", "ATTCCACTAATTTATTCCATGTCACACTTTTCGCATCTTTGTTATGCTATGGTTATTTCATACCATAA"));
        _parts.put("BFA_5", new Part("BFA_5", "lacUV5", "CCCCAGGCTTTACACTTTATGCTTCCGGCTCGTATAATGTGTGGAATTGTGAG"));
        _parts.put("BFA_6", new Part("BFA_6", "pCat", "GGCACGTAAGAGGTTCCAACTTTCACCATAATGAAACA"));
        _parts.put("BFA_7", new Part("BFA_7", "pLlacO1", "ATAAATGTGAGCGGATAACAATTGACATTGTGAGCGGATAACAAGATACTGAGCACATCAGCAGGACGCACTGACC"));
        _parts.put("BFA_8", new Part("BFA_8", "pLux", "ACCTGTAGGATCGTACAGGTTTACGCAAGAAAATGGTTTGTTATAGTCGAATAAA"));
        _parts.put("BFA_9", new Part("BFA_9", "pT7A1", "ATTTAAAATTTATCAAAAAGAGTATTGACTTAAAGTCTAACCTATAGGATACTTACAGCCATCGAGAG"));
        _parts.put("BFA_10", new Part("BFA_10", "pTac", "TTGACAATTAATCATCCGGCTCGTATAATGTGTGGAATTGTGAG"));
        _parts.put("BFA_11", new Part("BFA_11", "pTet", "TAATTCCTAATTTTTGTTGACACTCTATCGTTGATAGAGTTATTTTACCACTCCCTATCAGTGATAGAGAAAA"));
        _parts.put("BFA_12", new Part("BFA_12", "pminor", "GTGACCCAATAATGTGGGATAACATTGAAAAGATTAAAGAAATATGGGAAAACTCTGGAAAATCCGGG"));
        _parts.put("BFA_13", new Part("BFA_13", "pTrp", "AATGAGCTGTTGACAATTAATCATCGAACTAGTTAACTAGTACGCA"));
        _parts.put("BFA_14", new Part("BFA_14", "Nopromoter (tac spacer)", "ATTAATCATCCG"));
        _parts.put("BFA_15", new Part("BFA_15", "Anderson_RBS", "TCTAGAGAAAGAGGGGACAAACTAGT"));
        _parts.put("BFA_16", new Part("BFA_16", "Bujard_RBS", "GAATTCATTAAAGAGGAGAAAGGTACC"));
        _parts.put("BFA_17", new Part("BFA_17", "B0030_RBS", "ATTAAAGAGGAGAAA"));
        _parts.put("BFA_18", new Part("BFA_18", "B0031_RBS", "TCACACAGGAAACC"));
        _parts.put("BFA_19", new Part("BFA_19", "B0032_RBS", "TCACACAGGAAAG"));
        _parts.put("BFA_20", new Part("BFA_20", "B0033_RBS", "TCACACAGGAC"));
        _parts.put("BFA_21", new Part("BFA_21", "B0034_RBS", "AAAGAGGAGAAA"));
        _parts.put("BFA_22", new Part("BFA_22", "GSG_RBS", "TAAGGAGGTGACAAT"));
        _parts.put("BFA_23", new Part("BFA_23", "GSGV_RBS", "GCTCTTTAACAATTTATCATAAGGAGGTGACAAT"));
        _parts.put("BFA_24", new Part("BFA_24", "Invitrogen_RBS", "AAAATTAAGAGGTATATATTA"));
        _parts.put("BFA_25", new Part("BFA_25", "JBEI_RBS", "GAATTCAAAAGATCTTTTAAGAAGGAGATATACAT"));
        _parts.put("BFA_26", new Part("BFA_26", "Plotkin_RBS", "TGGATCCAAGAAGGAGATATAACC"));
        _parts.put("BFA_27", new Part("BFA_27", "Alon_RBS", "GGATCCTCTAGATTTAAGAAGGAGATATACAT"));
        _parts.put("BFA_28", new Part("BFA_28", "DeadRBS", "CACCATACACTG"));
    }
    
    @Override
    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException
    {
        response.setContentType("text/plain");
        response.getWriter().println("You have contacted the BIOFAB Design Web Service.");
    }
    
    @Override
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException
    {
        RichSequence    sequence;
        Part            part;
        Feature         feature = null;
        String[]        features;
        
        Namespace ns = RichObjectFactory.getDefaultNamespace();
        sequence = null;
        String componentID = request.getParameter("id");
        String format = request.getParameter("format");
        //String featureB = request.getParameter("fb");
        if(componentID != null && componentID.length() > 0)
        {
            features = componentID.split("\\.");

            String featureA = features[0];
            String featureB = "BFa_" + features[1];

            String preEOUSubseq = "tttagcttccttagctcctgaaaatctcgataactcaaaaaatacgcccggtagtgatcttatttcattatggtgaaagttggaacctcttacgtgccgatcaacgtctcattttcgccagatatc";
            String gfp = "ATGAGCAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTTAATGGGCACAAATTTTCTGTCCGTGGAGAGGGTGAAGGTGATGCTACAAACGGAAAACTCACCCTTAAATTTATTTGCACTACTGGAAAACTACCTGTTCCGTGGCCAACACTTGTCACTACTCTGACCTATGGTGTTCAATGCTTTTCCCGTTATCCGGATCACATGAAACGGCATGACTTTTTCAAGAGTGCCATGCCCGAAGGTTATGTACAGGAACGCACTATATCTTTCAAAGATGACGGGACCTACAAGACGCGTGCTGAAGTCAAGTTTGAAGGTGATACCCTTGTTAATCGTATCGAGTTAAAGGGTATTGATTTTAAAGAAGATGGAAACATTCTTGGACACAAACTCGAGTACAACTTTAACTCACACAATGTATACATCACGGCAGACAAACAAAAGAATGGAATCAAAGCTAACTTCAAAATTCGCCACAACGTTGAAGATGGTTCCGTTCAACTAGCAGACCATTATCAACAAAATACTCCAATTGGCGATGGCCCTGTCCTTTTACCAGACAACCATTACCTGTCGACACAATCTGTCCTTTCGAAAGATCCCAACGAAAAGCGTGACCACATGGTCCTTCTTGAGTTTGTAACTGCTGCTGGGATTACACATGGCATGGATGAGCTCTACAAA";
            String subseqA = "taaGGATCCaaactcgagtaaggatct";
            String dbITerminator = "ccaggcatcaaataaaacgaaaggctcagtcgaaagactgggcctttcgttttatctgttgtttgtcggtgaacgctctctactagagtcacactggctcaccttcgggtgggcctttctgcgtttata";
            String subseqB = "CCTAGG";
            String p15A = "gatatattccgcttcctcgctcactgactcgctacgctcggtcgttcgactgcggcgagcggaaatggcttacgaacggggcggagatttcctggaagatgccaggaagatacttaacagggaagtgagagggccgcggcaaagccgtttttccataggctccgcccccctgacaagcatcacgaaatctgacgctcaaatcagtggtggcgaaacccgacaggactataaagataccaggcgtttccccctggcggctccctcgtgcgctctcctgttcctgcctttcggtttaccggtgtcattccgctgttatggccgcgtttgtctcattccacgcctgacactcagttccgggtaggcagttcgctccaagctggactgtatgcacgaaccccccgttcagtccgaccgctgcgccttatccggtaactatcgtcttgagtccaacccggaaagacatgcaaaagcaccactggcagcagccactggtaattgatttagaggagttagtcttgaagtcatgcgccggttaaggctaaactgaaaggacaagttttggtgactgcgctcctccaagccagttacctcggttcaaagagttggtagctcagagaaccttcgaaaaaccgccctgcaaggcggttttttcgttttcagagcaagagattacgcgcagaccaaaacgatctcaagaagatcatcttattaa";
            String subseqC = "tcagataaaatatttctagatttcagtgcaatttatctcttcaaatgtagcacctgaagtcagccccatacgatataagttgttactagt";
            String toTerminator = "gcttggattctcaccaataaaaaacgcccggcggcaaccgagcgttctgaacaaatccagatggagttctgaggtcattactggatctatcaacaggagtccaagc";
            String subseqD = "gagctcgatatcaaa";
            String cmR2 = "ttacgccccgccctgccactcatcgcagtactgttgtaattcattaagcattctgccgacatggaagccatcacaaacggcatgatgaacctgaatcgccagcggcatcagcaccttgtcgccttgcgtataatatttgcccatggtgaaaacgggggcgaagaagttgtccatattggccacgtttaaatcaaaactggtgaaactcacccagggattggctgagacgaaaaacatattctcaataaaccctttagggaaataggccaggttttcaccgtaacacgccacatcttgcgaatatatgtgtagaaactgccggaaatcgtcgtggtattcactccagagcgatgaaaacgtttcagtttgctcatggaaaacggtgtaacaagggtgaacactatcccatatcaccagctcaccgtctttcattgccatacgaaattccggatgagcattcatcaggcgggcaagaatgtgaataaaggccggataaaacttgtgcttatttttctttacggtctttaaaaaggccgtaatatccagctgaacggtctggttataggtacattgagcaactgactgaaatgcctcaaaatgttctttacgatgccattgggatatatcaacggtggtatatccagtgatttttttctccat";

            try
            {
                sequence = RichSequence.Tools.createRichSequence(componentID, DNATools.createDNA(preEOUSubseq));
            }
            catch (IllegalSymbolException e1)
            {
                // TODO Auto-generated catch block
                e1.printStackTrace();
            }

     //       sequence.setSeqVersion(1.0);
     //       sequence.setIdentifier(name);

            SimpleRichAnnotation sourceAnnotation = new SimpleRichAnnotation();
            sourceAnnotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("organism"),"Escherichia coli",0));
            sourceAnnotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("plasmid"),"VKM81",0));
            sourceAnnotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("strain"),"BW25113",0));
            sourceAnnotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("mol_type"),"other DNA",0));

            StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
            featureTemplate.annotation = sourceAnnotation;
            featureTemplate.location = new RangeLocation(1,10);
            featureTemplate.source = "BIOFAB";
            featureTemplate.strand = StrandedFeature.POSITIVE;
            featureTemplate.type = "source";

            try
            {
              feature = sequence.createFeature(featureTemplate);
            }
            catch (Exception ex)
            {
              //ex.printStackTrace();
            }

            if(featureA != null && featureA.length() > 0)
            {
                featureA = featureA.toUpperCase();
                part = _parts.get(featureA);
                addPart(sequence, part, "promoter");
            }

            addNonAnnotatedSubsequence(sequence, "TTTG");

            if(featureB != null && featureB.length() > 0)
            {
                featureB = featureB.toUpperCase();
                part = _parts.get(featureB);
                addPart(sequence, part,"RBS");
            }

            addAnnotatedSubsequence(sequence, gfp, "CDS","gene","sfGFP");
            addNonAnnotatedSubsequence(sequence, subseqA);
            addAnnotatedSubsequence(sequence, dbITerminator, "terminator","label","dbI_terminator");
            addNonAnnotatedSubsequence(sequence, subseqB);
            addAnnotatedSubsequence(sequence, p15A, "rep_origin","label", "p15a");
            addNonAnnotatedSubsequence(sequence, subseqC);
            addAnnotatedSubsequence(sequence, toTerminator, "terminator","label", "To_terminator");
            addNonAnnotatedSubsequence(sequence, subseqD);
            addAnnotatedSubsequence(sequence, cmR2, "CDS","gene", "cmR2");

            feature.setLocation(new RangeLocation(1,sequence.length()));

            addComment(sequence, "The genetic constructs used here are taken or composed from available, well known genetic elements.  At this time BIOFAB staff have not yet taken care to define the precise functional boundaries of these genetic elements.  Thus, for example, a part labeled as a \"promoter\" may include sequences encoding all or part of a 5' UTR downstream of a transcription start site. And so on. Part of the mission of the BIOFAB is to define compatible sets of genetic objects with precise and composable boundaries. Such well engineered parts will be noted once available.");
            sequence.setCircular(true);

            if(format != null && format.equalsIgnoreCase("genbank"))
            {
                response.setContentType("text/plain");
                RichSequence.IOTools.writeGenbank(response.getOutputStream(), sequence, ns);
            }
            else
            {
                if(format.equalsIgnoreCase("insd"))
                {
                    response.setContentType("text/xml");
                    RichSequence.IOTools.writeINSDseq(response.getOutputStream(), sequence, ns);
                }
                else
                {
                    response.setContentType("text/plain");
                    RichSequence.IOTools.writeGenbank(response.getOutputStream(), sequence, ns);
                }

            }
        }
        else
        {
            response.setContentType("text/plain");
            response.getWriter().println("You have contacted the BIOFAB Design Web Service.");
        }
    }
    
    protected void addAnnotatedSubsequence(RichSequence sequence, String subSeq, String featureKey, String noteKey, String noteValue)
    {
        Edit edit;
        int start;
        int end;
        
        start = sequence.length() + 1;
        end = sequence.length() + subSeq.length();
        
        try
        {
            edit = new Edit(sequence.length() + 1, 0, DNATools.createDNA(subSeq.toUpperCase()));
            sequence.edit(edit);
        }
        catch (Exception e)
        {

        }
        
        SimpleRichAnnotation annotation = new SimpleRichAnnotation();
        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm(noteKey),noteValue,0));
        
        StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
        featureTemplate.annotation = annotation;
        featureTemplate.location = new RangeLocation(start,end);
        featureTemplate.source = "BIOFAB";
        featureTemplate.strand = StrandedFeature.POSITIVE;
        featureTemplate.type = featureKey;
        
        try 
        {
          sequence.createFeature(featureTemplate);
        }
        catch (Exception ex) 
        {
          //ex.printStackTrace();
        }
    }
    
    protected void addPart(RichSequence sequence, Part part, String featureKey)
    {
        Edit edit;
        int start;
        int end;
        
        start = sequence.length() + 1;
        end = sequence.length() + part.getSequence().length();
        
        try
        {
            edit = new Edit(sequence.length() + 1, 0, DNATools.createDNA(part.getSequence().toUpperCase()));
            sequence.edit(edit);
        }
        catch (Exception e)
        {

        }
        
        SimpleRichAnnotation annotation = new SimpleRichAnnotation();
        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("label"),part.getDescription(),0));
        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("biofab_id"),part.getID(),0));
        
        StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
        featureTemplate.annotation = annotation;
        featureTemplate.location = new RangeLocation(start,end);
        featureTemplate.source = "BIOFAB";
        featureTemplate.strand = StrandedFeature.POSITIVE;
        featureTemplate.type = featureKey;
        
        try 
        {
          sequence.createFeature(featureTemplate);
        }
        catch (Exception ex) 
        {
          //ex.printStackTrace();
        }
    }
    
    protected void addAnnotation(RichSequence sequence, String featureType, String noteKey, String noteValue, int start, int end)
    {
        SimpleRichAnnotation annotation = new SimpleRichAnnotation();
        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm(noteKey),noteValue,0));
        
        StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
        featureTemplate.annotation = annotation;
        featureTemplate.location = new RangeLocation(start,end);
        featureTemplate.source = "BIOFAB";
        featureTemplate.strand = StrandedFeature.POSITIVE;
        featureTemplate.type = featureType;
        
        try 
        {
          sequence.createFeature(featureTemplate);
        }
        catch (Exception ex) 
        {
          //ex.printStackTrace();
        }
    }
    
    protected void addNonAnnotatedSubsequence(RichSequence sequence, String seqString)
    {
        Edit edit;
        
        try
        {
            edit = new Edit(sequence.length() + 1, 0, DNATools.createDNA(seqString.toUpperCase()));
            sequence.edit(edit);
        }
        catch (Exception e)
        {

        }
    }
    
//    protected void addSourceAnnotation(RichSequence sequence)
//    {
//        SimpleRichAnnotation annotation = new SimpleRichAnnotation();
//        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("organism"),"Escherichia coli",0));
//        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("plasmid"),"VKM81",0));
//        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("strain"),"BW25113",0));
//        annotation.addNote(new SimpleNote(RichObjectFactory.getDefaultOntology().getOrCreateTerm("mol_type"),"other DNA",0));
//        
//        StrandedFeature.Template featureTemplate = new StrandedFeature.Template();
//        featureTemplate.annotation = annotation;
//        featureTemplate.location = new RangeLocation(1,sequence.length());
//        featureTemplate.source = "BIOFAB";
//        featureTemplate.strand = StrandedFeature.POSITIVE;
//        featureTemplate.type = "source";
//        
//        try 
//        {
//          sequence.createFeature(featureTemplate);
//        }
//        catch (Exception ex) 
//        {
//          //ex.printStackTrace();
//        }
//    }
    
    protected void addComment(RichSequence seq, String comment)
    {
        seq.addComment(new SimpleComment(comment, 0));
    }
}
