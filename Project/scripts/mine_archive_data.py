"""
Mine archive text files (raw court decisions) for missing personal data
and update the corresponding Akomanotoso XML files.

Extracts: zaposlenost, obrazovanje, bracniStatus, ranijeOsudjivan
from the defendant description paragraph in the verdict text.
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
ARCHIVE_DIRS = [
    BASE_DIR / "archive" / "presude" / "falsifikovanje novca",
    BASE_DIR / "archive" / "presude" / "falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko plaćanje",
]
XML_DIR = BASE_DIR / "data" / "cases" / "akomantoso"


def txt_name_to_xml_name(txt_name):
    """Convert text filename (K 1002010.txt) to XML filename (K 100_2010.xml).
    
    Text: 'K 1002010.txt' -> number is '1002010', last 4 digits = year '2010', rest = '100'
    XML:  'K 100_2010.xml'
    """
    stem = txt_name.replace(".txt", "").strip()
    # Extract number part after 'K '
    match = re.match(r"K\s+(\d+)", stem)
    if not match:
        return None
    digits = match.group(1)
    if len(digits) < 5:
        return None  # Need at least 1 digit for case + 4 for year
    year = digits[-4:]
    case_num = digits[:-4]
    if not case_num:
        return None
    return f"K {case_num}_{year}.xml"


def extract_defendant_paragraph(text):
    """Extract the defendant description paragraph from the verdict text.
    
    This is the paragraph starting with 'Optužen' or 'Okrivljen' after the 'PRESUDA/PRESUDU' section,
    containing comma-separated personal data.
    """
    # Remove header noise (first lines with Email, Facebook etc.)
    # Find the PRESUDA section
    presuda_match = re.search(
        r"P\s*R\s*E\s*S\s*U\s*D\s*[UAu]",
        text,
        re.IGNORECASE
    )
    if not presuda_match:
        return None
    
    text_after_presuda = text[presuda_match.end():]
    
    # Find the defendant description paragraph
    # Patterns: "Optuženi", "Optužena", "Okrivljeni", "Okrivljena", "Okrivljenog"
    defendant_match = re.search(
        r"((?:Optužen[iaeo]|Okrivljen[iaeo]|Okr\.)\s*:?\s*\n?\s*[A-ZŠĐČĆŽА-Я].*?)(?:\n\s*\n|\n\s*(?:K\s*R\s*I\s*V|O\s*S\s*L\s*O\s*B|O\s*S\s*U\s*[DĐ]|Što\s+je|ŠTO\s+JE|\-\s*(?:čime|na\s+osnovu)|na\s+osnovu\s+čl))",
        text_after_presuda,
        re.DOTALL | re.IGNORECASE
    )
    if defendant_match:
        return defendant_match.group(1)
    
    # Fallback: just grab 2000 chars after defendant name start
    defendant_start = re.search(
        r"(?:Optužen[iaeo]|Okrivljen[iaeo]|Okr\.)\s*:?\s*\n?\s*[A-ZŠĐČĆŽА-Я]",
        text_after_presuda,
        re.IGNORECASE
    )
    if defendant_start:
        chunk = text_after_presuda[defendant_start.start():defendant_start.start()+2000]
        # Take up to double newline
        end = chunk.find("\n\n")
        if end > 0:
            return chunk[:end]
        return chunk
    
    return None


def extract_zaposlenost(para):
    """Extract employment status from defendant paragraph."""
    if not para:
        return None
    para_lower = para.lower()
    
    # Check for specific professions (means employed)
    profession_patterns = [
        r"po\s+zanimanju\s+(\w+)",
        r"autoelektričar", r"automehaničar", r"mehaničar",
        r"vozač", r"konobar", r"kuvar", r"radnik",
        r"prodavac", r"zanatlija", r"stolar", r"bravar",
        r"moler", r"keramičar", r"zidar", r"tesar",
        r"ekonomist[a]?", r"pravnik", r"inženjer",
        r"profesor", r"nastavnik", r"ljekar", r"doktor",
        r"trgovac", r"ugostitelj", r"preduzetni",
        r"službenik", r"činovnik", r"policaj",
    ]
    
    # Direct patterns
    if re.search(r"\bnezaposl", para_lower):
        return "nezaposlen"
    if re.search(r"\bzaposl", para_lower):
        return "zaposlen"
    if re.search(r"\bstudent\b", para_lower):
        return "student"
    if re.search(r"\bpenzion", para_lower):
        return "penzioner"
    if re.search(r"\bučenik\b|\bucenik\b", para_lower):
        return "student"
    
    # Check professions (implies employed)
    for pattern in profession_patterns:
        if re.search(pattern, para_lower):
            return "zaposlen"
    
    return None


def extract_obrazovanje(para):
    """Extract education level from defendant paragraph."""
    if not para:
        return None
    para_lower = para.lower()
    
    # VSS / higher education
    if re.search(r"\bvss\b|\bvšs\b|\bvss\b", para_lower):
        return "VSS"
    if re.search(r"visok[aou]\s+(?:stručn|škol|obrazov)|fakultet|diplom|univerzitet|magistar|master", para_lower):
        return "VSS"
    
    # SSS / secondary education
    if re.search(r"\bsss\b", para_lower):
        return "SSS"
    if re.search(r"završi[ola]+\s+srednju|srednju\s+(?:škol|stručn)|srednje\s+(?:obrazov|škol)|srednja\s+(?:stručna\s+)?sprema", para_lower):
        return "SSS"
    # Specific schools that indicate SSS
    if re.search(r"završi[ola]+\s+\w+\s+školu(?!\s+i\s+fakultet)", para_lower) and not re.search(r"osnovnu\s+školu", para_lower):
        return "SSS"
    
    # Osnovna / primary education
    if re.search(r"osnovna\s+škola|osnovnu\s+školu|završi[ola]+\s+osnovnu|završi[ola]+\s+osam\s+razred|završi[ola]+\s+8\s+razred", para_lower):
        return "osnovna"
    if re.search(r"\bosnovna\b.*\bobrazov", para_lower):
        return "osnovna"
    
    # Just "pismen" (literate) without specific school
    if re.search(r"\bpismen[a]?\b", para_lower) and not re.search(r"sss|vss|vš|srednj|osnov|fakultet|škol", para_lower):
        return "pismen"
    
    # "nepismen" (illiterate)
    if re.search(r"\bnepismen", para_lower):
        return "nepismen"
    
    return None


def extract_bracni_status(para):
    """Extract marital status from defendant paragraph."""
    if not para:
        return None
    para_lower = para.lower()
    
    # Check for divorced first (more specific)
    if re.search(r"\brazveden[a]?\b", para_lower):
        return "razveden"
    
    # Single/unmarried
    if re.search(r"\bneoženjen\b|\bneozenjen\b|\bneudata\b|\bneoženja\b|\bneoženj\b|\bneoženje\b", para_lower):
        return "neozenjen"
    
    # Married
    if re.search(r"\boženjen\b|\bozenjen\b|\budata\b|\budatа\b|\budati\b", para_lower):
        return "ozenjen"
    
    # Widow/widower
    if re.search(r"\budovac\b|\budovica\b", para_lower):
        return "udovac"
    
    return None


def extract_ranije_osudjivan(para):
    """Extract previous conviction status from defendant paragraph."""
    if not para:
        return None
    para_lower = para.lower()
    
    # Negative first (neosuđivan)
    if re.search(r"neosuđivan|neosudjivan|neosudj|nije\s+osuđivan|nije\s+osudjivan|neosudjivan|nekažnjavan|nekažnjav|nekažnj|neosuđ|neosu[đdj]", para_lower):
        return "ne"
    
    # Positive (osuđivan, ranije osuđivan)
    if re.search(r"osuđivan|osudjivan|ranije\s+osuđ|ranije\s+osudj|osudjivan\s+presudom|osuđivan\s+presudom|višestruko\s+osuđ", para_lower):
        return "da"
    
    return None


def load_xml(xml_path):
    """Load XML and return tree, root, and proprietary element."""
    ET.register_namespace('', 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0')
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    ns = {'akn': 'http://docs.oasis-open.org/legaldocml/ns/akn/3.0'}
    prop = root.find('.//akn:proprietary', ns)
    if prop is None:
        prop = root.find('.//proprietary')
    
    return tree, root, prop


def get_xml_value(prop, tag):
    """Get current value of a tag in the proprietary element."""
    ns = '{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}'
    el = prop.find(tag)
    if el is None:
        el = prop.find(f"{ns}{tag}")
    if el is not None and el.text:
        return el.text.strip()
    return None


def set_xml_value(prop, tag, value):
    """Set or create a tag in the proprietary element."""
    ns = '{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}'
    el = prop.find(tag)
    if el is None:
        el = prop.find(f"{ns}{tag}")
    if el is not None:
        el.text = value
    else:
        # Create new element - insert before tipKrivicnogDjela or at end
        new_el = ET.SubElement(prop, tag)
        new_el.text = value


def is_missing(value):
    """Check if a value is missing/unknown."""
    if value is None:
        return True
    v = value.lower().strip()
    return v in ("", "nepoznat", "unknown")


def main():
    # Step 1: Map archive text files to XML files
    print("=" * 70)
    print("MINING ARCHIVE TEXT FILES FOR MISSING DATA")
    print("=" * 70)
    
    txt_files = {}
    for archive_dir in ARCHIVE_DIRS:
        if not archive_dir.exists():
            print(f"WARNING: Directory not found: {archive_dir}")
            continue
        for f in archive_dir.iterdir():
            if f.suffix == ".txt" and f.name.startswith("K "):
                xml_name = txt_name_to_xml_name(f.name)
                if xml_name:
                    txt_files[xml_name] = f
    
    print(f"\nFound {len(txt_files)} archive text files mapped to XML names")
    
    # Step 2: Check which XMLs need updates
    xml_files = sorted(XML_DIR.glob("*.xml"))
    print(f"Found {len(xml_files)} XML files")
    
    updates = {}  # xml_name -> {field: new_value}
    not_found_txts = []
    extracted_data = {}  # for reporting
    
    for xml_path in xml_files:
        xml_name = xml_path.name
        
        # Load XML
        try:
            tree, root, prop = load_xml(xml_path)
        except ET.ParseError as e:
            print(f"  XML parse error: {xml_name}: {e}")
            continue
        
        if prop is None:
            continue
        
        # Get current values
        current = {
            'zaposlenost': get_xml_value(prop, 'zaposlenost'),
            'obrazovanje': get_xml_value(prop, 'obrazovanje'),
            'bracniStatus': get_xml_value(prop, 'bracniStatus'),
            'ranijeOsudjivan': get_xml_value(prop, 'ranijeOsudjivan'),
        }
        
        # Check if any field needs updating
        needs_update = any(is_missing(v) for v in current.values())
        if not needs_update:
            continue
        
        # Find corresponding text file
        if xml_name not in txt_files:
            missing_fields = [k for k, v in current.items() if is_missing(v)]
            if missing_fields:
                not_found_txts.append((xml_name, missing_fields))
            continue
        
        # Read text file
        txt_path = txt_files[xml_name]
        try:
            text = txt_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                text = txt_path.read_text(encoding='latin-1')
            except Exception:
                print(f"  Cannot read: {txt_path.name}")
                continue
        
        # Extract defendant paragraph
        para = extract_defendant_paragraph(text)
        if not para:
            missing_fields = [k for k, v in current.items() if is_missing(v)]
            if missing_fields:
                print(f"  No defendant paragraph found in: {txt_path.name} (missing: {', '.join(missing_fields)})")
            continue
        
        # Extract data from paragraph
        case_updates = {}
        
        if is_missing(current['zaposlenost']):
            val = extract_zaposlenost(para)
            if val:
                case_updates['zaposlenost'] = val
        
        if is_missing(current['obrazovanje']):
            val = extract_obrazovanje(para)
            if val:
                case_updates['obrazovanje'] = val
        
        if is_missing(current['bracniStatus']):
            val = extract_bracni_status(para)
            if val:
                case_updates['bracniStatus'] = val
        
        if is_missing(current['ranijeOsudjivan']):
            val = extract_ranije_osudjivan(para)
            if val:
                case_updates['ranijeOsudjivan'] = val
        
        if case_updates:
            updates[xml_name] = case_updates
            extracted_data[xml_name] = {
                'paragraph_preview': para[:200],
                'updates': case_updates,
                'current': {k: v for k, v in current.items() if is_missing(v)}
            }
    
    # Step 3: Report findings
    print("\n" + "=" * 70)
    print("EXTRACTION RESULTS")
    print("=" * 70)
    
    total_updates = sum(len(u) for u in updates.values())
    print(f"\nFiles to update: {len(updates)}")
    print(f"Total field updates: {total_updates}")
    
    # Count per field
    field_counts = {'zaposlenost': 0, 'obrazovanje': 0, 'bracniStatus': 0, 'ranijeOsudjivan': 0}
    for upd in updates.values():
        for field in upd:
            field_counts[field] += 1
    
    print("\nUpdates per field:")
    for field, count in field_counts.items():
        print(f"  {field}: {count}")
    
    print("\nDetailed updates:")
    for xml_name in sorted(updates.keys()):
        upd = updates[xml_name]
        data = extracted_data[xml_name]
        print(f"\n  {xml_name}:")
        for field, val in upd.items():
            print(f"    {field}: (was: {data['current'].get(field, '?')}) -> {val}")
    
    if not_found_txts:
        print(f"\n\nXML files with missing data but NO matching text file: {len(not_found_txts)}")
        for xml_name, fields in not_found_txts[:10]:
            print(f"  {xml_name}: missing {', '.join(fields)}")
        if len(not_found_txts) > 10:
            print(f"  ... and {len(not_found_txts) - 10} more")
    
    # Step 4: Apply updates
    if total_updates == 0:
        print("\nNo updates to apply.")
        return
    
    print(f"\n{'=' * 70}")
    print(f"APPLYING {total_updates} UPDATES TO {len(updates)} XML FILES")
    print(f"{'=' * 70}")
    
    success_count = 0
    error_count = 0
    
    for xml_name, case_updates in sorted(updates.items()):
        xml_path = XML_DIR / xml_name
        try:
            # Re-read XML to apply updates
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for field, value in case_updates.items():
                # Try to replace existing tag with nepoznat/Nepoznat
                patterns = [
                    (f"<{field}>nepoznat</{field}>", f"<{field}>{value}</{field}>"),
                    (f"<{field}>Nepoznat</{field}>", f"<{field}>{value}</{field}>"),
                    (f"<{field}>NEPOZNAT</{field}>", f"<{field}>{value}</{field}>"),
                    (f"<{field}></{field}>", f"<{field}>{value}</{field}>"),
                ]
                
                replaced = False
                for old, new in patterns:
                    if old in content:
                        content = content.replace(old, new, 1)
                        replaced = True
                        break
                
                if not replaced:
                    # Tag doesn't exist - need to insert it
                    # Insert before <tipKrivicnogDjela> or <clanKZ>
                    for anchor in ["<tipKrivicnogDjela>", "<clanKZ>", "<kazna>"]:
                        if anchor in content:
                            indent = "        "  # Match existing indentation
                            new_tag = f"{indent}<{field}>{value}</{field}>\n        "
                            content = content.replace(anchor, new_tag + anchor, 1)
                            replaced = True
                            break
                    
                    if not replaced:
                        print(f"  WARNING: Could not insert {field} in {xml_name}")
            
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            success_count += 1
            fields_str = ", ".join(f"{k}={v}" for k, v in case_updates.items())
            print(f"  Updated: {xml_name} ({fields_str})")
            
        except Exception as e:
            error_count += 1
            print(f"  ERROR updating {xml_name}: {e}")
    
    print(f"\nDone! Updated {success_count} files, {error_count} errors.")


if __name__ == "__main__":
    main()
