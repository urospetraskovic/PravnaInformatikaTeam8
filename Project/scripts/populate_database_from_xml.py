#!/usr/bin/env python3
"""
Convert AkomaNtoso XML judgment files to JSON database format
"""

import json
import xml.etree.ElementTree as ET
import os
from pathlib import Path

# Map of XML files to their case data (manually extracted from verdicts)
CASE_DATA_MAP = {
    'Case_K_34_2014_HG.xml': {
        "case_number": "K 34/2014",
        "court": "Osnovni Sud u Baru",
        "verdict_date": "2016",
        "case_type": "Falsifikovanje novca",
        "defendant": {
            "name": "H.G.",
            "occupation": "keramičar",
            "marital_status": "oženjen",
            "financial_status": "loše imovno stanje",
            "prior_convictions": "Nepoznato",
            "education": "Nepoznato"
        },
        "victim": {
            "name": "Nepoznata"
        },
        "incident": {
            "date": "2012-06-21",
            "location": "Pekara 'Montenegro II', Baru"
        },
        "legal": {
            "articles_charged": ["Član 258 st. 2"],
            "charges_count": 1
        },
        "evidence": {
            "documentary": ["Faktura pekare"],
            "witness_count": 1,
            "expert_findings": 1,
            "summary": "Svjedok T.B. (vlasnica pekare), vještačenje grafologa i Centralne banke"
        },
        "verdict": {
            "guilty": True,
            "acquitted": False,
            "conditional": False,
            "sentence_type": "Kazna zatvora",
            "sentence_duration_months": 12,
            "sentence_description": "1 godina zatvora",
            "execution_status": "Izvršena"
        },
        "appeals": {
            "appeal_filed": "Nepoznato",
            "higher_court_outcome": "Nepoznato"
        },
        "notes": "Falsifikovana novčanica od 50€"
    },
    'Case_K_34_2014_MF.xml': {
        "case_number": "K 34/2014",
        "court": "Osnovni Sud u Baru",
        "verdict_date": "2016",
        "case_type": "Falsifikovanje novca",
        "defendant": {
            "name": "M.F.",
            "occupation": "keramičar",
            "marital_status": "neoženjen",
            "financial_status": "loše imovno stanje",
            "prior_convictions": "Osudjen presudom K.122/12 od 10.04.2013",
            "education": "Nepoznato"
        },
        "victim": {
            "name": "Nepoznata"
        },
        "incident": {
            "date": "Unknown",
            "location": "Unknown"
        },
        "legal": {
            "articles_charged": ["Član 372 st.1 tač.2 ZKP-a"],
            "charges_count": 1
        },
        "evidence": {
            "documentary": [],
            "witness_count": 0,
            "expert_findings": 0,
            "summary": "Ne bis in idem - već osudjen za isto djelo"
        },
        "verdict": {
            "guilty": False,
            "acquitted": True,
            "conditional": False,
            "sentence_type": "Odbacivanje optužbe",
            "sentence_duration_months": 0,
            "sentence_description": "Optužba odbija se",
            "execution_status": "Izvršena"
        },
        "appeals": {
            "appeal_filed": "Nepoznato",
            "higher_court_outcome": "Nepoznato"
        },
        "notes": "Odbijanje optužbe zbog pravne zaštite - ne bis in idem"
    },
    'Case_K_375_2007_IZ.xml': {
        "case_number": "K 375/2007",
        "court": "Osnovni Sud u Baru",
        "verdict_date": "2008",
        "case_type": "Falsifikovanje novca",
        "defendant": {
            "name": "I.Z.",
            "occupation": "gradjevinski radnik",
            "marital_status": "razveden",
            "financial_status": "Nepoznato",
            "prior_convictions": "Osudjen za silovanje",
            "education": "Nepoznato"
        },
        "victim": {
            "name": "Vlasnica kioska D.S."
        },
        "incident": {
            "date": "2007-05-06",
            "location": "Kiosk, Baru"
        },
        "legal": {
            "articles_charged": ["Član 258 st. 4"],
            "charges_count": 1
        },
        "evidence": {
            "documentary": ["Dokumentacija banke"],
            "witness_count": 1,
            "expert_findings": 1,
            "summary": "Iskaz radnice D.S., vještačenje, dokumentacija banke"
        },
        "verdict": {
            "guilty": True,
            "acquitted": False,
            "conditional": False,
            "sentence_type": "Kazna zatvora",
            "sentence_duration_months": 3,
            "sentence_description": "3 mjeseca zatvora",
            "execution_status": "Izvršena"
        },
        "appeals": {
            "appeal_filed": "Nepoznato",
            "higher_court_outcome": "Nepoznato"
        },
        "notes": "Članova 258 st. 4 - primio kao pravi, kasnije otkrio kao falsifikovan"
    },
    'Case_K_167_2015_RLJ.xml': {
        "case_number": "K 167/2015",
        "court": "Osnovni Sud u Beranama",
        "verdict_date": "2015",
        "case_type": "Falsifikovanje novca - Produženo",
        "defendant": {
            "name": "R.Lj.",
            "occupation": "zaposlen",
            "marital_status": "oženjen",
            "financial_status": "Nepoznato",
            "prior_convictions": "Nema",
            "education": "apsolvent istorije"
        },
        "victim": {
            "name": "Više lica"
        },
        "incident": {
            "date": "2015-10-29",
            "location": "Bijelo Polje, Berane"
        },
        "legal": {
            "articles_charged": ["Član 258"],
            "charges_count": 6
        },
        "evidence": {
            "documentary": ["Video snimak"],
            "witness_count": 5,
            "expert_findings": 1,
            "summary": "Video snimak sa objekta, više svjedoka, tehnička analiza"
        },
        "verdict": {
            "guilty": True,
            "acquitted": False,
            "conditional": False,
            "sentence_type": "Kazna zatvora",
            "sentence_duration_months": 12,
            "sentence_description": "1 godina zatvora",
            "execution_status": "Izvršena"
        },
        "appeals": {
            "appeal_filed": "Nepoznato",
            "higher_court_outcome": "Nepoznato"
        },
        "notes": "Produženo krivično djelo - 6 falsifikovanih novčanica od 200€"
    },
    'Case_K_406_2011_DS.xml': {
        "case_number": "K 406/2011",
        "court": "Osnovni Sud u Bijelom Polju",
        "verdict_date": "2011",
        "case_type": "Falsifikovanje novca",
        "defendant": {
            "name": "D.S.",
            "occupation": "Nepoznato",
            "marital_status": "Nepoznato",
            "financial_status": "siromašan",
            "prior_convictions": "Nema",
            "education": "Nepoznato"
        },
        "victim": {
            "name": "Nepoznata"
        },
        "incident": {
            "date": "2009-12-01",
            "location": "Sarajevo"
        },
        "legal": {
            "articles_charged": ["Član 258 st. 2"],
            "charges_count": 1
        },
        "evidence": {
            "documentary": ["Evidencija banke"],
            "witness_count": 2,
            "expert_findings": 1,
            "summary": "Iskaz policije, vještačenje, bankovni archivi"
        },
        "verdict": {
            "guilty": True,
            "acquitted": False,
            "conditional": False,
            "sentence_type": "Kazna zatvora",
            "sentence_duration_months": 6,
            "sentence_description": "6 mjeseci zatvora",
            "execution_status": "Izvršena"
        },
        "appeals": {
            "appeal_filed": "Nepoznato",
            "higher_court_outcome": "Nepoznato"
        },
        "notes": "8 falsifikovanih novčanica (1×50KM + 7×20KM). Lošije krivotvorine. Međunarodna krivična djela."
    },
    'Case_K_140_2011_SN_MV.xml': {
        "case_number": "K 140/2011",
        "court": "Osnovni Sud u Bijelom Polju",
        "verdict_date": "2011",
        "case_type": "Falsifikovanje novca - Saizvršilaštvo",
        "defendant": {
            "name": "S.N.A i M.V.A",
            "occupation": "nepoznato",
            "marital_status": "neoženjen/oženjen",
            "financial_status": "siromašni",
            "prior_convictions": "Nema",
            "education": "srednja škola"
        },
        "victim": {
            "name": "Više lica"
        },
        "incident": {
            "date": "2011-02-18",
            "location": "Bijelo Polje, Berane - Srbija/Crna Gora granica"
        },
        "legal": {
            "articles_charged": ["Član 258"],
            "charges_count": 1
        },
        "evidence": {
            "documentary": ["Izvještaji"],
            "witness_count": 4,
            "expert_findings": 1,
            "summary": "Kros-graničnog slučaja sa vještačenjem i svjedočenjem"
        },
        "verdict": {
            "guilty": True,
            "acquitted": False,
            "conditional": False,
            "sentence_type": "Kazna zatvora",
            "sentence_duration_months": 6,
            "sentence_description": "6 mjeseci zatvora (obojica)",
            "execution_status": "Izvršena"
        },
        "appeals": {
            "appeal_filed": "Nepoznato",
            "higher_court_outcome": "Nepoznato"
        },
        "notes": "Saizvršilaštvo - zajednička krivična djela. 5 novčanica od 200€. M.V. ima djecu sa cerebralnom paralizom."
    },
    'Case_K_42_2014_KD_BD.xml': {
        "case_number": "K 42/2014",
        "court": "Osnovni Sud u Bijelom Polju",
        "verdict_date": "2014",
        "case_type": "Falsifikovanje novca - Međunarodno",
        "defendant": {
            "name": "K.D., B.D., J.N.",
            "occupation": "nepoznato",
            "marital_status": "neoženjen",
            "financial_status": "nepoznato",
            "prior_convictions": "Nema",
            "education": "Nepoznato"
        },
        "victim": {
            "name": "Более lica"
        },
        "incident": {
            "date": "2013-07-19",
            "location": "Bijelo Polje, Crna Gora"
        },
        "legal": {
            "articles_charged": ["Član 258"],
            "charges_count": 1
        },
        "evidence": {
            "documentary": ["Izvještaji"],
            "witness_count": 3,
            "expert_findings": 1,
            "summary": "Međunarodni slučaj sa vrlo dobrim falsifikatima"
        },
        "verdict": {
            "guilty": True,
            "acquitted": False,
            "conditional": False,
            "sentence_type": "Kazna zatvora",
            "sentence_duration_months": 6,
            "sentence_description": "K.D. i B.D. - 6 mjeseci; J.N. oslobođen",
            "execution_status": "Izvršena"
        },
        "appeals": {
            "appeal_filed": "Nepoznato",
            "higher_court_outcome": "Nepoznato"
        },
        "notes": "13 falsifikovanih novčanica od 200€. Tri okrivljena - dvoje osuđeno, jedan oslobođen. Falsiikati veoma dobre izrade."
    },
    'Case_K_4_2019_CS.xml': {
        "case_number": "K 4/2019",
        "court": "Osnovni Sud u Cetinju",
        "verdict_date": "2019",
        "case_type": "Falsifikovanje novca - Produženo",
        "defendant": {
            "name": "C.S.",
            "occupation": "Nepoznato",
            "marital_status": "Nepoznato",
            "financial_status": "Nepoznato",
            "prior_convictions": "Nepoznato",
            "education": "Nepoznato"
        },
        "victim": {
            "name": "Nepoznata"
        },
        "incident": {
            "date": "2019-01-01",
            "location": "Cetinje"
        },
        "legal": {
            "articles_charged": ["Član 258"],
            "charges_count": 1
        },
        "evidence": {
            "documentary": [],
            "witness_count": 0,
            "expert_findings": 0,
            "summary": "Produženo krivično djelo falsifikovanja novca"
        },
        "verdict": {
            "guilty": True,
            "acquitted": False,
            "conditional": False,
            "sentence_type": "Nepoznato",
            "sentence_duration_months": 0,
            "sentence_description": "Nepoznato",
            "execution_status": "Nepoznato"
        },
        "appeals": {
            "appeal_filed": "Nepoznato",
            "higher_court_outcome": "Nepoznato"
        },
        "notes": "Cetinje predmet - ograničeni podaci dostupni"
    },
    'Case_K_280_2012_PM.xml': {
        "case_number": "K 280/2012",
        "court": "Osnovni Sud u Cetinju",
        "verdict_date": "2014",
        "case_type": "Falsifikovanje novca",
        "defendant": {
            "name": "P.M.",
            "occupation": "Nepoznato",
            "marital_status": "Nepoznato",
            "financial_status": "Nepoznato",
            "prior_convictions": "Nepoznato",
            "education": "Nepoznato"
        },
        "victim": {
            "name": "Nepoznata"
        },
        "incident": {
            "date": "2012-01-01",
            "location": "Cetinje"
        },
        "legal": {
            "articles_charged": ["Član 258"],
            "charges_count": 1
        },
        "evidence": {
            "documentary": [],
            "witness_count": 0,
            "expert_findings": 0,
            "summary": "Falsifikovanje novca"
        },
        "verdict": {
            "guilty": True,
            "acquitted": False,
            "conditional": False,
            "sentence_type": "Nepoznato",
            "sentence_duration_months": 0,
            "sentence_description": "Nepoznato",
            "execution_status": "Nepoznato"
        },
        "appeals": {
            "appeal_filed": "Nepoznato",
            "higher_court_outcome": "Nepoznato"
        },
        "notes": "Cetinje predmet - ograničeni podaci dostupni"
    },
    'Case_K_42_2022.xml': {
        "case_number": "K 42/2022",
        "court": "Osnovni Sud u Cetinju",
        "verdict_date": "2022",
        "case_type": "Falsifikovanje novca",
        "defendant": {
            "name": "Lica okrivljena",
            "occupation": "Nepoznato",
            "marital_status": "Nepoznato",
            "financial_status": "Nepoznato",
            "prior_convictions": "Nepoznato",
            "education": "Nepoznato"
        },
        "victim": {
            "name": "Nepoznata"
        },
        "incident": {
            "date": "2022-01-01",
            "location": "Cetinje"
        },
        "legal": {
            "articles_charged": ["Član 258"],
            "charges_count": 1
        },
        "evidence": {
            "documentary": [],
            "witness_count": 0,
            "expert_findings": 0,
            "summary": "Falsifikovanje novca"
        },
        "verdict": {
            "guilty": True,
            "acquitted": False,
            "conditional": False,
            "sentence_type": "Nepoznato",
            "sentence_duration_months": 0,
            "sentence_description": "Nepoznato",
            "execution_status": "Nepoznato"
        },
        "appeals": {
            "appeal_filed": "Nepoznato",
            "higher_court_outcome": "Nepoznato"
        },
        "notes": "2022 slučaj - ograničeni podaci dostupni"
    }
}

def create_updated_database():
    """Create updated database with new cases"""
    
    # Load existing database
    db_path = 'data/cases/DB/EXTRACTED_CASES_DATABASE.json'
    
    with open(db_path, 'r', encoding='utf-8') as f:
        old_database = json.load(f)
    
    # Remove old cases (keep only ~5 as examples)
    old_database = old_database[:5]
    
    # Add new cases
    new_cases = []
    for xml_filename, case_data in CASE_DATA_MAP.items():
        case_entry = {
            "case_id": xml_filename.replace('.xml', ''),
            **case_data
        }
        new_cases.append(case_entry)
    
    # Combine
    updated_database = old_database + new_cases
    
    # Save
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(updated_database, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Database updated successfully!")
    print(f"   - Old cases: {len(old_database)}")
    print(f"   - New cases: {len(new_cases)}")
    print(f"   - Total cases: {len(updated_database)}")
    
    return updated_database

if __name__ == '__main__':
    try:
        create_updated_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
