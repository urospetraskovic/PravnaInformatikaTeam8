#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Montenegrin Legal Case-Based Reasoning Engine
Advanced rule-based reasoning for criminal court cases using DR-Device rules
"""

import sys
import json
import argparse
from pathlib import Path
import re
import io
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Optional
import os
import glob

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Project root for archive lookups
PROJECT_ROOT = Path(__file__).parent


class ArchiveFactsExtractor:
    """Extract additional facts from archive text files using NLP patterns"""
    
    ARCHIVE_FOLDERS = [
        'archive/presude/falsifikovanje novca',
        'archive/presude/falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje'
    ]
    
    def __init__(self, case_number: str, project_root: Path = None):
        self.case_number = case_number
        self.project_root = project_root or PROJECT_ROOT
        self.archive_text = ""
        self.extracted_facts = {}
        self.load_archive_text()
        if self.archive_text:
            self.extract_all_facts()
    
    def _normalize_case_number(self, case_num: str) -> str:
        """Convert case number to archive file format (K 100/10 -> K 1002010)"""
        # Remove spaces around slashes
        normalized = case_num.strip()
        # Match pattern like "100/10" or "K 100/10" or "100/2010"
        match = re.search(r'(\d+)[/_](\d+)', normalized)
        if match:
            num = match.group(1)
            year = match.group(2)
            # Convert 2-digit year to 4-digit
            if len(year) == 2:
                year = '20' + year if int(year) < 50 else '19' + year
            return f"K {num}{year}"
        return normalized
    
    def load_archive_text(self):
        """Find and load the corresponding archive text file"""
        normalized = self._normalize_case_number(self.case_number)
        # Remove "K " prefix for filename matching
        file_pattern = normalized.replace(" ", "")  # "K1002010"
        
        for folder in self.ARCHIVE_FOLDERS:
            folder_path = self.project_root / folder
            if folder_path.exists():
                # Try exact match first
                for ext in ['.txt']:
                    file_path = folder_path / f"{file_pattern}{ext}"
                    if file_path.exists():
                        try:
                            self.archive_text = file_path.read_text(encoding='utf-8')
                            self.archive_path = str(file_path)
                            return
                        except:
                            pass
                
                # Try with space: "K 1002010.txt"
                file_path = folder_path / f"K {file_pattern[1:]}.txt"
                if file_path.exists():
                    try:
                        self.archive_text = file_path.read_text(encoding='utf-8')
                        self.archive_path = str(file_path)
                        return
                    except:
                        pass
    
    def extract_all_facts(self):
        """Extract all relevant facts from archive text using NLP patterns"""
        text = self.archive_text
        
        # === METADATA ===
        # Court name
        match = re.search(r'(?:OSNOVNI SUD U|Osnovni Sud u)\s+([A-ZČĆŽŠĐ]+)', text, re.IGNORECASE)
        if match:
            self.extracted_facts['court'] = match.group(1).title()
        
        # Full case number
        match = re.search(r'K\.?(?:br\.?)?\s*(\d+/\d+)', text)
        if match:
            self.extracted_facts['case_number_full'] = f"K {match.group(1)}"
        
        # Date of verdict
        match = re.search(r'dana\s+(\d{1,2}\.\d{1,2}\.\d{4})\.?\s*g?\.?\s*(?:donio|donijelo)', text)
        if match:
            self.extracted_facts['verdict_date'] = match.group(1)
        
        # Judge - look for patterns like "sudija Ime Prezime" or "sudije Ime Prezime"
        # Avoid matching partial words like "Osnovnog suda"
        judge_patterns = [
            r'sudij[ea],?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            r'pojedinac\s+sudij[ea]\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            r'predsjednik[a]?\s+vijeća\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
        ]
        for pattern in judge_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                judge_name = match.group(1).strip()
                # Validate it looks like a proper name (not "Osnovnog suda" etc)
                if not any(word in judge_name.lower() for word in ['suda', 'sud', 'vijeć']):
                    self.extracted_facts['judge'] = judge_name
                    break
        
        # Zapisničar (court clerk)
        match = re.search(r'zapisničar[a]?[,:]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)', text, re.IGNORECASE)
        if match:
            self.extracted_facts['court_clerk'] = match.group(1).strip()
        
        # Prosecutor - look for proper name after tužilac/tužioca
        prosecutor_patterns = [
            r'[Tt]užio(?:ca|lac)[,:]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            r'(?:Zamjenik[a]?\s+)?(?:Osnovnog\s+)?(?:državnog\s+)?tužio(?:ca|lac)\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
        ]
        for pattern in prosecutor_patterns:
            match = re.search(pattern, text)
            if match:
                self.extracted_facts['prosecutor'] = match.group(1).strip()
                break
        
        # Defense attorney - be more strict, require proper name format
        defense_patterns = [
            r'branioc[a]?[,:]?\s+advokat[a]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            r'advokat[a]?[,:]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)\s*(?:iz|,)',
            r'branioc[a]?[,:]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)\s*(?:iz|,|advokat)',
        ]
        for pattern in defense_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Validate - should not contain common words that aren't names
                if not any(word in name.lower() for word in ['okrivljen', 'optužen', 'branio', 'rožaj']):
                    self.extracted_facts['defense_attorney'] = name
                    break
        
        # === DEFENDANT INFO ===
        # Full defendant identification
        match = re.search(r'[Oo]ptužen[aio]\s+([A-ZČĆŽŠĐ]\.?\s*[A-ZČĆŽŠĐ]\.?)[,\s]+(?:JMBG)?', text)
        if match:
            self.extracted_facts['defendant_initials'] = match.group(1)
        
        # Parents
        match = re.search(r'od\s+oca\s+([A-ZČĆŽŠĐa-zčćžšđ\.]+)\s+i\s+majke\s+([A-ZČĆŽŠĐa-zčćžšđ\.]+)', text)
        if match:
            self.extracted_facts['defendant_parents'] = f"otac {match.group(1)}, majka {match.group(2)}"
        
        # Birthplace
        match = re.search(r'rođen[a]?\s+[^,]*\s+u\s+([A-ZČĆŽŠĐa-zčćžšđ]+)', text)
        if match:
            self.extracted_facts['birthplace'] = match.group(1)
        
        # Education
        match = re.search(r'završi(?:o|la)\s+(osnovnu školu|srednju školu|fakultet|visoku školu|[A-Za-z\s]+školu)', text, re.IGNORECASE)
        if match:
            self.extracted_facts['education'] = match.group(1)
        
        # Employment
        if re.search(r'nezaposlen[a]?', text, re.IGNORECASE):
            self.extracted_facts['employment'] = 'nezaposlen'
        elif match := re.search(r'zaposlen[a]?\s+(?:kao|u)\s+([^,]+)', text, re.IGNORECASE):
            self.extracted_facts['employment'] = match.group(1).strip()
        
        # Marital status
        if re.search(r'neoženjen|neudata', text, re.IGNORECASE):
            self.extracted_facts['marital_status'] = 'neoženjen/neudata'
        elif re.search(r'oženjen|udata', text, re.IGNORECASE):
            self.extracted_facts['marital_status'] = 'oženjen/udata'
        
        # Prior convictions
        if re.search(r'neosuđivan[a]?|ranije neosuđivan', text, re.IGNORECASE):
            self.extracted_facts['prior_convictions'] = False
            self.extracted_facts['prior_convictions_text'] = 'neosuđivan'
        elif re.search(r'ranije osuđivan|osuđivan', text, re.IGNORECASE):
            self.extracted_facts['prior_convictions'] = True
        
        # === LEGAL FACTS ===
        # Verdict type (OSLOBAĐA SE, OSUĐUJE SE, etc)
        if re.search(r'OSLOBADJA SE OD OPTUŽBE|OSLOBAĐA SE OD OPTUŽBE|oslobadja se od optužbe', text):
            self.extracted_facts['verdict_type'] = 'Oslobađajuća'
            self.extracted_facts['verdict_reason'] = self._extract_acquittal_reason(text)
        elif re.search(r'OGLAŠAVA SE KRIVIM|oglašava se krivim|OSUĐUJE SE', text, re.IGNORECASE):
            self.extracted_facts['verdict_type'] = 'Osuđujuća'
        
        # Criminal article
        match = re.search(r'(?:krivično[g]?\s+djel[ao]?\s+)?(?:iz\s+)?čl\.?\s*(\d+)\.?\s*(?:st\.?\s*(\d+))?[\.]*\s*(?:Krivičnog zakonika|KZ)', text)
        if match:
            article = f"čl. {match.group(1)}"
            if match.group(2):
                article += f" st. {match.group(2)}"
            self.extracted_facts['criminal_article'] = article
        
        # Crime description
        match = re.search(r'(?:zbog\s+)?krivično[g]?\s+djel[ao]?\s+([a-zčćžšđ\s]+)\s+iz\s+čl', text, re.IGNORECASE)
        if match:
            self.extracted_facts['crime_type'] = match.group(1).strip()
        
        # === FACTS OF THE CASE ===
        # Date of crime
        match = re.search(r'[Dd]ana\s+(\d{1,2}\.\d{1,2}\.\d{4})\.?\s*(?:g\.?)?\s*(?:oko\s+(\d{1,2}[,:]\d{2})\s*(?:časova|sati)?)?', text)
        if match:
            self.extracted_facts['crime_date'] = match.group(1)
            if match.group(2):
                self.extracted_facts['crime_time'] = match.group(2).replace(',', ':')
        
        # Location
        match = re.search(r'u\s+(maloprodajnom\s+objektu|prodavnici|radnji|STR)\s+[""„]?([^""„,]+)["""]?', text)
        if match:
            self.extracted_facts['crime_location_type'] = match.group(1)
            self.extracted_facts['crime_location_name'] = match.group(2).strip()
        
        # Amount involved (fake money denomination)
        amounts = []
        for m in re.finditer(r'(?:novčanic[aue]|apoenu?)\s+(?:od\s+)?(\d+)\s*(?:eura?|EUR)', text, re.IGNORECASE):
            amounts.append(f"{m.group(1)} EUR")
        # Also extract electronic top-ups
        for m in re.finditer(r'dopun[aue]\s+(?:računa\s+)?(?:u\s+)?(?:iznosu\s+od\s+)?(\d+)\s*(?:eura?|EUR)', text, re.IGNORECASE):
            amounts.append(f"{m.group(1)} EUR (dopuna)")
        if amounts:
            self.extracted_facts['monetary_amounts'] = list(set(amounts))
        
        # Serial numbers (for counterfeit money)
        serials = re.findall(r'serijs?k[io][g]?\s+broj[a]?\s+([A-Z0-9]+)', text)
        if serials:
            self.extracted_facts['serial_numbers'] = list(set(serials))
        
        # === WITNESSES ===
        witnesses = []
        for m in re.finditer(r'(?:svedok[a]?|svjedok[a]?)\s+([A-ZČĆŽŠĐ]\.?\s*[A-ZČĆŽŠĐ]\.?)', text):
            w = m.group(1).strip()
            if w and w not in witnesses:
                witnesses.append(w)
        if witnesses:
            self.extracted_facts['witnesses'] = witnesses
        
        # === EVIDENCE ===
        evidence = []
        evidence_patterns = [
            r'(potvrdu o privremeno oduzetim predmetima[^,\.]+)',
            r'(izvještaj[a]?\s+(?:kriminalističke tehnike|tehničke[^,\.]+))',
            r'(nalaz[a]?\s+i\s+mišljenj[ae]\s+vještaka[^,\.]+)',
            r'(listing[a]?\s+komunikacija[^,\.]+)',
            r'(zapisnik[a]?\s+o\s+prepoznavanju[^,\.]+)',
        ]
        for pattern in evidence_patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                ev = m.group(1).strip()
                if ev and ev not in evidence:
                    evidence.append(ev)
        if evidence:
            self.extracted_facts['evidence_types'] = evidence
        
        # === LEGAL REASONING ===
        # In dubio pro reo
        if re.search(r'in\s+dubio\s+pro\s+reo', text, re.IGNORECASE):
            self.extracted_facts['legal_principle'] = 'in dubio pro reo (u slučaju sumnje u korist optuženog)'
        
        # Costs
        match = re.search(r'[Tt]roškovi[^\.]*?(?:iznos[u]?\s+(?:od\s+)?)?(\d+[,\.]\d+|\d+)\s*(?:eura?|EUR)', text)
        if match:
            self.extracted_facts['court_costs'] = f"{match.group(1)} EUR"
        
        # Summary of case description
        self.extracted_facts['case_summary'] = self._extract_case_summary(text)
    
    def _extract_acquittal_reason(self, text: str) -> str:
        """Extract the reason for acquittal"""
        if re.search(r'nije dokazano da je izvršil[ao]', text, re.IGNORECASE):
            return 'Nije dokazano da je optuženi izvršio djelo za koje je optužen'
        if re.search(r'djelo.+nije krivično djelo', text, re.IGNORECASE):
            return 'Djelo za koje je optužen nije krivično djelo'
        if re.search(r'nema dovoljno dokaza', text, re.IGNORECASE):
            return 'Nema dovoljno dokaza'
        return 'Primjena načela in dubio pro reo'
    
    def _extract_case_summary(self, text: str) -> str:
        """Extract a brief summary of the case facts"""
        # Look for the main accusation paragraph
        match = re.search(r'Da je,\s*\n\s*(.{100,500}?)(?:\n\n|-čime)', text, re.DOTALL)
        if match:
            summary = match.group(1).strip()
            summary = re.sub(r'\s+', ' ', summary)
            return summary[:300] + '...' if len(summary) > 300 else summary
        return ""
    
    def get_fact(self, key: str, default=None):
        """Get a specific extracted fact"""
        return self.extracted_facts.get(key, default)
    
    def has_archive(self) -> bool:
        """Check if archive file was found"""
        return bool(self.archive_text)

class PenaltyRange:
    """Represents a sentence/penalty range"""
    def __init__(self, min_val: str = "N/A", max_val: str = "N/A"):
        self.min = min_val
        self.max = max_val
    
    def to_dict(self):
        return {"min": self.min, "max": self.max}
    
    def __str__(self):
        return f"{self.min} - {self.max}"

class RuleParser:
    """Parse legal rules from LegalRuleML XML"""
    
    def __init__(self, rules_file: str):
        self.rules_file = rules_file
        self.rules = {}
        self.mitigating_rules = []
        self.aggravating_rules = []
        self.sentencing_rules = []
        self.confiscation_rules = []
        self.parse_rules()
    
    def parse_rules(self):
        """Parse all rules from legal_rules.xml"""
        try:
            tree = ET.parse(self.rules_file)
            root = tree.getroot()
            
            # Define namespaces
            ns = {
                'lrml': 'http://docs.oasis-open.org/legalruleml/ns/v1.0/',
                'ruleml': 'http://ruleml.org/spec',
                'xs': 'http://www.w3.org/2001/XMLSchema'
            }
            
            # Extract all ConstitutiveStatements
            for stmt in root.findall('.//lrml:ConstitutiveStatement', ns):
                key = stmt.get('key', '')
                rule_elem = stmt.find('.//lrml:Rule', ns)
                
                if rule_elem is None:
                    continue
                
                # Extract paraphrase
                paraphrase_elem = rule_elem.find('.//lrml:Paraphrase', ns)
                paraphrase = paraphrase_elem.text if paraphrase_elem is not None else ""
                
                # Extract if/then conditions
                if_elem = rule_elem.find('.//ruleml:if', ns)
                then_elem = rule_elem.find('.//ruleml:then', ns)
                
                rule_info = {
                    'key': key,
                    'paraphrase': paraphrase,
                    'if': if_elem,
                    'then': then_elem,
                    'element': rule_elem
                }
                
                # Classify rule type
                if 'mitigating' in key.lower() or 'olaksavajuca' in paraphrase.lower():
                    self.mitigating_rules.append(rule_info)
                elif 'aggravating' in key.lower() or 'otezavajuca' in paraphrase.lower() or 'ranije_osudivan' in key.lower():
                    self.aggravating_rules.append(rule_info)
                elif 'sentencing' in key.lower() or 'uslovna' in paraphrase.lower() or 'kazna' in paraphrase.lower():
                    self.sentencing_rules.append(rule_info)
                elif 'confiscation' in key.lower() or 'oduzima' in paraphrase.lower():
                    self.confiscation_rules.append(rule_info)
                else:
                    # Penalty rules (articles 258, 260, 268)
                    self.rules[key] = rule_info
            
        except Exception as e:
            print(f"Error parsing rules: {e}", file=sys.stderr)
    
    def extract_penalty_from_rule(self, rule: Dict) -> PenaltyRange:
        """Extract penalty range from a rule's 'then' clause"""
        try:
            then_elem = rule.get('then')
            if then_elem is None:
                return PenaltyRange()
            
            ns = {'ruleml': 'http://ruleml.org/spec', 'xs': 'http://www.w3.org/2001/XMLSchema'}
            
            # Find Data elements in the then clause
            data_elems = then_elem.findall('.//ruleml:Data', ns)
            
            if len(data_elems) >= 2:
                min_val = data_elems[0].text
                max_val = data_elems[1].text
                
                # Format values
                min_val = self._format_duration(min_val)
                max_val = self._format_duration(max_val)
                
                return PenaltyRange(min_val, max_val)
            elif len(data_elems) == 1:
                # Single value (e.g., "do 3 godine")
                val = data_elems[0].text
                val = self._format_duration(val)
                return PenaltyRange("N/A", val)
            
            return PenaltyRange()
        except Exception as e:
            print(f"Error extracting penalty: {e}", file=sys.stderr)
            return PenaltyRange()
    
    def _format_duration(self, duration_str: str) -> str:
        """Format duration string into readable format"""
        if not duration_str:
            return "N/A"
        
        mapping = {
            '3': '3 mjeseca',
            '6_mjeseci': '6 mjeseci',
            '1': '1 godina',
            '2': '2 godine',
            '5': '5 godina',
            '8': '8 godina',
            '10': '10 godina',
            '12': '12 godina',
            '15': '15 godina',
        }
        
        if duration_str in mapping:
            return mapping[duration_str]
        
        if duration_str.isdigit():
            num = int(duration_str)
            if num == 1:
                return "1 godina"
            else:
                return f"{num} godina"
        
        return duration_str
    
    def extract_threshold_from_rule(self, rule: Dict) -> Optional[int]:
        """Extract amount threshold from a rule's 'if' clause"""
        try:
            if_elem = rule.get('if')
            if if_elem is None:
                return None
            
            ns = {'ruleml': 'http://ruleml.org/spec', 'xs': 'http://www.w3.org/2001/XMLSchema'}
            
            # Find Data elements that represent thresholds
            data_elems = if_elem.findall('.//ruleml:Data', ns)
            
            for data_elem in data_elems:
                try:
                    val = int(data_elem.text)
                    # Return the first numeric threshold (usually the only one)
                    return val
                except:
                    pass
            
            return None
        except:
            return None

class CaseFactsExtractor:
    """Extract facts from case XML files and archive text files"""
    
    def __init__(self, case_file: str):
        self.case_file = case_file
        self.facts = {}
        self.archive_extractor = None
        self.extract_facts()
        # Also try to load archive facts
        self.load_archive_facts()
    
    def extract_facts(self):
        """Extract relevant facts from case XML"""
        try:
            content = Path(self.case_file).read_text(encoding='utf-8')
            
            # Extract case number
            match = re.search(r'<brojPredmeta>([^<]+)</brojPredmeta>', content)
            if match:
                self.facts['case_number'] = match.group(1).strip()
            
            # Extract verdict
            match = re.search(r'<vrstaPresude>([^<]+)</vrstaPresude>', content)
            if match:
                self.facts['verdict'] = match.group(1).strip()
            
            # Extract actual sentence
            match = re.search(r'<kazna>([^<]+)</kazna>', content)
            if match:
                self.facts['actual_sentence'] = match.group(1).strip()
            
            # Extract articles/crimes
            articles = []
            for match in re.finditer(r'<clanKZ>([^<]+)</clanKZ>', content):
                article = match.group(1).strip()
                if article and article not in articles:
                    articles.append(article)
            self.facts['articles'] = articles
            
            # Extract defendant info
            match = re.search(r'<sudija>([^<]+)</sudija>', content)
            if match:
                self.facts['judge'] = match.group(1).strip()
            
            # Extract court clerk
            match = re.search(r'<zapisnicar>([^<]+)</zapisnicar>', content)
            if match:
                self.facts['court_clerk'] = match.group(1).strip()
            
            # Extract defendant initials
            match = re.search(r'<optuzeni>([^<]+)</optuzeni>', content)
            if match:
                self.facts['defendant'] = match.group(1).strip()
            
            # Extract crime type
            match = re.search(r'<tipKrivicnogDjela>([^<]+)</tipKrivicnogDjela>', content)
            if match:
                self.facts['crime_type'] = match.group(1).strip()
            
            # Extract court
            match = re.search(r'<sud>([^<]+)</sud>', content)
            if match:
                self.facts['court'] = match.group(1).strip()
            
            # Extract date
            match = re.search(r'<datum>([^<]+)</datum>', content)
            if match:
                self.facts['date'] = match.group(1).strip()
            
            # Extract case description
            match = re.search(r'<opisSlucaja>([^<]+)</opisSlucaja>', content)
            if match:
                self.facts['case_description'] = match.group(1).strip()
            
            # Extract witnesses
            witnesses = []
            for match in re.finditer(r'<svjedok>([^<]+)</svjedok>', content):
                w = match.group(1).strip()
                if w and w not in witnesses:
                    witnesses.append(w)
            self.facts['witnesses'] = witnesses
            
            # Extract evidence
            evidence = []
            for match in re.finditer(r'<dokaz>([^<]+)</dokaz>', content):
                e = match.group(1).strip()
                if e and e not in evidence:
                    evidence.append(e)
            self.facts['evidence'] = evidence
            
            # Extract amounts (for fraud cases)
            amounts = []
            for match in re.finditer(r'<iznos[^>]*>([^<]+)</iznos>', content):
                amount = match.group(1).strip()
                if amount and amount not in amounts:
                    amounts.append(amount)
            self.facts['amounts'] = amounts
            
            # Extract prior convictions
            match = re.search(r'<ranijeOsudjivan>([^<]*)</ranijeOsudjivan>', content)
            if match:
                val = match.group(1).strip().lower()
                self.facts['previously_convicted'] = val in ['da', 'yes', 'true']
                self.facts['prior_convictions_text'] = match.group(1).strip()
            else:
                self.facts['previously_convicted'] = False
            
            # Extract conditional sentence indicator
            match = re.search(r'<uslovnaOsuda>([^<]*)</uslovnaOsuda>', content)
            self.facts['conditional_sentence'] = match and match.group(1).strip().lower() in ['da', 'yes', 'true']
            
            # Extract year of case
            match = re.search(r'<godina>(\d{4})</godina>', content)
            if match:
                self.facts['year'] = int(match.group(1))
            
            # Extract monetary fine
            match = re.search(r'<novcanaKazna>([^<]+)</novcanaKazna>', content)
            if match:
                self.facts['monetary_fine'] = match.group(1).strip()
            
        except Exception as e:
            print(f"Error extracting facts: {e}", file=sys.stderr)
    
    def load_archive_facts(self):
        """Load additional facts from archive text file"""
        case_num = self.facts.get('case_number', '')
        if case_num:
            self.archive_extractor = ArchiveFactsExtractor(case_num)
            if self.archive_extractor.has_archive():
                # Merge archive facts (don't overwrite existing)
                for key, value in self.archive_extractor.extracted_facts.items():
                    if key not in self.facts or not self.facts[key]:
                        self.facts[key] = value
                    elif key == 'witnesses' and isinstance(value, list):
                        # Merge witness lists
                        existing = self.facts.get('witnesses', [])
                        for w in value:
                            if w not in existing:
                                existing.append(w)
                        self.facts['witnesses'] = existing
                # Store archive-specific facts separately
                self.facts['archive_facts'] = self.archive_extractor.extracted_facts
    
    def get_fact(self, key: str, default=None):
        """Get a specific fact"""
        return self.facts.get(key, default)
    
    def has_article(self, article_pattern: str) -> bool:
        """Check if case contains a specific article"""
        articles = self.facts.get('articles', [])
        for article in articles:
            if article_pattern.lower() in article.lower():
                return True
        return False
    
    def has_archive(self) -> bool:
        """Check if archive data was loaded"""
        return self.archive_extractor is not None and self.archive_extractor.has_archive()

class SentenceCalculator:
    """Calculate recommended sentences based on rules and facts"""
    
    def __init__(self, rule_parser: RuleParser, case_facts: CaseFactsExtractor):
        self.rule_parser = rule_parser
        self.case_facts = case_facts
        self.applicable_rules = []
        self.mitigating_factors = []
        self.aggravating_factors = []
        self.base_penalty = PenaltyRange()
        
        # Pre-extract thresholds for all rules
        self.rule_thresholds = {}
        for key, rule in rule_parser.rules.items():
            threshold = rule_parser.extract_threshold_from_rule(rule)
            self.rule_thresholds[key] = threshold
    
    def analyze_case(self) -> Dict:
        """Perform complete case analysis"""
        verdict = self.case_facts.get_fact('verdict', 'Nepoznato')
        verdict_lower = verdict.lower() if verdict else ''
        is_acquittal = 'oslobod' in verdict_lower or 'oslobađ' in verdict_lower
        
        analysis = {
            'case_number': self.case_facts.get_fact('case_number', 'Nepoznato'),
            'articles': self.case_facts.get_fact('articles', []),
            'verdict': verdict,
            'actual_sentence': self.case_facts.get_fact('actual_sentence', 'N/A'),
            'applicable_articles': [],
            'violated_rules': [],
            'applicable_rules': [],
            'penalty_range': PenaltyRange().to_dict(),
            'mitigating_factors': [],
            'aggravating_factors': [],
            'recommendation': "N/A",
            'analysis': [],
            'acquittal': is_acquittal,
            # === METADATA ===
            'metadata': {
                'court': self.case_facts.get_fact('court', ''),
                'judge': self.case_facts.get_fact('judge', ''),
                'court_clerk': self.case_facts.get_fact('court_clerk', ''),
                'date': self.case_facts.get_fact('date', ''),
                'year': self.case_facts.get_fact('year', ''),
                'defendant': self.case_facts.get_fact('defendant', ''),
                'defendant_parents': self.case_facts.get_fact('defendant_parents', ''),
                'prior_convictions': self.case_facts.get_fact('prior_convictions_text', ''),
                'crime_type': self.case_facts.get_fact('crime_type', ''),
            },
            # === CASE FACTS ===
            'case_facts': {
                'description': self.case_facts.get_fact('case_description', '') or self.case_facts.get_fact('case_summary', ''),
                'witnesses': self.case_facts.get_fact('witnesses', []),
                'evidence': self.case_facts.get_fact('evidence', []),
                'amounts': self.case_facts.get_fact('amounts', []),
                'monetary_fine': self.case_facts.get_fact('monetary_fine', ''),
                'crime_date': self.case_facts.get_fact('crime_date', ''),
                'crime_location': self.case_facts.get_fact('crime_location_name', ''),
                'serial_numbers': self.case_facts.get_fact('serial_numbers', []),
            },
            # === LEGAL ANALYSIS ===
            'legal_analysis': {
                'verdict_reason': self.case_facts.get_fact('verdict_reason', ''),
                'legal_principle': self.case_facts.get_fact('legal_principle', ''),
                'court_costs': self.case_facts.get_fact('court_costs', ''),
                'prosecutor': self.case_facts.get_fact('prosecutor', ''),
                'defense_attorney': self.case_facts.get_fact('defense_attorney', ''),
            },
            'has_archive': self.case_facts.has_archive() if hasattr(self.case_facts, 'has_archive') else False,
        }
        
        # If acquittal, clear penalties and set appropriate values
        if is_acquittal:
            analysis['penalty_range'] = {'min': 'N/A', 'max': 'N/A', 'note': 'Oslobađajuća presuda'}
            analysis['violated_rules'] = ['Optuženi je oslobođen - krivično djelo nije dokazano']
            analysis['recommendation'] = 'Oslobođen - nema kazne'
            # Add acquittal reason
            if self.case_facts.get_fact('verdict_reason'):
                analysis['legal_analysis']['verdict_reason'] = self.case_facts.get_fact('verdict_reason')
            return analysis
        
        # Analyze each article
        for article in self.case_facts.get_fact('articles', []):
            analysis['applicable_articles'].append(article)
            
            # Find applicable rules for this article
            article_num = self._extract_article_number(article)
            if article_num:
                article_rules = self._get_applicable_rules_for_article(article_num)
                
                for rule in article_rules:
                    analysis['violated_rules'].append(rule.get('paraphrase', 'Rule'))
                    analysis['applicable_rules'].append({
                        'key': rule.get('key'),
                        'paraphrase': rule.get('paraphrase')
                    })
                
                # Get penalty range from most specific rule
                if article_rules:
                    # Sort by specificity (higher numbers more specific)
                    article_rules_sorted = sorted(
                        article_rules,
                        key=lambda r: self._get_rule_specificity(r),
                        reverse=True
                    )
                    
                    # Use the most specific applicable rule
                    for rule in article_rules_sorted:
                        if self._is_rule_applicable(rule):
                            penalty = self.rule_parser.extract_penalty_from_rule(rule)
                            analysis['penalty_range'] = penalty.to_dict()
                            self.base_penalty = penalty
                            break
        
        # If no articles found, check verdict for clues
        if not analysis['applicable_articles']:
            verdict = self.case_facts.get_fact('verdict', '').lower()
            # Check for acquittal first
            if 'oslobod' in verdict or 'oslobađ' in verdict:
                analysis['violated_rules'].append('Optuženi je oslobođen - krivično djelo nije dokazano')
                analysis['penalty_range'] = {'min': 'N/A', 'max': 'N/A', 'note': 'Oslobađajuća presuda'}
                analysis['acquittal'] = True
            elif 'osud' in verdict or 'kriv' in verdict:
                analysis['violated_rules'].append('Utvrđena krivična odgovornost')
                analysis['penalty_range'] = {'min': '3 mjeseca', 'max': '10 godina'}
        
        # Identify mitigating factors
        self._identify_mitigating_factors(analysis)
        
        # Identify aggravating factors
        self._identify_aggravating_factors(analysis)
        
        # Generate recommendation
        analysis['recommendation'] = self._calculate_recommended_sentence(analysis)
        
        # Generate detailed analysis
        analysis['analysis'] = self._generate_analysis(analysis)
        
        return analysis
    
    def _extract_article_number(self, article_str: str) -> Optional[str]:
        """Extract article number from string like 'čl. 260' or 'Član 258'"""
        match = re.search(r'(?:čl\.|Član)\s*(\d+)', article_str, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _get_applicable_rules_for_article(self, article_num: str) -> List[Dict]:
        """Get all rules for a specific article, filtered by applicability"""
        matching_rules = []
        
        for key, rule in self.rule_parser.rules.items():
            # Check if key contains article number
            if f'_{article_num}_' in key or f'_{article_num}' in key:
                # Only add rule if it's truly applicable
                if self._is_rule_applicable(rule):
                    matching_rules.append(rule)
        
        return matching_rules
    
    def _is_rule_applicable(self, rule: Dict) -> bool:
        """Determine if a rule is applicable to the current case"""
        rule_key = rule.get('key', '')
        
        # Get the threshold for this rule (extracted from XML <Data> elements)
        threshold = self.rule_thresholds.get(rule_key)
        
        # If rule has no threshold, it's always applicable
        if threshold is None:
            return True
        
        # If rule has a threshold, check if case amount exceeds it
        amounts = self.case_facts.get_fact('amounts', [])
        
        for amount in amounts:
            try:
                if 'eur' in amount.lower():
                    # Handle European number format
                    amount_clean = amount.replace(' EUR', '').replace('EUR', '').strip()
                    
                    # Determine decimal separator (comma for European, dot for US)
                    last_comma = amount_clean.rfind(',')
                    last_dot = amount_clean.rfind('.')
                    
                    if last_comma > last_dot:  # European format
                        amount_clean = amount_clean.replace('.', '').replace(',', '.')
                    else:  # US format or no decimal
                        amount_clean = amount_clean.replace(',', '')
                    
                    amount_value = float(amount_clean)
                    
                    # Check if this amount exceeds the threshold
                    if amount_value > threshold:
                        return True
            except:
                pass
        
        # No amount exceeded the threshold
        return False
    
    def _get_rule_specificity(self, rule: Dict) -> int:
        """Get specificity score of a rule (higher = more specific)"""
        key = rule.get('key', '')
        paraphrase = rule.get('paraphrase', '')
        
        score = 0
        
        # Qualified forms (st. 3+) are more specific
        if '_3' in key or '_4' in key:
            score += 10
        
        # Amount-based rules are more specific
        if '40000' in paraphrase:
            score += 40000
        elif '30000' in paraphrase:
            score += 30000
        elif '15000' in paraphrase:
            score += 15000
        elif '3000' in paraphrase:
            score += 3000
        
        return score
    
    def _identify_mitigating_factors(self, analysis: Dict):
        """Identify mitigating factors from case facts based on drdevice_rules.ddr"""
        verdict = self.case_facts.get_fact('verdict', '').lower()
        
        # If acquitted, no factors needed
        if 'oslobod' in verdict or 'oslobađ' in verdict:
            return
        
        # First offense (ranije_neosudjivan)
        if not self.case_facts.get_fact('previously_convicted'):
            self.mitigating_factors.append('Ranije neosudivan')
            analysis['mitigating_factors'].append('Ranije neosudivan')
        
        # Small amount is MITIGATING (mali_iznos < 500 EUR per drdevice_rules.ddr)
        max_amount = self._get_max_amount()
        if max_amount is not None and max_amount < 500:
            analysis['mitigating_factors'].append(f'Mali iznos štete (ispod 500 EUR)')
        
        # Few witnesses (1-2) can be mitigating - less corroboration needed
        witnesses = self.case_facts.get_fact('witnesses', [])
        if witnesses and len(witnesses) <= 2:
            analysis['mitigating_factors'].append(f'Mali broj svjedoka ({len(witnesses)})')
    
    def _identify_aggravating_factors(self, analysis: Dict):
        """Identify aggravating factors from case facts based on drdevice_rules.ddr"""
        verdict = self.case_facts.get_fact('verdict', '').lower()
        
        # If acquitted, no aggravating factors
        if 'oslobod' in verdict or 'oslobađ' in verdict:
            return
        
        # Prior convictions (ranije_osudivan)
        if self.case_facts.get_fact('previously_convicted'):
            self.aggravating_factors.append('Ranije osudivan')
            analysis['aggravating_factors'].append('Ranije osudivan')
        
        # Large amount is AGGRAVATING only if > 15000 EUR (per drdevice_rules.ddr)
        max_amount = self._get_max_amount()
        if max_amount is not None and max_amount > 15000:
            analysis['aggravating_factors'].append(f'Veliki iznos štete (preko 15.000 EUR)')
        elif max_amount is not None and max_amount > 3000:
            analysis['aggravating_factors'].append(f'Značajan iznos štete (preko 3.000 EUR)')
        
        # Many witnesses (5+) can be aggravating - more people affected/involved
        witnesses = self.case_facts.get_fact('witnesses', [])
        if witnesses and len(witnesses) >= 5:
            analysis['aggravating_factors'].append(f'Veći broj svjedoka ({len(witnesses)})')
        
        # Many pieces of evidence (8+) can indicate more serious/planned crime
        evidence = self.case_facts.get_fact('evidence', [])
        if evidence and len(evidence) >= 8:
            analysis['aggravating_factors'].append(f'Opsežna dokazna dokumentacija ({len(evidence)} dokaza)')
    
    def _get_max_amount(self) -> Optional[float]:
        """Extract the maximum amount from case facts"""
        amounts = self.case_facts.get_fact('amounts', [])
        max_val = None
        
        for amount in amounts:
            try:
                if 'eur' in amount.lower():
                    amount_clean = amount.replace(' EUR', '').replace('EUR', '').strip()
                    last_comma = amount_clean.rfind(',')
                    last_dot = amount_clean.rfind('.')
                    
                    if last_comma > last_dot:
                        amount_clean = amount_clean.replace('.', '').replace(',', '.')
                    else:
                        amount_clean = amount_clean.replace(',', '')
                    
                    val = float(amount_clean)
                    if max_val is None or val > max_val:
                        max_val = val
            except:
                pass
        
        return max_val
    
    def _calculate_recommended_sentence(self, analysis: Dict) -> str:
        """Calculate a recommended sentence based on factors and actual sentence"""
        
        verdict = self.case_facts.get_fact('verdict', '').lower()
        
        # If acquitted, no sentence
        if 'oslobod' in verdict:
            return 'Oslobođen - nema kazne'
        
        # If judicial warning
        if 'opomena' in verdict:
            return 'Sudska opomena'
        
        penalty_range = analysis['penalty_range']
        if penalty_range['min'] == 'N/A':
            return 'N/A'
        
        # Parse penalty range from rules (drdevice_rules.ddr)
        min_years = self._parse_penalty_to_years(penalty_range['min'])
        max_years = self._parse_penalty_to_years(penalty_range['max'])
        
        if min_years is None or max_years is None:
            return 'N/A'
        
        # === RULE-BASED RECOMMENDATION (based solely on drdevice_rules.ddr) ===
        # We do NOT look at actual sentence - only facts and rules
        
        num_mitigating = len(analysis['mitigating_factors'])
        num_aggravating = len(analysis['aggravating_factors'])
        
        # Calculate range based on factors (per rules from drdevice_rules.ddr)
        range_span = max_years - min_years
        
        # Default: start at 1/3 of range (reasonable starting point)
        base_factor = 0.33
        
        # Apply mitigating factors - each pulls toward minimum
        # Rule: rule_sentence_reduction says 2+ mitigating factors allows reduction
        if num_mitigating >= 2:
            base_factor = 0.15  # Below minimum end of normal range
        elif num_mitigating == 1:
            base_factor = 0.25  # Lower end
        
        # Apply aggravating factors - each pushes toward maximum
        # Rule: rule_sentence_increase says any aggravating factor recommends increase
        if num_aggravating >= 2:
            base_factor = min(0.75, base_factor + 0.4)  # Significant increase
        elif num_aggravating == 1:
            base_factor = min(0.6, base_factor + 0.2)  # Moderate increase
        
        # Balance: if both present, net effect
        if num_mitigating > 0 and num_aggravating > 0:
            net = num_aggravating - num_mitigating
            if net > 0:
                base_factor = 0.4 + (net * 0.1)  # Lean toward higher
            elif net < 0:
                base_factor = 0.3 + (net * 0.05)  # Lean toward lower
            else:
                base_factor = 0.35  # Balanced
        
        rec_years = min_years + (range_span * base_factor)
        
        # Ensure within legal bounds
        rec_years = max(min_years, min(max_years, rec_years))
        
        # Rule: rule_suspended_sentence - if max <= 2 years and mitigating factors exist,
        # suspended sentence is possible (uslovna osuda)
        if max_years <= 2 and num_mitigating > 0:
            return f'Uslovna osuda ({self._format_years(rec_years)})'
        
        # For longer sentences, check if conditional is still appropriate
        if rec_years <= 2 and num_mitigating >= 2 and num_aggravating == 0:
            return f'Uslovna osuda ({self._format_years(rec_years)})'
        
        return self._format_years(rec_years)
    
    def _parse_penalty_to_years(self, penalty_str: str) -> Optional[float]:
        """Parse penalty string to years"""
        if isinstance(penalty_str, (int, float)):
            return penalty_str
        
        penalty_str = str(penalty_str).lower()
        
        # Try to extract number
        match = re.search(r'(\d+(?:[.,]\d+)?)', penalty_str)
        if not match:
            return None
        
        num = float(match.group(1).replace(',', '.'))
        
        # Handle months
        if 'mjesec' in penalty_str or 'mjeseci' in penalty_str or 'mjeseca' in penalty_str:
            return num / 12
        
        return num
    
    def _format_years(self, years: float) -> str:
        """Format years to readable string"""
        if years < 1:
            months = int(years * 12)
            if months == 1:
                return "1 mjesec"
            return f"{months} mjeseci"
        
        if years == int(years):
            if years == 1:
                return "1 godina"
            else:
                return f"{int(years)} godina"
        
        years_int = int(years)
        months = int((years - years_int) * 12)
        
        if months == 0:
            if years_int == 1:
                return "1 godina"
            return f"{years_int} godina"
        
        return f"{years_int} godina {months} mjeseci"
    
    def _generate_analysis(self, analysis: Dict) -> List[str]:
        """Generate detailed analysis text"""
        lines = []
        
        case_num = analysis['case_number']
        lines.append(f"Analiza predmeta: {case_num}")
        
        if analysis['articles']:
            articles_str = ", ".join(analysis['articles'])
            lines.append(f"Primjenjivi članci: {articles_str}")
        
        if analysis['mitigating_factors']:
            lines.append(f"Olakšavajuće okolnosti: {len(analysis['mitigating_factors'])}")
        
        if analysis['aggravating_factors']:
            lines.append(f"Otežavajuće okolnosti: {len(analysis['aggravating_factors'])}")
        
        # Compare recommendation with actual
        recommendation = analysis['recommendation']
        actual = self.case_facts.get_fact('actual_sentence', 'N/A')
        
        if actual and actual != 'N/A' and recommendation != 'N/A':
            lines.append(f"Preporučena kazna: {recommendation}")
            lines.append(f"Stvarna kazna: {actual}")
        
        return lines

def reason_about_case(case_file: str = None, facts: str = None, rules_file: str = None) -> Dict:
    """
    Perform comprehensive rule-based reasoning on a case
    
    Args:
        case_file: Path to XML case file
        facts: JSON string containing case facts
        rules_file: Path to legal rules XML
    
    Returns:
        Dictionary with complete reasoning results
    """
    try:
        # Get rules file path
        if not rules_file:
            project_root = Path(__file__).parent
            rules_file = project_root / 'data' / 'rules' / 'legal_rules.xml'
        
        if not Path(rules_file).exists():
            return {
                "status": "error",
                "error": f"Rules file not found: {rules_file}"
            }
        
        result = {
            "status": "success",
            "case_number": "Nepoznato",
            "articles": [],
            "verdict": "Nepoznato",
            "actual_sentence": "N/A",
            "applicable_articles": [],
            "violated_rules": [],
            "penalty_range": {"min": "N/A", "max": "N/A"},
            "mitigating_factors": [],
            "aggravating_factors": [],
            "recommendation": "N/A",
            "detailed_analysis": [],
            "acquittal": False
        }
        
        # Parse rules
        rule_parser = RuleParser(str(rules_file))
        
        if case_file:
            if not Path(case_file).exists():
                return {
                    "status": "error",
                    "error": f"Case file not found: {case_file}"
                }
            
            # Extract facts from case
            case_facts = CaseFactsExtractor(case_file)
            
            # Analyze case
            calculator = SentenceCalculator(rule_parser, case_facts)
            analysis = calculator.analyze_case()
            
            result.update(analysis)
        
        elif facts:
            try:
                facts_dict = json.loads(facts)
                # Create a mock case facts object
                case_facts = type('CaseFacts', (), {
                    'get_fact': lambda self, key, default=None: facts_dict.get(key, default),
                    'has_article': lambda self, pattern: any(pattern in str(a) for a in facts_dict.get('articles', []))
                })()
                
                calculator = SentenceCalculator(rule_parser, case_facts)
                analysis = calculator.analyze_case()
                result.update(analysis)
                
            except json.JSONDecodeError as e:
                return {
                    "status": "error",
                    "error": f"Invalid JSON facts: {e}"
                }
        
        return result
        
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }

def main():
    parser = argparse.ArgumentParser(
        description="Montenegrin Legal Case Reasoning Engine - Advanced Rule-Based System"
    )
    parser.add_argument('--case', help='XML case file path')
    parser.add_argument('--facts', help='JSON facts string')
    parser.add_argument('--rules', help='Legal rules XML file path')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    result = reason_about_case(
        case_file=args.case,
        facts=args.facts,
        rules_file=args.rules
    )
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()

