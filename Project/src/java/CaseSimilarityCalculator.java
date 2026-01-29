package cbr.similarity;

import cbr.database.CaseDescription;
import java.util.*;

/**
 * CaseSimilarityCalculator - Computes similarity between two legal cases
 * Uses weighted attributes to determine how similar two verdicts are
 * 
 * Similarity Metrics:
 * - Case Type Match: 0.4 weight (most important)
 * - Verdict Type Match: 0.25 weight
 * - Harm Assessment: 0.15 weight
 * - Evidence Quality: 0.1 weight
 * - Power Dynamics: 0.1 weight
 * 
 * Result: Similarity score 0.0 (completely different) to 1.0 (identical)
 */
public class CaseSimilarityCalculator {
    
    // Weighting factors for different attributes
    private static final double WEIGHT_CASE_TYPE = 0.40;
    private static final double WEIGHT_VERDICT = 0.25;
    private static final double WEIGHT_HARM = 0.15;
    private static final double WEIGHT_EVIDENCE = 0.10;
    private static final double WEIGHT_POWER_DYNAMICS = 0.10;

    /**
     * Calculate overall similarity between two cases
     * Returns a score from 0.0 to 1.0
     */
    public static double calculateSimilarity(CaseDescription case1, CaseDescription case2) {
        double caseTypeSim = compareCaseTypes(case1, case2);
        double verdictSim = compareVerdicts(case1, case2);
        double harmSim = compareHarm(case1, case2);
        double evidenceSim = compareEvidence(case1, case2);
        double powerDynSim = comparePowerDynamics(case1, case2);

        double totalSimilarity = 
            (caseTypeSim * WEIGHT_CASE_TYPE) +
            (verdictSim * WEIGHT_VERDICT) +
            (harmSim * WEIGHT_HARM) +
            (evidenceSim * WEIGHT_EVIDENCE) +
            (powerDynSim * WEIGHT_POWER_DYNAMICS);

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

        // Check for related crime categories
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
     * Compare power dynamics
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
               type.contains("fraud") || type.contains("misappropriation");
    }

    private static boolean isViolenceType(String type) {
        return type.contains("assault") || type.contains("violence") ||
               type.contains("zlostavlj") || type.contains("nasilje");
    }

    /**
     * Get similarity explanation (for debugging/display)
     */
    public static String getSimilarityExplanation(CaseDescription case1, CaseDescription case2) {
        double caseTypeSim = compareCaseTypes(case1, case2);
        double verdictSim = compareVerdicts(case1, case2);
        double harmSim = compareHarm(case1, case2);
        double evidenceSim = compareEvidence(case1, case2);
        double powerDynSim = comparePowerDynamics(case1, case2);

        StringBuilder sb = new StringBuilder();
        sb.append(String.format("Case Type: %.2f%n", caseTypeSim * 100));
        sb.append(String.format("Verdict: %.2f%n", verdictSim * 100));
        sb.append(String.format("Harm: %.2f%n", harmSim * 100));
        sb.append(String.format("Evidence: %.2f%n", evidenceSim * 100));
        sb.append(String.format("Power Dynamics: %.2f%n", powerDynSim * 100));

        double total = calculateSimilarity(case1, case2);
        sb.append(String.format("TOTAL: %.2f%%", total * 100));

        return sb.toString();
    }
}
