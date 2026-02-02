#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Falsification Verdict Parser
Parses complex Montenegrin court verdicts and exports to multiple formats
"""

import re
import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, List, Any

class VerdictParser:
    """Parses falsification verdicts with advanced pattern matching"""
    
    def __init__(self):
        self.verdicts = []
    
    def parse_verdict_text(self, text: str, case_type: str = "Falsifikovanje novca") -> Dict[str, Any]:
        """
        Parse a complete verdict from raw text.
        Handles complex Serbian legal document formatting.
        """
        
        verdict = {
            "case_id": None,
            "case_number": None,
            "court": None,
            "judge": None,
            "verdict_date": None,
            "verdict_date_formatted": None,
            "case_type": case_type,
            "defendant": {
                "name": None,
                "father_name": None,
                "birthplace": None,
                "birth_year": None,
                "age": None,
                "citizenship": None,
                "occupation": None,
                "marital_status": None,
                "children": None,
                "education": None,
                "employment_status": None,
                "financial_status": None,
                "prior_convictions": None,
                "full_description": ""
            },
            "incident": {
                "date": None,
                "location": None,
                "narrative": "",
                "money_details": {
                    "total_amount": None,
                    "denominations": [],
                    "serial_numbers": []
                }
            },
            "legal": {
                "articles_charged": [],
                "charges_count": 0,
            },
            "evidence": {
                "witnesses": [],
                "expert_findings": [],
                "documents": []
            },
            "verdict": {
                "guilty": False,
                "acquitted": False,
                "conditional": False,
                "sentence_type": None,
                "sentence_duration_months": None,
                "sentence_description": ""
            },
            "appeals": {
                "appeal_filed": None,
                "higher_court_outcome": None
            }
        }
        
        # Split into sections for easier processing
        lines = text.split('\n')
        full_text = text
        
        # ============ EXTRACT CASE NUMBER & DATE ============
        for i, line in enumerate(lines):
            if re.search(r'K\.?\s*br\.?\s*\d', line):
                match = re.search(r'K\.?\s*br\.?\s*(\d+/\d+)', line)
                if match:
                    verdict["case_number"] = f"K {match.group(1)}"
                    verdict["case_id"] = f"Case_{match.group(1).replace('/', '_')}"
        
        # Extract date - look for patterns
        date_patterns = [
            r'(\d{1,2})\.\s*(novembar|decembar|januar|februar|mart|april|maj|juni|juli|august|septembar|oktobar)',
            r'([A-Z][a-z]+)\s+(\d{4})',
            r'(\d{1,2})\s*-?\s*(\d{1,2})\s*\.\s*(\d{4})',
        ]
        for pattern in date_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                if 'novembar' in match.group(0).lower():
                    month_match = re.search(r'(\d{1,2})\.\s*novembar\s*(\d{4})', match.group(0))
                    if month_match:
                        verdict["verdict_date"] = month_match.group(2)
                        verdict["verdict_date_formatted"] = f"{month_match.group(1)}. novembar {month_match.group(2)}"
                        break
        
        # ============ EXTRACT COURT ============
        for i, line in enumerate(lines):
            if 'SUD' in line.upper():
                court_match = re.search(r'(?:OSNOVNI |Osnovni )(?:SUD|Sud)\s+u?\s+([A-Z][a-zA-Z\s]*)', line, re.IGNORECASE)
                if court_match:
                    verdict["court"] = f"Osnovni Sud u {court_match.group(1).strip()}"
        
        # ============ EXTRACT DEFENDANT INFO ============
        # Look for defendant personal info block (typically after "optuženi" section)
        defendant_match = re.search(
            r'[Oo]puženi\s+([A-Z][A-Za-z\.]+),?\s+od\s+oca\s+([A-Za-z\.]+)\s+i\s+majke\s+([A-Za-z\.]+)',
            full_text
        )
        if defendant_match:
            verdict["defendant"]["name"] = defendant_match.group(1).strip()
            verdict["defendant"]["father_name"] = defendant_match.group(2).strip()
        
        # Extract birth info
        birth_match = re.search(r'rodjene?n?\s+\.\.\.\.?g?odine\s+u\s+([A-Z][a-zA-Z\s]+)', full_text)
        if birth_match:
            verdict["defendant"]["birthplace"] = birth_match.group(1).strip()
        
        # Extract education/status
        if 'nepismen' in full_text.lower():
            verdict["defendant"]["education"] = "Illiterate"
        elif 'pismen' in full_text.lower():
            verdict["defendant"]["education"] = "Literate"
            edu_match = re.search(r'završio\s+([^\n,]+)', full_text)
            if edu_match:
                verdict["defendant"]["education"] = edu_match.group(1).strip()
        
        # Extract marital status
        if 'neoženjen' in full_text.lower():
            verdict["defendant"]["marital_status"] = "Unmarried"
        elif 'oženjen' in full_text.lower():
            verdict["defendant"]["marital_status"] = "Married"
        
        if 'otac' in full_text.lower():
            children_match = re.search(r'otac\s+([a-z]+)\s+djete', full_text, re.IGNORECASE)
            if children_match:
                verdict["defendant"]["children"] = children_match.group(1)
        
        # Financial status
        if 'lošeg imovnog stanja' in full_text.lower():
            verdict["defendant"]["financial_status"] = "Poor"
        elif 'dobrog imovnog stanja' in full_text.lower():
            verdict["defendant"]["financial_status"] = "Good"
        
        # ============ EXTRACT INCIDENT DETAILS ============
        # Extract money amounts and serial numbers
        money_pattern = r'(\d+)\s*(?:papirn[a-z]*\s+)?novčanic[a-z]*\s+u\s+(?:apoenu\s+)?od\s+(\d+(?:\.\d+)?)\s*(?:KM|EUR|eura|€)'
        money_matches = re.findall(money_pattern, full_text, re.IGNORECASE)
        
        for count, amount in money_matches:
            verdict["incident"]["money_details"]["denominations"].append({
                "count": int(count),
                "amount": amount
            })
        
        # Extract serial numbers
        serial_pattern = r'(?:serij(?:skog\s+)?(?:slova\s+i\s+)?broja?\s+)?([A-Z]\d{7})'
        serials = re.findall(serial_pattern, full_text)
        verdict["incident"]["money_details"]["serial_numbers"] = list(set(serials))  # Remove duplicates
        
        # ============ EXTRACT LEGAL CHARGES ============
        # The ACTUAL charge is in the pattern: "čime je izvršio krivično djelo ... iz čl.XXX st.Y"
        # This is the ONLY article the defendant is actually guilty of
        # Other articles mentioned (like čl. 2, 4, 5, etc.) are procedural references, NOT charges
        
        # First, look for the actual crime pattern
        crime_pattern = r'čime je izvršio (?:produženo )?krivično djelo\s+(?:falsifikovanje|..+?)\s+iz\s+čl\.?\s*(\d+)(?:\s+st\.?\s*(\d+))?'
        crime_matches = re.findall(crime_pattern, full_text, re.IGNORECASE)
        
        if crime_matches:
            # Use only the FIRST match from the crime pattern (the actual charge)
            article_num, st = crime_matches[0]
            article_str = f"Član {article_num}"
            if st:
                article_str += f" st.{st}"
            article_str += " KZ CG"
            verdict["legal"]["articles_charged"].append(article_str)
        else:
            # Fallback: look for regular article pattern only in the "K r i v j e" section
            krivje_section = re.search(r'K r i v j e(.*?)(?:čime je|pa ga sud)', full_text, re.DOTALL | re.IGNORECASE)
            if krivje_section:
                section_text = krivje_section.group(1)
                article_pattern = r'(?:članom?|čl\.)\s+(\d+)(?:\s+st\.?\s*(\d+))?'
                articles = re.findall(article_pattern, section_text, re.IGNORECASE)
                
                for article_num, st in articles:
                    # Filter out procedural articles (small numbers like 2,4,5,13,15,32,36,42,45,46)
                    if int(article_num) > 100:  # Only charges, not procedural articles
                        article_str = f"Član {article_num}"
                        if st:
                            article_str += f" st.{st}"
                        article_str += " KZ CG"
                        if article_str not in verdict["legal"]["articles_charged"]:
                            verdict["legal"]["articles_charged"].append(article_str)
        
        # ============ EXTRACT VERDICT ============
        verdict_section = re.search(r'OSUDJ|OSLOBOD|PRAVOSNAŽNOST', full_text, re.IGNORECASE)
        if verdict_section:
            # Case-insensitive verdict matching
            if re.search(r'OSUDJ|Osuđ', full_text):
                verdict["verdict"]["guilty"] = True
            elif re.search(r'OSLOBOD', full_text):
                verdict["verdict"]["acquitted"] = True
        
        # ============ EXTRACT SENTENCE ============
        # Prison sentence patterns
        sentence_patterns = [
            (r'(?:zatvora?|prison)\s+u\s+trajanju\s+od\s+(\d+)\s*\.\?\s*\(([^\)]+)\)', 'months'),
            (r'(?:zatvora?|prison)\s+(?:od\s+)?(\d+)\s+(?:meseci?|mjeseci?|months)', 'months'),
            (r'(?:zatvora?|prison)\s+(\d+)\s+(?:meseci?|mjeseci?)', 'months'),
            (r'kaznu\s+zatvora\s+(\d+)\s*\.\s*\(([^\)]+)\)', 'months'),
        ]
        
        for pattern, unit in sentence_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                duration = match.group(1)
                verdict["verdict"]["sentence_duration_months"] = duration
                verdict["verdict"]["sentence_type"] = "Prison"
                if match.lastindex and match.lastindex > 1:
                    verdict["verdict"]["sentence_description"] = match.group(2)
                break
        
        # Full sentence text
        sentence_text_match = re.search(
            r'Na kaznu zatvora.*?\n',
            full_text
        )
        if sentence_text_match:
            verdict["verdict"]["sentence_description"] = sentence_text_match.group(0).strip()
        
        # Store full defendant description for reference
        defendant_block = re.search(
            r'[Oo]puženi\s+[A-Z].*?(?=\n\nK|K r i|^---)',
            full_text,
            re.MULTILINE | re.DOTALL
        )
        if defendant_block:
            verdict["defendant"]["full_description"] = defendant_block.group(0).strip()
        
        # Store incident narrative
        narrative_match = re.search(
            r'(?:Što je:|Incident:)(.*?)(?=čime je|pa ga sud|Branilac)',
            full_text,
            re.DOTALL | re.IGNORECASE
        )
        if narrative_match:
            incident_text = narrative_match.group(1).strip()
            # Clean up excess whitespace
            incident_text = re.sub(r'\s+', ' ', incident_text)
            verdict["incident"]["narrative"] = incident_text[:500]  # Limit to 500 chars
        
        return verdict
    
    def parse_multiple_verdicts(self, text: str, case_type: str = "Falsifikovanje novca") -> List[Dict]:
        """
        Parse multiple verdicts from a single text file.
        Splits by PRESUDA/P R E S U D U markers.
        """
        # Split by verdict boundaries
        verdict_blocks = re.split(r'(?:^|\n)(?:P R E S U D U|PRESUDA)(?:\n|$)', text, flags=re.MULTILINE)
        
        verdicts = []
        for block in verdict_blocks[1:]:  # Skip first (before any PRESUDA)
            if len(block.strip()) > 200:  # Only substantial blocks
                verdict = self.parse_verdict_text(block, case_type)
                if verdict.get("case_number"):  # Only if we found a case number
                    verdicts.append(verdict)
        
        return verdicts


class VerdictExporter:
    """Exports verdicts to various formats"""
    
    @staticmethod
    def to_json(verdicts: List[Dict], filepath: Path) -> None:
        """Export to JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(verdicts, f, ensure_ascii=False, indent=2)
        print(f"✓ Exported JSON: {filepath}")
    
    @staticmethod
    def to_csv(verdicts: List[Dict], filepath: Path) -> None:
        """Export to CSV"""
        if not verdicts:
            print("No verdicts to export")
            return
        
        fieldnames = [
            'case_id', 'case_number', 'court', 'verdict_date', 'case_type',
            'defendant_name', 'articles_charged', 'guilty', 'acquitted',
            'sentence_type', 'sentence_duration_months', 'incident_narrative'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for v in verdicts:
                writer.writerow({
                    'case_id': v.get('case_id', ''),
                    'case_number': v.get('case_number', ''),
                    'court': v.get('court', ''),
                    'verdict_date': v.get('verdict_date', ''),
                    'case_type': v.get('case_type', ''),
                    'defendant_name': v.get('defendant', {}).get('name', ''),
                    'articles_charged': ' | '.join(v.get('legal', {}).get('articles_charged', [])),
                    'guilty': v.get('verdict', {}).get('guilty', False),
                    'acquitted': v.get('verdict', {}).get('acquitted', False),
                    'sentence_type': v.get('verdict', {}).get('sentence_type', ''),
                    'sentence_duration_months': v.get('verdict', {}).get('sentence_duration_months', ''),
                    'incident_narrative': v.get('incident', {}).get('narrative', '')[:200],
                })
        
        print(f"✓ Exported CSV: {filepath}")
    
    @staticmethod
    def to_akomantoso(verdict: Dict) -> str:
        """Convert verdict to AkomaNtoso XML string"""
        
        judgment = ET.Element('judgment')
        judgment.set('name', f"Case {verdict.get('case_number', 'Unknown')}")
        judgment.set('{http://www.w3.org/XML/1998/namespace}lang', 'sr')
        judgment.set('xmlns', "http://docs.oasis-open.org/legaldocml/ns/akn/3.0")
        
        # METADATA
        meta = ET.SubElement(judgment, 'meta')
        
        identification = ET.SubElement(meta, 'identification')
        identification.set('source', 'court')
        
        # FRBR sections
        frbr_work = ET.SubElement(identification, 'FRBRWork')
        case_id = verdict.get('case_id', 'unknown')
        
        for elem_name, elem_value in [
            ('FRBRthis', {'value': f"/akn/me/judgment/{case_id}/!main"}),
            ('FRBRuri', {'value': f"/akn/me/judgment/{case_id}"}),
            ('FRBRdate', {'date': verdict.get('verdict_date', '2024')}),
            ('FRBRcountry', {'value': 'me'}),
            ('FRBRnumber', {'value': verdict.get('case_number', 'K 0000/00')}),
            ('FRBRname', {'value': verdict.get('case_type', 'Verdict')}),
        ]:
            elem = ET.SubElement(frbr_work, elem_name)
            for k, v in elem_value.items():
                elem.set(k, str(v))
        
        # References
        references = ET.SubElement(meta, 'references')
        references.set('source', 'application')
        
        for article in verdict.get('legal', {}).get('articles_charged', []):
            ref = ET.SubElement(references, 'TLCReference')
            article_num = re.search(r'(\d+)', article)
            if article_num:
                ref.set('eId', f"ref_art_{article_num.group(1)}")
                ref.set('href', f"/akn/me/act/criminal-code/glava-23#{article_num.group(1)}")
                ref.set('showAs', article)
        
        # BODY
        body = ET.SubElement(judgment, 'body')
        
        # Background
        background = ET.SubElement(body, 'background')
        bg_p = ET.SubElement(background, 'p')
        bg_p.text = f"Sud: {verdict.get('court', 'Neznano')}. Datum: {verdict.get('verdict_date_formatted', verdict.get('verdict_date', 'Neznano'))}."
        
        # Incident
        if verdict.get('incident', {}).get('narrative'):
            incident_section = ET.SubElement(body, 'narrative')
            inc_p = ET.SubElement(incident_section, 'p')
            inc_p.text = f"Incident: {verdict['incident']['narrative']}"
        
        # Motivation
        motivation = ET.SubElement(body, 'motivation')
        mot_p = ET.SubElement(motivation, 'p')
        articles_text = ', '.join(verdict.get('legal', {}).get('articles_charged', []))
        mot_p.text = f"Na osnovu člana {articles_text}."
        
        # Decision
        decision = ET.SubElement(body, 'decision')
        dec_p = ET.SubElement(decision, 'p')
        if verdict.get('verdict', {}).get('guilty'):
            dec_p.text = f"Okrivljeni je pronadjen KRIVIM. Kazna: {verdict.get('verdict', {}).get('sentence_description', 'Zatvora')}."
        else:
            dec_p.text = "Okrivljeni je oslobođen od optužbe."
        
        # Convert to string
        rough_string = ET.tostring(judgment, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("FALSIFICATION VERDICT PARSER AND EXPORTER")
    print("="*60 + "\n")
    
    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    archive_dir = project_root / "archive" / "presude"
    
    files_to_process = [
        (archive_dir / "falsifikovanje novca" / "1.txt", "Falsifikovanje novca"),
        (archive_dir / "falsifikovanje novca" / "2.txt", "Falsifikovanje novca"),
        (archive_dir / "falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje" / "1.txt", 
         "Falsifikovanje i zloupotreba kreditnih kartica"),
    ]
    
    parser = VerdictParser()
    all_verdicts = []
    
    # Parse all files
    for filepath, case_type in files_to_process:
        if filepath.exists():
            print(f"📖 Parsing: {filepath.name}...")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            verdicts = parser.parse_multiple_verdicts(content, case_type)
            all_verdicts.extend(verdicts)
            print(f"   ✓ Found {len(verdicts)} verdicts\n")
        else:
            print(f"⚠ File not found: {filepath}\n")
    
    print(f"\n📊 Total verdicts parsed: {len(all_verdicts)}")
    
    # Create output directories
    data_dir = project_root / "data"
    db_dir = data_dir / "cases" / "falsifikovanja"
    db_dir.mkdir(parents=True, exist_ok=True)
    
    akomantoso_dir = db_dir / "akomantoso"
    akomantoso_dir.mkdir(parents=True, exist_ok=True)
    
    exports_dir = data_dir / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    
    # Export individual AkomaNtoso files
    print("\n🔄 Generating AkomaNtoso XML files...")
    for i, verdict in enumerate(all_verdicts, 1):
        case_id = verdict.get('case_id') or f"Case_{i:03d}"
        xml_content = VerdictExporter.to_akomantoso(verdict)
        
        xml_file = akomantoso_dir / f"{case_id}.xml"
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f"   ✓ {case_id}.xml")
    
    # Export aggregated files
    print("\n💾 Exporting aggregated files...")
    
    VerdictExporter.to_json(all_verdicts, exports_dir / "FALSIFICATION_CASES.json")
    VerdictExporter.to_csv(all_verdicts, exports_dir / "FALSIFICATION_CASES.csv")
    
    print("\n✅ All exports completed!\n")
    print(f"📂 Files saved in: {db_dir}")
    print(f"📂 Exports saved in: {exports_dir}\n")
    
    # Print summary
    print("SUMMARY:")
    print(f"  Total verdicts: {len(all_verdicts)}")
    print(f"  Guilty verdicts: {sum(1 for v in all_verdicts if v.get('verdict', {}).get('guilty'))}")
    print(f"  Acquitted: {sum(1 for v in all_verdicts if v.get('verdict', {}).get('acquitted'))}")


if __name__ == '__main__':
    main()
