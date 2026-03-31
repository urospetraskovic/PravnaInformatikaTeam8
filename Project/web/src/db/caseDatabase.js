const path = require('path');
const fs = require('fs');
const { parseXMLFile } = require('../parsers/xmlParser');

// Load case database from XML files - try akomantoso_new first, fallback to akomantoso
const casesDir = path.join(__dirname, '../../../data/cases/akomantoso_new');
const casesDirFallback = path.join(__dirname, '../../../data/cases/akomantoso');

const caseDatabase = [];

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
  caseDatabase.push({
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
  });
}

module.exports = { caseDatabase, casesDir, casesDirFallback };
