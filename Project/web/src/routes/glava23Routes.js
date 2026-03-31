const express = require('express');
const path = require('path');
const router = express.Router();
const { parseGlava23 } = require('../parsers/glava23Parser');

// API: Get Glava 23 (Criminal Code Chapter 23) articles
router.get('/glava23', (req, res) => {
  const glava23Path = path.join(__dirname, '../../../../data/glava23/criminal_code.xml');

  try {
    const result = parseGlava23(glava23Path);
    if (result.error) {
      return res.status(result.status || 500).json({ error: result.error });
    }
    res.json(result);
  } catch (error) {
    console.error('Error reading Glava 23:', error);
    res.status(500).json({ error: 'Error reading Glava 23' });
  }
});

module.exports = router;
