# AkomaNtoso XML Annotation in Your Project

## Overview
**AkomaNtoso** is an international standard for legal document markup. It's based on OASIS LegalDocML (Legal Document Markup Language) and used by parliaments worldwide to annotate laws, judgments, and legal documents in XML format.

---

## Where AkomaNtoso is in Your Project

### 1. **Example AkomaNtoso File** (From Your Archive)
📁 Location: [archive/exercise_materials/vezbe/01 Вежбе/02_ZBSP_akn.xml](archive/exercise_materials/vezbe/01%20Вежбе/02_ZBSP_akn.xml)

This is a real example of an annotated Montenegrin law:
- **Document:** "Закон о безбедности саобраћаја на путевима" (Law on Road Traffic Safety)
- **Standard:** AkomaNtoso 3.0
- **Language:** Serbian (sr)

### 2. **Your Course Materials** (Exercise Archive)
📁 Location: [archive/exercise_materials/vezbe/04 Вежбе/presude-cbr/](archive/exercise_materials/vezbe/04%20Вежбе/presude-cbr/)

This contains a jCOLIBRI project that integrates:
- Case-Based Reasoning system
- Legal verdict annotation
- XML document processing

---

## AkomaNtoso Structure Explained

### **Document Root Element**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0/WD17">
    <!-- Document type: act, judgment, journal, etc. -->
    <act name="Document Title">
        <meta>...</meta>
        <body>...</body>
    </act>
</akomaNtoso>
```

### **Document Types Supported**
From your notes and the standard:

1. **`<act>`** - Laws, statutes, regulations
   - Example: Law on Road Traffic Safety

2. **`<judgment>`** - Court verdicts, rulings
   - Example: Montenegrin court verdicts (your use case!)

3. **`<journal>`** - Legal magazines, publications
   - Example: Official gazette

4. **`<book>`** - Collections, books

---

## Metadata Section (`<meta>`)

### **FRBRWork - Functional Requirements for Bibliographic Records**

```xml
<FRBRWork>
    <FRBRthis value="/akn/rs/act/2009-41-1404/!main"/>
    <!-- !main = access to actual document content -->
    
    <FRBRuri value="/akn/rs/act/2009-41-1404"/>
    <!-- Unique identifier for this version -->
    
    <FRBRdate date="2009-05-29"/>
    <!-- Original date of document -->
    
    <FRBRauthor href="#ns" as="#author"/>
    <!-- Who created it -->
    
    <FRBRcountry value="rs"/>
    <!-- Country code (rs = Serbia/similar for Montenegro = me) -->
    
    <FRBRnumber value="2009-41-1404"/>
    <!-- Official document number -->
    
    <FRBRname value="Document Title"/>
    <!-- Full name -->
</FRBRWork>
```

### **FRBRExpression - Specific Version**

```xml
<FRBRExpression>
    <FRBRthis value="/akn/rs/act/2009-41-1404/sr@2018-05-25/!main"/>
    
    <FRBRdate date="2018-05-25"/>
    <!-- When this version was made (amendment) -->
    
    <FRBRlanguage language="sr"/>
    <!-- Language: sr=Serbian, me=Montenegrin (if applicable) -->
    
    <FRBRauthor href="#sg" as="#editor"/>
    <!-- Who edited this version -->
</FRBRExpression>
```

### **FRBRManifestation - Physical Format**

```xml
<FRBRManifestation>
    <FRBRthis value="/akn/rs/act/2009-41-1404/sr@2018-05-31/!main.xml"/>
    <!-- The actual XML file we're looking at -->
    
    <FRBRformat value="xml"/>
    <!-- Could be: xml, html, pdf, etc. -->
    
    <FRBRdate date="2018-11-08"/>
    <!-- When file was created -->
</FRBRManifestation>
```

### **Three FRBR Levels Explained:**

| Level | What it is | Example |
|-------|-----------|---------|
| **Work** | Abstract document | "The Law on Traffic Safety" |
| **Expression** | Specific version | "Serbian version amended May 25, 2018" |
| **Manifestation** | Physical format | "This XML file created Nov 8, 2018" |

---

## Document Structure (`<body>`)

### **Hierarchical Organization**

```xml
<body>
    <!-- CHAPTER 4: Traffic Rules -->
    <chapter eId="chp_4">
        <num>IV.</num>
        <heading>ПРАВИЛА САОБРАЋАЈА</heading>
        
        <!-- SECTION 20: Bicycles -->
        <section eId="chp_4__sec_20">
            <num>20.</num>
            <heading>Посебне одредбе о саобраћају бицикала</heading>
            
            <!-- ARTICLE 88: Children on bicycles -->
            <article eId="art_88">
                <num>Члан 89.</num>
                
                <!-- PARAGRAPH 1 -->
                <paragraph eId="art_88__para_1">
                    <content eId="art_88__para_1__content">
                        <p>Дете млађе од 12 година не сме да управља бициклом.</p>
                    </content>
                </paragraph>
                
                <!-- PARAGRAPH 2 -->
                <paragraph eId="art_88__para_2">
                    <content eId="art_88__para_2__content">
                        <p>Изузетно у пешачкој зони...</p>
                    </content>
                </paragraph>
            </article>
        </section>
    </chapter>
</body>
```

### **Element Types**

| Element | Serbian | Purpose | Example |
|---------|---------|---------|---------|
| `<chapter>` | Глава | Highest level grouping | Chapter IV: Traffic Rules |
| `<section>` | Одељак | Sub-grouping within chapter | Section 20: Bicycles |
| `<article>` | Члан | Specific law provision | Article 88: Children rules |
| `<paragraph>` | Став | Subdivision of article | Paragraph 1, 2, 3... |
| `<point>` | Тачка | Sub-subdivision | Point a), b), c)... |

### **Element Identifiers (`eId`)**

The `eId` attribute creates **unique identifiers** for linking:

```
chp_4              = Chapter 4
chp_4__sec_20      = Chapter 4, Section 20
art_88             = Article 88
art_88__para_1     = Article 88, Paragraph 1
art_332__para_1__point_34 = Article 332, Paragraph 1, Point 34
```

---

## References and Linking (`<ref>` and `href`)

### **Cross-References Between Articles**

```xml
<!-- In Article 332 Penalties section -->
<article eId="art_332">
    <paragraph eId="art_332__para_1">
        <content>
            <p>
                <!-- This creates a hyperlink to Article 88 -->
                <ref href="/akn/rs/act/2009-41-1404#art_88">
                    члана 88
                </ref>
            </p>
        </content>
    </paragraph>
</article>
```

### **How References Work**

```
href="/akn/rs/act/2009-41-1404#art_88"
     ↓
/akn/rs/act/2009-41-1404    = The law document itself
#art_88                     = Jump to element with eId="art_88"
```

**In Your Frontend:**
- Click on article reference → Browser jumps to that article
- Used for navigating related laws
- Enables cross-document linking

### **Reference Metadata Section**

```xml
<references source="#gostojic">
    <!-- Role definitions -->
    <TLCRole eId="author" 
             href="/akn/rs/ontology/role/author" 
             showAs="Author"/>
    
    <!-- Organization definitions -->
    <TLCOrganization eId="ns" 
                     href="/akn/rs/ontology/organization/ns" 
                     showAs="Народна скупштина"/>
    
    <!-- Person definitions -->
    <TLCPerson eId="gostojic" 
               href="/akn/rs/ontology/person/somebody" 
               showAs="Стеван Гостојић"/>
</references>
```

---

## Judgment Structure (For Your Court Verdicts)

From your notes, judgments have this structure:

```xml
<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
    <judgment>
        <meta>
            <!-- Similar FRBR metadata as acts -->
            <identification>...</identification>
            <references>...</references>
        </meta>
        
        <body>
            <!-- Judgment-specific structure -->
            
            <!-- 1. BACKGROUND: Parties and facts -->
            <background>
                <party eId="party_accused" role="defendant">
                    <person>John Doe</person>
                </party>
                <party eId="party_prosecutor" role="prosecutor">
                    <organization>Prosecutor's Office</organization>
                </party>
            </background>
            
            <!-- 2. MOTIVATION: Judge's reasoning -->
            <motivation>
                <p>The evidence shows that...</p>
                <p>According to 
                   <ref href="/akn/rs/act/2009-41-1404#art_88">
                       Article 88
                   </ref>, the defendant...
                </p>
            </motivation>
            
            <!-- 3. DECISION: The verdict -->
            <decision>
                <p>We find the defendant 
                   <verdict>GUILTY</verdict> of violating 
                   <ref href="/akn/rs/act/2009-41-1404#art_88">
                       Article 88, Paragraph 1
                   </ref>
                </p>
                <p>Sentence: 6 months imprisonment</p>
            </decision>
        </body>
    </judgment>
</akomaNtoso>
```

---

## How Your Project Uses AkomaNtoso

### **Current Implementation**

1. **Storage**: Example annotation at [archive/exercise_materials/vezbe/01 Вежбе/02_ZBSP_akn.xml](archive/exercise_materials/vezbe/01%20Вежбе/02_ZBSP_akn.xml)

2. **Backend**: Java files extract case data (CaseDescription.java) which corresponds to:
   - Judgment metadata
   - Parties (defendant, victim, judge)
   - Articles charged (cross-references to laws)
   - Decision/verdict

3. **Frontend**: Currently displays:
   - Court name (from `<meta>`)
   - Case type/articles (from `<body>`)
   - Verdict (from decision section)

### **Missing Features (Future Implementation)**

1. **XML Annotation API** - Generate AkomaNtoso XML from case data
2. **Reference Navigation** - Click article links to jump to law text
3. **Document Viewer** - Display XML with syntax highlighting
4. **Cross-Reference Database** - Link cases to specific laws
5. **Semantic Search** - Find cases by legal articles cited

---

## Creating AkomaNtoso Annotations (Next Steps)

### **Method 1: Manual Annotation**
```xml
1. Start with template
2. Add metadata (case number, date, court)
3. Structure judgment in sections
4. Add references to articles
5. Validate XML schema
```

### **Method 2: AI-Assisted (Your Notes Mention)**
```
1. Input: Court verdict text
2. Tool: ChatGPT or Gemini API
3. Prompt: "Convert to AkomaNtoso XML"
4. Output: Structured XML
5. Review & Validate
```

### **Method 3: Programmatic (Your Backend)**
```java
// Build from CaseDescription object
Judgment judgment = new Judgment();
judgment.setMetadata(caseData.getCourt(), caseData.getCaseNumber());
judgment.setBackground(caseData.getDefendant(), caseData.getVictim());
judgment.setMotivation(caseData.getIncidentNarrative());
judgment.setDecision(caseData.getVerdict(), caseData.getSentence());
judgment.toAkomaNtosoXML(); // Generate XML
```

---

## Key Takeaways

✅ **AkomaNtoso is in your project** as:
- Example file: `02_ZBSP_akn.xml`
- Referenced in your exercise materials
- Used in your CBR system for legal document structure

✅ **Your data maps to AkomaNtoso** as:
- `CaseDescription` → Judgment metadata
- Articles charged → `<ref>` to law articles
- Verdict → `<decision>` section
- Court information → `<meta>` section

✅ **Next step for your team:**
- Generate AkomaNtoso XML from case data
- Create XML viewer in web UI
- Implement article cross-referencing
- Validate against OASIS schemas

---

## References

- **Standard Specification**: [AkomaNtoso 3.0](https://docs.oasis-open.org/legaldocml/akn-core/v1.0/os/part2-specs/schemas/akomantoso30.xsd)
- **Used By**: European Parliament, Serbian Parliament, many national legislatures
- **Format**: XML based on OASIS LegalDocML standard
- **Your Example**: [02_ZBSP_akn.xml](archive/exercise_materials/vezbe/01%20Вежбе/02_ZBSP_akn.xml)

