const path = require('path');
const fs = require('fs');

// cbrCases is populated after caseDatabase loads, so we import lazily via getter
// to avoid circular dependency. Routes import { cbrCases } from this module.
const cbrCsvPath = path.join(__dirname, '../../../case_reasoning/presude-cbr/src/main/resources/presude.csv');
const cbrCases = [];

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

function buildCbrRecordFromParsed(c) {
  return {
    id: c.caseNumber,
    sud: c.court || 'Nepoznat',
    ...normalizeCbrQuery({
      brojPredmeta: c.caseNumber,
      tipKrivicnogDjela: c.tipKrivicnogDjela || c.type || '',
      clanKZ: c.clanKZ || '',
      iznos: String(c.totalAmount || 0),
      ukupanIznos: String(c.totalAmount || 0),
      ranijeOsudjivan: c.ranijeOsudjivan || 'nepoznat',
      uslovnaOsuda: c.uslovnaOsuda ? 'Da' : 'Ne',
      vrstaPresude: c.verdict || 'nepoznat',
      zaposlenost: c.zaposlenost || 'nepoznat',
      bracniStatus: c.bracniStatus || 'nepoznat',
      kaznaUMjesecima: c.sentenceMonths || 0,
      novcanaKazna: parseFloat(c.novcanaKazna) || 0,
      obrazovanje: c.obrazovanje || 'nepoznat',
      brojTransakcija: c.brojTransakcija || 0,
      brojOkrivljenih: c.brojOkrivljenih || 1,
      brojSvjedoka: c.brojSvjedoka || 0,
      brojDokaza: c.brojDokaza || 0,
      priznanje: 'ne',
      pokusaj: 'ne',
      saizvrsilastvo: 'ne',
    }),
  };
}

function loadGeneratedCbrCases(caseDatabase) {
  let count = 0;
  for (const c of caseDatabase) {
    if (c.generatedBy) {
      cbrCases.push(buildCbrRecordFromParsed(c));
      count++;
    }
  }
  if (count > 0) {
    console.log(`🧠 Loaded ${count} user-generated cases into CBR memory from XML`);
  }
}

module.exports = {
  cbrCases,
  cbrCsvPath,
  loadCbrCases,
  loadGeneratedCbrCases,
  normalizeCbrQuery,
  buildCbrRecordFromParsed,
};
