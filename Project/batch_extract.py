#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lightweight Batch Extractor - Processes verdict files one at a time
"""

import os
import sys
import time
import gc
import re

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enhanced_verdict_extractor import EnhancedVerdictExtractor, AkomaNtosoGenerator, split_cases_from_text

def main():
    # Directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, 'data', 'cases', 'akomantoso')
    
    # Clear existing XMLs except extraction_results.json
    print("Clearing old XML files...")
    for f in os.listdir(output_dir):
        if f.endswith('.xml'):
            os.remove(os.path.join(output_dir, f))
    print("Old XMLs cleared.")
    
    # Source directories
    dirs = [
        (os.path.join(base_dir, 'archive', 'presude', 'falsifikovanje novca'), 'falsifikovanje novca'),
        (os.path.join(base_dir, 'archive', 'presude', 'falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje'), 'falsifikovanje i zloupotreba kreditnih kartica')
    ]
    
    extractor = EnhancedVerdictExtractor()
    generator = AkomaNtosoGenerator(output_dir)
    
    total_cases = 0
    all_results = []
    used_ids = set()
    
    for source_dir, crime_type in dirs:
        print(f"\n=== Processing: {crime_type} ===")
        
        # Get numbered files only (skip link files)
        files = sorted([f for f in os.listdir(source_dir) if f.endswith('.txt') and f[0].isdigit()])
        
        for filename in files:
            filepath = os.path.join(source_dir, filename)
            print(f"\nProcessing: {filename}")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Split by "U IME CRNE GORE" to get individual cases
                cases = split_cases_from_text(content)
                
                print(f"  Found {len(cases)} cases in file")
                
                for i, case_text in enumerate(cases):
                    # Extract data
                    data = extractor.extract_all_data(case_text)
                    data['tip_krivicnog_djela'] = crime_type
                    
                    # Generate case ID
                    broj = data.get('broj_predmeta', '')
                    if broj and broj != 'Nepoznat':
                        base_id = 'Case_K_' + re.sub(r'[/\s]', '_', broj)
                    else:
                        base_id = f"Case_{filename.replace('.txt', '')}_{i+1}"
                    
                    # Ensure unique ID
                    case_id = base_id
                    suffix = 1
                    while case_id in used_ids:
                        case_id = f"{base_id}_{suffix}"
                        suffix += 1
                    used_ids.add(case_id)
                    
                    # Create and save XML
                    root, generated_id = generator.create_xml(data)
                    # Use our unique case_id instead of the generated one
                    root[0].set('name', case_id)
                    xml_path = generator.save_xml(root, case_id)
                    
                    total_cases += 1
                    
                    # Short description for logging
                    opis = data.get('opis_slucaja', '')[:50] + '...' if data.get('opis_slucaja') else 'N/A'
                    print(f"    Case {i+1}: {case_id} - Sud: {data.get('sud', 'N/A')}")
                    
                    all_results.append({
                        'case_id': case_id,
                        'broj_predmeta': data.get('broj_predmeta', 'Nepoznat'),
                        'sud': data.get('sud', 'Nepoznat'),
                        'tip': crime_type
                    })
                    
                    # Small pause to not overwhelm system
                    time.sleep(0.02)
                
                # Force garbage collection after each file
                gc.collect()
                
            except Exception as e:
                print(f"  ERROR: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    print(f"\n{'='*50}")
    print(f"DONE! Total cases extracted: {total_cases}")
    print(f"XML files saved to: {output_dir}")
    
    # Save results summary
    import json
    with open(os.path.join(output_dir, 'extraction_results.json'), 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
