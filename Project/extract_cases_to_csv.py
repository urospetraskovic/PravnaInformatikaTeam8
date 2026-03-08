"""
Extract key facts from Akomanotoso XML court decision files into CSV format
for use with the jCOLIBRI Case-Based Reasoning system.

Legal domain: Chapter 23 - Crimes Against Payment System (Glava 23 KZ CG)
- Article 258: Falsifikovanje novca (Counterfeiting money)
- Article 260: Zloupotreba platnih kartica (Credit card fraud)
"""

import os
import csv
import re
import xml.etree.ElementTree as ET

XML_DIR = os.path.join(os.path.dirname(__file__), "data", "cases", "akomantoso")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "presude-cbr", "src", "main", "resources", "presude.csv")

NS = {"akn": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"}


def get_text(element, tag):
    """Get text content of a child element, or empty string if not found."""
    el = element.find(tag)
    if el is not None and el.text:
        return el.text.strip()
    return ""


def normalize_crime_type(raw):
    """Normalize crime type to standard categories."""
    raw_lower = raw.lower()
    if "kreditn" in raw_lower or "platnih kartica" in raw_lower or "260" in raw_lower:
        return "zloupotreba platnih kartica"
    if "falsifikovan" in raw_lower and "novca" in raw_lower:
        return "falsifikovanje novca"
    if "falsifikovan" in raw_lower:
        return "falsifikovanje novca"
    return raw if raw else "nepoznat"


def normalize_article(raw):
    """Normalize law article reference."""
    if not raw:
        return "nepoznat"
    # Remove extra whitespace
    raw = " ".join(raw.split())
    return raw


def normalize_previously_convicted(raw):
    """Normalize previous conviction status."""
    raw_lower = raw.lower().strip() if raw else ""
    if raw_lower == "da":
        return "da"
    if raw_lower == "ne":
        return "ne"
    if "neosuđivan" in raw_lower or "neosudj" in raw_lower or "neosudjivan" in raw_lower:
        return "ne"
    if "osuđivan" in raw_lower or "osudjivan" in raw_lower:
        if "ne" not in raw_lower:
            return "da"
        return "ne"
    return "nepoznat"


def normalize_employment(raw):
    """Normalize employment status."""
    raw_lower = raw.lower() if raw else ""
    if not raw_lower or raw_lower == "nepoznat":
        return "nepoznat"
    if "nezaposl" in raw_lower:
        return "nezaposlen"
    if "zaposl" in raw_lower or "radi" in raw_lower or "firmi" in raw_lower:
        return "zaposlen"
    if "student" in raw_lower or "učenik" in raw_lower or "ucenik" in raw_lower or "škol" in raw_lower:
        return "student"
    if "penzion" in raw_lower:
        return "penzioner"
    return "nepoznat"


def normalize_marital_status(raw):
    """Normalize marital status."""
    raw_lower = raw.lower() if raw else ""
    if not raw_lower:
        return "nepoznat"
    if "neoženjen" in raw_lower or "neozenjen" in raw_lower or "neudata" in raw_lower:
        return "neozenjen"
    if "oženjen" in raw_lower or "ozenjen" in raw_lower or "udata" in raw_lower or "udatа" in raw_lower:
        return "ozenjen"
    if "razveden" in raw_lower or "razvedena" in raw_lower:
        return "razveden"
    return "nepoznat"


def normalize_verdict_type(raw):
    """Normalize verdict type."""
    raw_lower = raw.lower() if raw else ""
    if "uslov" in raw_lower:
        return "uslovna"
    if "oslobađ" in raw_lower or "oslobadj" in raw_lower or "oslobadjajuc" in raw_lower:
        return "oslobadjajuca"
    if "osuđ" in raw_lower or "osudj" in raw_lower or "osudjujuc" in raw_lower:
        return "osudjujuca"
    return "nepoznat"


def parse_euro_amount(text):
    """Parse a euro amount string like '1.000,50 EUR' or '400,00' into a float."""
    if not text:
        return 0.0
    # Remove EUR suffix
    text = re.sub(r'\s*(EUR|eura|evra|€)\s*', '', text, flags=re.IGNORECASE).strip()
    # Handle European number format: 1.000,50 -> 1000.50
    if ',' in text and '.' in text:
        text = text.replace('.', '').replace(',', '.')
    elif ',' in text:
        text = text.replace(',', '.')
    # Remove any remaining non-numeric chars except decimal point
    text = re.sub(r'[^\d.]', '', text)
    try:
        return float(text)
    except ValueError:
        return 0.0


def extract_amounts(proprietary):
    """Extract all monetary amounts and return (max_amount, total_amount, transaction_count)."""
    AKN = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
    amounts = []
    for tag in ["iznosi", f"{AKN}iznosi"]:
        iznosi_el = proprietary.find(tag)
        if iznosi_el is not None:
            for itag in ["iznos", f"{AKN}iznos"]:
                for iznos_el in iznosi_el.findall(itag):
                    if iznos_el.text:
                        val = parse_euro_amount(iznos_el.text.strip())
                        if val > 0:
                            amounts.append(val)
            break
    if not amounts:
        # Try to extract from opisSlucaja
        opis_el = proprietary.find("opisSlucaja") or proprietary.find(f"{AKN}opisSlucaja")
        opis = opis_el.text.strip() if opis_el is not None and opis_el.text else ""
        if opis:
            euro_matches = re.findall(r"([\d.,]+)\s*(?:eura|evra|€|eur)", opis, re.IGNORECASE)
            if euro_matches:
                vals = [parse_euro_amount(m) for m in euro_matches]
                amounts = [v for v in vals if v > 0]
    max_amount = max(amounts) if amounts else 0.0
    total_amount = sum(amounts) if amounts else 0.0
    transaction_count = len(amounts)
    return max_amount, total_amount, transaction_count


def extract_sentence_months(kazna_text):
    """Extract sentence duration in months from the kazna text."""
    if not kazna_text:
        return 0
    kazna_lower = kazna_text.lower()

    # Check for "novčana kazna" (monetary fine only, no prison)
    if "novčan" in kazna_lower or "novcan" in kazna_lower:
        return 0

    # Try to find years
    years = 0
    year_match = re.search(r"(\d+)\s*(?:\([^)]*\))?\s*godin", kazna_lower)
    if year_match:
        years = int(year_match.group(1))

    # Try to find months
    months = 0
    month_match = re.search(r"(\d+)\s*(?:\([^)]*\))?\s*mjesec", kazna_lower)
    if month_match:
        months = int(month_match.group(1))

    # Try to find days
    days = 0
    day_match = re.search(r"(\d+)\s*(?:\([^)]*\))?\s*dan", kazna_lower)
    if day_match:
        days = int(day_match.group(1))

    total_months = years * 12 + months + (days / 30.0)

    if total_months == 0:
        # Try number words
        word_to_num = {
            "jedan": 1, "dva": 2, "tri": 3, "četiri": 4, "cetiri": 4,
            "pet": 5, "šest": 6, "sest": 6, "sedam": 7, "osam": 8,
            "devet": 9, "deset": 10, "jedanaest": 11, "dvanaest": 12,
        }
        for word, num in word_to_num.items():
            if word in kazna_lower:
                if "godin" in kazna_lower:
                    total_months = num * 12
                elif "mjesec" in kazna_lower:
                    total_months = num
                break

    return round(total_months, 1)


def extract_fine_amount(novcana_kazna_text):
    """Extract monetary fine amount in EUR."""
    if not novcana_kazna_text:
        return 0.0
    # Remove non-numeric chars except . and ,
    cleaned = novcana_kazna_text.replace(",", ".")
    match = re.search(r"([\d.]+)", cleaned)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return 0.0
    return 0.0


def normalize_education(raw):
    """Normalize education level."""
    raw_lower = raw.lower() if raw else ""
    if not raw_lower:
        return "nepoznat"
    if "vss" in raw_lower or "visok" in raw_lower or "fakultet" in raw_lower or "univerzitet" in raw_lower:
        return "VSS"
    if "sss" in raw_lower or "srednj" in raw_lower:
        return "SSS"
    if "osnov" in raw_lower:
        return "osnovna"
    if "pisme" in raw_lower:
        return "pismen"
    return "nepoznat"


def count_children(proprietary, parent_tag, child_tag):
    """Count child elements under a parent tag (handles both namespaced and non-namespaced)."""
    AKN = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
    for ptag in [parent_tag, f"{AKN}{parent_tag}"]:
        parent = proprietary.find(ptag)
        if parent is not None:
            count = 0
            for ctag in [child_tag, f"{AKN}{child_tag}"]:
                count += len(parent.findall(ctag))
            return count
    return 0


def extract_defendant_count(opis):
    """Extract number of defendants from opisSlucaja text."""
    if not opis:
        return 1
    # Look for numbered defendants: "1.", "2.", "3." near names
    # Pattern: "Optuženi:" or "Okrivljen" followed by numbered list
    numbered = re.findall(r"(?:^|\s)(\d+)\s*\.\s*[A-ZŠĐČĆŽ]", opis)
    if numbered:
        nums = [int(n) for n in numbered]
        count = max(nums)
        if count >= 2:
            return count
    # Look for "zajedno" (together) or plural guilty "Krivi su"
    if re.search(r"zajedno|krivi su|obojic[ea]", opis, re.IGNORECASE):
        return 2
    return 1


def detect_confession(proprietary, opis):
    """Detect if confession/plea bargain is mentioned."""
    if opis and re.search(r"priznan|sporazum\s+o\s+priznan", opis, re.IGNORECASE):
        return "da"
    # Also check dokazi for confession reference
    AKN = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
    for dtag in ["dokazi", f"{AKN}dokazi"]:
        dokazi_el = proprietary.find(dtag)
        if dokazi_el is not None:
            for ctag in ["dokaz", f"{AKN}dokaz"]:
                for dokaz in dokazi_el.findall(ctag):
                    if dokaz.text and re.search(r"priznan", dokaz.text, re.IGNORECASE):
                        return "da"
    return "ne"


def detect_attempt(opis):
    """Detect if the crime was attempted (not completed)."""
    if not opis:
        return "ne"
    if re.search(r"pokušao|pokušala|nije\s+uspi?j?e?o|neuspješn", opis, re.IGNORECASE):
        return "da"
    return "ne"


def detect_coperpetration(opis):
    """Detect if co-perpetration/conspiracy is present."""
    if not opis:
        return "ne"
    if re.search(r"zajedno|po\s+prethodnom\s+dogovoru|saučesni|saizvršil", opis, re.IGNORECASE):
        return "da"
    return "ne"


def normalize_court(raw):
    """Normalize court name to just the city."""
    if not raw:
        return "nepoznat"
    # Known courts - extract just the city name
    court_map = {
        "podgoric": "Podgorica", "nikši": "Nikšić", "niksic": "Nikšić",
        "rožaj": "Rožaje", "rozaj": "Rožaje", "berana": "Berane",
        "bar": "Bar",  "kotor": "Kotor", "cetinj": "Cetinje",
        "herceg": "Herceg Novi", "bijel": "Bijelo Polje",
        "pljevlj": "Pljevlja", "plav": "Plav", "ulcinj": "Ulcinj",
        "danilovgrad": "Danilovgrad", "kolašin": "Kolašin", "kolasin": "Kolašin",
    }
    raw_lower = raw.lower()
    for key, city in court_map.items():
        if key in raw_lower:
            return city
    return raw


def parse_case(xml_path):
    """Parse a single Akomanotoso XML file and extract key facts."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"  XML parse error in {xml_path}: {e}")
        return None

    # Find proprietary element (contains extracted metadata)
    prop = root.find(".//{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}proprietary")
    if prop is None:
        # Try without namespace
        prop = root.find(".//proprietary")
    if prop is None:
        print(f"  No proprietary data in {xml_path}")
        return None

    # Extract fields - handle both namespaced and non-namespaced
    def get(tag):
        el = prop.find(tag)
        if el is None:
            el = prop.find(f"{{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}}{tag}")
        if el is not None and el.text:
            return el.text.strip()
        return ""

    sud = normalize_court(get("sud"))
    broj_predmeta = get("brojPredmeta")
    tip_krivicnog_djela = normalize_crime_type(get("tipKrivicnogDjela"))
    clan_kz = normalize_article(get("clanKZ"))
    max_iznos, ukupan_iznos, broj_transakcija = extract_amounts(prop)
    ranije_osudjivan = normalize_previously_convicted(get("ranijeOsudjivan"))
    uslovna_osuda = get("uslovnaOsuda") if get("uslovnaOsuda") else "Ne"
    vrsta_presude = normalize_verdict_type(get("vrstaPresude"))
    zaposlenost = normalize_employment(get("zaposlenost"))
    bracni_status = normalize_marital_status(get("bracniStatus"))
    kazna_text = get("kazna")
    kazna_mjeseci = extract_sentence_months(kazna_text)
    novcana_kazna = extract_fine_amount(get("novcanaKazna"))

    # New attributes
    obrazovanje = normalize_education(get("obrazovanje"))
    broj_svjedoka = count_children(prop, "svjedoci", "svjedok")
    broj_dokaza = count_children(prop, "dokazi", "dokaz")

    opis_el = prop.find("opisSlucaja") or prop.find("{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}opisSlucaja")
    opis = opis_el.text.strip() if opis_el is not None and opis_el.text else ""

    broj_okrivljenih = extract_defendant_count(opis)
    priznanje = detect_confession(prop, opis)
    pokusaj = detect_attempt(opis)
    saizvrsilastvo = detect_coperpetration(opis)

    case = {
        "sud": sud,
        "brojPredmeta": broj_predmeta,
        "tipKrivicnogDjela": tip_krivicnog_djela,
        "clanKZ": clan_kz,
        "iznos": max_iznos,
        "ranijeOsudjivan": ranije_osudjivan,
        "uslovnaOsuda": uslovna_osuda,
        "vrstaPresude": vrsta_presude,
        "zaposlenost": zaposlenost,
        "bracniStatus": bracni_status,
        "kaznaUMjesecima": kazna_mjeseci,
        "novcanaKazna": novcana_kazna,
        "obrazovanje": obrazovanje,
        "ukupanIznos": ukupan_iznos,
        "brojTransakcija": broj_transakcija,
        "brojOkrivljenih": broj_okrivljenih,
        "brojSvjedoka": broj_svjedoka,
        "brojDokaza": broj_dokaza,
        "priznanje": priznanje,
        "pokusaj": pokusaj,
        "saizvrsilastvo": saizvrsilastvo,
    }
    return case


def main():
    print(f"Scanning XML files in: {XML_DIR}")
    xml_files = sorted([f for f in os.listdir(XML_DIR) if f.endswith(".xml")])
    print(f"Found {len(xml_files)} XML files")

    cases = []
    for xml_file in xml_files:
        xml_path = os.path.join(XML_DIR, xml_file)
        case = parse_case(xml_path)
        if case:
            cases.append(case)
        else:
            print(f"  Skipped: {xml_file}")

    print(f"\nExtracted {len(cases)} cases")

    # Assign sequential IDs
    for i, case in enumerate(cases):
        case["id"] = i

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    # Write CSV
    fieldnames = [
        "id", "sud", "brojPredmeta", "tipKrivicnogDjela", "clanKZ",
        "iznos", "ranijeOsudjivan", "uslovnaOsuda", "vrstaPresude",
        "zaposlenost", "bracniStatus", "kaznaUMjesecima", "novcanaKazna",
        "obrazovanje", "ukupanIznos", "brojTransakcija", "brojOkrivljenih",
        "brojSvjedoka", "brojDokaza", "priznanje", "pokusaj", "saizvrsilastvo"
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        # Write header as comment
        f.write("# " + ";".join(fieldnames) + "\n")
        for case in cases:
            writer.writerow(case)

    print(f"CSV written to: {OUTPUT_CSV}")

    # Print summary statistics
    crime_types = {}
    articles = {}
    verdicts = {}
    for c in cases:
        crime_types[c["tipKrivicnogDjela"]] = crime_types.get(c["tipKrivicnogDjela"], 0) + 1
        articles[c["clanKZ"]] = articles.get(c["clanKZ"], 0) + 1
        verdicts[c["vrstaPresude"]] = verdicts.get(c["vrstaPresude"], 0) + 1

    print("\n--- Statistics ---")
    print("Crime types:", crime_types)
    print("Articles:", articles)
    print("Verdict types:", verdicts)


if __name__ == "__main__":
    main()
