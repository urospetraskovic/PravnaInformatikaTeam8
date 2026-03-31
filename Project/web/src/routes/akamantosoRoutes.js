const express = require('express');
const path = require('path');
const fs = require('fs');
const router = express.Router();
const { caseDatabase } = require('../db/caseDatabase');

// API: Get AkomaNtoso XML for a specific case
router.get('/akomantoso/:caseId(*)', (req, res) => {
  const caseId = decodeURIComponent(req.params.caseId || '');
  const caseDir = path.join(__dirname, '../../../../data/cases/akomantoso');

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

module.exports = router;
