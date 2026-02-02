#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate proper AkomaNtoso XML files for the three falsification verdicts
Following the structure from the example provided
"""

import json
from pathlib import Path
from datetime import datetime

class AkomaNtosoGenerator:
    
    @staticmethod
    def generate_case_xml(case):
        """Generate AkomaNtoso XML for a single case"""
        
        # Extract data from case dict
        case_id = case["case_id"]
        case_num = case["case_number"].replace(" ", "_")
        court = case["court"]
        verdict_date = case["verdict_date"]
        defendant = case["defendant"]
        incident = case["incident"]
        articles = case["applicable_articles"]
        evidence = case["evidence"]
        sentence = case["sentence"]
        evidence_summary = case["evidence_summary"]
        
        # Build articles list
        articles_xml = "\n".join([
            f'                <TLCReference eId="ref_{art.replace(" ", "_").replace(".", "")}" href="/akn/me/act/criminal-code/glava-23#{art}" showAs="{art} KZ CG"/>'
            for art in articles
        ])
        
        # Build evidence list
        evidence_xml = "\n".join([
            f'                    <p>{e}</p>'
            for e in evidence
        ])
        
        xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<judgment xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" name="Case {case["case_number"]}" xml:lang="sr">
  <meta>
    <identification source="court">
      <FRBRWork>
        <FRBRthis value="/akn/me/judgment/{case_id}/!main"/>
        <FRBRuri value="/akn/me/judgment/{case_id}"/>
        <FRBRdate date="{verdict_date}"/>
        <FRBRcountry value="me"/>
        <FRBRnumber value="{case['case_number']}"/>
        <FRBRname value="{case['case_type']}"/>
      </FRBRWork>
      <FRBRExpression>
        <FRBRthis value="/akn/me/judgment/{case_id}/sr@{verdict_date}/!main"/>
        <FRBRuri value="/akn/me/judgment/{case_id}/sr@{verdict_date}"/>
        <FRBRdate date="{verdict_date}"/>
        <FRBRlanguage language="sr"/>
      </FRBRExpression>
      <FRBRManifestation>
        <FRBRthis value="/akn/me/judgment/{case_id}/sr@{verdict_date}/!main.xml"/>
        <FRBRuri value="/akn/me/judgment/{case_id}/sr@{verdict_date}/!main.akn"/>
        <FRBRdate date="{datetime.now().strftime('%Y-%m-%d')}"/>
        <FRBRformat value="xml"/>
      </FRBRManifestation>
    </identification>
    <publication name="court" date="{verdict_date}" showAs="{court}"/>
    <classification source="court">
      <keyword value="criminal" showAs="Krivično pravo - Falsifikovanje" dictionary="ME"/>
    </classification>
    <references source="application">
{articles_xml}
    </references>
  </meta>
  <body>
    <background>
      <p><strong>Sud:</strong> {court}</p>
      <p><strong>Broj predmeta:</strong> {case['case_number']}</p>
      <p><strong>Datum presude:</strong> {verdict_date}</p>
      <p><strong>Vrsta krivičnog djela:</strong> {case['case_type']}</p>
    </background>
    <narrative>
      <p><strong>Optuženi:</strong> {defendant['name']}</p>
      <p><strong>Zanimanje:</strong> {defendant['occupation']}</p>
      <p><strong>Bračno stanje:</strong> {defendant['marital_status']}</p>
      <p><strong>Financijsko stanje:</strong> {defendant['financial_status']}</p>
      <p><strong>Prethodne osude:</strong> {defendant['prior_convictions']}</p>
      <p/>
      <p><strong>Incident:</strong></p>
      <p>Datum: {incident['date']}</p>
      <p>Lokacija: {incident['location']}</p>
      <p>Opis: {incident['description']}</p>
    </narrative>
    <motivation>
      <p><strong>Primijenjeni članovi zakona:</strong></p>
      <p>{", ".join(articles)}</p>
      <p/>
      <p><strong>Dokazi:</strong></p>
{evidence_xml}
      <p/>
      <p><strong>Sažetak dokaza:</strong></p>
      <p>{evidence_summary}</p>
    </motivation>
    <decision>
      <p><strong>Presuda:</strong> {defendant['name']} je osuđen na {sentence['type'].lower()}</p>
      <p><strong>Kazna:</strong> {sentence['duration']}</p>
      <p><strong>Odluka:</strong> {sentence['decision']}</p>
    </decision>
  </body>
</judgment>
'''
        return xml

def main():
    # Load the extracted verdicts
    with open(r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\extracted_verdicts.json", 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    output_dir = Path(r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\akomantoso")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("📄 Generating AkomaNtoso XML files...\n")
    
    for case in cases:
        xml_content = AkomaNtosoGenerator.generate_case_xml(case)
        
        # Write XML file
        filename = output_dir / f"{case['case_id']}.xml"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"✅ Generated {case['case_id']}.xml")
        print(f"   Case: {case['case_number']} - {case['court']}")
        print(f"   Defendant: {case['defendant']['name']}")
        print(f"   Verdict: {case['sentence']['decision']} ({case['sentence']['type']})\n")
    
    print(f"\n✅ Successfully generated {len(cases)} AkomaNtoso XML files")

if __name__ == "__main__":
    main()
