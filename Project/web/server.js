const express = require('express');
const path = require('path');
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

// Add headers to ensure JSON responses
app.use((req, res, next) => {
  if (req.path.startsWith('/api/')) {
    res.header('Content-Type', 'application/json; charset=utf-8');
  }
  next();
});

// Load databases (side-effect: populates caseDatabase and cbrCases arrays)
const { caseDatabase } = require('./src/db/caseDatabase');
const { loadCbrCases, loadGeneratedCbrCases } = require('./src/db/cbrDatabase');
loadCbrCases();
loadGeneratedCbrCases(caseDatabase);

// Register routes - API MUST come before static files!
app.use('/api', require('./src/routes/casesRoutes'));
app.use('/api', require('./src/routes/glava23Routes'));
app.use('/api', require('./src/routes/akamantosoRoutes'));
app.use('/api', require('./src/routes/reasoningRoutes'));
app.use('/api', require('./src/routes/judgmentRoutes'));

// Serve static files AFTER API routes
app.use(express.static(path.join(__dirname, 'public')));

const { trainMarkovModels } = require('./src/models/markovChain');

app.listen(PORT, async () => {
  console.log(`\n✅ Legal CBR Web UI running at http://localhost:${PORT}`);
  console.log(`📊 Database loaded with ${caseDatabase.length} Montenegrian cases`);

  // Train Markov chain models on archive court decisions
  trainMarkovModels();
  console.log('');

  // Auto-open browser
  try {
    const open = (await import('open')).default;
    await open(`http://localhost:${PORT}`);
    console.log('🌐 Browser opened automatically');
  } catch (err) {
    console.log('💡 Open http://localhost:' + PORT + ' in your browser');
  }
});
