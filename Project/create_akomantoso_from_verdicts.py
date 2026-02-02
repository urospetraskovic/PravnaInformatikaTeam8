#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse verdict text files and convert to AkomaNtoso XML judgment files
"""

import re
import json
from pathlib import Path
from datetime import datetime
from xml.dom import minidom

def extract_cases_from_verdict_file(text):
    """Extract individual case entries from verdict text"""
    cases = []
    
    # Split by Roman numerals (I, II, III, etc.) to find verdict sections
    # But first, let's find the main case info at the top
    case_number_match = re.search(r'K\.?br\.?\s*(\d+)/(\d+)', text)
    if not case_number_match:
        return []
    
    case_number = f"K {case_number_match.group(1)}/{case_number_match.group(2)}"
    
    # Find court
    court_match = re.search(r'(?:Osnovni|Viši)\s+Sud\s+(?:u|u)\s+([^\n]+?)(?:\n|$)', text)
    court = court_match.group(1).strip() if court_match else "Unknown"
    
    # Find date
    date_match = re.search(r'(\d{1,2})[.,]\s*(januar|februar|mart|april|maj|jun|jul|august|septembar|oktober|novembar|decembar)[.,]\s*(\d{4})', text, re.IGNORECASE)
    verdict_date = f"{date_match.group(3)}-" if date_match else "Unknown"
    
    # Find verdict sections - look for patterns like "Optuženi," or "K r i v j e"
    # Split by major sections
    sections = re.split(r'\n\s*(?:I{1,3}|IV|V|VI|VII|VIII|IX|X)\s*\n', text)
    
    case_info = {
        'case_number': case_number,
        'court': court,
        'verdict_date': verdict_date,
        'full_text': text[:2000]  # Store first 2000 chars as summary
    }
    
    return [case_info]

def create_akomantoso_judgment_xml(case_number, court, verdict_date, defendant_name, verdict_type, sentence, articles):
    """Generate proper AkomaNtoso judgment XML"""
    
    # Clean up inputs
    case_id = case_number.replace(' ', '_').replace('/', '_')
    verdict_guilty = verdict_type.lower() in ['guilty', 'osudjen', 'osuđen']
    
    # Create XML structure
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<judgment xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0" name="Case ' + case_number + '" xml:lang="sr">',
        '  <meta>',
        '    <identification source="court">',
        '      <FRBRWork>',
        '        <FRBRthis value="/akn/me/judgment/Case_' + case_id + '/!main"/>',
        '        <FRBRuri value="/akn/me/judgment/Case_' + case_id + '"/>',
        '        <FRBRdate date="' + (verdict_date if verdict_date != "Unknown" else "None") + '"/>',
        '        <FRBRcountry value="me"/>',
        '        <FRBRnumber value="' + case_number + '"/>',
        '        <FRBRname value="Falsifikovanje novca"/>',
        '      </FRBRWork>',
        '      <FRBRExpression>',
        '        <FRBRthis value="/akn/me/judgment/Case_' + case_id + '/sr@' + (verdict_date if verdict_date != "Unknown" else "2000-01-01") + '/!main"/>',
        '        <FRBRuri value="/akn/me/judgment/Case_' + case_id + '/sr@' + (verdict_date if verdict_date != "Unknown" else "2000-01-01") + '"/>',
        '        <FRBRdate date="' + (verdict_date if verdict_date != "Unknown" else "None") + '"/>',
        '        <FRBRlanguage language="sr"/>',
        '      </FRBRExpression>',
        '      <FRBRManifestation>',
        '        <FRBRthis value="/akn/me/judgment/Case_' + case_id + '/sr@' + (verdict_date if verdict_date != "Unknown" else "2000-01-01") + '/!main.xml"/>',
        '        <FRBRuri value="/akn/me/judgment/Case_' + case_id + '/sr@' + (verdict_date if verdict_date != "Unknown" else "2000-01-01") + '/!main.akn"/>',
        '        <FRBRdate date="' + datetime.now().strftime("%Y-%m-%d") + '"/>',
        '        <FRBRformat value="xml"/>',
        '      </FRBRManifestation>',
        '    </identification>',
        '    <references source="application">',
    ]
    
    # Add article references
    for article in articles[:5]:
        if article and article != "Unknown":
            xml_parts.append(f'      <TLCReference eId="ref_{article.replace(" ", "_")}" href="/akn/me/act/criminal-code#{article}" showAs="{article}"/>')
    
    xml_parts.extend([
        '    </references>',
        '  </meta>',
        '  <body>',
        '    <background>',
        f'      <p><strong>Sud:</strong> {court}</p>',
        f'      <p><strong>Broj predmeta:</strong> {case_number}</p>',
        f'      <p><strong>Datum presude:</strong> {verdict_date}</p>',
        f'      <p><strong>Vrsta krivičnog djela:</strong> Falsifikovanje novca</p>',
        '    </background>',
        '    <narrative>',
        f'      <p><strong>Optuženi:</strong> {defendant_name}</p>',
        '    </narrative>',
        '    <motivation>',
        f'      <p><strong>Primijenjeni članovi zakona:</strong></p>',
        '      <p>' + ', '.join(articles[:3]) if articles else '<p>Član 258' + '</p>',
        '    </motivation>',
        '    <decision>',
        f'      <p><strong>Presuda:</strong> {"Osudjen" if verdict_guilty else "Oslobođen"}</p>',
        f'      <p><strong>Kazna:</strong> {sentence}</p>',
        f'      <p><strong>Odluka:</strong> {"GUILTY" if verdict_guilty else "ACQUITTED"}</p>',
        '    </decision>',
        '  </body>',
        '</judgment>'
    ])
    
    return '\n'.join(xml_parts)

# Main extraction
verdict_dir = Path(r'c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\archive\presude\falsifikovanje novca')
output_dir = Path(r'c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\akomantoso_new')

# Create output directory
output_dir.mkdir(parents=True, exist_ok=True)

# Process verdict files
case_count = 0
for txt_file in sorted(verdict_dir.glob('*.txt')):
    if 'linkovi' in txt_file.name.lower():
        continue
    
    with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Extract case info
    cases = extract_cases_from_verdict_file(content)
    
    for case in cases:
        case_count += 1
        
        # Create XML file
        xml_content = create_akomantoso_judgment_xml(
            case['case_number'],
            case['court'],
            case['verdict_date'],
            'Defendant',
            'Unknown',
            'Not specified',
            ['Član 258']
        )
        
        # Save XML file
        case_id = case['case_number'].replace(' ', '_').replace('/', '_')
        xml_file = output_dir / f"Case_{case_id}.xml"
        
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"✅ Created: {xml_file.name}")

print(f"\n📊 Total cases extracted: {case_count}")
print(f"📁 Output directory: {output_dir}")
