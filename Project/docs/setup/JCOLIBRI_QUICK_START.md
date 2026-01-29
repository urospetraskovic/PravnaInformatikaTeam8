# jCOLIBRI Integration Quick Start Guide

## Project Status: READY FOR CBR SYSTEM INTEGRATION ✓

**Date:** January 29, 2026  
**Completion:** Extraction phase 100% complete  
**Next Phase:** jCOLIBRI database population

---

## Files Ready for Import

### 1. EXTRACTED_CASES_DATABASE.csv
- **Location:** Project root directory
- **Format:** Comma-separated values (UTF-8)
- **Size:** 4,511 bytes
- **Rows:** 13 (header + 12 main verdicts + 1 retrial)
- **Columns:** 25 structured fields
- **Purpose:** Direct import into jCOLIBRI CaseDescription.java

**Column Reference:**
```
case_id, case_number, court, judge, verdict_date, case_type,
defendant_name, defendant_age, defendant_occupation, defendant_education, defendant_convictions,
victim_name, victim_status, victim_age,
incident_date, incident_location, incident_type,
articles_charged,
verdict_guilty, verdict_conditional, sentence_months,
harm_physical, harm_psychological, witness_count, expert_count
```

### 2. EXTRACTED_CASES_DATABASE.json
- **Location:** Project root directory
- **Format:** JSON (UTF-8, pretty-printed)
- **Size:** 33,031 bytes
- **Records:** 13 complete case objects
- **Purpose:** Full structured database with nested fields
- **Use Case:** Data analysis, knowledge base import, backup format

**Field Structure (Per Case):**
```json
{
  "case_id": "Case_001",
  "case_number": "K 217/24",
  "court": "Osnovni Sud u Beranji",
  "judge": "Name",
  "verdict_date": "2024",
  "case_type": "Threatening/Endangering Safety",
  "defendant": { /* 13 fields */ },
  "victim": { /* 7 fields */ },
  "incident": { /* 8 fields */ },
  "legal": { /* 4 fields */ },
  "evidence": { /* 4 fields */ },
  "power_dynamics": { /* 3 fields */ },
  "verdict": { /* 7 fields */ },
  "appeals": { /* 3 fields */ }
}
```

### 3. CASE_DATABASE_STRUCTURED.py
- **Location:** Project root directory
- **Type:** Python 3 executable script
- **Dependencies:** None (uses only stdlib: json, csv, datetime)
- **Functions:**
  - `export_to_json()` - Regenerate JSON export
  - `export_to_csv()` - Regenerate CSV export
  - `print_case_summary()` - Display statistics
- **Usage:** Can re-export data if schema changes needed
- **Command:** `python CASE_DATABASE_STRUCTURED.py`

---

## Case Database Summary

### Quick Statistics
- **Total Cases:** 13 records (12 distinct verdicts + 1 retrial)
- **Date Range:** 2012-2024 (12 years)
- **Geographic Coverage:** 7 courts, 6 Montenegrin municipalities
- **Verdict Split:** 10 guilty, 2 acquitted, 2 conditional sentences
- **Evidence:** 30 witness testimonies + 9 expert findings
- **Crime Types:** 7 distinct categories

### Court Distribution
```
Podgorica (Osnovni Sud u Podgorici):      4 cases (31%)
Bijelo Polje (Osnovni Sud u Bijelo Polju): 3 cases (23%)
Cetinje (Osnovni Sud u Cetinje):           2 cases (15%)
Berané, Pljevlja, Rožaje, Kotor:          1 case each (31%)
```

### Crime Type Distribution
```
Threatening/Endangering Safety:  3 cases
Financial crimes (theft/fraud):  3 cases
Workplace violence/assault:      3 cases
Workplace negligence:            1 case
Labor rights violation:          1 case
Stalking (Proganjanje):          1 case *** NEW ***
Domestic violence:               1 case
```

---

## Key Cases for jCOLIBRI Configuration

### Mandatory Test Cases
1. **K 98/2018 (Stalking - NEW)**
   - Verdict: GUILTY
   - Unique Features: Psychiatric diagnosis, communication pattern analysis
   - Use for: Testing harassment pattern matching

2. **K 664/2022 (Workplace Assault)**
   - Verdict: GUILTY
   - Unique Features: Video surveillance with timestamp analysis, multiple eyewitnesses
   - Use for: Testing workplace violence escalation patterns

3. **K 22/2022 (Social Insurance Fraud - Acquitted)**
   - Verdict: ACQUITTED
   - Unique Features: "In dubio pro reo" acquittal despite suspicious behavior
   - Use for: Testing reasonable doubt criteria

### Similarity Matching Examples

**Input:** New case involving repeated unwanted phone calls and workplace harassment
**Expected Matches:** K 98/2018 (stalking), K 1 (threats), K 2 (workplace harassment)

**Input:** Workplace supervisor assaulted by subordinate with multiple witnesses
**Expected Matches:** K 664/2022 (assault), K 10 (workplace assault)

**Input:** Embezzlement through accounting fraud by employee
**Expected Matches:** K 3 & K 6 (embezzlement cases)

---

## Integration Checklist

### Step 1: Database Import
- [ ] Load EXTRACTED_CASES_DATABASE.csv
- [ ] Verify 13 rows imported successfully
- [ ] Confirm all 25 columns populated
- [ ] Test case retrieval (select all, count = 13)

### Step 2: Field Mapping
- [ ] Map CSV columns to CaseDescription.java attributes
- [ ] Configure defendant object population
- [ ] Configure victim object population
- [ ] Configure incident object population
- [ ] Configure legal/verdict object population

### Step 3: Similarity Configuration
- [ ] Define TabularSimilarity for case_type field
- [ ] Define TabularSimilarity for court field
- [ ] Define TabularSimilarity for verdict field
- [ ] Define TabularSimilarity for harm assessment
- [ ] Set weighting factors (test with case weights)

### Step 4: Test Scenarios
- [ ] Input Test Case 1: Threatening behavior → should retrieve K 217/24, K 64/14, K 128/15
- [ ] Input Test Case 2: Workplace assault → should retrieve K 664/2022 (top match)
- [ ] Input Test Case 3: Stalking pattern → should retrieve K 98/2018 (top match)
- [ ] Input Test Case 4: Financial crime → should retrieve K 292/2014 cases
- [ ] Validate retrieval order and similarity scores

### Step 5: Production Deployment
- [ ] Finalize similarity metrics
- [ ] Document weighting rationale
- [ ] Create user guide for precedent matching
- [ ] Deploy to production environment
- [ ] Schedule validation review

---

## Important Notes for Integration

### K 98/2018 - Stalking Case (NEWLY INTEGRATED)
This case requires special handling in jCOLIBRI:
- **Article:** Article 168a st.1 (Stalking/Proganjanje)
- **Key Features:**
  - 20+ unwanted phone calls over 33 days
  - SMS/Viber messages with threats and false accusations
  - In-person confrontation at court building
  - Defendant psychiatric diagnosis documented
  - Victim psychological harm: Level 4 (severe)
  - Family impact: Spouse stress-related hospitalization
  - Occupational impact: Medical director unable to answer on-call phones

- **Similarity Matching Strategy:**
  - Match against workplace harassment cases when victim employed
  - Match against domestic violence cases for intimate partner stalking
  - Match psychiatric component when defendant has documented mental illness
  - Identify escalation patterns: repeated contact → explicit threats → in-person encounter

### Data Quality Notes
- Some defendant/victim names marked "Not specified" (privacy protection in published verdicts)
- JMBG numbers not available in public verdict texts
- Judge names not documented for older cases (2012-2014 verdicts)
- Information gaps are data limitations, not extraction errors

### Acquittal Handling
Three acquittals in database (K 64/14, K 7/2020, K 22/2022) provide important precedents:
- Acquittals should still be included in case retrieval (showing why conviction failed)
- "In dubio pro reo" principle demonstrates when reasonable doubt applies
- Useful for showing prosecution evidence requirements

---

## Performance Optimization

### Database Query Optimization
```java
// For new unknown case, retrieve:
// 1. Same crime type (exact match) - weight 0.4
// 2. Same court system (geographic match) - weight 0.2
// 3. Similar harm assessment - weight 0.2
// 4. Similar power dynamics - weight 0.1
// 5. Similar evidence profile - weight 0.1

// Return top 3-5 matches sorted by similarity score
```

### Suggested KNN Configuration
- K = 5 (retrieve 5 most similar cases)
- Distance metric: Euclidean for numeric fields, exact match for categorical
- Normalization: Min-max scaling for all numeric harm scores

---

## File Locations

```
c:\Users\Win10\Documents\GitHub\PravnaInformatikaTeam8\Project\
├── EXTRACTED_CASES_DATABASE.csv       [IMPORT THIS]
├── EXTRACTED_CASES_DATABASE.json      [Reference format]
├── CASE_DATABASE_STRUCTURED.py        [Re-export script]
├── EXTRACTION_COMPLETE_SUMMARY.md     [Full documentation]
├── EXTRACTED_MOBBING_CASES.txt        [Source verdict texts]
├── VERDICT_EXTRACTION_GUIDE.txt       [Extraction methodology]
└── [Additional project files]
```

---

## Next Actions

1. **Immediate:** Import EXTRACTED_CASES_DATABASE.csv into jCOLIBRI
2. **This Week:** Configure similarity metrics for all case attributes
3. **Week 2:** Develop and validate test cases
4. **Week 3:** Final integration and production deployment
5. **By April 2026:** Complete jCOLIBRI system operational

---

## Support Resources

- **Full Documentation:** See EXTRACTION_COMPLETE_SUMMARY.md for detailed case information
- **Extraction Methodology:** See VERDICT_EXTRACTION_GUIDE.txt for field extraction process
- **Source Data:** See EXTRACTED_MOBBING_CASES.txt for complete verdict texts
- **Python Export:** Run CASE_DATABASE_STRUCTURED.py if data schema changes

---

**Status:** READY FOR jCOLIBRI INTEGRATION  
**Last Updated:** January 29, 2026  
**Team:** 3-person development team, University project, April 2026 deadline
