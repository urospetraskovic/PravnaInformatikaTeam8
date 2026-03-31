const express = require('express');
const path = require('path');
const router = express.Router();
const { caseDatabase } = require('../db/caseDatabase');
const { cbrCases, normalizeCbrQuery } = require('../db/cbrDatabase');
const { computeSimilarity, formatCourtName, displayVerdict } = require('../reasoning/cbrReasoning');

// Reasoning API endpoint
router.post('/reasoning', async (req, res) => {
  const { caseId, facts } = req.body;

  if (!caseId && !facts) {
    return res.status(400).json({ error: 'Either caseId or facts required' });
  }

  try {
    const { spawn } = require('child_process');
    const projectRoot = path.join(__dirname, '../../../..');

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

router.post('/cbr-reasoning', (req, res) => {
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
      tipKrivicnogDjela: caseRecord.tipKrivicnogDjela || caseRecord.type || '',
      clanKZ: caseRecord.clanKZ || '',
      ranijeOsudjivan: caseRecord.ranijeOsudjivan || 'nepoznat',
      zaposlenost: caseRecord.zaposlenost || 'nepoznat',
      bracniStatus: caseRecord.bracniStatus || 'nepoznat',
      obrazovanje: caseRecord.obrazovanje || 'nepoznat',
      iznos: String(caseRecord.totalAmount || 0),
      ukupanIznos: String(caseRecord.totalAmount || 0),
      kaznaUMjesecima: String(caseRecord.sentenceMonths || 0),
      novcanaKazna: String(parseFloat(caseRecord.novcanaKazna) || 0),
      uslovnaOsuda: caseRecord.uslovnaOsuda ? 'Da' : 'Ne',
      vrstaPresude: caseRecord.verdict || 'nepoznat',
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

router.post('/cbr-reasoning-input', (req, res) => {
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

module.exports = router;
