#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to generate Akoma Ntoso XML files from court case txt files.
Processes cases for:
- Član 258 (Falsifikovanje novca - Counterfeit Money)
- Član 260 (Kreditne kartice - Credit Card Fraud)
"""

import os
import re
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Output directory
OUTPUT_DIR = r"data\cases\akomantoso"

def prettify_xml(elem):
    """Return a pretty-printed XML string."""
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('utf-8')

def sanitize_filename(case_number):
    """Convert case number to valid filename."""
    # Replace special chars
    name = case_number.replace('/', '_').replace(' ', '_').replace('.', '_')
    name = re.sub(r'[^A-Za-z0-9_]', '', name)
    return f"Case_{name}"

def extract_year_from_case(case_number):
    """Extract year from case number like K 182/2019"""
    match = re.search(r'/(\d{2,4})', case_number)
    if match:
        year = match.group(1)
        if len(year) == 2:
            year = '20' + year if int(year) < 50 else '19' + year
        return year
    return datetime.now().strftime('%Y')

def create_akomantoso_xml(case_data):
    """Create Akoma Ntoso XML structure for a case."""
    case_id = sanitize_filename(case_data['case_number'])
    year = extract_year_from_case(case_data['case_number'])
    date_str = case_data.get('date', f'{year}-01-01')
    
    # Create root element
    judgment = ET.Element('judgment')
    judgment.set('xmlns', 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0')
    judgment.set('name', f"Case {case_data['case_number']}")
    judgment.set('xml:lang', 'sr')
    
    # Meta section
    meta = ET.SubElement(judgment, 'meta')
    
    # Identification
    identification = ET.SubElement(meta, 'identification')
    identification.set('source', 'court')
    
    # FRBRWork
    frbr_work = ET.SubElement(identification, 'FRBRWork')
    ET.SubElement(frbr_work, 'FRBRthis').set('value', f'/akn/me/judgment/{case_id}/!main')
    ET.SubElement(frbr_work, 'FRBRuri').set('value', f'/akn/me/judgment/{case_id}')
    ET.SubElement(frbr_work, 'FRBRdate').set('date', date_str)
    ET.SubElement(frbr_work, 'FRBRnumber').set('value', case_data['case_number'])
    
    # FRBRExpression
    frbr_expr = ET.SubElement(identification, 'FRBRExpression')
    ET.SubElement(frbr_expr, 'FRBRthis').set('value', f'/akn/me/judgment/{case_id}/!exp')
    ET.SubElement(frbr_expr, 'FRBRuri').set('value', f'/akn/me/judgment/{case_id}')
    ET.SubElement(frbr_expr, 'FRBRdate').set('date', date_str)
    ET.SubElement(frbr_expr, 'FRBRlanguage').set('language', 'sr')
    
    # FRBRManifestation
    frbr_manif = ET.SubElement(identification, 'FRBRManifestation')
    ET.SubElement(frbr_manif, 'FRBRthis').set('value', f'/akn/me/judgment/{case_id}')
    ET.SubElement(frbr_manif, 'FRBRuri').set('value', f'/akn/me/judgment/{case_id}')
    ET.SubElement(frbr_manif, 'FRBRdate').set('date', date_str)
    
    # References
    references = ET.SubElement(meta, 'references')
    references.set('source', 'application')
    
    # Add article references based on crime type
    article = case_data.get('article', '258')
    ref = ET.SubElement(references, 'TLCReference')
    ref.set('eId', f'ref_Član_{article}')
    ref.set('href', f'/akn/me/act/criminal-code/glava-23#Član {article}')
    ref.set('showAs', f'Član {article}')
    
    # Add Član 75 for security measures
    ref75 = ET.SubElement(references, 'TLCReference')
    ref75.set('eId', 'ref_Član_75')
    ref75.set('href', '/akn/me/act/criminal-code/glava#Član 75')
    ref75.set('showAs', 'Član 75')
    
    # Body section
    body = ET.SubElement(judgment, 'body')
    
    # Background
    background = ET.SubElement(body, 'background')
    crime_type = case_data.get('crime_type', 'Falsifikovanje novca')
    court = case_data.get('court', 'Osnovni Sud')
    
    p1 = ET.SubElement(background, 'p')
    strong1 = ET.SubElement(p1, 'strong')
    strong1.text = "Vrsta krivičnog djela:"
    strong1.tail = f" {crime_type}"
    
    p2 = ET.SubElement(background, 'p')
    strong2 = ET.SubElement(p2, 'strong')
    strong2.text = "Predmet:"
    strong2.tail = f" {case_data['case_number']}"
    
    p3 = ET.SubElement(background, 'p')
    strong3 = ET.SubElement(p3, 'strong')
    strong3.text = "Sud:"
    strong3.tail = f" {court}"
    
    p4 = ET.SubElement(background, 'p')
    strong4 = ET.SubElement(p4, 'strong')
    strong4.text = "Pravni okvir:"
    strong4.tail = f" Krivični zakonik Crne Gore - Član {article}"
    
    # Narrative
    narrative = ET.SubElement(body, 'narrative')
    
    defendant = case_data.get('defendant', 'Okrivljeno lice')
    p_def = ET.SubElement(narrative, 'p')
    strong_def = ET.SubElement(p_def, 'strong')
    strong_def.text = "Okrivljeni:"
    strong_def.tail = f" {defendant}"
    
    p_crime = ET.SubElement(narrative, 'p')
    strong_crime = ET.SubElement(p_crime, 'strong')
    strong_crime.text = "Vrsta krivičnog djela:"
    strong_crime.tail = f" {crime_type}"
    
    description = case_data.get('description', 'Krivično djelo izvršeno sa direktnim umišljajem')
    p_desc = ET.SubElement(narrative, 'p')
    strong_desc = ET.SubElement(p_desc, 'strong')
    strong_desc.text = "Opis događaja:"
    strong_desc.tail = f" {description}"
    
    # Motivation
    motivation = ET.SubElement(body, 'motivation')
    
    p_art = ET.SubElement(motivation, 'p')
    strong_art = ET.SubElement(p_art, 'strong')
    strong_art.text = "Primijenjeni članovi:"
    strong_art.tail = f" Član {article} Krivičnog zakonika Crne Gore"
    
    p_qual = ET.SubElement(motivation, 'p')
    strong_qual = ET.SubElement(p_qual, 'strong')
    strong_qual.text = "Kvalifikacija:"
    strong_qual.tail = f" {crime_type} prema Članu {article} Krivičnog zakonika"
    
    p_proof = ET.SubElement(motivation, 'p')
    strong_proof = ET.SubElement(p_proof, 'strong')
    strong_proof.text = "Dokazivanje:"
    strong_proof.tail = " Krivično djelo je dokazano kroz:"
    
    ul = ET.SubElement(motivation, 'ul')
    evidence = case_data.get('evidence', ['Iskaze svjedoka', 'Materijalne dokaze', 'Iskaze okrivljenih'])
    for ev in evidence:
        li = ET.SubElement(ul, 'li')
        li.text = ev
    
    # Decision
    decision = ET.SubElement(body, 'decision')
    
    p_verdict = ET.SubElement(decision, 'p')
    strong_verdict = ET.SubElement(p_verdict, 'strong')
    strong_verdict.text = "PRESUDA:"
    
    verdict_type = case_data.get('verdict', 'OSUĐEN')
    p_result = ET.SubElement(decision, 'p')
    strong_result = ET.SubElement(p_result, 'strong')
    strong_result.text = f"Okrivljeni je {verdict_type}:"
    
    ul_dec = ET.SubElement(decision, 'ul')
    li1 = ET.SubElement(ul_dec, 'li')
    strong_li1 = ET.SubElement(li1, 'strong')
    strong_li1.text = "Za krivično djelo:"
    strong_li1.tail = f" {crime_type} prema Članu {article} Krivičnog zakonika Crne Gore"
    
    sentence = case_data.get('sentence', 'Kazna zatvora')
    li2 = ET.SubElement(ul_dec, 'li')
    strong_li2 = ET.SubElement(li2, 'strong')
    strong_li2.text = "Kazna:"
    strong_li2.tail = f" {sentence}"
    
    p_costs = ET.SubElement(decision, 'p')
    strong_costs = ET.SubElement(p_costs, 'strong')
    strong_costs.text = "Troškovi:"
    strong_costs.tail = " Okrivljeni je obavezan da plati troškove krivičnog postupka"
    
    return judgment, case_id

def parse_date(date_str):
    """Parse date from various formats to YYYY-MM-DD."""
    months = {
        'januar': '01', 'februar': '02', 'mart': '03', 'april': '04',
        'maj': '05', 'jun': '06', 'jul': '07', 'avgust': '08',
        'septembar': '09', 'oktobar': '10', 'novembar': '11', 'decembar': '12'
    }
    
    # Try format: "19. Decembar 2019"
    match = re.search(r'(\d{1,2})\.\s*(\w+)\s*(\d{4})', date_str, re.IGNORECASE)
    if match:
        day = match.group(1).zfill(2)
        month_name = match.group(2).lower()
        year = match.group(3)
        month = months.get(month_name, '01')
        return f"{year}-{month}-{day}"
    
    return None

def extract_cases_from_file(filepath, crime_type, article):
    """Extract individual cases from a txt file."""
    cases = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            with open(filepath, 'r', encoding='cp1252') as f:
                content = f.read()
        except:
            return cases
    
    # Split by court headers - pattern for new cases
    case_blocks = re.split(r'\n(?=Osnovni Sud u [A-Za-zčćžšđČĆŽŠĐ]+\n)', content)
    
    for block in case_blocks:
        if not block.strip():
            continue
            
        case_data = {}
        
        # Extract court
        court_match = re.search(r'Osnovni Sud u ([A-Za-zčćžšđČĆŽŠĐ]+)', block)
        if court_match:
            case_data['court'] = f"Osnovni Sud u {court_match.group(1)}"
        else:
            continue  # Skip if no court found
        
        # Extract case number
        case_match = re.search(r'K\.?\s*(?:br\.?)?\s*(\d+/\d+)', block)
        if case_match:
            case_data['case_number'] = f"K {case_match.group(1)}"
        else:
            continue  # Skip if no case number
        
        # Extract date
        date_match = re.search(r'(\d{1,2}\.\s*\w+\s*\d{4})', block)
        if date_match:
            parsed_date = parse_date(date_match.group(1))
            if parsed_date:
                case_data['date'] = parsed_date
        
        # Set crime type and article
        case_data['crime_type'] = crime_type
        case_data['article'] = article
        
        # Extract defendant initials
        defendant_match = re.search(r'okrivljenog?\s+([A-ZČĆŽŠĐ])\.\s*([A-ZČĆŽŠĐ])\.?', block, re.IGNORECASE)
        if defendant_match:
            case_data['defendant'] = f"{defendant_match.group(1)}. {defendant_match.group(2)}."
        else:
            # Try another pattern
            defendant_match2 = re.search(r'okrivljen[io]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+)\s+([A-ZČĆŽŠĐ])', block)
            if defendant_match2:
                case_data['defendant'] = f"{defendant_match2.group(1)[0]}. {defendant_match2.group(2)}."
        
        # Extract sentence
        sentence_match = re.search(r'kazn[ua]\s+zatvora\s+u\s+trajanju\s+od\s+([\d]+)\s*(godin[ae]?|mjesec[ia]?)', block, re.IGNORECASE)
        if sentence_match:
            num = sentence_match.group(1)
            unit = sentence_match.group(2)
            case_data['sentence'] = f"Kazna zatvora u trajanju od {num} {unit}"
        else:
            # Check for conditional sentence
            if 'uslovna osuda' in block.lower() or 'uslovn' in block.lower():
                case_data['sentence'] = "Uslovna osuda"
        
        # Extract brief description
        if 'stavi' in block.lower() and 'opticaj' in block.lower():
            case_data['description'] = "Stavljanje lažnog novca u opticaj kao pravog"
        elif 'pribavi' in block.lower() and 'kartic' in block.lower():
            case_data['description'] = "Neovlašćeno pribavljanje i upotreba platne kartice"
        elif 'falsifik' in block.lower():
            case_data['description'] = "Falsifikovanje novca/kartice i stavljanje u promet"
        
        # Set evidence types based on crime
        if article == '258':
            case_data['evidence'] = [
                'Iskaze svjedoka',
                'Nalaze i mišljenja vještaka o falsifikaciji novčanica',
                'Potvrde o pronađenim i oduzetim novčanicama',
                'Izvještaj Centralne banke o tehničkoj analizi novca',
                'Iskaze okrivljenih'
            ]
        else:  # article 260
            case_data['evidence'] = [
                'Iskaze svjedoka',
                'Izvode sa bankovnih računa',
                'Potvrde o oduzetim platnim karticama',
                'Video zapise sa bankomata',
                'Iskaze okrivljenih'
            ]
        
        case_data['verdict'] = 'OSUĐEN'
        
        cases.append(case_data)
    
    return cases

def generate_xml_files():
    """Main function to generate all XML files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    generated_files = []
    
    # Process falsifikovanje novca (Article 258)
    novac_dir = r"archive\presude\falsifikovanje novca"
    if os.path.exists(novac_dir):
        for filename in os.listdir(novac_dir):
            if filename.endswith('.txt') and filename[0].isdigit():
                filepath = os.path.join(novac_dir, filename)
                cases = extract_cases_from_file(
                    filepath, 
                    "Falsifikovanje novca", 
                    "258"
                )
                for case in cases:
                    try:
                        xml_elem, case_id = create_akomantoso_xml(case)
                        xml_str = prettify_xml(xml_elem)
                        
                        output_path = os.path.join(OUTPUT_DIR, f"{case_id}.xml")
                        # Avoid overwriting existing files
                        counter = 1
                        while os.path.exists(output_path):
                            output_path = os.path.join(OUTPUT_DIR, f"{case_id}_{counter}.xml")
                            counter += 1
                        
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(xml_str)
                        generated_files.append(output_path)
                        print(f"Generated: {output_path}")
                    except Exception as e:
                        print(f"Error generating XML for case {case.get('case_number', 'unknown')}: {e}")
    
    # Process kreditne kartice (Article 260)
    kartice_dir = r"archive\presude\falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje"
    if os.path.exists(kartice_dir):
        for filename in os.listdir(kartice_dir):
            if filename.endswith('.txt') and filename[0].isdigit():
                filepath = os.path.join(kartice_dir, filename)
                cases = extract_cases_from_file(
                    filepath,
                    "Falsifikovanje i zloupotreba kreditnih kartica",
                    "260"
                )
                for case in cases:
                    try:
                        xml_elem, case_id = create_akomantoso_xml(case)
                        xml_str = prettify_xml(xml_elem)
                        
                        output_path = os.path.join(OUTPUT_DIR, f"{case_id}.xml")
                        counter = 1
                        while os.path.exists(output_path):
                            output_path = os.path.join(OUTPUT_DIR, f"{case_id}_{counter}.xml")
                            counter += 1
                        
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(xml_str)
                        generated_files.append(output_path)
                        print(f"Generated: {output_path}")
                    except Exception as e:
                        print(f"Error generating XML for case {case.get('case_number', 'unknown')}: {e}")
    
    return generated_files

if __name__ == "__main__":
    print("Starting Akoma Ntoso XML generation...")
    print("=" * 50)
    
    files = generate_xml_files()
    
    print("=" * 50)
    print(f"Total files generated: {len(files)}")
    print("XML generation complete!")
