#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Falsification Verdict Extractor and Converter
Extracts data from text verdicts and converts to AkomaNtoso XML, JSON, CSV
"""

import re
import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from datetime import datetime

class FalsificationExtractor:
    """Extracts structured data from falsification verdict texts"""
    
    def __init__(self):
        self.verdicts = []
        self.glava_23 = {}
        self.load_glava_23()
        
    def load_glava_23(self):
        """Load Glava 23 articles for reference"""
        glava_path = Path(__file__).parent.parent.parent / "archive" / "glava 23.txt"
        if glava_path.exists():
            with open(glava_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract articles
                articles = re.findall(r'Član (\d+)(.*?)(?=Član \d+|Pranje novca|$)', content, re.DOTALL)
                for article_num, article_text in articles:
                    self.glava_23[f"258"] = "Falsifikovanje novca"
                    self.glava_23[f"260"] = "Falsifikovanje i zloupotreba kreditnih kartica"
    
    def parse_verdict_text(self, text, verdict_type="novca"):
        """Parse a single verdict text and extract structured data"""
        verdict = {
            "case_id": None,
            "case_number": None,
            "court": None,
            "judge": None,
            "verdict_date": None,
            "case_type": "Falsifikovanje " + verdict_type,
            "defendant": {
                "name": None,
                "birthplace": None,
                "occupation": None,
                "marital_status": None,
                "children": None,
                "education": None,
                "employment_status": None,
                "financial_status": None,
                "prior_convictions": None,
            },
            "victim": {
                "name": None,
                "status": "Unknown",
                "harm_type": "Financial"
            },
            "incident": {
                "date": None,
                "location": None,
                "narrative": None,
                "money_amount": None,
                "money_denomination": None,
                "serial_numbers": [],
            },
            "legal": {
                "articles_charged": [],
                "charges_count": 0,
            },
            "evidence": {
                "documentary": [],
                "witness_count": 0,
                "expert_findings": 0,
                "physical_evidence": [],
            },
            "verdict": {
                "guilty": False,
                "acquitted": False,
                "conditional": False,
                "sentence_type": None,
                "sentence_duration_months": None,
            },
        }
        
        lines = text.split('\n')
        
        # Extract case number and court
        for i, line in enumerate(lines):
            if re.search(r'K\. br\.|K br\.', line):
                match = re.search(r'K\.? br\.? (\d+/\d+)', line)
                if match:
                    verdict["case_number"] = f"K {match.group(1)}"
                    verdict["case_id"] = f"Case_{match.group(1).replace('/', '_')}"
                
                # Court often on same line or nearby
                if 'SUD' in line.upper() or 'SUD' in lines[i-1].upper():
                    court_line = line if 'SUD' in line.upper() else lines[i-1]
                    court_match = re.search(r'(?:Osnovni |Osnovna )?[Ss]ud u? ([A-Z][^\n,]*)', court_line)
                    if court_match:
                        verdict["court"] = f"Osnovni Sud u {court_match.group(1).strip()}"
            
            # Extract verdict date
            if re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|januari|februar|mart|april|maj|juni|juli|august|septembar|oktobar|novembar|decembar|\d{1,2}\.\s*\d{1,2}\.\s*\d{4})', line, re.IGNORECASE):
                date_match = re.search(r'(\d{1,2})\.?\s*([A-Za-z]+|novembar|decembar|januar)\s*(\d{4})', line, re.IGNORECASE)
                if date_match:
                    verdict["verdict_date"] = date_match.group(3)
            
            # Extract defendant info from "osoba" or name patterns
            if re.search(r'optužen|defendant', line, re.IGNORECASE):
                # Look for personal info - often follows this line
                for j in range(i, min(i+5, len(lines))):
                    if re.search(r'od oca|of father|rođen|born', lines[j], re.IGNORECASE):
                        name_match = re.search(r'([A-Z]\.[A-Z]?\.?)', lines[j])
                        if name_match:
                            verdict["defendant"]["name"] = name_match.group(1)
                        
                        year_match = re.search(r'(\d{4})\.?god', lines[j])
                        if year_match:
                            verdict["defendant"]["birthplace"] = year_match.group(1)
            
            # Extract money details
            money_matches = re.findall(
                r'(\d+)\s*(novčanic|banknot|KM|EUR|eura|€)\s*(?:u apoenu od )?(\d+)',
                line, re.IGNORECASE
            )
            for match in money_matches:
                verdict["incident"]["money_amount"] = match[0]
                verdict["incident"]["money_denomination"] = match[2]
            
            # Extract serial numbers
            if re.search(r'serij[^:]*:', line, re.IGNORECASE):
                serials = re.findall(r'([A-Z]\d{7})', line)
                verdict["incident"]["serial_numbers"].extend(serials)
            
            # Extract articles charged
            if 'član' in line.lower() or 'article' in line.lower() or 'art\.' in line.lower():
                articles = re.findall(r'članom? (\d+)', line, re.IGNORECASE)
                for article in articles:
                    if article not in verdict["legal"]["articles_charged"]:
                        verdict["legal"]["articles_charged"].append(f"Član {article} KZ CG")
            
            # Extract verdict
            if 'OSUDJ' in line.upper() or 'OSUĐ' in line.upper():
                verdict["verdict"]["guilty"] = True
            elif 'OSLOBOD' in line.upper():
                verdict["verdict"]["acquitted"] = True
            
            # Extract sentence
            if re.search(r'zatvor|prison', line, re.IGNORECASE):
                sentence_match = re.search(r'(\d+)\s*(mesec|mjesec|month|god|year)', line, re.IGNORECASE)
                if sentence_match:
                    verdict["verdict"]["sentence_duration_months"] = sentence_match.group(1)
                    verdict["verdict"]["sentence_type"] = "Zatvora" if 'zatvor' in line.lower() else "Prison"
        
        return verdict
    
    def extract_from_file(self, filepath, verdict_type="novca"):
        """Extract all verdicts from a file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by verdict markers
        verdict_blocks = re.split(r'P R E S U D U|PRESUDA', content)
        
        extracted = []
        for block in verdict_blocks[1:]:  # Skip first split (header)
            if len(block.strip()) > 100:  # Only process substantial blocks
                verdict = self.parse_verdict_text(block, verdict_type)
                if verdict["case_number"]:
                    extracted.append(verdict)
        
        return extracted


class AkomaNtosoConverter:
    """Converts verdict data to AkomaNtoso XML"""
    
    AKOMANTOSO_NS = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0/WD17"
    
    def convert(self, verdict):
        """Convert verdict to AkomaNtoso XML"""
        
        judgment = ET.Element('judgment')
        judgment.set('name', f"Case {verdict.get('case_number', 'Unknown')}")
        judgment.set('{http://www.w3.org/XML/1998/namespace}lang', 'sr')
        judgment.set('xmlns', self.AKOMANTOSO_NS)
        
        # METADATA
        meta = self._create_metadata(verdict)
        judgment.append(meta)
        
        # BODY
        body = self._create_body(verdict)
        judgment.append(body)
        
        # CONCLUSIONS
        conclusions = ET.SubElement(judgment, 'conclusions')
        conc_p = ET.SubElement(conclusions, 'p')
        if verdict["verdict"]["guilty"]:
            conc_p.text = f"Okrivljeni je pronadjen KRIVIM za krivično djelo {verdict.get('case_type', 'unknown')} i osuđen je na kaznu zatvora."
        else:
            conc_p.text = f"Okrivljeni je oslobođen od optužbe."
        
        return judgment
    
    def _create_metadata(self, verdict):
        """Create metadata section"""
        meta = ET.Element('meta')
        
        identification = ET.SubElement(meta, 'identification')
        identification.set('source', '#court')
        
        # FRBR Work
        frbr_work = ET.SubElement(identification, 'FRBRWork')
        case_id = verdict.get('case_id', 'unknown')
        
        self._add_sub_element(frbr_work, 'FRBRthis', {'value': f"/akn/me/judgment/{case_id}/!main"})
        self._add_sub_element(frbr_work, 'FRBRuri', {'value': f"/akn/me/judgment/{case_id}"})
        self._add_sub_element(frbr_work, 'FRBRdate', {'date': verdict.get('verdict_date', '2024')})
        self._add_sub_element(frbr_work, 'FRBRcountry', {'value': 'me'})
        self._add_sub_element(frbr_work, 'FRBRnumber', {'value': verdict.get('case_number', 'K 0000/00')})
        self._add_sub_element(frbr_work, 'FRBRname', {'value': verdict.get('case_type', 'Judgment')})
        
        # FRBR Expression
        frbr_expr = ET.SubElement(identification, 'FRBRExpression')
        self._add_sub_element(frbr_expr, 'FRBRthis', {'value': f"/akn/me/judgment/{case_id}/sr@{verdict.get('verdict_date')}/!main"})
        self._add_sub_element(frbr_expr, 'FRBRuri', {'value': f"/akn/me/judgment/{case_id}/sr@{verdict.get('verdict_date')}"})
        self._add_sub_element(frbr_expr, 'FRBRlanguage', {'language': 'sr'})
        
        # References to articles
        references = ET.SubElement(meta, 'references')
        references.set('source', 'application')
        
        for article in verdict.get('legal', {}).get('articles_charged', []):
            ref = ET.SubElement(references, 'TLCReference')
            article_num = re.search(r'(\d+)', article).group(1) if re.search(r'\d+', article) else 'unknown'
            ref.set('eId', f"ref_art_{article_num}")
            ref.set('href', f"/akn/me/act/criminal-code/glava-23#{article_num}")
            ref.set('showAs', article)
        
        return meta
    
    def _create_body(self, verdict):
        """Create body section"""
        body = ET.Element('body')
        
        # Background
        background = ET.SubElement(body, 'background')
        background_p = ET.SubElement(background, 'p')
        background_p.text = f"Sud: {verdict.get('court', 'Unknown')}. Datum: {verdict.get('verdict_date', 'Unknown')}."
        
        # Incident narrative
        if verdict.get('incident', {}).get('narrative'):
            narrative = ET.SubElement(body, 'narrative')
            narr_p = ET.SubElement(narrative, 'p')
            narr_p.text = verdict['incident']['narrative']
        
        # Legal analysis
        legal_section = ET.SubElement(body, 'motivation')
        legal_p = ET.SubElement(legal_section, 'p')
        articles = ', '.join(verdict.get('legal', {}).get('articles_charged', []))
        legal_p.text = f"Na osnovu člana(a) {articles} Krivičnog Zakonika."
        
        return body
    
    def _add_sub_element(self, parent, tag, attrs):
        """Helper to add sub-element with attributes"""
        elem = ET.SubElement(parent, tag)
        for key, value in attrs.items():
            elem.set(key, str(value))
        return elem
    
    def prettify(self, elem):
        """Return a pretty-printed XML string"""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


def main():
    """Main execution"""
    
    # Initialize
    extractor = AkomaNtosoConverter()
    converter = AkomaNtosoConverter()
    
    # File paths
    verdicts_dir = Path(__file__).parent.parent.parent / "archive" / "presude"
    falsif_novca = verdicts_dir / "falsifikovanje novca" / "1.txt"
    falsif_kartica = verdicts_dir / "falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje" / "1.txt"
    
    all_verdicts = []
    
    # Extract from both files
    if falsif_novca.exists():
        print(f"Extracting from {falsif_novca}...")
        all_verdicts.extend(extractor.extract_from_file(str(falsif_novca), "novca"))
    
    if falsif_kartica.exists():
        print(f"Extracting from {falsif_kartica}...")
        all_verdicts.extend(extractor.extract_from_file(str(falsif_kartica), "kartica"))
    
    print(f"Extracted {len(all_verdicts)} verdicts")
    
    # Create output directories
    output_dir = Path(__file__).parent.parent / "cases" / "falsifikovanja"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    akomantoso_dir = output_dir / "akomantoso"
    akomantoso_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate files
    for i, verdict in enumerate(all_verdicts, 1):
        case_id = verdict.get("case_id") or f"Case_{i:03d}"
        
        # AkomaNtoso XML
        xml_root = converter.convert(verdict)
        xml_str = converter.prettify(xml_root)
        xml_file = akomantoso_dir / f"{case_id}.xml"
        with open(xml_file, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        print(f"Created {xml_file}")
    
    # JSON export
    json_file = Path(__file__).parent / "FALSIFICATION_CASES.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_verdicts, f, ensure_ascii=False, indent=2)
    print(f"Created {json_file}")
    
    # CSV export
    csv_file = Path(__file__).parent / "FALSIFICATION_CASES.csv"
    if all_verdicts:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['case_id', 'case_number', 'court', 'verdict_date', 'case_type', 
                         'defendant_name', 'articles_charged', 'guilty', 'sentence_type', 'sentence_duration']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for verdict in all_verdicts:
                writer.writerow({
                    'case_id': verdict.get('case_id', ''),
                    'case_number': verdict.get('case_number', ''),
                    'court': verdict.get('court', ''),
                    'verdict_date': verdict.get('verdict_date', ''),
                    'case_type': verdict.get('case_type', ''),
                    'defendant_name': verdict.get('defendant', {}).get('name', ''),
                    'articles_charged': '; '.join(verdict.get('legal', {}).get('articles_charged', [])),
                    'guilty': verdict.get('verdict', {}).get('guilty', False),
                    'sentence_type': verdict.get('verdict', {}).get('sentence_type', ''),
                    'sentence_duration': verdict.get('verdict', {}).get('sentence_duration_months', ''),
                })
        print(f"Created {csv_file}")

if __name__ == '__main__':
    main()
