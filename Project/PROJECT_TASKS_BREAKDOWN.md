# Правна Информатика - Пројектни Задаци (Project Task Breakdown)
## Team 8 - Legal Informatics Project 2025/2026

---

## 📋 PROJECT OVERVIEW

This project creates a **Decision Support System for Judges** that:
- Contains a **Knowledge Base** of legal norms and court decisions (судске праксе)
- Enables **reasoning over facts** entered by the user (judge)
- Proposes **violated legal norms** and **potential sanctions**
- Shows **relevant case law** as justification

### Selected Legal Domain
- **Law**: Кривични законик Црне Горе (Criminal Code of Montenegro)
- **Chapter**: Глава 23 - Кривична дјела против платног промета и привредног пословања
- **Main Articles**: 
  - **Члан 258** - Фалсификовање новца (Counterfeiting money)
  - **Члан 260** - Фалсификовање и злоупотреба кредитних картица (Credit card fraud)

### Source of Verdicts
- Website: sudovi.me (Montenegrin courts)
- Location: `archive/presude/`
  - `falsifikovanje novca/` (Article 258) - 6 files with ~60 verdicts
  - `falsifikovanje i zloupotreba kreditnih kartica/` (Article 260) - 7 files with ~70 verdicts

---

## 🎯 TASK BREAKDOWN BY PROJECT REQUIREMENTS

### TASK 1: Law Annotation in Akoma Ntoso Format ✅ (Partially Done)
**Status**: Needs improvement  
**Location**: `data/glava23/criminal_code.xml`

#### Sub-tasks:
- [ ] **1.1** Complete all articles from Глава 23 (258-286) in Akoma Ntoso XML
- [ ] **1.2** Add proper `eId` attributes for all elements (chapters, articles, paragraphs)
- [ ] **1.3** Add cross-references between articles using `<ref>` tags
- [ ] **1.4** Add organization references (courts, government bodies)
- [ ] **1.5** Add date annotations where applicable
- [ ] **1.6** Add penalty information as structured data
- [ ] **1.7** Create navigation anchors for hyperlinks from verdicts

**Pattern to follow**: `archive/exercise_materials/vezbe/01 Вежбе/02_ZBSP_akn.xml`

---

### TASK 2: Court Decisions in Akoma Ntoso Format 🔄 (In Progress)
**Status**: 6 files exist, need 15+ more  
**Location**: `data/cases/akomantoso_new/`

#### Sub-tasks:
- [ ] **2.1** Create Akoma Ntoso XML for 20+ verdicts from Article 258 (falsifikovanje novca)
- [ ] **2.2** Create Akoma Ntoso XML for 20+ verdicts from Article 260 (credit cards)
- [ ] **2.3** Annotate metadata:
  - Case number (broj predmeta)
  - Court name (sud)
  - Date (datum)
  - Judge name (sudija)
  - Defendant info (optuženi)
  - Prosecutor (tužilac)
  - Witnesses (svjedoci)
- [ ] **2.4** Annotate references to law articles using `<ref href="#art_258">` format
- [ ] **2.5** Structure verdict sections: background, narrative, motivation, decision
- [ ] **2.6** Add sentence/penalty information

**Template structure**:
```xml
<judgment xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
  <meta>
    <identification>
      <FRBRWork>...</FRBRWork>
      <FRBRExpression>...</FRBRExpression>
      <FRBRManifestation>...</FRBRManifestation>
    </identification>
    <references>
      <TLCReference href="/akn/me/act/criminal-code#art_258"/>
    </references>
  </meta>
  <body>
    <background>... court info, parties ...</background>
    <narrative>... facts of the case ...</narrative>
    <motivation>... legal reasoning ...</motivation>
    <decision>... verdict and sentence ...</decision>
  </body>
</judgment>
```

---

### TASK 3: Legal Rules in LegalRuleML Format ⚠️ (Not Started)
**Status**: Not started  
**Location**: To create in `data/rules/`

#### Sub-tasks:
- [ ] **3.1** Create `rules.lrml` file for DR-Device
- [ ] **3.2** Model minimum 10 prescriptive statements for Article 258:
  - Rule: If person puts counterfeit money in circulation → violates Art. 258 st.2
  - Rule: If amount > 15,000 EUR → violates Art. 258 st.3 (heavier penalty)
  - Rule: If person makes counterfeit money → violates Art. 258 st.1
- [ ] **3.3** Model minimum 10 prescriptive statements for Article 260:
  - Rule: If person uses stolen credit card → violates Art. 260 st.1
  - Rule: If gain > 3,000 EUR → violates Art. 260 st.3
  - Rule: If gain > 30,000 EUR → violates Art. 260 st.4
- [ ] **3.4** Create penalty statements linking rules to sanctions
- [ ] **3.5** Create override statements for rule priorities
- [ ] **3.6** Create facts.xml input file template
- [ ] **3.7** Test with DR-Device tool

**Facts to model** (minimum 7 key facts):
1. `counterfeit_money_created` (boolean)
2. `counterfeit_money_circulated` (boolean)
3. `amount_eur` (number)
4. `credit_card_stolen` (boolean)
5. `credit_card_forged` (boolean)
6. `financial_gain_obtained` (boolean)
7. `financial_gain_amount` (number)
8. `defendant_knew_money_was_fake` (boolean)
9. `defendant_reported_crime` (boolean)
10. `prior_convictions` (boolean)

---

### TASK 4: NLP Extraction of Metadata and Facts 🔄 (Partially Done)
**Status**: Scripts exist but need improvement  
**Location**: Various Python scripts in root

#### Sub-tasks:
- [ ] **4.1** Review and improve `extract_verdicts.py`
- [ ] **4.2** Create NLP pipeline to extract:
  - Defendant name/initials (optuženi)
  - Judge name (sudija)
  - Court clerk (zapisničar)
  - Witnesses (svjedoci)
  - Decision date (datum)
  - Case number (broj predmeta)
- [ ] **4.3** Extract factual description (činjenično stanje):
  - Amount of money involved
  - Type of crime (creation, circulation, possession)
  - Whether card was stolen or forged
  - Financial gain amount
- [ ] **4.4** Create manual correction interface
- [ ] **4.5** Store extracted data in structured format (CSV/JSON)
- [ ] **4.6** Use LLM (GPT/Gemini) for complex extraction

**Key extraction patterns**:
- `Optuženi .* od oca .* i majke .*` → defendant info
- `dana \d{2}\.\d{2}\.\d{4}` → dates
- `iznos od .* eura` → amounts
- `čl\.\s*\d+\s*st\.\s*\d+` → article references

---

### TASK 5: Rule-Based Reasoning with DR-Device ⚠️ (Not Started)
**Status**: Not started  
**Location**: To create in `src/java/drdevice/` or integration scripts

#### Sub-tasks:
- [ ] **5.1** Set up Java 8 environment for DR-Device
- [ ] **5.2** Create rulebase.lrml with Article 258 and 260 rules
- [ ] **5.3** Create XSL transformation files
- [ ] **5.4** Create integration script to:
  - Take facts from web form
  - Run DR-Device
  - Parse export file
  - Return violated articles and penalties
- [ ] **5.5** Create test cases for all rules
- [ ] **5.6** Display reasoning results in UI

---

### TASK 6: Case-Based Reasoning with jColibri 🔄 (Structure Exists)
**Status**: Java classes exist, need completion  
**Location**: `src/java/`

#### Sub-tasks:
- [ ] **6.1** Review existing `CaseDescription.java` - add all 7+ attributes
- [ ] **6.2** Complete `CaseSimilarityCalculator.java` with proper similarity functions
- [ ] **6.3** Create similarity tables for categorical attributes:
  - Crime type similarity matrix
  - Sentence type similarity
- [ ] **6.4** Create numerical similarity functions:
  - Amount similarity (logarithmic scale)
  - Sentence duration similarity
- [ ] **6.5** Set up case database in CSV format
- [ ] **6.6** Implement KNN retrieval
- [ ] **6.7** Create post-cycle to add new cases

**Case attributes** (minimum 7):
1. `sud` - Court name (string)
2. `vrsta_djela` - Crime type (enum: FALSIFIKOVANJE_NOVCA, ZLOUPOTREBA_KARTICE)
3. `iznos_stete` - Damage amount in EUR (number)
4. `prethodna_osudivanost` - Prior convictions (boolean)
5. `priznanje` - Confession (boolean)
6. `vrsta_kazne` - Sentence type (enum: ZATVOR, USLOVNA, NOVCANA)
7. `trajanje_kazne_mjeseci` - Sentence duration in months (number)
8. `olaksavajuce_okolnosti` - Mitigating circumstances (boolean)
9. `otezavajuce_okolnosti` - Aggravating circumstances (boolean)
10. `clan_zakona` - Violated article (string)

---

### TASK 7: Law and Verdict Viewer UI ✅ (Exists, needs fixes)
**Status**: Frontend exists, hyperlinks need fixing  
**Location**: `src/web/public/index.html`

#### Sub-tasks:
- [ ] **7.1** Fix navigation between law text and verdicts
- [ ] **7.2** Implement hyperlink from verdict → law article:
  - When clicking "Члан 258" in verdict, jump to law text
  - Highlight referenced article
- [ ] **7.3** Display extracted metadata in sidebar
- [ ] **7.4** Show facts from verdict description
- [ ] **7.5** Add filtering by crime type (258 vs 260)
- [ ] **7.6** Ensure Akoma Ntoso XML is not shown to user (rendered HTML only)
- [ ] **7.7** Add Cyrillic/Latin toggle

---

### TASK 8: New Case Input and Reasoning Interface ⚠️ (Not Started)
**Status**: Not started  
**Location**: To add to `src/web/`

#### Sub-tasks:
- [ ] **8.1** Create form for entering new case facts:
  - Crime type dropdown
  - Amount input field
  - Checkboxes for boolean facts
- [ ] **8.2** Integrate with rule-based reasoning (DR-Device)
- [ ] **8.3** Integrate with case-based reasoning (jColibri)
- [ ] **8.4** Display proposed:
  - Violated articles with text
  - Suggested sanctions (min-max range)
  - Similar cases with similarity scores
- [ ] **8.5** Allow judge to select final verdict
- [ ] **8.6** Save new case to database

---

### TASK 9: Verdict Generation ⚠️ (Not Started)
**Status**: Not started  
**Location**: To create

#### Sub-tasks:
- [ ] **9.1** Create verdict template based on existing verdicts
- [ ] **9.2** Use LLM to generate verdict text from:
  - Input facts
  - Reasoning results
  - Selected similar cases
- [ ] **9.3** Generate PDF version
- [ ] **9.4** Auto-annotate generated verdict in Akoma Ntoso
- [ ] **9.5** Add new verdict to case database

---

## 📁 FILE STRUCTURE

```
Project/
├── archive/
│   ├── glava 23.txt                    # Law text (source)
│   ├── presude/
│   │   ├── falsifikovanje novca/       # Art. 258 verdicts
│   │   │   ├── 1.txt ... 6.txt
│   │   └── falsifikovanje i zloupotreba.../  # Art. 260 verdicts
│   │       └── 1.txt ... 7.txt
│   └── exercise_materials/             # Templates and examples
│
├── data/
│   ├── glava23/
│   │   └── criminal_code.xml           # Law in Akoma Ntoso ⬅️ IMPROVE
│   ├── cases/
│   │   ├── akomantoso_new/             # Verdicts in Akoma Ntoso ⬅️ ADD MORE
│   │   └── database.csv                # Case attributes ⬅️ CREATE
│   ├── rules/
│   │   ├── rulebase.lrml               # Legal rules ⬅️ CREATE
│   │   └── facts_template.xml          # Input facts ⬅️ CREATE
│   └── exports/
│
├── src/
│   ├── java/                           # jColibri CBR
│   │   ├── CaseDescription.java        # ⬅️ COMPLETE
│   │   └── CaseSimilarityCalculator.java
│   └── web/
│       ├── server.js
│       └── public/
│           └── index.html              # Main UI ⬅️ FIX
│
├── scripts/
│   ├── extract_facts.py                # NLP extraction ⬅️ CREATE
│   ├── generate_akomantoso.py          # XML generation
│   └── verdict_generator.py            # Verdict generation ⬅️ CREATE
│
└── docs/                               # Documentation
```

---

## 🚀 PRIORITY ORDER

### Phase 1: Data Foundation (Today)
1. ✅ Create 20 Akoma Ntoso verdict files
2. ✅ Complete law XML with all articles
3. ✅ Extract case attributes to CSV

### Phase 2: Reasoning Setup (Next)
4. Create LegalRuleML rules
5. Complete jColibri similarity functions
6. Test both reasoning systems

### Phase 3: Integration
7. Fix UI hyperlinks
8. Create new case input form
9. Connect reasoning to UI

### Phase 4: Generation
10. Implement verdict generation
11. Final testing and documentation

---

## 📝 NOTES FROM EXERCISES

From `sve vezbe txt.txt`:
- Use Cyrillic for all Serbian text
- Chapter = глава, Section = поглавље, Article = члан
- Pattern for eId: `art_258__para_1`, `chp_23__sec_1`
- References use `<ref href="#art_258">члан 258</ref>`
- Verdicts need: background, narrative, motivation, decision
- Similar cases should show similarity score (0-1)
- DR-Device needs Java 8
- jColibri uses CSV or similar for case database

---

*Last updated: February 5, 2026*
