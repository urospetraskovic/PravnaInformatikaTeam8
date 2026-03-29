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
const userCasesFile = path.join(__dirname, '../data/cases/user_cases.json');
let caseDatabase = [];

function normalizeLegalArticleText(value) {
  return String(value || '')
    .replace(/član/gi, 'čl.')
    .replace(/clan/gi, 'čl.')
    .replace(/cl\./gi, 'čl.')
    .replace(/stav/gi, 'st.')
    .replace(/\s+/g, ' ')
    .trim();
}

function pickMainArticleByCrimeType(typeText) {
  const value = String(typeText || '').toLowerCase();
  if (value.includes('kreditn') || value.includes('kartic') || value.includes('bezgotovinsk')) return 260;
  if (value.includes('novca') || value.includes('novac')) return 258;
  return null;
}

function extractCanonicalArticleRef(rawText, forcedMainArticle = null) {
  const text = normalizeLegalArticleText(rawText);
  if (!text) return null;

  let article = null;
  let stav = null;
  
  // Directly match 258.4 or 260.2 format
  const dotMatch = text.match(/\b(258|260)\.(\d{1,2})\b/);
  if (dotMatch) {
    article = parseInt(dotMatch[1], 10);
    stav = parseInt(dotMatch[2], 10);
  } else {
    const explicitArticle = text.match(/(?:čl\.?)\s*(\d{2,3})/i);
    if (explicitArticle) {
      article = parseInt(explicitArticle[1], 10);
    }
  
    if (!article) {
      const safeArticle = text.match(/\b(258|260)\b/);
      if (safeArticle) {
        article = parseInt(safeArticle[1], 10);
      }
    }
  }

  if (!article && forcedMainArticle) {
    article = forcedMainArticle;
  }
  if (!article) return null;

  if (article !== 258 && article !== 260) {
    return null;
  }

  if (!stav) {
    const explicitStav = text.match(/(?:st\.?)\s*(\d{1,2})/i);
    if (explicitStav) {
      stav = parseInt(explicitStav[1], 10);
    }
  }

  // Handles broken OCR-like forms such as "258. čl. 2".
  if (!stav) {
    const brokenPattern = text.match(/\b(258|260)\b[^\d]{0,12}čl\.?\s*(\d{1,2})/i);
    if (brokenPattern) {
      stav = parseInt(brokenPattern[2], 10);
    }
  }

  if (!stav) {
    const numbers = (text.match(/\d+/g) || []).map((n) => parseInt(n, 10));
    if (numbers.length >= 2 && (numbers[0] === 258 || numbers[0] === 260) && numbers[1] > 0 && numbers[1] <= 10) {
      stav = numbers[1];
    }
  }

  const label = stav ? `${article}.${stav}` : `${article}`;
  return { article, stav, label };
}

function buildAppliedArticles({ clanKZ, tipKrivicnogDjela, references = [], bodyRefs = [], decisionPs = [] }) {
  const forcedMainArticle = pickMainArticleByCrimeType(tipKrivicnogDjela);
  const candidates = [];

  if (clanKZ) {
    candidates.push(clanKZ);
  }

  for (let i = 0; i < (references ? references.length : 0); i++) {
    const ref = references[i];
    const showAs = ref && ref.getAttribute ? ref.getAttribute('showAs') : '';
    if (showAs) candidates.push(showAs);
  }

  for (let i = 0; i < (bodyRefs ? bodyRefs.length : 0); i++) {
    const ref = bodyRefs[i];
    const href = (ref && ref.getAttribute ? ref.getAttribute('href') : '') || '';
    const hrefMatch = href.match(/art_(\d+)(?:__para_(\d+))?/i);
    if (hrefMatch) {
      const article = parseInt(hrefMatch[1], 10);
      const stav = hrefMatch[2] ? parseInt(hrefMatch[2], 10) : null;
      if (article === 258 || article === 260) {
        candidates.push(stav ? `${article}.${stav}` : `${article}`);
      }
    }
  }

  for (let i = 0; i < (decisionPs ? decisionPs.length : 0); i++) {
    const p = decisionPs[i];
    const text = (p && p.textContent) ? p.textContent : '';
    if (text) candidates.push(text);
  }

  const seen = new Set();
  const result = [];

  for (const candidate of candidates) {
    const parsed = extractCanonicalArticleRef(candidate, forcedMainArticle);
    if (!parsed) continue;
    const key = `${parsed.article}-${parsed.stav || 0}`;
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(parsed.label);
  }

  if (result.length === 0 && forcedMainArticle) {
    result.push(`${forcedMainArticle}`);
  }

  return result;
}

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
    
    // Get article references and normalize them to exact "čl. X st. Y" when possible.
    const references = meta.getElementsByTagNameNS('*', 'TLCReference');
    const bodyRefs = body.getElementsByTagNameNS('*', 'ref');
    
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

    const articles = buildAppliedArticles({
      clanKZ,
      tipKrivicnogDjela,
      references,
      bodyRefs,
      decisionPs,
    });
    
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
      const paragraphItems = [];
      
      for (let j = 0; j < paragraphs.length; j++) {
        const paragraph = paragraphs[j];
        const paraNum = paragraph.getElementsByTagNameNS('*', 'num')[0]?.textContent?.trim() || '';
        const pNodes = paragraph.getElementsByTagNameNS('*', 'p');
        const paraId = paragraph.getAttribute('eId') || (eId ? `${eId}__para_${j + 1}` : `para_${j + 1}`);

        if (pNodes.length > 0) {
          const paraTextParts = [];
          for (let k = 0; k < pNodes.length; k++) {
            const text = (pNodes[k].textContent || '').trim();
            if (text) {
              paraTextParts.push(text);
              content.push(paraNum ? `${paraNum} ${text}` : text);
            }
          }
          const paraText = paraTextParts.join(' ').trim();
          if (paraText) {
            paragraphItems.push({ eId: paraId, num: paraNum, text: paraText });
          }
          continue;
        }

        // Fallback for paragraphs that do not use explicit <p> nodes.
        const rawText = (paragraph.textContent || '').trim();
        if (rawText) {
          content.push(rawText);
          paragraphItems.push({ eId: paraId, num: paraNum, text: rawText });
        }
      }
      
      articles.push({
        eId: eId,
        num: articleNum,
        heading: heading,
        paragraphs: paragraphItems,
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
app.get('/api/akomantoso/:caseId(*)', (req, res) => {
  const caseId = decodeURIComponent(req.params.caseId || '');
  const caseDir = path.join(__dirname, '../data/cases/akomantoso');
  
  // Find the case file by searching for matching id formats in database
  const caseRecord = caseDatabase.find(c =>
    c.id === caseId ||
    c.caseNumber === caseId ||
    c.case_id === caseId
  );
  
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

      // Handle short year IDs like 109/13 -> K 109_2013.xml
      if (match[2].length === 2) {
        const fullYear = `20${match[2]}`;
        possibleFileNames.push(`K ${match[1]}_${fullYear}`);
        possibleFileNames.push(`K_${match[1]}_${fullYear}`);
      }
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

function loadUserCbrCases() {
  try {
    if (!fs.existsSync(userCasesFile)) return;
    const raw = fs.readFileSync(userCasesFile, 'utf8');
    const stored = JSON.parse(raw);
    if (!Array.isArray(stored)) return;

    for (const entry of stored) {
      if (entry && entry.cbrRecord) {
        cbrCases.push(entry.cbrRecord);
      }
    }
    if (stored.length > 0) {
      console.log(`🧠 Loaded ${stored.length} user-entered cases into CBR memory`);
    }
  } catch (err) {
    console.error('Error loading user-entered cases:', err.message);
  }
}
loadUserCbrCases();

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

function normalizeCbrQuery(raw = {}) {
  return {
    brojPredmeta: String(raw.brojPredmeta || `NOVI-${Date.now()}`),
    tipKrivicnogDjela: String(raw.tipKrivicnogDjela || ''),
    clanKZ: String(raw.clanKZ || ''),
    iznos: String(raw.iznos ?? 0),
    ukupanIznos: String(raw.ukupanIznos ?? raw.iznos ?? 0),
    ranijeOsudjivan: String(raw.ranijeOsudjivan || 'nepoznat'),
    uslovnaOsuda: String(raw.uslovnaOsuda || 'Ne'),
    vrstaPresude: String(raw.vrstaPresude || 'nepoznat'),
    zaposlenost: String(raw.zaposlenost || 'nepoznat'),
    bracniStatus: String(raw.bracniStatus || 'nepoznat'),
    kaznaUMjesecima: String(raw.kaznaUMjesecima ?? 0),
    novcanaKazna: String(raw.novcanaKazna ?? 0),
    obrazovanje: String(raw.obrazovanje || 'nepoznat'),
    brojTransakcija: String(raw.brojTransakcija ?? 0),
    brojOkrivljenih: String(raw.brojOkrivljenih ?? 1),
    brojSvjedoka: String(raw.brojSvjedoka ?? 0),
    brojDokaza: String(raw.brojDokaza ?? 0),
    priznanje: String(raw.priznanje || 'ne'),
    pokusaj: String(raw.pokusaj || 'ne'),
    saizvrsilastvo: String(raw.saizvrsilastvo || 'ne'),
  };
}

function escapeXml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function parseCaseIdentity(rawCaseNumber = '') {
  const now = new Date();
  const fallbackYear = now.getFullYear();
  const raw = String(rawCaseNumber || '').trim();

  let broj = '';
  let year = fallbackYear;

  let match = raw.match(/(\d+)\s*\/\s*(\d{2,4})/);
  if (!match) {
    match = raw.match(/(\d+)[^\d]+(\d{2,4})/);
  }

  if (match) {
    broj = match[1];
    const parsedYear = parseInt(match[2], 10);
    if (!Number.isNaN(parsedYear)) {
      if (parsedYear > 99 && parsedYear < 2100) {
        year = parsedYear;
      } else if (parsedYear <= 99) {
        year = (parsedYear <= 30 ? 2000 : 1900) + parsedYear;
      }
    }
  } else {
    const digits = raw.match(/\d+/);
    broj = digits ? digits[0] : String(now.getTime()).slice(-6);
  }

  if (!broj) {
    broj = String(now.getTime()).slice(-6);
  }

  return {
    broj,
    year,
    fileBase: `K ${broj}_${year}`,
    judgmentName: `K_${broj}_${year}`,
    fallbackCaseNumber: `${broj}/${String(year).slice(-2)}`,
  };
}

function normalizeVerdictLabel(vrstaPresude = '') {
  const v = String(vrstaPresude || '').toLowerCase().trim();
  if (v === 'uslovna' || v === 'uslovna osuda' || v === 'uslovna presuda') return 'Uslovna presuda';
  if (v === 'oslobadjajuca' || v === 'oslobađajuća' || v === 'oslobađajuca') return 'Oslobađajuća';
  if (v === 'osudjujuca' || v === 'osuđujuća' || v === 'osuđujuca') return 'Osuđujuća';
  if (v === 'sudska opomena' || v === 'opomena') return 'Sudska opomena';
  return 'Osuđujuća';
}

function formatSentence(decision = {}) {
  const months = parseFloat(decision.kaznaUMjesecima);
  const fine = parseFloat(decision.novcanaKazna);

  if (!Number.isNaN(months) && months > 0) {
    const n = Number.isInteger(months) ? String(months) : String(months);
    return `${n} mjeseci`;
  }
  if (!Number.isNaN(fine) && fine > 0) {
    return `novčana kazna ${fine} EUR`;
  }
  return 'Nije navedeno';
}

function buildAkomaNtosoCaseXml(input, decision, identity) {
  const now = new Date();
  const inputDate = String(input.datumPresude || '').trim();
  const isoDate = /^\d{4}-\d{2}-\d{2}$/.test(inputDate) ? inputDate : now.toISOString().slice(0, 10);
  const caseNumber = String(input.brojPredmeta || identity.fallbackCaseNumber);
  const verdict = normalizeVerdictLabel(decision.vrstaPresude);
  const sentence = formatSentence(decision);
  const uslovna = String(decision.uslovnaOsuda || 'Ne');
  const sudMjesto = String(input.sud || 'Podgorici').trim();
  const sudLabel = `Osnovni Sud u ${sudMjesto}`;
  const tipDjela = String(input.tipKrivicnogDjela || '').trim();
  const clanKZ = String(input.clanKZ || '').trim();
  const opis = String(input.opis || 'Nije navedeno').trim();
  const zaposlenost = String(input.zaposlenost || 'nepoznat');
  const obrazovanje = String(input.obrazovanje || 'nepoznat');
  const ranijeOsudjivan = String(input.ranijeOsudjivan || 'nepoznat');
  const bracniStatus = String(input.bracniStatus || 'nepoznat');
  const sudija = String(input.sudija || 'Korisnički unos').trim();
  const zapisnicar = String(input.zapisnicar || 'Korisnički unos').trim();
  const okrivljeni = String(input.okrivljeni || 'Korisnički unos').trim();
  const brojTransakcija = parseInt(input.brojTransakcija ?? 0, 10);
  const brojOkrivljenih = parseInt(input.brojOkrivljenih ?? 1, 10);
  const brojSvjedoka = parseInt(input.brojSvjedoka ?? 0, 10);
  const brojDokaza = parseInt(input.brojDokaza ?? 0, 10);
  const ukupanIznos = parseFloat(input.ukupanIznos ?? input.iznos ?? 0);
  const fine = parseFloat(decision.novcanaKazna ?? 0);
  const cleanUkupanIznos = Number.isNaN(ukupanIznos) ? 0 : ukupanIznos;
  const cleanFine = Number.isNaN(fine) ? 0 : fine;

  const parseListInput = (value) =>
    String(value || '')
      .split(/\r?\n|;/)
      .map((item) => item.trim())
      .filter(Boolean);

  const witnessList = parseListInput(input.svjedoci);
  const evidenceList = parseListInput(input.dokazi);

  const computedWitnesses = witnessList.length > 0
    ? witnessList
    : Array.from({ length: Math.max(0, Number.isNaN(brojSvjedoka) ? 0 : brojSvjedoka) }, (_, idx) => `Svjedok ${idx + 1}`);

  const computedEvidence = evidenceList.length > 0
    ? evidenceList
    : Array.from({ length: Math.max(0, Number.isNaN(brojDokaza) ? 0 : brojDokaza) }, (_, idx) => `Dokaz ${idx + 1}`);

  const witnessXml = computedWitnesses.length > 0
    ? computedWitnesses.map((name) => `          <svjedok>${escapeXml(name)}</svjedok>`).join('\n')
    : '          <svjedok>Nije navedeno</svjedok>';

  const evidenceXml = computedEvidence.length > 0
    ? computedEvidence.map((item) => `          <dokaz>${escapeXml(item)}</dokaz>`).join('\n')
    : '          <dokaz>Nije navedeno</dokaz>';

  const motivationEvidenceXml = computedEvidence.length > 0
    ? computedEvidence.map((item) => `            <p>• ${escapeXml(item)}</p>`).join('\n')
    : '            <p>• Nije navedeno</p>';

  return `<?xml version="1.0" encoding="utf-8"?>
<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <judgment name="${escapeXml(identity.judgmentName)}">
    <meta>
      <identification source="#court">
        <FRBRWork>
          <FRBRthis value="/akn/me/judgment/${escapeXml(identity.judgmentName)}"/>
          <FRBRuri value="/akn/me/judgment/${escapeXml(identity.judgmentName)}"/>
          <FRBRdate date="${escapeXml(isoDate)}" name="judgment"/>
          <FRBRauthor href="#court"/>
          <FRBRcountry value="me"/>
        </FRBRWork>
        <FRBRExpression>
          <FRBRthis value="/akn/me/judgment/${escapeXml(identity.judgmentName)}/srp@${escapeXml(isoDate)}"/>
          <FRBRuri value="/akn/me/judgment/${escapeXml(identity.judgmentName)}/srp@${escapeXml(isoDate)}"/>
          <FRBRdate date="${escapeXml(isoDate)}" name="judgment"/>
          <FRBRauthor href="#court"/>
          <FRBRlanguage language="srp"/>
        </FRBRExpression>
        <FRBRManifestation>
          <FRBRthis value="/akn/me/judgment/${escapeXml(identity.judgmentName)}/srp@${escapeXml(isoDate)}.xml"/>
          <FRBRuri value="/akn/me/judgment/${escapeXml(identity.judgmentName)}/srp@${escapeXml(isoDate)}.xml"/>
          <FRBRdate date="${escapeXml(isoDate)}" name="generation"/>
          <FRBRauthor href="#system"/>
        </FRBRManifestation>
      </identification>
      <references source="#court">
        <TLCOrganization eId="court" href="/ontology/organization/me/${escapeXml(sudMjesto.toLowerCase().replace(/\s+/g, '_'))}" showAs="${escapeXml(sudLabel)}"/>
        <TLCPerson eId="sudija" href="/ontology/person/sudija_korisnicki_unos" showAs="${escapeXml(sudija)}"/>
        <TLCPerson eId="zapisnicar" href="/ontology/person/zapisnicar_korisnicki_unos" showAs="${escapeXml(zapisnicar)}"/>
        <TLCPerson eId="defendant" href="/ontology/person/okrivljeni_korisnicki_unos" showAs="${escapeXml(okrivljeni)}"/>
      </references>
      <proprietary source="#court">
        <sud>${escapeXml(sudMjesto)}</sud>
        <brojPredmeta>${escapeXml(caseNumber)}</brojPredmeta>
        <datum>${escapeXml(isoDate)}</datum>
        <datumNormalizovan>${escapeXml(isoDate)}</datumNormalizovan>
        <godina>${identity.year}</godina>
        <sudija>${escapeXml(sudija)}</sudija>
        <zapisnicar>${escapeXml(zapisnicar)}</zapisnicar>
        <okrivljeni>${escapeXml(okrivljeni)}</okrivljeni>
        <zaposlenost>${escapeXml(zaposlenost)}</zaposlenost>
        <obrazovanje>${escapeXml(obrazovanje)}</obrazovanje>
        <ranijeOsudjivan>${escapeXml(ranijeOsudjivan)}</ranijeOsudjivan>
        <tipKrivicnogDjela>${escapeXml(tipDjela)}</tipKrivicnogDjela>
        <clanKZ>${escapeXml(clanKZ)}</clanKZ>
        <brojTransakcija>${escapeXml(String(Number.isNaN(brojTransakcija) ? 0 : brojTransakcija))}</brojTransakcija>
        <brojOkrivljenih>${escapeXml(String(Number.isNaN(brojOkrivljenih) ? 1 : brojOkrivljenih))}</brojOkrivljenih>
        <brojSvjedoka>${escapeXml(String(Number.isNaN(brojSvjedoka) ? 0 : brojSvjedoka))}</brojSvjedoka>
        <brojDokaza>${escapeXml(String(Number.isNaN(brojDokaza) ? 0 : brojDokaza))}</brojDokaza>
        <kazna>${escapeXml(sentence)}</kazna>
        <uslovnaOsuda>${escapeXml(uslovna)}</uslovnaOsuda>
        <vrstaPresude>${escapeXml(verdict)}</vrstaPresude>
        <novcanaKazna>${escapeXml(String(cleanFine))}</novcanaKazna>
        <opisSlucaja>${escapeXml(opis)}</opisSlucaja>
        <iznosi>
          <iznos>${escapeXml(String(cleanUkupanIznos).replace('.', ','))} EUR</iznos>
        </iznosi>
        <svjedoci>
${witnessXml}
        </svjedoci>
        <dokazi>
${evidenceXml}
        </dokazi>
        <bracniStatus>${escapeXml(bracniStatus)}</bracniStatus>
      </proprietary>
    </meta>
    <judgmentBody>
      <introduction>
        <p>U IME CRNE GORE
${escapeXml(sudLabel)}, ${escapeXml(caseNumber)}, sudija ${escapeXml(sudija)}</p>
      </introduction>
      <background>
        <p>Okrivljeni: ${escapeXml(okrivljeni)}</p>
        <p>Zapisničar: ${escapeXml(zapisnicar)}</p>
        <p>Datum odluke: ${escapeXml(isoDate)}</p>
      </background>
      <arguments>
        <block name="opisSlucaja">
          <p>${escapeXml(opis)}</p>
        </block>
      </arguments>
      <motivation>
        <block name="dokazi">
          <tblock>
${motivationEvidenceXml}
          </tblock>
        </block>
      </motivation>
      <decision>
        <block name="odluka">
          <p>${escapeXml(verdict)}</p>
          <p>Kazna: ${escapeXml(sentence)}</p>
        </block>
      </decision>
    </judgmentBody>
    <conclusions>
      <block name="pravniOsnov">
        <p>Krivično djelo: ${escapeXml(tipDjela)} (${escapeXml(clanKZ)} Krivičnog zakonika Crne Gore)</p>
      </block>
    </conclusions>
  </judgment>
</akomaNtoso>`;
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

app.post('/api/cbr-reasoning-input', (req, res) => {
  const queryRaw = req.body?.query;
  if (!queryRaw) {
    return res.status(400).json({ error: 'query is required' });
  }
  if (cbrCases.length === 0) {
    return res.status(500).json({ error: 'CBR baza slučajeva nije učitana' });
  }

  const queryCase = normalizeCbrQuery(queryRaw);
  const queryBroj = queryCase.brojPredmeta;

  const results = [];
  for (const target of cbrCases) {
    const similarity = computeSimilarity(queryCase, target);
    results.push({ case: target, similarity });
  }

  results.sort((a, b) => b.similarity - a.similarity);
  const topK = Math.min(5, results.length);
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
    similarity: Math.round(r.similarity * 1000) / 10,
  }));

  let weightedSentence = 0;
  let weightSum = 0;
  for (const r of results.slice(0, topK)) {
    const months = parseFloat(r.case.kaznaUMjesecima) || 0;
    if (months > 0) {
      weightedSentence += r.similarity * months;
      weightSum += r.similarity;
    }
  }
  const recommendedMonths = weightSum > 0 ? Math.round((weightedSentence / weightSum) * 10) / 10 : null;

  const verdictCounts = {};
  for (const sc of similarCases) {
    const v = sc.vrstaPresude || 'nepoznato';
    verdictCounts[v] = (verdictCounts[v] || 0) + 1;
  }
  const conditionalCount = similarCases.filter(sc => sc.uslovnaOsuda === 'Da').length;

  res.json({
    queryCase: {
      brojPredmeta: queryBroj,
      tipKrivicnogDjela: queryCase.tipKrivicnogDjela,
      clanKZ: queryCase.clanKZ,
      kaznaUMjesecima: parseFloat(queryCase.kaznaUMjesecima) || 0,
      uslovnaOsuda: queryCase.uslovnaOsuda || 'nepoznat',
      vrstaPresude: displayVerdict(queryCase.vrstaPresude || 'nepoznat'),
      novcanaKazna: parseFloat(queryCase.novcanaKazna) || 0,
      ranijeOsudjivan: queryCase.ranijeOsudjivan || 'nepoznat',
      zaposlenost: queryCase.zaposlenost || 'nepoznat',
      priznanje: queryCase.priznanje || 'nepoznat',
    },
    similarCases,
    recommendation: {
      kaznaUMjesecima: recommendedMonths,
      verdictDistribution: verdictCounts,
      conditionalSentenceLikelihood: Math.round((conditionalCount / Math.max(topK, 1)) * 100),
      conditionalExplanation: `Od ${topK} najsličnijih predmeta, ${conditionalCount} ${conditionalCount === 1 ? 'je imao' : 'su imali'} uslovnu presudu.`
    },
    totalCasesCompared: results.length,
  });
});

app.post('/api/cases/user', (req, res) => {
  const input = req.body?.input;
  const decision = req.body?.decision;
  if (!input || !decision) {
    return res.status(400).json({ error: 'input and decision are required' });
  }

  const cbrRecord = {
    id: String(cbrCases.length + 1000),
    sud: String(input.sud || 'Korisnički unos'),
    ...normalizeCbrQuery({
      ...input,
      vrstaPresude: decision.vrstaPresude,
      uslovnaOsuda: decision.uslovnaOsuda,
      kaznaUMjesecima: decision.kaznaUMjesecima,
      novcanaKazna: decision.novcanaKazna,
    })
  };

  const userEntry = {
    savedAt: new Date().toISOString(),
    input,
    decision,
    cbrRecord,
  };

  try {
    const identity = parseCaseIdentity(input.brojPredmeta || cbrRecord.brojPredmeta);
    const xmlFileName = `${identity.fileBase}.xml`;
    const xmlPath = path.join(casesDirFallback, xmlFileName);

    if (!fs.existsSync(casesDirFallback)) {
      fs.mkdirSync(casesDirFallback, { recursive: true });
    }
    if (fs.existsSync(xmlPath)) {
      return res.status(409).json({ error: `Predmet već postoji: ${xmlFileName}` });
    }

    const xmlContent = buildAkomaNtosoCaseXml(input, decision, identity);
    fs.writeFileSync(xmlPath, xmlContent, 'utf8');

    const parsedCase = parseXMLFile(xmlPath);
    if (parsedCase) {
      const existingIndex = caseDatabase.findIndex(c => c.case_id === parsedCase.case_id);
      if (existingIndex >= 0) {
        caseDatabase[existingIndex] = parsedCase;
      } else {
        caseDatabase.push(parsedCase);
      }
    }

    let current = [];
    if (fs.existsSync(userCasesFile)) {
      const raw = fs.readFileSync(userCasesFile, 'utf8');
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) current = parsed;
    }
    userEntry.xmlFile = xmlFileName;
    current.push(userEntry);
    fs.writeFileSync(userCasesFile, JSON.stringify(current, null, 2), 'utf8');

    cbrCases.push(cbrRecord);
    res.json({ status: 'success', message: 'Case saved', cbrRecord, xmlFile: xmlFileName });
  } catch (err) {
    res.status(500).json({ error: `Save failed: ${err.message}` });
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
