const path = require('path');
const fs = require('fs');

// ===============================
// Markov Chain Text Generator
// ===============================
// Trigram (order-2) word-level Markov chain trained on real court decisions
// from the archive. This is a probabilistic ML model for text generation.

class MarkovChain {
  constructor(order = 2) {
    this.order = order;
    this.transitions = {};  // key: "word1 word2" -> { nextWord: count, ... }
    this.starters = [];     // sentence-starting n-grams
  }

  train(texts) {
    for (const text of texts) {
      const words = text.replace(/\s+/g, ' ').trim().split(' ').filter(Boolean);
      if (words.length < this.order + 1) continue;

      // Record the first n-gram as a starter
      this.starters.push(words.slice(0, this.order).join(' '));

      for (let i = 0; i <= words.length - this.order - 1; i++) {
        const key = words.slice(i, i + this.order).join(' ');
        const next = words[i + this.order];
        if (!this.transitions[key]) this.transitions[key] = {};
        this.transitions[key][next] = (this.transitions[key][next] || 0) + 1;
      }
    }
  }

  _pickWeighted(options) {
    const entries = Object.entries(options);
    if (entries.length === 0) return null;
    const total = entries.reduce((sum, [, count]) => sum + count, 0);
    let r = Math.random() * total;
    for (const [word, count] of entries) {
      r -= count;
      if (r <= 0) return word;
    }
    return entries[entries.length - 1][0];
  }

  generate(maxWords = 80, seed = null) {
    // If seed provided, find the best matching starter
    let current;
    if (seed) {
      const seedWords = seed.toLowerCase().split(/\s+/);
      const match = this.starters.find(s => seedWords.some(sw => s.toLowerCase().includes(sw)));
      current = match || this.starters[Math.floor(Math.random() * this.starters.length)];
    } else {
      if (this.starters.length === 0) return '';
      current = this.starters[Math.floor(Math.random() * this.starters.length)];
    }

    const words = current.split(' ');
    for (let i = 0; i < maxWords; i++) {
      const key = words.slice(-this.order).join(' ');
      const options = this.transitions[key];
      if (!options) break;
      const next = this._pickWeighted(options);
      if (!next) break;
      words.push(next);
      // Stop at natural sentence end
      if (words.length > 20 && next.endsWith('.')) break;
    }
    return words.join(' ');
  }
}

// Section-specific Markov chains
const markovModels = {
  reasoning: new MarkovChain(2),
  sentencing: new MarkovChain(2),
  intro: new MarkovChain(2),
};
let markovTrained = false;

function parseArchiveTextSections(text) {
  const sections = { intro: '', facts: '', reasoning: '', sentencing: '' };

  // Normalize whitespace
  const lines = text.split(/\r?\n/);
  const fullText = text.replace(/\r?\n/g, ' ').replace(/\s+/g, ' ');

  // Find section boundaries
  const presuduIdx = fullText.search(/P\s*R\s*E\s*S\s*U\s*D\s*U/i);
  const obrazlozenjeIdx = fullText.search(/O\s*b\s*r\s*a\s*z\s*l\s*o\s*ž\s*e\s*nj?\s*e/i);
  const uImeIdx = fullText.search(/U\s+IME\s+(CRNE\s+GORE|NARODA)/i);

  // Intro: from "U IME" to "PRESUDU"
  if (uImeIdx >= 0 && presuduIdx > uImeIdx) {
    sections.intro = fullText.substring(uImeIdx, presuduIdx).trim();
  }

  // Sentencing: from "PRESUDU" to "Obrazloženje"
  if (presuduIdx >= 0) {
    const end = obrazlozenjeIdx > presuduIdx ? obrazlozenjeIdx : fullText.length;
    sections.sentencing = fullText.substring(presuduIdx, end).trim();
  }

  // Reasoning: from "Obrazloženje" to end
  if (obrazlozenjeIdx >= 0) {
    const courtEndIdx = fullText.search(/OSNOVNI\s+SUD\s+U\s+\w+,?\s*dana/i);
    const end = courtEndIdx > obrazlozenjeIdx ? courtEndIdx : fullText.length;
    sections.reasoning = fullText.substring(obrazlozenjeIdx, end).trim();
  }

  return sections;
}

function trainMarkovModels() {
  if (markovTrained) return;

  const archiveDir = path.join(__dirname, '../../../archive/presude');
  if (!fs.existsSync(archiveDir)) {
    console.warn(' Archive directory not found, Markov models will not be trained.');
    return;
  }

  const introTexts = [];
  const reasoningTexts = [];
  const sentencingTexts = [];
  let fileCount = 0;

  // Recursively read all .txt files from archive
  function readDir(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        readDir(fullPath);
      } else if (entry.name.endsWith('.txt')) {
        try {
          const content = fs.readFileSync(fullPath, 'utf8');
          const sections = parseArchiveTextSections(content);
          if (sections.intro.length > 50) introTexts.push(sections.intro);
          if (sections.reasoning.length > 100) reasoningTexts.push(sections.reasoning);
          if (sections.sentencing.length > 50) sentencingTexts.push(sections.sentencing);
          fileCount++;
        } catch (err) { /* skip unreadable files */ }
      }
    }
  }

  readDir(archiveDir);

  if (fileCount > 0) {
    markovModels.intro.train(introTexts);
    markovModels.reasoning.train(reasoningTexts);
    markovModels.sentencing.train(sentencingTexts);
    markovTrained = true;
    console.log(`🧠 Markov chain modeli obučeni na ${fileCount} sudskih presuda (intro: ${introTexts.length}, reasoning: ${reasoningTexts.length}, sentencing: ${sentencingTexts.length})`);
  }
}

function generateMarkovText(section, seed, maxWords = 80) {
  trainMarkovModels();
  const model = markovModels[section];
  if (!model || Object.keys(model.transitions).length === 0) return null;
  const text = model.generate(maxWords, seed);
  if (!text || text.split(/\s+/).length < 8) return null;
  return text;
}

module.exports = {
  MarkovChain,
  markovModels,
  trainMarkovModels,
  parseArchiveTextSections,
  generateMarkovText,
};
