// Similarity functions for different attribute types
function exactMatch(a, b) {
  if (!a || !b || a === 'nepoznat' || b === 'nepoznat') return 0.5;
  return a.toLowerCase() === b.toLowerCase() ? 1.0 : 0.0;
}

// Format city name to full court name "Osnovni sud u [city]"
function formatCourtName(city) {
  if (!city) return 'Nepoznat';
  const cityMap = {
    'rožaje': 'Rožajama', 'rozaje': 'Rožajama',
    'podgorica': 'Podgorici', 'podgoric': 'Podgorici',
    'nikšić': 'Nikšiću', 'niksic': 'Nikšiću',
    'bar': 'Baru',
    'kotor': 'Kotoru',
    'cetinje': 'Cetinju', 'cetinj': 'Cetinju',
    'herceg novi': 'Herceg Novom', 'herceg': 'Herceg Novom',
    'bijelo polje': 'Bijelom Polju', 'bijel': 'Bijelom Polju',
    'pljevlja': 'Pljevljima', 'pljevlj': 'Pljevljima',
    'plav': 'Plavu',
    'ulcinj': 'Ulcinju',
    'danilovgrad': 'Danilovgradu',
    'kolašin': 'Kolašinu', 'kolasin': 'Kolašinu',
    'berane': 'Beranama', 'berana': 'Beranama',
  };
  const cityLower = city.toLowerCase().trim();
  for (const [key, locative] of Object.entries(cityMap)) {
    if (cityLower.includes(key)) {
      return 'Osnovni sud u ' + locative;
    }
  }
  return 'Osnovni sud u ' + city;
}

// Map CBR verdict labels to display labels
function displayVerdict(vrstaPresude) {
  if (!vrstaPresude) return 'nepoznat';
  const v = vrstaPresude.toLowerCase().trim();
  if (v === 'osudjujuca' || v === 'osuđujuća' || v === 'osuđujuca' || v === 'zatvorska kazna') return 'zatvorska kazna';
  if (v === 'uslovna' || v === 'uslovna osuda' || v === 'uslovna presuda') return 'uslovna presuda';
  if (v === 'oslobadjajuca' || v === 'oslobađajuća' || v === 'oslobađajuca' || v === 'oslobođen' || v === 'oslobođena') return 'oslobadjajuca';
  return v;
}

function numericSimilarity(a, b, maxDiff) {
  const na = parseFloat(a), nb = parseFloat(b);
  if (isNaN(na) || isNaN(nb)) return 0.5;
  const diff = Math.abs(na - nb);
  return Math.max(0, 1.0 - diff / maxDiff);
}

function booleanSimilarity(a, b) {
  if (!a || !b || a === 'nepoznat' || b === 'nepoznat') return 0.5;
  return a.toLowerCase() === b.toLowerCase() ? 1.0 : 0.0;
}

// Compute weighted similarity between two CBR case records
function computeSimilarity(queryCase, targetCase) {
  const weights = {
    tipKrivicnogDjela: 5.0,
    clanKZ: 4.0,
    ranijeOsudjivan: 3.0,
    priznanje: 3.0,
    pokusaj: 2.5,
    saizvrsilastvo: 2.0,
    zaposlenost: 1.5,
    bracniStatus: 1.0,
    obrazovanje: 1.0,
    iznos: 10.0,
    ukupanIznos: 10.0,
    brojTransakcija: 1.5,
    brojOkrivljenih: 1.0,
    brojSvjedoka: 1.0,
    brojDokaza: 1.5,
  };

  let totalWeight = 0;
  let weightedSum = 0;

  // Categorical attributes
  for (const attr of ['tipKrivicnogDjela', 'clanKZ', 'zaposlenost', 'bracniStatus', 'obrazovanje']) {
    const w = weights[attr] || 1.0;
    totalWeight += w;
    weightedSum += w * exactMatch(queryCase[attr], targetCase[attr]);
  }

  // Boolean attributes
  for (const attr of ['ranijeOsudjivan', 'priznanje', 'pokusaj', 'saizvrsilastvo']) {
    const w = weights[attr] || 1.0;
    totalWeight += w;
    weightedSum += w * booleanSimilarity(queryCase[attr], targetCase[attr]);
  }

  // Numeric attributes
  const numericConfigs = [
    ['iznos', 10000], ['ukupanIznos', 50000], ['brojTransakcija', 50],
    ['brojOkrivljenih', 10], ['brojSvjedoka', 10], ['brojDokaza', 30],
  ];
  for (const [attr, maxDiff] of numericConfigs) {
    const w = weights[attr] || 1.0;
    totalWeight += w;
    weightedSum += w * numericSimilarity(queryCase[attr], targetCase[attr], maxDiff);
  }

  return totalWeight > 0 ? weightedSum / totalWeight : 0;
}

module.exports = {
  computeSimilarity,
  exactMatch,
  numericSimilarity,
  booleanSimilarity,
  formatCourtName,
  displayVerdict,
};
