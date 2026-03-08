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
app.use(express.json()); // Parse JSON request bodies

// Load case database from XML files - try akomantoso_new first, fallback to akomantoso
const casesDir = path.join(__dirname, '../data/cases/akomantoso_new');
const casesDirFallback = path.join(__dirname, '../data/cases/akomantoso');
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
    let zapisnicar = 'Nepoznat';
    let sud = 'Nepoznat';
    let kazna = 'Nepoznat';
    let tipKrivicnogDjela = '';
    let uslovnaOsuda = false;
    let novcanaKazna = '';
    let godinaRodjenja = '';
    let godinaSlucaja = '';  // Year of the case from XML
    let prebivaliste = '';
    let zaposlenost = '';
    let bracniStatus = '';
    let ranijeOsudjivan = '';
    let svjedoci = [];
    let dokazi = [];
    let iznosi = [];  // Amounts from XML
    let brojPredmeta = '';
    let vrstaPresude = '';
    let opisSlucaja = '';
    let clanKZ = '';
    
    if (proprietary) {
      // Extract Serbian proprietary fields
      const getTextContent = (tagName) => {
        const el = proprietary.getElementsByTagNameNS('*', tagName)[0];
        return el ? el.textContent.trim() : '';
      };
      
      sudija = getTextContent('sudija') || 'Nepoznat';
      zapisnicar = getTextContent('zapisnicar') || 'Nepoznat';
      sud = getTextContent('sud') || sud;
      kazna = getTextContent('kazna') || 'Nepoznat';
      tipKrivicnogDjela = getTextContent('tipKrivicnogDjela') || '';
      uslovnaOsuda = getTextContent('uslovnaOsuda') === 'Da';
      novcanaKazna = getTextContent('novcanaKazna') || '';
      godinaRodjenja = getTextContent('godinaRodjenja') || '';
      godinaSlucaja = getTextContent('godina') || '';  // Extract year from XML
      prebivaliste = getTextContent('prebivaliste') || '';
      zaposlenost = getTextContent('zaposlenost') || '';
      bracniStatus = getTextContent('bracniStatus') || '';
      ranijeOsudjivan = getTextContent('ranijeOsudjivan') || '';
      brojPredmeta = getTextContent('brojPredmeta') || '';
      vrstaPresude = getTextContent('vrstaPresude') || '';
      opisSlucaja = getTextContent('opisSlucaja') || '';
      clanKZ = getTextContent('clanKZ') || '';
      
      // Extract amounts list
      const iznosiEl = proprietary.getElementsByTagNameNS('*', 'iznosi')[0];
      if (iznosiEl) {
        const iznosEls = iznosiEl.getElementsByTagNameNS('*', 'iznos');
        for (let i = 0; i < iznosEls.length; i++) {
          iznosi.push(iznosEls[i].textContent.trim());
        }
      }
      
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
    // If brojPredmeta is "Nepoznat" or empty, derive ID from filename (e.g., Case_1_9.xml -> "1/9")
    let caseNumber = brojPredmeta;
    if (!caseNumber || caseNumber === 'Nepoznat') {
      // Try FRBRnumber first
      if (FRBRnumber && FRBRnumber.getAttribute('value')) {
        caseNumber = FRBRnumber.getAttribute('value');
      } else {
        // Derive from filename: Case_K_277_22.xml -> "K 277/22", Case_1_9.xml -> "1/9"
        const basename = path.basename(filePath, '.xml');
        const match = basename.match(/Case_(?:K_)?(\d+)_(\d+)/i);
        if (match) {
          caseNumber = basename.includes('_K_') ? `K ${match[1]}/${match[2]}` : `${match[1]}/${match[2]}`;
        } else {
          caseNumber = basename; // Use filename as-is if pattern doesn't match
        }
      }
    }
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
      // Normalize court name - map raw XML values to proper city names
      const courtMap = {
        'podgoric': 'Podgorici', 'nikši': 'Nikšiću', 'niksic': 'Nikšiću',
        'rožaj': 'Rožajama', 'rozaj': 'Rožajama', 'berana': 'Beranama',
        'bar': 'Baru', 'kotor': 'Kotoru', 'cetinj': 'Cetinju',
        'herceg': 'Herceg Novom', 'bijel': 'Bijelom Polju',
        'pljevlj': 'Pljevljima', 'plav': 'Plavu', 'ulcinj': 'Ulcinju',
        'danilovgrad': 'Danilovgradu', 'kolašin': 'Kolašinu', 'kolasin': 'Kolašinu',
      };
      const sudLower = sud.toLowerCase();
      let normalizedSud = sud;
      for (const [key, city] of Object.entries(courtMap)) {
        if (sudLower.includes(key)) {
          normalizedSud = city;
          break;
        }
      }
      court = 'Osnovni sud u ' + normalizedSud;
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
    
    // First priority: Use clanKZ from proprietary section (most reliable)
    if (clanKZ) {
      // Format: "čl. 260 st. 2" or "Član 258" etc.
      articles.push(clanKZ);
    }
    
    // Fallback: Check TLCReference elements
    if (articles.length === 0) {
      for (let i = 0; i < references.length; i++) {
        const ref = references[i];
        const showAs = ref.getAttribute('showAs');
        if (showAs && (showAs.includes('Član') || showAs.includes('члан') || showAs.includes('Clan') || showAs.includes('čl.'))) {
          articles.push(showAs);
        }
      }
    }
    
    // Additional fallback: Derive article from crime type
    if (articles.length === 0 && tipKrivicnogDjela) {
      const lowerType = tipKrivicnogDjela.toLowerCase();
      if (lowerType.includes('kreditn') || lowerType.includes('kartic')) {
        articles.push('čl. 260 KZ'); // Credit card fraud
      } else if (lowerType.includes('novca') || lowerType.includes('novac')) {
        articles.push('čl. 258 KZ'); // Money counterfeiting
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
      if (vp === 'kriv' || vp === 'kriva') {
        verdict = 'KRIV';
      } else if (vp === 'osuđujuća' || vp === 'osuđujuca' || vp.includes('osuđujuć')) {
        verdict = 'OSUĐUJUĆA';  // Convicting verdict - keep separate for stats
      } else if (vp === 'oslobađajuća' || vp === 'oslobadjajuca' || vp.includes('oslob')) {
        verdict = 'OSLOBAĐAJUĆA';
      } else if (vp === 'uslovna osuda' || vp.includes('uslovna')) {
        verdict = 'USLOVNA PRESUDA';  // Conditional/suspended sentence
      } else if (vp === 'sudska opomena' || vp.includes('opomena')) {
        verdict = 'SUDSKA OPOMENA';  // Judicial warning
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
      sentenceText = 'Uslovna presuda';
    }
    
    // Extract year - prefer godina from XML, fallback to case number parsing
    let year = 2024;
    if (godinaSlucaja && /^\d{4}$/.test(godinaSlucaja)) {
      year = parseInt(godinaSlucaja);
    } else {
      const yearMatch = caseNumber.match(/\/(\d+)/);
      if (yearMatch) {
        const parsedYear = parseInt(yearMatch[1]);
        // Handle both 2-digit (K 4/19) and 4-digit (K 4/2019) year formats
        if (parsedYear > 99 && parsedYear < 2100) {
          year = parsedYear; // Already 4-digit year
        } else if (parsedYear <= 99) {
          year = (parsedYear <= 30 ? 2000 : 1900) + parsedYear;
        }
        // If parsedYear > 2100, it's likely a case number not a year - use default
      }
    }
    
    // Also try to extract year from FRBRdate if still default
    if (year === 2024) {
      const frbrdateEl = meta.getElementsByTagNameNS('*', 'FRBRdate')[0];
      if (frbrdateEl) {
        const dateAttr = frbrdateEl.getAttribute('date');
        if (dateAttr) {
          const dateYear = parseInt(dateAttr.substring(0, 4));
          if (dateYear > 1990 && dateYear < 2100) {
            year = dateYear;
          }
        }
      }
    }
    
    // Calculate total amount from iznosi
    let totalAmount = 0;
    for (const iznos of iznosi) {
      const match = iznos.match(/([\d.,]+)\s*EUR/i);
      if (match) {
        totalAmount += parseFloat(match[1].replace(',', '.'));
      }
    }
    
    // Build evidence string from dokazi array
    let evidenceStr = 'Nije navedeno';
    if (dokazi.length > 0) {
      evidenceStr = dokazi.join('; ');
    }
    
    return {
      id: caseNumber,
      caseNumber: caseNumber, // Alias for frontend compatibility
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
      zapisnicar: zapisnicar,
      uslovnaOsuda: uslovnaOsuda,
      novcanaKazna: novcanaKazna,
      godinaRodjenja: godinaRodjenja,
      prebivaliste: prebivaliste,
      zaposlenost: zaposlenost,
      bracniStatus: bracniStatus,
      ranijeOsudjivan: ranijeOsudjivan,
      svjedoci: svjedoci,
      dokazi: dokazi,
      clanKZ: clanKZ,
      iznosi: iznosi,
      totalAmount: totalAmount,
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
      caseNumber: 'K 05/1336',
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
  // Count different verdict types
  const krivCount = caseDatabase.filter(c => c.verdict === 'KRIV').length;
  const osudjujucaCount = caseDatabase.filter(c => c.verdict === 'OSUĐUJUĆA').length;
  const uslovnaCount = caseDatabase.filter(c => c.verdict === 'USLOVNA PRESUDA' || c.verdict === 'USLOVNA OSUDA').length;
  const oslobodjenCount = caseDatabase.filter(c => c.verdict === 'OSLOBAĐAJUĆA' || c.verdict === 'OSLOBOĐEN').length;
  const opomenaCount = caseDatabase.filter(c => c.verdict === 'SUDSKA OPOMENA').length;
  
  const stats = {
    totalCases: caseDatabase.length,
    guiltyCount: krivCount + osudjujucaCount,  // Combined guilty verdicts
    conditionalCount: uslovnaCount,  // Suspended sentences (technically guilty but no prison)
    acquittedCount: oslobodjenCount,
    opomenaCount: opomenaCount,  // Judicial warning count
    // Detailed breakdown
    krivCount: krivCount,
    osudjujucaCount: osudjujucaCount,
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
  const glava23Path = path.join(__dirname, '../data/glava23/criminal_code.xml');
  
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
  const caseDir = path.join(__dirname, '../data/cases/akomantoso');
  
  // Find the case file by searching for matching case_id in database
  const caseRecord = caseDatabase.find(c => c.id === caseId);
  
  if (caseRecord && caseRecord.xmlFile) {
    try {
      const xmlContent = fs.readFileSync(caseRecord.xmlFile, 'utf8');
      res.header('Content-Type', 'application/xml; charset=utf-8');
      return res.send(xmlContent);
    } catch (error) {
      console.error('Error reading AkomaNtoso file:', error);
      return res.status(500).json({ error: 'Error reading AkomaNtoso file' });
    }
  }
  
  // Fallback: try different formats
  let possibleFileNames = [];
  possibleFileNames.push(caseId);
  
  if (caseId.includes('/')) {
    const match = caseId.match(/(\d+)\/(\d+)/);
    if (match) {
      possibleFileNames.push(`K ${match[1]}_${match[2]}`);
      possibleFileNames.push(`K_${match[1]}_${match[2]}`);
    }
  }
  
  for (const fileName of possibleFileNames) {
    const xmlPath = path.join(caseDir, `${fileName}.xml`);
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

// Reasoning API endpoint
app.post('/api/reasoning', async (req, res) => {
  const { caseId, facts } = req.body;
  
  if (!caseId && !facts) {
    return res.status(400).json({ error: 'Either caseId or facts required' });
  }

  try {
    const { spawn } = require('child_process');
    const projectRoot = path.join(__dirname, '..');
    
    let pythonArgs;
    if (caseId) {
      // Find the case XML file - match by id, caseNumber, or case_id
      const caseRecord = caseDatabase.find(c => 
        c.id === caseId || 
        c.caseNumber === caseId || 
        c.case_id === caseId
      );
      if (!caseRecord || !caseRecord.xmlFile) {
        return res.status(404).json({ error: 'Case not found or no Akoma Ntoso file', searchedId: caseId });
      }
      pythonArgs = ['scripts/demo_reasoning.py', '--case', caseRecord.xmlFile, '--json'];
    } else {
      // Pass facts directly to reasoning engine
      pythonArgs = ['scripts/demo_reasoning.py', '--facts', JSON.stringify(facts), '--json'];
    }

    const pythonProcess = spawn('py', pythonArgs, { cwd: projectRoot });
    
    let stdout = '';
    let stderr = '';
    
    pythonProcess.stdout.on('data', (data) => { stdout += data.toString(); });
    pythonProcess.stderr.on('data', (data) => { stderr += data.toString(); });
    
    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('Reasoning error:', stderr);
        return res.status(500).json({ error: 'Reasoning failed', details: stderr });
      }
      
      try {
        // Find JSON in output (between first { and last })
        const jsonMatch = stdout.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const result = JSON.parse(jsonMatch[0]);
          res.json(result);
        } else {
          res.json({ raw_output: stdout });
        }
      } catch (parseError) {
        res.json({ raw_output: stdout });
      }
    });
    
    pythonProcess.on('error', (err) => {
      res.status(500).json({ error: 'Failed to start reasoning engine', details: err.message });
    });
    
  } catch (error) {
    console.error('Reasoning error:', error);
    res.status(500).json({ error: error.message });
  }
});

// =============================================
// CBR Similarity Reasoning (Case-Based Reasoning)
// =============================================

// Load CBR case base from CSV
const cbrCsvPath = path.join(__dirname, '../case_reasoning/presude-cbr/src/main/resources/presude.csv');
let cbrCases = [];

function loadCbrCases() {
  try {
    if (!fs.existsSync(cbrCsvPath)) {
      console.warn('⚠️  CBR CSV not found at', cbrCsvPath);
      return;
    }
    const csvContent = fs.readFileSync(cbrCsvPath, 'utf8');
    const lines = csvContent.trim().split('\n');
    if (lines.length < 2) return;
    
    // Parse header (skip # prefix)
    const header = lines[0].replace(/^#\s*/, '').split(';');
    
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(';');
      if (values.length < header.length) continue;
      const row = {};
      for (let j = 0; j < header.length; j++) {
        row[header[j].trim()] = values[j]?.trim() || '';
      }
      cbrCases.push(row);
    }
    console.log(`📋 CBR case base loaded: ${cbrCases.length} cases`);
  } catch (err) {
    console.error('Error loading CBR CSV:', err.message);
  }
}
loadCbrCases();

// Similarity functions for different attribute types
function exactMatch(a, b) {
  if (!a || !b || a === 'nepoznat' || b === 'nepoznat') return 0.5;
  return a.toLowerCase() === b.toLowerCase() ? 1.0 : 0.0;
}

// Format city name to full court name "Osnovni sud u [city]"
function formatCourtName(city) {
  if (!city) return 'Nepoznat';
  const cityMap = {
    'rožaje': 'Rožajama', 'rozaje': 'Rožajama',
    'podgorica': 'Podgorici', 'podgoric': 'Podgorici',
    'nikšić': 'Nikšiću', 'niksic': 'Nikšiću',
    'bar': 'Baru',
    'kotor': 'Kotoru',
    'cetinje': 'Cetinju', 'cetinj': 'Cetinju',
    'herceg novi': 'Herceg Novom', 'herceg': 'Herceg Novom',
    'bijelo polje': 'Bijelom Polju', 'bijel': 'Bijelom Polju',
    'pljevlja': 'Pljevljima', 'pljevlj': 'Pljevljima',
    'plav': 'Plavu',
    'ulcinj': 'Ulcinju',
    'danilovgrad': 'Danilovgradu',
    'kolašin': 'Kolašinu', 'kolasin': 'Kolašinu',
    'berane': 'Beranama', 'berana': 'Beranama',
  };
  const cityLower = city.toLowerCase().trim();
  for (const [key, locative] of Object.entries(cityMap)) {
    if (cityLower.includes(key)) {
      return 'Osnovni sud u ' + locative;
    }
  }
  return 'Osnovni sud u ' + city;
}

// Map CBR verdict labels to display labels
function displayVerdict(vrstaPresude) {
  if (!vrstaPresude) return 'nepoznat';
  const v = vrstaPresude.toLowerCase().trim();
  if (v === 'osudjujuca' || v === 'osuđujuća' || v === 'osuđujuca') return 'zatvorska kazna';
  if (v === 'uslovna' || v === 'uslovna osuda') return 'uslovna presuda';
  if (v === 'oslobadjajuca' || v === 'oslobađajuća' || v === 'oslobađajuca') return 'oslobadjajuca';
  return vrstaPresude;
}

function numericSimilarity(a, b, maxDiff) {
  const na = parseFloat(a), nb = parseFloat(b);
  if (isNaN(na) || isNaN(nb)) return 0.5;
  const diff = Math.abs(na - nb);
  return Math.max(0, 1.0 - diff / maxDiff);
}

function booleanSimilarity(a, b) {
  if (!a || !b || a === 'nepoznat' || b === 'nepoznat') return 0.5;
  return a.toLowerCase() === b.toLowerCase() ? 1.0 : 0.0;
}

// Compute weighted similarity between two CBR case records
function computeSimilarity(queryCase, targetCase) {
  const weights = {
    tipKrivicnogDjela: 5.0,
    clanKZ: 4.0,
    ranijeOsudjivan: 3.0,
    priznanje: 3.0,
    pokusaj: 2.5,
    saizvrsilastvo: 2.0,
    zaposlenost: 1.5,
    bracniStatus: 1.0,
    obrazovanje: 1.0,
    iznos: 10.0,
    ukupanIznos: 10.0,
    brojTransakcija: 1.5,
    brojOkrivljenih: 1.0,
    brojSvjedoka: 1.0,
    brojDokaza: 1.5,
  };

  let totalWeight = 0;
  let weightedSum = 0;

  // Categorical attributes
  for (const attr of ['tipKrivicnogDjela', 'clanKZ', 'zaposlenost', 'bracniStatus', 'obrazovanje']) {
    const w = weights[attr] || 1.0;
    totalWeight += w;
    weightedSum += w * exactMatch(queryCase[attr], targetCase[attr]);
  }

  // Boolean attributes
  for (const attr of ['ranijeOsudjivan', 'priznanje', 'pokusaj', 'saizvrsilastvo']) {
    const w = weights[attr] || 1.0;
    totalWeight += w;
    weightedSum += w * booleanSimilarity(queryCase[attr], targetCase[attr]);
  }

  // Numeric attributes
  const numericConfigs = [
    ['iznos', 10000], ['ukupanIznos', 50000], ['brojTransakcija', 50],
    ['brojOkrivljenih', 10], ['brojSvjedoka', 10], ['brojDokaza', 30],
  ];
  for (const [attr, maxDiff] of numericConfigs) {
    const w = weights[attr] || 1.0;
    totalWeight += w;
    weightedSum += w * numericSimilarity(queryCase[attr], targetCase[attr], maxDiff);
  }

  return totalWeight > 0 ? weightedSum / totalWeight : 0;
}

app.post('/api/cbr-reasoning', (req, res) => {
  const { caseId } = req.body;
  if (!caseId) {
    return res.status(400).json({ error: 'caseId is required' });
  }
  if (cbrCases.length === 0) {
    return res.status(500).json({ error: 'CBR baza slučajeva nije učitana' });
  }

  // Find the query case in the case database
  const caseRecord = caseDatabase.find(c =>
    c.id === caseId || c.caseNumber === caseId || c.case_id === caseId
  );
  if (!caseRecord) {
    return res.status(404).json({ error: 'Predmet nije pronađen' });
  }

  // Match query case to CBR CSV entry by case number
  const queryBroj = caseRecord.caseNumber || caseRecord.case_number || '';
  let queryCase = cbrCases.find(c => c.brojPredmeta === queryBroj);
  
  // Fallback: match by id
  if (!queryCase) {
    queryCase = cbrCases.find(c => c.id === String(caseRecord.csvIndex));
  }
  
  // Fallback: build query from parsed XML fields if no CSV match
  if (!queryCase) {
    queryCase = {
      tipKrivicnogDjela: caseRecord.crimeType || '',
      clanKZ: caseRecord.article || '',
      ranijeOsudjivan: caseRecord.priorConvictions || 'nepoznat',
      zaposlenost: caseRecord.employment || 'nepoznat',
      bracniStatus: caseRecord.maritalStatus || 'nepoznat',
      obrazovanje: caseRecord.education || 'nepoznat',
      iznos: String(caseRecord.amount || 0),
      ukupanIznos: String(caseRecord.totalAmount || 0),
      brojTransakcija: '0',
      brojOkrivljenih: '1',
      brojSvjedoka: '0',
      brojDokaza: '0',
      priznanje: 'nepoznat',
      pokusaj: 'ne',
      saizvrsilastvo: 'ne',
    };
  }

  // Compute similarity to all other cases
  const results = [];
  for (const target of cbrCases) {
    if (target.brojPredmeta === queryBroj) continue; // skip self
    const similarity = computeSimilarity(queryCase, target);
    results.push({ case: target, similarity });
  }

  // Sort by similarity descending, get top 5
  results.sort((a, b) => b.similarity - a.similarity);
  const topK = 5;
  const similarCases = results.slice(0, topK).map(r => ({
    brojPredmeta: r.case.brojPredmeta,
    sud: formatCourtName(r.case.sud),
    tipKrivicnogDjela: r.case.tipKrivicnogDjela,
    clanKZ: r.case.clanKZ,
    vrstaPresude: displayVerdict(r.case.vrstaPresude),
    kaznaUMjesecima: parseFloat(r.case.kaznaUMjesecima) || 0,
    uslovnaOsuda: r.case.uslovnaOsuda,
    novcanaKazna: parseFloat(r.case.novcanaKazna) || 0,
    iznos: parseFloat(r.case.iznos) || 0,
    ukupanIznos: parseFloat(r.case.ukupanIznos) || 0,
    ranijeOsudjivan: r.case.ranijeOsudjivan,
    priznanje: r.case.priznanje,
    zaposlenost: r.case.zaposlenost,
    bracniStatus: r.case.bracniStatus,
    obrazovanje: r.case.obrazovanje,
    brojTransakcija: parseInt(r.case.brojTransakcija) || 0,
    brojOkrivljenih: parseInt(r.case.brojOkrivljenih) || 0,
    brojSvjedoka: parseInt(r.case.brojSvjedoka) || 0,
    brojDokaza: parseInt(r.case.brojDokaza) || 0,
    pokusaj: r.case.pokusaj,
    saizvrsilastvo: r.case.saizvrsilastvo,
    similarity: Math.round(r.similarity * 1000) / 10, // percentage with 1 decimal
  }));

  // Compute recommended sentence from weighted average of similar cases
  let weightedSentence = 0, weightSum = 0;
  for (const r of results.slice(0, topK)) {
    const months = parseFloat(r.case.kaznaUMjesecima) || 0;
    if (months > 0) {
      weightedSentence += r.similarity * months;
      weightSum += r.similarity;
    }
  }
  const recommendedMonths = weightSum > 0 ? Math.round(weightedSentence / weightSum * 10) / 10 : null;

  // Count verdict types in similar cases
  const verdictCounts = {};
  for (const sc of similarCases) {
    const v = sc.vrstaPresude || 'nepoznato';
    verdictCounts[v] = (verdictCounts[v] || 0) + 1;
  }

  // Determine if conditional sentence is likely
  const conditionalCount = similarCases.filter(sc => sc.uslovnaOsuda === 'Da').length;

  // Get the actual sentence of the query case
  const actualSentenceMonths = parseFloat(queryCase.kaznaUMjesecima) || 0;
  const actualUslovnaOsuda = queryCase.uslovnaOsuda || 'nepoznat';
  const actualVrstaPresude = queryCase.vrstaPresude || 'nepoznat';
  const actualNovcanaKazna = parseFloat(queryCase.novcanaKazna) || 0;

  // Build explanation for conditional sentence likelihood
  const conditionalNames = similarCases.filter(sc => sc.uslovnaOsuda === 'Da').map(sc => sc.brojPredmeta);
  const nonConditionalNames = similarCases.filter(sc => sc.uslovnaOsuda !== 'Da').map(sc => sc.brojPredmeta);
  const conditionalExplanation = `Od ${topK} najsličnijih predmeta, ${conditionalCount} ${conditionalCount === 1 ? 'je imao' : 'su imali'} uslovnu presudu` +
    (conditionalNames.length > 0 ? ` (${conditionalNames.join(', ')})` : '') +
    ` a ${topK - conditionalCount} ${topK - conditionalCount === 1 ? 'nije' : 'nisu'}` +
    (nonConditionalNames.length > 0 ? ` (${nonConditionalNames.join(', ')})` : '') +
    `. Verovatnoća = ${conditionalCount}/${topK} = ${Math.round(conditionalCount / topK * 100)}%.`;

  res.json({
    queryCase: {
      brojPredmeta: queryBroj,
      tipKrivicnogDjela: queryCase.tipKrivicnogDjela,
      clanKZ: queryCase.clanKZ,
      kaznaUMjesecima: actualSentenceMonths,
      uslovnaOsuda: actualUslovnaOsuda,
      vrstaPresude: displayVerdict(actualVrstaPresude),
      novcanaKazna: actualNovcanaKazna,
      ranijeOsudjivan: queryCase.ranijeOsudjivan || 'nepoznat',
      zaposlenost: queryCase.zaposlenost || 'nepoznat',
      priznanje: queryCase.priznanje || 'nepoznat',
    },
    similarCases,
    recommendation: {
      kaznaUMjesecima: recommendedMonths,
      verdictDistribution: verdictCounts,
      conditionalSentenceLikelihood: Math.round(conditionalCount / topK * 100),
      conditionalExplanation,
    },
    totalCasesCompared: results.length,
  });
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
