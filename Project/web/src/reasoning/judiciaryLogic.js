const path = require('path');
const fs = require('fs');
const { generateMarkovText } = require('../models/markovChain');
const { casesDirFallback } = require('../db/caseDatabase');

function parseCaseIdentity(rawCaseNumber = '') {
  const now = new Date();
  const fallbackYear = now.getFullYear();
  // Strip leading "K" or "K " prefix before parsing numbers
  const raw = String(rawCaseNumber || '').trim().replace(/^K\s*/i, '');

  let broj = '';
  let year = fallbackYear;

  let match = raw.match(/(\d+)\s*\/\s*(\d{2,4})/);
  if (!match) {
    match = raw.match(/(\d+)[^\d]+(\d{2,4})/);
  }

  if (match) {
    broj = match[1];
    const parsedYear = parseInt(match[2], 10);
    if (!Number.isNaN(parsedYear)) {
      if (parsedYear > 99 && parsedYear < 2100) {
        year = parsedYear;
      } else if (parsedYear <= 99) {
        year = (parsedYear <= 30 ? 2000 : 1900) + parsedYear;
      }
    }
  } else {
    const digits = raw.match(/\d+/);
    broj = digits ? digits[0] : '';
  }

  // If broj is missing, compute sequential number for the year based on existing akomantoso files
  if (!broj) {
    broj = String(getNextSequentialCaseNumber(year));
  }

  // Enforce numeric and at most 4 digits per year; if longer, trim to 4
  broj = broj.replace(/\D/g, '');
  if (!broj) {
    broj = String(getNextSequentialCaseNumber(year));
  }
  if (broj.length > 4) {
    broj = broj.slice(0, 4);
  }

  return {
    broj,
    year,
    fileBase: `K ${broj}_${year}`,
    judgmentName: `K_${broj}_${year}`,
    fallbackCaseNumber: `${broj}/${String(year).slice(-2)}`,
  };
}

function getNextSequentialCaseNumber(targetYear) {
  try {
    if (!fs.existsSync(casesDirFallback)) return 1;
    const files = fs.readdirSync(casesDirFallback).filter(f => f.toLowerCase().endsWith('.xml'));
    let maxNum = 0;
    for (const file of files) {
      const m = file.match(/K\s*(\d+)_(\d{4})\.xml/i);
      if (m) {
        const num = parseInt(m[1], 10);
        const yr = parseInt(m[2], 10);
        if (!Number.isNaN(num) && yr === targetYear && num > maxNum) {
          maxNum = num;
        }
      }
    }
    return maxNum + 1;
  } catch (err) {
    console.warn('⚠️  Greška pri određivanju rednog broja slučaja:', err.message);
    return Math.floor(Date.now() % 10000) || 1;
  }
}

function normalizeVerdictLabel(vrstaPresude = '') {
  const v = String(vrstaPresude || '').toLowerCase().trim();
  if (v === 'uslovna' || v === 'uslovna osuda' || v === 'uslovna presuda') return 'Uslovna presuda';
  if (v === 'oslobadjajuca' || v === 'oslobađajuća' || v === 'oslobađajuca') return 'Oslobađajuća';
  if (v === 'osudjujuca' || v === 'osuđujuća' || v === 'osuđujuca') return 'Osuđujuća';
  if (v === 'sudska opomena' || v === 'opomena') return 'Sudska opomena';
  return 'Osuđujuća';
}

function describeSentence(decision = {}) {
  const months = parseFloat(decision.kaznaUMjesecima);
  const fine = parseFloat(decision.novcanaKazna);

  if (!Number.isNaN(months) && months > 0) {
    const n = Number.isInteger(months) ? String(months) : String(months);
    return `${n} mjeseci`;
  }
  if (!Number.isNaN(fine) && fine > 0) {
    return `novčana kazna ${fine} EUR`;
  }
  return 'Nije navedeno';
}

function extractMonthsFromText(text = '') {
  const match = String(text).match(/(\d+(?:[.,]\d+)?)\s*(mesec|mjesec|month)/i);
  return match ? parseFloat(match[1].replace(',', '.')) : null;
}

function deriveDecisionFromSignals(ruleReasoning = {}, cbrReasoning = {}, decisionOverride = {}) {
  const cbrRec = cbrReasoning?.recommendation || {};
  const ruleVerdictRaw = String(ruleReasoning.verdict || '');
  const ruleRecommendationText = String(ruleReasoning.recommendation || '');
  const ruleIsAcquittal = Boolean(ruleReasoning.acquittal) || ruleVerdictRaw.toLowerCase().includes('oslob');
  const conditionalChance = Number(cbrRec.conditionalSentenceLikelihood || 0);

  let verdict = 'osudjujuca';
  if (decisionOverride.vrstaPresude) {
    verdict = decisionOverride.vrstaPresude;
  } else if (ruleIsAcquittal) {
    verdict = 'oslobadjajuca';
  } else if (ruleRecommendationText.toLowerCase().includes('uslov') || conditionalChance >= 60) {
    verdict = 'uslovna';
  }

  const ruleMonths = extractMonthsFromText(ruleRecommendationText) || extractMonthsFromText(ruleReasoning.actual_sentence || '');
  const cbrMonths = Number.isFinite(cbrRec.kaznaUMjesecima) ? Number(cbrRec.kaznaUMjesecima) : null;
  let kazna = 0;
  if (Number.isFinite(decisionOverride.kaznaUMjesecima)) {
    kazna = decisionOverride.kaznaUMjesecima;
  } else if (Number.isFinite(ruleMonths) && Number.isFinite(cbrMonths)) {
    kazna = Math.round((ruleMonths + cbrMonths) / 2);
  } else if (Number.isFinite(ruleMonths)) {
    kazna = Math.round(ruleMonths);
  } else if (Number.isFinite(cbrMonths)) {
    kazna = Math.round(cbrMonths);
  }

  let novcana = Number.isFinite(decisionOverride.novcanaKazna) ? decisionOverride.novcanaKazna : 0;
  if (!novcana && Number.isFinite(cbrRec.novcanaKazna)) {
    novcana = Number(cbrRec.novcanaKazna);
  }

  return {
    vrstaPresude: verdict,
    kaznaUMjesecima: kazna,
    novcanaKazna: novcana,
    uslovnaOsuda: verdict === 'uslovna' ? 'Da' : (decisionOverride.uslovnaOsuda || 'Ne'),
  };
}

function buildReasoningSummary(ruleReasoning = {}, cbrReasoning = {}) {
  const applied = (ruleReasoning.articles || []).join(', ');
  const rec = ruleReasoning.recommendation || 'n/a';
  const cbrRec = cbrReasoning.recommendation || {};
  const cbrText = cbrRec.kaznaUMjesecima != null ? `CBR kazna ${cbrRec.kaznaUMjesecima} mes, uslovna ${cbrRec.conditionalSentenceLikelihood || 0}%` : 'CBR n/a';
  const similar = (cbrReasoning.similarCases || []).slice(0, 3).map((c) => c.brojPredmeta).filter(Boolean).join(', ');
  return `Primenjeni članci: ${applied || 'n/a'}. Rule preporuka: ${rec}. ${cbrText}. Slični: ${similar || 'nema'}.`;
}

function generateNarrativeSections(input, decision, ruleReasoning = {}, cbrReasoning = {}) {
  const summary = buildReasoningSummary(ruleReasoning, cbrReasoning);

  const listFromText = (value) => String(value || '').split(/\r?\n|;/).map((v) => v.trim()).filter(Boolean);
  const evidences = listFromText(input.dokazi);
  const witnesses = listFromText(input.svjedoci);

  const sudMjesto = String(input.sud || 'Podgorici').trim();
  const sudLabel = `Osnovni sud u ${sudMjesto}`;
  const verdictMap = { osudjujuca: 'Osuđujuća', uslovna: 'Uslovna presuda', oslobadjajuca: 'Oslobađajuća' };
  const verdictLabel = verdictMap[decision.vrstaPresude] || 'Osuđujuća';

  // Extract mitigating/aggravating factors from rule reasoning
  const mitigating = (ruleReasoning.mitigating_factors || ruleReasoning.olaksavajuce || []);
  const aggravating = (ruleReasoning.aggravating_factors || ruleReasoning.otezavajuce || []);
  const appliedArticles = (ruleReasoning.articles || []).join(', ') || input.clanKZ || '';
  const ruleRec = String(ruleReasoning.recommendation || '');

  // CBR similar cases info
  const cbrRec = cbrReasoning?.recommendation || {};
  const similarCases = (cbrReasoning?.similarCases || []).slice(0, 3);
  const similarCasesText = similarCases.map(c => `${c.brojPredmeta} (sličnost ${c.similarity}%, kazna ${c.kaznaUMjesecima} mj.)`).join('; ');

  // --- Use Markov chain ML model to generate sentencing justification ---
  // The Markov model generates legal phrasing learned from 129 real court decisions.
  // We use it specifically for the sentencing section (generic legal formulas),
  // NOT for case-specific facts (which would produce incoherent text).
  const markovSentencing = generateMarkovText('sentencing', decision.uslovnaOsuda === 'Da' ? 'USLOVNU OSUDU' : 'kaznu zatvora', 60);
  const usedMarkov = !!markovSentencing;

  // Build introduction
  const introduction = `U IME CRNE GORE, ${sudLabel}, po sudiji ${input.sudija || 'NN'}, uz učešće zapisničara ${input.zapisnicar || 'NN'}, u krivičnom predmetu protiv okrivljenog ${input.okrivljeni || 'NN'}, zbog krivičnog djela ${input.tipKrivicnogDjela || ''} iz ${input.clanKZ || ''} Krivičnog zakonika Crne Gore, nakon održanog glavnog pretresa, donio je dana ${input.datumPresude || 'NN'} sljedeću PRESUDU:`;

  // Build background from case description
  const background = input.opis || 'Nije naveden opis slučaja.';

  // Build motivation - entirely case-specific using reasoning results
  let motivationParts = [];

  motivationParts.push(`Optuženom ${input.okrivljeni || 'NN'} stavljeno je na teret krivično djelo ${input.tipKrivicnogDjela || ''} iz ${appliedArticles || input.clanKZ || ''} Krivičnog zakonika Crne Gore.`);

  motivationParts.push(`Sud je cijenio sve izvedene dokaze${evidences.length > 0 ? ' (' + evidences.join(', ') + ')' : ''} pojedinačno i u međusobnoj vezi, te utvrdio sljedeće činjenično stanje: ${input.opis || 'Nije navedeno.'}`);

  if (witnesses.length > 0) {
    motivationParts.push(`U dokaznom postupku saslušani su svjedoci: ${witnesses.join(', ')}.`);
  }

  motivationParts.push(`Cijeneći utvrđeno činjenično stanje, sud je našao da su se u radnjama okrivljenog stekla sva bitna obilježja krivičnog djela iz ${appliedArticles || input.clanKZ || ''} Krivičnog zakonika.`);

  // Sentencing justification - mitigating/aggravating factors
  if (mitigating.length > 0 || aggravating.length > 0) {
    let sanctionParts = [`Prilikom odluke o krivičnoj sankciji, sud je u smislu čl. 42 st. 1 Krivičnog zakonika cijenio sve okolnosti koje su od uticaja na njen izbor i visinu.`];
    if (mitigating.length > 0) {
      sanctionParts.push(`Na strani okrivljenog, kao olakšavajuće okolnosti sud je cijenio: ${mitigating.join(', ')}.`);
    }
    if (aggravating.length > 0) {
      sanctionParts.push(`Kao otežavajuće okolnosti sud je cijenio: ${aggravating.join(', ')}.`);
    }
    motivationParts.push(sanctionParts.join(' '));
  }

  if (ruleRec) {
    motivationParts.push(`Na osnovu rasuđivanja po pravilima, preporuka je: ${ruleRec}.`);
  }
  if (similarCasesText) {
    motivationParts.push(`Rasuđivanje po sličnim slučajevima (${similarCasesText}) dalo je preporučenu kaznu od ${cbrRec.kaznaUMjesecima != null ? cbrRec.kaznaUMjesecima + ' mjeseci' : 'N/A'}${cbrRec.conditionalSentenceLikelihood != null ? ', sa vjerovatnoćom uslovne presude ' + cbrRec.conditionalSentenceLikelihood + '%' : ''}.`);
  }

  // Markov-generated sentencing justification (ML-generated legal phrasing)
  if (markovSentencing) {
    motivationParts.push(markovSentencing);
  }

  motivationParts.push(`Imajući u vidu navedeno, odlučeno je kao u dispozitivu ove presude.`);
  const motivation = motivationParts.join(' ');

  // Build decision line
  let decisionLine;
  if (decision.vrstaPresude === 'oslobadjajuca') {
    decisionLine = `Na osnovu člana 363 st. 1 tač. 3 ZKP-a, okrivljeni ${input.okrivljeni || 'NN'} se OSLOBAĐA od optužbe da je izvršio krivično djelo ${input.tipKrivicnogDjela || ''} iz ${input.clanKZ || ''} Krivičnog zakonika Crne Gore, jer nije dokazano da je izvršio djelo za koje je optužen.`;
  } else if (decision.uslovnaOsuda === 'Da') {
    const provjeraMonths = Math.max(12, (decision.kaznaUMjesecima || 0) * 2);
    decisionLine = `Okrivljeni ${input.okrivljeni || 'NN'} proglašava se KRIVIM za krivično djelo ${input.tipKrivicnogDjela || ''} iz ${input.clanKZ || ''} Krivičnog zakonika Crne Gore, pa mu sud primjenom čl. 42, čl. 45, čl. 52, čl. 53 i čl. 54 Krivičnog zakonika izriče USLOVNU OSUDU kojom mu utvrđuje kaznu zatvora u trajanju od ${decision.kaznaUMjesecima || 0} mjeseci i istovremeno određuje da se ona neće izvršiti ako okrivljeni u roku od ${provjeraMonths} mjeseci od pravosnažnosti presude ne učini novo krivično djelo.${decision.novcanaKazna > 0 ? ` Okrivljenom se izriče i novčana kazna u iznosu od ${decision.novcanaKazna} EUR.` : ''}`;
  } else {
    decisionLine = `Okrivljeni ${input.okrivljeni || 'NN'} proglašava se KRIVIM za krivično djelo ${input.tipKrivicnogDjela || ''} iz ${input.clanKZ || ''} Krivičnog zakonika Crne Gore i OSUĐUJE SE na kaznu zatvora u trajanju od ${decision.kaznaUMjesecima || 0} mjeseci.${decision.novcanaKazna > 0 ? ` Okrivljenom se izriče i novčana kazna u iznosu od ${decision.novcanaKazna} EUR.` : ''}`;
  }

  return {
    introduction,
    background,
    motivation,
    decision: decisionLine,
    reasoningSummary: summary,
    generatorLabel: usedMarkov ? 'markov-chain' : 'template-fallback'
  };
}

function validateUserInput(input = {}) {
  const requiredFields = ['sud', 'sudija', 'zapisnicar', 'okrivljeni', 'datumPresude', 'clanKZ', 'opis'];
  for (const field of requiredFields) {
    if (!input[field]) {
      return `${field} je obavezno polje`;
    }
  }

  const numericChecks = [
    ['iznos', 0],
    ['ukupanIznos', 0],
    ['brojTransakcija', 0],
    ['brojOkrivljenih', 1],
    ['brojSvjedoka', 0],
    ['brojDokaza', 0],
  ];
  for (const [field, min] of numericChecks) {
    const value = Number(input[field]);
    if (Number.isNaN(value) || value < min) {
      return `${field} mora biti broj >= ${min}`;
    }
  }

  if (Number(input.ukupanIznos) < Number(input.iznos)) {
    return 'Ukupan iznos mora biti veći ili jednak pojedinačnom iznosu.';
  }

  return null;
}

module.exports = {
  parseCaseIdentity,
  getNextSequentialCaseNumber,
  deriveDecisionFromSignals,
  generateNarrativeSections,
  buildReasoningSummary,
  validateUserInput,
  normalizeVerdictLabel,
  describeSentence,
  extractMonthsFromText,
};
