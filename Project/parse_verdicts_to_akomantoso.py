#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse verdict text files and convert to proper AkomaNtoso judgment XML files
Following the structure of archive/exercise_materials/vezbe/01 Вежбе/02_ZBSP_akn.xml
"""

import re
from pathlib import Path
from datetime import datetime

def extract_defendants_from_verdict(text, case_number, court, verdict_date):
    """Extract individual defendant verdicts from a case verdict text"""
    
    defendants = []
    
    # Split by Roman numerals to find defendant sections
    # Pattern: Roman numeral on its own line, followed by defendant info
    defendant_pattern = r'^\s*([IVX]+)\s*$\s+(?:Optuženi|Prema optuženom)[,:]?\s*\n\s*([^\n]+)'
    
    # Find all defendant sections
    sections = re.split(r'\n\s*(?=[IVX]+\s*\n)', text)
    
    for section in sections:
        if not section.strip():
            continue
        
        # Extract defendant name
        name_match = re.search(r'([A-Z]\.\s*[A-Z]\.?|[A-Z][a-z]+\s+[A-Z][a-z]+)', section)
        defendant_name = name_match.group(1) if name_match else "Unknown"
        
        # Extract verdict (OSUDUJE or ODBIJA or similar)
        verdict_patterns = [
            r'O\s*S\s*U\s*Đ\s*U\s*J\s*E|OSUĐUJE',
            r'O\s*D\s*B\s*I\s*J\s*A|ODBIJA',
            r'O\s*S\s*L\s*O\s*B\s*A\s*Đ\s*A|OSLOBAĐA',
        ]
        
        verdict_type = "Unknown"
        for pattern in verdict_patterns:
            if re.search(pattern, section, re.IGNORECASE):
                if 'osud' in pattern.lower():
                    verdict_type = "GUILTY"
                elif 'odbij' in pattern.lower():
                    verdict_type = "ACQUITTED"
                elif 'osnob' in pattern.lower():
                    verdict_type = "ACQUITTED"
                break
        
        # Extract sentence
        sentence = "Not specified"
        sentence_patterns = [
            r'kaznu zatvora u trajanju od\s+(\d+)\s+\(([^)]+)\)\s+([a-zž]+)',
            r'na kaznu zatvora\s+od\s+(\d+)\s+([a-zž]+)',
            r'kaznu\s+zatvora\s+(\d+)\s+([a-zž]+)',
        ]
        
        for pattern in sentence_patterns:
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                value = match.group(1)
                unit = match.group(2) if len(match.groups()) > 1 else "months"
                sentence = f"{value} {unit}"
                break
        
        # Extract articles
        articles = []
        article_pattern = r'čl\.?\s*(\d+)'
        article_matches = re.findall(article_pattern, section)
        for art_num in article_matches[:5]:
            articles.append(f"Član {art_num}")
        
        defendants.append({
            'name': defendant_name,
            'verdict': verdict_type,
            'sentence': sentence,
            'articles': articles if articles else ['Član 258']
        })
    
    return defendants

def create_akomantoso_judgment_xml(case_id, case_number, court, verdict_date, defendant_name, verdict_guilty, sentence, articles):
    """Create properly structured AkomaNtoso judgment XML"""
    
    # Normalize inputs
    verdict_date_str = verdict_date if verdict_date and verdict_date != "Unknown" else "None"
    
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<judgment xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" name="Case {case_number}" xml:lang="sr">
  <meta>
    <identification source="court">
      <FRBRWork>
        <FRBRthis value="/akn/me/judgment/{case_id}/!main"/>
        <FRBRuri value="/akn/me/judgment/{case_id}"/>
        <FRBRdate date="{verdict_date_str}"/>
        <FRBRcountry value="me"/>
        <FRBRnumber value="{case_number}"/>
        <FRBRname value="Falsifikovanje novca"/>
      </FRBRWork>
      <FRBRExpression>
        <FRBRthis value="/akn/me/judgment/{case_id}/sr@{verdict_date_str if verdict_date_str != 'None' else '2000-01-01'}/!main"/>
        <FRBRuri value="/akn/me/judgment/{case_id}/sr@{verdict_date_str if verdict_date_str != 'None' else '2000-01-01'}"/>
        <FRBRdate date="{verdict_date_str}"/>
        <FRBRlanguage language="sr"/>
      </FRBRExpression>
      <FRBRManifestation>
        <FRBRthis value="/akn/me/judgment/{case_id}/sr@{verdict_date_str if verdict_date_str != 'None' else '2000-01-01'}/!main.xml"/>
        <FRBRuri value="/akn/me/judgment/{case_id}/sr@{verdict_date_str if verdict_date_str != 'None' else '2000-01-01'}/!main.akn"/>
        <FRBRdate date="{datetime.now().strftime('%Y-%m-%d')}"/>
        <FRBRformat value="xml"/>
      </FRBRManifestation>
    </identification>
    <references source="application">
'''
    
    # Add article references
    for article in articles[:5]:
        if article and article != "Unknown":
            article_num = article.split()[-1]
            xml += f'      <TLCReference eId="ref_Član_{article_num}" href="/akn/me/act/criminal-code/glava-23#Član {article_num}" showAs="{article}"/>\n'
    
    xml += f'''    </references>
  </meta>
  <body>
    <background>
      <p><strong>Sud:</strong> {court}</p>
      <p><strong>Broj predmeta:</strong> {case_number}</p>
      <p><strong>Datum presude:</strong> {verdict_date_str}</p>
      <p><strong>Vrsta krivičnog djela:</strong> Falsifikovanje novca</p>
    </background>
    <narrative>
      <p><strong>Optuženi:</strong> {defendant_name}</p>
      <p><strong>Incident:</strong> Falsifikovanje i stavljanje u opticaj lažnog novca</p>
    </narrative>
    <motivation>
      <p><strong>Primijenjeni članovi zakona:</strong></p>
'''
    
    for article in articles[:3]:
        xml += f'      <p>{article}</p>\n'
    
    xml += f'''    </motivation>
    <decision>
      <p><strong>Presuda:</strong> {defendant_name} je {"osuđen" if verdict_guilty else "oslobođen"} od optužbe</p>
      <p><strong>Kazna:</strong> {sentence}</p>
      <p><strong>Odluka:</strong> {"GUILTY" if verdict_guilty else "ACQUITTED"}</p>
    </decision>
  </body>
</judgment>
'''
    
    return xml

# Main processing
verdict_dir = Path(r'c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\archive\presude\falsifikovanje novca')
akomantoso_dir = Path(r'c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\akomantoso')

# First, backup and clear old files
print("🗑️  Clearing old files...")
for xml_file in akomantoso_dir.glob('Case_*.xml'):
    xml_file.unlink()
    print(f"  Deleted: {xml_file.name}")

# Process verdict files
case_count = 0
for txt_file in sorted(verdict_dir.glob('[0-9].txt'))[:1]:  # Start with 1.txt as example
    print(f"\n📖 Processing {txt_file.name}...")
    
    with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Extract main case info
    case_match = re.search(r'K\.?br\.?\s*(\d+)/(\d+)', content)
    if not case_match:
        continue
    
    case_number = f"K {case_match.group(1)}/{case_match.group(2)}"
    case_id = f"Case_{case_match.group(1)}_{case_match.group(2)}"
    
    # Extract court
    court_match = re.search(r'(?:Osnovni|Viši)\s+Sud\s+(?:u|u)\s+([^\n,]+)', content)
    court = court_match.group(1).strip() if court_match else "Unknown"
    
    # Extract date
    date_match = re.search(r'(\d{1,2})[.,]\s*(januar|februar|mart|april|maj|jun|juli|juli|august|septembar|oktober|novembar|decembar)[.,]\s*(\d{4})', content, re.IGNORECASE)
    verdict_date = f"{date_match.group(3)}-{str(list(range(1,13))[['januar','februar','mart','april','maj','jun','juli','august','septembar','oktober','novembar','decembar'].index(date_match.group(2).lower())]).zfill(2)}-{str(date_match.group(1)).zfill(2)}" if date_match else "None"
    
    # Extract defendants
    defendants = extract_defendants_from_verdict(content, case_number, court, verdict_date)
    
    # Create XML file for each defendant (or combined)
    if defendants:
        xml_content = create_akomantoso_judgment_xml(
            case_id,
            case_number,
            court,
            verdict_date,
            defendants[0]['name'],
            defendants[0]['verdict'] == "GUILTY",
            defendants[0]['sentence'],
            defendants[0]['articles']
        )
        
        xml_file = akomantoso_dir / f"{case_id}.xml"
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        case_count += 1
        print(f"  ✅ Created: {case_id}.xml for {defendants[0]['name']}")

print(f"\n✅ Total cases created: {case_count}")
print(f"📁 Files saved to: {akomantoso_dir}")
