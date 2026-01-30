package cbr.database;

import java.io.Serializable;
import java.util.*;

/**
 * CaseDescription - Montenegrin Legal Case Model for jCOLIBRI
 * Represents a single court verdict with AkomaNtoso 3.0 XML document hierarchy
 * 
 * Structure mirrors AkomaNtoso judgment format:
 * <judgment>
 *   <meta> (FRBR + Publication + References)
 *   <body>
 *     <chapter> (Background)
 *     <chapter> (Motivation)
 *     <chapter> (Decision)
 *   </body>
 * </judgment>
 * 
 * Each element can nest chapters -> sections -> articles -> paragraphs -> points
 * With eId identifiers for cross-referencing
 */
public class CaseDescription implements Serializable {
    private static final long serialVersionUID = 1L;

    private JudgmentMetadata metadata;
    private List<AkomaNtosoElement> bodyElements; // Chapters in judgment body
    
    // For backward compatibility with old flat API
    private JudgmentBackground background;
    private JudgmentMotivation motivation;
    private JudgmentDecision decision;

    public CaseDescription() {
        this.metadata = new JudgmentMetadata();
        this.bodyElements = new ArrayList<>();
        this.background = new JudgmentBackground();
        this.motivation = new JudgmentMotivation();
        this.decision = new JudgmentDecision();
    }

    public JudgmentMetadata getMetadata() { return metadata; }
    public void setMetadata(JudgmentMetadata metadata) { this.metadata = metadata; }

    public List<AkomaNtosoElement> getBodyElements() { return bodyElements; }
    public void setBodyElements(List<AkomaNtosoElement> elements) { this.bodyElements = elements; }

    public void addChapter(Chapter chapter) { this.bodyElements.add(chapter); }

    // Convenience helpers for backward compatibility with old flat API
    public Chapter addBackgroundChapter() {
        Chapter bg = new Chapter("chp_1", "I. Background");
        addChapter(bg);
        return bg;
    }

    public Chapter addMotivationChapter() {
        Chapter mot = new Chapter("chp_2", "II. Motivation");
        addChapter(mot);
        return mot;
    }

    public Chapter addDecisionChapter() {
        Chapter dec = new Chapter("chp_3", "III. Decision");
        addChapter(dec);
        return dec;
    }

    // ===== UTILITY METHODS =====

    @Override
    public String toString() {
        String number = metadata.getFrbrWork().getCaseNumber();
        String caseType = metadata.getPublication().getCaseType();
        String verdict = getDecision().getGuilty() ? "GUILTY" : 
                        (getDecision().getAcquitted() ? "ACQUITTED" : "CONDITIONAL");
        String court = metadata.getPublication().getCourt();
        return String.format("%s - %s: %s (%s)", number, caseType, verdict, court);
    }

    public Integer getTotalHarmScore() {
        Integer physical = background.getVictim().getHarmPhysical();
        Integer psychological = background.getVictim().getHarmPsychological();
        return (physical != null ? physical : 0) + (psychological != null ? psychological : 0);
    }

    public Integer getEvidenceQualityScore() {
        int score = 0;
        if (motivation.getVideoSurveillance() != null && motivation.getVideoSurveillance()) score += 2;
        if (motivation.getPhoneRecords() != null && motivation.getPhoneRecords()) score += 2;
        if (motivation.getPsychologicalAssessment() != null && motivation.getPsychologicalAssessment()) score += 2;
        score += (motivation.getWitnessCount() != null ? Math.min(motivation.getWitnessCount(), 5) : 0);
        score += (motivation.getExpertFindings() != null ? Math.min(motivation.getExpertFindings(), 3) : 0);
        return Math.min(score, 20);
    }

    public Boolean isWorkplaceCase() {
        return background.getFacts().getWorkplaceContext() != null && 
               background.getFacts().getWorkplaceContext();
    }

    public Boolean isHarassmentCase() {
        String type = metadata.getPublication().getCaseType();
        if (type == null) return false;
        String lower = type.toLowerCase();
        return lower.contains("stalking") || lower.contains("harassment") || 
               lower.contains("threat") || lower.contains("mobbing");
    }

    // ===== CONVENIENCE GETTERS FOR BACKWARD COMPATIBILITY =====

    public JudgmentBackground getBackground() { return background; }
    public void setBackground(JudgmentBackground background) { this.background = background; }

    public JudgmentMotivation getMotivation() { return motivation; }
    public void setMotivation(JudgmentMotivation motivation) { this.motivation = motivation; }

    public JudgmentDecision getDecision() { return decision; }
    public void setDecision(JudgmentDecision decision) { this.decision = decision; }

    // ===== CONVENIENCE GETTERS FOR BACKWARD COMPATIBILITY =====
    
    // From metadata.FRBRWork
    public String getCaseId() { return metadata.getFrbrWork().getCaseId(); }
    public void setCaseId(String caseId) { metadata.getFrbrWork().setCaseId(caseId); }

    public String getCaseNumber() { return metadata.getFrbrWork().getCaseNumber(); }
    public void setCaseNumber(String caseNumber) { metadata.getFrbrWork().setCaseNumber(caseNumber); }

    public String getVerdictDate() { return metadata.getFrbrWork().getVerdictDate(); }
    public void setVerdictDate(String verdictDate) { metadata.getFrbrWork().setVerdictDate(verdictDate); }

    // From metadata.publication
    public String getCourt() { return metadata.getPublication().getCourt(); }
    public void setCourt(String court) { metadata.getPublication().setCourt(court); }

    public String getCaseType() { return metadata.getPublication().getCaseType(); }
    public void setCaseType(String caseType) { metadata.getPublication().setCaseType(caseType); }

    // From metadata.references
    public String getJudge() { return metadata.getReferences().getJudgeName(); }
    public void setJudge(String judge) { metadata.getReferences().setJudgeName(judge); }

    // From background.defendant
    public String getDefendantName() { return background.getDefendant().getName(); }
    public void setDefendantName(String name) { background.getDefendant().setName(name); }

    public String getDefendantJMBG() { return background.getDefendant().getJmbg(); }
    public void setDefendantJMBG(String jmbg) { background.getDefendant().setJmbg(jmbg); }

    public String getDefendantBirthdate() { return background.getDefendant().getBirthdate(); }
    public void setDefendantBirthdate(String birthdate) { background.getDefendant().setBirthdate(birthdate); }

    public Integer getDefendantAge() { return background.getDefendant().getAge(); }
    public void setDefendantAge(Integer age) { background.getDefendant().setAge(age); }

    public String getDefendantGender() { return background.getDefendant().getGender(); }
    public void setDefendantGender(String gender) { background.getDefendant().setGender(gender); }

    public String getDefendantOccupation() { return background.getDefendant().getOccupation(); }
    public void setDefendantOccupation(String occupation) { background.getDefendant().setOccupation(occupation); }

    public String getDefendantEducation() { return background.getDefendant().getEducation(); }
    public void setDefendantEducation(String education) { background.getDefendant().setEducation(education); }

    public String getDefendantEmploymentStatus() { return background.getDefendant().getEmploymentStatus(); }
    public void setDefendantEmploymentStatus(String status) { background.getDefendant().setEmploymentStatus(status); }

    public String getDefendantMaritalStatus() { return background.getDefendant().getMaritalStatus(); }
    public void setDefendantMaritalStatus(String status) { background.getDefendant().setMaritalStatus(status); }

    public Integer getDefendantChildren() { return background.getDefendant().getChildren(); }
    public void setDefendantChildren(Integer children) { background.getDefendant().setChildren(children); }

    public String getDefendantFinancialStatus() { return background.getDefendant().getFinancialStatus(); }
    public void setDefendantFinancialStatus(String status) { background.getDefendant().setFinancialStatus(status); }

    public Integer getDefendantPriorConvictions() { return background.getDefendant().getPriorConvictions(); }
    public void setDefendantPriorConvictions(Integer count) { background.getDefendant().setPriorConvictions(count); }

    public String getDefendantMentalHealth() { return background.getDefendant().getMentalHealth(); }
    public void setDefendantMentalHealth(String status) { background.getDefendant().setMentalHealth(status); }

    public String getDefendantAddictionStatus() { return background.getDefendant().getAddictionStatus(); }
    public void setDefendantAddictionStatus(String status) { background.getDefendant().setAddictionStatus(status); }

    // From background.victim
    public String getVictimName() { return background.getVictim().getName(); }
    public void setVictimName(String name) { background.getVictim().setName(name); }

    public String getVictimStatus() { return background.getVictim().getStatus(); }
    public void setVictimStatus(String status) { background.getVictim().setStatus(status); }

    public String getVictimRelationship() { return background.getVictim().getRelationshipToDefendant(); }
    public void setVictimRelationship(String relationship) { background.getVictim().setRelationshipToDefendant(relationship); }

    public Boolean getWorkplaceRelationship() { return background.getVictim().getWorkplaceRelationship(); }
    public void setWorkplaceRelationship(Boolean workplace) { background.getVictim().setWorkplaceRelationship(workplace); }

    public Integer getVictimAge() { return background.getVictim().getAge(); }
    public void setVictimAge(Integer age) { background.getVictim().setAge(age); }

    public Integer getHarmPhysical() { return background.getVictim().getHarmPhysical(); }
    public void setHarmPhysical(Integer harm) { background.getVictim().setHarmPhysical(harm); }

    public Integer getHarmPsychological() { return background.getVictim().getHarmPsychological(); }
    public void setHarmPsychological(Integer harm) { background.getVictim().setHarmPsychological(harm); }

    public String getFamilyImpact() { return background.getVictim().getFamilyImpact(); }
    public void setFamilyImpact(String impact) { background.getVictim().setFamilyImpact(impact); }

    public String getOccupationalImpact() { return background.getVictim().getOccupationalImpact(); }
    public void setOccupationalImpact(String impact) { background.getVictim().setOccupationalImpact(impact); }

    // From background.facts
    public String getIncidentDate() { return background.getFacts().getDate(); }
    public void setIncidentDate(String date) { background.getFacts().setDate(date); }

    public String getIncidentTime() { return background.getFacts().getTime(); }
    public void setIncidentTime(String time) { background.getFacts().setTime(time); }

    public String getIncidentLocation() { return background.getFacts().getLocation(); }
    public void setIncidentLocation(String location) { background.getFacts().setLocation(location); }

    public String getIncidentDuration() { return background.getFacts().getDuration(); }
    public void setIncidentDuration(String duration) { background.getFacts().setDuration(duration); }

    public String getIncidentNarrative() { return background.getFacts().getNarrative(); }
    public void setIncidentNarrative(String narrative) { background.getFacts().setNarrative(narrative); }

    public Boolean getWorkplaceContext() { return background.getFacts().getWorkplaceContext(); }
    public void setWorkplaceContext(Boolean context) { background.getFacts().setWorkplaceContext(context); }

    public String getContextIndicator() { return background.getFacts().getContextIndicator(); }
    public void setContextIndicator(String indicator) { background.getFacts().setContextIndicator(indicator); }

    public String getTemporalPattern() { return background.getFacts().getTemporalPattern(); }
    public void setTemporalPattern(String pattern) { background.getFacts().setTemporalPattern(pattern); }

    // From motivation
    public List<String> getArticlesCharged() { return motivation.getArticlesCharged(); }
    public void setArticlesCharged(List<String> articles) { motivation.setArticlesCharged(articles); }

    public Integer getChargesCount() { return motivation.getChargesCount(); }
    public void setChargesCount(Integer count) { motivation.setChargesCount(count); }

    public String getLegalTheory() { return motivation.getLegalTheory(); }
    public void setLegalTheory(String theory) { motivation.setLegalTheory(theory); }

    public List<String> getDocumentaryEvidence() { return motivation.getDocumentaryEvidence(); }
    public void setDocumentaryEvidence(List<String> evidence) { motivation.setDocumentaryEvidence(evidence); }

    public Integer getWitnessCount() { return motivation.getWitnessCount(); }
    public void setWitnessCount(Integer count) { motivation.setWitnessCount(count); }

    public Integer getExpertFindings() { return motivation.getExpertFindings(); }
    public void setExpertFindings(Integer findings) { motivation.setExpertFindings(findings); }

    public List<String> getPhysicalEvidence() { return motivation.getPhysicalEvidence(); }
    public void setPhysicalEvidence(List<String> evidence) { motivation.setPhysicalEvidence(evidence); }

    public Boolean getVideoSurveillance() { return motivation.getVideoSurveillance(); }
    public void setVideoSurveillance(Boolean video) { motivation.setVideoSurveillance(video); }

    public Boolean getPhoneRecords() { return motivation.getPhoneRecords(); }
    public void setPhoneRecords(Boolean records) { motivation.setPhoneRecords(records); }

    public Boolean getPsychologicalAssessment() { return motivation.getPsychologicalAssessment(); }
    public void setPsychologicalAssessment(Boolean assessment) { motivation.setPsychologicalAssessment(assessment); }

    public String getPowerDynamicsType() { return background.getPowerDynamicsType(); }
    public void setPowerDynamicsType(String type) { background.setPowerDynamicsType(type); }

    public Boolean getSuperiorSubordinate() { return background.getSuperiorSubordinate(); }
    public void setSuperiorSubordinate(Boolean superior) { background.setSuperiorSubordinate(superior); }

    public Boolean getOrganizationalContext() { return background.getOrganizationalContext(); }
    public void setOrganizationalContext(Boolean org) { background.setOrganizationalContext(org); }

    public String getFamilyRelationship() { return background.getFamilyRelationship(); }
    public void setFamilyRelationship(String relationship) { background.setFamilyRelationship(relationship); }

    public String getStalkingContext() { return background.getStalkingContext(); }
    public void setStalkingContext(String context) { background.setStalkingContext(context); }

    public String getHarassmentPattern() { return background.getHarassmentPattern(); }
    public void setHarassmentPattern(String pattern) { background.setHarassmentPattern(pattern); }

    // From decision
    public Boolean getGuilty() { return decision.getGuilty(); }
    public void setGuilty(Boolean guilty) { decision.setGuilty(guilty); }

    public Boolean getAcquitted() { return decision.getAcquitted(); }
    public void setAcquitted(Boolean acquitted) { decision.setAcquitted(acquitted); }

    public Boolean getConditional() { return decision.getConditional(); }
    public void setConditional(Boolean conditional) { decision.setConditional(conditional); }

    public String getSentenceType() { return decision.getSentenceType(); }
    public void setSentenceType(String type) { decision.setSentenceType(type); }

    public Integer getSentenceDurationMonths() { return decision.getSentenceDurationMonths(); }
    public void setSentenceDurationMonths(Integer months) { decision.setSentenceDurationMonths(months); }

    public String getExecutionStatus() { return decision.getExecutionStatus(); }
    public void setExecutionStatus(String status) { decision.setExecutionStatus(status); }

    public String getSentenceConditions() { return decision.getSentenceConditions(); }
    public void setSentenceConditions(String conditions) { decision.setSentenceConditions(conditions); }

    public String getAcquittalReason() { return decision.getAcquittalReason(); }
    public void setAcquittalReason(String reason) { decision.setAcquittalReason(reason); }

    public Boolean getAppealFiled() { return decision.getAppealFiled(); }
    public void setAppealFiled(Boolean appeal) { decision.setAppealFiled(appeal); }

    public String getHigherCourtOutcome() { return decision.getHigherCourtOutcome(); }
    public void setHigherCourtOutcome(String outcome) { decision.setHigherCourtOutcome(outcome); }

    public String getEffectiveDate() { return decision.getEffectiveDate(); }
    public void setEffectiveDate(String date) { decision.setEffectiveDate(date); }

    public Integer getGuiltyCounts() { return motivation.getGuiltyCounts(); }
    public void setGuiltyCounts(Integer count) { motivation.setGuiltyCounts(count); }

    public Integer getAcquittedCounts() { return motivation.getAcquittedCounts(); }
    public void setAcquittedCounts(Integer count) { motivation.setAcquittedCounts(count); }



    // ===== UTILITY METHODS =====
    
    @Override
    public String toString() {
        return String.format("%s - %s: %s (%s)", 
            getCaseNumber(), getCaseType(), 
            getGuilty() ? "GUILTY" : (getAcquitted() ? "ACQUITTED" : "CONDITIONAL"),
            getCourt());
    }

    /**
     * Get total harm score (physical + psychological)
     */
    public Integer getTotalHarmScore() {
        int physical = getHarmPhysical() != null ? getHarmPhysical() : 0;
        int psychological = getHarmPsychological() != null ? getHarmPsychological() : 0;
        return physical + psychological;
    }

    /**
     * Get evidence quality score (based on type and quantity)
     */
    public Integer getEvidenceQualityScore() {
        int score = 0;
        if (getVideoSurveillance() != null && getVideoSurveillance()) score += 2;
        if (getPhoneRecords() != null && getPhoneRecords()) score += 2;
        if (getPsychologicalAssessment() != null && getPsychologicalAssessment()) score += 2;
        score += (getWitnessCount() != null ? Math.min(getWitnessCount(), 5) : 0);
        score += (getExpertFindings() != null ? Math.min(getExpertFindings(), 3) : 0);
        return Math.min(score, 20); // Cap at 20
    }

    /**
     * Check if this case involves workplace context
     */
    public Boolean isWorkplaceCase() {
        return getWorkplaceContext() != null && getWorkplaceContext();
    }

    /**
     * Check if this case involves harassment/stalking
     */
    public Boolean isHarassmentCase() {
        String type = getCaseType() != null ? getCaseType().toLowerCase() : "";
        return type.contains("stalking") || type.contains("harassment") || 
               type.contains("threat") || type.contains("mobbing");
    }

    // ===== INNER CLASSES FOR AKOMANTOSO STRUCTURE =====

    /**
     * JudgmentMetadata - Corresponds to <meta> section in AkomaNtoso
     * Contains FRBR, publication, classification, and references
     */
    public static class JudgmentMetadata implements Serializable {
        private FRBRWork frbrWork;
        private FRBRExpression frbrExpression;
        private FRBRManifestation frbrManifestation;
        private PublicationInfo publication;
        private MetadataReferences references;

        public JudgmentMetadata() {
            this.frbrWork = new FRBRWork();
            this.frbrExpression = new FRBRExpression();
            this.frbrManifestation = new FRBRManifestation();
            this.publication = new PublicationInfo();
            this.references = new MetadataReferences();
        }

        public FRBRWork getFrbrWork() { return frbrWork; }
        public FRBRExpression getFrbrExpression() { return frbrExpression; }
        public FRBRManifestation getFrbrManifestation() { return frbrManifestation; }
        public PublicationInfo getPublication() { return publication; }
        public MetadataReferences getReferences() { return references; }

        public void setFrbrWork(FRBRWork work) { this.frbrWork = work; }
        public void setFrbrExpression(FRBRExpression expr) { this.frbrExpression = expr; }
        public void setFrbrManifestation(FRBRManifestation manif) { this.frbrManifestation = manif; }
        public void setPublication(PublicationInfo pub) { this.publication = pub; }
        public void setReferences(MetadataReferences refs) { this.references = refs; }
    }

    /**
     * FRBRWork - Abstract document (FRBR Level 1)
     * Represents the intellectual work
     */
    public static class FRBRWork implements Serializable {
        private String caseId;           // e.g., Case_001
        private String caseNumber;       // e.g., K 217/24
        private String verdictDate;      // e.g., 2024
        private String country;          // e.g., "me" for Montenegro
        private String name;             // Document title

        public FRBRWork() {}

        public String getCaseId() { return caseId; }
        public void setCaseId(String caseId) { this.caseId = caseId; }

        public String getCaseNumber() { return caseNumber; }
        public void setCaseNumber(String caseNumber) { this.caseNumber = caseNumber; }

        public String getVerdictDate() { return verdictDate; }
        public void setVerdictDate(String date) { this.verdictDate = date; }

        public String getCountry() { return country; }
        public void setCountry(String country) { this.country = country; }

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
    }

    /**
     * FRBRExpression - Specific version (FRBR Level 2)
     * Represents a specific expression/version of the work
     */
    public static class FRBRExpression implements Serializable {
        private String language;         // e.g., "sr" for Serbian
        private String versionDate;      // Amendment date
        private String editor;           // Who edited this version

        public FRBRExpression() { this.language = "sr"; }

        public String getLanguage() { return language; }
        public void setLanguage(String language) { this.language = language; }

        public String getVersionDate() { return versionDate; }
        public void setVersionDate(String date) { this.versionDate = date; }

        public String getEditor() { return editor; }
        public void setEditor(String editor) { this.editor = editor; }
    }

    /**
     * FRBRManifestation - Physical format (FRBR Level 3)
     * Represents the physical manifestation/file format
     */
    public static class FRBRManifestation implements Serializable {
        private String format;           // e.g., "xml"
        private String creationDate;     // When file was created
        private String generator;        // Tool that generated it

        public FRBRManifestation() { this.format = "xml"; }

        public String getFormat() { return format; }
        public void setFormat(String format) { this.format = format; }

        public String getCreationDate() { return creationDate; }
        public void setCreationDate(String date) { this.creationDate = date; }

        public String getGenerator() { return generator; }
        public void setGenerator(String generator) { this.generator = generator; }
    }

    /**
     * PublicationInfo - Publication metadata
     */
    public static class PublicationInfo implements Serializable {
        private String court;            // Court name
        private String caseType;         // Case type/classification
        private String publicationDate;  // When published
        private String publicationNumber; // Publication number/gazette

        public PublicationInfo() {}

        public String getCourt() { return court; }
        public void setCourt(String court) { this.court = court; }

        public String getCaseType() { return caseType; }
        public void setCaseType(String type) { this.caseType = type; }

        public String getPublicationDate() { return publicationDate; }
        public void setPublicationDate(String date) { this.publicationDate = date; }

        public String getPublicationNumber() { return publicationNumber; }
        public void setPublicationNumber(String number) { this.publicationNumber = number; }
    }

    /**
     * MetadataReferences - External references, roles, organizations, persons
     */
    public static class MetadataReferences implements Serializable {
        private String judgeName;        // Judge name
        private List<String> rolesReferenced;    // Author, Editor, Generator
        private List<String> organizationsReferenced;  // Court, Parliament, etc
        private List<String> personNamesReferenced;    // People mentioned

        public MetadataReferences() {
            this.rolesReferenced = new ArrayList<>();
            this.organizationsReferenced = new ArrayList<>();
            this.personNamesReferenced = new ArrayList<>();
        }

        public String getJudgeName() { return judgeName; }
        public void setJudgeName(String name) { this.judgeName = name; }

        public List<String> getRolesReferenced() { return rolesReferenced; }
        public List<String> getOrganizationsReferenced() { return organizationsReferenced; }
        public List<String> getPersonNamesReferenced() { return personNamesReferenced; }

        public void addRole(String role) { this.rolesReferenced.add(role); }
        public void addOrganization(String org) { this.organizationsReferenced.add(org); }
        public void addPerson(String person) { this.personNamesReferenced.add(person); }
    }

    /**
     * JudgmentBackground - Corresponds to <background> section
     * Contains parties (defendant, victim, judge) and facts
     */
    public static class JudgmentBackground implements Serializable {
        private Party defendant;
        private Party victim;
        private IncidentFacts facts;
        private String powerDynamicsType;
        private Boolean superiorSubordinate;
        private Boolean organizationalContext;
        private String familyRelationship;
        private String stalkingContext;
        private String harassmentPattern;

        public JudgmentBackground() {
            this.defendant = new Party("defendant");
            this.victim = new Party("victim");
            this.facts = new IncidentFacts();
        }

        public Party getDefendant() { return defendant; }
        public Party getVictim() { return victim; }
        public IncidentFacts getFacts() { return facts; }

        public String getPowerDynamicsType() { return powerDynamicsType; }
        public void setPowerDynamicsType(String type) { this.powerDynamicsType = type; }

        public Boolean getSuperiorSubordinate() { return superiorSubordinate; }
        public void setSuperiorSubordinate(Boolean superior) { this.superiorSubordinate = superior; }

        public Boolean getOrganizationalContext() { return organizationalContext; }
        public void setOrganizationalContext(Boolean org) { this.organizationalContext = org; }

        public String getFamilyRelationship() { return familyRelationship; }
        public void setFamilyRelationship(String rel) { this.familyRelationship = rel; }

        public String getStalkingContext() { return stalkingContext; }
        public void setStalkingContext(String context) { this.stalkingContext = context; }

        public String getHarassmentPattern() { return harassmentPattern; }
        public void setHarassmentPattern(String pattern) { this.harassmentPattern = pattern; }
    }

    /**
     * Party - Person involved in judgment (defendant, victim, judge, etc.)
     */
    public static class Party implements Serializable {
        private String eId;              // Element ID (e.g., "party_defendant")
        private String role;             // defendant, victim, judge, prosecutor
        private String name;
        private String jmbg;             // National ID
        private String birthdate;
        private Integer age;
        private String gender;           // M/F
        private String occupation;
        private String education;
        private String employmentStatus;
        private String maritalStatus;
        private Integer children;
        private String financialStatus;
        private Integer priorConvictions;
        private String mentalHealth;
        private String addictionStatus;
        // Victim-specific
        private String status;           // Role (employee, employer, family, etc.)
        private String relationshipToDefendant;
        private Boolean workplaceRelationship;
        private Integer harmPhysical;    // 0-5 scale
        private Integer harmPsychological; // 0-5 scale
        private String familyImpact;
        private String occupationalImpact;

        public Party() {}
        public Party(String role) { this.role = role; }

        public String getEId() { return eId; }
        public void setEId(String eId) { this.eId = eId; }

        public String getRole() { return role; }
        public void setRole(String role) { this.role = role; }

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }

        public String getJmbg() { return jmbg; }
        public void setJmbg(String jmbg) { this.jmbg = jmbg; }

        public String getBirthdate() { return birthdate; }
        public void setBirthdate(String birthdate) { this.birthdate = birthdate; }

        public Integer getAge() { return age; }
        public void setAge(Integer age) { this.age = age; }

        public String getGender() { return gender; }
        public void setGender(String gender) { this.gender = gender; }

        public String getOccupation() { return occupation; }
        public void setOccupation(String occupation) { this.occupation = occupation; }

        public String getEducation() { return education; }
        public void setEducation(String education) { this.education = education; }

        public String getEmploymentStatus() { return employmentStatus; }
        public void setEmploymentStatus(String status) { this.employmentStatus = status; }

        public String getMaritalStatus() { return maritalStatus; }
        public void setMaritalStatus(String status) { this.maritalStatus = status; }

        public Integer getChildren() { return children; }
        public void setChildren(Integer children) { this.children = children; }

        public String getFinancialStatus() { return financialStatus; }
        public void setFinancialStatus(String status) { this.financialStatus = status; }

        public Integer getPriorConvictions() { return priorConvictions; }
        public void setPriorConvictions(Integer count) { this.priorConvictions = count; }

        public String getMentalHealth() { return mentalHealth; }
        public void setMentalHealth(String status) { this.mentalHealth = status; }

        public String getAddictionStatus() { return addictionStatus; }
        public void setAddictionStatus(String status) { this.addictionStatus = status; }

        // Victim-specific getters/setters
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }

        public String getRelationshipToDefendant() { return relationshipToDefendant; }
        public void setRelationshipToDefendant(String relationship) { this.relationshipToDefendant = relationship; }

        public Boolean getWorkplaceRelationship() { return workplaceRelationship; }
        public void setWorkplaceRelationship(Boolean workplace) { this.workplaceRelationship = workplace; }

        public Integer getHarmPhysical() { return harmPhysical; }
        public void setHarmPhysical(Integer harm) { this.harmPhysical = harm; }

        public Integer getHarmPsychological() { return harmPsychological; }
        public void setHarmPsychological(Integer harm) { this.harmPsychological = harm; }

        public String getFamilyImpact() { return familyImpact; }
        public void setFamilyImpact(String impact) { this.familyImpact = impact; }

        public String getOccupationalImpact() { return occupationalImpact; }
        public void setOccupationalImpact(String impact) { this.occupationalImpact = impact; }
    }

    /**
     * IncidentFacts - Facts of the case
     */
    public static class IncidentFacts implements Serializable {
        private String date;
        private String time;
        private String location;
        private String duration;
        private String narrative;
        private Boolean workplaceContext;
        private String contextIndicator;
        private String temporalPattern;

        public IncidentFacts() {}

        public String getDate() { return date; }
        public void setDate(String date) { this.date = date; }

        public String getTime() { return time; }
        public void setTime(String time) { this.time = time; }

        public String getLocation() { return location; }
        public void setLocation(String location) { this.location = location; }

        public String getDuration() { return duration; }
        public void setDuration(String duration) { this.duration = duration; }

        public String getNarrative() { return narrative; }
        public void setNarrative(String narrative) { this.narrative = narrative; }

        public Boolean getWorkplaceContext() { return workplaceContext; }
        public void setWorkplaceContext(Boolean context) { this.workplaceContext = context; }

        public String getContextIndicator() { return contextIndicator; }
        public void setContextIndicator(String indicator) { this.contextIndicator = indicator; }

        public String getTemporalPattern() { return temporalPattern; }
        public void setTemporalPattern(String pattern) { this.temporalPattern = pattern; }
    }

    /**
     * JudgmentMotivation - Corresponds to <motivation> section
     * Contains legal reasoning and evidence analysis
     */
    public static class JudgmentMotivation implements Serializable {
        private List<String> articlesCharged;
        private Integer chargesCount;
        private Integer guiltyCounts;
        private Integer acquittedCounts;
        private String legalTheory;
        private List<String> documentaryEvidence;
        private Integer witnessCount;
        private Integer expertFindings;
        private List<String> physicalEvidence;
        private Boolean videoSurveillance;
        private Boolean phoneRecords;
        private Boolean psychologicalAssessment;

        public JudgmentMotivation() {
            this.articlesCharged = new ArrayList<>();
            this.documentaryEvidence = new ArrayList<>();
            this.physicalEvidence = new ArrayList<>();
        }

        public List<String> getArticlesCharged() { return articlesCharged; }
        public void setArticlesCharged(List<String> articles) { this.articlesCharged = articles; }

        public Integer getChargesCount() { return chargesCount; }
        public void setChargesCount(Integer count) { this.chargesCount = count; }

        public Integer getGuiltyCounts() { return guiltyCounts; }
        public void setGuiltyCounts(Integer count) { this.guiltyCounts = count; }

        public Integer getAcquittedCounts() { return acquittedCounts; }
        public void setAcquittedCounts(Integer count) { this.acquittedCounts = count; }

        public String getLegalTheory() { return legalTheory; }
        public void setLegalTheory(String theory) { this.legalTheory = theory; }

        public List<String> getDocumentaryEvidence() { return documentaryEvidence; }
        public void setDocumentaryEvidence(List<String> evidence) { this.documentaryEvidence = evidence; }

        public Integer getWitnessCount() { return witnessCount; }
        public void setWitnessCount(Integer count) { this.witnessCount = count; }

        public Integer getExpertFindings() { return expertFindings; }
        public void setExpertFindings(Integer findings) { this.expertFindings = findings; }

        public List<String> getPhysicalEvidence() { return physicalEvidence; }
        public void setPhysicalEvidence(List<String> evidence) { this.physicalEvidence = evidence; }

        public Boolean getVideoSurveillance() { return videoSurveillance; }
        public void setVideoSurveillance(Boolean video) { this.videoSurveillance = video; }

        public Boolean getPhoneRecords() { return phoneRecords; }
        public void setPhoneRecords(Boolean records) { this.phoneRecords = records; }

        public Boolean getPsychologicalAssessment() { return psychologicalAssessment; }
        public void setPsychologicalAssessment(Boolean assessment) { this.psychologicalAssessment = assessment; }
    }

    /**
     * JudgmentDecision - Corresponds to <decision> section
     * Contains verdict and sentencing information
     */
    public static class JudgmentDecision implements Serializable {
        private Boolean guilty;
        private Boolean acquitted;
        private Boolean conditional;
        private String sentenceType;
        private Integer sentenceDurationMonths;
        private String executionStatus;
        private String sentenceConditions;
        private String acquittalReason;
        private Boolean appealFiled;
        private String higherCourtOutcome;
        private String effectiveDate;

        public JudgmentDecision() {}

        public Boolean getGuilty() { return guilty; }
        public void setGuilty(Boolean guilty) { this.guilty = guilty; }

        public Boolean getAcquitted() { return acquitted; }
        public void setAcquitted(Boolean acquitted) { this.acquitted = acquitted; }

        public Boolean getConditional() { return conditional; }
        public void setConditional(Boolean conditional) { this.conditional = conditional; }

        public String getSentenceType() { return sentenceType; }
        public void setSentenceType(String type) { this.sentenceType = type; }

        public Integer getSentenceDurationMonths() { return sentenceDurationMonths; }
        public void setSentenceDurationMonths(Integer months) { this.sentenceDurationMonths = months; }

        public String getExecutionStatus() { return executionStatus; }
        public void setExecutionStatus(String status) { this.executionStatus = status; }

        public String getSentenceConditions() { return sentenceConditions; }
        public void setSentenceConditions(String conditions) { this.sentenceConditions = conditions; }

        public String getAcquittalReason() { return acquittalReason; }
        public void setAcquittalReason(String reason) { this.acquittalReason = reason; }

        public Boolean getAppealFiled() { return appealFiled; }
        public void setAppealFiled(Boolean appeal) { this.appealFiled = appeal; }

        public String getHigherCourtOutcome() { return higherCourtOutcome; }
        public void setHigherCourtOutcome(String outcome) { this.higherCourtOutcome = outcome; }

        public String getEffectiveDate() { return effectiveDate; }
        public void setEffectiveDate(String date) { this.effectiveDate = date; }
    }

    // ===== AKOMANTOSO DOCUMENT HIERARCHY =====

    /**
     * AkomaNtosoElement - Base class for all AkomaNtoso document elements
     * Represents hierarchical structure: Chapter -> Section -> Article -> Paragraph -> Point
     */
    public static abstract class AkomaNtosoElement implements Serializable {
        protected String eId;           // Element identifier (e.g., "chp_1", "art_88")
        protected String heading;       // Display heading
        protected List<AkomaNtosoElement> children; // Nested elements

        public AkomaNtosoElement(String eId, String heading) {
            this.eId = eId;
            this.heading = heading;
            this.children = new ArrayList<>();
        }

        public String getEId() { return eId; }
        public void setEId(String eId) { this.eId = eId; }

        public String getHeading() { return heading; }
        public void setHeading(String heading) { this.heading = heading; }

        public List<AkomaNtosoElement> getChildren() { return children; }
        public void addChild(AkomaNtosoElement child) { this.children.add(child); }

        public abstract String getElementType(); // "chapter", "section", "article", etc.
    }

    /**
     * Chapter - Level 1 document element
     * Example eId: "chp_1", "chp_4" 
     */
    public static class Chapter extends AkomaNtosoElement {
        public Chapter(String eId, String heading) {
            super(eId, heading);
        }
        @Override
        public String getElementType() { return "chapter"; }
    }

    /**
     * Section - Level 2 document element (nested in Chapter)
     * Example eId: "chp_4__sec_20"
     */
    public static class Section extends AkomaNtosoElement {
        public Section(String eId, String heading) {
            super(eId, heading);
        }
        @Override
        public String getElementType() { return "section"; }
    }

    /**
     * Article - Level 3 document element (nested in Section)
     * Example eId: "art_88"
     */
    public static class Article extends AkomaNtosoElement {
        private String articleNumber;  // "Члан 88", "Члан 332"

        public Article(String eId, String heading) {
            super(eId, heading);
        }

        public String getArticleNumber() { return articleNumber; }
        public void setArticleNumber(String number) { this.articleNumber = number; }

        @Override
        public String getElementType() { return "article"; }
    }

    /**
     * Paragraph - Level 4 document element (nested in Article)
     * Example eId: "art_88__para_1", "art_88__para_2"
     */
    public static class Paragraph extends AkomaNtosoElement {
        private String content;        // Text content of paragraph

        public Paragraph(String eId) {
            super(eId, null);
        }

        public String getContent() { return content; }
        public void setContent(String content) { this.content = content; }

        @Override
        public String getElementType() { return "paragraph"; }
    }

    /**
     * Point - Level 5 document element (nested in Paragraph, for list items)
     * Example eId: "art_332__para_1__point_34"
     */
    public static class Point extends AkomaNtosoElement {
        private String pointNumber;    // "34)", "1)"
        private String content;        // Text content

        public Point(String eId) {
            super(eId, null);
        }

        public String getPointNumber() { return pointNumber; }
        public void setPointNumber(String number) { this.pointNumber = number; }

        public String getContent() { return content; }
        public void setContent(String content) { this.content = content; }

        @Override
        public String getElementType() { return "point"; }
    }

    /**
     * Reference - Represents cross-reference to another element
     * Example: <ref href="#art_88">Article 88</ref>
     */
    public static class Reference implements Serializable {
        private String href;           // Target element ID
        private String displayText;    // Display text

        public Reference(String href, String displayText) {
            this.href = href;
            this.displayText = displayText;
        }

        public String getHref() { return href; }
        public void setHref(String href) { this.href = href; }

        public String getDisplayText() { return displayText; }
        public void setDisplayText(String text) { this.displayText = text; }
    }
}

