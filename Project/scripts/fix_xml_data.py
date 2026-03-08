#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix all Akoma Ntoso XML files by filling in missing data from TXT source files.
Also fixes terminology: "Uslovna osuda" → "Uslovna presuda" in <vrstaPresude> tags.
"""

import os
import re
import glob
import sys
import html

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XML_DIR = os.path.join(PROJECT_ROOT, 'data', 'cases', 'akomantoso')
TXT_DIRS = [
    os.path.join(PROJECT_ROOT, 'archive', 'presude', 'falsifikovanje novca'),
    os.path.join(PROJECT_ROOT, 'archive', 'presude', 'falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje'),
]

def xml_escape(text):
    """Escape text for safe XML inclusion."""
    if not text:
        return text
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    return text

def find_txt_file(case_num, year):
    """Find corresponding TXT file for a case number/year."""
    patterns = [
        f"K {case_num}{year}.txt",
        f"K{case_num}{year}.txt",
    ]
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

def read_txt(txt_path):
    """Read TXT file with encoding fallback."""
    for enc in ['utf-8', 'cp1252', 'latin-1']:
        try:
            with open(txt_path, 'r', encoding=enc) as f:
                return f.read()
        except:
            continue
    return ''

def extract_judge(text):
    """Extract judge name from TXT."""
    patterns = [
        r'(?:po\s+)?sudij[ei]\s+(?:pojedincu\s+)?(?:mr\.?\s+)?([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)+)',
        r'[Pp]redsjednik[a]?\s+(?:suda|vijeća)\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)+)',
        r'sudij[ea],?\s+(?:mr\.?\s+)?([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)+)',
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            name = m.group(1).strip()
            if not any(w in name.lower() for w in ['suda', 'sud', 'vijeć', 'osnov', 'crne', 'gore', 'novom', 'podgoric']):
                return name
    return None

def extract_clerk(text):
    """Extract court clerk (zapisničar) from TXT using multiple patterns."""
    patterns = [
        # "sa zapisničarom Natašom Lalović" or "sa zapisničarem Prezime Ime"
        r'sa\s+zapisničar(?:om|em)\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:[- ][A-ZČĆŽŠĐ][a-zčćžšđ]+)+)',
        # "uz učešće zapisničara Ime Prezime" (word 'zapisničara' BEFORE name)
        r'učeš[ćc]e\s+zapisničar[aeiuok]*\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:[- ][A-ZČĆŽŠĐ][a-zčćžšđ]+)+)',
        # "uz učešće namještenika suda Prezime Ime, kao zapisničara"
        r'(?:namještenika?\s+suda|sudskog\s+namještenika?)\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:[- ][A-ZČĆŽŠĐ][a-zčćžšđ]+)+)\s*,?\s*kao\s+zapisničar',
        # "uz učešće samostalne referentkinje / referenta / saradnice Prezime Ime, kao zapisničara"
        r'(?:samostaln[eog]+\s+)?(?:referentkinj[ea]|saradni[ck][ea]|referenta?)\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:[- ][A-ZČĆŽŠĐ][a-zčćžšđ]+)+)\s*,?\s*kao\s+zapisničar',
        # "uz učešće Prezime Ime, kao zapisničara" (no prefix)
        r'učeš[ćc]e\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:[- ][A-ZČĆŽŠĐ][a-zčćžšđ]+)+)\s*,?\s*kao\s+zapisničar',
        # "uz sudjelovanje Ime Prezime, kao zapisničara" (no prefix)
        r'sudjelovanje\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:[- ][A-ZČĆŽŠĐ][a-zčćžšđ]+)+)\s*,?\s*kao\s+zapisničar',
        # "uz sudjelovanje sudskog namještenika Prezime Ime, kao zapisničara"
        r'sudjelovanje\s+(?:sudskog\s+)?(?:namještenika?\s+(?:suda\s+)?)?([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:[- ][A-ZČĆŽŠĐ][a-zčćžšđ]+)+)\s*,?\s*kao\s+zapisničar',
        # "uz učestvovanje zapisničara Prezime Ime"
        r'učestvovanje\s+zapisničar[ae]\s+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
        # Generic: any text followed by "kao zapisničara" where text is a name
        r'([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:[- ][A-ZČĆŽŠĐ][a-zčćžšđ]+)+)\s*,?\s*kao\s+zapisničar[aek]',
        # Footer: "ZAPISNIČAR\n Ime Prezime" or "Zapisničar:\nIme Prezime"
        r'(?:ZAPISNIČAR|Zapisničar)[:\s]*/?[\s\n]*([A-ZČĆŽŠĐ][a-zčćžšđ]+(?:[- ][A-ZČĆŽŠĐ][a-zčćžšđ]+)+)',
        # Footer: "ZTO: Ime Prezime"
        r'ZTO[:\s]+([A-ZČĆŽŠĐ][a-zčćžšđ]+\s+[A-ZČĆŽŠĐ][a-zčćžšđ]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            # Remove trailing "s.r." etc
            name = re.sub(r'\s*s\.?\s*r\.?\s*$', '', name).strip()
            # Remove prefix role words that got captured
            name = re.sub(r'^(?:namještenika?|samostaln[eog]+\s+referentkinje?|saradni[ck][ea]|referenta?|referentkinje?)\s+', '', name, flags=re.IGNORECASE).strip()
            if not any(w in name.lower() for w in ['suda', 'sud', 'vijeć', 'optužen', 'okrivlj', 'osnov']):
                if len(name) > 3:
                    return name
    return None

def extract_prior_convictions(text):
    """Extract prior conviction status from TXT."""
    # First check defendant description block
    defendant_block = ''
    dm = re.search(
        r'(?:O[pk]tužen[aio]|Okrivljen[aio])\s*:?\s*\n?(.{50,2000}?)(?:K\s*R\s*I\s*V|OSLOBADJA|OSLOBAĐA|O\s*S\s*U\s*[ĐD]\s*U\s*J\s*E|Zato\s+što|Što\s+je|Da\s+je)',
        text, re.DOTALL | re.IGNORECASE
    )
    if dm:
        defendant_block = dm.group(1)
    
    check_text = defendant_block if defendant_block else text
    
    if re.search(r'neosudj?ivan[a]?|neosuđivan[a]?|ranije\s+neosudj?ivan|ranije\s+neosuđivan', check_text, re.IGNORECASE):
        return 'Ne'
    if re.search(r'nekažnjavan[a]?|nekaznj?avan[a]?', check_text, re.IGNORECASE):
        return 'Ne'
    if re.search(r'(?:ranije\s+)?osudj?ivan[a]?|(?:ranije\s+)?osuđivan[a]?', check_text, re.IGNORECASE):
        return 'Da'
    if re.search(r'izrečena\s+(?:mu|joj)\s+(?:je\s+)?mjera\s+bezbjednosti', check_text, re.IGNORECASE):
        return 'Da'
    return None

def extract_case_description(text):
    """Extract the main case description from TXT."""
    # Pattern 1: "Što je :" followed by description until "- čime"
    patterns = [
        r'(?:Što\s+je\s*:?\s*\n)(.*?)(?:\n\s*-?\s*[čč]ime|\n\s*Čime)',
        r'(?:Da\s+je\s*,?\s*\n)(.*?)(?:\n\s*-?\s*[čč]ime|\n\s*Čime)',
        r'(?:Kriv[a]?\s+je\s*\n\s*Što\s+je\s*:?\s*\n)(.*?)(?:\n\s*-?\s*[čč]ime|\n\s*Čime)',
        r'(?:K\s*r\s*i\s*v\s*a?\s+j\s*e\s*\n\s*Š\s*t\s*o\s+j\s*e\s*:?\s*\n)(.*?)(?:\n\s*-?\s*[čč]ime|\n\s*Čime)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            desc = m.group(1).strip()
            desc = re.sub(r'\s+', ' ', desc)
            if len(desc) > 30:
                # Check it's actually a crime description, not procedural text
                if re.search(r'[Dd]ana\s+\d|neovlašćeno|pribavi[ol]|lažn|falsifik|platnu\s+kartic|novčanic', desc):
                    return desc
    
    # Pattern 2: Look for "Dana DD.MM.YYYY" in the crime facts section
    m = re.search(r'(?:Što\s+je|K\s*R\s*I\s*V).*?(Dana\s+\d{1,2}[\., ]\s*\d{1,2}[\., ]\s*\d{2,4}.*?)(?:\n\s*-?\s*[čc]ime|\n\s*Čime)', text, re.DOTALL | re.IGNORECASE)
    if m:
        desc = m.group(1).strip()
        desc = re.sub(r'\s+', ' ', desc)
        if len(desc) > 30:
            return desc
    
    return None

def extract_evidence(text):
    """Extract evidence items from TXT (Obrazloženje section)."""
    evidence_section = ''
    em = re.search(r'O\s*b\s*r\s*a\s*z\s*l\s*o\s*ž\s*e\s*n\s*j\s*e(.*?)$', text, re.DOTALL | re.IGNORECASE)
    if em:
        evidence_section = em.group(1)
    
    check_txt = evidence_section if evidence_section else text
    evidence_items = []
    
    evidence_patterns = [
        r'(izvod[a]?\s+iz\s+kaznene\s+evidencije[^,\.\n]{0,80})',
        r'(uvjerenj[ea]\s+iz\s+kaznene\s+evidencije[^,\.\n]{0,80})',
        r'(potvrdu?\s+o\s+privremeno\s+oduzetim\s+predmetima[^,\.\n]{0,80})',
        r'(izvještaj[a]?\s+(?:o\s+)?(?:kriminalističke\s+)?(?:tehnike|tehničke|tehničkoj\s+analizi)[^,\.\n]{0,100})',
        r'(nalaz[a]?\s+i\s+mišljenj[ae]\s+vještaka[^,\.\n]{0,100})',
        r'(nalaz[a]?\s+vještaka[^,\.\n]{0,100})',
        r'(listing[a]?\s+komunikacija[^,\.\n]{0,80})',
        r'(zapisnik[a]?\s+o\s+(?:uviđaju|prepoznavanju|pretresanju|saslušanju)[^,\.\n]{0,100})',
        r'(potvrdu?\s+(?:CKB|banke|NLB|Erste|Komercijalne|Crnogorske)[^,\.\n]{0,100})',
        r'(iskaz[a]?\s+(?:svjedoka|svedoka|okrivljenoga?|optuženo?ga?)[^,\.\n]{0,100})',
        r'(video\s*(?:snimak|zapis|nadzor)[^,\.\n]{0,80})',
        r'(fotodokumentacij[aeou][^,\.\n]{0,80})',
        r'(grafološk[aeiou]\s+vještačenj[aeu][^,\.\n]{0,80})',
        r'(službenu?\s+zabilješk[aeu][^,\.\n]{0,100})',
        r'(izvještaj[a]?\s+o\s+(?:ekspertizi|balističkom|forenzičk)[^,\.\n]{0,100})',
        r'(medicinsk[aeiou]\s+dokumentacij[aeou][^,\.\n]{0,80})',
    ]
    
    for pat in evidence_patterns:
        for m2 in re.finditer(pat, check_txt, re.IGNORECASE):
            ev = m2.group(1).strip()
            # Clean up
            ev = re.sub(r'\s+', ' ', ev)
            ev = ev.rstrip(',. ')
            if ev and len(ev) > 5:
                # Avoid exact duplicates
                if not any(ev.lower() == existing.lower() for existing in evidence_items):
                    evidence_items.append(ev)
    
    return evidence_items if evidence_items else None

def extract_sentence(text):
    """Extract the sentence/penalty from TXT."""
    # Pattern for prison sentence - handle optional period/dot before parenthesis like "6.(šest)"
    patterns = [
        r'(?:Na\s+)?(?:jedinstvenu?\s+)?[Kk]azn[aue]\s+zatvora\s+u\s+trajanju\s+od\s+(\d+)\s*\.?\s*\(([^)]+)\)\s*(mjesec[ia]?|mesec[ia]?|godin[ae]?|dan[a]?)',
        r'(?:Na\s+)?[Kk]azn[aue]\s+zatvora\s+u\s+trajanju\s+od\s+(\d+)\s*(mjesec[ia]?|mesec[ia]?|godin[ae]?|dan[a]?)',
        r'[Kk]azn[aue]\s+rada\s+u\s+javnom\s+interesu\s+u\s+trajanju\s+od\s+(\d+)\s*\.?\s*\(([^)]+)\)\s*(časov[a]?|sat[ia]?)',
        r'[Kk]azn[aue]\s+rada\s+u\s+javnom\s+interesu\s+u\s+trajanju\s+od\s+(\d+)\s*(časov[a]?|sat[ia]?)',
    ]
    
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            groups = m.groups()
            num = groups[0]
            if len(groups) == 3 and '(' in pat:
                word_num = groups[1]
                unit = groups[2]
                return f"{num} ({word_num}) {unit}"
            elif len(groups) >= 2:
                unit = groups[-1]
                return f"{num} {unit}"
    
    # Novčana kazna
    m = re.search(r'nov[čc]an[aou]\s+kazn[aou]\s+(?:u\s+iznosu\s+od\s+)?(\d+[,.]?\d*)\s*(?:eura?|EUR|€)', text, re.IGNORECASE)
    if m:
        return f"novčana kazna {m.group(1)} EUR"
    
    # Sudska opomena (judicial warning)
    if re.search(r'suds[kc][aou]\s+opomen[aou]', text, re.IGNORECASE):
        return "sudska opomena"
    
    return None

def extract_verdict_type(text):
    """Extract verdict type from TXT."""
    is_conditional = bool(re.search(r'USLOVN[UAO]\s+OSUD[UAO]|USLOVN[UAO]\s+PRESUD[UAO]|uslovn[aou]\s+osud[aou]|uslovn[aou]\s+presud[aou]', text, re.IGNORECASE))
    
    if re.search(r'OSLOBADJA\s+SE\s+OD\s+OPTUŽBE|OSLOBAĐA\s+SE\s+OD\s+OPTUŽBE|OSLOBAĐA\s+SE', text, re.IGNORECASE):
        return 'Oslobađajuća'
    elif is_conditional:
        return 'Uslovna presuda'
    elif re.search(r'KRIV\s+JE|K\s*R\s*I\s*V\s*A?\s+JE', text):
        return 'Osuđujuća'
    elif re.search(r'OGLAŠAVA\s+SE\s+KRIVIM|O\s*S\s*U\s*[ĐD]\s*U\s*J\s*E', text, re.IGNORECASE):
        return 'Osuđujuća'
    
    return None

def extract_marital_status(text):
    """Extract marital status from TXT."""
    if re.search(r'\bneoženjen\b|\bneudata\b', text, re.IGNORECASE):
        return 'neoženjen/neudata'
    elif re.search(r'\brazveden\b|\brazvedena\b', text, re.IGNORECASE):
        return 'razveden/razvedena'
    elif re.search(r'\boženjen\b|\budata\b', text, re.IGNORECASE):
        return 'oženjen/udata'
    return None

def extract_residence(text):
    """Extract residence from TXT."""
    patterns = [
        r'(?:nastanjen[aog]*|sa\s+prebivalištem)\s+u\s+([A-ZČĆŽŠĐa-zčćžšđ]{3,}(?:\s+[A-ZČĆŽŠĐa-zčćžšđ]+)?)',
        r'(?:sa\s+boravištem)\s+u\s+([A-ZČĆŽŠĐa-zčćžšđ]{3,}(?:\s+[A-ZČĆŽŠĐa-zčćžšđ]+)?)',
    ]
    bad_words = ['ul', 'ulici', 'jmbg', 'godine', 'dana', 'mjestu', 'mjesec', 'mesec',
                 'izvoda', 'državi', 'selu', 'naselju', 'adresi', 'toku', 'roku', 'gradu']
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            place = m.group(1).strip()
            if len(place) < 3:
                continue
            if any(w == place.lower() for w in bad_words):
                continue
            if any(place.lower().startswith(w) for w in bad_words):
                continue
            return place
    return None

def inject_missing_field_in_proprietary(content, tag, value, after_tag=None):
    """Inject a missing XML tag into the <proprietary> section.
    Handles self-closing empty tags like <tag /> or <tag/>.
    If after_tag is given, insert after the first occurrence of that closing tag.
    Otherwise, insert before </proprietary>."""
    
    # Check if tag already exists with content
    if re.search(rf'<{tag}>[^<]+</{tag}>', content):
        return content  # Already has content
    
    escaped_value = xml_escape(value)
    
    # First try: replace self-closing empty tag like <tag /> or <tag/>
    self_closing_pattern = rf'<{tag}\s*/>'
    if re.search(self_closing_pattern, content):
        content = re.sub(self_closing_pattern, f'<{tag}>{escaped_value}</{tag}>', content, count=1)
        return content
    
    # Second try: replace empty tag like <tag></tag>
    empty_pattern = rf'<{tag}>\s*</{tag}>'
    if re.search(empty_pattern, content):
        content = re.sub(empty_pattern, f'<{tag}>{escaped_value}</{tag}>', content, count=1)
        return content
    
    # Third: inject new element
    new_element = f"        <{tag}>{escaped_value}</{tag}>"
    
    if after_tag:
        # Insert after the closing tag
        pattern = rf'(</{after_tag}>)'
        m = re.search(pattern, content)
        if m:
            insert_pos = m.end()
            content = content[:insert_pos] + '\n' + new_element + content[insert_pos:]
            return content
    
    # Insert before </proprietary> with flexible whitespace
    m = re.search(r'(\s*</proprietary>)', content)
    if m:
        content = content[:m.start()] + '\n' + new_element + m.group(0) + content[m.end():]
    return content

def inject_evidence_in_proprietary(content, evidence_items):
    """Inject <dokazi> section into the <proprietary> block."""
    # Check if dokazi already exists
    if re.search(r'<dokazi>', content):
        return content
    
    lines = ['        <dokazi>']
    for ev in evidence_items:
        escaped = xml_escape(ev)
        lines.append(f'          <dokaz>{escaped}</dokaz>')
    lines.append('        </dokazi>')
    
    dokazi_block = '\n'.join(lines)
    
    # Insert before </proprietary>
    content = content.replace('      </proprietary>', dokazi_block + '\n      </proprietary>')
    return content

def inject_evidence_in_motivation(content, evidence_items):
    """Inject evidence into the <motivation> section of the judgmentBody."""
    # Check if there's already a motivation section with evidence
    if re.search(r'<motivation>', content) and re.search(r'<tblock>', content):
        return content
    
    lines = []
    lines.append('      <motivation>')
    lines.append('        <block name="dokazi">')
    lines.append('          <tblock>')
    for ev in evidence_items:
        escaped = xml_escape(ev)
        lines.append(f'            <p>• {escaped}</p>')
    lines.append('          </tblock>')
    lines.append('        </block>')
    lines.append('      </motivation>')
    
    motivation_block = '\n'.join(lines)
    
    # If there's already a <motivation> section, skip
    if '<motivation>' in content:
        return content
    
    # Insert before <decision>
    if '<decision>' in content:
        content = content.replace('      <decision>', motivation_block + '\n      <decision>')
    
    return content

def update_xml_field(content, tag, new_value):
    """Update an existing XML tag value, or replace 'Nepoznat' with actual value."""
    escaped = xml_escape(new_value)
    
    # Replace existing empty or "Nepoznat" value
    pattern = rf'(<{tag}>)(?:Nepoznat|N/A|None|)(</{tag}>)'
    replacement = rf'\g<1>{escaped}\g<2>'
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        return new_content
    
    return content

def fix_vrsta_presude(content):
    """Fix 'Uslovna osuda' to 'Uslovna presuda' in <vrstaPresude> tags."""
    content = re.sub(
        r'<vrstaPresude>Uslovna osuda</vrstaPresude>',
        '<vrstaPresude>Uslovna presuda</vrstaPresude>',
        content
    )
    return content

def is_field_empty(content, tag):
    """Check if an XML field is missing or empty (including self-closing tags)."""
    # Self-closing: <tag /> or <tag/>
    if re.search(rf'<{tag}\s*/>', content):
        return True
    # Tag with empty or placeholder content
    m = re.search(rf'<{tag}>([^<]*)</{tag}>', content)
    if m:
        val = m.group(1).strip()
        return not val or val in ('Nepoznat', 'N/A', 'None', '')
    # Tag doesn't exist at all
    if not re.search(rf'<{tag}[ />]', content) and not re.search(rf'<{tag}>', content):
        return True
    return False

def process_xml_file(xml_path, dry_run=False):
    """Process a single XML file: find missing data, fill from TXT."""
    xml_name = os.path.basename(xml_path)
    m = re.match(r'K\s+(\d+)_(\d+)\.xml', xml_name)
    if not m:
        return None
    
    case_num = int(m.group(1))
    year = int(m.group(2))
    
    try:
        with open(xml_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return None
    
    original_content = content
    changes = []
    
    # 1. Fix "Uslovna osuda" → "Uslovna presuda"
    new_content = fix_vrsta_presude(content)
    if new_content != content:
        changes.append('Fixed vrstaPresude: Uslovna osuda → Uslovna presuda')
        content = new_content
    
    # Find TXT file
    txt_path = find_txt_file(case_num, year)
    if not txt_path:
        # No TXT file - only do terminology fixes
        if content != original_content and not dry_run:
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return changes if changes else None
    
    text = read_txt(txt_path)
    if not text:
        if content != original_content and not dry_run:
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(content)
        return changes if changes else None
    
    # 2. Fix missing sudija
    if is_field_empty(content, 'sudija'):
        judge = extract_judge(text)
        if judge:
            content = inject_missing_field_in_proprietary(content, 'sudija', judge, 'sud')
            changes.append(f'Added sudija: {judge}')
    
    # 3. Fix missing zapisnicar
    if is_field_empty(content, 'zapisnicar'):
        clerk = extract_clerk(text)
        if clerk:
            content = inject_missing_field_in_proprietary(content, 'zapisnicar', clerk)
            changes.append(f'Added zapisnicar: {clerk}')
    
    # 4. Fix missing ranijeOsudjivan
    if is_field_empty(content, 'ranijeOsudjivan'):
        prior = extract_prior_convictions(text)
        if prior:
            content = inject_missing_field_in_proprietary(content, 'ranijeOsudjivan', prior, 'optuzeni')
            changes.append(f'Added ranijeOsudjivan: {prior}')
    
    # 5. Fix missing kazna
    if is_field_empty(content, 'kazna'):
        sentence = extract_sentence(text)
        if sentence:
            content = inject_missing_field_in_proprietary(content, 'kazna', sentence, 'clanKZ')
            changes.append(f'Added kazna: {sentence}')
    
    # 6. Fix missing opisSlucaja
    if is_field_empty(content, 'opisSlucaja'):
        desc = extract_case_description(text)
        if desc:
            content = inject_missing_field_in_proprietary(content, 'opisSlucaja', desc)
            changes.append(f'Added opisSlucaja: {desc[:80]}...')
    
    # 7. Fix missing dokazi
    if not re.search(r'<dokaz>[^<]+</dokaz>', content):
        evidence = extract_evidence(text)
        if evidence:
            content = inject_evidence_in_proprietary(content, evidence)
            content = inject_evidence_in_motivation(content, evidence)
            changes.append(f'Added {len(evidence)} dokazi items')
    
    # 8. Fix missing vrstaPresude
    if is_field_empty(content, 'vrstaPresude'):
        verdict = extract_verdict_type(text)
        if verdict:
            content = inject_missing_field_in_proprietary(content, 'vrstaPresude', verdict)
            changes.append(f'Added vrstaPresude: {verdict}')
    
    # 9. Fix missing bracniStatus
    if is_field_empty(content, 'bracniStatus'):
        marital = extract_marital_status(text)
        if marital:
            content = inject_missing_field_in_proprietary(content, 'bracniStatus', marital)
            changes.append(f'Added bracniStatus: {marital}')
    
    # 10. Fix missing prebivaliste
    if is_field_empty(content, 'prebivaliste'):
        residence = extract_residence(text)
        if residence:
            content = inject_missing_field_in_proprietary(content, 'prebivaliste', residence)
            changes.append(f'Added prebivaliste: {residence}')
    
    # Also update the judgmentBody sections if opisSlucaja or dokazi were added
    # Update opisSlucaja in <arguments> block
    opis_match = re.search(r'<opisSlucaja>([^<]+)</opisSlucaja>', content)
    args_block = re.search(r'<block name="opisSlucaja">\s*<p>([^<]*)</p>', content)
    if opis_match and args_block:
        opis_text = opis_match.group(1)
        args_text = args_block.group(1)
        if len(opis_text) > len(args_text) + 20:
            # Update arguments block with the full description
            content = content.replace(
                f'<block name="opisSlucaja">\n          <p>{args_text}</p>',
                f'<block name="opisSlucaja">\n          <p>{opis_text}</p>'
            )
    
    # Write if changed
    if content != original_content and not dry_run:
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return changes if changes else None


def main():
    dry_run = '--dry-run' in sys.argv
    
    xml_files = sorted(glob.glob(os.path.join(XML_DIR, 'K *.xml')))
    
    total_changes = 0
    files_changed = 0
    
    for xml_path in xml_files:
        xml_name = os.path.basename(xml_path)
        changes = process_xml_file(xml_path, dry_run=dry_run)
        
        if changes:
            files_changed += 1
            total_changes += len(changes)
            prefix = "[DRY RUN] " if dry_run else ""
            print(f"{prefix}{xml_name}:")
            for change in changes:
                print(f"  ✓ {change}")
    
    mode = "DRY RUN - no files modified" if dry_run else "FILES UPDATED"
    print(f"\n=== {mode} ===")
    print(f"Files changed: {files_changed}/{len(xml_files)}")
    print(f"Total changes: {total_changes}")


if __name__ == '__main__':
    main()
