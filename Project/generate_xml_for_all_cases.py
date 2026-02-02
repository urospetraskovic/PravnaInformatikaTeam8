#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate AKOmanToso XML files for all cases in the database
"""

import json
import os
from pathlib import Path
from datetime import datetime

def generate_xml_for_case(case_data):
    """Generate AKOmanToso XML for a single case"""
    
    case_id = case_data.get("case_id", "Unknown")
    case_number = case_data.get("case_number", "Unknown")
    court = case_data.get("court", "Unknown")
    case_type = case_data.get("case_type", "Unknown")
    verdict_date = case_data.get("verdict_date", "Unknown")
    
    # Extract defendant info
    defendant = case_data.get("defendant", {})
    if isinstance(defendant, dict):
        defendant_name = defendant.get("name", "Unknown")
    else:
        defendant_name = str(defendant)
    
    # Extract verdict info
    verdict = case_data.get("verdict", {})
    if isinstance(verdict, dict):
        verdict_description = verdict.get("sentence_description", "Not specified")
        if verdict.get("guilty"):
            decision = "GUILTY"
        elif verdict.get("acquitted"):
            decision = "ACQUITTED"
        elif verdict.get("conditional"):
            decision = "CONDITIONAL"
        else:
            decision = "UNKNOWN"
    else:
        verdict_description = str(verdict)
        decision = "UNKNOWN"
    
    # Extract articles
    legal = case_data.get("legal", {})
    articles = legal.get("articles_charged", [])
    
    articles_xml = "\n".join([
        f'                <TLCReference eId="ref_{art.replace(" ", "_").replace(".", "")}" href="/akn/me/act/criminal-code/glava-23#{art}" showAs="{art}"/>'
        for art in articles
    ]) if articles else ''
    
    # Extract incident
    incident = case_data.get("incident", {})
    if isinstance(incident, dict):
        incident_location = incident.get("location", "Unknown")
    else:
        incident_location = str(incident)
    
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<judgment xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" name="Case {case_number}" xml:lang="sr">
  <meta>
    <identification source="court">
      <FRBRWork>
        <FRBRthis value="/akn/me/judgment/{case_id}/!main"/>
        <FRBRuri value="/akn/me/judgment/{case_id}"/>
        <FRBRdate date="{verdict_date}"/>
        <FRBRcountry value="me"/>
        <FRBRnumber value="{case_number}"/>
        <FRBRname value="{case_type}"/>
      </FRBRWork>
      <FRBRExpression>
        <FRBRthis value="/akn/me/judgment/{case_id}/sr@2000-01-01/!main"/>
        <FRBRuri value="/akn/me/judgment/{case_id}/sr@2000-01-01"/>
        <FRBRdate date="{verdict_date}"/>
        <FRBRlanguage language="sr"/>
      </FRBRExpression>
      <FRBRManifestation>
        <FRBRthis value="/akn/me/judgment/{case_id}/sr@2000-01-01/!main.xml"/>
        <FRBRuri value="/akn/me/judgment/{case_id}/sr@2000-01-01/!main.akn"/>
        <FRBRdate date="{datetime.now().strftime('%Y-%m-%d')}"/>
        <FRBRformat value="xml"/>
      </FRBRManifestation>
    </identification>
    <references source="application">
{articles_xml}
    </references>
  </meta>
  <body>
    <background>
      <p><strong>Sud:</strong> {court}</p>
      <p><strong>Broj predmeta:</strong> {case_number}</p>
      <p><strong>Datum presude:</strong> {verdict_date}</p>
      <p><strong>Vrsta krivičnog djela:</strong> {case_type}</p>
    </background>
    <narrative>
      <p><strong>Optuženi:</strong> {defendant_name}</p>
      <p><strong>Lokacija incidenta:</strong> {incident_location}</p>
    </narrative>
    <motivation>
      <p><strong>Primijenjeni članovi zakona:</strong></p>
      <p>{", ".join(articles) if articles else "Unknown"}</p>
    </motivation>
    <decision>
      <p><strong>Presuda:</strong> {decision}</p>
      <p><strong>Opis kazne:</strong> {verdict_description}</p>
      <p><strong>Odluka:</strong> {decision}</p>
    </decision>
  </body>
</judgment>
'''
    
    return xml

def main():
    # Load database
    db_path = Path("data/cases/DB/EXTRACTED_CASES_DATABASE.json")
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return
    
    with open(db_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    print(f"📋 Loaded {len(cases)} cases from database")
    
    # Create output directory if it doesn't exist
    output_dir = Path("data/cases/akomantoso")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate XML for each case
    generated = 0
    skipped = 0
    
    for i, case in enumerate(cases, 1):
        case_id = case.get("case_id", f"case_{i}")
        
        # Skip if XML already exists
        xml_file = output_dir / f"{case_id}.xml"
        if xml_file.exists():
            print(f"⏭️  {i:2d}. {case.get('case_number', 'Unknown'):15s} - XML already exists")
            skipped += 1
            continue
        
        try:
            xml_content = generate_xml_for_case(case)
            
            with open(xml_file, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            print(f"✅ {i:2d}. {case.get('case_number', 'Unknown'):15s} → {xml_file.name}")
            generated += 1
        except Exception as e:
            print(f"❌ {i:2d}. {case.get('case_number', 'Unknown'):15s} - Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Generated: {generated} new XML files")
    print(f"   ⏭️  Skipped: {skipped} existing files")
    print(f"   📁 Output directory: {output_dir}")

if __name__ == "__main__":
    main()
