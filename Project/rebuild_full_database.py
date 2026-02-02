#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebuild full database with all 22 cases - combining new data with old cases
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path

# First, load the 3 improved cases we just created
new_cases = [
    {
        "case_id": "Case_K_34_2014",
        "case_number": "K 34/2014",
        "court": "Osnovni Sud u Baru",
        "verdict_date": "2016-07-06",
        "case_type": "Falsifikovanje novca",
        "defendant": {"name": "H. G.", "occupation": "Keramičar", "marital_status": "Married", "financial_status": "Poor", "prior_convictions": "No"},
        "verdict": {"guilty": True, "acquitted": False, "sentence_type": "Prison", "sentence_duration_months": 12},
    },
    {
        "case_id": "Case_K_406_2011",
        "case_number": "K 406/2011",
        "court": "Osnovni Sud u Bijelom Polju",
        "verdict_date": "2011-11-24",
        "case_type": "Falsifikovanje novca",
        "defendant": {"name": "D.S.", "marital_status": "Married", "prior_convictions": "Yes"},
        "verdict": {"guilty": True, "acquitted": False, "sentence_type": "Prison", "sentence_duration_months": 6},
    },
    {
        "case_id": "Case_K_42_2022",
        "case_number": "K 42/2022",
        "court": "Osnovni Sud u Kotoru",
        "verdict_date": "2022-04-04",
        "case_type": "Falsifikovanje novca",
        "defendant": {"name": "T Š", "occupation": "Driver", "marital_status": "Married", "financial_status": "Medium", "prior_convictions": "Yes"},
        "verdict": {"guilty": True, "acquitted": False, "sentence_type": "Public work", "sentence_duration_months": 3},
    },
]

# Parse the AkomaNtoso files to extract all other cases
akomantoso_dir = Path(r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\akomantoso")
all_cases = []

# Add the 3 improved cases first
for case in new_cases:
    all_cases.append(case)

print(f"✅ Added 3 improved cases from new verdicts")

# Parse all other AkomaNtoso XML files to extract case data
for xml_file in sorted(akomantoso_dir.glob("Case_*.xml")):
    # Skip the new ones we already added
    if any(case["case_id"] in xml_file.name for case in new_cases):
        continue
    
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Remove namespace for easier parsing
        ns = {'akn': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0'}
        
        # Extract data from judgment
        frbr_number = root.findtext('.//FRBRnumber', 'Unknown')
        frbr_name = root.findtext('.//FRBRname', 'Unknown')
        frbr_date = root.findtext('.//FRBRdate[@date]', 'Unknown')
        
        # Try to get date from attribute
        date_elem = root.find('.//FRBRdate')
        if date_elem is not None and 'date' in date_elem.attrib:
            frbr_date = date_elem.attrib['date']
        
        background_text = root.findtext('.//background/p', '')
        
        # Extract court from background
        court = "Unknown"
        for p in root.findall('.//background/p'):
            if p.text and 'Sud' in p.text:
                court = p.text.replace('Sud: ', '').replace('<strong>', '').replace('</strong>', '').strip()
                break
        
        # Extract verdict status
        decision_text = root.findtext('.//decision/p', '').lower()
        guilty = 'kriva' in decision_text or 'guilty' in decision_text or 'osudi' in decision_text
        acquitted = 'oslobodjen' in decision_text or 'acquitted' in decision_text
        
        case_entry = {
            "case_id": xml_file.stem,
            "case_number": frbr_number if frbr_number != "Unknown" else xml_file.stem,
            "court": court,
            "verdict_date": frbr_date if frbr_date != "Unknown" else "Unknown",
            "case_type": frbr_name if frbr_name != "Unknown" else "Falsifikovanje",
            "defendant": {"name": "Unknown", "occupation": "Unknown"},
            "verdict": {
                "guilty": guilty,
                "acquitted": acquitted,
                "sentence_type": "Unknown",
                "sentence_duration_months": "Unknown"
            }
        }
        
        all_cases.append(case_entry)
        print(f"  ✅ Parsed {xml_file.stem}")
        
    except Exception as e:
        print(f"  ⚠️  Error parsing {xml_file.stem}: {e}")

print(f"\n📊 Total cases found: {len(all_cases)}")
print(f"   - 3 with complete data (new verdicts)")
print(f"   - {len(all_cases) - 3} with partial data (from AkomaNtoso)")

# Save the full database
output_path = r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\DB\EXTRACTED_CASES_DATABASE.json"

# Create simplified format for quick loading
simple_db = []
for case in all_cases:
    simple_db.append({
        "case_id": case["case_id"],
        "case_number": case["case_number"],
        "court": case.get("court", "Unknown"),
        "verdict_date": case.get("verdict_date", "Unknown"),
        "case_type": case.get("case_type", "Unknown"),
        "defendant": case.get("defendant", {"name": "Unknown"}),
        "verdict": case.get("verdict", {"guilty": False, "acquitted": False}),
    })

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(simple_db, f, ensure_ascii=False, indent=2)

print(f"\n✅ Updated database with all {len(all_cases)} cases")
print(f"📁 Saved to: {output_path}")
