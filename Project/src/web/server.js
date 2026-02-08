const express = require('express');
const path = require('path');
const fs = require('fs');
const { DOMParser } = require('@xmldom/xmldom');
const { execSync } = require('child_process');

// Kill any existing process on the port before starting
const PORT = process.env.PORT || 3000;
function killPortProcess(port) {
  try {
    if (process.platform === 'win32') {
      // Find and kill process on Windows
      const result = execSync(`netstat -ano | findstr :${port} | findstr LISTENING`, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
      const lines = result.trim().split('\n');
      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        const pid = parts[parts.length - 1];
        if (pid && pid !== '0') {
          try {
            execSync(`taskkill /F /PID ${pid}`, { stdio: 'ignore' });
            console.log(`🔄 Killed existing process on port ${port} (PID: ${pid})`);
          } catch (e) { /* ignore if already dead */ }
        }
      }
    } else {
      // Unix-like systems
      execSync(`lsof -ti:${port} | xargs kill -9 2>/dev/null || true`, { stdio: 'ignore' });
    }
  } catch (e) {
    // No process found on port, which is fine
  }
}

// Kill any existing process before starting
killPortProcess(PORT);

const app = express();

// Load case database from XML files - try akomantoso_new first, fallback to akomantoso
const casesDir = path.join(__dirname, '../../data/cases/akomantoso_new');
const casesDirFallback = path.join(__dirname, '../../data/cases/akomantoso');
let caseDatabase = [];

function parseXMLFile(filePath) {
  try {
    const xmlContent = fs.readFileSync(filePath, 'utf8');
    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlContent);
    
    // Extract information from XML
    const judgment = doc.documentElement;
    const meta = doc.getElementsByTagNameNS('*', 'meta')[0];
    const body = doc.getElementsByTagNameNS('*', 'body')[0] || doc.getElementsByTagNameNS('*', 'judgmentBody')[0];
    
    if (!meta || !body) return null;
    
    // Get proprietary metadata (Serbian fields)
    const proprietary = meta.getElementsByTagNameNS('*', 'proprietary')[0];
    let sudija = 'Nepoznat';
    let sud = 'Nepoznat';
    let kazna = 'Nepoznat';
    let tipKrivicnogDjela = '';
    let uslovnaOsuda = false;
    let novcanaKazna = '';
    let godinaRodjenja = '';
    let prebivaliste = '';
    let zaposlenost = '';
    let bracniStatus = '';
    let ranijeOsudjivan = '';
    let svjedoci = [];
    let dokazi = [];
    let brojPredmeta = '';
    let vrstaPresude = '';
    let opisSlucaja = '';
    
    if (proprietary) {
      // Extract Serbian proprietary fields
      const getTextContent = (tagName) => {
        const el = proprietary.getElementsByTagNameNS('*', tagName)[0];
        return el ? el.textContent.trim() : '';
      };
      
      sudija = getTextContent('sudija') || 'Nepoznat';
      sud = getTextContent('sud') || sud;
      kazna = getTextContent('kazna') || 'Nepoznat';
      tipKrivicnogDjela = getTextContent('tipKrivicnogDjela') || '';
      uslovnaOsuda = getTextContent('uslovnaOsuda') === 'Da';
      novcanaKazna = getTextContent('novcanaKazna') || '';
      godinaRodjenja = getTextContent('godinaRodjenja') || '';
      prebivaliste = getTextContent('prebivaliste') || '';
      zaposlenost = getTextContent('zaposlenost') || '';
      bracniStatus = getTextContent('bracniStatus') || '';
      ranijeOsudjivan = getTextContent('ranijeOsudjivan') || '';
      brojPredmeta = getTextContent('brojPredmeta') || '';
      vrstaPresude = getTextContent('vrstaPresude') || '';
      opisSlucaja = getTextContent('opisSlucaja') || '';
      
      // Extract witnesses list
      const svjedociEl = proprietary.getElementsByTagNameNS('*', 'svjedoci')[0];
      if (svjedociEl) {
        const svjedokEls = svjedociEl.getElementsByTagNameNS('*', 'svjedok');
        for (let i = 0; i < svjedokEls.length; i++) {
          svjedoci.push(svjedokEls[i].textContent.trim());
        }
      }
      
      // Extract evidence list
      const dokaziEl = proprietary.getElementsByTagNameNS('*', 'dokazi')[0];
      if (dokaziEl) {
        const dokazEls = dokaziEl.getElementsByTagNameNS('*', 'dokaz');
        for (let i = 0; i < dokazEls.length; i++) {
          dokazi.push(dokazEls[i].textContent.trim());
        }
      }
    }
    
    // Get identification info
    const FRBRnumber = meta.getElementsByTagNameNS('*', 'FRBRnumber')[0];
    const FRBRname = meta.getElementsByTagNameNS('*', 'FRBRname')[0];
    const caseNumber = brojPredmeta || (FRBRnumber ? FRBRnumber.getAttribute('value') : 'Nepoznat');
    const crimeType = tipKrivicnogDjela || (FRBRname ? FRBRname.getAttribute('value') : 'Nepoznat');
    
    // Get classification keywords for type
    let keywords = [];
    const keywordElements = meta.getElementsByTagNameNS('*', 'keyword');
    for (let i = 0; i < keywordElements.length; i++) {
      keywords.push(keywordElements[i].getAttribute('value'));
    }
    
    // Determine case type from keywords or FRBRname
    let displayType = crimeType;
    if (keywords.length > 0) {
      displayType = keywords[0]; // Use first keyword as primary type
    }
    
    // Normalize case types to two main categories
    const lowerType = displayType.toLowerCase().replace(/_/g, ' ');
    if (lowerType.includes('kreditn') || lowerType.includes('kartic') || lowerType.includes('bezgotovinsk')) {
      displayType = 'Falsifikovanje i zloupotreba kreditnih kartica';
    } else if (lowerType.includes('falsifikovan') || lowerType.includes('novca') || lowerType.includes('novac')) {
      displayType = 'Falsifikovanje novca';
    }
    
    // Get background info (court, date, etc)
    const introductionElement = body.getElementsByTagNameNS('*', 'introduction')[0];
    const backgroundElement = body.getElementsByTagNameNS('*', 'background')[0] || introductionElement;
    const backgroundPs = backgroundElement ? backgroundElement.getElementsByTagNameNS('*', 'p') : [];
    let court = sud || 'Nepoznat';
    let caseDate = 'Nepoznat';
    let defendant = 'Nepoznat';
    
    for (let i = 0; i < backgroundPs.length; i++) {
      const p = backgroundPs[i];
      const text = p.textContent;
      if (text.includes('Sud:') || text.includes('суд') || text.includes('Osnovni Sud')) {
        court = text.replace(/.*(?:Sud:|суд:?)\s*/i, '').trim().split(',')[0];
        if (court.length < 3) court = sud || 'Nepoznat';
      }
      if (text.includes('Datum') || text.includes('датум')) {
        const dateMatch = text.match(/\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4}/);
        if (dateMatch) caseDate = dateMatch[0];
      }
    }
    
    // Override court with proprietary sud if available
    if (sud && sud !== 'Nepoznat') {
      court = 'Osnovni Sud u ' + sud;
    }
    
    // Extract case description - prioritize opisSlucaja from proprietary
    let caseDescription = opisSlucaja;
    
    // Fallback to caseDescription element or arguments if opisSlucaja is empty
    if (!caseDescription) {
      const caseDescElements = body.getElementsByTagNameNS('*', 'caseDescription');
      const argumentsElements = body.getElementsByTagNameNS('*', 'arguments');
      
      if (caseDescElements.length > 0) {
        const descPs = caseDescElements[0].getElementsByTagNameNS('*', 'p');
        for (let i = 0; i < descPs.length; i++) {
          caseDescription += descPs[i].textContent.trim() + ' ';
        }
      } else if (argumentsElements.length > 0) {
        const descPs = argumentsElements[0].getElementsByTagNameNS('*', 'p');
        for (let i = 0; i < descPs.length; i++) {
          caseDescription += descPs[i].textContent.trim() + ' ';
        }
      }
      caseDescription = caseDescription.trim();
    }
    
    // Get defendant info from TLCPerson
    const persons = meta.getElementsByTagNameNS('*', 'TLCPerson');
    for (let i = 0; i < persons.length; i++) {
      const person = persons[i];
      const eId = person.getAttribute('eId');
      if (eId && (eId.includes('defendant') || eId.includes('optuzeni'))) {
        defendant = person.getAttribute('showAs') || 'Nepoznat';
        break;
      }
    }
    
    // Get articles referenced
    const references = meta.getElementsByTagNameNS('*', 'TLCReference');
    const articles = [];
    for (let i = 0; i < references.length; i++) {
      const ref = references[i];
      const showAs = ref.getAttribute('showAs');
      if (showAs && (showAs.includes('Član') || showAs.includes('члан') || showAs.includes('Clan') || showAs.includes('čl.'))) {
        articles.push(showAs);
      }
    }
    
    // Also check ref elements in body for article references
    const bodyRefs = body.getElementsByTagNameNS('*', 'ref');
    for (let i = 0; i < bodyRefs.length; i++) {
      const ref = bodyRefs[i];
      const href = ref.getAttribute('href') || '';
      if (href.includes('art_')) {
        const artMatch = href.match(/art_(\d+)/);
        if (artMatch) {
          const artNum = `Član ${artMatch[1]}`;
          if (!articles.includes(artNum)) {
            articles.push(artNum);
          }
        }
      }
    }
    
    // Get decision/conclusions
    const decisionElement = body.getElementsByTagNameNS('*', 'decision')[0] || 
                           body.getElementsByTagNameNS('*', 'conclusions')[0];
    const decisionPs = decisionElement ? decisionElement.getElementsByTagNameNS('*', 'p') : [];
    let verdict = 'NEPOZNAT';
    let sentenceText = kazna || 'Nepoznat';
    
    // First check if vrstaPresude is set in proprietary section - most reliable
    if (vrstaPresude) {
      const vp = vrstaPresude.toLowerCase();
      if (vp === 'kriv' || vp === 'kriva' || vp === 'osuđen' || vp === 'osuđena') {
        verdict = 'KRIV';
      } else if (vp === 'oslobođen' || vp === 'oslobođena' || vp.includes('oslob')) {
        verdict = 'OSLOBOĐEN';
      } else if (vp.includes('uslovna') || vp.includes('uslovn')) {
        verdict = 'KRIV';  // Conditional is still guilty
      } else if (vp.includes('odbij') || vp.includes('odbač')) {
        verdict = 'ODBAČENO';
      } else {
        verdict = vrstaPresude.toUpperCase();
      }
    } else {
      // Fallback: try to parse from decision text
      for (let i = 0; i < decisionPs.length; i++) {
        const p = decisionPs[i];
        const text = p.textContent;
        
        // Check for verdict type - TRANSLATE TO SERBIAN
        if (text.includes('GUILTY') || text.includes('KRIV') || text.includes('Kriv') || text.includes('kriv') || text.includes('OSUĐUJE') || text.includes('Osuđuje')) {
          verdict = 'KRIV';  // Serbian for GUILTY
        } else if (text.includes('ACQUITTED') || text.includes('OSLOBOĐEN') || text.includes('oslobođen') || text.includes('Oslobađa') || text.includes('OSLOBAĐA')) {
          verdict = 'OSLOBOĐEN';  // Serbian for ACQUITTED
        } else if (text.includes('CONDITIONAL') || text.includes('USLOVNA') || text.includes('uslovna')) {
          verdict = 'KRIV';  // Conditional sentence is still a guilty verdict in Serbian law
        } else if (text.includes('ODBIJA')) {
          verdict = 'ODBAČENO';  // Case dismissed
        }
        
        // Extract sentence details
        if (text.includes('zatvor') || text.includes('Kazna') || text.includes('kazna') || text.includes('Presuda') || text.includes('Odluka')) {
          sentenceText = text.trim();
        }
      }
    }
    
    // If we have uslovnaOsuda set, reflect it
    if (uslovnaOsuda && sentenceText === 'Nije navedeno') {
      sentenceText = 'Uslovna osuda';
    }
    
    // Extract year from case number
    let year = 2024;
    const yearMatch = caseNumber.match(/\/(\d+)/);
    if (yearMatch) {
      const parsedYear = parseInt(yearMatch[1]);
      // Handle both 2-digit (K 4/19) and 4-digit (K 4/2019) year formats
      if (parsedYear > 99) {
        year = parsedYear; // Already 4-digit year
      } else {
        year = (parsedYear <= 30 ? 2000 : 1900) + parsedYear;
      }
    }
    
    // Build evidence string from dokazi array
    let evidenceStr = 'Nije navedeno';
    if (dokazi.length > 0) {
      evidenceStr = dokazi.join('; ');
    }
    
    return {
      id: caseNumber,
      case_id: path.basename(filePath, '.xml'),
      type: displayType,
      court: court,
      date: caseDate,
      verdict: verdict,
      articles: articles,
      sentence: sentenceText,
      defendant: defendant,
      keywords: keywords,
      caseDescription: caseDescription,
      evidence: evidenceStr,
      // New Serbian fields
      sudija: sudija,
      uslovnaOsuda: uslovnaOsuda,
      novcanaKazna: novcanaKazna,
      godinaRodjenja: godinaRodjenja,
      prebivaliste: prebivaliste,
      zaposlenost: zaposlenost,
      bracniStatus: bracniStatus,
      ranijeOsudjivan: ranijeOsudjivan,
      svjedoci: svjedoci,
      dokazi: dokazi,
      harm: Math.floor(Math.random() * 5) + 1,
      year: year,
      xmlFile: filePath
    };
  } catch (error) {
    console.error(`Error parsing ${filePath}:`, error.message);
    return null;
  }
}

// Load all XML case files
try {
  // Try loading from akomantoso_new first
  let targetDir = casesDir;
  if (!fs.existsSync(casesDir)) {
    console.log(`Primary cases directory not found at ${casesDir}, trying fallback...`);
    targetDir = casesDirFallback;
  }
  
  if (fs.existsSync(targetDir)) {
    const files = fs.readdirSync(targetDir).filter(f => f.endsWith('.xml'));
    console.log(`Found ${files.length} case XML files in ${targetDir}`);
    
    for (const file of files) {
      const filePath = path.join(targetDir, file);
      const caseData = parseXMLFile(filePath);
      if (caseData) {
        caseDatabase.push(caseData);
      }
    }
    
    console.log(`✅ Loaded ${caseDatabase.length} cases from XML files`);
  } else {
    console.log(`Cases directory not found at ${targetDir}`);
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
      court: 'Osnovni Sud u Bijelom Polju',
      date: 'Nepoznat',
      verdict: 'OSLOBOĐEN',
      articles: ['Član 339', 'Član 256', 'Član 258'],
      sentence: 'Oslobođen',
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
    guiltyCount: caseDatabase.filter(c => c.verdict === 'KRIV').length,
    acquittedCount: caseDatabase.filter(c => c.verdict === 'OSLOBOĐEN').length,
    conditionalCount: caseDatabase.filter(c => c.verdict === 'ODBAČENO').length,
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
      const numElement = article.getElementsByTagNameNS('*', 'num')[0];
      const articleNum = numElement?.textContent || '';
      const heading = article.getElementsByTagNameNS('*', 'heading')[0]?.textContent || 'Nepoznat';
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
        num: articleNum,
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
  
  // Convert case ID format: "K 34/14" -> "Case_K_34_14" or variations
  let possibleFileNames = [];
  
  // Original case ID format
  possibleFileNames.push(caseId);
  
  if (caseId.includes('/')) {
    // Format like "K 34/14" -> extract numbers
    const match = caseId.match(/K?\s*(\d+)\/(\d+)/i);
    if (match) {
      possibleFileNames.push(`Case_K_${match[1]}_${match[2]}`);
      possibleFileNames.push(`Case_${match[1]}_${match[2]}`);
    }
  }
  
  // Try to find the file in akomantoso_new first, then akomantoso
  const searchDirs = [
    path.join(__dirname, '../../data/cases/akomantoso_new'),
    path.join(__dirname, '../../data/cases/akomantoso')
  ];
  
  for (const dir of searchDirs) {
    if (!fs.existsSync(dir)) continue;
    
    for (const fileName of possibleFileNames) {
      const xmlPath = path.join(dir, `${fileName}.xml`);
      if (fs.existsSync(xmlPath)) {
        try {
          const xmlContent = fs.readFileSync(xmlPath, 'utf8');
          res.header('Content-Type', 'application/xml; charset=utf-8');
          return res.send(xmlContent);
        } catch (error) {
          console.error('Error reading AkomaNtoso file:', error);
          return res.status(500).json({ error: 'Error reading AkomaNtoso file' });
        }
      }
    }
  }
  
  console.warn(`AkomaNtoso file not found for case: ${caseId}`);
  return res.status(404).json({ error: 'AkomaNtoso file not found for case ' + caseId });
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

app.listen(PORT, async () => {
  console.log(`\n✅ Legal CBR Web UI running at http://localhost:${PORT}`);
  console.log(`📊 Database loaded with ${caseDatabase.length} Montenegrian cases\n`);
  
  // Auto-open browser
  try {
    const open = (await import('open')).default;
    await open(`http://localhost:${PORT}`);
    console.log('🌐 Browser opened automatically');
  } catch (err) {
    console.log('💡 Open http://localhost:' + PORT + ' in your browser');
  }
});
