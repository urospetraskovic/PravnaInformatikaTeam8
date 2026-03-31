const express = require('express');
const path = require('path');
const fs = require('fs');
const router = express.Router();
const { caseDatabase, casesDirFallback } = require('../db/caseDatabase');
const { cbrCases, buildCbrRecordFromParsed } = require('../db/cbrDatabase');
const { parseXMLFile } = require('../parsers/xmlParser');
const { buildAkomaNtosoCaseXml } = require('../builders/xmlBuilder');
const {
  parseCaseIdentity,
  getNextSequentialCaseNumber,
  deriveDecisionFromSignals,
  generateNarrativeSections,
  validateUserInput,
} = require('../reasoning/judiciaryLogic');

router.post('/cases/user', (req, res) => {
  const input = req.body?.input;
  const decision = req.body?.decision;
  if (!input || !decision) {
    return res.status(400).json({ error: 'input and decision are required' });
  }

  try {
    const identity = parseCaseIdentity(input.brojPredmeta);
    const xmlFileName = `${identity.fileBase}.xml`;
    const xmlPath = path.join(casesDirFallback, xmlFileName);

    if (!fs.existsSync(casesDirFallback)) {
      fs.mkdirSync(casesDirFallback, { recursive: true });
    }
    const isUpdate = fs.existsSync(xmlPath);

    const sections = generateNarrativeSections(input, decision);
    const xmlContent = buildAkomaNtosoCaseXml(input, decision, identity, sections);
    fs.writeFileSync(xmlPath, xmlContent, 'utf8');

    const parsedCase = parseXMLFile(xmlPath);
    if (parsedCase) {
      const existingIndex = caseDatabase.findIndex(c => c.case_id === parsedCase.case_id);
      if (existingIndex >= 0) {
        caseDatabase[existingIndex] = parsedCase;
      } else {
        caseDatabase.push(parsedCase);
      }
      const cbrRecord = buildCbrRecordFromParsed(parsedCase);
      const cbrIdx = cbrCases.findIndex(c => c.brojPredmeta === cbrRecord.brojPredmeta);
      if (cbrIdx >= 0) {
        cbrCases[cbrIdx] = cbrRecord;
      } else {
        cbrCases.push(cbrRecord);
      }
    }

    const message = isUpdate ? 'Kazna je uspješno ažurirana' : 'Slučaj je uspješno sačuvan';
    res.json({ status: 'success', message, isUpdate, xmlFile: xmlFileName, sections });
  } catch (err) {
    res.status(500).json({ error: `Save failed: ${err.message}` });
  }
});

router.post('/generate-judgment', (req, res) => {
  const input = req.body?.input || {};
  const ruleReasoning = req.body?.ruleReasoning || {};
  const cbrReasoning = req.body?.cbrReasoning || {};
  const decisionOverride = req.body?.decisionOverride || {};
  const previewOnly = req.body?.previewOnly === true;

  const validationError = validateUserInput(input);
  if (validationError) {
    return res.status(400).json({ error: validationError });
  }

  try {
    const identity = parseCaseIdentity(input.brojPredmeta);

    let fileBase = identity.fileBase;
    let xmlPath = path.join(casesDirFallback, `${fileBase}.xml`);

    if (!previewOnly) {
      if (!fs.existsSync(casesDirFallback)) {
        fs.mkdirSync(casesDirFallback, { recursive: true });
      }
      // If file exists, pick the next sequential number for that year
      if (fs.existsSync(xmlPath)) {
        const nextNum = getNextSequentialCaseNumber(identity.year);
        fileBase = `K ${nextNum}_${identity.year}`;
        xmlPath = path.join(casesDirFallback, `${fileBase}.xml`);
      }
    }

    const adjustedIdentity = {
      ...identity,
      fileBase,
      judgmentName: fileBase.replace(/\s+/g, '_'),
    };

    const decision = deriveDecisionFromSignals(ruleReasoning, cbrReasoning, decisionOverride);
    const sections = generateNarrativeSections(input, decision, ruleReasoning, cbrReasoning);
    const xmlContent = buildAkomaNtosoCaseXml(input, decision, adjustedIdentity, sections);

    let parsedCase = null;
    if (!previewOnly) {
      fs.writeFileSync(xmlPath, xmlContent, 'utf8');
      parsedCase = parseXMLFile(xmlPath);
      if (parsedCase) {
        const existingIndex = caseDatabase.findIndex((c) => c.case_id === parsedCase.case_id);
        if (existingIndex >= 0) {
          caseDatabase[existingIndex] = parsedCase;
        } else {
          caseDatabase.push(parsedCase);
        }
        const cbrRecord = buildCbrRecordFromParsed(parsedCase);
        const cbrIdx = cbrCases.findIndex(c => c.brojPredmeta === cbrRecord.brojPredmeta);
        if (cbrIdx >= 0) {
          cbrCases[cbrIdx] = cbrRecord;
        } else {
          cbrCases.push(cbrRecord);
        }
      }
    }

    res.json({
      status: 'success',
      xmlFile: previewOnly ? null : path.basename(xmlPath),
      caseId: parsedCase?.id || adjustedIdentity.fileBase,
      decision,
      sections,
      reasoningSummary: sections.reasoningSummary,
    });
  } catch (err) {
    res.status(500).json({ error: `Generisanje nije uspelo: ${err.message}` });
  }
});

router.post('/generate-description', (req, res) => {
  const input = req.body?.input || {};

  const okrivljeni = String(input.okrivljeni || 'NN').trim();
  const sud = String(input.sud || 'Podgorici').trim();
  const tipKrivicnogDjela = String(input.tipKrivicnogDjela || '').trim();
  const clanKZ = String(input.clanKZ || '').trim();
  const iznos = parseFloat(input.iznos) || 0;
  const ukupanIznos = parseFloat(input.ukupanIznos) || 0;
  const brojTransakcija = parseInt(input.brojTransakcija) || 0;
  const svjedoci = String(input.svjedoci || '').trim();
  const dokazi = String(input.dokazi || '').trim();
  const datumPresude = String(input.datumPresude || '').trim();
  const ranijeOsudjivan = String(input.ranijeOsudjivan || 'ne').toLowerCase();
  const pokusaj = String(input.pokusaj || 'ne').toLowerCase();
  const saizvrsilastvo = String(input.saizvrsilastvo || 'ne').toLowerCase();
  const zaposlenost = String(input.zaposlenost || 'nepoznat').toLowerCase();
  const priznanje = String(input.priznanje || 'ne').toLowerCase();

  const listFromText = (value) => String(value || '').split(/\r?\n|;/).map((v) => v.trim()).filter(Boolean);
  const evidenceList = listFromText(dokazi);
  const witnessList = listFromText(svjedoci);

  const datumLabel = datumPresude ? `dana ${datumPresude}` : '';
  const sudLabel = `u ${sud}`;
  const isPokusaj = pokusaj === 'da';
  const isSaizvrsilastvo = saizvrsilastvo === 'da';
  const isKartice = tipKrivicnogDjela.toLowerCase().includes('kartic');

  let parts = [];

  if (isKartice) {
    let action = `${isPokusaj ? 'pokušao da izvrši' : 'izvršio'} krivično djelo falsifikovanja i zloupotrebe kreditnih kartica iz ${clanKZ} Krivičnog zakonika Crne Gore`;
    if (brojTransakcija > 0) action += `, vršeći neovlašćene transakcije u broju od ${brojTransakcija}`;
    if (iznos > 0) action += ` u iznosu od ${iznos} EUR po transakciji`;
    if (ukupanIznos > 0 && ukupanIznos !== iznos) action += `, ukupno ${ukupanIznos} EUR`;
    parts.push(`Optuženi ${okrivljeni} se tereti da je ${sudLabel}${datumLabel ? ', ' + datumLabel : ''}, ${action}.`);
  } else {
    let action = `${isPokusaj ? 'pokušao da stavi u promet' : 'stavio u promet'} falsifikovani novac iz ${clanKZ} Krivičnog zakonika Crne Gore`;
    if (iznos > 0) action += ` u vrijednosti od ${iznos} EUR`;
    if (ukupanIznos > 0 && ukupanIznos !== iznos) action += ` (ukupan iznos ${ukupanIznos} EUR)`;
    parts.push(`Optuženi ${okrivljeni} se tereti da je ${sudLabel}${datumLabel ? ', ' + datumLabel : ''}, ${action}.`);
  }

  if (isSaizvrsilastvo) {
    parts.push(`Djelo je izvršeno u saizvršilaštvu.`);
  }

  if (ranijeOsudjivan === 'da') {
    parts.push(`Okrivljeni je ranije osuđivan.`);
  } else if (ranijeOsudjivan === 'ne') {
    parts.push(`Okrivljeni ranije nije osuđivan.`);
  }

  if (zaposlenost !== 'nepoznat') {
    const zapMap = { zaposlen: 'zaposlen', nezaposlen: 'nezaposlen', student: 'student', penzioner: 'penzioner' };
    const zapLabel = zapMap[zaposlenost] || zaposlenost;
    parts.push(`Okrivljeni je ${zapLabel}.`);
  }

  if (priznanje === 'da') {
    parts.push(`Okrivljeni je priznao izvršenje krivičnog djela.`);
  }

  if (witnessList.length > 0) {
    parts.push(`Saslušani su svjedoci: ${witnessList.join(', ')}.`);
  }

  if (evidenceList.length > 0) {
    parts.push(`Materijalni dokazi: ${evidenceList.join(', ')}.`);
  }

  const description = parts.join(' ');
  res.json({ description });
});

module.exports = router;
