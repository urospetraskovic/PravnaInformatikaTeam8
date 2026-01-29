package cbr.database;

import java.io.Serializable;
import java.util.*;

/**
 * CaseDescription - Montenegrin Legal Case Model for jCOLIBRI
 * Represents a single court verdict with all relevant legal, evidentiary, and outcome information
 * 
 * Supported Crime Types:
 * - Article 168/168a: Threats, harassment, stalking
 * - Article 166a: Workplace assault
 * - Article 220: Domestic violence
 * - Article 224: Labor rights violations
 * - Article 230: Social insurance fraud
 * - Article 239: Theft
 * - Article 260: Credit card fraud
 * - Article 272: Embezzlement, document falsification
 * - Article 338: Safety negligence
 * - Article 414: Document falsification
 * - Article 420: Union benefits embezzlement
 */
public class CaseDescription implements Serializable {
    private static final long serialVersionUID = 1L;

    // ===== IDENTIFIERS =====
    private String caseId;           // Unique database identifier (e.g., Case_001)
    private String caseNumber;       // Official K number (e.g., K 217/24)
    private String court;            // Court name and location
    private String judge;            // Judge name
    private String verdictDate;      // Date of verdict
    private String caseType;         // Legal classification

    // ===== DEFENDANT INFORMATION =====
    private String defendantName;
    private String defendantJMBG;    // National ID
    private String defendantBirthdate;
    private Integer defendantAge;
    private String defendantGender;  // M/F
    private String defendantOccupation;
    private String defendantEducation;
    private String defendantEmploymentStatus;  // Employed/Unemployed/Self-employed
    private String defendantMaritalStatus;
    private Integer defendantChildren;
    private String defendantFinancialStatus;
    private Integer defendantPriorConvictions;
    private String defendantMentalHealth;  // Psychiatric diagnosis if applicable
    private String defendantAddictionStatus;

    // ===== VICTIM INFORMATION =====
    private String victimName;
    private String victimStatus;     // Role (employee, employer, family, etc.)
    private String victimRelationship; // Relationship to defendant
    private Boolean workplaceRelationship; // Yes/No
    private Integer victimAge;
    private Integer harmPhysical;    // 0-5 scale
    private Integer harmPsychological; // 0-5 scale
    private String familyImpact;     // Collateral effects
    private String occupationalImpact;

    // ===== INCIDENT DETAILS =====
    private String incidentDate;
    private String incidentTime;
    private String incidentLocation;
    private String incidentDuration;
    private String incidentNarrative;
    private Boolean workplaceContext;
    private String contextIndicator; // Classification
    private String temporalPattern;  // Single/repeated/escalating

    // ===== LEGAL INFORMATION =====
    private List<String> articlesCharged;
    private Integer chargesCount;
    private Integer guiltyCounts;
    private Integer acquittedCounts;
    private String legalTheory;

    // ===== EVIDENCE INFORMATION =====
    private List<String> documentaryEvidence;
    private Integer witnessCount;
    private Integer expertFindings;
    private List<String> physicalEvidence;
    private Boolean videoSurveillance;
    private Boolean phoneRecords;
    private Boolean psychologicalAssessment;

    // ===== POWER DYNAMICS =====
    private String powerDynamicsType;
    private Boolean superiorSubordinate;
    private Boolean organizationalContext;
    private String familyRelationship;
    private String stalkingContext;
    private String harassmentPattern;

    // ===== VERDICT & SENTENCING =====
    private Boolean guilty;
    private Boolean acquitted;
    private Boolean conditional;
    private String sentenceType;     // Prison/suspended/fine/probation
    private Integer sentenceDurationMonths;
    private String executionStatus;
    private String sentenceConditions;
    private String acquittalReason;

    // ===== APPEALS =====
    private Boolean appealFiled;
    private String higherCourtOutcome;
    private String effectiveDate;

    // Constructor
    public CaseDescription() {
        this.articlesCharged = new ArrayList<>();
        this.documentaryEvidence = new ArrayList<>();
        this.physicalEvidence = new ArrayList<>();
    }

    // ===== GETTERS & SETTERS =====
    
    public String getCaseId() { return caseId; }
    public void setCaseId(String caseId) { this.caseId = caseId; }

    public String getCaseNumber() { return caseNumber; }
    public void setCaseNumber(String caseNumber) { this.caseNumber = caseNumber; }

    public String getCourt() { return court; }
    public void setCourt(String court) { this.court = court; }

    public String getJudge() { return judge; }
    public void setJudge(String judge) { this.judge = judge; }

    public String getVerdictDate() { return verdictDate; }
    public void setVerdictDate(String verdictDate) { this.verdictDate = verdictDate; }

    public String getCaseType() { return caseType; }
    public void setCaseType(String caseType) { this.caseType = caseType; }

    public String getDefendantName() { return defendantName; }
    public void setDefendantName(String defendantName) { this.defendantName = defendantName; }

    public String getDefendantJMBG() { return defendantJMBG; }
    public void setDefendantJMBG(String defendantJMBG) { this.defendantJMBG = defendantJMBG; }

    public String getDefendantBirthdate() { return defendantBirthdate; }
    public void setDefendantBirthdate(String defendantBirthdate) { this.defendantBirthdate = defendantBirthdate; }

    public Integer getDefendantAge() { return defendantAge; }
    public void setDefendantAge(Integer defendantAge) { this.defendantAge = defendantAge; }

    public String getDefendantGender() { return defendantGender; }
    public void setDefendantGender(String defendantGender) { this.defendantGender = defendantGender; }

    public String getDefendantOccupation() { return defendantOccupation; }
    public void setDefendantOccupation(String defendantOccupation) { this.defendantOccupation = defendantOccupation; }

    public String getDefendantEducation() { return defendantEducation; }
    public void setDefendantEducation(String defendantEducation) { this.defendantEducation = defendantEducation; }

    public String getDefendantEmploymentStatus() { return defendantEmploymentStatus; }
    public void setDefendantEmploymentStatus(String defendantEmploymentStatus) { this.defendantEmploymentStatus = defendantEmploymentStatus; }

    public String getDefendantMaritalStatus() { return defendantMaritalStatus; }
    public void setDefendantMaritalStatus(String defendantMaritalStatus) { this.defendantMaritalStatus = defendantMaritalStatus; }

    public Integer getDefendantChildren() { return defendantChildren; }
    public void setDefendantChildren(Integer defendantChildren) { this.defendantChildren = defendantChildren; }

    public String getDefendantFinancialStatus() { return defendantFinancialStatus; }
    public void setDefendantFinancialStatus(String defendantFinancialStatus) { this.defendantFinancialStatus = defendantFinancialStatus; }

    public Integer getDefendantPriorConvictions() { return defendantPriorConvictions; }
    public void setDefendantPriorConvictions(Integer defendantPriorConvictions) { this.defendantPriorConvictions = defendantPriorConvictions; }

    public String getDefendantMentalHealth() { return defendantMentalHealth; }
    public void setDefendantMentalHealth(String defendantMentalHealth) { this.defendantMentalHealth = defendantMentalHealth; }

    public String getDefendantAddictionStatus() { return defendantAddictionStatus; }
    public void setDefendantAddictionStatus(String defendantAddictionStatus) { this.defendantAddictionStatus = defendantAddictionStatus; }

    public String getVictimName() { return victimName; }
    public void setVictimName(String victimName) { this.victimName = victimName; }

    public String getVictimStatus() { return victimStatus; }
    public void setVictimStatus(String victimStatus) { this.victimStatus = victimStatus; }

    public String getVictimRelationship() { return victimRelationship; }
    public void setVictimRelationship(String victimRelationship) { this.victimRelationship = victimRelationship; }

    public Boolean getWorkplaceRelationship() { return workplaceRelationship; }
    public void setWorkplaceRelationship(Boolean workplaceRelationship) { this.workplaceRelationship = workplaceRelationship; }

    public Integer getVictimAge() { return victimAge; }
    public void setVictimAge(Integer victimAge) { this.victimAge = victimAge; }

    public Integer getHarmPhysical() { return harmPhysical; }
    public void setHarmPhysical(Integer harmPhysical) { this.harmPhysical = harmPhysical; }

    public Integer getHarmPsychological() { return harmPsychological; }
    public void setHarmPsychological(Integer harmPsychological) { this.harmPsychological = harmPsychological; }

    public String getFamilyImpact() { return familyImpact; }
    public void setFamilyImpact(String familyImpact) { this.familyImpact = familyImpact; }

    public String getOccupationalImpact() { return occupationalImpact; }
    public void setOccupationalImpact(String occupationalImpact) { this.occupationalImpact = occupationalImpact; }

    public String getIncidentDate() { return incidentDate; }
    public void setIncidentDate(String incidentDate) { this.incidentDate = incidentDate; }

    public String getIncidentTime() { return incidentTime; }
    public void setIncidentTime(String incidentTime) { this.incidentTime = incidentTime; }

    public String getIncidentLocation() { return incidentLocation; }
    public void setIncidentLocation(String incidentLocation) { this.incidentLocation = incidentLocation; }

    public String getIncidentDuration() { return incidentDuration; }
    public void setIncidentDuration(String incidentDuration) { this.incidentDuration = incidentDuration; }

    public String getIncidentNarrative() { return incidentNarrative; }
    public void setIncidentNarrative(String incidentNarrative) { this.incidentNarrative = incidentNarrative; }

    public Boolean getWorkplaceContext() { return workplaceContext; }
    public void setWorkplaceContext(Boolean workplaceContext) { this.workplaceContext = workplaceContext; }

    public String getContextIndicator() { return contextIndicator; }
    public void setContextIndicator(String contextIndicator) { this.contextIndicator = contextIndicator; }

    public String getTemporalPattern() { return temporalPattern; }
    public void setTemporalPattern(String temporalPattern) { this.temporalPattern = temporalPattern; }

    public List<String> getArticlesCharged() { return articlesCharged; }
    public void setArticlesCharged(List<String> articlesCharged) { this.articlesCharged = articlesCharged; }

    public Integer getChargesCount() { return chargesCount; }
    public void setChargesCount(Integer chargesCount) { this.chargesCount = chargesCount; }

    public Integer getGuiltyCounts() { return guiltyCounts; }
    public void setGuiltyCounts(Integer guiltyCounts) { this.guiltyCounts = guiltyCounts; }

    public Integer getAcquittedCounts() { return acquittedCounts; }
    public void setAcquittedCounts(Integer acquittedCounts) { this.acquittedCounts = acquittedCounts; }

    public String getLegalTheory() { return legalTheory; }
    public void setLegalTheory(String legalTheory) { this.legalTheory = legalTheory; }

    public List<String> getDocumentaryEvidence() { return documentaryEvidence; }
    public void setDocumentaryEvidence(List<String> documentaryEvidence) { this.documentaryEvidence = documentaryEvidence; }

    public Integer getWitnessCount() { return witnessCount; }
    public void setWitnessCount(Integer witnessCount) { this.witnessCount = witnessCount; }

    public Integer getExpertFindings() { return expertFindings; }
    public void setExpertFindings(Integer expertFindings) { this.expertFindings = expertFindings; }

    public List<String> getPhysicalEvidence() { return physicalEvidence; }
    public void setPhysicalEvidence(List<String> physicalEvidence) { this.physicalEvidence = physicalEvidence; }

    public Boolean getVideoSurveillance() { return videoSurveillance; }
    public void setVideoSurveillance(Boolean videoSurveillance) { this.videoSurveillance = videoSurveillance; }

    public Boolean getPhoneRecords() { return phoneRecords; }
    public void setPhoneRecords(Boolean phoneRecords) { this.phoneRecords = phoneRecords; }

    public Boolean getPsychologicalAssessment() { return psychologicalAssessment; }
    public void setPsychologicalAssessment(Boolean psychologicalAssessment) { this.psychologicalAssessment = psychologicalAssessment; }

    public String getPowerDynamicsType() { return powerDynamicsType; }
    public void setPowerDynamicsType(String powerDynamicsType) { this.powerDynamicsType = powerDynamicsType; }

    public Boolean getSuperiorSubordinate() { return superiorSubordinate; }
    public void setSuperiorSubordinate(Boolean superiorSubordinate) { this.superiorSubordinate = superiorSubordinate; }

    public Boolean getOrganizationalContext() { return organizationalContext; }
    public void setOrganizationalContext(Boolean organizationalContext) { this.organizationalContext = organizationalContext; }

    public String getFamilyRelationship() { return familyRelationship; }
    public void setFamilyRelationship(String familyRelationship) { this.familyRelationship = familyRelationship; }

    public String getStalkingContext() { return stalkingContext; }
    public void setStalkingContext(String stalkingContext) { this.stalkingContext = stalkingContext; }

    public String getHarassmentPattern() { return harassmentPattern; }
    public void setHarassmentPattern(String harassmentPattern) { this.harassmentPattern = harassmentPattern; }

    public Boolean getGuilty() { return guilty; }
    public void setGuilty(Boolean guilty) { this.guilty = guilty; }

    public Boolean getAcquitted() { return acquitted; }
    public void setAcquitted(Boolean acquitted) { this.acquitted = acquitted; }

    public Boolean getConditional() { return conditional; }
    public void setConditional(Boolean conditional) { this.conditional = conditional; }

    public String getSentenceType() { return sentenceType; }
    public void setSentenceType(String sentenceType) { this.sentenceType = sentenceType; }

    public Integer getSentenceDurationMonths() { return sentenceDurationMonths; }
    public void setSentenceDurationMonths(Integer sentenceDurationMonths) { this.sentenceDurationMonths = sentenceDurationMonths; }

    public String getExecutionStatus() { return executionStatus; }
    public void setExecutionStatus(String executionStatus) { this.executionStatus = executionStatus; }

    public String getSentenceConditions() { return sentenceConditions; }
    public void setSentenceConditions(String sentenceConditions) { this.sentenceConditions = sentenceConditions; }

    public String getAcquittalReason() { return acquittalReason; }
    public void setAcquittalReason(String acquittalReason) { this.acquittalReason = acquittalReason; }

    public Boolean getAppealFiled() { return appealFiled; }
    public void setAppealFiled(Boolean appealFiled) { this.appealFiled = appealFiled; }

    public String getHigherCourtOutcome() { return higherCourtOutcome; }
    public void setHigherCourtOutcome(String higherCourtOutcome) { this.higherCourtOutcome = higherCourtOutcome; }

    public String getEffectiveDate() { return effectiveDate; }
    public void setEffectiveDate(String effectiveDate) { this.effectiveDate = effectiveDate; }

    // ===== UTILITY METHODS =====
    
    @Override
    public String toString() {
        return String.format("%s - %s: %s (%s)", caseNumber, caseType, 
            guilty ? "GUILTY" : (acquitted ? "ACQUITTED" : "CONDITIONAL"),
            court);
    }

    /**
     * Get total harm score (physical + psychological)
     */
    public Integer getTotalHarmScore() {
        int physical = harmPhysical != null ? harmPhysical : 0;
        int psychological = harmPsychological != null ? harmPsychological : 0;
        return physical + psychological;
    }

    /**
     * Get evidence quality score (based on type and quantity)
     */
    public Integer getEvidenceQualityScore() {
        int score = 0;
        if (videoSurveillance != null && videoSurveillance) score += 2;
        if (phoneRecords != null && phoneRecords) score += 2;
        if (psychologicalAssessment != null && psychologicalAssessment) score += 2;
        score += (witnessCount != null ? Math.min(witnessCount, 5) : 0);
        score += (expertFindings != null ? Math.min(expertFindings, 3) : 0);
        return Math.min(score, 20); // Cap at 20
    }

    /**
     * Check if this case involves workplace context
     */
    public Boolean isWorkplaceCase() {
        return workplaceContext != null && workplaceContext;
    }

    /**
     * Check if this case involves harassment/stalking
     */
    public Boolean isHarassmentCase() {
        String type = caseType != null ? caseType.toLowerCase() : "";
        return type.contains("stalking") || type.contains("harassment") || 
               type.contains("threat") || type.contains("mobbing");
    }
}
