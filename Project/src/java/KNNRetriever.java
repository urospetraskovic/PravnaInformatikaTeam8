package cbr.retrieval;

import cbr.database.CaseDescription;
import cbr.database.CaseDatabase;
import cbr.similarity.CaseSimilarityCalculator;
import java.util.*;
import java.util.stream.Collectors;

/**
 * KNNRetriever - K-Nearest Neighbors case retrieval engine
 * Given an unknown case, retrieves the K most similar cases from database
 * 
 * Usage:
 *   KNNRetriever retriever = new KNNRetriever(caseDatabase, k=5);
 *   List<CaseMatch> matches = retriever.retrieveSimilarCases(unknownCase);
 */
public class KNNRetriever {
    private CaseDatabase caseDatabase;
    private int k;  // Number of nearest neighbors to retrieve

    public static class CaseMatch implements Comparable<CaseMatch> {
        public CaseDescription caseDescr;
        public double similarityScore;

        public CaseMatch(CaseDescription caseDescr, double similarityScore) {
            this.caseDescr = caseDescr;
            this.similarityScore = similarityScore;
        }

        @Override
        public int compareTo(CaseMatch other) {
            // Sort by similarity score descending
            return Double.compare(other.similarityScore, this.similarityScore);
        }

        @Override
        public String toString() {
            return String.format("%s (%s) - Similarity: %.2f%%", 
                caseDescr.getCaseNumber(), 
                caseDescr.getCaseType(),
                similarityScore * 100);
        }
    }

    /**
     * Constructor
     * @param caseDatabase The case knowledge base
     * @param k Number of nearest neighbors to retrieve (typically 3-5)
     */
    public KNNRetriever(CaseDatabase caseDatabase, int k) {
        this.caseDatabase = caseDatabase;
        this.k = k;
    }

    /**
     * Retrieve K most similar cases
     */
    public List<CaseMatch> retrieveSimilarCases(CaseDescription unknownCase) {
        List<CaseMatch> allMatches = new ArrayList<>();

        // Calculate similarity for all cases in database
        for (CaseDescription dbCase : caseDatabase.getAllCases()) {
            double similarity = CaseSimilarityCalculator.calculateSimilarity(unknownCase, dbCase);
            allMatches.add(new CaseMatch(dbCase, similarity));
        }

        // Sort by similarity and return top K
        Collections.sort(allMatches);
        return allMatches.stream()
            .limit(k)
            .collect(Collectors.toList());
    }

    /**
     * Retrieve similar cases with minimum similarity threshold
     */
    public List<CaseMatch> retrieveSimilarCases(CaseDescription unknownCase, double minSimilarity) {
        List<CaseMatch> allMatches = new ArrayList<>();

        for (CaseDescription dbCase : caseDatabase.getAllCases()) {
            double similarity = CaseSimilarityCalculator.calculateSimilarity(unknownCase, dbCase);
            if (similarity >= minSimilarity) {
                allMatches.add(new CaseMatch(dbCase, similarity));
            }
        }

        Collections.sort(allMatches);
        return allMatches.stream()
            .limit(k)
            .collect(Collectors.toList());
    }

    /**
     * Retrieve cases of specific type
     */
    public List<CaseMatch> retrieveByType(CaseDescription unknownCase, String caseType) {
        List<CaseMatch> typeMatches = new ArrayList<>();

        for (CaseDescription dbCase : caseDatabase.getCasesByType(caseType)) {
            double similarity = CaseSimilarityCalculator.calculateSimilarity(unknownCase, dbCase);
            typeMatches.add(new CaseMatch(dbCase, similarity));
        }

        Collections.sort(typeMatches);
        return typeMatches.stream()
            .limit(k)
            .collect(Collectors.toList());
    }

    /**
     * Retrieve workplace cases only
     */
    public List<CaseMatch> retrieveWorkplaceCases(CaseDescription unknownCase) {
        List<CaseMatch> workplaceMatches = new ArrayList<>();

        for (CaseDescription dbCase : caseDatabase.getWorkplaceCases()) {
            double similarity = CaseSimilarityCalculator.calculateSimilarity(unknownCase, dbCase);
            workplaceMatches.add(new CaseMatch(dbCase, similarity));
        }

        Collections.sort(workplaceMatches);
        return workplaceMatches.stream()
            .limit(k)
            .collect(Collectors.toList());
    }

    /**
     * Retrieve harassment/stalking cases
     */
    public List<CaseMatch> retrieveHarassmentCases(CaseDescription unknownCase) {
        List<CaseMatch> harassmentMatches = new ArrayList<>();

        for (CaseDescription dbCase : caseDatabase.getHarassmentCases()) {
            double similarity = CaseSimilarityCalculator.calculateSimilarity(unknownCase, dbCase);
            harassmentMatches.add(new CaseMatch(dbCase, similarity));
        }

        Collections.sort(harassmentMatches);
        return harassmentMatches.stream()
            .limit(k)
            .collect(Collectors.toList());
    }

    /**
     * Retrieve cases with similar verdict outcomes
     */
    public List<CaseMatch> retrieveByVerdict(CaseDescription unknownCase, String verdictType) {
        List<CaseMatch> verdictMatches = new ArrayList<>();

        for (CaseDescription dbCase : caseDatabase.getCasesByVerdict(verdictType)) {
            double similarity = CaseSimilarityCalculator.calculateSimilarity(unknownCase, dbCase);
            verdictMatches.add(new CaseMatch(dbCase, similarity));
        }

        Collections.sort(verdictMatches);
        return verdictMatches.stream()
            .limit(k)
            .collect(Collectors.toList());
    }

    /**
     * Set number of neighbors to retrieve
     */
    public void setK(int k) {
        this.k = k;
    }

    /**
     * Get current K value
     */
    public int getK() {
        return k;
    }

    /**
     * Print retrieval results with explanations
     */
    public void printResults(List<CaseMatch> matches, CaseDescription queryCase) {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("CASE RETRIEVAL RESULTS");
        System.out.println("=".repeat(80));
        System.out.println("\nQuery Case: " + queryCase.getCaseType());
        if (queryCase.getIncidentNarrative() != null) {
            System.out.println("Description: " + queryCase.getIncidentNarrative());
        }
        
        System.out.println("\nTop " + matches.size() + " Most Similar Cases:");
        System.out.println("-".repeat(80));

        int rank = 1;
        for (CaseMatch match : matches) {
            System.out.printf("%d. %s%n", rank, match.toString());
            System.out.printf("   Articles: %s%n", 
                String.join(", ", match.caseDescr.getArticlesCharged()));
            System.out.printf("   Verdict: %s%n",
                match.caseDescr.getGuilty() ? "GUILTY" :
                (match.caseDescr.getAcquitted() ? "ACQUITTED" : "CONDITIONAL"));
            if (match.caseDescr.getSentenceDurationMonths() != null && 
                match.caseDescr.getSentenceDurationMonths() > 0) {
                System.out.printf("   Sentence: %d months%n", 
                    match.caseDescr.getSentenceDurationMonths());
            }
            System.out.println();
            rank++;
        }
        System.out.println("=".repeat(80) + "\n");
    }

    /**
     * Get detailed similarity breakdown
     */
    public String getDetailedExplanation(CaseDescription queryCase, CaseDescription matchCase) {
        return CaseSimilarityCalculator.getSimilarityExplanation(queryCase, matchCase);
    }
}
