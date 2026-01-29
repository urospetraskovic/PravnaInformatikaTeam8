import cbr.database.CaseDescription;
import cbr.database.CaseDatabase;
import cbr.retrieval.KNNRetriever;
import cbr.retrieval.KNNRetriever.CaseMatch;
import java.util.*;

/**
 * MontenegrianLegalCBR - Main application for jCOLIBRI legal precedent matching
 * 
 * Workplace Mobbing Case-Based Reasoning System
 * 12 verified Montenegrin Supreme Court verdicts
 * Real-time case similarity analysis and precedent retrieval
 */
public class MontenegrianLegalCBR {
    private CaseDatabase caseDatabase;
    private KNNRetriever retriever;
    private Scanner scanner;

    public MontenegrianLegalCBR() {
        this.caseDatabase = new CaseDatabase();
        this.retriever = new KNNRetriever(caseDatabase, 5);
        this.scanner = new Scanner(System.in);
    }

    public static void main(String[] args) {
        MontenegrianLegalCBR app = new MontenegrianLegalCBR();
        app.run();
    }

    private void run() {
        printWelcome();
        
        boolean running = true;
        while (running) {
            printMenu();
            String choice = scanner.nextLine().trim();

            switch (choice) {
                case "1":
                    caseDatabase.printStatistics();
                    break;
                case "2":
                    listAllCases();
                    break;
                case "3":
                    searchByType();
                    break;
                case "4":
                    searchByVerdict();
                    break;
                case "5":
                    viewCaseDetails();
                    break;
                case "6":
                    runTestScenarios();
                    break;
                case "7":
                    running = false;
                    System.out.println("\nThank you for using Montenegrian Legal CBR System.");
                    System.out.println("Exiting...\n");
                    break;
                default:
                    System.out.println("Invalid choice. Please try again.\n");
            }
        }
        scanner.close();
    }

    private void printWelcome() {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("MONTENEGRIAN LEGAL PRECEDENT MATCHING SYSTEM");
        System.out.println("Case-Based Reasoning for Workplace Mobbing & Related Crimes");
        System.out.println("=".repeat(80));
        System.out.println("\nDatabase: 12 Supreme Court Verdicts (2012-2024)");
        System.out.println("Crime Types: Harassment, Stalking, Violence, Financial Crimes");
        System.out.println("Coverage: 7 Montenegrian Courts\n");
    }

    private void printMenu() {
        System.out.println("\n--- MAIN MENU ---");
        System.out.println("1. View Database Statistics");
        System.out.println("2. List All Cases");
        System.out.println("3. Search by Case Type");
        System.out.println("4. Search by Verdict");
        System.out.println("5. View Case Details");
        System.out.println("6. Run Test Scenarios");
        System.out.println("7. Exit");
        System.out.print("\nSelect option (1-7): ");
    }

    private void listAllCases() {
        System.out.println("\n--- ALL CASES IN DATABASE ---\n");
        int count = 1;
        for (CaseDescription c : caseDatabase.getAllCases()) {
            String verdict = c.getGuilty() ? "GUILTY" : (c.getAcquitted() ? "ACQUITTED" : "CONDITIONAL");
            System.out.printf("%2d. %s - %s (%s)%n", count, c.getCaseNumber(), c.getCaseType(), verdict);
            System.out.printf("    Court: %s | Judge: %s%n", c.getCourt(), c.getJudge() != null ? c.getJudge() : "Unknown");
            System.out.printf("    Articles: %s%n\n", String.join(", ", c.getArticlesCharged()));
            count++;
        }
    }

    private void searchByType() {
        System.out.println("\n--- SEARCH BY CASE TYPE ---");
        System.out.println("Available types:");
        System.out.println("1. Threatening/Safety");
        System.out.println("2. Harassment");
        System.out.println("3. Stalking");
        System.out.println("4. Workplace Assault");
        System.out.println("5. Financial Crimes");
        System.out.print("Enter search term: ");
        String term = scanner.nextLine().trim();

        List<CaseDescription> results = caseDatabase.getCasesByType(term);
        
        if (results.isEmpty()) {
            System.out.println("No cases found for type: " + term);
        } else {
            System.out.println("\nFound " + results.size() + " case(s):\n");
            for (CaseDescription c : results) {
                System.out.println("- " + c.getCaseNumber() + ": " + c.getCaseType());
            }
        }
    }

    private void searchByVerdict() {
        System.out.println("\n--- SEARCH BY VERDICT ---");
        System.out.println("1. Guilty");
        System.out.println("2. Acquitted");
        System.out.println("3. Conditional");
        System.out.print("Select verdict type: ");
        String choice = scanner.nextLine().trim();

        String verdictType = "";
        switch (choice) {
            case "1": verdictType = "guilty"; break;
            case "2": verdictType = "acquitted"; break;
            case "3": verdictType = "conditional"; break;
            default: 
                System.out.println("Invalid choice.");
                return;
        }

        List<CaseDescription> results = caseDatabase.getCasesByVerdict(verdictType);
        System.out.println("\nFound " + results.size() + " " + verdictType + " cases:\n");
        
        for (CaseDescription c : results) {
            Integer sentence = c.getSentenceDurationMonths();
            String sentenceStr = sentence != null && sentence > 0 ? 
                " - " + sentence + " months" : "";
            System.out.println("- " + c.getCaseNumber() + ": " + c.getCaseType() + sentenceStr);
        }
    }

    private void viewCaseDetails() {
        System.out.print("\nEnter case number (e.g., K 98/2018): ");
        String caseNumber = scanner.nextLine().trim();

        CaseDescription c = caseDatabase.getCaseByNumber(caseNumber);
        if (c == null) {
            System.out.println("Case not found: " + caseNumber);
            return;
        }

        printCaseDetails(c);
    }

    private void printCaseDetails(CaseDescription c) {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("CASE DETAILS: " + c.getCaseNumber());
        System.out.println("=".repeat(80));

        System.out.println("\n[BASIC INFO]");
        System.out.println("Type: " + c.getCaseType());
        System.out.println("Court: " + c.getCourt());
        System.out.println("Judge: " + (c.getJudge() != null ? c.getJudge() : "Unknown"));
        System.out.println("Verdict Date: " + c.getVerdictDate());

        System.out.println("\n[DEFENDANT]");
        System.out.println("Name: " + (c.getDefendantName() != null ? c.getDefendantName() : "Not specified"));
        System.out.println("Occupation: " + (c.getDefendantOccupation() != null ? c.getDefendantOccupation() : "Unknown"));
        System.out.println("Prior Convictions: " + (c.getDefendantPriorConvictions() != null ? c.getDefendantPriorConvictions() : "Unknown"));
        if (c.getDefendantMentalHealth() != null) {
            System.out.println("Mental Health: " + c.getDefendantMentalHealth());
        }

        System.out.println("\n[VICTIM]");
        System.out.println("Name: " + (c.getVictimName() != null ? c.getVictimName() : "Not specified"));
        System.out.println("Status: " + (c.getVictimStatus() != null ? c.getVictimStatus() : "Unknown"));
        System.out.println("Relationship: " + (c.getVictimRelationship() != null ? c.getVictimRelationship() : "Unknown"));

        System.out.println("\n[INCIDENT]");
        System.out.println("Date: " + c.getIncidentDate());
        System.out.println("Location: " + c.getIncidentLocation());
        System.out.println("Description: " + c.getIncidentNarrative());
        System.out.println("Harm - Physical: " + c.getHarmPhysical() + "/5");
        System.out.println("Harm - Psychological: " + c.getHarmPsychological() + "/5");

        System.out.println("\n[LEGAL]");
        System.out.println("Articles: " + String.join(", ", c.getArticlesCharged()));
        System.out.println("Charges: " + c.getChargesCount());
        if (c.getGuiltyCounts() != null && c.getGuiltyCounts() > 0) {
            System.out.println("Guilty Counts: " + c.getGuiltyCounts());
        }
        if (c.getAcquittedCounts() != null && c.getAcquittedCounts() > 0) {
            System.out.println("Acquitted Counts: " + c.getAcquittedCounts());
        }

        System.out.println("\n[EVIDENCE]");
        System.out.println("Witnesses: " + c.getWitnessCount());
        System.out.println("Expert Findings: " + c.getExpertFindings());
        System.out.println("Documentary Evidence: " + String.join("; ", c.getDocumentaryEvidence()));

        System.out.println("\n[VERDICT]");
        String verdict = c.getGuilty() ? "GUILTY" : (c.getAcquitted() ? "ACQUITTED" : "CONDITIONAL");
        System.out.println("Outcome: " + verdict);
        if (c.getSentenceDurationMonths() != null && c.getSentenceDurationMonths() > 0) {
            System.out.println("Sentence: " + c.getSentenceDurationMonths() + " months");
        }
        if (c.getAcquittalReason() != null) {
            System.out.println("Reason: " + c.getAcquittalReason());
        }

        System.out.println("\n" + "=".repeat(80) + "\n");
    }

    private void runTestScenarios() {
        System.out.println("\n" + "=".repeat(80));
        System.out.println("RUNNING AUTOMATED TEST SCENARIOS");
        System.out.println("=".repeat(80));

        // Test 1: Stalking case similarity
        System.out.println("\nTEST 1: Stalking Pattern Recognition");
        CaseDescription stalkingQuery = new CaseDescription();
        stalkingQuery.setCaseType("Stalking / Proganjanje");
        stalkingQuery.setPhoneRecords(true);
        stalkingQuery.setPsychologicalAssessment(true);
        stalkingQuery.setHarmPsychological(4);

        List<CaseMatch> stalkingResults = retriever.retrieveSimilarCases(stalkingQuery, 0.5);
        if (!stalkingResults.isEmpty()) {
            System.out.println("Top match: " + stalkingResults.get(0).toString());
        }

        // Test 2: Workplace assault
        System.out.println("\nTEST 2: Workplace Assault Detection");
        CaseDescription assaultQuery = new CaseDescription();
        assaultQuery.setCaseType("Workplace Assault");
        assaultQuery.setVideoSurveillance(true);
        assaultQuery.setWitnessCount(5);
        assaultQuery.setSuperiorSubordinate(true);

        List<CaseMatch> assaultResults = retriever.retrieveSimilarCases(assaultQuery, 0.5);
        if (!assaultResults.isEmpty()) {
            System.out.println("Top match: " + assaultResults.get(0).toString());
        }

        // Test 3: Acquittal patterns
        System.out.println("\nTEST 3: Acquittal Pattern Analysis");
        List<CaseDescription> acquittedCases = caseDatabase.getCasesByVerdict("acquitted");
        System.out.println("Acquitted cases found: " + acquittedCases.size());
        for (CaseDescription ac : acquittedCases) {
            System.out.println("- " + ac.getCaseNumber() + ": " + ac.getCaseType());
        }

        System.out.println("\n" + "=".repeat(80));
        System.out.println("TEST SCENARIOS COMPLETED\n");
    }
}
