#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate proper database entries for the three falsification verdicts
"""

import json
import csv

# Define the three cases with manually extracted key data
CASES = [
    {
        "case_id": "Case_K_34_2014",
        "case_number": "K 34/2014",
        "court": "Osnovni Sud u Baru",
        "verdict_date": "2016-07-06",
        "case_type": "Falsifikovanje novca",
        "defendant": {
            "name": "H. G.",
            "occupation": "Keramičar",
            "marital_status": "Married",
            "education": "Osnovne škole",
            "financial_status": "Poor",
            "prior_convictions": "No"
        },
        "victim": {
            "name": "Unknown",
            "type": "General (currency circulation)"
        },
        "incident": {
            "date": "2012-06-21",
            "location": "Pekara Montenegro II, Čeluga, Bar",
            "description": "Placed counterfeit 50 EUR note in currency circulation while paying for pizza"
        },
        "applicable_articles": ["Član 258 st. 2 KZ"],
        "evidence": [
            "Counterfeit 50 EUR banknote (serial X-)",
            "Witness testimony",
            "Documentary evidence from store"
        ],
        "sentence": {
            "decision": "Guilty",
            "type": "Prison",
            "duration": "1 year",
            "duration_months": 12
        },
        "evidence_summary": "Counterfeit 50 EUR note found in store transaction",
        "additional_facts": "Material measure of security: Seizure of one counterfeit 50 EUR banknote; Court costs: 952 EUR; Court fee: 30 EUR"
    },
    {
        "case_id": "Case_K_406_2011",
        "case_number": "K 406/2011",
        "court": "Osnovni Sud u Bijelom Polju",
        "verdict_date": "2011-11-24",
        "case_type": "Falsifikovanje novca",
        "defendant": {
            "name": "D.S.",
            "occupation": "Unknown",
            "marital_status": "Married",
            "education": "Unknown",
            "financial_status": "Unknown",
            "prior_convictions": "Yes"
        },
        "victim": {
            "name": "Unknown",
            "type": "General (currency circulation)"
        },
        "incident": {
            "date": "2009-12-18",
            "location": "Sarajevo",
            "description": "Possessed counterfeit money during police stop and discarded notes"
        },
        "applicable_articles": ["Član 258 st. 2 KZ"],
        "evidence": [
            "Witness testimony from MUP officers B.A. and U.S.",
            "Confirmation of temporary seizure of items",
            "Expert findings on counterfeit notes (8 notes total)",
            "Forensic examination of counterfeit currency"
        ],
        "sentence": {
            "decision": "Guilty",
            "type": "Prison",
            "duration": "6 months",
            "duration_months": 6
        },
        "evidence_summary": "6 counterfeit 20 KM notes and 1 counterfeit 50 KM note seized; Expert analysis confirmed counterfeits; Witness officers testified defendant discarded notes during police stop",
        "additional_facts": "Material measure of security: Seizure of counterfeit notes; Court fee: 30 EUR; Defendant is known offender"
    },
    {
        "case_id": "Case_K_42_2022",
        "case_number": "K 42/2022",
        "court": "Osnovni Sud u Kotoru",
        "verdict_date": "2022-04-04",
        "case_type": "Falsifikovanje novca",
        "defendant": {
            "name": "T Š",
            "occupation": "Driver",
            "marital_status": "Married",
            "education": "OŠ (Primary school)",
            "financial_status": "Medium",
            "prior_convictions": "Yes (10 months in 2017)"
        },
        "victim": {
            "name": "Unknown",
            "type": "General (currency circulation)"
        },
        "incident": {
            "date": "2022-01-23",
            "location": "Trafika Ts, Bar",
            "description": "Put counterfeit 50 EUR note into circulation at a shop counter to purchase cigarettes"
        },
        "applicable_articles": ["Član 258 st. 4 KZ"],
        "evidence": [
            "Witness testimony from shop employee N.D.",
            "Central Bank technical analysis (Report 36, 28.01.2022)",
            "Confirmation of temporarily seized money (24.01.2022)",
            "Defendant's confession and detailed explanation",
            "Criminal record from Ministry of Justice"
        ],
        "sentence": {
            "decision": "Guilty",
            "type": "Public work",
            "duration": "120 hours (3 months)",
            "duration_months": 3,
            "additional_condition": "If not completed: 1 month prison per 60 hours"
        },
        "evidence_summary": "Central Bank confirmed 50 EUR counterfeit note (poor quality, identifiable as fake); Note passed through store cash count; Defendant admitted guilt and explained receiving notes from brother-in-law from car sale",
        "additional_facts": "Material measure of security: Seizure of 50 EUR counterfeit note; Court fee: 30 EUR; Defendant cooperated and pleaded guilty; Previously sentenced for Article 300 KZ (attempted theft or similar offense)"
    }
]

def export_json(filename):
    """Export to JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(CASES, f, ensure_ascii=False, indent=2)
    print(f"✅ Exported to {filename}")

def export_csv(filename):
    """Export to CSV"""
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            "case_id", "case_number", "court", "verdict_date", "case_type",
            "defendant_name", "defendant_occupation", "defendant_marital", 
            "defendant_education", "defendant_financial", "defendant_convictions",
            "incident_date", "incident_location", "incident_description",
            "articles", "sentence_decision", "sentence_type", "sentence_duration",
            "evidence_count", "evidence_summary"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        
        for case in CASES:
            writer.writerow({
                "case_id": case["case_id"],
                "case_number": case["case_number"],
                "court": case["court"],
                "verdict_date": case["verdict_date"],
                "case_type": case["case_type"],
                "defendant_name": case["defendant"]["name"],
                "defendant_occupation": case["defendant"]["occupation"],
                "defendant_marital": case["defendant"]["marital_status"],
                "defendant_education": case["defendant"]["education"],
                "defendant_financial": case["defendant"]["financial_status"],
                "defendant_convictions": case["defendant"]["prior_convictions"],
                "incident_date": case["incident"]["date"],
                "incident_location": case["incident"]["location"],
                "incident_description": case["incident"]["description"],
                "articles": "|".join(case["applicable_articles"]),
                "sentence_decision": case["sentence"]["decision"],
                "sentence_type": case["sentence"]["type"],
                "sentence_duration": case["sentence"]["duration"],
                "evidence_count": len(case["evidence"]),
                "evidence_summary": case["evidence_summary"]
            })
    print(f"✅ Exported to {filename}")

if __name__ == "__main__":
    print("✅ Extracted 3 falsification cases\n")
    for case in CASES:
        print(f"📋 {case['case_number']} - {case['court']}")
        print(f"   Defendant: {case['defendant']['name']}")
        print(f"   Verdict: {case['sentence']['decision']} - {case['sentence']['type']} ({case['sentence']['duration']})")
        print(f"   Articles: {', '.join(case['applicable_articles'])}")
        print(f"   Evidence: {len(case['evidence'])} types\n")
    
    export_json(r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\extracted_verdicts.json")
    export_csv(r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\extracted_verdicts.csv")
