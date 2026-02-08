#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced Verdict Extractor - Poboljšani ekstraktor presuda
Extracts detailed information from Montenegrin court verdict files
and generates Akoma Ntoso 3.0 XML files with Serbian field names.

IMPROVED VERSION: Better patterns for sudija, opis_slucaja, tip_krivicnog_djela
"""

import os
import re
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from pathlib import Path


class EnhancedVerdictExtractor:
    """Extracts comprehensive data from verdict text files."""
    
    def __init__(self):
        self.verdict_patterns = {
            # Court information - expanded patterns
            'sud': [
                r'(?:OSNOVNI SUD U|Osnovni Sud u|VIŠI SUD U|Viši Sud u)\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)*)',
                r'Osnovni\s+sud\s+u\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+)',
                r'OSNOVNI\s+SUD\s+U\s+([A-ZČĆŽŠĐ]+(?:\s+[A-ZČĆŽŠĐ]+)*)',
            ],
            # Case number - expanded patterns
            'broj_predmeta': [
                r'(?:K\.?\s*br\.?|Posl\.\s*br\.?|K\.br\.)\s*[:\s]*(\d+/\d+(?:/\d+)?)',
                r'K\s+(\d+/\d+)',
                r'K\.?\s*(\d+/\d{2,4})',
            ],
            # Date - expanded patterns
            'datum': [
                r'(?:dana|Dana)\s+(\d{1,2}\.\s*\d{1,2}\.\s*\d{4})',
                r'(\d{1,2}\.\s*(?:januar|februar|mart|april|maj|jun|jul|avgust|septembar|oktobar|novembar|decembar)[a-z]*\s*\d{4})',
                r'(\d{1,2}\.\s*\w+\s+\d{4})\s*(?:godine|god\.?)',
                r'(\d{1,2}\.\s*[A-Za-z]+\s+\d{4})',
            ],
            # Judge - SIGNIFICANTLY EXPANDED PATTERNS
            'sudija': [
                # Direct patterns like "sudija Tamara Spasojević"
                r'sudija\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
                # Pattern: "sudija pojedinac" with name
                r'sudija\s+pojedinac[,\s]+(?:sa\s+)?([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
                # Pattern: "i to sudija Name Name"
                r'i\s+to\s+sudija\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
                # Pattern at the end of document: "S u d i j a," followed by name
                r'S\s*u\s*d\s*i\s*j\s*a\s*[,:]?\s*\n+\s*([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
                # Pattern: "po sudiji Name Name"
                r'po\s+sudiji\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
                # Pattern: "sudije Name Name"
                r'sudije\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
                # Pattern: "predsjednika vijeća" 
                r'(?:predsjednika\s+vijeća|vijeću)[,\s]+(?:i\s+)?(?:sudija?\s+)?([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
                # Pattern: "krivični, sudija Name"
                r'krivični[,\s]+(?:i\s+to\s+)?sudija\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
                # Pattern with comma: ", sudija Name Name,"
                r',\s*sudija\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)\s*,',
                # Fallback: look for "Zapisničar Sudija" section at end
                r'Zapisničar\s+S\s*u\s*d\s*i\s*j\s*a\s*[,:]?\s*\n*[^A-Za-z]*([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)\s*$',
            ],
            # Defendant - Optuženi/Okrivljeni
            'optuzeni': [
                r'(?:Okrivljen[iaeo]|okrivljen[iaeo])\s+([A-ZČĆŽŠĐ][\.\s][A-ZČĆŽŠĐ][\.\s]?)',
                r'(?:Optužen[iaeo]|optužen[iaeo])\s+([A-ZČĆŽŠĐ][\.\s][A-ZČĆŽŠĐ][\.\s]?)',
                r'(?:protiv\s+okrivljenog|protiv\s+okrivljene)\s+([A-ZČĆŽŠĐ][\.\s][A-ZČĆŽŠĐ][\.\s]?)',
                r'Okrivljeni[,\s]*\n+\s*([A-ZČĆŽŠĐ]\.\s*[A-ZČĆŽŠĐ]\.)',
                r'(?:optuženog|okrivljenog)\s+([A-ZČĆŽŠĐ]\.\s*[A-ZČĆŽŠĐ]\.)',
            ],
            # Parent info
            'podaci_o_roditeljima': [
                r'od\s+oca\s+([A-ZČĆŽŠĐ][a-zčćžšđ]*\.?)\s+i\s+majke\s+([A-ZČĆŽŠĐ][a-zčćžšđ]*\.?)',
            ],
            # Birth year/date
            'godina_rodjenja': [
                r'rođen(?:a)?\s+(\d{2}\.\d{2}\.\d{4})\s*(?:godine|god\.?)?',
                r'rođen(?:a)?(?:\s+\.+)?\s*godine\s+u',
            ],
            # Residence
            'prebivaliste': [
                r'(?:sa prebivalištem|stalno nastanjen|živi)\s+(?:u\s+)?([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:[\s,]+[A-Za-zčćžšđČĆŽŠĐ\s]+)?)',
                r'nastanjen\s+u\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            ],
            # Employment status
            'zaposlenost': [
                r'(nezaposlen[a]?)',
                r'(zaposlen[a]?\s+(?:kao|u|na)\s+[^,]+)',
            ],
            # Marital status
            'bracni_status': [
                r'(neoženjen|oženjen|neudata|udata|razveden[a]?)',
            ],
            # Education
            'obrazovanje': [
                r'(?:sa završen(?:om|im)|završio|završila)\s+((?:OŠ|SSS|VSS|srednju školu|osnovnu školu|fakultet)[^,]*)',
                r'(pismen[a]?)',
                r'završio\s+(Srednju\s+[Šš]kolu)',
                r'završena\s+(SSS|srednja\s+škola)',
            ],
            # Prior convictions
            'ranije_osudjivan': [
                r'((?:ranije\s+)?(?:ne)?osuđivan(?:a)?)',
                r'(ne\s+osudjivan)',
                r'(neosuđivan)',
            ],
            # Criminal article
            'clan_kz': [
                r'čl\.?\s*(\d+)\s*(?:st\.?\s*(\d+))?',
            ],
            # Crime type - SIGNIFICANTLY EXPANDED PATTERNS
            'tip_krivicnog_djela': [
                # Direct crime type mentions
                r'(?:krivičn(?:og?|e)\s+djel(?:o|a))\s+(falsifikovanje\s+novca)',
                r'(?:krivičn(?:og?|e)\s+djel(?:o|a))\s+(falsifikovanje\s+i\s+zloupotreba\s+kreditnih\s+kartica[^,]*)',
                # From the header/metadata
                r'zbog\s+krivičnog\s+djela\s+(falsifikovanje\s+novca)',
                r'zbog\s+krivičnog\s+djela\s+(falsifikovanje\s+i\s+zloupotreba\s+kreditnih\s+kartica[^,]*)',
                # Produženo krivično djelo
                r'produženo\s+krivično\s+djelo\s+(falsifikovanje[^,]+?)(?:\s+iz\s+čl\.)',
                # From "čime je izvršio"
                r'čime\s+je\s+izvršio\s+(?:produženo\s+)?krivično\s+djelo\s*[-–]?\s*(falsifikovanje[^,\n]+)',
                # From article reference
                r'iz\s+čl\.?\s*258[^,]*',  # Article 258 = falsifikovanje novca
                r'iz\s+čl\.?\s*260[^,]*',  # Article 260 = falsifikovanje kreditnih kartica
                # Sticaj patterns
                r'u\s+sticaju\s+sa\s+krivičnim\s+djelom\s+(falsifikovanje[^,]+)',
            ],
            # Sentence - Kazna - EXPANDED
            'kazna': [
                r'(?:KAZN[UAU]\s+ZATVORA|kazn[ua]\s+zatvora)\s+u\s+trajanju\s+od\s+(\d+(?:\s*\([^)]+\))?\s*(?:godina?|godin[ea]|mjesec[ia]?|dan[ai]?))',
                r'(?:Na\s+)?kaznu\s+zatvora\s+u\s+trajanju\s+od\s+(\d+\s*\([^)]+\)\s*(?:godina?|godin[ea]|mjesec[ia]?))',
                r'kazn[ua]\s+zatvora\s+(?:u\s+trajanju\s+)?od\s+(\d+\s*mjesec[ia]?)',
                r'(\d+\s*\([^)]+\)\s*(?:godina?|mjesec[ia]?))',
                r'USLOVN[UAU]\s+OSUD[UAU]',
            ],
            # Suspended sentence
            'uslovna_osuda': [
                r'USLOVN[UAU]\s+OSUD[UAU]',
                r'uslovno\s+na\s+(\d+\s*(?:godine?|mjesec[ia]))',
                r'USLOVNU\s+OSUDU',
                r'izriče\s+USLOVNU\s+OSUDU',
            ],
            # Fine - Novčana kazna
            'novcana_kazna': [
                r'(?:novčan[au]\s+kazn[ua]|troškova\s+krivičnog\s+postupka)\s+(?:u\s+)?iznos(?:u)?\s+od\s+([\d,.]+)\s*(?:eur[ao]?|€)',
                r'paušala?\s+iznos(?:u)?\s+od\s+([\d,.]+)\s*(?:eur[ao]?|€)',
            ],
            # Verdict type - expanded
            'vrsta_presude': [
                r'(K\s*R\s*I\s*V\s*(?:\s*J\s*E|A\s+JE))',
                r'(K\s+r\s+i\s+v\s+(?:\s*j\s*e|a\s+je))',
                r'(O\s*S\s*U\s*[ĐDGJ]\s*U\s*J\s*E)',
                r'(OSLOBAĐA)',
                r'(ODBIJA\s+SE\s+OPTUŽBA)',
                r'(K\s+r\s+i\s+v\s+i\s+s\s+u)',  # Krivi su
            ],
        }
        
        # Serbian month names to numbers
        self.serbian_months = {
            'januar': '01', 'februar': '02', 'mart': '03', 'april': '04',
            'maj': '05', 'jun': '06', 'jul': '07', 'avgust': '08',
            'septembar': '09', 'oktobar': '10', 'novembar': '11', 'decembar': '12',
            'januara': '01', 'februara': '02', 'marta': '03', 'aprila': '04',
            'maja': '05', 'juna': '06', 'jula': '07', 'avgusta': '08',
            'septembra': '09', 'oktobra': '10', 'novembra': '11', 'decembra': '12'
        }

    def extract_field(self, text, field_name):
        """Extract a field from text using multiple patterns."""
        patterns = self.verdict_patterns.get(field_name, [])
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                groups = match.groups()
                # Return tuple only if more than one non-None group
                non_none_groups = [g for g in groups if g is not None]
                if len(groups) > 1 and len(non_none_groups) > 1:
                    return groups
                elif len(groups) >= 1 and groups[0]:
                    return groups[0]
        return None

    def normalize_date(self, date_str):
        """Normalize date to YYYY-MM-DD format."""
        if not date_str:
            return None
        
        # Clean up the date string
        date_str = date_str.strip()
        
        # Try different date formats
        # Format: DD.MM.YYYY
        match = re.match(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})', date_str)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Format: DD. Month YYYY
        for month_name, month_num in self.serbian_months.items():
            if month_name in date_str.lower():
                match = re.match(r'(\d{1,2})\.\s*' + month_name + r'\s*(\d{4})', date_str.lower())
                if match:
                    day, year = match.groups()
                    return f"{year}-{month_num}-{day.zfill(2)}"
        
        return date_str

    def extract_judge_comprehensive(self, text):
        """
        Comprehensive judge extraction - tries multiple methods.
        Returns the judge name or None.
        """
        # Helper function to validate judge name
        def is_valid_judge_name(name):
            if not name or len(name) < 5:
                return False
            # Should not contain institutional words
            invalid_words = ['suda', 'sud', 'vijeća', 'vijeće', 'osnovnog', 'višeg', 'vrhovnog', 
                           'apelacionog', 'crne', 'gore', 'zapisničar', 'zapisničarka', 'tužilac',
                           'tužioca', 'advokat', 'branilac', 'branioca', 'porotnik', 'ana-marij',
                           'zapisnicar', 'okrivljen']
            name_lower = name.lower()
            for word in invalid_words:
                if word in name_lower:
                    return False
            # Should have at least 2 parts (name and surname)
            parts = name.split()
            if len(parts) < 2:
                return False
            # First and last parts should be capitalized and have reasonable length
            if len(parts[0]) < 2 or len(parts[-1]) < 2:
                return False
            # Should not be a partial phrase (like "pojedincu Dubravki" or "pojedinc Dubravka")
            invalid_first_words = ['pojedincu', 'pojedinac', 'pojedinc', 'vijeća', 'vijece', 'suda', 'leković', 'lekovic']
            if parts[0].lower() in invalid_first_words:
                return False
            return True
        
        # Helper function to normalize dative names to nominative
        def normalize_name(name):
            """Convert dative case names to nominative (e.g., 'Branislavu' -> 'Branislav')"""
            parts = name.split()
            normalized_parts = []
            for part in parts:
                # Common dative endings and their nominative forms
                if part.endswith('u') and len(part) > 3:
                    # Could be dative -u ending (Branislavu -> Branislav)
                    normalized_parts.append(part[:-1])
                elif part.endswith('i') and len(part) > 3:
                    # Could be dative -i ending (Momirki -> Momirka)
                    normalized_parts.append(part[:-1] + 'a')
                else:
                    normalized_parts.append(part)
            return ' '.join(normalized_parts)
        
        # Method 1: Look at the BEGINNING of the document for "sudija Name Surname" pattern
        # This is the most reliable as it's in the opening header
        first_section = text[:3000]  # First 3000 characters - the main verdict header
        
        # First try to find patterns with nominative case names
        nominative_patterns = [
            # "i to sudija Name Surname" - most reliable
            r'i\s+to\s+sudija\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            # "krivični, i to sudija Name"
            r'krivični[,\s]+(?:i\s+)?(?:to\s+)?sudija\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            # "sudija pojedinac Name" followed by comma
            r'sudija\s+pojedinac[,\s]+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)\s*,',
            # "sutkinja Name Surname" (female judge)
            r'sutkinja\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            # "Sudija Osnovnog suda u City Name Surname"
            r'[Ss]udija\s+(?:Osnovnog|Višeg|Apelacionog)\s+suda\s+u\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            r'[Ss]utkinja\s+(?:Osnovnog|Višeg|Apelacionog)\s+suda\s+u\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
        ]
        
        for pattern in nominative_patterns:
            match = re.search(pattern, first_section, re.IGNORECASE)
            if match:
                judge_name = match.group(1).strip()
                if is_valid_judge_name(judge_name):
                    return judge_name
        
        # Patterns for judge in header that might be in dative case
        dative_patterns = [
            # "po sudiji Name Surname" (name in dative)
            r'po\s+sudiji\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            # "sudija pojedinac Name" without comma
            r'sudija\s+pojedinac[,\s]+(?:sa\s+)?([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            # "predsjednika vijeća Name Surname"
            r'predsjednika\s+vijeća[,\s]+(?:sudije?\s+)?([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            # "pojedincu Name" pattern
            r'pojedincu\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
        ]
        
        for pattern in dative_patterns:
            match = re.search(pattern, first_section, re.IGNORECASE)
            if match:
                judge_name = match.group(1).strip()
                # Normalize dative case to nominative
                judge_name = normalize_name(judge_name)
                if is_valid_judge_name(judge_name):
                    return judge_name
        
        # Method 2: Look at the end of document for signature sections
        # But only if header didn't work
        end_section = text[-3000:]  # Last 3000 characters
        
        # Look for "SUTKINJA:" or "SUDIJA:" patterns with name on same or next line
        signature_patterns = [
            # "SUTKINJA:\nName Surname" or "SUDIJA:\nName Surname"
            r'SUTKINJA\s*:\s*\n*\s*([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            r'SUDIJA\s*:\s*\n*\s*([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
            # With possible s.r. suffix
            r'SUTKINJA\s*:\s*\n*\s*([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)\s*,?\s*s\.?\s*r\.?',
            r'SUDIJA\s*:\s*\n*\s*([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)\s*,?\s*s\.?\s*r\.?',
            # S u d i j a (spaced) pattern
            r'S\s*u\s*d\s*i\s*j\s*a\s*[,:]?\s*\n+\s*([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
        ]
        for pattern in signature_patterns:
            match = re.search(pattern, end_section, re.MULTILINE | re.IGNORECASE)
            if match:
                judge_name = match.group(1).strip()
                if is_valid_judge_name(judge_name):
                    return judge_name
        
        # Method 3: Standard patterns from verdict_patterns (anywhere in text)
        judge = self.extract_field(text, 'sudija')
        if judge and is_valid_judge_name(judge):
            return judge.strip()
        
        # Method 4: Look for simple "sudija Name" pattern in first section
        # but exclude lines that contain "zapisničar"
        simple_matches = re.findall(r'[Ss]udija\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)', first_section)
        for judge_name in simple_matches:
            judge_name = judge_name.strip()
            if is_valid_judge_name(judge_name):
                return judge_name
        
        return None

    def extract_case_description_comprehensive(self, text):
        """
        Comprehensive case description extraction.
        Tries multiple methods to find the case description.
        EVERY verdict has a description - keep trying until we find it!
        """
        # Clean up the text for better matching
        text_clean = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Method 1: "Što je:" or "Što je :" section - most common format
        patterns_sto_je = [
            r'[ŠŠšS]to\s+je\s*:\s*\n*(.*?)(?:\n\s*-\s*[čČ]ime|\n\s*[čČ]ime\s+je)',
            r'[ŠŠšS]to\s+je\s*:\s*(.*?)(?:-\s*[čČ]ime|[čČ]ime\s+je)',
            r'[ŠŠšS]to\s+su\s*:\s*\n*(.*?)(?:\n\s*-\s*[čČ]ime|\n\s*[čČ]ime)',
        ]
        for pattern in patterns_sto_je:
            match = re.search(pattern, text_clean, re.DOTALL | re.IGNORECASE)
            if match:
                desc = match.group(1).strip()
                desc = re.sub(r'\s+', ' ', desc)
                if len(desc) > 30:
                    return desc[:1500]
        
        # Method 2: After "K R I V je" or "KRIV JE" or "Kriv je" section
        patterns_kriv = [
            r'K\s*R\s*I\s*V\s*(?:\s*J\s*E|A\s+JE)\s*[:\n]*(.*?)(?:-\s*[čČ]ime|[čČ]ime\s+je\s+izvršio)',
            r'K\s*r\s*i\s*v\s*(?:\s*j\s*e|a\s+je)\s*[:\n]*(.*?)(?:-\s*[čČ]ime|[čČ]ime\s+je)',
            r'K\s+r\s+i\s+v\s+a\s+j\s+e\s*[:\n]*(.*?)(?:-\s*[čČ]ime|[čČ]ime)',
            r'K\s+r\s+i\s+v\s+i\s+s\s+u\s*[:\n]*(.*?)(?:-\s*[čČ]ime|[čČ]ime)',
            r'KRIVA?\s+JE\s*[:\n]*(.*?)(?:-\s*[čČ]ime|[čČ]ime\s+je)',
        ]
        for pattern in patterns_kriv:
            match = re.search(pattern, text_clean, re.DOTALL | re.IGNORECASE)
            if match:
                desc = match.group(1).strip()
                # Remove any prefix like "Zato što je" or "Što je"
                desc = re.sub(r'^(?:Zato\s+)?[ŠšS]to\s+j[ea][:,]?\s*', '', desc, flags=re.IGNORECASE)
                desc = re.sub(r'\s+', ' ', desc)
                if len(desc) > 30:
                    return desc[:1500]
        
        # Method 3: Look for crime description starting with date pattern "Dana DD.MM.YYYY"
        date_patterns = [
            r'(Dana\s+\d{1,2}\.\s*\d{1,2}\.\s*\d{4}[^-]{50,}?)(?:-\s*[čČ]ime|[čČ]ime\s+je)',
            r'(Dana\s+\d{1,2}\.\s*\d{1,2}\.\s*\d{4}[^\n]{50,})',
            r'([Dd]ana\s+\d{1,2}\.\d{1,2}\.\d{4}\s*(?:godine?)?,?\s+[^\n-]{30,})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text_clean, re.DOTALL | re.IGNORECASE)
            if match:
                desc = match.group(1).strip()
                desc = re.sub(r'\s+', ' ', desc)
                if len(desc) > 30:
                    return desc[:1500]
        
        # Method 4: Look for "U periodu od" - common for ongoing crimes
        period_pattern = r'(U\s+periodu\s+od\s+[^-]{50,}?)(?:-\s*[čČ]ime|[čČ]ime\s+je)'
        match = re.search(period_pattern, text_clean, re.DOTALL | re.IGNORECASE)
        if match:
            desc = match.group(1).strip()
            desc = re.sub(r'\s+', ' ', desc)
            if len(desc) > 30:
                return desc[:1500]
        
        # Method 5: Look for content between verdict declaration and "čime je izvršio"
        verdict_section = r'(?:P\s*R\s*E\s*S\s*U\s*D\s*[AU]|PRESUDU)\s*\n+(.*?)(?:-\s*[čČ]ime|[čČ]ime\s+je\s+izvršio)'
        match = re.search(verdict_section, text_clean, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1)
            # Extract after KRIV JE or Što je
            kriv_match = re.search(r'(?:K\s*R\s*I\s*V|[ŠšS]to\s+je)\s*[:\n]*(.*)', content, re.DOTALL | re.IGNORECASE)
            if kriv_match:
                desc = kriv_match.group(1).strip()
                desc = re.sub(r'\s+', ' ', desc)
                if len(desc) > 30:
                    return desc[:1500]
        
        # Method 6: Search for paragraph after defendant info that starts with date/location
        defendant_to_crime = r'neosuđivan[a]?\s*[.:\n]+(.*?)(?:-\s*[čČ]ime|[čČ]ime\s+je)'
        match = re.search(defendant_to_crime, text_clean, re.DOTALL | re.IGNORECASE)
        if match:
            desc = match.group(1).strip()
            # Remove any prefix like "K R I V je" 
            desc = re.sub(r'^K\s*R?\s*I?\s*V?\s*[aA]?\s*J?\s*E?\s*[:\n]*\s*', '', desc)
            desc = re.sub(r'^[ŠšS]to\s+je\s*:\s*', '', desc)
            desc = re.sub(r'\s+', ' ', desc)
            if len(desc) > 30:
                return desc[:1500]
        
        # Method 7: Last resort - find any substantial text after "PRESUDA" and before "čime"
        last_resort = r'PRESUD[AU]\s*\n+.*?(?:K\s*R\s*I\s*V|osuđivan).*?\n+(.*?)(?:[čČ]ime|O\s*S\s*U\s*[ĐDÐ]\s*U\s*J\s*E)'
        match = re.search(last_resort, text_clean, re.DOTALL | re.IGNORECASE)
        if match:
            desc = match.group(1).strip()
            desc = re.sub(r'\s+', ' ', desc)
            if len(desc) > 30:
                return desc[:1500]
        
        return None

    def extract_crime_type(self, text, filename=""):
        """
        Determine the crime type from text and filename.
        Returns proper Serbian crime type name.
        """
        # First check filename for clues
        if 'kreditn' in filename.lower() or 'kartic' in filename.lower():
            return 'falsifikovanje i zloupotreba kreditnih kartica'
        if 'novca' in filename.lower() or 'novac' in filename.lower():
            return 'falsifikovanje novca'
        
        # Check for article numbers - definitive
        if re.search(r'čl\.?\s*260', text, re.IGNORECASE):
            return 'falsifikovanje i zloupotreba kreditnih kartica'
        if re.search(r'čl\.?\s*258', text, re.IGNORECASE):
            return 'falsifikovanje novca'
        
        # Check text content for crime type keywords
        text_lower = text.lower()
        
        if 'kreditnih kartica' in text_lower or 'bezgotovinsko plaćanje' in text_lower:
            return 'falsifikovanje i zloupotreba kreditnih kartica'
        if 'falsifikovanje novca' in text_lower or 'lažan novac' in text_lower or 'lažne novčanice' in text_lower:
            return 'falsifikovanje novca'
        
        # Check extracted field
        extracted = self.extract_field(text, 'tip_krivicnog_djela')
        if extracted:
            extracted_lower = extracted.lower()
            if 'kreditn' in extracted_lower or 'kartic' in extracted_lower:
                return 'falsifikovanje i zloupotreba kreditnih kartica'
            if 'novca' in extracted_lower or 'novac' in extracted_lower:
                return 'falsifikovanje novca'
            return extracted
        
        return 'Nepoznat'  # Return "Unknown" in Serbian

    def extract_witnesses(self, text):
        """Extract witness names from text."""
        witnesses = []
        patterns = [
            r'svjedok[a]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][\.\s]?)',
            r'saslušao\s+svjedoke?\s+([^,]+)',
            r'svjedoka\s+(?:oštećenog\s+)?([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ]\.?)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            witnesses.extend(matches)
        return list(set(witnesses))[:5]  # Return up to 5 unique witnesses

    def extract_evidence(self, text):
        """Extract evidence items from text."""
        evidence = []
        patterns = [
            r'izvršio\s+uvid\s+u\s+([^,;]+)',
            r'pročitao\s+([^,;]+)',
            r'saslušao\s+([^,;]+)',
            r'(izvještaj\s+o\s+[^,;]+)',
            r'(zapisnik\s+o\s+[^,;]+)',
            r'(potvrda\s+o\s+[^,;]+)',
            r'(foto\s*dokumentacij[ua]\s+[^,;]+)',
            r'(video\s+zapis[^,;]+)',
            r'(nalaz\s+i\s+mišljenje\s+vještaka[^,;]+)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                cleaned = m.strip()
                if len(cleaned) > 10 and cleaned not in evidence:
                    evidence.append(cleaned)
        return evidence[:10]  # Return up to 10 evidence items

    def extract_amount(self, text):
        """Extract monetary amounts from the verdict."""
        amounts = []
        patterns = [
            r'(\d+[,.]?\d*)\s*(?:eur[ao]?|€)',
            r'iznos(?:u)?\s+(?:od\s+)?(\d+[,.]?\d*)\s*(?:eur[ao]?|€)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            amounts.extend(matches)
        return list(set(amounts))

    def extract_all_data(self, text, filename=""):
        """Extract all available data from verdict text."""
        data = {
            'naziv_fajla': filename,
            'sud': None,
            'broj_predmeta': None,
            'datum': None,
            'datum_normalizovan': None,
            'godina': None,
            'sudija': None,
            'optuzeni': None,
            'podaci_o_roditeljima': None,
            'godina_rodjenja': None,
            'prebivaliste': None,
            'zaposlenost': None,
            'bracni_status': None,
            'obrazovanje': None,
            'ranije_osudjivan': None,
            'tip_krivicnog_djela': None,
            'clan_kz': None,
            'kazna': None,
            'uslovna_osuda': False,
            'novcana_kazna': None,
            'vrsta_presude': None,
            'svjedoci': [],
            'dokazi': [],
            'iznosi': [],
            'opis_slucaja': None,
        }
        
        # Extract basic fields
        data['sud'] = self.extract_field(text, 'sud') or 'Nepoznat'
        data['broj_predmeta'] = self.extract_field(text, 'broj_predmeta') or 'Nepoznat'
        
        # Extract and normalize date
        raw_date = self.extract_field(text, 'datum')
        if raw_date:
            data['datum'] = raw_date
            data['datum_normalizovan'] = self.normalize_date(raw_date)
            if data['datum_normalizovan']:
                data['godina'] = data['datum_normalizovan'][:4]
        else:
            data['datum'] = 'Nepoznat'
        
        # Extract judge using comprehensive method
        data['sudija'] = self.extract_judge_comprehensive(text) or 'Nepoznat'
        
        # Extract defendant info
        data['optuzeni'] = self.extract_field(text, 'optuzeni') or 'Nepoznat'
        
        # Extract parent info
        parents = self.extract_field(text, 'podaci_o_roditeljima')
        if parents and isinstance(parents, tuple):
            data['podaci_o_roditeljima'] = f"otac {parents[0]}, majka {parents[1]}"
        
        # Extract other personal info
        data['godina_rodjenja'] = self.extract_field(text, 'godina_rodjenja')
        data['prebivaliste'] = self.extract_field(text, 'prebivaliste')
        data['zaposlenost'] = self.extract_field(text, 'zaposlenost')
        data['bracni_status'] = self.extract_field(text, 'bracni_status')
        data['obrazovanje'] = self.extract_field(text, 'obrazovanje')
        data['ranije_osudjivan'] = self.extract_field(text, 'ranije_osudjivan') or 'Nepoznat'
        
        # Extract crime type using comprehensive method
        data['tip_krivicnog_djela'] = self.extract_crime_type(text, filename)
        
        # Extract articles
        articles = self.extract_field(text, 'clan_kz')
        if articles:
            if isinstance(articles, tuple):
                art_num = articles[0] if articles[0] else ''
                st_num = articles[1] if len(articles) > 1 and articles[1] else ''
                data['clan_kz'] = f"čl. {art_num}" + (f" st. {st_num}" if st_num else "")
            else:
                data['clan_kz'] = f"čl. {articles}"
        
        # Extract sentence
        data['kazna'] = self.extract_field(text, 'kazna') or 'Nepoznat'
        
        # Check for conditional sentence
        uslovna = self.extract_field(text, 'uslovna_osuda')
        data['uslovna_osuda'] = uslovna is not None
        
        # Extract fine
        data['novcana_kazna'] = self.extract_field(text, 'novcana_kazna')
        
        # Extract verdict type
        vrsta = self.extract_field(text, 'vrsta_presude')
        if vrsta:
            vrsta_clean = re.sub(r'\s+', '', vrsta.upper())
            if 'KRIVJE' in vrsta_clean or 'KRIVAJE' in vrsta_clean or 'KRIVISU' in vrsta_clean:
                data['vrsta_presude'] = 'Kriv'
            elif 'OSUDJUJE' in vrsta_clean or 'OSUDUJE' in vrsta_clean:
                data['vrsta_presude'] = 'Osuđuje'
            elif 'OSLOBAÐA' in vrsta_clean or 'OSLOBADA' in vrsta_clean:
                data['vrsta_presude'] = 'Oslobađa'
            elif 'ODBIJA' in vrsta_clean:
                data['vrsta_presude'] = 'Odbija se optužba'
            else:
                data['vrsta_presude'] = 'Kriv'  # Default if found but not matched
        else:
            data['vrsta_presude'] = 'Nepoznat'
        
        # Extract witnesses
        data['svjedoci'] = self.extract_witnesses(text)
        
        # Extract evidence
        data['dokazi'] = self.extract_evidence(text)
        
        # Extract amounts
        data['iznosi'] = self.extract_amount(text)
        
        # Extract case description using comprehensive method
        data['opis_slucaja'] = self.extract_case_description_comprehensive(text) or 'Opis nije dostupan'
        
        return data


class AkomaNtosoGenerator:
    """Generates Akoma Ntoso 3.0 XML files with Serbian field names."""
    
    NAMESPACES = {
        'akn': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_case_id(self, data):
        """Generate a unique case ID from extracted data."""
        broj = data.get('broj_predmeta', '')
        if broj and broj != 'Nepoznat':
            # Clean up the case number
            broj_clean = re.sub(r'[/\s]', '_', broj)
            return f"Case_K_{broj_clean}"
        return f"Case_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def create_xml(self, data):
        """Create Akoma Ntoso XML from extracted data."""
        case_id = self.generate_case_id(data)
        
        # Create root element
        root = ET.Element('akomaNtoso', {
            'xmlns': self.NAMESPACES['akn'],
            'xmlns:xsi': self.NAMESPACES['xsi']
        })
        
        # Create judgment element
        judgment = ET.SubElement(root, 'judgment', {'name': case_id})
        
        # Meta section
        meta = ET.SubElement(judgment, 'meta')
        
        # Identification
        identification = ET.SubElement(meta, 'identification', {'source': '#court'})
        
        # FRBRWork
        frbrwork = ET.SubElement(identification, 'FRBRWork')
        ET.SubElement(frbrwork, 'FRBRthis', {'value': f'/akn/me/judgment/{case_id}'})
        ET.SubElement(frbrwork, 'FRBRuri', {'value': f'/akn/me/judgment/{case_id}'})
        
        date_val = data.get('datum_normalizovan') or datetime.now().strftime('%Y-%m-%d')
        sud_val = data.get('sud') or 'Nepoznat'
        ET.SubElement(frbrwork, 'FRBRdate', {'date': date_val, 'name': 'judgment'})
        ET.SubElement(frbrwork, 'FRBRauthor', {'href': f'#{sud_val.lower().replace(" ", "_")}'})
        ET.SubElement(frbrwork, 'FRBRcountry', {'value': 'me'})
        
        # FRBRExpression
        frbrexp = ET.SubElement(identification, 'FRBRExpression')
        ET.SubElement(frbrexp, 'FRBRthis', {'value': f'/akn/me/judgment/{case_id}/srp@{date_val}'})
        ET.SubElement(frbrexp, 'FRBRuri', {'value': f'/akn/me/judgment/{case_id}/srp@{date_val}'})
        ET.SubElement(frbrexp, 'FRBRdate', {'date': date_val, 'name': 'judgment'})
        ET.SubElement(frbrexp, 'FRBRauthor', {'href': '#court'})
        ET.SubElement(frbrexp, 'FRBRlanguage', {'language': 'srp'})
        
        # FRBRManifestation
        frbrmani = ET.SubElement(identification, 'FRBRManifestation')
        ET.SubElement(frbrmani, 'FRBRthis', {'value': f'/akn/me/judgment/{case_id}/srp@{date_val}.xml'})
        ET.SubElement(frbrmani, 'FRBRuri', {'value': f'/akn/me/judgment/{case_id}/srp@{date_val}.xml'})
        ET.SubElement(frbrmani, 'FRBRdate', {'date': datetime.now().strftime('%Y-%m-%d'), 'name': 'generation'})
        ET.SubElement(frbrmani, 'FRBRauthor', {'href': '#system'})
        
        # References
        references = ET.SubElement(meta, 'references', {'source': '#court'})
        
        # Court reference
        sud_val = data.get('sud') or 'Nepoznat'
        ET.SubElement(references, 'TLCOrganization', {
            'eId': 'court',
            'href': f'/ontology/organization/me/{sud_val.lower().replace(" ", "_")}',
            'showAs': f'Osnovni Sud u {sud_val}'
        })
        
        # Judge reference
        sudija_val = data.get('sudija')
        if sudija_val and sudija_val != 'Nepoznat':
            ET.SubElement(references, 'TLCPerson', {
                'eId': 'sudija',
                'href': f'/ontology/person/{sudija_val.lower().replace(" ", "_")}',
                'showAs': sudija_val
            })
        
        # Defendant reference
        optuzeni_val = data.get('optuzeni')
        if optuzeni_val and optuzeni_val != 'Nepoznat':
            ET.SubElement(references, 'TLCPerson', {
                'eId': 'optuzeni',
                'href': f'/ontology/person/defendant',
                'showAs': optuzeni_val
            })
        
        # Proprietary metadata (Serbian field names)
        proprietary = ET.SubElement(meta, 'proprietary', {'source': '#court'})
        
        # Add all Serbian fields - use 'Nepoznat' instead of None/empty
        fields_to_add = [
            ('sud', data.get('sud') or 'Nepoznat'),
            ('brojPredmeta', data.get('broj_predmeta') or 'Nepoznat'),
            ('datum', data.get('datum') or 'Nepoznat'),
            ('datumNormalizovan', data.get('datum_normalizovan') or ''),
            ('godina', data.get('godina') or 'Nepoznat'),
            ('sudija', data.get('sudija') or 'Nepoznat'),
            ('optuzeni', data.get('optuzeni') or 'Nepoznat'),
            ('podaciORoditeljima', data.get('podaci_o_roditeljima') or ''),
            ('godinaRodjenja', data.get('godina_rodjenja') or ''),
            ('prebivaliste', data.get('prebivaliste') or ''),
            ('zaposlenost', data.get('zaposlenost') or ''),
            ('bracniStatus', data.get('bracni_status') or ''),
            ('obrazovanje', data.get('obrazovanje') or ''),
            ('ranijeOsudjivan', data.get('ranije_osudjivan') or 'Nepoznat'),
            ('tipKrivicnogDjela', data.get('tip_krivicnog_djela') or 'Nepoznat'),
            ('clanKZ', data.get('clan_kz') or ''),
            ('kazna', data.get('kazna') or 'Nepoznat'),
            ('uslovnaOsuda', 'Da' if data.get('uslovna_osuda') else 'Ne'),
            ('novcanaKazna', data.get('novcana_kazna') or ''),
            ('vrstaPresude', data.get('vrsta_presude') or 'Nepoznat'),
            ('opisSlucaja', data.get('opis_slucaja') or 'Opis nije dostupan'),
        ]
        
        for field_name, value in fields_to_add:
            if value:  # Only add non-empty values
                elem = ET.SubElement(proprietary, field_name)
                elem.text = str(value)
        
        # Add witnesses as list
        if data.get('svjedoci'):
            svjedoci_elem = ET.SubElement(proprietary, 'svjedoci')
            for svjedok in data['svjedoci']:
                s = ET.SubElement(svjedoci_elem, 'svjedok')
                s.text = svjedok
        
        # Add evidence as list
        if data.get('dokazi'):
            dokazi_elem = ET.SubElement(proprietary, 'dokazi')
            for dokaz in data['dokazi']:
                d = ET.SubElement(dokazi_elem, 'dokaz')
                d.text = dokaz
        
        # Add amounts
        if data.get('iznosi'):
            iznosi_elem = ET.SubElement(proprietary, 'iznosi')
            for iznos in data['iznosi']:
                i = ET.SubElement(iznosi_elem, 'iznos')
                i.text = f"{iznos} EUR"
        
        # Judgment body
        judgment_body = ET.SubElement(judgment, 'judgmentBody')
        
        # Introduction
        intro = ET.SubElement(judgment_body, 'introduction')
        intro_p = ET.SubElement(intro, 'p')
        intro_text = f"U IME CRNE GORE\n\n"
        if data.get('sud') and data.get('sud') != 'Nepoznat':
            intro_text += f"Osnovni Sud u {data['sud']}"
        if data.get('broj_predmeta') and data.get('broj_predmeta') != 'Nepoznat':
            intro_text += f", {data['broj_predmeta']}"
        if data.get('sudija') and data.get('sudija') != 'Nepoznat':
            intro_text += f", sudija {data['sudija']}"
        intro_p.text = intro_text
        
        # Background - defendant info
        background = ET.SubElement(judgment_body, 'background')
        bg_block = ET.SubElement(background, 'block', {'name': 'podaciOOptuzenom'})
        bg_p = ET.SubElement(bg_block, 'p')
        
        defendant_info = f"Optuženi: {data.get('optuzeni', 'Nepoznat')}"
        if data.get('podaci_o_roditeljima'):
            defendant_info += f", {data['podaci_o_roditeljima']}"
        if data.get('prebivaliste'):
            defendant_info += f", prebivalište: {data['prebivaliste']}"
        if data.get('zaposlenost'):
            defendant_info += f", {data['zaposlenost']}"
        if data.get('bracni_status'):
            defendant_info += f", {data['bracni_status']}"
        if data.get('ranije_osudjivan') and data.get('ranije_osudjivan') != 'Nepoznat':
            defendant_info += f", {data['ranije_osudjivan']}"
        bg_p.text = defendant_info
        
        # Arguments section - case description
        if data.get('opis_slucaja') and data.get('opis_slucaja') != 'Opis nije dostupan':
            arguments = ET.SubElement(judgment_body, 'arguments')
            arg_block = ET.SubElement(arguments, 'block', {'name': 'opisSlucaja'})
            arg_p = ET.SubElement(arg_block, 'p')
            arg_p.text = data['opis_slucaja']
        
        # Motivation - evidence
        if data.get('dokazi'):
            motivation = ET.SubElement(judgment_body, 'motivation')
            mot_block = ET.SubElement(motivation, 'block', {'name': 'dokazi'})
            mot_tblock = ET.SubElement(mot_block, 'tblock')
            for dokaz in data['dokazi'][:5]:  # Limit to 5 for XML
                dok_p = ET.SubElement(mot_tblock, 'p')
                dok_p.text = f"• {dokaz}"
        
        # Decision
        decision = ET.SubElement(judgment_body, 'decision')
        dec_block = ET.SubElement(decision, 'block', {'name': 'odluka'})
        
        # Verdict type
        if data.get('vrsta_presude') and data.get('vrsta_presude') != 'Nepoznat':
            verdict_p = ET.SubElement(dec_block, 'p')
            verdict_p.text = data['vrsta_presude'].upper()
        
        # Sentence
        if data.get('kazna') and data.get('kazna') != 'Nepoznat':
            sentence_p = ET.SubElement(dec_block, 'p')
            sentence_text = f"Kazna: {data['kazna']}"
            if data.get('uslovna_osuda'):
                sentence_text += " (uslovna osuda)"
            sentence_p.text = sentence_text
        
        # Fine
        if data.get('novcana_kazna'):
            fine_p = ET.SubElement(dec_block, 'p')
            fine_p.text = f"Novčana kazna: {data['novcana_kazna']} EUR"
        
        # Conclusions
        conclusions = ET.SubElement(judgment, 'conclusions')
        conc_block = ET.SubElement(conclusions, 'block', {'name': 'pravniOsnov'})
        conc_p = ET.SubElement(conc_block, 'p')
        
        crime_type = data.get('tip_krivicnog_djela', 'Nepoznat')
        legal_basis = f"Krivično djelo: {crime_type}"
        if data.get('clan_kz'):
            legal_basis += f" ({data['clan_kz']} Krivičnog zakonika Crne Gore)"
        conc_p.text = legal_basis
        
        return root, case_id
    
    def prettify(self, elem):
        """Return a pretty-printed XML string."""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding=None)
    
    def save_xml(self, root, case_id):
        """Save XML to file."""
        xml_string = self.prettify(root)
        
        # Remove extra blank lines
        xml_lines = [line for line in xml_string.split('\n') if line.strip()]
        xml_string = '\n'.join(xml_lines)
        
        filepath = self.output_dir / f"{case_id}.xml"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        return filepath


def split_cases_from_text(text):
    """
    Split a text file containing multiple cases into individual case texts.
    Each case starts with "U IME CRNE GORE".
    """
    # Split by "U IME CRNE GORE" pattern
    # We use a regex that captures different variations
    pattern = r'(?=\n*U\s+IME\s+CRNE\s+GORE\b)'
    
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    
    # Filter out empty parts and parts that are just whitespace
    cases = []
    for part in parts:
        part = part.strip()
        if part and len(part) > 500:  # A valid case should have substantial content
            # Make sure it contains "PRESUD" to confirm it's a verdict
            if 'PRESUD' in part.upper() or 'P R E S U D' in part.upper():
                cases.append(part)
    
    return cases


def process_verdict_files(input_dirs, output_dir):
    """Process all verdict files and generate Akoma Ntoso XML."""
    extractor = EnhancedVerdictExtractor()
    generator = AkomaNtosoGenerator(output_dir)
    
    results = []
    processed_case_numbers = set()  # Track to avoid duplicates
    
    for input_dir in input_dirs:
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"Direktorijum ne postoji: {input_dir}")
            continue
        
        # Only process numbered txt files (1.txt, 2.txt, etc.)
        # Skip link collection files
        for txt_file in sorted(input_path.glob('*.txt')):
            # Skip link collection files
            if 'linkovi' in txt_file.name.lower() or txt_file.name.startswith('K '):
                print(f"Preskačem (link fajl): {txt_file.name}")
                continue
            
            print(f"\nObrađujem fajl: {txt_file.name}")
            
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Split into individual cases
                cases = split_cases_from_text(text)
                print(f"  Pronađeno {len(cases)} presuda u fajlu")
                
                for case_idx, case_text in enumerate(cases, 1):
                    try:
                        # Extract data for this case
                        data = extractor.extract_all_data(case_text, txt_file.name)
                        
                        # Check for duplicate case numbers
                        case_num = data.get('broj_predmeta', '')
                        if case_num and case_num != 'Nepoznat':
                            if case_num in processed_case_numbers:
                                print(f"    [{case_idx}] Preskačem duplikat: {case_num}")
                                continue
                            processed_case_numbers.add(case_num)
                        
                        # Generate XML
                        root, case_id = generator.create_xml(data)
                        filepath = generator.save_xml(root, case_id)
                        
                        results.append({
                            'izvorni_fajl': str(txt_file),
                            'presuda_broj': case_idx,
                            'xml_fajl': str(filepath),
                            'broj_predmeta': data.get('broj_predmeta'),
                            'sud': data.get('sud'),
                            'sudija': data.get('sudija'),
                            'tip_krivicnog_djela': data.get('tip_krivicnog_djela'),
                            'kazna': data.get('kazna'),
                            'opis_slucaja': data.get('opis_slucaja', '')[:100] + '...' if data.get('opis_slucaja') else 'Nema',
                            'status': 'uspješno'
                        })
                        
                        print(f"    [{case_idx}] ✓ {filepath.name}")
                        print(f"        Broj: {data.get('broj_predmeta')}, Sudija: {data.get('sudija')}")
                        
                    except Exception as e:
                        print(f"    [{case_idx}] ✗ Greška: {e}")
                        results.append({
                            'izvorni_fajl': str(txt_file),
                            'presuda_broj': case_idx,
                            'status': 'greška',
                            'poruka': str(e)
                        })
                
            except Exception as e:
                print(f"  ✗ Greška pri čitanju fajla: {e}")
                results.append({
                    'izvorni_fajl': str(txt_file),
                    'status': 'greška',
                    'poruka': str(e)
                })
    
    return results


def main():
    """Main entry point."""
    # Define input directories
    base_dir = Path(__file__).parent
    input_dirs = [
        base_dir / 'archive' / 'presude' / 'falsifikovanje novca',
        base_dir / 'archive' / 'presude' / 'falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje',
    ]
    
    # Output directory
    output_dir = base_dir / 'data' / 'cases' / 'akomantoso'
    
    print("=" * 60)
    print("POBOLJŠANI EKSTRAKTOR PRESUDA - VERZIJA 2.0")
    print("Akoma Ntoso 3.0 Generator sa srpskim poljima")
    print("=" * 60)
    print()
    
    # Process files
    results = process_verdict_files(input_dirs, output_dir)
    
    # Summary
    print()
    print("=" * 60)
    print("REZIME")
    print("=" * 60)
    
    successful = [r for r in results if r.get('status') == 'uspješno']
    failed = [r for r in results if r.get('status') == 'greška']
    
    print(f"Ukupno obrađeno: {len(results)}")
    print(f"Uspješno: {len(successful)}")
    print(f"Greške: {len(failed)}")
    
    # Print extracted judges
    print("\n--- EKSTRAKTOVANI SUDIJE ---")
    for r in successful:
        print(f"  {r.get('broj_predmeta', 'N/A')}: {r.get('sudija', 'N/A')}")
    
    # Print extracted types
    print("\n--- TIPOVI KRIVIČNIH DJELA ---")
    for r in successful:
        print(f"  {r.get('broj_predmeta', 'N/A')}: {r.get('tip_krivicnog_djela', 'N/A')}")
    
    # Save results to JSON
    results_file = output_dir / 'extraction_results.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nRezultati sačuvani u: {results_file}")


if __name__ == '__main__':
    main()
