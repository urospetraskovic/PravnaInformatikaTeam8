package cbr.similarity;

import cbr.database.CaseDescription;
import java.util.*;

/**
 * CaseSimilarityCalculator - Computes similarity between two legal cases
 * Uses weighted attributes to determine how similar two verdicts are
 * 
 * Similarity Metrics for Chapter 23 (Crimes against Payment System):
 * - Case Type Match: 0.30 weight
 * - Articles Charged Match: 0.25 weight (NEW - crucial for legal cases)
 * - Verdict Type Match: 0.20 weight
 * - Damage Amount: 0.15 weight (replaces harm for financial crimes)
 * - Evidence Quality: 0.10 weight
 * 
 * Result: Similarity score 0.0 (completely different) to 1.0 (identical)
 */
public class CaseSimilarityCalculator {
    
    // Weighting factors for different attributes - tuned for Chapter 23 crimes
    private static final double WEIGHT_CASE_TYPE = 0.30;
    private static final double WEIGHT_ARTICLES = 0.25;  // NEW
    private static final double WEIGHT_VERDICT = 0.20;
    private static final double WEIGHT_DAMAGE = 0.15;    // Replaces harm for financial crimes
    private static final double WEIGHT_EVIDENCE = 0.10;

    /**
     * Calculate overall similarity between two cases
     * Returns a score from 0.0 to 1.0
     */
    public static double calculateSimilarity(CaseDescription case1, CaseDescription case2) {
        double caseTypeSim = compareCaseTypes(case1, case2);
        double articlesSim = compareArticlesCharged(case1, case2);  // NEW
        double verdictSim = compareVerdicts(case1, case2);
        double damageSim = compareDamageAmount(case1, case2);       // NEW - replaces harm
        double evidenceSim = compareEvidence(case1, case2);

        double totalSimilarity = 
            (caseTypeSim * WEIGHT_CASE_TYPE) +
            (articlesSim * WEIGHT_ARTICLES) +
            (verdictSim * WEIGHT_VERDICT) +
            (damageSim * WEIGHT_DAMAGE) +
            (evidenceSim * WEIGHT_EVIDENCE);

        return Math.min(totalSimilarity, 1.0);
    }

    /**
     * Compare case types
     * Exact match = 1.0, related types = 0.5-0.8, unrelated = 0.0
     */
    private static double compareCaseTypes(CaseDescription case1, CaseDescription case2) {
        if (case1.getCaseType() == null || case2.getCaseType() == null) {
            return 0.0;
        }

        String type1 = case1.getCaseType().toLowerCase();
        String type2 = case2.getCaseType().toLowerCase();

        // Exact match
        if (type1.equals(type2)) {
            return 1.0;
        }

        // Check for related crime categories - Chapter 23 specific
        if (isFalsificationCrimeType(type1) && isFalsificationCrimeType(type2)) {
            // All falsification crimes are closely related
            return 0.90;
        }

        if (isPaymentSystemCrimeType(type1) && isPaymentSystemCrimeType(type2)) {
            // Payment system crimes (cards, checks) are related
            return 0.85;
        }

        if (isEconomicCrimeType(type1) && isEconomicCrimeType(type2)) {
            // Economic crimes in broader sense
            return 0.75;
        }

        // Cross-category similarities within Chapter 23
        if ((isFalsificationCrimeType(type1) || isPaymentSystemCrimeType(type1)) &&
            (isFalsificationCrimeType(type2) || isPaymentSystemCrimeType(type2))) {
            return 0.70;  // Related but different sub-categories
        }

        if (isHarassmentType(type1) && isHarassmentType(type2)) {
            return 0.85;
        }

        if (isFinancialCrimeType(type1) && isFinancialCrimeType(type2)) {
            return 0.80;
        }

        if (isViolenceType(type1) && isViolenceType(type2)) {
            return 0.75;
        }

        // Check for broader similarities
        if (type1.contains("threat") || type1.contains("endangering")) {
            if (type2.contains("threat") || type2.contains("endangering") || 
                type2.contains("stalking") || type2.contains("harassment")) {
                return 0.65;
            }
        }

        // Different crime types
        return 0.0;
    }

    /**
     * Compare verdict outcomes
     * Same verdict type = 1.0, partial match = 0.5, different = 0.0
     */
    private static double compareVerdicts(CaseDescription case1, CaseDescription case2) {
        Boolean guilty1 = case1.getGuilty();
        Boolean guilty2 = case2.getGuilty();
        Boolean acquitted1 = case1.getAcquitted();
        Boolean acquitted2 = case2.getAcquitted();
        Boolean conditional1 = case1.getConditional();
        Boolean conditional2 = case2.getConditional();

        // Same verdict type
        if (guilty1 != null && guilty1 && guilty2 != null && guilty2) {
            // Both guilty - check sentence similarity if available
            Integer sent1 = case1.getSentenceDurationMonths();
            Integer sent2 = case2.getSentenceDurationMonths();
            if (sent1 != null && sent2 != null) {
                int diff = Math.abs(sent1 - sent2);
                if (diff <= 2) return 1.0;      // Within 2 months: very similar
                if (diff <= 6) return 0.9;      // Within 6 months: similar
                if (diff <= 12) return 0.75;    // Within 12 months: moderately similar
                return 0.5;                      // Large difference
            }
            return 1.0;
        }

        if (acquitted1 != null && acquitted1 && acquitted2 != null && acquitted2) {
            return 1.0;  // Both acquitted
        }

        if (conditional1 != null && conditional1 && conditional2 != null && conditional2) {
            return 0.95;  // Both conditional
        }

        // Partial match: conditional vs guilty (both non-acquittal)
        if ((conditional1 != null && conditional1 || guilty1 != null && guilty1) &&
            (conditional2 != null && conditional2 || guilty2 != null && guilty2) &&
            !(acquitted1 != null && acquitted1) && !(acquitted2 != null && acquitted2)) {
            return 0.5;
        }

        // Different verdicts
        return 0.0;
    }

    /**
     * Compare harm assessment (physical + psychological)
     * Similar harm levels = higher similarity
     */
    private static double compareHarm(CaseDescription case1, CaseDescription case2) {
        Integer total1 = case1.getTotalHarmScore();
        Integer total2 = case2.getTotalHarmScore();

        if (total1 == null || total2 == null) {
            return 0.5;  // Neutral if data missing
        }

        int diff = Math.abs(total1 - total2);

        if (diff == 0) return 1.0;        // Identical harm
        if (diff == 1) return 0.95;       // Very similar
        if (diff <= 2) return 0.85;       // Similar
        if (diff <= 4) return 0.70;       // Moderately similar
        if (diff <= 6) return 0.50;       // Somewhat similar
        return 0.25;                      // Very different harm levels
    }

    /**
     * Compare evidence quality
     * More similar evidence types and quantities = higher similarity
     */
    private static double compareEvidence(CaseDescription case1, CaseDescription case2) {
        // Check for specific evidence types
        int sim = 0;
        int total = 0;

        // Video surveillance match
        total++;
        if ((case1.getVideoSurveillance() != null && case1.getVideoSurveillance()) ==
            (case2.getVideoSurveillance() != null && case2.getVideoSurveillance())) {
            sim++;
        }

        // Phone records match
        total++;
        if ((case1.getPhoneRecords() != null && case1.getPhoneRecords()) ==
            (case2.getPhoneRecords() != null && case2.getPhoneRecords())) {
            sim++;
        }

        // Psychological assessment match
        total++;
        if ((case1.getPsychologicalAssessment() != null && case1.getPsychologicalAssessment()) ==
            (case2.getPsychologicalAssessment() != null && case2.getPsychologicalAssessment())) {
            sim++;
        }

        // Witness count similarity
        total++;
        Integer wit1 = case1.getWitnessCount() != null ? case1.getWitnessCount() : 0;
        Integer wit2 = case2.getWitnessCount() != null ? case2.getWitnessCount() : 0;
        if (Math.abs(wit1 - wit2) <= 2) {
            sim += (double)sim / total;  // Partial credit
        }

        return (double)sim / total;
    }

    /**
     * Compare articles charged (Chapter 23 specific)
     * Exact article match = 1.0, same article different paragraph = 0.8, 
     * related articles = 0.5, unrelated = 0.0
     */
    private static double compareArticlesCharged(CaseDescription case1, CaseDescription case2) {
        List<String> articles1 = case1.getArticlesCharged();
        List<String> articles2 = case2.getArticlesCharged();
        
        if (articles1 == null || articles1.isEmpty() || 
            articles2 == null || articles2.isEmpty()) {
            return 0.5;  // Neutral if no article info
        }
        
        double maxSim = 0.0;
        
        for (String art1 : articles1) {
            for (String art2 : articles2) {
                double sim = compareArticleStrings(art1, art2);
                maxSim = Math.max(maxSim, sim);
            }
        }
        
        return maxSim;
    }
    
    /**
     * Compare two article strings (e.g., "Član 258 st.1" vs "Član 258 st.2")
     */
    private static double compareArticleStrings(String art1, String art2) {
        if (art1 == null || art2 == null) return 0.0;
        
        // Normalize strings
        String n1 = art1.toLowerCase().replaceAll("[^0-9]", " ").trim();
        String n2 = art2.toLowerCase().replaceAll("[^0-9]", " ").trim();
        
        // Extract article number (first number)
        String[] nums1 = n1.split("\\s+");
        String[] nums2 = n2.split("\\s+");
        
        if (nums1.length == 0 || nums2.length == 0) return 0.0;
        
        int articleNum1 = Integer.parseInt(nums1[0]);
        int articleNum2 = Integer.parseInt(nums2[0]);
        
        // Same article number
        if (articleNum1 == articleNum2) {
            // Check if same paragraph (st.)
            if (nums1.length > 1 && nums2.length > 1) {
                if (nums1[1].equals(nums2[1])) {
                    return 1.0;  // Exact match (same article, same paragraph)
                }
                return 0.85;    // Same article, different paragraph
            }
            return 0.90;        // Same article, no paragraph specified
        }
        
        // Check for related articles in Chapter 23
        // 258 (Counterfeiting) is related to 259 (Securities) and 260 (Credit cards)
        if (isRelatedChapter23Article(articleNum1, articleNum2)) {
            return 0.60;
        }
        
        // Both within Chapter 23 (258-286)
        if (isChapter23Article(articleNum1) && isChapter23Article(articleNum2)) {
            return 0.40;
        }
        
        return 0.0;  // Unrelated articles
    }
    
    private static boolean isRelatedChapter23Article(int art1, int art2) {
        // Group 1: Falsification crimes (258, 259, 260, 261, 262)
        int[] falsificationGroup = {258, 259, 260, 261, 262};
        // Group 2: Payment system crimes (260, 263, 267)
        int[] paymentGroup = {260, 263, 267};
        // Group 3: Economic abuse (268, 272, 273, 274, 275, 276)
        int[] economicGroup = {268, 272, 273, 274, 275, 276};
        
        return (inGroup(art1, falsificationGroup) && inGroup(art2, falsificationGroup)) ||
               (inGroup(art1, paymentGroup) && inGroup(art2, paymentGroup)) ||
               (inGroup(art1, economicGroup) && inGroup(art2, economicGroup));
    }
    
    private static boolean inGroup(int art, int[] group) {
        for (int g : group) {
            if (g == art) return true;
        }
        return false;
    }
    
    private static boolean isChapter23Article(int articleNum) {
        return articleNum >= 258 && articleNum <= 286;
    }
    
    /**
     * Compare damage amount (for Chapter 23 financial crimes)
     * Similar amounts = higher similarity
     */
    private static double compareDamageAmount(CaseDescription case1, CaseDescription case2) {
        // Try to get damage amount - use harm score as fallback
        Integer amount1 = case1.getTotalHarmScore();  // Could be extended to damage_amount field
        Integer amount2 = case2.getTotalHarmScore();
        
        if (amount1 == null || amount2 == null) {
            return 0.5;  // Neutral if no data
        }
        
        // Compare amounts using percentage difference
        double max = Math.max(amount1, amount2);
        if (max == 0) return 1.0;  // Both zero
        
        double diff = Math.abs(amount1 - amount2) / max;
        
        if (diff <= 0.1) return 1.0;    // Within 10%
        if (diff <= 0.25) return 0.85;  // Within 25%
        if (diff <= 0.5) return 0.65;   // Within 50%
        if (diff <= 1.0) return 0.40;   // Within 100%
        return 0.20;                     // Very different amounts
    }

    /**
     * Compare power dynamics (kept for backward compatibility)
     * Similar power relationships indicate similar case structures
     */
    private static double comparePowerDynamics(CaseDescription case1, CaseDescription case2) {
        Boolean workplace1 = case1.getOrganizationalContext();
        Boolean workplace2 = case2.getOrganizationalContext();
        
        Boolean superior1 = case1.getSuperiorSubordinate();
        Boolean superior2 = case2.getSuperiorSubordinate();

        int matches = 0;
        int total = 2;

        // Workplace context match
        if ((workplace1 != null && workplace1) == (workplace2 != null && workplace2)) {
            matches++;
        }

        // Superior/subordinate relationship match
        if ((superior1 != null && superior1) == (superior2 != null && superior2)) {
            matches++;
        }

        return (double)matches / total;
    }

    // ===== HELPER METHODS =====

    private static boolean isHarassmentType(String type) {
        return type.contains("stalking") || type.contains("harassment") ||
               type.contains("threat") || type.contains("endangering") ||
               type.contains("mobbing") || type.contains("proganj");
    }

    private static boolean isFinancialCrimeType(String type) {
        return type.contains("embezzlement") || type.contains("theft") ||
               type.contains("fraud") || type.contains("misappropriation") ||
               type.contains("falsifikovanje") || type.contains("фалсификовање") ||
               type.contains("counterfeiting") || type.contains("pranje") ||
               type.contains("money laundering") || type.contains("utaja") ||
               type.contains("tax evasion");
    }

    private static boolean isViolenceType(String type) {
        return type.contains("assault") || type.contains("violence") ||
               type.contains("zlostavlj") || type.contains("nasilje");
    }

    private static boolean isFalsificationCrimeType(String type) {
        // Chapter 23 crimes - Falsification crimes
        return type.contains("falsifikovanje novca") || type.contains("фалсификовање новца") ||
               type.contains("counterfeiting money") || type.contains("lazan novac") ||
               type.contains("falsifikovanje hartija") || type.contains("securities fraud") ||
               type.contains("kreditn") || type.contains("kartic") ||
               type.contains("credit card") || type.contains("payment card") ||
               type.contains("bezgotovinsko") || type.contains("cashless");
    }

    private static boolean isPaymentSystemCrimeType(String type) {
        // Chapter 23 crimes - Payment system crimes
        return type.contains("cek") || type.contains("check") ||
               type.contains("kartic") || type.contains("card") ||
               type.contains("platni") || type.contains("payment") ||
               type.contains("bezgotovinsk") || type.contains("cashless");
    }

    private static boolean isEconomicCrimeType(String type) {
        // Chapter 23 crimes - Economic operation crimes
        return type.contains("pranje novca") || type.contains("money laundering") ||
               type.contains("utaja") || type.contains("tax evasion") ||
               type.contains("krijumcar") || type.contains("smuggling") ||
               type.contains("monopol") || type.contains("monopoly") ||
               type.contains("stecaj") || type.contains("bankruptcy");
    }

    /**
     * Get similarity explanation (for debugging/display)
     * Updated for Chapter 23 specific metrics
     */
    public static String getSimilarityExplanation(CaseDescription case1, CaseDescription case2) {
        double caseTypeSim = compareCaseTypes(case1, case2);
        double articlesSim = compareArticlesCharged(case1, case2);
        double verdictSim = compareVerdicts(case1, case2);
        double damageSim = compareDamageAmount(case1, case2);
        double evidenceSim = compareEvidence(case1, case2);

        StringBuilder sb = new StringBuilder();
        sb.append("=== Case Similarity Analysis (Chapter 23) ===\n");
        sb.append(String.format("Crime Type:        %.1f%% (weight: %.0f%%)%n", caseTypeSim * 100, WEIGHT_CASE_TYPE * 100));
        sb.append(String.format("Articles Charged:  %.1f%% (weight: %.0f%%)%n", articlesSim * 100, WEIGHT_ARTICLES * 100));
        sb.append(String.format("Verdict/Sentence:  %.1f%% (weight: %.0f%%)%n", verdictSim * 100, WEIGHT_VERDICT * 100));
        sb.append(String.format("Damage Amount:     %.1f%% (weight: %.0f%%)%n", damageSim * 100, WEIGHT_DAMAGE * 100));
        sb.append(String.format("Evidence:          %.1f%% (weight: %.0f%%)%n", evidenceSim * 100, WEIGHT_EVIDENCE * 100));
        sb.append("----------------------------------------------\n");

        double total = calculateSimilarity(case1, case2);
        sb.append(String.format("TOTAL SIMILARITY:  %.1f%%\n", total * 100));
        
        // Add interpretation
        if (total >= 0.8) {
            sb.append("Interpretation: HIGH similarity - very relevant precedent\n");
        } else if (total >= 0.6) {
            sb.append("Interpretation: MODERATE similarity - useful for comparison\n");
        } else if (total >= 0.4) {
            sb.append("Interpretation: LOW similarity - limited relevance\n");
        } else {
            sb.append("Interpretation: MINIMAL similarity - different case type\n");
        }

        return sb.toString();
    }
    
    /**
     * Get detailed comparison of two cases including all attributes
     */
    public static String getDetailedComparison(CaseDescription case1, CaseDescription case2) {
        StringBuilder sb = new StringBuilder();
        sb.append("=== Detailed Case Comparison ===\n\n");
        
        sb.append(String.format("Case 1: %s%n", case1.getCaseNumber() != null ? case1.getCaseNumber() : "Unknown"));
        sb.append(String.format("Case 2: %s%n%n", case2.getCaseNumber() != null ? case2.getCaseNumber() : "Unknown"));
        
        // Crime type comparison
        sb.append("CRIME TYPE:\n");
        sb.append(String.format("  Case 1: %s%n", case1.getCaseType() != null ? case1.getCaseType() : "N/A"));
        sb.append(String.format("  Case 2: %s%n", case2.getCaseType() != null ? case2.getCaseType() : "N/A"));
        sb.append(String.format("  Similarity: %.1f%%%n%n", compareCaseTypes(case1, case2) * 100));
        
        // Articles comparison
        sb.append("ARTICLES CHARGED:\n");
        if (case1.getArticlesCharged() != null) {
            sb.append(String.format("  Case 1: %s%n", String.join(", ", case1.getArticlesCharged())));
        }
        if (case2.getArticlesCharged() != null) {
            sb.append(String.format("  Case 2: %s%n", String.join(", ", case2.getArticlesCharged())));
        }
        sb.append(String.format("  Similarity: %.1f%%%n%n", compareArticlesCharged(case1, case2) * 100));
        
        // Verdict comparison
        sb.append("VERDICT:\n");
        sb.append(String.format("  Case 1: %s%n", case1.getVerdict() != null ? case1.getVerdict() : "N/A"));
        sb.append(String.format("  Case 2: %s%n", case2.getVerdict() != null ? case2.getVerdict() : "N/A"));
        sb.append(String.format("  Similarity: %.1f%%%n%n", compareVerdicts(case1, case2) * 100));
        
        // Damage comparison
        sb.append("DAMAGE AMOUNT:\n");
        sb.append(String.format("  Case 1: %.2f EUR%n", case1.getDamageAmount()));
        sb.append(String.format("  Case 2: %.2f EUR%n", case2.getDamageAmount()));
        sb.append(String.format("  Similarity: %.1f%%%n%n", compareDamageAmount(case1, case2) * 100));
        
        // Overall
        sb.append("==============================\n");
        sb.append(getSimilarityExplanation(case1, case2));
        
        return sb.toString();
    }
}
