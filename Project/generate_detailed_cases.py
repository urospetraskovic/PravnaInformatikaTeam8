#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Akoma Ntoso XML generator with full case details.
Extracts detailed information from court judgment txt files.
"""

import os
import re
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

OUTPUT_DIR = r"data\cases\akomantoso_new"

def prettify_xml(elem):
    """Return a pretty-printed XML string."""
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('utf-8')

def sanitize_id(text):
    """Convert text to valid ID."""
    text = text.replace('/', '_').replace(' ', '_').replace('.', '_')
    text = re.sub(r'[^A-Za-z0-9_]', '', text)
    return text

def extract_date(text):
    """Extract and parse date from text."""
    months = {
        'januar': '01', 'februar': '02', 'mart': '03', 'april': '04',
        'maj': '05', 'jun': '06', 'jul': '07', 'avgust': '08',
        'septembar': '09', 'oktobar': '10', 'novembar': '11', 'decembar': '12'
    }
    match = re.search(r'(\d{1,2})\.\s*(\w+)\s*(\d{4})', text, re.IGNORECASE)
    if match:
        day = match.group(1).zfill(2)
        month_name = match.group(2).lower()
        year = match.group(3)
        month = months.get(month_name, '01')
        return f"{year}-{month}-{day}", f"{day}.{month}.{year}."
    return None, None

def extract_case_details(content, crime_type, article):
    """Extract comprehensive case details from judgment text."""
    case = {}
    
    # Extract court
    court_match = re.search(r'(?:OSNOVNI|Osnovni)\s+[Ss]ud\s+u\s+([A-ZČĆŽŠĐa-zčćžšđ]+)', content)
    if court_match:
        case['court'] = f"Osnovni sud u {court_match.group(1).title()}"
        case['court_id'] = f"osnovni_sud_{court_match.group(1).lower()}"
    else:
        case['court'] = "Osnovni sud"
        case['court_id'] = "osnovni_sud"
    
    # Extract case number
    case_match = re.search(r'K\.?\s*(?:br\.?)?\s*(\d+/\d+)', content)
    if case_match:
        case['case_number'] = f"K {case_match.group(1)}"
        case['case_id'] = f"K_{case_match.group(1).replace('/', '_')}"
    else:
        return None
    
    # Extract date
    date_match = re.search(r'(\d{1,2}\.\s*\w+\s*\d{4})', content)
    if date_match:
        iso_date, display_date = extract_date(date_match.group(1))
        case['date_iso'] = iso_date or datetime.now().strftime('%Y-%m-%d')
        case['date_display'] = display_date or date_match.group(1)
    else:
        case['date_iso'] = datetime.now().strftime('%Y-%m-%d')
        case['date_display'] = "Nepoznato"
    
    # Extract judge
    judge_match = re.search(r'sudij[ae]\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)', content)
    if judge_match:
        case['judge'] = judge_match.group(1)
    else:
        case['judge'] = "Sudija"
    
    # Extract clerk (zapisničar)
    clerk_match = re.search(r'zapisničar[ae]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)', content, re.IGNORECASE)
    if clerk_match:
        case['clerk'] = clerk_match.group(1)
    else:
        case['clerk'] = "Zapisničar"
    
    # Extract defendant info - look for detailed pattern
    defendant_block = re.search(
        r'(?:Okrivljen[ia]?|Optužen[ia]?)[:\s]+([A-ZČĆŽŠĐ])\.\s*([A-ZČĆŽŠĐ])\.?,?\s*(?:JMBG[^\n]*)?[,\s]+od\s+oca\s+([A-ZČĆŽŠĐ][a-zčćžšđ\.]+)[,\s]+(?:i\s+)?majke\s+([A-ZČĆŽŠĐ][a-zčćžšđ\.]+)[,\s]+(?:rođen[ae]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ\.]+)[,\s]+)?(?:rođen[ae]?)?\s*(?:[\d\.]+\s*)?(?:godine)?\s*(?:u\s+([A-Za-zčćžšđČĆŽŠĐ\s]+?))?[,\s]+(?:sa\s+)?(?:prebivalištem|nastanjen|stalno\s+nastanjen)\s+u\s+([A-Za-zčćžšđČĆŽŠĐ\s]+)',
        content, re.IGNORECASE | re.DOTALL
    )
    
    if defendant_block:
        case['defendant_initials'] = f"{defendant_block.group(1)}. {defendant_block.group(2)}."
        case['defendant_father'] = defendant_block.group(3)
        case['defendant_mother'] = defendant_block.group(4)
        case['defendant_birthplace'] = defendant_block.group(6).strip() if defendant_block.group(6) else "Nepoznato"
        case['defendant_residence'] = defendant_block.group(7).strip().split(',')[0] if defendant_block.group(7) else "Nepoznato"
    else:
        # Simpler pattern
        simple_match = re.search(r'(?:okrivljen|optužen)[^\n]*?([A-ZČĆŽŠĐ])\.\s*([A-ZČĆŽŠĐ])\.?', content, re.IGNORECASE)
        if simple_match:
            case['defendant_initials'] = f"{simple_match.group(1)}. {simple_match.group(2)}."
        else:
            case['defendant_initials'] = "N. N."
        case['defendant_father'] = "Nepoznato"
        case['defendant_mother'] = "Nepoznato"
        case['defendant_birthplace'] = "Nepoznato"
        case['defendant_residence'] = "Nepoznato"
    
    # Extract occupation
    occupation_match = re.search(r'(?:po\s+zanimanju|zanimanje)[:\s]+([a-zčćžšđA-ZČĆŽŠĐ\s]+?)(?:,|\.|nezaposlen)', content, re.IGNORECASE)
    if occupation_match:
        case['occupation'] = occupation_match.group(1).strip()
    elif 'nezaposlen' in content.lower():
        case['occupation'] = "nezaposlen"
    else:
        case['occupation'] = "Nepoznato"
    
    # Extract marital status
    if 'oženjen' in content.lower() and 'neoženjen' not in content.lower():
        case['marital_status'] = "oženjen"
    elif 'neoženjen' in content.lower():
        case['marital_status'] = "neoženjen"
    elif 'udat' in content.lower() and 'neudat' not in content.lower():
        case['marital_status'] = "udata"
    elif 'neudat' in content.lower():
        case['marital_status'] = "neudata"
    elif 'razveden' in content.lower():
        case['marital_status'] = "razveden/a"
    else:
        case['marital_status'] = "Nepoznato"
    
    # Extract children info
    children_match = re.search(r'(?:otac|majka)\s+(\w+)\s+(?:djece|djeteta)', content, re.IGNORECASE)
    if children_match:
        case['children'] = children_match.group(1)
    else:
        case['children'] = "Nepoznato"
    
    # Extract prior convictions
    if 'ranije neosuđivan' in content.lower() or 'nije osuđivan' in content.lower():
        case['prior_convictions'] = "ranije neosuđivan"
    elif 'ranije osuđivan' in content.lower():
        conviction_match = re.search(r'ranije\s+osuđivan[^\n]*?(?:presudom[^\n]+)', content, re.IGNORECASE)
        if conviction_match:
            case['prior_convictions'] = "ranije osuđivan"
        else:
            case['prior_convictions'] = "ranije osuđivan"
    else:
        case['prior_convictions'] = "Nepoznato"
    
    # Extract crime description (the "Što je" or fact section)
    crime_desc_match = re.search(
        r'(?:Što\s+je|ŠTO\s+JE|Kriv\s+je)[:\s]*\n*(.*?)(?:\n\s*[-–—]\s*čime|čime\s+je|Pa\s+sud|pa\s+ga\s+sud)',
        content, re.IGNORECASE | re.DOTALL
    )
    if crime_desc_match:
        crime_desc = crime_desc_match.group(1).strip()
        crime_desc = re.sub(r'\s+', ' ', crime_desc)
        crime_desc = crime_desc[:1500]  # Limit length
        case['crime_description'] = crime_desc
    else:
        case['crime_description'] = ""
    
    # Generate case summary/description
    case['case_summary'] = generate_case_summary(case, content, crime_type, article)
    
    # Extract sentence
    sentence_match = re.search(
        r'(?:OSUĐUJE|osuđuje|O\s*S\s*U\s*Đ\s*U\s*J\s*E)[^\n]*(?:kazn[ua]\s+zatvora\s+u\s+trajanju\s+od\s+)?(\d+)\s*\(?(\w+)\)?(?:\s*(?:mjesec[ai]?|godin[ae]))?',
        content, re.IGNORECASE
    )
    if sentence_match:
        num = sentence_match.group(1)
        unit = sentence_match.group(2) if sentence_match.group(2) else ""
        if 'godin' in unit.lower() or int(num) > 12:
            case['sentence'] = f"{num} godina zatvora"
            case['sentence_duration'] = f"P{num}Y"
        else:
            case['sentence'] = f"{num} mjeseci zatvora"
            case['sentence_duration'] = f"P{num}M"
    elif 'uslovna osuda' in content.lower() or 'uslovn' in content.lower():
        cond_match = re.search(r'(\d+)\s*(?:\()?\w+(?:\))?\s*mjesec[ai]?\s*(?:zatvora)?\s*(?:uslovno|uslovn)', content, re.IGNORECASE)
        if cond_match:
            case['sentence'] = f"Uslovna osuda - {cond_match.group(1)} mjeseci"
            case['sentence_duration'] = f"P{cond_match.group(1)}M"
        else:
            case['sentence'] = "Uslovna osuda"
            case['sentence_duration'] = "conditional"
    else:
        case['sentence'] = "Prema zakonu"
        case['sentence_duration'] = "unspecified"
    
    # Extract verdict type
    if 'kriv je' in content.lower() or 'oglašava se krivim' in content.lower():
        case['verdict'] = "KRIV JE"
    elif 'oslobađa' in content.lower():
        case['verdict'] = "OSLOBAĐA SE"
    else:
        case['verdict'] = "KRIV JE"
    
    # Extract costs
    costs_match = re.search(r'troškova?\s+(?:krivičnog\s+)?postupka[^\d]*(\d+(?:[.,]\d+)?)\s*(?:eura?|€)', content, re.IGNORECASE)
    if costs_match:
        case['costs'] = f"{costs_match.group(1)} eura"
    else:
        case['costs'] = "Po odluci suda"
    
    # Extract paušal
    pausal_match = re.search(r'(?:sudski\s+)?paušal[^\d]*(\d+(?:[.,]\d+)?)\s*(?:eura?|€)', content, re.IGNORECASE)
    if pausal_match:
        case['pausal'] = f"{pausal_match.group(1)} eura"
    else:
        case['pausal'] = ""
    
    # Set crime type and article
    case['crime_type'] = crime_type
    case['article'] = article
    
    # Extract evidence types
    case['evidence'] = extract_evidence(content, article)
    
    # Extract mitigating circumstances
    case['mitigating'] = extract_mitigating(content)
    
    # Extract aggravating circumstances
    case['aggravating'] = extract_aggravating(content)
    
    return case

def generate_case_summary(case, content, crime_type, article):
    """Generate a comprehensive case summary paragraph."""
    parts = []
    
    # Start with defendant
    defendant = case.get('defendant_initials', 'Okrivljeni')
    court = case.get('court', 'sud').replace('Osnovni sud u ', '')
    
    parts.append(f"Okrivljeni {defendant} iz {case.get('defendant_residence', 'Crne Gore')}")
    
    # Add date if available
    if case.get('date_display') and case['date_display'] != "Nepoznato":
        parts.append(f"je dana {case['date_display']}")
    
    # Add crime description based on article type
    if article == '258':
        # Counterfeit money
        amount_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:eura?|€|EUR)', content, re.IGNORECASE)
        denomination_match = re.search(r'novčanic[aeu]\s+(?:u\s+apoenu\s+)?od\s+(\d+(?:[.,]\d+)?)\s*(?:eura?|€)', content, re.IGNORECASE)
        
        if 'stavi' in content.lower() and 'opticaj' in content.lower():
            parts.append("stavio u opticaj lažni novac")
            if denomination_match:
                parts.append(f"- novčanicu od {denomination_match.group(1)} eura")
        elif 'pribavi' in content.lower():
            parts.append("pribavio lažni novac u namjeri da ga stavi u opticaj kao pravi")
        else:
            parts.append("izvršio krivično djelo falsifikovanja novca")
            
        # Location context
        location_match = re.search(r'(?:u\s+)?(?:prodavnici|marketu|trafici|pumpi|banci|lokalu)\s+"?([^"]+)"?', content, re.IGNORECASE)
        if location_match:
            parts.append(f"u prodajnom objektu")
    
    elif article == '260':
        # Credit card fraud
        if 'oduzeo' in content.lower() or 'otuđio' in content.lower() or 'ukrao' in content.lower():
            parts.append("neovlašćeno pribavio tuđu platnu karticu")
        if 'upotrijebio' in content.lower() or 'korist' in content.lower():
            amount_match = re.search(r'(?:iznos(?:u)?|potrošio|podigao)[^\d]*(\d+(?:[.,]\d+)?)\s*(?:eura?|€)', content, re.IGNORECASE)
            if amount_match:
                parts.append(f"i istu upotrijebio za pribavljanje imovinske koristi u iznosu od {amount_match.group(1)} eura")
            else:
                parts.append("i istu upotrijebio za pribavljanje protivpravne imovinske koristi")
    
    # Add verification info
    if 'centralne banke' in content.lower() or 'tehničk' in content.lower():
        parts.append("Tehničkom analizom utvrđeno je da se radi o falsifikatu.")
    
    # Add confession/proof context
    if 'prizna' in content.lower():
        parts.append("Okrivljeni je priznao izvršenje krivičnog djela.")
    
    # Add prior conviction context
    if case.get('prior_convictions') == "ranije osuđivan":
        parts.append("Okrivljeni je ranije osuđivan.")
    elif case.get('prior_convictions') == "ranije neosuđivan":
        parts.append("Okrivljeni ranije nije osuđivan.")
    
    # Add sentence info
    if case.get('sentence'):
        parts.append(f"Sud ga je osudio na {case['sentence']}.")
    
    # Combine into summary
    summary = " ".join(parts)
    summary = re.sub(r'\s+', ' ', summary).strip()
    
    # Ensure it's not too long but comprehensive
    if len(summary) > 800:
        summary = summary[:800] + "..."
    
    return summary

def extract_evidence(content, article):
    """Extract mentioned evidence types."""
    evidence = []
    
    if 'izvješta' in content.lower() or 'izvještaj' in content.lower():
        if 'centralne banke' in content.lower():
            evidence.append("Izvještaj Centralne banke o tehničkoj analizi novčanica")
        if 'forenzičk' in content.lower():
            evidence.append("Izvještaj Forenzičkog centra")
    
    if 'svjedo' in content.lower():
        evidence.append("Iskazi svjedoka")
    
    if 'prizna' in content.lower():
        evidence.append("Priznanje okrivljenog")
    
    if 'potvrda' in content.lower():
        evidence.append("Potvrda o privremeno oduzetim predmetima")
    
    if 'video' in content.lower() or 'snima' in content.lower():
        evidence.append("Video snimci")
    
    if article == '260':
        if 'izvod' in content.lower() or 'transakcij' in content.lower():
            evidence.append("Izvodi sa bankovnih računa")
    
    if not evidence:
        evidence = ["Materijalni dokazi", "Iskazi svjedoka"]
    
    return evidence

def extract_mitigating(content):
    """Extract mitigating circumstances."""
    mitigating = []
    
    okolnosti_match = re.search(r'olakšavajuć[^\n]*okolnost[^\n]*:?\s*([^\n]+(?:\n[^\n]+)*?)(?:otežavajuć|od\s+otežavajućih|sud\s+je)', content, re.IGNORECASE)
    if okolnosti_match:
        text = okolnosti_match.group(1).lower()
        if 'priznan' in text:
            mitigating.append("Priznanje krivičnog djela")
        if 'porodičn' in text or 'otac' in text or 'majka' in text or 'djec' in text:
            mitigating.append("Porodične prilike")
        if 'materijaln' in text or 'imovinsk' in text:
            mitigating.append("Teške materijalne prilike")
        if 'neosuđivan' in text:
            mitigating.append("Ranija neosuđivanost")
        if 'korekt' in text or 'ponašan' in text:
            mitigating.append("Korektno ponašanje u toku postupka")
        if 'kajan' in text:
            mitigating.append("Kajanje")
    
    if not mitigating:
        if 'prizna' in content.lower():
            mitigating.append("Priznanje krivičnog djela")
        if 'neosuđivan' in content.lower():
            mitigating.append("Ranija neosuđivanost")
    
    return mitigating if mitigating else ["Nije utvrđeno"]

def extract_aggravating(content):
    """Extract aggravating circumstances."""
    aggravating = []
    
    okolnosti_match = re.search(r'otežavajuć[^\n]*okolnost[^\n]*:?\s*([^\n]+(?:\n[^\n]+)*?)(?:sud\s+je|imajući|pa\s+je)', content, re.IGNORECASE)
    if okolnosti_match:
        text = okolnosti_match.group(1).lower()
        if 'osuđivan' in text and 'neosuđivan' not in text:
            aggravating.append("Ranija osuđivanost")
        if 'način' in text or 'okolnost' in text:
            aggravating.append("Način izvršenja krivičnog djela")
    
    if not aggravating:
        if 'ranije osuđivan' in content.lower():
            aggravating.append("Ranija osuđivanost")
    
    return aggravating if aggravating else ["Nije utvrđeno"]

def create_full_xml(case):
    """Create comprehensive Akoma Ntoso XML structure."""
    case_id = case['case_id']
    defendant_id = sanitize_id(case['defendant_initials'])
    
    # Root element
    akomantoso = ET.Element('akomaNtoso')
    akomantoso.set('xmlns', 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0')
    
    # Judgment element
    judgment = ET.SubElement(akomantoso, 'judgment')
    judgment.set('name', f"Case {case['case_number']} - {case['defendant_initials']}")
    
    # === META SECTION ===
    meta = ET.SubElement(judgment, 'meta')
    
    # Identification
    identification = ET.SubElement(meta, 'identification')
    identification.set('source', '#court')
    
    # FRBRWork
    frbr_work = ET.SubElement(identification, 'FRBRWork')
    ET.SubElement(frbr_work, 'FRBRthis').set('value', f'/akn/me/judgment/{case_id}/!main')
    ET.SubElement(frbr_work, 'FRBRuri').set('value', f'/akn/me/judgment/{case_id}')
    frbr_date = ET.SubElement(frbr_work, 'FRBRdate')
    frbr_date.set('date', case['date_iso'])
    frbr_date.set('name', 'decision')
    ET.SubElement(frbr_work, 'FRBRauthor').set('href', f'#{case["court_id"]}')
    ET.SubElement(frbr_work, 'FRBRcountry').set('value', 'me')
    ET.SubElement(frbr_work, 'FRBRnumber').set('value', case['case_number'])
    ET.SubElement(frbr_work, 'FRBRname').set('value', case['crime_type'])
    
    # FRBRExpression
    frbr_expr = ET.SubElement(identification, 'FRBRExpression')
    ET.SubElement(frbr_expr, 'FRBRthis').set('value', f'/akn/me/judgment/{case_id}/sr@{case["date_iso"]}/!main')
    ET.SubElement(frbr_expr, 'FRBRuri').set('value', f'/akn/me/judgment/{case_id}/sr@{case["date_iso"]}')
    expr_date = ET.SubElement(frbr_expr, 'FRBRdate')
    expr_date.set('date', case['date_iso'])
    expr_date.set('name', 'expression')
    ET.SubElement(frbr_expr, 'FRBRauthor').set('href', f'#{case["court_id"]}')
    ET.SubElement(frbr_expr, 'FRBRlanguage').set('language', 'sr')
    
    # FRBRManifestation
    frbr_manif = ET.SubElement(identification, 'FRBRManifestation')
    ET.SubElement(frbr_manif, 'FRBRthis').set('value', f'/akn/me/judgment/{case_id}/sr@{case["date_iso"]}/!main.xml')
    ET.SubElement(frbr_manif, 'FRBRuri').set('value', f'/akn/me/judgment/{case_id}/sr@{case["date_iso"]}/!main.akn')
    manif_date = ET.SubElement(frbr_manif, 'FRBRdate')
    manif_date.set('date', datetime.now().strftime('%Y-%m-%d'))
    manif_date.set('name', 'transform')
    ET.SubElement(frbr_manif, 'FRBRformat').set('value', 'xml')
    
    # References
    references = ET.SubElement(meta, 'references')
    references.set('source', '#court')
    
    # Court organization
    court_org = ET.SubElement(references, 'TLCOrganization')
    court_org.set('eId', case['court_id'])
    court_org.set('href', f'/akn/me/ontology/organization/{case["court_id"]}')
    court_org.set('showAs', case['court'])
    
    # Judge
    judge_elem = ET.SubElement(references, 'TLCPerson')
    judge_elem.set('eId', 'sudija')
    judge_elem.set('href', f'/akn/me/ontology/person/sudija')
    judge_elem.set('showAs', case['judge'])
    
    # Clerk
    clerk_elem = ET.SubElement(references, 'TLCPerson')
    clerk_elem.set('eId', 'zapisnicar')
    clerk_elem.set('href', f'/akn/me/ontology/person/zapisnicar')
    clerk_elem.set('showAs', case['clerk'])
    
    # Defendant
    defendant_elem = ET.SubElement(references, 'TLCPerson')
    defendant_elem.set('eId', 'optuzeni')
    defendant_elem.set('href', f'/akn/me/ontology/person/defendant_{defendant_id}')
    defendant_elem.set('showAs', case['defendant_initials'])
    
    # Legal reference
    legal_ref = ET.SubElement(references, 'TLCReference')
    legal_ref.set('eId', f'ref_art_{case["article"]}')
    legal_ref.set('href', f'/akn/me/act/criminal-code#art_{case["article"]}')
    legal_ref.set('showAs', f'Član {case["article"]} - {case["crime_type"]}')
    
    # Classification
    classification = ET.SubElement(meta, 'classification')
    classification.set('source', '#court')
    
    crime_keyword = ET.SubElement(classification, 'keyword')
    crime_keyword.set('value', sanitize_id(case['crime_type'].lower()))
    crime_keyword.set('showAs', case['crime_type'])
    crime_keyword.set('dictionary', 'criminal_offenses')
    
    article_keyword = ET.SubElement(classification, 'keyword')
    article_keyword.set('value', f'clan_{case["article"]}')
    article_keyword.set('showAs', f'Član {case["article"]}')
    article_keyword.set('dictionary', 'articles')
    
    # === HEADER SECTION ===
    header = ET.SubElement(judgment, 'header')
    ET.SubElement(header, 'p').set('class', 'court')
    header[-1].text = case['court'].upper()
    ET.SubElement(header, 'p').set('class', 'caseNumber')
    header[-1].text = case['case_number']
    ET.SubElement(header, 'p').set('class', 'date')
    header[-1].text = f"{case['date_display']} godine"
    ET.SubElement(header, 'p').set('class', 'formula')
    header[-1].text = "U IME CRNE GORE"
    
    # === JUDGMENT BODY ===
    body = ET.SubElement(judgment, 'judgmentBody')
    
    # Introduction
    intro = ET.SubElement(body, 'introduction')
    intro_p = ET.SubElement(intro, 'p')
    intro_p.text = f"{case['court'].upper()}, sudija {case['judge']}, kao sudija pojedinac uz zapisničara {case['clerk']}, u krivičnom predmetu protiv optuženog {case['defendant_initials']} zbog krivičnog djela {case['crime_type'].lower()} iz čl.{case['article']} Krivičnog zakonika."
    
    # Background
    background = ET.SubElement(body, 'background')
    
    # Court info
    p_court = ET.SubElement(background, 'p')
    b_court = ET.SubElement(p_court, 'b')
    b_court.text = "Sud:"
    b_court.tail = f" {case['court']}"
    
    p_number = ET.SubElement(background, 'p')
    b_number = ET.SubElement(p_number, 'b')
    b_number.text = "Broj predmeta:"
    b_number.tail = f" {case['case_number']}"
    
    p_date = ET.SubElement(background, 'p')
    b_date = ET.SubElement(p_date, 'b')
    b_date.text = "Datum presude:"
    b_date.tail = f" {case['date_display']}"
    
    p_judge = ET.SubElement(background, 'p')
    b_judge = ET.SubElement(p_judge, 'b')
    b_judge.text = "Sudija:"
    b_judge.tail = f" {case['judge']}"
    
    p_clerk = ET.SubElement(background, 'p')
    b_clerk = ET.SubElement(p_clerk, 'b')
    b_clerk.text = "Zapisničar:"
    b_clerk.tail = f" {case['clerk']}"
    
    # Defendant info block
    def_block = ET.SubElement(background, 'blockContainer')
    def_block.set('eId', 'defendant_info')
    def_heading = ET.SubElement(def_block, 'heading')
    def_heading.text = "Podaci o okrivljenom"
    
    def_fields = [
        ("Okrivljeni:", case['defendant_initials']),
        ("Mjesto rođenja:", case['defendant_birthplace']),
        ("Prebivalište:", case['defendant_residence']),
        ("Zanimanje:", case['occupation']),
        ("Porodično stanje:", case['marital_status']),
        ("Djeca:", case['children']),
        ("Ranija osuđivanost:", case['prior_convictions'])
    ]
    
    for label, value in def_fields:
        p = ET.SubElement(def_block, 'p')
        b = ET.SubElement(p, 'b')
        b.text = label
        b.tail = f" {value}"
    
    # Case Description (KEY ELEMENT!)
    case_desc = ET.SubElement(body, 'caseDescription')
    case_desc_heading = ET.SubElement(case_desc, 'heading')
    case_desc_heading.text = "Opis slučaja"
    case_desc_p = ET.SubElement(case_desc, 'p')
    case_desc_p.text = case['case_summary']
    
    # Motivation
    motivation = ET.SubElement(body, 'motivation')
    
    # Crime description block
    crime_block = ET.SubElement(motivation, 'blockContainer')
    crime_block.set('eId', 'crime_description')
    crime_heading = ET.SubElement(crime_block, 'heading')
    crime_heading.text = "Opis krivičnog djela"
    crime_p = ET.SubElement(crime_block, 'p')
    crime_p.text = case.get('crime_description', case['case_summary'])[:800]
    
    # Legal qualification
    legal_block = ET.SubElement(motivation, 'blockContainer')
    legal_block.set('eId', 'legal_qualification')
    legal_heading = ET.SubElement(legal_block, 'heading')
    legal_heading.text = "Pravna kvalifikacija"
    legal_p = ET.SubElement(legal_block, 'p')
    legal_p.text = f"Čime je izvršio krivično djelo - {case['crime_type'].lower()} iz čl.{case['article']} Krivičnog zakonika Crne Gore."
    
    # Evidence block
    evidence_block = ET.SubElement(motivation, 'blockContainer')
    evidence_block.set('eId', 'evidence')
    evidence_heading = ET.SubElement(evidence_block, 'heading')
    evidence_heading.text = "Dokazi"
    for ev in case['evidence']:
        ev_p = ET.SubElement(evidence_block, 'p')
        ev_p.text = ev
    
    # Mitigating circumstances
    mitig_block = ET.SubElement(motivation, 'blockContainer')
    mitig_block.set('eId', 'mitigating_circumstances')
    mitig_heading = ET.SubElement(mitig_block, 'heading')
    mitig_heading.text = "Olakšavajuće okolnosti"
    mitig_p = ET.SubElement(mitig_block, 'p')
    mitig_p.text = ", ".join(case['mitigating']) + "."
    
    # Aggravating circumstances
    aggrav_block = ET.SubElement(motivation, 'blockContainer')
    aggrav_block.set('eId', 'aggravating_circumstances')
    aggrav_heading = ET.SubElement(aggrav_block, 'heading')
    aggrav_heading.text = "Otežavajuće okolnosti"
    aggrav_p = ET.SubElement(aggrav_block, 'p')
    aggrav_p.text = ", ".join(case['aggravating']) + "."
    
    # Decision
    decision = ET.SubElement(body, 'decision')
    
    # Verdict block
    verdict_block = ET.SubElement(decision, 'blockContainer')
    verdict_block.set('eId', 'verdict')
    verdict_heading = ET.SubElement(verdict_block, 'heading')
    verdict_heading.text = "PRESUDA"
    
    verdict_p1 = ET.SubElement(verdict_block, 'p')
    b_verdict = ET.SubElement(verdict_p1, 'b')
    b_verdict.text = "Odluka:"
    b_verdict.tail = f" {case['verdict']}"
    
    verdict_p2 = ET.SubElement(verdict_block, 'p')
    verdict_p2.text = f"OSUĐUJE SE na {case['sentence']}."
    
    # Costs block
    costs_block = ET.SubElement(decision, 'blockContainer')
    costs_block.set('eId', 'costs')
    costs_heading = ET.SubElement(costs_block, 'heading')
    costs_heading.text = "Troškovi postupka"
    costs_p = ET.SubElement(costs_block, 'p')
    costs_text = f"Optuženi {case['defendant_initials']} je dužan da plati troškove krivičnog postupka u iznosu od {case['costs']}"
    if case['pausal']:
        costs_text += f" i sudski paušal u iznosu od {case['pausal']}"
    costs_text += " u roku od 15 dana od dana pravosnažnosti."
    costs_p.text = costs_text
    
    # Conclusions
    conclusions = ET.SubElement(judgment, 'conclusions')
    conc_p1 = ET.SubElement(conclusions, 'p')
    conc_p1.text = case['court'].upper()
    conc_p2 = ET.SubElement(conclusions, 'p')
    conc_p2.text = f"Dana {case['date_display']} godine"
    
    signature = ET.SubElement(conclusions, 'signature')
    clerk_sig = ET.SubElement(signature, 'person')
    clerk_sig.set('refersTo', '#zapisnicar')
    clerk_sig.text = f"Zapisničar: {case['clerk']}"
    judge_sig = ET.SubElement(signature, 'person')
    judge_sig.set('refersTo', '#sudija')
    judge_sig.text = f"SUDIJA: {case['judge']}"
    
    legal_advice = ET.SubElement(conclusions, 'p')
    b_advice = ET.SubElement(legal_advice, 'b')
    b_advice.text = "PRAVNA POUKA:"
    b_advice.tail = " Protiv ove presude može se izjaviti žalba Višem sudu u roku od 15 dana od dana prijema pismenog otpravka. Žalba se predaje ovom sudu u dva primjerka."
    
    return akomantoso, f"Case_{case_id}_{defendant_id}"

def process_file(filepath, crime_type, article):
    """Process a single text file and extract all cases."""
    results = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            with open(filepath, 'r', encoding='cp1252') as f:
                content = f.read()
        except:
            return results
    
    # Split by court headers
    case_blocks = re.split(r'\n(?=Osnovni Sud u [A-Za-zčćžšđČĆŽŠĐ]+\n)', content)
    
    for block in case_blocks:
        if not block.strip() or len(block) < 500:
            continue
        
        case = extract_case_details(block, crime_type, article)
        if case:
            results.append(case)
    
    return results

def main():
    """Main function to generate all XML files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    generated = []
    
    # Process falsifikovanje novca (Article 258)
    novac_dir = r"archive\presude\falsifikovanje novca"
    if os.path.exists(novac_dir):
        for filename in os.listdir(novac_dir):
            if filename.endswith('.txt') and filename[0].isdigit():
                filepath = os.path.join(novac_dir, filename)
                print(f"Processing {filepath}...")
                cases = process_file(filepath, "Falsifikovanje novca", "258")
                
                for case in cases:
                    try:
                        xml_elem, file_id = create_full_xml(case)
                        xml_str = prettify_xml(xml_elem)
                        
                        output_path = os.path.join(OUTPUT_DIR, f"{file_id}.xml")
                        counter = 1
                        while os.path.exists(output_path):
                            output_path = os.path.join(OUTPUT_DIR, f"{file_id}_{counter}.xml")
                            counter += 1
                        
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(xml_str)
                        generated.append(output_path)
                        print(f"  Generated: {os.path.basename(output_path)}")
                    except Exception as e:
                        print(f"  Error: {e}")
    
    # Process kreditne kartice (Article 260)
    kartice_dir = r"archive\presude\falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje"
    if os.path.exists(kartice_dir):
        for filename in os.listdir(kartice_dir):
            if filename.endswith('.txt') and filename[0].isdigit():
                filepath = os.path.join(kartice_dir, filename)
                print(f"Processing {filepath}...")
                cases = process_file(filepath, "Falsifikovanje i zloupotreba kreditnih kartica", "260")
                
                for case in cases:
                    try:
                        xml_elem, file_id = create_full_xml(case)
                        xml_str = prettify_xml(xml_elem)
                        
                        output_path = os.path.join(OUTPUT_DIR, f"{file_id}.xml")
                        counter = 1
                        while os.path.exists(output_path):
                            output_path = os.path.join(OUTPUT_DIR, f"{file_id}_{counter}.xml")
                            counter += 1
                        
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(xml_str)
                        generated.append(output_path)
                        print(f"  Generated: {os.path.basename(output_path)}")
                    except Exception as e:
                        print(f"  Error: {e}")
    
    print(f"\n✅ Generated {len(generated)} XML files with full details!")
    return generated

if __name__ == "__main__":
    main()
