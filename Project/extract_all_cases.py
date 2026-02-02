#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete data extraction from all available sources
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
import re

class ComprehensiveExtractor:
    def __init__(self):
        self.cases = {}
    
    def extract_from_xml(self, xml_file):
        """Extract available data from AkomaNtoso XML"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            case_id = xml_file.stem
            
            # Extract case number
            case_number = root.findtext('.//FRBRnumber', 'Unknown')
            
            # Extract case type
            case_type = root.findtext('.//FRBRname', 'Unknown')
            
            # Extract court
            court = 'Unknown'
            for p_elem in root.findall('.//background/p'):
                text = p_elem.text or ''
                if 'Sud:' in text:
                    court = text.replace('Sud: ', '').replace('Datum: None.', '').strip()
            
            # Extract verdict status
            decision_text = root.findtext('.//decision/p', '').lower()
            guilty = 'osudi' in decision_text or 'guilty' in decision_text
            acquitted = 'oslobodjen' in decision_text or 'acquitted' in decision_text
            
            # Extract articles
            articles = []
            for ref in root.findall('.//TLCReference'):
                showas = ref.get('showAs', '')
                if showas and 'Član' in showas:
                    articles.append(showas.split(' showAs=')[0] if ' showAs=' in showas else showas)
            
            return {
                'case_id': case_id,
                'case_number': case_number if case_number != 'Unknown' else case_id,
                'court': court,
                'case_type': case_type,
                'defendant': {'name': 'Unknown'},
                'verdict': {
                    'guilty': guilty,
                    'acquitted': acquitted,
                    'sentence_type': 'Unknown',
                    'sentence_duration_months': 'Unknown'
                },
                'articles': articles[:3] if articles else ['Unknown']
            }
        except Exception as e:
            print(f"Error parsing {xml_file}: {e}")
            return None
    
    def extract_from_text(self, text_file, case_number=None):
        """Extract data from verdict text file"""
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            text = ''.join(lines)
            
            # Extract court - usually first line with "Sud"
            court = 'Unknown'
            for line in lines[:20]:
                if 'Sud' in line and 'Email' not in line:
                    court = line.strip()
                    break
            
            # Extract case number - usually second line with "K"
            if not case_number:
                case_number = 'Unknown'
                for line in lines[:10]:
                    case_match = re.search(r'K[\s\.]*(\d+)[/\s](\d+)', line)
                    if case_match:
                        case_number = f"K {case_match.group(1)}/{case_match.group(2)}"
                        break
            
            # Extract defendant
            defendant = 'Unknown'
            defendant_match = re.search(r'(?:Optuženi|Okrivljeni)[\s,]+([A-Z][A-Z]\s*\.?[\s,]?[A-Z]\.?)', text)
            if defendant_match:
                defendant = defendant_match.group(1).strip()
            
            # Extract year from case number
            year_match = re.search(r'/(\d+)(?:\s*godina)?', text)
            year = 'Unknown'
            if year_match:
                year_num = int(year_match.group(1))
                year = f"20{year_num:02d}" if year_num <= 30 else f"19{year_num:02d}"
            
            # Check verdict
            guilty = bool(re.search(r'osudi|kazna', text, re.IGNORECASE))
            acquitted = bool(re.search(r'oslobodjen|odbija', text, re.IGNORECASE))
            
            # Extract sentence
            sentence_type = 'Unknown'
            sentence_duration = 'Unknown'
            
            prison_match = re.search(r'zatvor[a]?[u]?\s+u\s+trajanju\s+od\s+(\d+)\s*\(?(\w+)\)?', text, re.IGNORECASE)
            if prison_match:
                sentence_type = 'Prison'
                duration_num = prison_match.group(1)
                duration_unit = prison_match.group(2).lower()
                if 'mesec' in duration_unit or 'month' in duration_unit:
                    sentence_duration = f"{duration_num} months"
                elif 'god' in duration_unit or 'year' in duration_unit:
                    sentence_duration = f"{int(duration_num)*12} months"
            
            # Extract articles
            articles = []
            article_matches = re.findall(r'[Čč]lan[om]?\s+(\d{1,3})', text)
            for art in set(article_matches[:5]):  # Top 5 unique articles
                articles.append(f"Član {art}")
            
            return {
                'case_id': None,  # Will be assigned from XML
                'case_number': case_number,
                'court': court,
                'defendant': {'name': defendant},
                'year': year,
                'verdict': {
                    'guilty': guilty,
                    'acquitted': acquitted,
                    'sentence_type': sentence_type,
                    'sentence_duration_months': sentence_duration
                },
                'articles': articles if articles else ['Unknown']
            }
        except Exception as e:
            print(f"Error parsing {text_file}: {e}")
            return None
    
    def merge_data(self, xml_data, text_data):
        """Merge data from XML and text sources"""
        if text_data:
            xml_data['defendant'] = text_data.get('defendant', xml_data['defendant'])
            xml_data['year'] = text_data.get('year', 'Unknown')
            xml_data['verdict']['sentence_type'] = text_data['verdict'].get('sentence_type', 'Unknown')
            xml_data['verdict']['sentence_duration_months'] = text_data['verdict'].get('sentence_duration_months', 'Unknown')
            if text_data['articles']:
                xml_data['articles'] = text_data['articles']
        return xml_data

# Main processing
akomantoso_dir = Path(r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\akomantoso")
text_dir = Path(r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\archive\presude\falsifikovanje novca")

extractor = ComprehensiveExtractor()
all_cases = []

# Process all XML files
xml_files = sorted([f for f in akomantoso_dir.glob("Case_*.xml")])
text_files = sorted([f for f in text_dir.glob("*.txt")])

print(f"Found {len(xml_files)} XML files and {len(text_files)} text files\n")

# Map case numbers to text files
text_cache = {}
for i, txt_file in enumerate(text_files, 1):
    try:
        text_data = extractor.extract_from_text(txt_file)
        if text_data:
            case_num = text_data['case_number']
            text_cache[case_num] = text_data
            print(f"  📄 Text file {i}: {case_num} - {text_data['defendant']['name']}")
    except:
        pass

print()

# Process XML files and merge with text data
for xml_file in xml_files:
    xml_data = extractor.extract_from_xml(xml_file)
    if not xml_data:
        continue
    
    # Try to find matching text file
    text_data = text_cache.get(xml_data['case_number'])
    
    # Merge
    merged = extractor.merge_data(xml_data, text_data)
    all_cases.append(merged)
    
    status = "OK_COMPLETE" if text_data else "OK_PARTIAL"
    case_num = xml_data['case_number'][:15]
    court_name = xml_data['court'][:30] if xml_data['court'] != 'Unknown' else 'Unknown'
    defendant_name = merged['defendant']['name']
    print(f"{status:15} | {case_num:15} | {court_name:30}")

print(f"\n📊 Total cases processed: {len(all_cases)}")
complete_count = sum(1 for c in all_cases if c['defendant']['name'] != 'Unknown')
print(f"   Complete data: {complete_count}")
print(f"   Partial data: {len(all_cases) - complete_count}")

# Save to database
output_path = r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\DB\EXTRACTED_CASES_DATABASE.json"

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_cases, f, ensure_ascii=False, indent=2)

print(f"\n✅ Database saved: {output_path}")
