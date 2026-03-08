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
import subprocess
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
        match = re.search(r'(?:OSNOVNI SUD U|Osnovni Sud u|OSNOVNI SUD u)\s+([A-ZČĆŽŠĐa-zčćžšđ\s]+?)(?:,|\n)', text, re.IGNORECASE)
        if match:
            self.extracted_facts['court'] = match.group(1).strip().title()
        
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
        
        # Prior convictions - check carefully in defendant description block
        # Look in the defendant description area (near JMBG, od oca, etc.)
        defendant_block = ''
        defendant_match = re.search(r'(?:O[pk]tužen[aio]|Okrivljen[aio])\s*:?\s*\n?(.{50,800}?)(?:K\s*R\s*I\s*V|OSLOBADJA|OSLOBAĐA|O\s*S\s*U\s*Đ\s*U\s*J\s*E|Zato što)', text, re.DOTALL | re.IGNORECASE)
        if defendant_match:
            defendant_block = defendant_match.group(1)
        
        # Check neosudjivan/osudjivan - both latin and cyrillic variants
        if re.search(r'neosudj?ivan[a]?|neosuđivan[a]?|ranije\s+neosudj?ivan|ranije\s+neosuđivan', defendant_block or text, re.IGNORECASE):
            self.extracted_facts['prior_convictions'] = False
            self.extracted_facts['prior_convictions_text'] = 'neosuđivan'
        elif re.search(r'(?:ranije\s+)?osudj?ivan[a]?|(?:ranije\s+)?osuđivan[a]?', defendant_block or text, re.IGNORECASE):
            self.extracted_facts['prior_convictions'] = True
            self.extracted_facts['prior_convictions_text'] = 'osuđivan'
            # Try to extract what they were previously convicted for
            prior_match = re.search(r'osudj?ivan[a]?\s+(?:i to\s+)?(?:presudom\s+)?(.{10,200}?)(?:\.|,\s*\n)', text, re.IGNORECASE)
            if prior_match:
                self.extracted_facts['prior_conviction_details'] = prior_match.group(1).strip()
        
        # === CONFESSION / GUILTY PLEA ===
        if re.search(r'prizna[ojela]+\s+(?:u cjelosti\s+)?(?:izvršenje\s+)?(?:krivičn|krivic)', text, re.IGNORECASE):
            self.extracted_facts['confession'] = True
        elif re.search(r'prizna[ojela]+\s+(?:svoju\s+)?krivicu', text, re.IGNORECASE):
            self.extracted_facts['confession'] = True
        elif re.search(r'sporazum[a]?\s+o\s+prizn', text, re.IGNORECASE):
            self.extracted_facts['confession'] = True
            self.extracted_facts['plea_agreement'] = True
        else:
            self.extracted_facts['confession'] = False
        
        # === RESTITUTION ===
        if re.search(r'nadoknad[io]+\s+(?:novčan[uo]\s+)?štetu|vratio?\s+novac|nadoknad[io]+.{0,30}oštećen', text, re.IGNORECASE):
            self.extracted_facts['restitution'] = True
        else:
            self.extracted_facts['restitution'] = False
        
        # === REMORSE / KAJANJE ===
        if re.search(r'izražen[o]?\s+kajanje|iskreno\s+(?:se\s+)?kaje|žao\s+(?:mu|joj|što)', text, re.IGNORECASE):
            self.extracted_facts['remorse'] = True
        else:
            self.extracted_facts['remorse'] = False
        
        # === FAMILY CIRCUMSTANCES ===
        children_match = re.search(r'otac\s+(\w+)\s+(?:maloljetn[eog]+\s+)?(?:dj?ec[ea]|djete)|majka\s+(\w+)\s+(?:maloljetn[eog]+\s+)?(?:dj?ec[ea]|djete)', text, re.IGNORECASE)
        if children_match:
            self.extracted_facts['has_children'] = True
        elif re.search(r'bez\s+djece|nema\s+djece', text, re.IGNORECASE):
            self.extracted_facts['has_children'] = False
        
        # === LEGAL FACTS ===
        # Verdict type (OSLOBAĐA SE, OSUĐUJE SE, etc)
        if re.search(r'OSLOBADJA SE OD OPTUŽBE|OSLOBAĐA SE OD OPTUŽBE|oslobadja se od optužbe|OSLOBAĐA SE', text):
            self.extracted_facts['verdict_type'] = 'Oslobađajuća'
            self.extracted_facts['verdict_reason'] = self._extract_acquittal_reason(text)
        elif re.search(r'KRIV\s+JE|K\s*R\s*I\s*V\s*A?\s+JE', text):
            self.extracted_facts['verdict_type'] = 'Osuđujuća'
        elif re.search(r'OGLAŠAVA SE KRIVIM|oglašava se krivim|OSUĐUJE SE', text, re.IGNORECASE):
            self.extracted_facts['verdict_type'] = 'Osuđujuća'
        
        # === ACTUAL SENTENCE EXTRACTION ===
        self._extract_actual_sentence(text)
        
        # === UBLAŽAVANJE (SENTENCE MITIGATION) DETECTION ===
        self._extract_ublazavanje(text)
        
        # Criminal article - extract ALL mentioned articles
        articles = []
        for m in re.finditer(r'čl\.?\s*(\d+)\.?\s*(?:st\.?\s*(\d+))?[\.]?\s*(?:u\s+vezi\s+(?:sa\s+)?(?:st\.?\s*(\d+))?)?\s*(?:Krivičnog zakonika|KZ|KZCG|KZ\s*CG)', text):
            article = f"čl. {m.group(1)}"
            if m.group(2):
                article += f" st. {m.group(2)}"
            if m.group(3):
                article += f" u vezi st. {m.group(3)}"
            if article not in articles:
                articles.append(article)
        if articles:
            self.extracted_facts['criminal_articles'] = articles
            self.extracted_facts['criminal_article'] = articles[0]  # primary article
        
        # Crime description
        match = re.search(r'(?:zbog\s+)?krivično[g]?\s+djel[ao]?\s+[-–]?\s*([a-zčćžšđ\s]+)\s+iz\s+čl', text, re.IGNORECASE)
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
        
        # Amount involved - comprehensive EUR amount extraction
        amounts_raw = []
        total_falsified = 0.0
        total_gain = 0.0
        
        # Extract denominations: "novčanica/apoenu od X eura"
        for m in re.finditer(r'(?:novčanic[aue]|apoenu?)\s+(?:od\s+)?(\d+[,.]?\d*)\s*(?:eura?|EUR|€)', text, re.IGNORECASE):
            val = float(m.group(1).replace(',', '.'))
            amounts_raw.append(('denomination', val))
        
        # Count of banknotes: "X novčanica od Y eura" or "X lažnih novčanica"
        for m in re.finditer(r'(\d+)\s+(?:lažn[ie]h?\s+)?(?:novčanic[ae]|komad[a]?)\s+(?:u\s+)?(?:apoenu?\s+)?(?:od\s+)?(\d+[,.]?\d*)\s*(?:eura?|EUR|€)', text, re.IGNORECASE):
            count = int(m.group(1))
            denom = float(m.group(2).replace(',', '.'))
            total_val = count * denom
            amounts_raw.append(('batch', total_val))
            total_falsified += total_val
        
        # Specific amounts: "u iznosu od X eura", "iznos od X eura"
        for m in re.finditer(r'(?:u\s+)?iznos[u]?\s+(?:od\s+)?(\d+[,.]?\d*)\s*(?:eura?|EUR|€)', text, re.IGNORECASE):
            val = float(m.group(1).replace(',', '.'))
            amounts_raw.append(('amount', val))
        
        # "protivpravnu imovinsku korist u iznosu od X eura" 
        for m in re.finditer(r'(?:protivpravn[aou]\s+)?imovinsk[aou]\s+korist[i]?\s+(?:u\s+)?(?:iznosu?\s+)?(?:od\s+)?(\d+[,.]?\d*)\s*(?:eura?|EUR|€)', text, re.IGNORECASE):
            val = float(m.group(1).replace(',', '.'))
            total_gain = max(total_gain, val)
            amounts_raw.append(('gain', val))
        
        # Electronic top-ups
        for m in re.finditer(r'dopun[aue]\s+(?:računa\s+)?(?:u\s+)?(?:iznosu\s+od\s+)?(\d+[,.]?\d*)\s*(?:eura?|EUR|€)', text, re.IGNORECASE):
            val = float(m.group(1).replace(',', '.'))
            amounts_raw.append(('topup', val))
        
        # ATM withdrawals: "podigao/podigla X eura"
        for m in re.finditer(r'(?:podig[ao]+|podizanj[ea])\s+(?:iznos[a]?\s+(?:od\s+)?)?(\d+[,.]?\d*)\s*(?:eura?|EUR|€)', text, re.IGNORECASE):
            val = float(m.group(1).replace(',', '.'))
            amounts_raw.append(('withdrawal', val))
            total_gain = max(total_gain, val)
        
        # POS transactions: "X transakcija"
        for m in re.finditer(r'(\d+)\s+(?:POS\s+)?transakcij[ae]', text, re.IGNORECASE):
            self.extracted_facts['num_transactions'] = int(m.group(1))
        
        if amounts_raw:
            # Build readable amounts list
            amounts_formatted = []
            seen = set()
            for atype, val in amounts_raw:
                key = f"{val:.2f}"
                if key not in seen:
                    seen.add(key)
                    if val == int(val):
                        amounts_formatted.append(f"{int(val)} EUR")
                    else:
                        amounts_formatted.append(f"{val:.2f} EUR")
            self.extracted_facts['monetary_amounts'] = amounts_formatted
            
            # Calculate total falsified amount (use max of all found amounts)
            all_vals = [v for _, v in amounts_raw]
            if total_falsified > 0:
                self.extracted_facts['total_falsified_amount'] = total_falsified
            else:
                self.extracted_facts['total_falsified_amount'] = max(all_vals) if all_vals else 0
            
            if total_gain > 0:
                self.extracted_facts['total_gain_amount'] = total_gain
        
        # Serial numbers (for counterfeit money)
        serials = re.findall(r'serijs?k[io][g]?\s+broj[a]?\s+([A-Z0-9]+)', text)
        if serials:
            self.extracted_facts['serial_numbers'] = list(set(serials))
        
        # === WITNESSES ===
        witnesses = []
        # Full name witnesses: "svjedok/svedok Ime Prezime" or "svjedok-oštećeni Ime Prezime"
        witness_patterns = [
            r'(?:svjedok|svedok)[a]?(?:\s*[-–]\s*oštećen[aio]g?)?[,:]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\.?\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+\.?)',
            r'(?:svjedok|svedok)[a]?(?:\s*[-–]\s*oštećen[aio]g?)?[,:]?\s+([A-ZČĆŽŠĐ]\.?\s*[A-ZČĆŽŠĐ]\.?)',
            r'saslušan[aio]?\s+(?:svjedok|svedok)[a]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\.?\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+\.?)',
        ]
        for pattern in witness_patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                w = m.group(1).strip()
                # Filter out common non-name words
                if w and w not in witnesses and len(w) > 2:
                    if not any(word in w.lower() for word in ['sud', 'vijeć', 'optužen', 'okrivlj', 'tužio', 'branioc']):
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
    
    def _extract_actual_sentence(self, text: str):
        """Extract the actual sentence given by the court"""
        # Look for "USLOVNA OSUDA/PRESUDA" or "USLOVNU OSUDU/PRESUDU"
        if re.search(r'USLOVN[UAO]\s+OSUD[UAO]', text, re.IGNORECASE):
            self.extracted_facts['sentence_type'] = 'uslovna_osuda'
            # Extract the conditional sentence details
            # "kaznu zatvora u trajanju od X mjeseci" with probation "rok od Y godina"
            m = re.search(r'(?:utvr[đd]uje)?(?:\s+joj|\s+mu)?\s*kazn[aue]\s+zatvora\s+u\s+trajanju\s+od\s+(\d+)\s*\(?(\w+)\)?', text, re.IGNORECASE)
            if m:
                num = int(m.group(1))
                unit = m.group(2).lower()
                if 'mjesec' in unit or 'mesec' in unit:
                    self.extracted_facts['sentence_months'] = num
                    self.extracted_facts['actual_sentence_text'] = f"Uslovna presuda: {num} meseci zatvora"
                elif 'godin' in unit or 'leto' in unit:
                    self.extracted_facts['sentence_months'] = num * 12
                    self.extracted_facts['actual_sentence_text'] = f"Uslovna presuda: {num} god. zatvora"
                elif 'dan' in unit:
                    self.extracted_facts['sentence_months'] = round(num / 30, 1)
                    self.extracted_facts['actual_sentence_text'] = f"Uslovna presuda: {num} dana zatvora"
            else:
                self.extracted_facts['actual_sentence_text'] = 'Uslovna presuda'
            
            # Extract probation period
            m2 = re.search(r'(?:rok[u]?\s+(?:od\s+)?|u\s+roku\s+od\s+)(\d+)\s*\(?(\w+)\)?\s*(?:,|\s+)?(?:po\s+pravnosna|ne\s+u[čc]ini|od\s+dana)', text, re.IGNORECASE)
            if m2:
                prob_num = int(m2.group(1))
                prob_unit = m2.group(2).lower()
                if 'godin' in prob_unit:
                    self.extracted_facts['probation_years'] = prob_num
                    prev = self.extracted_facts.get('actual_sentence_text', 'Uslovna presuda')
                    self.extracted_facts['actual_sentence_text'] = f"{prev}, rok provere {prob_num} godine"
        
        # Look for effective prison sentence: "Na kaznu zatvora u trajanju od X"
        elif re.search(r'O\s*S\s*U\s*[ĐD]\s*U\s*J\s*E', text):
            m = re.search(r'(?:Na\s+)?kazn[aue]\s+zatvora\s+u\s+trajanju\s+od\s+(\d+)\s*\(?(\w+)\)?', text, re.IGNORECASE)
            if m:
                num = int(m.group(1))
                unit = m.group(2).lower()
                if 'mjesec' in unit or 'mesec' in unit:
                    self.extracted_facts['sentence_type'] = 'efektivni_zatvor'
                    self.extracted_facts['sentence_months'] = num
                    self.extracted_facts['actual_sentence_text'] = f"{num} meseci zatvora"
                elif 'godin' in unit:
                    self.extracted_facts['sentence_type'] = 'efektivni_zatvor'
                    self.extracted_facts['sentence_months'] = num * 12
                    self.extracted_facts['actual_sentence_text'] = f"{num} godina zatvora"
                elif 'dan' in unit:
                    self.extracted_facts['sentence_type'] = 'efektivni_zatvor'
                    self.extracted_facts['sentence_months'] = round(num / 30, 1)
                    self.extracted_facts['actual_sentence_text'] = f"{num} dana zatvora"
        
        # Broad fallback: try to find any "kazna zatvora u trajanju od X" pattern
        if 'actual_sentence_text' not in self.extracted_facts:
            m = re.search(r'kazn[aue]\s+zatvora\s+u\s+trajanju\s+od\s+(\d+)\s*\(?(\w+)\)?', text, re.IGNORECASE)
            if m:
                num = int(m.group(1))
                unit = m.group(2).lower()
                if 'mjesec' in unit or 'mesec' in unit:
                    self.extracted_facts['actual_sentence_text'] = f"{num} meseci zatvora"
                    self.extracted_facts['sentence_months'] = num
                elif 'godin' in unit:
                    self.extracted_facts['actual_sentence_text'] = f"{num} godina zatvora"
                    self.extracted_facts['sentence_months'] = num * 12
                elif 'dan' in unit:
                    self.extracted_facts['actual_sentence_text'] = f"{num} dana zatvora"
                    self.extracted_facts['sentence_months'] = round(num / 30, 1)
        
        # Also look for fine (novčana kazna)
        m = re.search(r'nov[čc]an[aou]\s+kazn[aou]\s+(?:u\s+iznosu\s+od\s+)?(\d+[,.]?\d*)\s*(?:eura?|EUR)', text, re.IGNORECASE)
        if m:
            self.extracted_facts['monetary_fine'] = f"{m.group(1)} EUR"
        
        # Security measure (mera bezbednosti)
        if re.search(r'MJERA\s+BEZBJEDNOSTI|mjera\s+bezbjednosti|MERA\s+BEZBEDNOSTI|mera\s+bezbednosti', text, re.IGNORECASE):
            self.extracted_facts['security_measure'] = True
            m = re.search(r'(?:Oduzimanj[ae]|oduzimanj[ae])\s+(.{10,100}?)(?:\.|,)', text)
            if m:
                self.extracted_facts['security_measure_detail'] = m.group(1).strip()
    
    def _extract_ublazavanje(self, text: str):
        """Extract sentence mitigation (ublažavanje kazne) information - čl. 45, 46 KZ"""
        # Check if court applied sentence mitigation
        if re.search(r'ubla[žz]avan[je]+\s+kazne|ubla[žz]i[ot]?\s+kazn|ubla[žz]en[aou]?\s+kazn', text, re.IGNORECASE):
            self.extracted_facts['ublazavanje_applied'] = True
        
        # Check for specific articles 45 and 46
        if re.search(r'[čc]l\.?\s*45', text):
            self.extracted_facts['ublazavanje_applied'] = True
            self.extracted_facts['ublazavanje_cl45'] = True
        
        if re.search(r'[čc]l\.?\s*46\s*(?:st\.?\s*(\d+))?\s*(?:ta[čc]\.?\s*(\d+))?', text):
            self.extracted_facts['ublazavanje_applied'] = True
            m = re.search(r'[čc]l\.?\s*46\s+st\.?\s*(\d+)\s+ta[čc]\.?\s*(\d+)', text)
            if m:
                self.extracted_facts['ublazavanje_cl46_st'] = int(m.group(1))
                self.extracted_facts['ublazavanje_cl46_tac'] = int(m.group(2))
        
        # Check for "naročito olakšavajuće okolnosti" (especially mitigating - key for ublažavanje)
        if re.search(r'naročito\\s+olakšavajuć|naro[čc]ito\\s+olak[šs]avaju[ćc]', text, re.IGNORECASE):
            self.extracted_facts['especially_mitigating'] = True
            self.extracted_facts['ublazavanje_applied'] = True
        
        # Check which specific sentencing articles were applied
        applied_articles = []
        for m in re.finditer(r'(?:primjenom\s+)?[čc]l\.?\s*(\d+)', text):
            art_num = int(m.group(1))
            if art_num in [42, 45, 46, 47, 48, 49, 52, 53, 54]:
                applied_articles.append(art_num)
        if applied_articles:
            self.extracted_facts['sentencing_articles_applied'] = list(set(applied_articles))
        
        # Check for suspended sentence articles (52, 53, 54)
        if 52 in applied_articles or 53 in applied_articles or 54 in applied_articles:
            self.extracted_facts['suspended_sentence_articles'] = True
    
    def _extract_acquittal_reason(self, text: str) -> str:
        """Extract the reason for acquittal"""
        if re.search(r'nije dokazano da je izvršil[ao]', text, re.IGNORECASE):
            return 'Nije dokazano da je optuženi izvršio delo za koje je optužen'
        if re.search(r'djelo.+nije krivično djelo', text, re.IGNORECASE):
            return 'Delo za koje je optužen nije krivično delo'
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
            
            # Check the Rel element to determine penalty type
            rel_elem = then_elem.find('.//ruleml:Rel', ns)
            rel_text = rel_elem.text if rel_elem is not None else ''
            
            if len(data_elems) >= 2:
                min_val = data_elems[0].text
                max_val = data_elems[1].text
                
                min_val = self._format_duration(min_val)
                max_val = self._format_duration(max_val)
                
                return PenaltyRange(min_val, max_val)
            elif len(data_elems) == 1:
                val = data_elems[0].text
                val = self._format_duration(val)
                # "kazna_zatvora_do" = open minimum (general min 30 days per KZ CG)
                # "kazna_zatvora" with single value = specific term
                if 'do' in rel_text.lower():
                    return PenaltyRange("30 dana", val)
                return PenaltyRange("N/A", val)
            
            return PenaltyRange()
        except Exception as e:
            print(f"Error extracting penalty: {e}", file=sys.stderr)
            return PenaltyRange()
    
    def _format_duration(self, duration_str: str) -> str:
        """Format duration string into readable format"""
        if not duration_str:
            return "N/A"
        
        # Explicit month values
        month_mapping = {
            '6_meseci': '6 meseci',
            '3_meseca': '3 meseca',
            '6_mjeseci': '6 meseci',
            '3_mjeseca': '3 meseca',
            '30_dana': '30 dana',
        }
        
        if duration_str in month_mapping:
            return month_mapping[duration_str]
        
        # Pure numbers are treated as years
        if duration_str.isdigit():
            num = int(duration_str)
            if num == 1:
                return "1 godina"
            elif num <= 4:
                return f"{num} godine"
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
        
        # Determine the best actual sentence display text
        archive_facts = self.case_facts.get_fact('archive_facts', {})
        raw_sentence = self.case_facts.get_fact('actual_sentence', 'N/A')
        is_conditional = self.case_facts.get_fact('conditional_sentence', False)
        archive_sentence_text = archive_facts.get('actual_sentence_text', '')
        
        # Prefer archive-extracted sentence text (has uslovna presuda prefix etc.)
        if archive_sentence_text:
            display_sentence = archive_sentence_text
        elif is_conditional and raw_sentence and raw_sentence != 'N/A':
            display_sentence = f"Uslovna presuda: {raw_sentence}"
        elif raw_sentence and raw_sentence not in ('N/A', 'Nepoznat', 'None', ''):
            display_sentence = raw_sentence
        else:
            display_sentence = 'N/A'
        
        analysis = {
            'case_number': self.case_facts.get_fact('case_number', 'Nepoznato'),
            'articles': self.case_facts.get_fact('articles', []),
            'verdict': verdict,
            'actual_sentence': display_sentence,
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
        
        # If acquittal, note it but STILL apply rules to see what they would recommend
        if is_acquittal:
            analysis['actual_verdict_note'] = 'Optuženi je u stvarnom postupku oslobođen od optužbe'
            if self.case_facts.get_fact('verdict_reason'):
                analysis['legal_analysis']['verdict_reason'] = self.case_facts.get_fact('verdict_reason')
            # Do NOT return early - continue with rule-based reasoning below
        
        # If judicial warning (sudska opomena), set actual sentence accordingly
        if 'opomena' in verdict_lower:
            analysis['actual_sentence'] = 'Sudska opomena'
            # Still continue with rule-based reasoning
        
        # Analyze each article
        for article in self.case_facts.get_fact('articles', []):
            analysis['applicable_articles'].append(article)
            
            # Find applicable rules for this article
            article_num = self._extract_article_number(article)
            article_para = self._extract_article_paragraph(article)
            if article_num:
                article_rules = self._get_applicable_rules_for_article(article_num)
                
                for rule in article_rules:
                    analysis['violated_rules'].append(rule.get('paraphrase', 'Rule'))
                    analysis['applicable_rules'].append({
                        'key': rule.get('key'),
                        'paraphrase': rule.get('paraphrase')
                    })
                
                # Get penalty range: prefer exact paragraph match, then most specific
                if article_rules:
                    # First, try to find exact paragraph match
                    best_rule = None
                    if article_para:
                        for rule in article_rules:
                            key = rule.get('key', '')
                            # Match patterns like rule_260_2, rule_258_2a, rule_258_2b
                            if f'_{article_num}_{article_para}' in key:
                                penalty = self.rule_parser.extract_penalty_from_rule(rule)
                                if penalty.min != 'N/A' or penalty.max != 'N/A':
                                    best_rule = rule
                                    break
                    
                    # Fallback: sort by specificity and pick best applicable
                    if not best_rule:
                        article_rules_sorted = sorted(
                            article_rules,
                            key=lambda r: self._get_rule_specificity(r),
                            reverse=True
                        )
                        for rule in article_rules_sorted:
                            if self._is_rule_applicable(rule):
                                best_rule = rule
                                break
                    
                    if best_rule:
                        penalty = self.rule_parser.extract_penalty_from_rule(best_rule)
                        analysis['penalty_range'] = penalty.to_dict()
                        self.base_penalty = penalty
        
        # If no articles found, check verdict for clues
        if not analysis['applicable_articles']:
            verdict = self.case_facts.get_fact('verdict', '').lower()
            # Check for acquittal first
            if 'oslobod' in verdict or 'oslobađ' in verdict:
                analysis['violated_rules'].append('Optuženi je oslobođen - krivično delo nije dokazano')
                analysis['penalty_range'] = {'min': 'N/A', 'max': 'N/A', 'note': 'Oslobađajuća presuda'}
                analysis['acquittal'] = True
            elif 'osud' in verdict or 'kriv' in verdict:
                analysis['violated_rules'].append('Utvrđena krivična odgovornost')
                analysis['penalty_range'] = {'min': '3 meseca', 'max': '10 godina'}
        
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
    
    def _extract_article_paragraph(self, article_str: str) -> Optional[str]:
        """Extract paragraph number from string like 'čl. 260 st. 2'"""
        match = re.search(r'st(?:av)?\.?\s*(\d+)', article_str, re.IGNORECASE)
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
        """Identify mitigating factors from case facts based on drdevice_rules.ddr and čl. 42 KZ CG"""
        # Note: We apply rules even for acquittals to show what rules would recommend
        
        archive = self.case_facts.get_fact('archive_facts', {})
        
        # First offense (ranije_neosudjivan) - čl. 42 st. 1
        prior = self.case_facts.get_fact('previously_convicted')
        if prior is None:
            prior = archive.get('prior_convictions', None)
        if not prior:
            self.mitigating_factors.append('Ranije neosudivan')
            analysis['mitigating_factors'].append('Ranije neosudivan (čl. 42)')
        
        # Confession / guilty plea - čl. 42 (okolnosti nakon djela)
        confession = archive.get('confession', None)
        if confession is None:
            confession = self.case_facts.get_fact('confession', None)
        if confession:
            self.mitigating_factors.append('Priznanje krivice')
            analysis['mitigating_factors'].append('Priznanje krivice (čl. 42)')
        
        # Plea agreement
        if archive.get('plea_agreement', False):
            self.mitigating_factors.append('Sporazum o priznanju krivice')
            analysis['mitigating_factors'].append('Sporazum o priznanju krivice')
        
        # Remorse (kajanje) - čl. 42
        if archive.get('remorse', False):
            self.mitigating_factors.append('Kajanje/pokajanje')
            analysis['mitigating_factors'].append('Kajanje (čl. 42)')
        
        # Restitution (naknada štete) - čl. 42
        if archive.get('restitution', False):
            self.mitigating_factors.append('Naknada štete')
            analysis['mitigating_factors'].append('Naknada/vraćanje štete (čl. 42)')
        
        # Family circumstances (has children) - čl. 42 (porodične prilike)
        if archive.get('has_children', False):
            self.mitigating_factors.append('Porodične prilike - ima decu')
            analysis['mitigating_factors'].append('Porodične prilike - ima decu (čl. 42)')
        
        # Unemployment / poor financial status - čl. 42 (lične prilike)
        employment = archive.get('employment', '')
        if employment and ('nezaposlen' in employment.lower()):
            self.mitigating_factors.append('Nezaposlen - loše materijalno stanje')
            analysis['mitigating_factors'].append('Loše materijalno stanje (čl. 42)')
        
        # Small amount is MITIGATING (mali_iznos < 500 EUR per drdevice_rules.ddr)
        max_amount = self._get_max_amount()
        if max_amount is not None and max_amount < 500:
            analysis['mitigating_factors'].append(f'Mali iznos štete (ispod 500 EUR)')
        

    
    def _identify_aggravating_factors(self, analysis: Dict):
        """Identify aggravating factors from case facts based on drdevice_rules.ddr"""
        # Note: We apply rules even for acquittals to show what rules would recommend
        
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
        """
        Calculate recommended sentence applying čl. 42, 45, 46, 47, 52 KZ CG.
        
        Key logic from Montenegrin Criminal Code:
        - čl. 42: General sentencing factors (mitigating/aggravating)
        - čl. 45: Ublažavanje (mitigation below minimum) when "naročito olakšavajuće okolnosti"
        - čl. 46 st. 1: Mitigation limits:
            tač. 1: min 5+ years -> can go down to 2 years
            tač. 2: min 3+ years -> can go down to 1 year
            tač. 3: min 2+ years -> can go down to 6 months
            tač. 4: min 1+ year  -> can go down to 3 months
            tač. 5: general min   -> can go down to 30 days
            tač. 6: prison min   -> can impose fine instead
        - čl. 47: Full release from punishment (in exceptional cases with restitution)
        - čl. 52: Uslovna presuda (suspended sentence) when sentence ≤ 2 years
        """
        
        verdict = self.case_facts.get_fact('verdict', '').lower()
        
        # Note: Even for acquittals and opomena, we continue with rule-based reasoning
        # to show what the rules would recommend - we don't short-circuit here
        
        penalty_range = analysis['penalty_range']
        if penalty_range['min'] == 'N/A':
            return 'N/A'
        
        # Parse penalty range from rules (drdevice_rules.ddr)
        min_years = self._parse_penalty_to_years(penalty_range['min'])
        max_years = self._parse_penalty_to_years(penalty_range['max'])
        
        if min_years is None or max_years is None:
            return 'N/A'
        
        num_mitigating = len(analysis['mitigating_factors'])
        num_aggravating = len(analysis['aggravating_factors'])
        archive = self.case_facts.get_fact('archive_facts', {})
        
        # === STEP 1: Check for čl. 47 - Oslobođenje od kazne ===
        # Exceptional case: restitution + many strong mitigating factors 
        if (archive.get('restitution', False) and 
            num_mitigating >= 4 and num_aggravating == 0):
            analysis.setdefault('reasoning_steps', []).append(
                'čl. 47: Razmotreno oslobođenje od kazne (restitucija + 4+ olakšavajućih)')
        
        # === STEP 2: Determine if Ublažavanje (čl. 45) is applicable ===
        # Ublažavanje below statutory minimum is only meaningful when min >= 1 year
        # For lower minimums, courts sentence near the minimum using čl. 42 factors
        ublazavanje_applicable = False
        ublazavanje_reason = ''
        
        if min_years >= 1:
            # Ublažavanje when "naročito olakšavajuće okolnosti" (čl. 45)
            # In practice: 2+ mitigating with NO aggravating
            if num_mitigating >= 2 and num_aggravating == 0:
                ublazavanje_applicable = True
                ublazavanje_reason = f'Naročito olakšavajuće okolnosti ({num_mitigating} olakšavajućih, 0 otežavajućih) - čl. 45'
            
            # Also if archive explicitly notes ublažavanje
            if archive.get('ublazavanje_applied', False):
                ublazavanje_applicable = True
                ublazavanje_reason = 'Sud primenio ublažavanje kazne - čl. 45, 46'
        
        # Strong ublažavanje: 3+ mitigating factors
        strong_ublazavanje = num_mitigating >= 3 and num_aggravating == 0
        
        # === STEP 3: Apply čl. 46 - Calculate mitigated minimum ===
        mitigated_min_years = min_years  # Start with statutory minimum
        
        if ublazavanje_applicable:
            if min_years >= 5:
                # tač. 1: min 5+ godina → može do 2 godine
                mitigated_min_years = 2.0
                analysis.setdefault('reasoning_steps', []).append(
                    'čl. 46 st. 1 tač. 1: Zakonski minimum ≥5 godina → ublaženo do 2 godine')
            elif min_years >= 3:
                # tač. 2: min 3+ godina → može do 1 godine
                mitigated_min_years = 1.0
                analysis.setdefault('reasoning_steps', []).append(
                    'čl. 46 st. 1 tač. 2: Zakonski minimum ≥3 godine → ublaženo do 1 godine')
            elif min_years >= 2:
                # tač. 3: min 2+ godina → može do 6 meseci
                mitigated_min_years = 0.5
                analysis.setdefault('reasoning_steps', []).append(
                    'čl. 46 st. 1 tač. 3: Zakonski minimum ≥2 godine → ublaženo do 6 meseci')
            elif min_years >= 1:
                # tač. 4: min 1+ godina → može do 3 meseca
                mitigated_min_years = 0.25
                analysis.setdefault('reasoning_steps', []).append(
                    'čl. 46 st. 1 tač. 4: Zakonski minimum ≥1 godina → ublaženo do 3 meseca')
        
        # === STEP 4: Calculate recommended sentence ===
        if ublazavanje_applicable:
            # Sentence range with ublažavanje: [mitigated_min, statutory_min]
            ub_range = min_years - mitigated_min_years
            
            if strong_ublazavanje:
                # Strong mitigation (3+ factors) → sentence at mitigated minimum
                # Pattern: čl. 258/2 (min 2yr) with 3+ factors → 6 months
                rec_years = mitigated_min_years
            else:
                # Regular ublažavanje (2 factors) → slightly above mitigated minimum
                rec_years = mitigated_min_years + (ub_range * 0.15)
            
            analysis.setdefault('reasoning_steps', []).append(
                f'Ublažavanje primenjeno: {ublazavanje_reason}')
            analysis.setdefault('reasoning_steps', []).append(
                f'Raspon kazne nakon ublažavanja: {self._format_years(mitigated_min_years)} - {self._format_years(min_years)}')
        else:
            # No ublažavanje: sentence within normal [min, max] range
            range_span = max_years - min_years
            
            if num_aggravating > 0 and num_mitigating == 0:
                # Only aggravating → upper portion
                base_factor = 0.5 if num_aggravating >= 2 else 0.35
            elif num_mitigating > 0 and num_aggravating > 0:
                # Both present → balance
                net = num_aggravating - num_mitigating
                base_factor = max(0.1, min(0.6, 0.25 + (net * 0.1)))
            elif num_mitigating >= 2:
                # 2+ mitigating, no aggravating, but min too low for ublažavanje
                # → sentence AT the statutory minimum
                base_factor = 0.0
                analysis.setdefault('reasoning_steps', []).append(
                    f'čl. 42: Olakšavajuće okolnosti - kazna na zakonskom minimumu')
            elif num_mitigating == 1:
                # One mitigating → near minimum
                base_factor = 0.05
            else:
                # No factors → lower-mid range
                base_factor = 0.15
            
            rec_years = min_years + (range_span * base_factor)
            rec_years = max(min_years, min(max_years, rec_years))
        
        # === STEP 5: Check for Uslovna presuda (čl. 52) ===
        # Suspended sentence possible when: rec ≤ 2 years AND mitigating factors exist
        uslovna_osuda = False
        probation_years = 2
        
        if rec_years <= 2 and num_mitigating >= 1 and num_aggravating == 0:
            uslovna_osuda = True
            if rec_years <= 0.5:
                probation_years = 2  # 6mo → 2yr probation (common)
            elif rec_years <= 1:
                probation_years = 2
            else:
                probation_years = 3
            
            analysis.setdefault('reasoning_steps', []).append(
                f'čl. 52: Uslovna presuda moguća (kazna ≤ 2 godine, olakšavajuće okolnosti)')
        
        # Archive explicitly noted suspended sentence
        if archive.get('suspended_sentence_articles', False) and rec_years <= 2:
            uslovna_osuda = True
        
        # === STEP 6: Format final recommendation ===
        if uslovna_osuda:
            return f'Uslovna presuda: {self._format_years(rec_years)}, rok provere {probation_years} godine (čl. 52)'
        
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
        
        # Handle days
        if 'dan' in penalty_str:
            return num / 365
        
        # Handle months
        if 'mjesec' in penalty_str or 'mesec' in penalty_str:
            return num / 12
        
        return num
    
    def _format_years(self, years: float) -> str:
        """Format years to readable string"""
        if years < 1:
            months = int(years * 12)
            if months == 1:
                return "1 mesec"
            return f"{months} meseci"
        
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
        
        return f"{years_int} godina {months} meseci"
    
    def _generate_analysis(self, analysis: Dict) -> List[str]:
        """Generate detailed analysis text"""
        lines = []
        
        case_num = analysis['case_number']
        lines.append(f"Analiza predmeta: {case_num}")
        
        if analysis['articles']:
            articles_str = ", ".join(analysis['articles'])
            lines.append(f"Primenjeni članci: {articles_str}")
        
        if analysis['mitigating_factors']:
            lines.append(f"Olakšavajuće okolnosti ({len(analysis['mitigating_factors'])}):")
            for factor in analysis['mitigating_factors']:
                lines.append(f"  - {factor}")
        
        if analysis['aggravating_factors']:
            lines.append(f"Otežavajuće okolnosti ({len(analysis['aggravating_factors'])}):")
            for factor in analysis['aggravating_factors']:
                lines.append(f"  - {factor}")
        
        # Show reasoning steps (čl. 42-52 application)
        reasoning_steps = analysis.get('reasoning_steps', [])
        if reasoning_steps:
            lines.append("Pravno rezonovanje:")
            for step in reasoning_steps:
                lines.append(f"  → {step}")
        
        # Compare recommendation with actual
        recommendation = analysis['recommendation']
        actual = self.case_facts.get_fact('actual_sentence', 'N/A')
        archive = self.case_facts.get_fact('archive_facts', {})
        actual_text = archive.get('actual_sentence_text', actual)
        
        # Note acquittal status
        if analysis.get('acquittal'):
            lines.append("NAPOMENA: Optuženi je u stvarnom postupku oslobođen od optužbe.")
            lines.append("Rezonovanje po pravilima se ipak primenjuje da bi se videlo šta pravila kažu:")
        
        if actual_text and actual_text != 'N/A' and recommendation != 'N/A':
            lines.append(f"Preporučena kazna (po pravilima): {recommendation}")
            lines.append(f"Stvarna kazna: {actual_text}")
        elif recommendation != 'N/A':
            lines.append(f"Preporučena kazna (po pravilima): {recommendation}")
        
        return lines


class DrDeviceReasoner:
    """
    Integrates DR-Device defeasible reasoning into the case analysis pipeline.
    
    Pipeline: case facts → facts.rdf + facts.n3 → CLIPSDOS (rulebase.clp) → export.rdf → parsed results
    
    DR-Device performs defeasible reasoning with overrides:
    - Qualified offenses override basic offenses (e.g., čl. 258 st. 2 > st. 1)
    - Aggravating factors can block mitigation allowance
    - Aggravating factors can block suspended sentence eligibility
    """
    
    DR_DEVICE_DIR = PROJECT_ROOT / 'dr-device'
    LC_NS = 'http://informatika.ftn.uns.ac.rs/legal-case.rdf#'
    
    def __init__(self, case_facts_dict: Dict):
        """
        Args:
            case_facts_dict: Dictionary of case facts (from CaseFactsExtractor.facts
                             or parsed JSON facts)
        """
        self.facts = case_facts_dict
        self.dr_device_dir = self.DR_DEVICE_DIR
    
    def _map_article(self) -> str:
        """Map case articles to DR-Device article number (258 or 260)."""
        articles = self.facts.get('articles', [])
        for article in articles:
            if '258' in str(article):
                return '258'
            if '260' in str(article):
                return '260'
        # Try crime_type field
        crime_type = self.facts.get('crime_type', '')
        if 'falsifikovan' in crime_type.lower() and 'novca' in crime_type.lower():
            return '260'
        if 'kartic' in crime_type.lower() or 'kreditn' in crime_type.lower():
            return '258'
        return ''
    
    def _get_max_amount(self) -> float:
        """Extract maximum monetary amount from case facts."""
        amounts = self.facts.get('amounts', [])
        max_val = 0.0
        for amount in amounts:
            try:
                clean = re.sub(r'[^\d.,]', '', str(amount))
                if not clean:
                    continue
                last_comma = clean.rfind(',')
                last_dot = clean.rfind('.')
                if last_comma > last_dot:
                    clean = clean.replace('.', '').replace(',', '.')
                else:
                    clean = clean.replace(',', '')
                val = float(clean)
                max_val = max(max_val, val)
            except (ValueError, TypeError):
                pass
        return max_val
    
    def _bool_to_yesno(self, val) -> str:
        """Convert various boolean representations to 'yes'/'no'."""
        if val is True:
            return 'yes'
        if val is False or val is None:
            return 'no'
        val_str = str(val).lower().strip()
        if val_str in ('da', 'yes', 'true', '1'):
            return 'yes'
        return 'no'
    
    def generate_facts_rdf(self) -> str:
        """Generate facts.rdf from case facts dictionary."""
        article = self._map_article()
        if not article:
            return ''
        
        max_amount = self._get_max_amount()
        archive = self.facts.get('archive_facts', {})
        defendant = self.facts.get('defendant', 'Okrivljeni') or 'Okrivljeni'
        
        # Map boolean facts
        confession = self._bool_to_yesno(
            archive.get('confession', self.facts.get('confession')))
        prior = self._bool_to_yesno(self.facts.get('previously_convicted'))
        remorse = self._bool_to_yesno(archive.get('remorse'))
        restitution = self._bool_to_yesno(archive.get('restitution'))
        has_children = self._bool_to_yesno(archive.get('has_children'))
        cooperation = self._bool_to_yesno(archive.get('cooperation'))
        organized = self._bool_to_yesno(archive.get('organized_crime'))
        gained_profit = self._bool_to_yesno(archive.get('gained_profit'))
        
        rdf = f'''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:lc="http://informatika.ftn.uns.ac.rs/legal-case.rdf#">
  <lc:case rdf:about="http://informatika.ftn.uns.ac.rs/legal-case.rdf#case01">
    <lc:defendant>{defendant}</lc:defendant>
    <lc:article>{article}</lc:article>
    <lc:amount_over_15000>{"yes" if max_amount > 15000 else "no"}</lc:amount_over_15000>
    <lc:amount_over_3000>{"yes" if max_amount > 3000 else "no"}</lc:amount_over_3000>
    <lc:amount_over_30000>{"yes" if max_amount > 30000 else "no"}</lc:amount_over_30000>
    <lc:gained_profit>{gained_profit}</lc:gained_profit>
    <lc:confession>{confession}</lc:confession>
    <lc:prior_conviction>{prior}</lc:prior_conviction>
    <lc:remorse>{remorse}</lc:remorse>
    <lc:restitution>{restitution}</lc:restitution>
    <lc:has_children>{has_children}</lc:has_children>
    <lc:cooperation>{cooperation}</lc:cooperation>
    <lc:organized_crime>{organized}</lc:organized_crime>
  </lc:case>
</rdf:RDF>'''
        return rdf
    
    def _rdf_to_n3(self, rdf_content: str) -> str:
        """Convert RDF/XML to NTriples format (bypasses Java Jena requirement)."""
        lines = []
        lc = self.LC_NS
        rdf_ns = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
        
        try:
            root = ET.fromstring(rdf_content)
        except ET.ParseError:
            return ''
        
        for elem in root:
            tag = elem.tag
            # Extract class name from tag like {ns}case
            if '}' in tag:
                ns, local = tag.split('}', 1)
                ns = ns[1:]  # remove leading {
            else:
                continue
            
            about = elem.get(f'{{{rdf_ns}}}about', '')
            if not about:
                continue
            
            # rdf:type triple
            lines.append(f'<{about}> <{rdf_ns}type> <{ns}{local}> .')
            
            # Property triples
            for prop in elem:
                ptag = prop.tag
                if '}' in ptag:
                    pns, plocal = ptag.split('}', 1)
                    pns = pns[1:]
                else:
                    continue
                
                text = (prop.text or '').strip()
                if text:
                    lines.append(f'<{about}> <{pns}{plocal}> "{text}" .')
        
        return '\n'.join(lines) + '\n'
    
    def run_clipsdos(self) -> Tuple[bool, str]:
        """Run CLIPSDOS.exe and return (success, stdout)."""
        clips = self.dr_device_dir / 'CLIPSDOS' / 'CLIPSDOS.exe'
        if not clips.exists():
            return False, f'CLIPSDOS.exe not found at {clips}'
        
        try:
            result = subprocess.run(
                [str(clips), '-f2', 'start.clp'],
                cwd=str(self.dr_device_dir),
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, 'DR-Device timed out (30s)'
        except Exception as e:
            return False, str(e)
    
    def parse_export_rdf(self) -> Dict:
        """Parse export.rdf for defeasibly proven conclusions."""
        export_path = self.dr_device_dir / 'export.rdf'
        if not export_path.exists():
            return {'error': 'No export.rdf generated'}
        
        content = export_path.read_text(encoding='utf-8', errors='replace')
        
        results = {
            'proven_conclusions': [],
            'guilt': None,
            'guilt_label': None,
            'has_mitigating': False,
            'has_aggravating': False,
            'mitigation_allowed': False,
            'suspended_sentence_possible': False,
            'penalty_min_months': None,
            'penalty_max_months': None,
        }
        
        # Parse using regex (DOCTYPE entities make ET parsing difficult)
        blocks = re.findall(
            r'<export:(\w+)\s+rdf:about=[^>]+>(.*?)</export:\1>',
            content, re.DOTALL
        )
        
        guilt_labels = {
            'guilty_258_basic': 'Čl. 258 st. 1 (osnovno delo)',
            'guilty_258_qualified': 'Čl. 258 st. 2 (kvalifikovani oblik - iznos preko 15.000 EUR)',
            'guilty_260_basic': 'Čl. 260 st. 1 (osnovno delo)',
            'guilty_260_gain': 'Čl. 260 st. 2 (sticanje imovinske koristi)',
            'guilty_260_high': 'Čl. 260 st. 3 (iznos preko 30.000 EUR)',
            'guilty_260_very_high': 'Čl. 260 st. 4 (iznos preko 40.000 EUR)',
        }
        
        for class_name, block_content in blocks:
            truth = re.search(r'truthStatus[^>]*>([^<]+)', block_content)
            if truth and 'proven-positive' in truth.group(1):
                results['proven_conclusions'].append(class_name)
                
                if class_name.startswith('guilty_'):
                    results['guilt'] = class_name
                    results['guilt_label'] = guilt_labels.get(class_name, class_name)
                elif class_name == 'has_mitigating':
                    results['has_mitigating'] = True
                elif class_name == 'has_aggravating':
                    results['has_aggravating'] = True
                elif class_name == 'mitigation_allowed':
                    results['mitigation_allowed'] = True
                elif class_name == 'suspended_sentence_possible':
                    results['suspended_sentence_possible'] = True
                elif class_name == 'to_imprison_min':
                    val = re.search(r'value[^>]*>(\d+)', block_content)
                    if val:
                        results['penalty_min_months'] = int(val.group(1))
                elif class_name == 'to_imprison_max':
                    val = re.search(r'value[^>]*>(\d+)', block_content)
                    if val:
                        results['penalty_max_months'] = int(val.group(1))
        
        return results
    
    def parse_proof_ruleml(self) -> List[Dict]:
        """Parse proof.ruleml for reasoning chain (proof tree)."""
        proof_path = self.dr_device_dir / 'proof.ruleml'
        if not proof_path.exists():
            return []
        
        content = proof_path.read_text(encoding='utf-8', errors='replace')
        proofs = []
        
        # Extract each Defeasibly_Proved block
        proved_blocks = re.findall(
            r'<Defeasibly_Proved>(.*?)</Defeasibly_Proved>',
            content, re.DOTALL
        )
        
        for block in proved_blocks:
            proof = {}
            # Extract conclusion
            resource = re.search(r'RDF_resource\s+uri=[\'"]([^"\']+)', block)
            if resource:
                uri = resource.group(1).split(';')[-1] if ';' in resource.group(1) else resource.group(1)
                proof['conclusion'] = uri.rstrip("'\"")
            
            # Extract supporting rule
            rule_ref = re.search(r'supportive_rule.*?rule=[\'"](\w+)', block, re.DOTALL)
            if rule_ref:
                proof['rule'] = rule_ref.group(1)
            
            # Check if any attackers were blocked
            if '<Blocked>' in block:
                proof['had_blocked_attackers'] = True
                blocked_rule = re.search(
                    r'Blocked_Defeasible_rule.*?rule=[\'"](\w+)', block, re.DOTALL)
                if blocked_rule:
                    proof['blocked_rule'] = blocked_rule.group(1)
            
            if proof:
                proofs.append(proof)
        
        return proofs
    
    def run(self) -> Dict:
        """
        Execute the full DR-Device defeasible reasoning pipeline.
        
        Returns:
            Dictionary with proven conclusions, guilt determination,
            penalty range, and proof chain.
        """
        # Step 1: Generate facts.rdf
        rdf = self.generate_facts_rdf()
        if not rdf:
            return {
                'status': 'skipped',
                'reason': 'No applicable article (258/260) found for DR-Device'
            }
        
        # Write facts.rdf
        facts_rdf_path = self.dr_device_dir / 'facts.rdf'
        facts_rdf_path.write_text(rdf, encoding='utf-8')
        
        # Step 2: Generate facts.n3 (bypasses Java Jena for NTriples)
        n3 = self._rdf_to_n3(rdf)
        facts_n3_path = self.dr_device_dir / 'facts.n3'
        facts_n3_path.write_text(n3, encoding='utf-8')
        
        # Step 3: Ensure rulebase.clp exists
        clp_path = self.dr_device_dir / 'rulebase.clp'
        if not clp_path.exists():
            self._ensure_rulebase()
        
        # Step 4: Run CLIPSDOS
        success, output = self.run_clipsdos()
        if not success:
            return {
                'status': 'error',
                'reason': f'CLIPSDOS failed: {output[:500]}'
            }
        
        # Step 5: Parse results
        results = self.parse_export_rdf()
        results['status'] = 'success'
        
        # Step 6: Parse proof chain
        results['proof_chain'] = self.parse_proof_ruleml()
        
        # Step 7: Format human-readable summary
        results['summary'] = self._format_summary(results)
        
        return results
    
    def _ensure_rulebase(self):
        """Ensure rulebase.clp exists by running the transform pipeline."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "transform_lrml",
                str(self.dr_device_dir / "transform_lrml.py"),
            )
            mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            
            lrml_path = self.dr_device_dir / 'rulebase.lrml'
            ruleml_path = self.dr_device_dir / 'rulebase.ruleml'
            clp_path = self.dr_device_dir / 'rulebase.clp'
            
            transformer = mod.LrmlToRulemlTransformer(str(lrml_path), 'facts.rdf')
            ruleml_content = transformer.transform()
            ruleml_path.write_text(ruleml_content, encoding='utf-8')
            
            clips_transformer = mod.RulemlToClipsTransformer(str(ruleml_path))
            clips_content = clips_transformer.transform()
            clp_path.write_text(clips_content, encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not generate rulebase.clp: {e}", file=sys.stderr)
    
    def _format_summary(self, results: Dict) -> str:
        """Format a human-readable summary of DR-Device conclusions."""
        lines = []
        
        if results.get('guilt_label'):
            lines.append(f"Krivica: {results['guilt_label']}")
        
        if results.get('has_mitigating'):
            lines.append("Olakšavajuće okolnosti: utvrđene (defeasibly proven)")
        if results.get('has_aggravating'):
            lines.append("Otežavajuće okolnosti: utvrđene (defeasibly proven)")
        
        if results.get('mitigation_allowed'):
            lines.append("Ublažavanje kazne: dozvoljeno (čl. 45 KZ CG)")
        if results.get('suspended_sentence_possible'):
            lines.append("Uslovna presuda: moguća (čl. 52 KZ CG)")
        
        min_m = results.get('penalty_min_months')
        max_m = results.get('penalty_max_months')
        if min_m is not None and max_m is not None:
            lines.append(f"Raspon kazne: {min_m} - {max_m} meseci zatvora")
        
        return '; '.join(lines) if lines else 'Nema zaključaka'


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
            
            # Run DR-Device defeasible reasoning
            try:
                dr_reasoner = DrDeviceReasoner(case_facts.facts)
                dr_results = dr_reasoner.run()
                result['dr_device_reasoning'] = dr_results
            except Exception as e:
                result['dr_device_reasoning'] = {'status': 'error', 'reason': str(e)}
        
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
                
                # Run DR-Device defeasible reasoning
                try:
                    dr_reasoner = DrDeviceReasoner(facts_dict)
                    dr_results = dr_reasoner.run()
                    result['dr_device_reasoning'] = dr_results
                except Exception as e:
                    result['dr_device_reasoning'] = {'status': 'error', 'reason': str(e)}
                
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

