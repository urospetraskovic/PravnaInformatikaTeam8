#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audit all Akoma Ntoso XML files for missing data and report what needs to be filled
from the corresponding TXT files in archive/presude/.
"""

import os
import re
import glob
import sys

# Force UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XML_DIR = os.path.join(PROJECT_ROOT, 'data', 'cases', 'akomantoso')
TXT_DIRS = [
    os.path.join(PROJECT_ROOT, 'archive', 'presude', 'falsifikovanje novca'),
    os.path.join(PROJECT_ROOT, 'archive', 'presude', 'falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje'),
]

def xml_filename_to_case_id(xml_name):
    """K 100_2010.xml -> (100, 2010)"""
    m = re.match(r'K\s+(\d+)_(\d+)\.xml', xml_name)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None

def find_txt_file(case_num, year):
    """Find corresponding TXT file for a case number/year."""
    # TXT files are named like "K 1002010.txt" (no underscore, no space between num and year)
    patterns = [
        f"K {case_num}{year}.txt",
        f"K{case_num}{year}.txt",
    ]
    # Also try 2-digit year
    year2 = str(year)[-2:]
    patterns.append(f"K {case_num}{year2}.txt")
    patterns.append(f"K{case_num}{year2}.txt")
    
    for txt_dir in TXT_DIRS:
        if not os.path.exists(txt_dir):
            continue
        for pattern in patterns:
            path = os.path.join(txt_dir, pattern)
            if os.path.exists(path):
                return path
    return None

def extract_xml_field(content, tag):
    """Extract text from an XML tag."""
    m = re.search(rf'<{tag}>([^<]*)</{tag}>', content)
    if m:
        return m.group(1).strip()
    return ''

def has_xml_tag(content, tag):
    """Check if XML has a specific tag."""
    return bool(re.search(rf'<{tag}>', content))

def extract_from_txt(txt_path):
    """Extract all relevant fields from a TXT court judgment file."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except:
        try:
            with open(txt_path, 'r', encoding='cp1252') as f:
                text = f.read()
        except:
            return {}
    
    result = {}
    
    # === JUDGE (sudija) ===
    judge_patterns = [
        r'(?:po\s+)?sudij[ei]\s+(?:pojedincu\s+)?([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
        r'sudij[ea],?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
        r'pojedinac\s+sudij[ea]\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
        r'predsjednik[a]?\s+vijeća\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
        r'sudij[ei]\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
    ]
    for pat in judge_patterns:
        m = re.search(pat, text)
        if m:
            name = m.group(1).strip()
            if not any(w in name.lower() for w in ['suda', 'sud', 'vijeć', 'osnov', 'crne', 'gore']):
                result['judge'] = name
                break
    
    # === COURT CLERK (zapisničar) ===
    m = re.search(r'zapisničar[aue]?\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)', text, re.IGNORECASE)
    if m:
        result['court_clerk'] = m.group(1).strip()
    
    # === PRIOR CONVICTIONS (ranijeOsudjivan) ===
    # Check in defendant description area
    defendant_block = ''
    dm = re.search(r'(?:O[pk]tužen[aio]|Okrivljen[aio])\s*:?\s*\n?(.{50,1500}?)(?:K\s*R\s*I\s*V|OSLOBADJA|OSLOBAĐA|O\s*S\s*U\s*[ĐD]\s*U\s*J\s*E|Zato što|Što je)', text, re.DOTALL | re.IGNORECASE)
    if dm:
        defendant_block = dm.group(1)
    
    check_text = defendant_block or text
    if re.search(r'neosudj?ivan[a]?|neosuđivan[a]?|ranije\s+neosudj?ivan|ranije\s+neosuđivan', check_text, re.IGNORECASE):
        result['prior_convictions'] = 'Ne'
    elif re.search(r'(?:ranije\s+)?osudj?ivan[a]?|(?:ranije\s+)?osuđivan[a]?', check_text, re.IGNORECASE):
        result['prior_convictions'] = 'Da'
    
    # === SENTENCE / PENALTY (kazna) ===
    # Look for "kazna zatvora u trajanju od X mjeseci/godina"
    sentence_patterns = [
        r'kazn[aue]\s+zatvora\s+u\s+trajanju\s+od\s+(\d+)\s*\(([^)]+)\)\s*(mjesec[ia]?|mesec[ia]?|godin[ae]?|dan[a]?)',
        r'kazn[aue]\s+zatvora\s+u\s+trajanju\s+od\s+(\d+)\s*(mjesec[ia]?|mesec[ia]?|godin[ae]?|dan[a]?)',
        r'kazn[aue]\s+rada\s+u\s+javnom\s+interesu\s+u\s+trajanju\s+od\s+(\d+)\s*\(([^)]+)\)\s*(časov[a]?|sat[ia]?)',
    ]
    for pat in sentence_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            groups = m.groups()
            num = groups[0]
            if len(groups) == 3 and '(' in pat:
                word_num = groups[1]
                unit = groups[2]
            elif len(groups) == 2:
                unit = groups[1]
                word_num = None
            else:
                unit = groups[-1]
                word_num = None
            
            if word_num:
                result['kazna'] = f"{num} ({word_num}) {unit}"
            else:
                result['kazna'] = f"{num} {unit}"
            break
    
    # Also check for monetary fine (novčana kazna)
    m = re.search(r'nov[čc]an[aou]\s+kazn[aou]\s+(?:u\s+iznosu\s+od\s+)?(\d+[,.]?\d*)\s*(?:eura?|EUR|€)', text, re.IGNORECASE)
    if m:
        result['novcana_kazna'] = m.group(1)
    
    # === USLOVNA OSUDA ===
    if re.search(r'USLOVN[UAO]\s+OSUD[UAO]|USLOVN[UAO]\s+PRESUD[UAO]|uslovn[aou]\s+osud[aou]|uslovn[aou]\s+presud[aou]', text, re.IGNORECASE):
        result['uslovna'] = 'Da'
    else:
        result['uslovna'] = 'Ne'
    
    # === VERDICT TYPE ===
    if re.search(r'OSLOBADJA\s+SE\s+OD\s+OPTUŽBE|OSLOBAĐA\s+SE\s+OD\s+OPTUŽBE|OSLOBAĐA\s+SE', text, re.IGNORECASE):
        result['verdict_type'] = 'Oslobađajuća'
    elif re.search(r'KRIV\s+JE|K\s*R\s*I\s*V\s*A?\s+JE', text):
        result['verdict_type'] = 'Osuđujuća'
    elif re.search(r'OGLAŠAVA\s+SE\s+KRIVIM|OSUĐUJE\s+SE|O\s*S\s*U\s*[ĐD]\s*U\s*J\s*E', text, re.IGNORECASE):
        result['verdict_type'] = 'Osuđujuća'
    
    # If uslovna + osuđujuća = "Uslovna presuda"
    if result.get('uslovna') == 'Da' and result.get('verdict_type') == 'Osuđujuća':
        result['verdict_type'] = 'Uslovna presuda'
    
    # === CASE DESCRIPTION (opisSlucaja) ===
    # Look for the main accusation paragraph — usually after "Što je:" or "Da je,"
    desc_patterns = [
        r'(?:Što\s+je\s*:?\s*\n)(.*?)(?:\n\s*-\s*čime|\n\s*Čime)',
        r'(?:Da\s+je\s*,?\s*\n)(.*?)(?:\n\s*-\s*čime|\n\s*Čime)',
        r'(?:Kriv\s+je\s*\n\s*Što\s+je\s*:?\s*\n)(.*?)(?:\n\s*-\s*čime|\n\s*Čime)',
    ]
    for pat in desc_patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            desc = m.group(1).strip()
            desc = re.sub(r'\s+', ' ', desc)
            if len(desc) > 30:
                result['opis_slucaja'] = desc
                break
    
    # === EVIDENCE (dokazi) ===    
    # Look for evidence in "Obrazloženje" section
    evidence_section = ''
    em = re.search(r'O\s*b\s*r\s*a\s*z\s*l\s*o\s*ž\s*e\s*n\s*j\s*e(.*?)$', text, re.DOTALL | re.IGNORECASE)
    if em:
        evidence_section = em.group(1)
    
    evidence_items = []
    evidence_patterns = [
        r'(izvod[a]?\s+iz\s+kaznene\s+evidencije[^,\.]*)',
        r'(potvrdu?\s+o\s+privremeno\s+oduzetim\s+predmetima[^,\.]*)',
        r'(izvještaj[a]?\s+(?:kriminalističke\s+)?(?:tehnike|tehničke)[^,\.]*)',
        r'(nalaz[a]?\s+i\s+mišljenj[ae]\s+vještaka[^,\.]*)',
        r'(listing[a]?\s+komunikacija[^,\.]*)',
        r'(zapisnik[a]?\s+o\s+(?:uviđaju|prepoznavanju|pretresanju|saslušanju)[^,\.]*)',
        r'(potvrdu?\s+(?:CKB|banke|NLB|Erste|Komercijalne)[^,\.]*)',
        r'(iskaz[a]?\s+(?:svjedoka|svedoka|okrivljenoga?|optuženo?ga?)[^,\.]*)',
        r'(video\s*(?:snimak|zapis|nadzor)[^,\.]*)',
    ]
    check_txt = evidence_section if evidence_section else text
    for pat in evidence_patterns:
        for m2 in re.finditer(pat, check_txt, re.IGNORECASE):
            ev = m2.group(1).strip()
            if ev and len(ev) > 5 and ev not in evidence_items:
                evidence_items.append(ev)
    if evidence_items:
        result['dokazi'] = evidence_items
    
    # === MARITAL STATUS (bracniStatus) ===
    if re.search(r'\bneoženjen\b|\bneudata\b', text, re.IGNORECASE):
        result['bracni_status'] = 'neoženjen/neudata'
    elif re.search(r'\boženjen\b|\budata\b', text, re.IGNORECASE):
        result['bracni_status'] = 'oženjen/udata'
    elif re.search(r'\brazveden\b|\brazvedena\b', text, re.IGNORECASE):
        result['bracni_status'] = 'razveden/razvedena'
    
    # === RESIDENCE (prebivaliste) ===
    m = re.search(r'(?:nastanjen[aog]*|sa\s+prebivalištem)\s+u\s+([A-ZČĆŽŠĐa-zčćžšđ]+)', text, re.IGNORECASE)
    if m:
        result['prebivaliste'] = m.group(1).strip()
    
    return result

def audit_xml_files():
    """Audit all XML files and report missing fields."""
    xml_files = sorted(glob.glob(os.path.join(XML_DIR, 'K *.xml')))
    
    fields_to_check = [
        ('kazna', 'kazna'),
        ('sudija', 'sudija'),
        ('zapisnicar', 'zapisnicar'),
        ('ranijeOsudjivan', 'ranijeOsudjivan'),
        ('opisSlucaja', 'opisSlucaja'),
        ('vrstaPresude', 'vrstaPresude'),
    ]
    
    missing_report = {}
    
    for xml_path in xml_files:
        xml_name = os.path.basename(xml_path)
        case_num, year = xml_filename_to_case_id(xml_name)
        if case_num is None:
            continue
        
        try:
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            continue
        
        missing = []
        
        # Check each field
        kazna = extract_xml_field(content, 'kazna')
        if not kazna or kazna in ('Nepoznat', 'N/A', 'None', ''):
            missing.append('kazna')
        
        sudija = extract_xml_field(content, 'sudija')
        if not sudija or sudija in ('Nepoznat', 'N/A', 'None', ''):
            missing.append('sudija')
        
        zapisnicar = extract_xml_field(content, 'zapisnicar')
        if not zapisnicar or zapisnicar in ('Nepoznat', 'N/A', 'None', ''):
            missing.append('zapisnicar')
        
        ranije = extract_xml_field(content, 'ranijeOsudjivan')
        if not ranije or ranije in ('Nepoznat', 'N/A', 'None', ''):
            missing.append('ranijeOsudjivan')
        
        opis = extract_xml_field(content, 'opisSlucaja')
        if not opis or len(opis) < 20:
            missing.append('opisSlucaja')
        
        # Check for dokazi
        if not re.search(r'<dokaz>', content):
            missing.append('dokazi')
        
        vrsta = extract_xml_field(content, 'vrstaPresude')
        if not vrsta or vrsta in ('Nepoznat', 'N/A', 'None', ''):
            missing.append('vrstaPresude')
        
        if missing:
            txt_path = find_txt_file(case_num, year)
            txt_data = {}
            if txt_path:
                txt_data = extract_from_txt(txt_path)
            
            missing_report[xml_name] = {
                'xml_path': xml_path,
                'txt_path': txt_path,
                'missing': missing,
                'txt_data': txt_data,
                'case_num': case_num,
                'year': year,
            }
    
    return missing_report

def print_report(report):
    """Print a summary of missing data."""
    if not report:
        print("All XML files have complete data!")
        return
    
    print(f"\n=== AUDIT REPORT: {len(report)} XML files with missing data ===\n")
    
    # Count by field
    field_counts = {}
    for xml_name, info in report.items():
        for field in info['missing']:
            field_counts[field] = field_counts.get(field, 0) + 1
    
    print("Missing field counts:")
    for field, count in sorted(field_counts.items(), key=lambda x: -x[1]):
        print(f"  {field}: {count} files")
    print()
    
    # Count how many can be filled from TXT
    fillable = 0
    field_fillable = {}
    for xml_name, info in report.items():
        txt = info['txt_data']
        for field in info['missing']:
            if field == 'kazna' and txt.get('kazna'):
                fillable += 1
                field_fillable['kazna'] = field_fillable.get('kazna', 0) + 1
            elif field == 'sudija' and txt.get('judge'):
                fillable += 1
                field_fillable['sudija'] = field_fillable.get('sudija', 0) + 1
            elif field == 'zapisnicar' and txt.get('court_clerk'):
                fillable += 1
                field_fillable['zapisnicar'] = field_fillable.get('zapisnicar', 0) + 1
            elif field == 'ranijeOsudjivan' and txt.get('prior_convictions'):
                fillable += 1
                field_fillable['ranijeOsudjivan'] = field_fillable.get('ranijeOsudjivan', 0) + 1
            elif field == 'opisSlucaja' and txt.get('opis_slucaja'):
                fillable += 1
                field_fillable['opisSlucaja'] = field_fillable.get('opisSlucaja', 0) + 1
            elif field == 'dokazi' and txt.get('dokazi'):
                fillable += 1
                field_fillable['dokazi'] = field_fillable.get('dokazi', 0) + 1
            elif field == 'vrstaPresude' and txt.get('verdict_type'):
                fillable += 1
                field_fillable['vrstaPresude'] = field_fillable.get('vrstaPresude', 0) + 1
    
    print(f"Fillable from TXT files: {fillable} total field gaps")
    for field, count in sorted(field_fillable.items(), key=lambda x: -x[1]):
        print(f"  {field}: {count} fillable")
    print()
    
    # Detail for each file
    for xml_name, info in sorted(report.items()):
        txt_status = "TXT found" if info['txt_path'] else "NO TXT FILE"
        print(f"{xml_name} [{txt_status}]")
        print(f"  Missing: {', '.join(info['missing'])}")
        txt = info['txt_data']
        if txt:
            for field in info['missing']:
                if field == 'kazna' and txt.get('kazna'):
                    print(f"  -> kazna from TXT: {txt['kazna']}")
                elif field == 'sudija' and txt.get('judge'):
                    print(f"  -> sudija from TXT: {txt['judge']}")
                elif field == 'zapisnicar' and txt.get('court_clerk'):
                    print(f"  -> zapisnicar from TXT: {txt['court_clerk']}")
                elif field == 'ranijeOsudjivan' and txt.get('prior_convictions'):
                    print(f"  -> ranijeOsudjivan from TXT: {txt['prior_convictions']}")
                elif field == 'opisSlucaja' and txt.get('opis_slucaja'):
                    print(f"  -> opisSlucaja from TXT: {txt['opis_slucaja'][:100]}...")
                elif field == 'dokazi' and txt.get('dokazi'):
                    print(f"  -> dokazi from TXT: {len(txt['dokazi'])} items")
                elif field == 'vrstaPresude' and txt.get('verdict_type'):
                    print(f"  -> vrstaPresude from TXT: {txt['verdict_type']}")
        print()


if __name__ == '__main__':
    report = audit_xml_files()
    print_report(report)
