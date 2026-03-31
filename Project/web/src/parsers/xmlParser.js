const path = require('path');
const fs = require('fs');
const { DOMParser } = require('@xmldom/xmldom');

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
    let obrazovanje = 'nepoznat';
    let brojTransakcija = 0;
    let brojOkrivljenih = 1;
    let brojSvjedoka = 0;
    let brojDokaza = 0;
    let generatedBy = '';

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
      obrazovanje = getTextContent('obrazovanje') || 'nepoznat';
      brojTransakcija = parseInt(getTextContent('brojTransakcija') || '0', 10);
      brojOkrivljenih = parseInt(getTextContent('brojOkrivljenih') || '1', 10);
      brojSvjedoka = parseInt(getTextContent('brojSvjedoka') || '0', 10);
      brojDokaza = parseInt(getTextContent('brojDokaza') || '0', 10);
      generatedBy = getTextContent('generatedBy') || '';

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
      sentenceMonths: (() => { const m = String(sentenceText || '').match(/(\d+)/); return m ? parseInt(m[1], 10) : 0; })(),
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
      tipKrivicnogDjela: tipKrivicnogDjela,
      obrazovanje: obrazovanje,
      brojTransakcija: brojTransakcija,
      brojOkrivljenih: brojOkrivljenih,
      brojSvjedoka: brojSvjedoka,
      brojDokaza: brojDokaza,
      generatedBy: generatedBy,
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

module.exports = {
  parseXMLFile,
  normalizeLegalArticleText,
  extractCanonicalArticleRef,
  buildAppliedArticles,
  pickMainArticleByCrimeType,
};
