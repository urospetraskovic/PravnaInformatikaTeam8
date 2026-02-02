const express = require('express');
const path = require('path');
const fs = require('fs');
const { DOMParser } = require('@xmldom/xmldom');
const app = express();

// Load case database from XML files
const casesDir = path.join(__dirname, '../../data/cases/akomantoso');
let caseDatabase = [];

function parseXMLFile(filePath) {
  try {
    const xmlContent = fs.readFileSync(filePath, 'utf8');
    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlContent);
    
    // Extract information from XML
    const judgment = doc.documentElement;
    const meta = doc.getElementsByTagNameNS('*', 'meta')[0];
    const body = doc.getElementsByTagNameNS('*', 'body')[0];
    
    if (!meta || !body) return null;
    
    // Get identification info
    const FRBRnumber = meta.getElementsByTagNameNS('*', 'FRBRnumber')[0];
    const FRBRname = meta.getElementsByTagNameNS('*', 'FRBRname')[0];
    const caseNumber = FRBRnumber ? FRBRnumber.getAttribute('value') : 'Unknown';
    const crimeType = FRBRname ? FRBRname.getAttribute('value') : 'Unknown';
    
    // Get background info (court, date, etc)
    const backgroundElement = body.getElementsByTagNameNS('*', 'background')[0];
    const backgroundPs = backgroundElement ? backgroundElement.getElementsByTagNameNS('*', 'p') : [];
    let court = 'Unknown';
    let caseDate = 'Unknown';
    
    for (let i = 0; i < backgroundPs.length; i++) {
      const p = backgroundPs[i];
      const text = p.textContent;
      if (text.includes('Sud:')) {
        court = text.replace(/.*Sud:\s*/i, '').trim();
      }
      if (text.includes('Datum presude:')) {
        caseDate = text.replace(/.*Datum presude:\s*/i, '').trim();
      }
    }
    
    // Get articles referenced
    const references = meta.getElementsByTagNameNS('*', 'TLCReference');
    const articles = [];
    for (let i = 0; i < references.length; i++) {
      const ref = references[i];
      const showAs = ref.getAttribute('showAs');
      if (showAs && showAs.includes('Član')) {
        articles.push(showAs);
      }
    }
    
    // Get decision
    const decisionElement = body.getElementsByTagNameNS('*', 'decision')[0];
    const decisionPs = decisionElement ? decisionElement.getElementsByTagNameNS('*', 'p') : [];
    let verdict = 'UNKNOWN';
    let sentenceText = 'Not specified';
    
    for (let i = 0; i < decisionPs.length; i++) {
      const p = decisionPs[i];
      const text = p.textContent;
      if (text.includes('GUILTY')) verdict = 'GUILTY';
      else if (text.includes('ACQUITTED')) verdict = 'ACQUITTED';
      else if (text.includes('CONDITIONAL')) verdict = 'CONDITIONAL';
      
      if (text.includes('Presuda:') || text.includes('presuda:')) {
        sentenceText = text.trim();
      }
    }
    
    return {
      id: caseNumber,
      case_id: path.basename(filePath, '.xml'),
      type: crimeType,
      court: court,
      date: caseDate,
      verdict: verdict,
      articles: articles,
      sentence: sentenceText,
      harm: Math.floor(Math.random() * 5) + 1, // placeholder
      year: 2024,
      xmlFile: filePath
    };
  } catch (error) {
    console.error(`Error parsing ${filePath}:`, error.message);
    return null;
  }
}

// Load all XML case files
try {
  if (fs.existsSync(casesDir)) {
    const files = fs.readdirSync(casesDir).filter(f => f.endsWith('.xml'));
    console.log(`Found ${files.length} case XML files`);
    
    for (const file of files) {
      const filePath = path.join(casesDir, file);
      const caseData = parseXMLFile(filePath);
      if (caseData) {
        caseDatabase.push(caseData);
      }
    }
    
    console.log(`✅ Loaded ${caseDatabase.length} cases from XML files`);
  } else {
    console.log(`Cases directory not found at ${casesDir}`);
  }
} catch (error) {
  console.error('Error loading case database:', error.message);
}

// Fallback database if no XML files found
if (caseDatabase.length === 0) {
  console.log('Using fallback database...');
  caseDatabase = [
    {
      id: 'K 05/1336',
      case_id: 'Case_05_1336',
      type: 'Falsifikovanje novca',
      court: 'Osnovni Sud u BIJELOM POLJU',
      date: 'Unknown',
      verdict: 'ACQUITTED',
      articles: ['Član 339', 'Član 256', 'Član 258'],
      sentence: 'ACQUITTED',
      harm: 3,
      year: 2024
    }
  ];
}

// Routes - API MUST come before static files!
app.use(express.json());

// Add headers to ensure JSON responses
app.use((req, res, next) => {
  if (req.path.startsWith('/api/')) {
    res.header('Content-Type', 'application/json; charset=utf-8');
  }
  next();
});

// API: Get all cases
app.get('/api/cases', (req, res) => {
  res.json(caseDatabase);
});

// API: Get case statistics
app.get('/api/statistics', (req, res) => {
  const stats = {
    totalCases: caseDatabase.length,
    guiltyCount: caseDatabase.filter(c => c.verdict === 'GUILTY').length,
    acquittedCount: caseDatabase.filter(c => c.verdict === 'ACQUITTED').length,
    conditionalCount: caseDatabase.filter(c => c.verdict === 'CONDITIONAL').length,
    averageHarm: caseDatabase.length > 0 ? (caseDatabase.reduce((sum, c) => sum + c.harm, 0) / caseDatabase.length).toFixed(2) : 0,
    courts: [...new Set(caseDatabase.map(c => c.court))].length
  };
  res.json(stats);
});

// API: Get all unique case types
app.get('/api/case-types', (req, res) => {
  const uniqueTypes = [...new Set(caseDatabase.map(c => c.type))].sort();
  const typesWithCounts = uniqueTypes.map(type => ({
    type,
    count: caseDatabase.filter(c => c.type === type).length
  }));
  res.json(typesWithCounts);
});

// API: Get Glava 23 (Criminal Code Chapter 23) articles
app.get('/api/glava23', (req, res) => {
  const glava23Path = path.join(__dirname, '../../data/glava23/criminal_code.xml');
  
  try {
    if (!fs.existsSync(glava23Path)) {
      return res.status(404).json({ error: 'Glava 23 file not found' });
    }
    
    const xmlContent = fs.readFileSync(glava23Path, 'utf8');
    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlContent);
    
    // Extract all articles from the XML
    const articles = [];
    const articleElements = doc.getElementsByTagNameNS('*', 'article');
    
    for (let i = 0; i < articleElements.length; i++) {
      const article = articleElements[i];
      const eId = article.getAttribute('eId');
      const heading = article.getElementsByTagNameNS('*', 'heading')[0]?.textContent || 'Unknown';
      const paragraphs = article.getElementsByTagNameNS('*', 'paragraph');
      const content = [];
      
      for (let j = 0; j < paragraphs.length; j++) {
        const p = paragraphs[j].getElementsByTagNameNS('*', 'p')[0];
        if (p) {
          content.push(p.textContent);
        }
      }
      
      articles.push({
        eId: eId,
        heading: heading,
        content: content.join('\n\n')
      });
    }
    
    res.json({ articles: articles });
  } catch (error) {
    console.error('Error reading Glava 23:', error);
    res.status(500).json({ error: 'Error reading Glava 23' });
  }
});

// API: Get AkomaNtoso XML for a specific case
app.get('/api/akomantoso/:caseId', (req, res) => {
  const caseId = req.params.caseId;
  
  // Convert case ID format: "K 34/14" -> "Case_34_14"
  let xmlFileName = caseId;
  if (caseId.includes('/')) {
    // Format like "K 34/14" -> extract "34" and "14"
    const match = caseId.match(/(\d+)\/(\d+)/);
    if (match) {
      xmlFileName = `Case_${match[1]}_${match[2]}`;
    }
  }
  
  const xmlPath = path.join(__dirname, '../../data/cases/akomantoso', `${xmlFileName}.xml`);
  
  try {
    if (!fs.existsSync(xmlPath)) {
      console.warn(`AkomaNtoso file not found: ${xmlPath}`);
      return res.status(404).json({ error: 'AkomaNtoso file not found for case ' + caseId });
    }
    
    const xmlContent = fs.readFileSync(xmlPath, 'utf8');
    res.header('Content-Type', 'application/xml; charset=utf-8');
    res.send(xmlContent);
  } catch (error) {
    console.error('Error reading AkomaNtoso file:', error);
    res.status(500).json({ error: 'Error reading AkomaNtoso file' });
  }
});

// API: Search cases by type
app.get('/api/search/type/:type', (req, res) => {
  const type = req.params.type.toLowerCase();
  const results = caseDatabase.filter(c => c.type.toLowerCase().includes(type))
    .sort((a, b) => b.harm - a.harm);
  res.json(results);
});

// API: Get case by ID
app.get('/api/cases/:id(*)', (req, res) => {
  try {
    const caseId = decodeURIComponent(req.params.id);
    const caseRecord = caseDatabase.find(c => c.id === caseId);
    
    if (!caseRecord) {
      console.warn(`Case not found: ${caseId}`);
      return res.status(404).json({ 
        error: 'Case not found',
        requestedId: caseId,
        availableCases: caseDatabase.map(c => c.id)
      });
    }
    
    res.json(caseRecord);
  } catch (error) {
    console.error('Error fetching case:', error);
    res.status(500).json({ 
      error: 'Error loading case',
      message: error.message
    });
  }
});

// Serve static files AFTER API routes
app.use(express.static(path.join(__dirname, 'public')));

const PORT = process.env.PORT || 3000;
app.listen(PORT, async () => {
  console.log(`\n✅ Legal CBR Web UI running at http://localhost:${PORT}`);
  console.log(`📊 Database loaded with ${caseDatabase.length} Montenegrian cases\n`);
});
