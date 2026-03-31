const express = require('express');
const fs = require('fs');
const router = express.Router();
const { caseDatabase } = require('../db/caseDatabase');
const { cbrCases } = require('../db/cbrDatabase');

// API: Get all cases
router.get('/cases', (req, res) => {
  res.json(caseDatabase);
});

// API: Get case statistics
router.get('/statistics', (req, res) => {
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
router.get('/case-types', (req, res) => {
  const uniqueTypes = [...new Set(caseDatabase.map(c => c.type))].sort();
  const typesWithCounts = uniqueTypes.map(type => ({
    type,
    count: caseDatabase.filter(c => c.type === type).length
  }));
  res.json(typesWithCounts);
});

// API: Search cases by type
router.get('/search/type/:type', (req, res) => {
  const type = req.params.type.toLowerCase();
  const results = caseDatabase.filter(c => c.type.toLowerCase().includes(type))
    .sort((a, b) => b.harm - a.harm);
  res.json(results);
});

// API: Get case by ID
router.get('/cases/:id(*)', (req, res) => {
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

// API: Delete case by ID
router.delete('/cases/:id(*)', (req, res) => {
  const caseId = decodeURIComponent(req.params.id);
  const idx = caseDatabase.findIndex(c => c.id === caseId || c.case_id === caseId || c.caseNumber === caseId);
  if (idx < 0) return res.status(404).json({ error: 'Predmet nije pronađen' });

  const caseRecord = caseDatabase[idx];

  if (caseRecord.xmlFile && fs.existsSync(caseRecord.xmlFile)) {
    fs.unlinkSync(caseRecord.xmlFile);
  }

  caseDatabase.splice(idx, 1);

  const cbrIdx = cbrCases.findIndex(c => c.brojPredmeta === caseRecord.caseNumber);
  if (cbrIdx >= 0) cbrCases.splice(cbrIdx, 1);

  console.log(`🗑️ Deleted case: ${caseId}`);
  res.json({ status: 'success', deleted: caseId });
});

module.exports = router;
