# AkomaNtoso Quick Reference - Structure Diagram

## Document Hierarchy

```
┌─ akomaNtoso (Root)
│
├─ act / judgment / journal (Document Type)
│
├─ meta (Metadata)
│  ├─ identification
│  │  ├─ FRBRWork (Abstract Document)
│  │  │  ├── FRBRthis (Access point)
│  │  │  ├── FRBRuri (Unique ID)
│  │  │  ├── FRBRdate (Creation date)
│  │  │  ├── FRBRcountry (Country code: me, rs, etc)
│  │  │  ├── FRBRnumber (Official number)
│  │  │  └── FRBRname (Title)
│  │  │
│  │  ├─ FRBRExpression (Specific Version)
│  │  │  ├── FRBRuri (Version ID)
│  │  │  ├── FRBRdate (Amendment date)
│  │  │  └── FRBRlanguage (Language code)
│  │  │
│  │  └─ FRBRManifestation (Physical Format)
│  │     ├── FRBRuri (File location)
│  │     └── FRBRformat (xml, html, pdf, etc)
│  │
│  ├─ publication (Official gazette info)
│  │
│  ├─ classification (Keywords)
│  │
│  └─ references (External links, people, organizations)
│     ├── TLCRole (Author, Editor, etc)
│     ├── TLCOrganization (Courts, Parliament, etc)
│     └── TLCPerson (Individual names)
│
└─ body (Content)
   ├─ preamble (For laws)
   │
   ├─ background (For judgments)
   │  ├── party (defendant, prosecutor, judge, victim)
   │  └── facts
   │
   ├─ chapter (Глава) ─── "Chapter I", "Chapter IV"
   │  ├─ section (Одељак) ─── "Section 20"
   │  │  ├─ article (Члан) ──── "Article 88"
   │  │  │  ├─ paragraph (Став) ── "Paragraph 1, 2, 3"
   │  │  │  │  ├─ point (Тачка) ─ "Point a), b), c)"
   │  │  │  │  └─ content
   │  │  │  │     └─ p (Text paragraph)
   │  │  │  │        └─ ref (Reference to other articles)
   │  │  │  │
   │  │  │  └─ content
   │  │  │     └─ p (Simple text)
   │  │  │
   │  │  └─ provision (Single provision if no articles)
   │  │
   │  └─ part (Alternative to chapters)
   │
   ├─ motivation (Judge's reasoning - for judgments)
   │  └─ p (Paragraphs with ref to articles)
   │
   ├─ decision (Verdict - for judgments)
   │  ├─ verdict element
   │  └─ p (Sentence information)
   │
   └─ conclusion (Summary - optional)
```

---

## Real Example from Your Files

```xml
CASE ID: K 217/24

┌─ Metadata (FRBRWork/Expression/Manifestation)
│  ├─ Court: Osnovni Sud u Beranji
│  ├─ Number: K 217/24
│  ├─ Date: 2024
│  └─ References: → Article 168
│
└─ Body
   ├─ Background
   │  ├─ Defendant: Not specified
   │  └─ Victim: Not specified
   │
   ├─ Motivation
   │  ├─ The court examined the evidence
   │  └─ Found violation of Article 168 st.1
   │
   └─ Decision
      ├─ Verdict: GUILTY
      └─ Sentence: 6 months
```

---

## Element-to-Code Mapping

### Your CaseDescription Fields → AkomaNtoso Elements

```
CaseDescription Property          AkomaNtoso Location
─────────────────────────────────────────────────────────────────
caseNumber (K 217/24)        →   meta/identification/FRBRWork/FRBRnumber
                                 & meta/publication/@number
                                 
court                        →   meta/publication/@showAs
                                 & body/background/party[@role="court"]
                                 
judge                        →   body/background/party[@role="judge"]
                                 & meta/references/TLCPerson
                                 
verdict (GUILTY)             →   body/decision/verdict
                                 
sentence (6 months)          →   body/decision/p
                                 
defendantName                →   body/background/party[@role="defendant"]/person
                                 
victimName                   →   body/background/party[@role="victim"]/person
                                 
articlesCharged              →   body/motivation/ref/@href
                                 meta/references/TLCReference
                                 
incidentNarrative            →   body/background/facts
                                 & body/motivation/p
                                 
harmPhysical                 →   body/background/facts (narrative)
harmPsychological            →   body/background/facts (narrative)
```

---

## Element IDs (eId) Pattern

```
Pattern: [type]_[number]__[level]_[number]

Examples:
─────────

chp_4                          = Chapter 4
   └─ eId="chp_4"

chp_4__sec_20                  = Chapter 4, Section 20
   └─ eId="chp_4__sec_20"

art_88                         = Article 88
   └─ eId="art_88"

art_88__para_1                 = Article 88, Paragraph 1
   └─ eId="art_88__para_1"

art_88__para_2                 = Article 88, Paragraph 2
   └─ eId="art_88__para_2"

art_332__para_1__point_34      = Article 332, Paragraph 1, Point 34
   └─ eId="art_332__para_1__point_34"
```

---

## Reference/Linking Pattern

```
href="/akn/[country]/[document-type]/[document-id]#[element-id]"
 │    │    │        │                │                │
 │    │    │        │                │                └─ Jump to this element
 │    │    │        │                └─ Document identifier
 │    │    │        └─ Document type (act, judgment, etc)
 │    │    └─ Country code (me=Montenegro, rs=Serbia)
 │    └─ AkomaNtoso namespace
 └─ Protocol

Examples:
──────────

/akn/me/act/criminal-code#art_168
  │    │  │   │             │
  │    │  │   │             └─ Article 168 of Criminal Code
  │    │  │   └─ Criminal Code document
  │    │  └─ Act (law)
  │    └─ Montenegro
  └─ AkomaNtoso

/akn/me/judgment/2024/K-217-24#party_defendant
  │    │  │         │    │       │
  │    │  │         │    │       └─ The defendant party element
  │    │  │         │    └─ Case number
  │    │  │         └─ Year
  │    │  └─ Judgment (verdict)
  │    └─ Montenegro
  └─ AkomaNtoso

/akn/me/judgment/2024/K-217-24/sr@2024/!main
  │    │  │         │    │       │     │
  │    │  │         │    │       │     └─ Main content (skip metadata)
  │    │  │         │    │       └─ Language@Date (Serbian, created 2024)
  │    │  │         │    └─ Case number
  │    │  │         └─ Year
  │    │  └─ Judgment
  │    └─ Montenegro
  └─ AkomaNtoso
```

---

## Document Types

```
<act>              Laws, statutes, regulations
├── preamble       Introduction explaining purpose
├── body           Structured chapters, articles
│  ├── chapter     Major grouping
│  ├── section     Sub-grouping
│  ├── article     Specific provisions
│  ├── paragraph   Sub-divisions
│  └── point       Further sub-divisions
└── conclusion     Final provisions

<judgment>         Court decisions, verdicts
├── background     Facts, parties, procedural history
├── motivation     Court's reasoning (why decision)
├── decision       The verdict and sentence
└── conclusion     Summary

<journal>          Official gazettes, publications
├── articles       Individual items published
└── document       Referenced documents

<book>             Collections, reference works
├── chapters       Organized sections
└── references     Bibliography
```

---

## Minimal Judgment Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
    <judgment name="Court Verdict">
        
        <meta>
            <identification source="court">
                <FRBRWork>
                    <FRBRthis value="/akn/me/judgment/2024/K-217-24/!main"/>
                    <FRBRuri value="/akn/me/judgment/2024/K-217-24"/>
                    <FRBRdate date="2024"/>
                    <FRBRcountry value="me"/>
                    <FRBRnumber value="K 217/24"/>
                    <FRBRname value="Verdict K 217/24"/>
                </FRBRWork>
                <FRBRExpression>
                    <FRBRuri value="/akn/me/judgment/2024/K-217-24/sr@2024"/>
                    <FRBRlanguage language="sr"/>
                </FRBRExpression>
                <FRBRManifestation>
                    <FRBRuri value="/akn/me/judgment/2024/K-217-24/sr@2024.xml"/>
                    <FRBRformat value="xml"/>
                </FRBRManifestation>
            </identification>
            <references source="court">
                <TLCReference eId="ref_art_168" 
                             href="/akn/me/act/criminal-code#art_168"/>
            </references>
        </meta>
        
        <body>
            <background eId="background">
                <party eId="party_defendant" role="defendant">
                    <person>Not specified</person>
                </party>
                <party eId="party_victim" role="victim">
                    <person>Not specified</person>
                </party>
            </background>
            
            <motivation eId="motivation">
                <p>The court examined the evidence and found violation of 
                   <ref href="/akn/me/act/criminal-code#art_168">
                       Article 168
                   </ref>
                </p>
            </motivation>
            
            <decision eId="decision">
                <p>The defendant is found <verdict role="guilty">GUILTY</verdict></p>
                <p>Sentence: 6 months imprisonment</p>
            </decision>
        </body>
    </judgment>
</akomaNtoso>
```

---

## Your Next Steps

1. ✅ **Understand Structure** - You've got the example file!
2. ❌ **Generate XML** - Create AkomaNtosoGenerator.java
3. ❌ **Display XML** - Add XML viewer to frontend
4. ❌ **Navigation** - Make article links clickable
5. ❌ **Integration** - Wire it all together

**Start with**: Generate simple XML from your CaseDescription objects → Show it works → Add UI features → Polish

