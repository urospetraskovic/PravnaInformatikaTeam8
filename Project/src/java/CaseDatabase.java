package cbr.database;

import java.util.*;

/**
 * CaseDatabase - Loads and manages all 12 Montenegrin verdict cases
 * Serves as the knowledge base for jCOLIBRI case-based reasoning system
 */
public class CaseDatabase {
    private List<CaseDescription> cases;
    
    public CaseDatabase() {
        this.cases = new ArrayList<>();
        loadAllCases();
    }

    private void loadAllCases() {
        // Case 1: K 217/24 - Threatening/Endangering Safety
        CaseDescription case1 = new CaseDescription();
        case1.setCaseId("Case_001");
        case1.setCaseNumber("K 217/24");
        case1.setCourt("Osnovni Sud u Beranji");
        case1.setJudge("Unknown");
        case1.setVerdictDate("2024");
        case1.setCaseType("Threatening/Endangering Safety");
        case1.setDefendantName("Not specified");
        case1.setDefendantOccupation("Unknown");
        case1.setVictimName("Not specified");
        case1.setVictimStatus("Unknown");
        case1.setIncidentDate("2024");
        case1.setIncidentLocation("Unknown");
        case1.setIncidentNarrative("Threatening/endangering safety of victim");
        case1.setWorkplaceContext(true);
        case1.setContextIndicator("Workplace harassment");
        case1.getArticlesCharged().add("Article 168 st.1 KZ CG");
        case1.setChargesCount(1);
        case1.setWitnessCount(0);
        case1.setExpertFindings(0);
        case1.setHarmPhysical(0);
        case1.setHarmPsychological(3);
        case1.setGuilty(true);
        case1.setAcquitted(false);
        case1.setConditional(false);
        case1.setSentenceType("Prison");
        case1.setExecutionStatus("Executed");
        cases.add(case1);

        // Case 2: K 277/12 - Labor Rights Violation
        CaseDescription case2 = new CaseDescription();
        case2.setCaseId("Case_002");
        case2.setCaseNumber("K 277/12");
        case2.setCourt("Osnovni Sud u Bijelo Polju");
        case2.setJudge("Unknown");
        case2.setVerdictDate("2013");
        case2.setCaseType("Labor Rights Violation / Workplace Harassment");
        case2.setDefendantName("Not specified");
        case2.setDefendantOccupation("Unknown");
        case2.setDefendantEmploymentStatus("Employed");
        case2.setVictimName("Not specified");
        case2.setVictimStatus("Unknown");
        case2.setVictimRelationship("Workplace colleague");
        case2.setWorkplaceRelationship(true);
        case2.setIncidentDate("2013");
        case2.setIncidentLocation("Workplace - Bijelo Polje");
        case2.setIncidentDuration("Ongoing");
        case2.setIncidentNarrative("Systematic workplace discrimination and harassment");
        case2.setWorkplaceContext(true);
        case2.setContextIndicator("Systematic workplace harassment");
        case2.getArticlesCharged().add("Article 224 KZ CG");
        case2.setChargesCount(1);
        case2.setWitnessCount(2);
        case2.setExpertFindings(0);
        case2.getDocumentaryEvidence().add("Employment records");
        case2.getDocumentaryEvidence().add("Organizational policy violations");
        case2.setHarmPhysical(0);
        case2.setHarmPsychological(3);
        case2.setSuperiorSubordinate(true);
        case2.setOrganizationalContext(true);
        case2.setGuilty(true);
        case2.setAcquitted(false);
        case2.setConditional(false);
        case2.setSentenceType("Prison/Suspended");
        case2.setExecutionStatus("Executed");
        cases.add(case2);

        // Case 3: K 292/2014 - Embezzlement (Original)
        CaseDescription case3 = new CaseDescription();
        case3.setCaseId("Case_003");
        case3.setCaseNumber("K 292/2014");
        case3.setCourt("Osnovni Sud u Bijelo Polju");
        case3.setJudge("Unknown");
        case3.setVerdictDate("2015");
        case3.setCaseType("Embezzlement / Misappropriation - Initial Verdict");
        case3.setDefendantName("Not specified");
        case3.setDefendantOccupation("Not specified");
        case3.setDefendantEmploymentStatus("Employed");
        case3.setDefendantPriorConvictions(0);
        case3.setVictimName("Not specified");
        case3.setVictimStatus("Organization");
        case3.setVictimRelationship("Employer");
        case3.setWorkplaceRelationship(true);
        case3.setIncidentDate("2014-2015");
        case3.setIncidentLocation("Workplace - Bijelo Polje");
        case3.setIncidentDuration("Multi-year embezzlement");
        case3.setIncidentNarrative("Complex embezzlement through accounting fraud");
        case3.setWorkplaceContext(true);
        case3.setContextIndicator("Financial crime / embezzlement");
        case3.getArticlesCharged().add("Article 272 st.2 KZ CG");
        case3.setChargesCount(9);
        case3.setGuiltyCounts(8);
        case3.setAcquittedCounts(1);
        case3.setWitnessCount(3);
        case3.setExpertFindings(1);
        case3.getDocumentaryEvidence().add("Accounting records");
        case3.getDocumentaryEvidence().add("Financial expert analysis");
        case3.setHarmPhysical(0);
        case3.setHarmPsychological(0);
        case3.setSuperiorSubordinate(true);
        case3.setOrganizationalContext(true);
        case3.setGuilty(true);
        case3.setAcquitted(false);
        case3.setConditional(false);
        case3.setSentenceType("Prison");
        case3.setAppealFiled(true);
        case3.setHigherCourtOutcome("Retrial ordered");
        cases.add(case3);

        // Case 4: K 64/14 - Threatening Safety (ACQUITTED)
        CaseDescription case4 = new CaseDescription();
        case4.setCaseId("Case_004");
        case4.setCaseNumber("K 64/14");
        case4.setCourt("Osnovni Sud u Cetinje");
        case4.setJudge("Unknown");
        case4.setVerdictDate("2015");
        case4.setCaseType("Threatening / Endangering Safety");
        case4.setDefendantName("Not specified");
        case4.setDefendantOccupation("Unknown");
        case4.setDefendantPriorConvictions(0);
        case4.setVictimName("Not specified");
        case4.setVictimStatus("Unknown");
        case4.setVictimRelationship("Unknown");
        case4.setIncidentDate("2014-2015");
        case4.setIncidentLocation("Cetinje");
        case4.setIncidentNarrative("Threats of violence without corroboration");
        case4.setContextIndicator("Threat case without sufficient evidence");
        case4.getArticlesCharged().add("Article 168 st.1 KZ CG");
        case4.setChargesCount(1);
        case4.setWitnessCount(1);
        case4.setExpertFindings(0);
        case4.setHarmPhysical(0);
        case4.setHarmPsychological(2);
        case4.setGuilty(false);
        case4.setAcquitted(true);
        case4.setConditional(false);
        case4.setSentenceType("None");
        case4.setSentenceDurationMonths(0);
        case4.setAcquittalReason("Insufficient witness credibility; context of prior conflict; reasonable doubt");
        cases.add(case4);

        // Case 5: K 170/12 - Workplace Safety Negligence
        CaseDescription case5 = new CaseDescription();
        case5.setCaseId("Case_005");
        case5.setCaseNumber("K 170/12");
        case5.setCourt("Osnovni Sud u Cetinje");
        case5.setJudge("Unknown");
        case5.setVerdictDate("2013");
        case5.setCaseType("Workplace Safety Negligence");
        case5.setDefendantName("Not specified");
        case5.setDefendantOccupation("Employer/Safety Officer");
        case5.setDefendantEmploymentStatus("Employed");
        case5.setDefendantPriorConvictions(0);
        case5.setVictimName("Not specified");
        case5.setVictimStatus("Employee");
        case5.setVictimRelationship("Subordinate");
        case5.setWorkplaceRelationship(true);
        case5.setIncidentDate("2012-2013");
        case5.setIncidentLocation("Workplace - Cetinje");
        case5.setIncidentNarrative("Employer failure to implement required protective safety measures");
        case5.setWorkplaceContext(true);
        case5.setContextIndicator("Workplace safety violation");
        case5.getArticlesCharged().add("Article 338 st.3 u vezi 329 KZ CG");
        case5.setChargesCount(1);
        case5.setWitnessCount(2);
        case5.setExpertFindings(1);
        case5.getDocumentaryEvidence().add("Site inspection findings");
        case5.getDocumentaryEvidence().add("Safety regulations");
        case5.setHarmPhysical(3);
        case5.setHarmPsychological(2);
        case5.setSuperiorSubordinate(true);
        case5.setOrganizationalContext(true);
        case5.setGuilty(true);
        case5.setAcquitted(false);
        case5.setConditional(false);
        case5.setSentenceType("Prison");
        case5.setExecutionStatus("Executed");
        cases.add(case5);

        // Case 6: K 292/2014 - Embezzlement (Retrial)
        CaseDescription case6 = new CaseDescription();
        case6.setCaseId("Case_006");
        case6.setCaseNumber("K 292/2014 (Re-trial)");
        case6.setCourt("Osnovni Sud u Bijelo Polju");
        case6.setJudge("Unknown");
        case6.setVerdictDate("2015");
        case6.setCaseType("Union Benefits Embezzlement - Retrial After Appeal");
        case6.setDefendantName("Not specified");
        case6.setDefendantOccupation("Not specified");
        case6.setDefendantEmploymentStatus("Employed");
        case6.setDefendantPriorConvictions(0);
        case6.setVictimName("Not specified");
        case6.setVictimStatus("Organization/Union");
        case6.setVictimRelationship("Employer");
        case6.setWorkplaceRelationship(true);
        case6.setIncidentDate("2014-2015");
        case6.setIncidentLocation("Workplace - Bijelo Polje");
        case6.setIncidentDuration("Multi-year embezzlement");
        case6.setIncidentNarrative("Union benefits embezzlement through systematic unauthorized withdrawals");
        case6.setWorkplaceContext(true);
        case6.setContextIndicator("Financial crime / embezzlement");
        case6.getArticlesCharged().add("Article 420 st.2 u vezi 49 KZ CG");
        case6.setChargesCount(9);
        case6.setGuiltyCounts(8);
        case6.setAcquittedCounts(1);
        case6.setWitnessCount(3);
        case6.setExpertFindings(1);
        case6.getDocumentaryEvidence().add("Financial records");
        case6.getDocumentaryEvidence().add("Organizational documentation");
        case6.setHarmPhysical(0);
        case6.setHarmPsychological(0);
        case6.setSuperiorSubordinate(true);
        case6.setOrganizationalContext(true);
        case6.setGuilty(true);
        case6.setAcquitted(false);
        case6.setConditional(false);
        case6.setSentenceType("Prison");
        case6.setAppealFiled(true);
        case6.setHigherCourtOutcome("Retrial - conviction upheld");
        cases.add(case6);

        // Case 7: K 30/2020 - Coal Theft (ACQUITTED)
        CaseDescription case7 = new CaseDescription();
        case7.setCaseId("Case_007");
        case7.setCaseNumber("K 30/2020");
        case7.setCourt("Osnovni Sud u Pljevlja");
        case7.setJudge("Unknown");
        case7.setVerdictDate("2020");
        case7.setCaseType("Coal Theft + Document Falsification");
        case7.setDefendantName("Not specified (3 defendants)");
        case7.setDefendantOccupation("Unknown");
        case7.setDefendantPriorConvictions(0);
        case7.setVictimName("Not specified");
        case7.setVictimStatus("Organization");
        case7.setVictimRelationship("Employer/Owner");
        case7.setWorkplaceRelationship(true);
        case7.setIncidentDate("2020");
        case7.setIncidentLocation("Pljevlja (coal mine)");
        case7.setIncidentNarrative("Theft of coal and falsification of official documents");
        case7.setWorkplaceContext(true);
        case7.setContextIndicator("Occupational crime");
        case7.getArticlesCharged().add("Article 272 st.1 u vezi st.23 KZ CG");
        case7.getArticlesCharged().add("Article 414 st.3 u vezi st.1 KZ CG");
        case7.setChargesCount(2);
        case7.setWitnessCount(2);
        case7.setExpertFindings(0);
        case7.getDocumentaryEvidence().add("Receipts with timestamps");
        case7.getPhysicalEvidence().add("Physical evidence - never located");
        case7.setHarmPhysical(0);
        case7.setHarmPsychological(0);
        case7.setSuperiorSubordinate(true);
        case7.setOrganizationalContext(true);
        case7.setGuilty(false);
        case7.setAcquitted(true);
        case7.setConditional(false);
        case7.setSentenceType("None");
        case7.setSentenceDurationMonths(0);
        case7.setAcquittalReason("Documentary evidence contradicted witness testimony; physical evidence never located; reasonable doubt");
        cases.add(case7);

        // Case 8: K 22/2022 - Social Insurance Fraud (ACQUITTED)
        CaseDescription case8 = new CaseDescription();
        case8.setCaseId("Case_008");
        case8.setCaseNumber("K 22/2022");
        case8.setCourt("Osnovni Sud u Podgorici");
        case8.setJudge("Larisa Mijušković-Stamatović");
        case8.setVerdictDate("2023-05-16");
        case8.setCaseType("Social Insurance Fraud - Simulated Incapacity");
        case8.setDefendantName("D.M.");
        case8.setDefendantOccupation("Diplomirani magistar građevinarstva");
        case8.setDefendantGender("Male");
        case8.setDefendantEducation("University (Architecture)");
        case8.setDefendantEmploymentStatus("Employed");
        case8.setDefendantMaritalStatus("Married");
        case8.setDefendantChildren(2);
        case8.setDefendantFinancialStatus("Poor");
        case8.setDefendantPriorConvictions(0);
        case8.setVictimName("Not specified");
        case8.setVictimStatus("Health insurance system");
        case8.setVictimRelationship("Social insurance beneficiary");
        case8.setWorkplaceRelationship(false);
        case8.setIncidentDate("2019-05-07 to 2020-12-31");
        case8.setIncidentLocation("Multiple courts and private entities");
        case8.setIncidentDuration("630 days (20+ months)");
        case8.setIncidentNarrative("Defendant claimed inability to work while receiving freelance expert witness work income");
        case8.setWorkplaceContext(true);
        case8.setContextIndicator("Workplace mobbing as underlying cause");
        case8.getArticlesCharged().add("Article 230 u vezi čl. 49 st. 1 KZ CG");
        case8.setChargesCount(1);
        case8.setWitnessCount(2);
        case8.setExpertFindings(2);
        case8.getDocumentaryEvidence().add("Bank transaction records");
        case8.getDocumentaryEvidence().add("Court notification letters");
        case8.getDocumentaryEvidence().add("Medical documentation");
        case8.setHarmPhysical(0);
        case8.setHarmPsychological(0);
        case8.setGuilty(false);
        case8.setAcquitted(true);
        case8.setConditional(false);
        case8.setSentenceType("None");
        case8.setSentenceDurationMonths(0);
        case8.setAcquittalReason("Physician testimony established legitimate incapacity; periodic expert work was therapeutic component of treatment; no fraud proven");
        case8.setAppealFiled(false);
        cases.add(case8);

        // Case 9: K 98/2018 - STALKING (CRITICAL - NEWLY INTEGRATED)
        CaseDescription case9 = new CaseDescription();
        case9.setCaseId("Case_009");
        case9.setCaseNumber("K 98/2018");
        case9.setCourt("Osnovni Sud u Podgorici");
        case9.setJudge("Rade Ćetković");
        case9.setVerdictDate("2018-05-28");
        case9.setCaseType("Stalking / Proganjanje");
        case9.setDefendantName("I.P.");
        case9.setDefendantOccupation("Diplomirani pravnik (law graduate)");
        case9.setDefendantGender("Male");
        case9.setDefendantEducation("University - Law");
        case9.setDefendantEmploymentStatus("Employed - Sejm/Government");
        case9.setDefendantMaritalStatus("Unmarried");
        case9.setDefendantChildren(1);
        case9.setDefendantFinancialStatus("Poor");
        case9.setDefendantPriorConvictions(0);
        case9.setDefendantMentalHealth("Paranoid psychosis");
        case9.setVictimName("M. Š.");
        case9.setVictimStatus("Director of Centar za sudsku medicinu");
        case9.setVictimRelationship("Professional acquaintance");
        case9.setWorkplaceRelationship(false);
        case9.setVictimAge(null);
        case9.setIncidentDate("2017-12-20 to 2018-01-22");
        case9.setIncidentTime("Multiple times - including 00:58, 02:33, 04:30+ hours");
        case9.setIncidentLocation("Multiple - phone, SMS, Viber, in-person court building");
        case9.setIncidentDuration("33 days");
        case9.setIncidentNarrative("Persistent unwanted contact via 20+ phone calls, explicit SMS/Viber messages (threats, accusations), in-person confrontation at court building");
        case9.setWorkplaceContext(false);
        case9.setContextIndicator("Mental health crisis - workplace harassment at defendant employer");
        case9.setTemporalPattern("Escalating");
        case9.getArticlesCharged().add("Article 168a st. 1 KZ CG");
        case9.setChargesCount(1);
        case9.setWitnessCount(4);
        case9.setExpertFindings(1);
        case9.getDocumentaryEvidence().add("Phone records");
        case9.getDocumentaryEvidence().add("SMS/Viber transcripts");
        case9.getDocumentaryEvidence().add("Video surveillance");
        case9.getDocumentaryEvidence().add("Email records");
        case9.setVideoSurveillance(true);
        case9.setPhoneRecords(true);
        case9.setPsychologicalAssessment(true);
        case9.setHarmPhysical(0);
        case9.setHarmPsychological(4);
        case9.setFamilyImpact("Spouse required psychiatric care for stress reaction");
        case9.setOccupationalImpact("Medical director unable to answer work phones due to harassment anxiety");
        case9.setStalkingContext("Multiple communication means + in-person + threats + false accusations");
        case9.setHarassmentPattern("Repeated unwanted contact, escalating to explicit threats and accusations");
        case9.setGuilty(true);
        case9.setAcquitted(false);
        case9.setConditional(false);
        case9.setSentenceType("Prison + Psychiatric Treatment");
        case9.setSentenceDurationMonths(6);
        case9.setSentenceConditions("Mandatory psychiatric treatment in SPB Dobrota, Kotor");
        case9.setExecutionStatus("Executed");
        cases.add(case9);

        // Case 10: K 664/2022 - Workplace Assault
        CaseDescription case10 = new CaseDescription();
        case10.setCaseId("Case_010");
        case10.setCaseNumber("K 664/2022");
        case10.setCourt("Osnovni Sud u Podgorici");
        case10.setJudge("Larisa Mijušković-Stamatović");
        case10.setVerdictDate("2022-11-14");
        case10.setCaseType("Workplace Assault / Zlostavljanje");
        case10.setDefendantName("E.K.");
        case10.setDefendantAge(37);
        case10.setDefendantOccupation("Viši savjetnik - administrative office employee");
        case10.setDefendantGender("Male");
        case10.setDefendantEducation("Pismen");
        case10.setDefendantEmploymentStatus("Employed");
        case10.setDefendantMaritalStatus("Unmarried");
        case10.setDefendantChildren(1);
        case10.setDefendantFinancialStatus("Poor");
        case10.setDefendantPriorConvictions(0);
        case10.setDefendantMentalHealth("Diabetes, stress-related");
        case10.setVictimName("M.B.");
        case10.setVictimStatus("N.P. (supervisor/director)");
        case10.setVictimAge(61);
        case10.setVictimRelationship("Direct supervisor");
        case10.setWorkplaceRelationship(true);
        case10.setIncidentDate("2022-09-26");
        case10.setIncidentTime("08:30 hours");
        case10.setIncidentLocation("Victim's office - M. P. administrative building, Podgorica");
        case10.setIncidentDuration("Several minutes");
        case10.setIncidentNarrative("Defendant entered supervisor's office, verbally confronted, struck victim with open hand on right head/ear, victim fell, defendant continued kicking");
        case10.setWorkplaceContext(true);
        case10.setContextIndicator("Workplace assault by subordinate on supervisor");
        case10.getArticlesCharged().add("Article 166a st.1 KZ CG");
        case10.setChargesCount(1);
        case10.setWitnessCount(5);
        case10.setExpertFindings(1);
        case10.getDocumentaryEvidence().add("Medical examination records");
        case10.getPhysicalEvidence().add("Medical records showing injuries");
        case10.setVideoSurveillance(true);
        case10.setHarmPhysical(2);
        case10.setHarmPsychological(3);
        case10.setSuperiorSubordinate(true);
        case10.setOrganizationalContext(true);
        case10.setGuilty(true);
        case10.setAcquitted(false);
        case10.setConditional(false);
        case10.setSentenceType("Prison");
        case10.setSentenceDurationMonths(4);
        case10.setExecutionStatus("Executed");
        cases.add(case10);

        // Case 11: K 592/2022 - Theft + Credit Card Fraud
        CaseDescription case11 = new CaseDescription();
        case11.setCaseId("Case_011");
        case11.setCaseNumber("K 592/2022");
        case11.setCourt("Osnovni Sud u Podgorici");
        case11.setJudge("Larisa Mijušković-Stamatović");
        case11.setVerdictDate("2022-11-21");
        case11.setCaseType("Theft + Credit Card Fraud");
        case11.setDefendantName("L.A.");
        case11.setDefendantOccupation("Frizerka (hairdresser)");
        case11.setDefendantGender("Female");
        case11.setDefendantEducation("Srednja hemijska škola");
        case11.setDefendantEmploymentStatus("Unemployed");
        case11.setDefendantMaritalStatus("Unmarried");
        case11.setDefendantChildren(1);
        case11.setDefendantFinancialStatus("Poor");
        case11.setDefendantPriorConvictions(3);
        case11.setDefendantAddictionStatus("In drug treatment - buprenorphine therapy");
        case11.setVictimName("V.B.");
        case11.setVictimStatus("Taxi driver");
        case11.setVictimRelationship("Stranger");
        case11.setWorkplaceRelationship(false);
        case11.setIncidentDate("2022-09");
        case11.setIncidentTime("15:00 hours");
        case11.setIncidentLocation("Taxi vehicle - Podgorica region");
        case11.setIncidentDuration("During vehicle ride");
        case11.setIncidentNarrative("Defendant stole wallet during taxi ride; later used stolen credit cards for purchases");
        case11.setWorkplaceContext(false);
        case11.setContextIndicator("Opportunistic property crime");
        case11.getArticlesCharged().add("Article 239 st.1 KZ CG");
        case11.getArticlesCharged().add("Article 260 st.2 u vezi st.1 KZ CG");
        case11.setChargesCount(2);
        case11.setWitnessCount(1);
        case11.setExpertFindings(1);
        case11.getDocumentaryEvidence().add("Bank transaction records");
        case11.getDocumentaryEvidence().add("Credit card statements");
        case11.getPhysicalEvidence().add("Stolen wallet (recovered)");
        case11.getPhysicalEvidence().add("Credit card (recovered)");
        case11.setVideoSurveillance(true);
        case11.setHarmPhysical(0);
        case11.setHarmPsychological(2);
        case11.setGuilty(true);
        case11.setAcquitted(false);
        case11.setConditional(false);
        case11.setSentenceType("Prison");
        case11.setSentenceDurationMonths(6);
        case11.setExecutionStatus("Executed");
        cases.add(case11);

        // Case 12: K 128/15 - Threatening Safety (CONDITIONAL)
        CaseDescription case12 = new CaseDescription();
        case12.setCaseId("Case_012");
        case12.setCaseNumber("K 128/15");
        case12.setCourt("Osnovni Sud u Rožaje");
        case12.setJudge("Unknown");
        case12.setVerdictDate("2015-10-26");
        case12.setCaseType("Threatening / Endangering Safety");
        case12.setDefendantName("N.V.");
        case12.setDefendantOccupation("Volunteer in local government");
        case12.setDefendantGender("Male");
        case12.setDefendantEducation("University educated");
        case12.setDefendantFinancialStatus("Poor");
        case12.setDefendantPriorConvictions(0);
        case12.setVictimName("H.K.");
        case12.setVictimStatus("Health center director");
        case12.setVictimRelationship("Professional acquaintance");
        case12.setWorkplaceRelationship(false);
        case12.setIncidentDate("2015-08-27");
        case12.setIncidentTime("07:00 hours");
        case12.setIncidentLocation("Health center - Rožaje");
        case12.setIncidentDuration("Single incident");
        case12.setIncidentNarrative("Defendant made verbal threats of violence, alleging possession of deadly weapons");
        case12.setWorkplaceContext(false);
        case12.setContextIndicator("Workplace conflict escalation - defendant's mother employed at facility");
        case12.getArticlesCharged().add("Article 168 st.1 KZ CG");
        case12.setChargesCount(1);
        case12.setWitnessCount(5);
        case12.setExpertFindings(0);
        case12.setHarmPhysical(0);
        case12.setHarmPsychological(3);
        case12.setGuilty(true);
        case12.setAcquitted(false);
        case12.setConditional(true);
        case12.setSentenceType("Conditional imprisonment");
        case12.setSentenceDurationMonths(60);
        case12.setSentenceConditions("Not executed if no new crime within 1 year");
        case12.setExecutionStatus("Conditional");
        cases.add(case12);

        // Case 13: K 375/14 - Domestic Violence (CONDITIONAL)
        CaseDescription case13 = new CaseDescription();
        case13.setCaseId("Case_013");
        case13.setCaseNumber("K 375/14");
        case13.setCourt("Osnovni Sud u Kotor");
        case13.setJudge("Unknown");
        case13.setVerdictDate("2015-02-03");
        case13.setCaseType("Domestic Violence");
        case13.setDefendantName("K.Ž.");
        case13.setDefendantOccupation("Hospitality worker");
        case13.setDefendantGender("Male");
        case13.setDefendantEducation("High school");
        case13.setDefendantEmploymentStatus("Employed");
        case13.setDefendantMaritalStatus("Vanbračna zajednica (common-law partnership)");
        case13.setDefendantChildren(1);
        case13.setDefendantPriorConvictions(3);
        case13.setVictimName("K.N.");
        case13.setVictimStatus("Common-law partner");
        case13.setVictimRelationship("Intimate partner");
        case13.setWorkplaceRelationship(false);
        case13.setIncidentDate("2014-08-11");
        case13.setIncidentTime("20:00 hours");
        case13.setIncidentLocation("Home - Kotor");
        case13.setIncidentDuration("Single incident");
        case13.setIncidentNarrative("Defendant physically assaulted partner with fists after verbal dispute");
        case13.setWorkplaceContext(false);
        case13.setContextIndicator("Domestic violence - intimate partner violence");
        case13.getArticlesCharged().add("Article 220 st.1 KZ CG");
        case13.setChargesCount(1);
        case13.setWitnessCount(0);
        case13.setExpertFindings(1);
        case13.getDocumentaryEvidence().add("Medical examination records");
        case13.getPhysicalEvidence().add("Medical findings");
        case13.setHarmPhysical(1);
        case13.setHarmPsychological(2);
        case13.setGuilty(true);
        case13.setAcquitted(false);
        case13.setConditional(true);
        case13.setSentenceType("Conditional imprisonment");
        case13.setSentenceDurationMonths(30);
        case13.setSentenceConditions("Not executed if no new crime within 1 year");
        case13.setExecutionStatus("Conditional");
        cases.add(case13);
    }

    /**
     * Get all cases in database
     */
    public List<CaseDescription> getAllCases() {
        return new ArrayList<>(cases);
    }

    /**
     * Get case by case number
     */
    public CaseDescription getCaseByNumber(String caseNumber) {
        for (CaseDescription c : cases) {
            if (c.getCaseNumber().equals(caseNumber)) {
                return c;
            }
        }
        return null;
    }

    /**
     * Get cases by verdict type
     */
    public List<CaseDescription> getCasesByVerdict(String verdictType) {
        List<CaseDescription> result = new ArrayList<>();
        for (CaseDescription c : cases) {
            if ("guilty".equalsIgnoreCase(verdictType) && c.getGuilty()) {
                result.add(c);
            } else if ("acquitted".equalsIgnoreCase(verdictType) && c.getAcquitted()) {
                result.add(c);
            } else if ("conditional".equalsIgnoreCase(verdictType) && c.getConditional()) {
                result.add(c);
            }
        }
        return result;
    }

    /**
     * Get cases by crime type
     */
    public List<CaseDescription> getCasesByType(String caseType) {
        List<CaseDescription> result = new ArrayList<>();
        String pattern = caseType.toLowerCase();
        for (CaseDescription c : cases) {
            if (c.getCaseType().toLowerCase().contains(pattern)) {
                result.add(c);
            }
        }
        return result;
    }

    /**
     * Get workplace-related cases
     */
    public List<CaseDescription> getWorkplaceCases() {
        List<CaseDescription> result = new ArrayList<>();
        for (CaseDescription c : cases) {
            if (c.isWorkplaceCase()) {
                result.add(c);
            }
        }
        return result;
    }

    /**
     * Get harassment/stalking cases
     */
    public List<CaseDescription> getHarassmentCases() {
        List<CaseDescription> result = new ArrayList<>();
        for (CaseDescription c : cases) {
            if (c.isHarassmentCase()) {
                result.add(c);
            }
        }
        return result;
    }

    /**
     * Get total case count
     */
    public int getCaseCount() {
        return cases.size();
    }

    /**
     * Print database statistics
     */
    public void printStatistics() {
        System.out.println("\n=== CASE DATABASE STATISTICS ===");
        System.out.println("Total cases: " + cases.size());
        
        int guilty = 0, acquitted = 0, conditional = 0;
        for (CaseDescription c : cases) {
            if (c.getGuilty()) guilty++;
            if (c.getAcquitted()) acquitted++;
            if (c.getConditional()) conditional++;
        }
        
        System.out.println("Guilty verdicts: " + guilty);
        System.out.println("Acquitted verdicts: " + acquitted);
        System.out.println("Conditional sentences: " + conditional);
        System.out.println("Workplace cases: " + getWorkplaceCases().size());
        System.out.println("Harassment cases: " + getHarassmentCases().size());
        System.out.println("================================\n");
    }
}
