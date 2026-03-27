#!/usr/bin/env python3
"""
Sync exact charged legal article references (cl. 258/260 + stav)
from archive TXT judgments into Akoma Ntoso XML files.

This updates:
- <clanKZ>...</clanKZ> in <proprietary>
- Optional legal-basis parenthetical in <conclusions> text, when present
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
XML_DIR = PROJECT_ROOT / "data" / "cases" / "akomantoso"
TXT_DIRS = [
    PROJECT_ROOT / "archive" / "presude" / "falsifikovanje novca",
    PROJECT_ROOT / "archive" / "presude" / "falsifikovanje i zloupotreba kreditnih kartica i kartica za bezgotovinsko pla\u0107anje",
]

CANONICAL_LABEL = "{article}.{stav}"


def read_text_with_fallback(path: Path) -> str:
    for enc in ("utf-8", "cp1250", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="ignore")


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or " ").strip()


def parse_xml_identity(xml_name: str):
    match = re.match(r"^K\s+(\d+)_(\d{4})\.xml$", xml_name, flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def build_txt_index():
    index = {}

    for txt_dir in TXT_DIRS:
        if not txt_dir.exists():
            continue
        for txt_path in txt_dir.glob("K *.txt"):
            stem = txt_path.stem.strip()
            match = re.match(r"^K\s*(\d{5,})$", stem, flags=re.IGNORECASE)
            if not match:
                continue

            digits = match.group(1)
            case_num = int(digits[:-4])
            year = int(digits[-4:])
            if year < 2000 or year > 2100:
                continue

            index[(case_num, year)] = txt_path

    return index


def extract_charged_article_and_stav(txt: str):
    # OCR/typing tolerance for cl./clan/st./stav and spacing/punctuation.
    low_noise = normalize_space(txt[:14000])

    targeted_patterns = [
        r"zbog\s+krivicnog\s+djela.{0,220}?iz\s+clana\s*(258|260)\s*[.,]?\s*stav\s*(\d{1,2})",
        r"zbog\s+krivicnog\s+djela.{0,220}?iz\s+cl\.?\s*(258|260)\s*[.,]?\s*st\.?\s*(\d{1,2})",
        r"zbog\s+krivicnog\s+djela.{0,220}?cl\.?\s*(258|260)\s*[.,]?\s*(?:st\.?|stav)\s*(\d{1,2})",
    ]

    normalized = (
        low_noise.replace("\u010d", "c")
        .replace("\u0107", "c")
        .replace("\u0161", "s")
        .replace("\u017e", "z")
        .replace("\u0111", "d")
    )

    for pattern in targeted_patterns:
        match = re.search(pattern, normalized, flags=re.IGNORECASE)
        if match:
            article = int(match.group(1))
            stav = int(match.group(2))
            return article, stav

    generic_pattern = re.compile(
        r"(?:cl\.?|clana)\s*(258|260)\s*[.,]?\s*(?:st\.?|stav)\s*(\d{1,2})",
        flags=re.IGNORECASE,
    )

    for match in generic_pattern.finditer(normalized):
        before = normalized[max(0, match.start() - 80):match.start()]
        if "mjera bezbjednosti" in before or "na osnovu" in before:
            continue
        article = int(match.group(1))
        stav = int(match.group(2))
        return article, stav

    return None


def replace_or_insert_clan_kz(xml_content: str, canonical_ref: str):
    escaped_ref = canonical_ref

    if re.search(r"<clanKZ>.*?</clanKZ>", xml_content, flags=re.DOTALL):
        updated = re.sub(
            r"<clanKZ>.*?</clanKZ>",
            f"<clanKZ>{escaped_ref}</clanKZ>",
            xml_content,
            count=1,
            flags=re.DOTALL,
        )
        return updated

    insertion = f"        <clanKZ>{escaped_ref}</clanKZ>\n"
    if "</tipKrivicnogDjela>" in xml_content:
        return xml_content.replace("</tipKrivicnogDjela>", f"</tipKrivicnogDjela>\n{insertion}", 1)
    if "</proprietary>" in xml_content:
        return xml_content.replace("</proprietary>", f"{insertion}      </proprietary>", 1)
    return xml_content


def update_conclusions_reference(xml_content: str, canonical_ref: str):
    # Optional consistency update: (... Krivicnog zakonika Crne Gore)
    pattern = re.compile(
        r"\((?:\u010dl\.?|\u010dlan|cl\.?|clan)\s*\d{2,3}(?:\s*(?:st\.?|stav)\s*\d{1,2})?\s+Krivi\u010dnog\s+zakonika\s+Crne\s+Gore\)",
        flags=re.IGNORECASE,
    )
    replacement = f"({canonical_ref} Krivi\u010dnog zakonika Crne Gore)"
    return pattern.sub(replacement, xml_content, count=1)


def main():
    txt_index = build_txt_index()
    xml_files = sorted(XML_DIR.glob("K *_*.xml"))

    total_xml = 0
    matched_txt = 0
    extracted = 0
    updated = 0
    skipped_no_txt = 0
    skipped_no_ref = 0

    for xml_path in xml_files:
        total_xml += 1
        identity = parse_xml_identity(xml_path.name)
        if not identity:
            continue

        txt_path = txt_index.get(identity)
        if not txt_path:
            skipped_no_txt += 1
            continue
        matched_txt += 1

        txt_content = read_text_with_fallback(txt_path)
        extracted_ref = extract_charged_article_and_stav(txt_content)
        if not extracted_ref:
            skipped_no_ref += 1
            continue

        extracted += 1
        article, stav = extracted_ref
        canonical_ref = CANONICAL_LABEL.format(article=article, stav=stav)

        original = read_text_with_fallback(xml_path)
        new_content = replace_or_insert_clan_kz(original, canonical_ref)
        new_content = update_conclusions_reference(new_content, canonical_ref)

        if new_content != original:
            xml_path.write_text(new_content, encoding="utf-8")
            updated += 1

    print("=== sync_articles_from_presude.py ===")
    print(f"XML files scanned: {total_xml}")
    print(f"Matched TXT files: {matched_txt}")
    print(f"Extracted exact article+stav: {extracted}")
    print(f"Updated XML files: {updated}")
    print(f"Skipped (no TXT): {skipped_no_txt}")
    print(f"Skipped (no extracted ref): {skipped_no_ref}")


if __name__ == "__main__":
    main()
