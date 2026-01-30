const express = require('express');
const path = require('path');
const fs = require('fs');
const app = express();

// Load case database from JSON file
const dbPath = path.join(__dirname, '../../data/cases/DB/EXTRACTED_CASES_DATABASE.json');
let fullDatabase = [];

try {
  const rawData = fs.readFileSync(dbPath, 'utf8');
  const jsonData = JSON.parse(rawData);
  
  // Transform the database to a simpler format for the web UI
  fullDatabase = jsonData.map((caseData, index) => {
    try {
      const harmLevel = Math.min(5, Math.max(0, 
        (caseData.victim?.harm_psychological || 0) + 
        (caseData.victim?.harm_physical || 0)
      ));
      
      // Extract verdict from boolean flags
      let verdictString = 'UNKNOWN';
      if (typeof caseData.verdict === 'object' && caseData.verdict !== null) {
        if (caseData.verdict.guilty === true) {
          verdictString = 'GUILTY';
        } else if (caseData.verdict.acquitted === true) {
          verdictString = 'ACQUITTED';
        } else if (caseData.verdict.conditional === true) {
          verdictString = 'CONDITIONAL';
        }
      } else if (typeof caseData.verdict === 'string') {
        verdictString = caseData.verdict.toUpperCase();
      }

      // Extract evidence summary
      let evidenceText = 'No evidence documented';
      if (typeof caseData.evidence === 'object' && caseData.evidence !== null) {
        if (caseData.evidence.summary) {
          evidenceText = caseData.evidence.summary;
        } else if (caseData.evidence.description) {
          evidenceText = caseData.evidence.description;
        }
      } else if (typeof caseData.evidence === 'string') {
        evidenceText = caseData.evidence;
      }

      // Extract sentence from verdict object or fallback to other fields
      let sentenceText = 'Not specified';
      if (caseData.verdict && typeof caseData.verdict === 'object') {
        const sentenceType = caseData.verdict.sentence_type || '';
        const sentenceDuration = caseData.verdict.sentence_duration_months || '';
        if (sentenceType || sentenceDuration) {
          sentenceText = `${sentenceType}${sentenceDuration ? ' - ' + sentenceDuration + ' months' : ''}`.trim();
        }
      } else if (caseData.sentence_text || caseData.sentence) {
        sentenceText = caseData.sentence_text || caseData.sentence;
      }

      return {
        id: caseData.case_number || `Case_${index + 1}`,
        type: caseData.case_type || 'Unknown',
        court: (caseData.court || 'Unknown')
          .replace('Osnovni Sud u ', '')
          .replace('Osnovni Sud ', '')
          .replace('Osnovna škola ', '')
          .trim() || 'Unknown Court',
        verdict: verdictString,
        sentence: sentenceText,
        articles: Array.isArray(caseData.legal?.articles_charged) 
          ? caseData.legal.articles_charged 
          : (caseData.legal?.articles_charged ? [caseData.legal.articles_charged] : []),
        defendant: caseData.defendant?.name || 'Unknown',
        victim: caseData.victim?.name || 'Unknown',
        harm: harmLevel,
        evidence: evidenceText,
        year: parseInt(caseData.verdict_date) || 2024,
        fullData: caseData
      };
    } catch (err) {
      console.warn(`Warning: Error processing case ${index + 1}:`, err.message);
      return {
        id: `Case_${index + 1}`,
        type: 'Unknown',
        court: 'Unknown',
        verdict: 'UNKNOWN',
        sentence: 'Not specified',
        articles: [],
        defendant: 'Unknown',
        victim: 'Unknown',
        harm: 0,
        evidence: 'No information',
        year: 2024,
        fullData: caseData
      };
    }
  });
  console.log(`✅ Successfully loaded ${fullDatabase.length} cases from database`);
} catch (error) {
  console.error('Error loading database:', error.message);
  console.log('Using fallback database...');
  
  // Fallback database if JSON loading fails
  fullDatabase = [
    {
      id: 'K 217/24',
      type: 'Workplace Harassment',
      court: 'Berané',
      verdict: 'GUILTY',
      sentence: '6 months',
      articles: ['168'],
      defendant: 'Unknown',
      victim: 'Unknown',
      harm: 3,
      evidence: 'Witness testimony',
      year: 2024
    },
    {
      id: 'K 277/12',
      type: 'Labor Rights Violation',
      court: 'Bijelo Polje',
      verdict: 'GUILTY',
      sentence: 'Suspended',
      articles: ['169'],
      defendant: 'Unknown',
      victim: 'Unknown',
      harm: 2,
      evidence: 'Documentation',
      year: 2012
    },
    {
      id: 'K 98/2018',
      type: 'Stalking',
      court: 'Podgorica',
      verdict: 'GUILTY',
      sentence: '1 year',
      articles: ['168a'],
      defendant: 'Unknown',
      victim: 'Unknown',
      harm: 4,
      evidence: 'Phone records, 20+ calls',
      year: 2018
    },
    {
      id: 'K 664/2022',
      type: 'Workplace Assault',
      court: 'Podgorica',
      verdict: 'GUILTY',
      sentence: '2 years 4 months',
      articles: ['215'],
      defendant: 'Unknown',
      victim: 'Unknown',
      harm: 5,
      evidence: 'Medical records, witness testimony',
      year: 2022
    },
    {
      id: 'K 64/14',
      type: 'Threatening/Safety',
      court: 'Cetinje',
      verdict: 'ACQUITTED',
      sentence: 'None',
      articles: ['168'],
      defendant: 'Unknown',
      victim: 'Unknown',
      harm: 1,
      evidence: 'Insufficient evidence',
      year: 2014
    },
    {
      id: 'K 292/2014',
      type: 'Embezzlement',
      court: 'Bijelo Polje',
      verdict: 'GUILTY',
      sentence: '4 years',
      articles: ['271'],
      defendant: 'Unknown',
      victim: 'Unknown',
      harm: 3,
      evidence: 'Financial records',
      year: 2014
    },
    {
      id: 'K 30/2020',
      type: 'Coal Theft',
      court: 'Pljevlja',
      verdict: 'ACQUITTED',
      sentence: 'None',
      articles: ['199'],
      defendant: 'Unknown',
      victim: 'Unknown',
      harm: 0,
      evidence: 'Insufficient evidence',
      year: 2020
    },
    {
      id: 'K 22/2022',
      type: 'Social Insurance Fraud',
      court: 'Podgorica',
      verdict: 'ACQUITTED',
      sentence: 'None',
      articles: ['264'],
      defendant: 'Unknown',
      victim: 'Unknown',
      harm: 1,
      evidence: 'Lack of proof',
      year: 2022
    },
    {
      id: 'K 375/14',
      type: 'Domestic Violence',
      court: 'Kotor',
      verdict: 'CONDITIONAL',
      sentence: 'Suspended',
      articles: ['215'],
      defendant: 'Unknown',
      victim: 'Unknown',
      harm: 4,
      evidence: 'Injury reports',
      year: 2014
    }
  ];
}

const caseDatabase = fullDatabase;

// Similarity calculation (simplified version of Java algorithm)
function calculateSimilarity(queryCase, dbCase) {
  let score = 0;
  
  // Type match (40%)
  const typeSimilarity = queryCase.type === dbCase.type ? 1.0 : 
                         (queryCase.type.includes('Harassment') && dbCase.type.includes('Harassment')) ? 0.85 :
                         (queryCase.type.includes('Assault') && dbCase.type.includes('Assault')) ? 0.85 : 0.3;
  score += typeSimilarity * 0.40;
  
  // Verdict match (25%)
  const verdictSimilarity = queryCase.verdict === dbCase.verdict ? 1.0 : 0.3;
  score += verdictSimilarity * 0.25;
  
  // Harm match (15%)
  const harmDiff = Math.abs(queryCase.harm - dbCase.harm);
  const harmSimilarity = harmDiff === 0 ? 1.0 : Math.max(0, 1 - (harmDiff * 0.1));
  score += harmSimilarity * 0.15;
  
  // Evidence match (10%)
  const evidenceSimilarity = queryCase.evidence === dbCase.evidence ? 1.0 : 0.7;
  score += evidenceSimilarity * 0.10;
  
  // Year proximity (10%)
  const yearDiff = Math.abs(queryCase.year - dbCase.year);
  const yearSimilarity = Math.max(0, 1 - (yearDiff / 100));
  score += yearSimilarity * 0.10;
  
  return score;
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
  const stats = {
    totalCases: caseDatabase.length,
    guiltyCount: caseDatabase.filter(c => c.verdict === 'GUILTY').length,
    acquittedCount: caseDatabase.filter(c => c.verdict === 'ACQUITTED').length,
    conditionalCount: caseDatabase.filter(c => c.verdict === 'CONDITIONAL').length,
    averageHarm: (caseDatabase.reduce((sum, c) => sum + c.harm, 0) / caseDatabase.length).toFixed(2),
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

// API: Search cases by type
app.get('/api/search/type/:type', (req, res) => {
  const type = req.params.type.toLowerCase();
  const results = caseDatabase.filter(c => c.type.toLowerCase().includes(type))
    .sort((a, b) => b.harm - a.harm);
  res.json(results);
});

// API: Search similar cases
app.post('/api/search/similar', (req, res) => {
  const queryCase = req.body;
  const results = caseDatabase
    .map(dbCase => ({
      ...dbCase,
      similarityScore: calculateSimilarity(queryCase, dbCase)
    }))
    .filter(c => c.similarityScore > 0.5)
    .sort((a, b) => b.similarityScore - a.similarityScore)
    .slice(0, 5);
  res.json(results);
});

// API: Get case by ID - decode URL-encoded spaces
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

// Serve static files AFTER API routes
app.use(express.static(path.join(__dirname, 'public')));

const PORT = process.env.PORT || 3000;
app.listen(PORT, async () => {
  console.log(`\n✅ Legal CBR Web UI running at http://localhost:${PORT}`);
  console.log('📊 Database loaded with 13 Montenegrian cases\n');
  
  // Automatically open browser
  try {
    const open = await import('open');
    await open.default(`http://localhost:${PORT}`);
  } catch (err) {
    console.warn('Could not automatically open browser. Please visit http://localhost:' + PORT);
  }
});
