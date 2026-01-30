# AkomaNtoso Implementation Roadmap for Your Project

## Current State: Where AkomaNtoso Lives in Your Codebase

### 📂 File Locations

```
Your Project/
│
├── 📄 archive/exercise_materials/vezbe/01 Вежбе/
│   └── 02_ZBSP_akn.xml ⭐ EXAMPLE AKOMANTOSO FILE
│       ├── Document: Law on Road Traffic Safety
│       ├── Format: AkomaNtoso 3.0 XML
│       ├── Language: Serbian
│       └── Structure: Chapters → Sections → Articles → Paragraphs
│
├── 📁 archive/exercise_materials/vezbe/04 Вежбе/presude-cbr/
│   └── JColibri CBR System with legal case processing
│
├── src/java/
│   ├── CaseDescription.java ⭐ MAPS TO JUDGMENT METADATA
│   │   ├── caseNumber → Judgment ID
│   │   ├── court → Court metadata
│   │   ├── defendant → Background/party section
│   │   ├── victim → Background/party section
│   │   ├── articlesCharged → References (ref href)
│   │   ├── incidentNarrative → Motivation section
│   │   ├── verdict → Decision section
│   │   └── sentence → Decision section
│   │
│   ├── CaseDatabase.java
│   ├── KNNRetriever.java
│   └── CaseSimilarityCalculator.java
│
├── src/web/public/
│   └── index.html ⭐ DISPLAYS CASE DATA (could show XML)
│       ├── Shows articles as tags
│       ├── Shows defendant/victim info
│       ├── Shows verdict
│       └── Could add XML view button
│
└── docs/
    ├── AKOMANTOSO_ANNOTATION_GUIDE.md (NEW!)
    ├── FRONTEND_BACKEND_ALIGNMENT.md (NEW!)
    └── other documentation
```

---

## Mapping: Your Data Structure → AkomaNtoso XML

### **Your Java CaseDescription Object**

```java
CaseDescription case = new CaseDescription();
case.setCaseNumber("K 217/24");
case.setCourt("Osnovni Sud u Beranji");
case.setDefendantName("Not specified");
case.setVictimName("Not specified");
case.setArticlesCharged(["Article 168 st.1"]);
case.setVerdict("GUILTY");
case.setSentence("6 months");
case.setIncidentNarrative("Threatening/endangering safety of victim");
```

### **Converts to AkomaNtoso XML**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
    <judgment name="Supreme Court Verdict">
        
        <!-- METADATA SECTION -->
        <meta>
            <identification source="case">
                <!-- FRBR Work Level -->
                <FRBRWork>
                    <FRBRthis value="/akn/me/judgment/2024/K-217-24/!main"/>
                    <FRBRdate date="2024"/>
                    <FRBRcountry value="me"/>
                    <FRBRnumber value="K 217/24"/>
                    <FRBRname value="Vedict Case K 217/24"/>
                </FRBRWork>
                
                <!-- FRBR Expression Level -->
                <FRBRExpression>
                    <FRBRuri value="/akn/me/judgment/2024/K-217-24/sr@2024"/>
                    <FRBRlanguage language="sr"/>
                </FRBRExpression>
                
                <!-- FRBR Manifestation Level -->
                <FRBRManifestation>
                    <FRBRuri value="/akn/me/judgment/2024/K-217-24/sr@2024/!main.xml"/>
                    <FRBRformat value="xml"/>
                </FRBRManifestation>
            </identification>
            
            <!-- COURT INFORMATION -->
            <publication number="K 217/24" date="2024" showAs="Supreme Court"/>
            
            <!-- REFERENCES TO LAWS CITED -->
            <references source="application">
                <!-- Link to Article 168 of Criminal Code -->
                <TLCReference eId="ref_art_168" 
                             href="/akn/me/act/criminal-code#art_168" 
                             showAs="Article 168 st.1"/>
            </references>
        </meta>
        
        <!-- JUDGMENT BODY -->
        <body>
            <!-- BACKGROUND: Who is involved -->
            <background>
                <party eId="party_defendant" role="defendant">
                    <person>Not specified</person>
                </party>
                <party eId="party_victim" role="victim">
                    <person>Not specified</person>
                </party>
                <party eId="party_court" role="court">
                    <organization>Osnovni Sud u Beranji</organization>
                </party>
            </background>
            
            <!-- MOTIVATION: Why the decision -->
            <motivation>
                <p>Based on the evidence presented:</p>
                <p eId="motivation_narrative">
                    Threatening/endangering safety of victim
                </p>
                <p>The Court finds that the defendant violated 
                   <ref href="/akn/me/act/criminal-code#art_168">
                       Article 168 st.1
                   </ref> of the Criminal Code.
                </p>
            </motivation>
            
            <!-- DECISION: The verdict -->
            <decision>
                <p eId="decision_verdict">
                    The defendant is found 
                    <verdict role="guilty">GUILTY</verdict>
                </p>
                <p eId="decision_sentence">
                    Sentence: 6 months imprisonment
                </p>
            </decision>
        </body>
    </judgment>
</akomaNtoso>
```

---

## Implementation Phases

### **Phase 1: Foundation (Current State)**
✅ Case data in Java objects (CaseDescription.java)
✅ Example AkomaNtoso files in archive
❌ No XML generation from cases

### **Phase 2: XML Generation (Next)**
Create API endpoint to convert cases to XML:

**Backend - Add to server.js:**
```javascript
app.get('/api/cases/:id/akomantoso', (req, res) => {
  const caseData = getCaseData(req.params.id);
  const xmlString = generateAkomaNtosoXML(caseData);
  res.header('Content-Type', 'application/xml');
  res.send(xmlString);
});
```

**Frontend - Add button:**
```html
<button onclick="viewAsXML('${caseData.id}')">
  📄 View AkomaNtoso XML
</button>
```

### **Phase 3: XML Viewer**
Add XML syntax-highlighted viewer in frontend:

```javascript
async function viewAsXML(caseId) {
  const response = await fetch(`/api/cases/${caseId}/akomantoso`);
  const xml = await response.text();
  
  // Display in modal with syntax highlighting
  displayXMLViewer(xml);
}
```

### **Phase 4: Article Navigation**
Make article references clickable:

```javascript
// When user clicks on article reference in judgment
<ref href="/akn/me/act/criminal-code#art_168" 
     onclick="navigateToArticle('art_168')">
    Article 168 st.1
</ref>

// Function to navigate
function navigateToArticle(articleId) {
  // Load law document
  // Highlight the article
  // Display it in side panel
}
```

### **Phase 5: Document Generation**
Auto-generate judgment documents from case data:

```javascript
// Create new judgment from form data
const judgment = {
  defendant: formData.defendant,
  articles: formData.articles,
  verdict: formData.verdict,
  narrative: formData.narrative
};

// Generate AkomaNtoso XML
const xml = await fetch('/api/judgment/generate', {
  method: 'POST',
  body: JSON.stringify(judgment)
});

// Save to database
// Generate PDF
// Display formatted judgment
```

---

## API Endpoints to Create

### **New Endpoints Needed**

```javascript
// Get case as AkomaNtoso XML
GET /api/cases/:id/akomantoso
  Response: XML string
  
// Generate new judgment XML from form data
POST /api/judgment/generate
  Request: { defendant, articles, verdict, sentence, narrative }
  Response: XML string
  
// Validate XML against schema
POST /api/judgment/validate
  Request: { xml }
  Response: { valid: true/false, errors: [...] }
  
// Get law article details for reference
GET /api/laws/articles/:articleId
  Response: { title, text, penalties, ... }
  
// Search cases by article cited
GET /api/search/articles/:articleId
  Response: [ cases that cite this article ]
```

---

## Helper Functions to Create

### **Java Backend (New Class: AkomaNtosoGenerator.java)**

```java
public class AkomaNtosoGenerator {
    
    public static String generateJudgmentXML(CaseDescription caseData) {
        // Build XML document
        // Structure: meta → body
        // Include all case information
        // Return as string
    }
    
    public static String toXMLMetadata(CaseDescription caseData) {
        // Generate FRBR metadata
        // Create reference to articles
    }
    
    public static String toXMLBody(CaseDescription caseData) {
        // Generate background section
        // Generate motivation section
        // Generate decision section
    }
    
    public static boolean validateXML(String xmlString) {
        // Validate against AkomaNtoso schema
        // Return validation result
    }
}
```

### **Node.js Backend (In server.js)**

```javascript
function generateAkomaNtosoXML(caseData) {
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
  <akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
    <judgment>
      <meta>
        ${generateMetadata(caseData)}
      </meta>
      <body>
        ${generateBackground(caseData)}
        ${generateMotivation(caseData)}
        ${generateDecision(caseData)}
      </body>
    </judgment>
  </akomaNtoso>`;
  return xml;
}
```

### **Frontend (In index.html)**

```javascript
function viewCaseAsXML(caseId) {
  fetch(`/api/cases/${caseId}/akomantoso`)
    .then(r => r.text())
    .then(xml => {
      showXMLModal(formatXML(xml));
    });
}

function formatXML(xmlString) {
  // Add indentation and syntax highlighting
  // Colorize tags, attributes, text
  return formattedXML;
}

function highlightXMLSyntax(xmlString) {
  return xmlString
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/(&lt;[^&]*&gt;)/g, '<span class="tag">$1</span>')
    .replace(/="([^"]*)"/g, '=<span class="attr">"$1"</span>');
}
```

---

## Testing the Implementation

### **Unit Tests (Java)**
```java
@Test
public void testGenerateAkomaNtosoXML() {
  CaseDescription case = new CaseDescription();
  case.setCaseNumber("K 217/24");
  case.setVerdict("GUILTY");
  
  String xml = AkomaNtosoGenerator.generateJudgmentXML(case);
  
  assertTrue(xml.contains("<?xml version"));
  assertTrue(xml.contains("<judgment>"));
  assertTrue(xml.contains("K 217/24"));
}
```

### **Integration Tests**
```java
@Test
public void testXMLValidation() {
  String xml = AkomaNtosoGenerator.generateJudgmentXML(testCase);
  boolean valid = AkomaNtosoGenerator.validateXML(xml);
  assertTrue(valid);
}
```

### **Browser Tests**
```javascript
// Test XML endpoint
fetch('/api/cases/K 217/24/akomantoso')
  .then(r => r.text())
  .then(xml => {
    console.log(xml); // Should see formatted XML
    assert(xml.includes('<judgment>'));
  });
```

---

## Resource Files Needed

### **AkomaNtoso Schema**
Download and save: [akomantoso30.xsd](https://docs.oasis-open.org/legaldocml/akn-core/v1.0/os/part2-specs/schemas/akomantoso30.xsd)

### **Example Templates**
Create templates directory:
```
/schemas/
  ├── akomantoso30.xsd
  ├── judgment-template.xml
  └── act-template.xml
```

### **Reference Data**
Map Montenegrin law articles:
```json
{
  "articles": {
    "168": {
      "title": "Threats, Harassment",
      "code": "Criminal Code",
      "penalties": "3-6 months"
    },
    "166a": {
      "title": "Workplace Assault",
      "code": "Criminal Code",
      "penalties": "6-12 months"
    }
  }
}
```

---

## Summary

| Phase | What | Status | Impact |
|-------|------|--------|--------|
| 1 | Case data structure | ✅ Done | Foundation set |
| 2 | XML generation | ❌ TODO | Enable document export |
| 3 | XML viewer | ❌ TODO | Better UI visibility |
| 4 | Article navigation | ❌ TODO | Enhanced usability |
| 5 | Document generation | ❌ TODO | Full workflow automation |

**Current Gap:** Your data exists but isn't being exported as AkomaNtoso XML. The structure is ready for it!

