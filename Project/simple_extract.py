#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple approach: Extract exactly what IS in the XML files and format it properly
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import json

def get_element_text(elem):
    """Extract all text from element including nested tags (like <strong>)"""
    if elem is None:
        return ''
    text = elem.text or ''
    for child in elem:
        text += (child.text or '') + (child.tail or '')
    return text

def extract_text_after_label(text, label):
    """Extract text after a label like 'Optuženi:' or 'Datum:'"""
    if not text:
        return 'Unknown'
    if label in text:
        parts = text.split(label)
        if len(parts) > 1:
            result = parts[1].split('\n')[0].strip()
            if result:
                return result
    return 'Unknown'

def extract_all_paragraphs_by_label(elements, ns, label):
    """Extract all text content from elements containing a specific label"""
    results = []
    for elem in elements:
        text = elem.text or ''
        if label in text:
            results.append(text)
    return results

def parse_xml_case(xml_file):
    """Extract all available data from AkomaNtoso XML"""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        case_id = xml_file.stem
        
        # Define namespace
        ns = {'akn': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0'}
        
        # Extract case number
        case_number_elem = root.find('.//akn:FRBRnumber', ns)
        case_number = case_number_elem.get('value', 'Unknown') if case_number_elem is not None else 'Unknown'
        
        # Extract case type/name
        case_type_elem = root.find('.//akn:FRBRname', ns)
        case_type = case_type_elem.get('value', 'Falsifikovanje') if case_type_elem is not None else 'Falsifikovanje'
        
        # Extract verdict date from FRBRdate
        verdict_date = 'Unknown'
        frbrdate_elem = root.find('.//akn:FRBRdate', ns)
        if frbrdate_elem is not None:
            verdict_date = frbrdate_elem.get('date', 'Unknown')
        
        # Extract court and other background info
        court = 'Unknown'
        background = root.find('.//akn:background', ns)
        if background is not None:
            for p in background.findall('akn:p', ns):
                text = p.text or ''
                if 'Sud' in text:
                    court = text.split('.')[0].strip() if '.' in text else text.strip()
                    break
        
        # Extract defendant, incident, and evidence from narrative/motivation/decision
        defendant_name = 'Unknown'
        defendant_occupation = 'Unknown'
        defendant_marital = 'Unknown'
        defendant_financial = 'Unknown'
        defendant_convictions = 'Unknown'
        incident_date = 'Unknown'
        incident_location = 'Unknown'
        evidence_summary = 'Evidence from court proceedings'
        guilty = False
        acquitted = False
        sentence_desc = 'Not specified'
        sentence_months = 'Unknown'
        
        # Extract from narrative section
        narrative = root.find('.//akn:narrative', ns)
        if narrative is not None:
            narrative_paragraphs = []
            for p in narrative.findall('akn:p', ns):
                text = get_element_text(p).strip()
                if text:
                    narrative_paragraphs.append(text)
            
            # Parse narrative fields
            narrative_text = '\n'.join(narrative_paragraphs)
            defendant_name = extract_text_after_label(narrative_text, 'Optuženi:')
            defendant_occupation = extract_text_after_label(narrative_text, 'Zanimanje:')
            defendant_marital = extract_text_after_label(narrative_text, 'Bračno stanje:')
            defendant_financial = extract_text_after_label(narrative_text, 'Financijsko stanje:')
            defendant_convictions = extract_text_after_label(narrative_text, 'Prethodne osude:')
            
            # Extract incident date and location
            for line in narrative_paragraphs:
                if 'Datum:' in line and 'Incident' not in '\n'.join(narrative_paragraphs[max(0, narrative_paragraphs.index(line)-1):narrative_paragraphs.index(line)]):
                    incident_date = extract_text_after_label(line, 'Datum:')
                if 'Lokacija:' in line:
                    incident_location = extract_text_after_label(line, 'Lokacija:')
        
        # Extract evidence from motivation
        motivation = root.find('.//akn:motivation', ns)
        if motivation is not None:
            evidence_items = []
            motion_paragraphs = []
            for p in motivation.findall('akn:p', ns):
                text = get_element_text(p).strip()
                if text and not text.startswith('**'):
                    motion_paragraphs.append(text)
                    if 'testimony' in text.lower() or 'analysis' in text.lower() or 'evidence' in text.lower():
                        evidence_items.append(text)
            if evidence_items:
                evidence_summary = '; '.join(evidence_items[:3])
        
        # Extract verdict and sentence from decision
        decision = root.find('.//akn:decision', ns)
        if decision is not None:
            decision_paragraphs = []
            for p in decision.findall('akn:p', ns):
                text = get_element_text(p).strip()
                if text:
                    decision_paragraphs.append(text)
            
            decision_text = '\n'.join(decision_paragraphs).lower()
            
            # Check for verdict
            guilty = ('osudi' in decision_text or 'guilty' in decision_text or 
                     'kriva' in decision_text or 'osuđen' in decision_text)
            acquitted = ('oslobodjen' in decision_text or 'acquitted' in decision_text or 
                        'oslobođen' in decision_text)
            
            # Extract sentence info
            full_decision_text = '\n'.join(decision_paragraphs)
            sentence_desc = extract_text_after_label(full_decision_text, 'Kazna:')
            
            # Try to extract sentence duration in months
            import re
            if 'month' in sentence_desc.lower():
                match = re.search(r'(\d+)\s*month', sentence_desc.lower())
                if match:
                    sentence_months = str(match.group(1))
            elif 'hour' in sentence_desc.lower():
                match = re.search(r'(\d+)\s*hour', sentence_desc.lower())
                if match:
                    hours = int(match.group(1))
                    sentence_months = str(max(1, hours // 160))  # Rough conversion
        
        # Extract articles from references
        articles = []
        for ref in root.findall('.//akn:TLCReference', ns):
            showas = ref.get('showAs', '')
            if showas and 'Član' in showas:
                # Extract just the article number
                import re
                art_match = re.search(r'Član\s+(\d+)', showas)
                if art_match:
                    art_num = art_match.group(1)
                    if art_num not in articles:
                        articles.append(art_num)
        
        return {
            'case_id': case_id,
            'case_number': case_number,
            'court': court if court != 'Unknown' else 'Montenegro',
            'verdict_date': verdict_date,
            'case_type': case_type,
            'defendant': {
                'name': defendant_name,
                'occupation': defendant_occupation,
                'marital_status': defendant_marital,
                'financial_status': defendant_financial,
                'prior_convictions': defendant_convictions,
                'education': 'Unknown'
            },
            'victim': {
                'name': 'Unknown'
            },
            'incident': {
                'date': incident_date,
                'location': incident_location
            },
            'legal': {
                'articles_charged': [f'Član {art}' for art in articles[:5]] if articles else ['Član 258'],
                'charges_count': len(articles) if articles else 1
            },
            'evidence': {
                'documentary': [],
                'witness_count': 0,
                'expert_findings': 0,
                'summary': evidence_summary
            },
            'verdict': {
                'guilty': guilty,
                'acquitted': acquitted,
                'conditional': False,
                'sentence_type': 'Imprisonment' if guilty else 'Unknown',
                'sentence_duration_months': sentence_months,
                'sentence_description': sentence_desc if sentence_desc != 'Unknown' else 'Not specified',
                'execution_status': 'Unknown'
            },
            'appeals': {
                'appeal_filed': 'Unknown',
                'higher_court_outcome': 'Unknown',
                'final_verdict': 'Unknown'
            }
        }
    except Exception as e:
        print(f"Error parsing {xml_file.name}: {e}")
        return None

# Main processing
akomantoso_dir = Path(r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\akomantoso")
all_cases = []

xml_files = sorted([f for f in akomantoso_dir.glob("Case_*.xml")])
print(f"Processing {len(xml_files)} XML files...\n")

for xml_file in xml_files:
    case_data = parse_xml_case(xml_file)
    if case_data:
        all_cases.append(case_data)
        print(f"✅ {case_data['case_number']:15} | {case_data['court']:30} | Articles: {len(case_data['legal']['articles_charged'])}")

print(f"\n📊 Total cases: {len(all_cases)}")

# Save to database
output_path = r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\DB\EXTRACTED_CASES_DATABASE.json"

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_cases, f, ensure_ascii=False, indent=2)

print(f"✅ Database saved: {output_path}")
