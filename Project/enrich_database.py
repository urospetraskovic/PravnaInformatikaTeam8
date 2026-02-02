#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enrich the database by extracting additional data from verdict text files
"""

import json
import re
from pathlib import Path

def extract_verdict_data(text):
    """Extract verdict information from text"""
    verdict_data = {
        'defendant_name': None,
        'verdict_guilty': None,
        'sentence': None,
        'details': None
    }
    
    # Look for OSUĐUJE (Found Guilty) or similar patterns
    if 'OSUĐUJE' in text or 'Osuđuje' in text:
        verdict_data['verdict_guilty'] = True
    elif 'OSLOBAĐA' in text or 'Oslobađa' in text:
        verdict_data['verdict_guilty'] = False
    
    # Look for sentence duration (e.g., "1 (jedne) godine" for 1 year)
    sentence_patterns = [
        r'kaznu zatvora[^,]*?od\s+(\d+)\s*\(\s*[^)]+\)\s*(\w+)',
        r'na kaznu\s+(\d+)\s*(\w+)',
        r'zatvora.*?od\s+(\d+)\s*(\w+)',
    ]
    
    for pattern in sentence_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1)
            unit = match.group(2).lower() if len(match.groups()) > 1 else 'months'
            
            if 'godine' in unit or 'year' in unit:
                months = int(value) * 12
            elif 'mjeseca' in unit or 'month' in unit:
                months = int(value)
            elif 'dana' in unit or 'day' in unit:
                months = max(1, int(value) // 30)
            else:
                months = int(value)
            
            verdict_data['sentence'] = {
                'duration_months': months,
                'description': match.group(0)[:100]
            }
            break
    
    return verdict_data

def find_case_number_in_text(text):
    """Extract case number from verdict text and normalize it"""
    # Look for "K.br.XX/YY" or "K XX/YY" pattern
    patterns = [
        r'K\.br\.(\d+)/(\d+)',
        r'K\s*br\.(\d+)/(\d+)',
        r'K\s+(\d+)/(\d+)',
        r'K\.(\d+)/(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            case_num = f"K {match.group(1)}/{match.group(2)}"
            return case_num
    
    return None

def match_case_number(text_case_num, db_case_numbers):
    """Try to find matching case in database, handling format variations"""
    if text_case_num in db_case_numbers:
        return text_case_num
    
    # Try converting abbreviated years (14 -> 2014, 19 -> 2019, etc.)
    match = re.match(r'K\s+(\d+)/(\d+)', text_case_num)
    if match:
        num, year = match.groups()
        
        # If year is 2 digits, try converting to 4 digits
        if len(year) == 2:
            # Try 20XX format
            for century in ['20', '19', '21']:
                variant = f'K {num}/{century}{year}'
                if variant in db_case_numbers:
                    return variant
        
        # Also check if full year format exists
        for db_case in db_case_numbers:
            db_match = re.match(r'K\s+(\d+)/(\d+)', db_case)
            if db_match and db_match.group(1) == num:
                # Same case number, possibly different year format
                return db_case
    
    return None

def enrich_database():
    """Enrich database with verdict file data"""
    
    # Load current database
    db_path = Path(r'c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\DB\EXTRACTED_CASES_DATABASE.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    # Create case number -> case data mapping
    case_map = {case['case_number']: case for case in cases}
    db_case_numbers = set(case_map.keys())
    
    # Process verdict files
    verdict_dir = Path(r'c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\archive\presude')
    
    enriched_count = 0
    
    for txt_file in verdict_dir.rglob('*.txt'):
        # Skip index/link files
        if 'linkovi' in txt_file.name.lower() or 'index' in txt_file.name.lower():
            continue
        
        try:
            with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract case number from text
            text_case_number = find_case_number_in_text(content)
            if not text_case_number:
                continue
            
            # Try to match with database case
            db_case_number = match_case_number(text_case_number, db_case_numbers)
            if not db_case_number:
                continue
            
            # Get verdict data
            verdict_info = extract_verdict_data(content)
            case = case_map[db_case_number]
            
            # Update case if we found new information
            if verdict_info['verdict_guilty'] is not None:
                case['verdict']['guilty'] = verdict_info['verdict_guilty']
                case['verdict']['acquitted'] = not verdict_info['verdict_guilty']
                enriched_count += 1
                print(f"✅ Enriched {db_case_number}: Guilty={verdict_info['verdict_guilty']}")
            
            if verdict_info['sentence']:
                case['verdict']['sentence_duration_months'] = str(verdict_info['sentence']['duration_months'])
        
        except Exception as e:
            print(f"Error processing {txt_file.name}: {e}")
    
    # Save enriched database
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Database enriched: {enriched_count} cases updated with verdict information")
    return enriched_count

if __name__ == '__main__':
    enrich_database()
