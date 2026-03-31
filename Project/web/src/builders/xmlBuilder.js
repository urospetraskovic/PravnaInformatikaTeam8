function escapeXml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function normalizeVerdictLabel(vrstaPresude = '') {
  const v = String(vrstaPresude || '').toLowerCase().trim();
  if (v === 'uslovna' || v === 'uslovna osuda' || v === 'uslovna presuda') return 'Uslovna presuda';
  if (v === 'oslobadjajuca' || v === 'oslobađajuća' || v === 'oslobađajuca') return 'Oslobađajuća';
  if (v === 'osudjujuca' || v === 'osuđujuća' || v === 'osuđujuca') return 'Osuđujuća';
  if (v === 'sudska opomena' || v === 'opomena') return 'Sudska opomena';
  return 'Osuđujuća';
}

function formatSentence(decision = {}) {
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

function buildAkomaNtosoCaseXml(input, decision, identity, generated = {}) {
  const now = new Date();
  const inputDate = String(input.datumPresude || '').trim();
  const isoDate = /^\d{4}-\d{2}-\d{2}$/.test(inputDate) ? inputDate : now.toISOString().slice(0, 10);
  const caseNumber = String(input.brojPredmeta || identity.fallbackCaseNumber);
  const verdict = normalizeVerdictLabel(decision.vrstaPresude);
  const sentence = formatSentence(decision);
  const uslovna = String(decision.uslovnaOsuda || 'Ne');
  const sudMjesto = String(input.sud || 'Podgorici').trim();
  const sudLabel = `Osnovni Sud u ${sudMjesto}`;
  const tipDjela = String(input.tipKrivicnogDjela || '').trim();
  const clanKZ = String(input.clanKZ || '').trim();
  const opis = String(input.opis || 'Nije navedeno').trim();
  const zaposlenost = String(input.zaposlenost || 'nepoznat');
  const obrazovanje = String(input.obrazovanje || 'nepoznat');
  const ranijeOsudjivan = String(input.ranijeOsudjivan || 'nepoznat');
  const bracniStatus = String(input.bracniStatus || 'nepoznat');
  const sudija = String(input.sudija || 'Korisnički unos').trim();
  const zapisnicar = String(input.zapisnicar || 'Korisnički unos').trim();
  const okrivljeni = String(input.okrivljeni || 'Korisnički unos').trim();
  const brojTransakcija = parseInt(input.brojTransakcija ?? 0, 10);
  const brojOkrivljenih = parseInt(input.brojOkrivljenih ?? 1, 10);
  const brojSvjedoka = parseInt(input.brojSvjedoka ?? 0, 10);
  const brojDokaza = parseInt(input.brojDokaza ?? 0, 10);
  const ukupanIznos = parseFloat(input.ukupanIznos ?? input.iznos ?? 0);
  const fine = parseFloat(decision.novcanaKazna ?? 0);
  const cleanUkupanIznos = Number.isNaN(ukupanIznos) ? 0 : ukupanIznos;
  const cleanFine = Number.isNaN(fine) ? 0 : fine;

  const parseListInput = (value) =>
    String(value || '')
      .split(/\r?\n|;/)
      .map((item) => item.trim())
      .filter(Boolean);

  const witnessList = parseListInput(input.svjedoci);
  const evidenceList = parseListInput(input.dokazi);

  const computedWitnesses = witnessList.length > 0
    ? witnessList
    : Array.from({ length: Math.max(0, Number.isNaN(brojSvjedoka) ? 0 : brojSvjedoka) }, (_, idx) => `Svjedok ${idx + 1}`);

  const computedEvidence = evidenceList.length > 0
    ? evidenceList
    : Array.from({ length: Math.max(0, Number.isNaN(brojDokaza) ? 0 : brojDokaza) }, (_, idx) => `Dokaz ${idx + 1}`);

  const witnessXml = computedWitnesses.length > 0
    ? computedWitnesses.map((name) => `          <svjedok>${escapeXml(name)}</svjedok>`).join('\n')
    : '          <svjedok>Nije navedeno</svjedok>';

  const evidenceXml = computedEvidence.length > 0
    ? computedEvidence.map((item) => `          <dokaz>${escapeXml(item)}</dokaz>`).join('\n')
    : '          <dokaz>Nije navedeno</dokaz>';

  const motivationEvidenceXml = computedEvidence.length > 0
    ? computedEvidence.map((item) => `            <p>• ${escapeXml(item)}</p>`).join('\n')
    : '            <p>• Nije navedeno</p>';

  const genIntro = String(generated.introduction || '').trim() || `U IME CRNE GORE — ${sudLabel}, predmet ${caseNumber}, sudija ${sudija}.`;
  const genBackground = String(generated.background || '').trim() || `Opis činjeničnog stanja: ${opis}`;
  const genMotivation = String(generated.motivation || '').trim() || 'Obrazloženje je sastavljeno na osnovu unetog opisa, primenjenih članova i dostupnih dokaza.';
  const genDecision = String(generated.decision || '').trim() || `${verdict}: kazna ${sentence}.`;
  const genSummary = String(generated.reasoningSummary || '').trim();
  const generatorLabel = generated.generatorLabel || 'markov-chain';

  return `<?xml version="1.0" encoding="utf-8"?>
<akomaNtoso xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <judgment name="${escapeXml(identity.judgmentName)}">
    <meta>
      <identification source="#court">
        <FRBRWork>
          <FRBRthis value="/akn/me/judgment/${escapeXml(identity.judgmentName)}"/>
          <FRBRuri value="/akn/me/judgment/${escapeXml(identity.judgmentName)}"/>
          <FRBRdate date="${escapeXml(isoDate)}" name="judgment"/>
          <FRBRauthor href="#court"/>
          <FRBRcountry value="me"/>
        </FRBRWork>
        <FRBRExpression>
          <FRBRthis value="/akn/me/judgment/${escapeXml(identity.judgmentName)}/srp@${escapeXml(isoDate)}"/>
          <FRBRuri value="/akn/me/judgment/${escapeXml(identity.judgmentName)}/srp@${escapeXml(isoDate)}"/>
          <FRBRdate date="${escapeXml(isoDate)}" name="judgment"/>
          <FRBRauthor href="#court"/>
          <FRBRlanguage language="srp"/>
        </FRBRExpression>
        <FRBRManifestation>
          <FRBRthis value="/akn/me/judgment/${escapeXml(identity.judgmentName)}/srp@${escapeXml(isoDate)}.xml"/>
          <FRBRuri value="/akn/me/judgment/${escapeXml(identity.judgmentName)}/srp@${escapeXml(isoDate)}.xml"/>
          <FRBRdate date="${escapeXml(isoDate)}" name="generation"/>
          <FRBRauthor href="#system"/>
        </FRBRManifestation>
      </identification>
      <references source="#court">
        <TLCOrganization eId="court" href="/ontology/organization/me/${escapeXml(sudMjesto.toLowerCase().replace(/\s+/g, '_'))}" showAs="${escapeXml(sudLabel)}"/>
        <TLCPerson eId="sudija" href="/ontology/person/sudija_korisnicki_unos" showAs="${escapeXml(sudija)}"/>
        <TLCPerson eId="zapisnicar" href="/ontology/person/zapisnicar_korisnicki_unos" showAs="${escapeXml(zapisnicar)}"/>
        <TLCPerson eId="defendant" href="/ontology/person/okrivljeni_korisnicki_unos" showAs="${escapeXml(okrivljeni)}"/>
      </references>
      <proprietary source="#court">
        <sud>${escapeXml(sudMjesto)}</sud>
        <brojPredmeta>${escapeXml(caseNumber)}</brojPredmeta>
        <datum>${escapeXml(isoDate)}</datum>
        <datumNormalizovan>${escapeXml(isoDate)}</datumNormalizovan>
        <godina>${identity.year}</godina>
        <sudija>${escapeXml(sudija)}</sudija>
        <zapisnicar>${escapeXml(zapisnicar)}</zapisnicar>
        <okrivljeni>${escapeXml(okrivljeni)}</okrivljeni>
        <zaposlenost>${escapeXml(zaposlenost)}</zaposlenost>
        <obrazovanje>${escapeXml(obrazovanje)}</obrazovanje>
        <ranijeOsudjivan>${escapeXml(ranijeOsudjivan)}</ranijeOsudjivan>
        <tipKrivicnogDjela>${escapeXml(tipDjela)}</tipKrivicnogDjela>
        <clanKZ>${escapeXml(clanKZ)}</clanKZ>
        <brojTransakcija>${escapeXml(String(Number.isNaN(brojTransakcija) ? 0 : brojTransakcija))}</brojTransakcija>
        <brojOkrivljenih>${escapeXml(String(Number.isNaN(brojOkrivljenih) ? 1 : brojOkrivljenih))}</brojOkrivljenih>
        <brojSvjedoka>${escapeXml(String(Number.isNaN(brojSvjedoka) ? 0 : brojSvjedoka))}</brojSvjedoka>
        <brojDokaza>${escapeXml(String(Number.isNaN(brojDokaza) ? 0 : brojDokaza))}</brojDokaza>
        <kazna>${escapeXml(sentence)}</kazna>
        <uslovnaOsuda>${escapeXml(uslovna)}</uslovnaOsuda>
        <vrstaPresude>${escapeXml(verdict)}</vrstaPresude>
        <novcanaKazna>${escapeXml(String(cleanFine))}</novcanaKazna>
        <opisSlucaja>${escapeXml(opis)}</opisSlucaja>
        <generatedBy>${escapeXml(generatorLabel)}</generatedBy>
        <generationNote>${escapeXml(genSummary || 'Generisano kombinovanjem opisa, pravila i sličnih presuda.')}</generationNote>
        <iznosi>
          <iznos>${escapeXml(String(cleanUkupanIznos).replace('.', ','))} EUR</iznos>
        </iznosi>
        <svjedoci>
${witnessXml}
        </svjedoci>
        <dokazi>
${evidenceXml}
        </dokazi>
        <bracniStatus>${escapeXml(bracniStatus)}</bracniStatus>
      </proprietary>
    </meta>
    <judgmentBody>
      <introduction>
        <p>${escapeXml(genIntro)}</p>
      </introduction>
      <background>
        <p>${escapeXml(genBackground)}</p>
        <p>Okrivljeni: ${escapeXml(okrivljeni)}</p>
        <p>Zapisničar: ${escapeXml(zapisnicar)}</p>
        <p>Datum odluke: ${escapeXml(isoDate)}</p>
      </background>
      <arguments>
        <block name="opisSlucaja">
          <p>${escapeXml(opis)}</p>
        </block>
      </arguments>
      <motivation>
        <block name="dokazi">
          <tblock>
${motivationEvidenceXml}
          </tblock>
        </block>
        <block name="obrazlozenje">
          <p>${escapeXml(genMotivation)}</p>
        </block>
      </motivation>
      <decision>
        <block name="odluka">
          <p>${escapeXml(genDecision)}</p>
          <p>Kazna: ${escapeXml(sentence)}</p>
        </block>
      </decision>
    </judgmentBody>
    <conclusions>
      <block name="pravniOsnov">
        <p>Krivično djelo: ${escapeXml(tipDjela)} (${escapeXml(clanKZ)} Krivičnog zakonika Crne Gore)</p>
      </block>
      <block name="generatorMeta">
        <p>${escapeXml(genSummary || 'Generisano na osnovu opisa slučaja i rezultata rasuđivanja.')}</p>
      </block>
    </conclusions>
  </judgment>
</akomaNtoso>`;
}

module.exports = {
  escapeXml,
  normalizeVerdictLabel,
  formatSentence,
  buildAkomaNtosoCaseXml,
};
