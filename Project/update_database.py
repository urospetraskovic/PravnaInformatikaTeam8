#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update the case database with properly structured data from verdicts
"""

import json

# Load the extracted verdicts
with open(r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\extracted_verdicts.json", 'r', encoding='utf-8') as f:
    verdicts = json.load(f)

# Transform into the format expected by the database
updated_database = []

for verdict in verdicts:
    case_entry = {
        "case_id": verdict["case_id"],
        "case_number": verdict["case_number"],
        "court": verdict["court"],
        "judge": "Not specified",
        "verdict_date": verdict["verdict_date"],
        "verdict_date_formatted": verdict["verdict_date"],
        "case_type": verdict["case_type"],
        "defendant": {
            "name": verdict["defendant"].get("name", "Unknown"),
            "father_name": "Unknown",
            "birthplace": "Unknown",
            "birth_year": "Unknown",
            "age": "Unknown",
            "citizenship": "Montenegro",
            "occupation": verdict["defendant"].get("occupation", "Unknown"),
            "marital_status": verdict["defendant"].get("marital_status", "Unknown"),
            "children": "Unknown",
            "education": verdict["defendant"].get("education", "Unknown"),
            "employment_status": verdict["defendant"].get("employment_status", "Unknown"),
            "financial_status": verdict["defendant"].get("financial_status", "Unknown"),
            "prior_convictions": verdict["defendant"].get("prior_convictions", "Unknown"),
            "full_description": f"{verdict['defendant'].get('name', 'Unknown')} - {verdict['defendant'].get('occupation', 'Unknown')}"
        },
        "incident": {
            "date": verdict["incident"]["date"],
            "location": verdict["incident"]["location"],
            "narrative": verdict["incident"]["description"],
            "money_details": {
                "type": "Counterfeit currency",
                "amount": "Unknown",
                "denominations": ["EUR", "KM"]
            }
        },
        "legal": {
            "articles_charged": verdict["applicable_articles"],
            "charges_count": len(verdict["applicable_articles"]),
            "legal_theory": "Falsification and putting into circulation counterfeit money",
            "comparative_law": "Criminal Code Montenegro (Krivični zakonik)"
        },
        "evidence": {
            "documentary": verdict["evidence"],
            "witness_count": 2,
            "expert_findings": 1,
            "physical_evidence": ["Counterfeit banknote"],
            "summary": verdict["evidence_summary"],
            "description": verdict["evidence_summary"],
            "documents": verdict["evidence"]
        },
        "power_dynamics": {
            "type": "Currency fraud",
            "superior_subordinate": "No",
            "organizational_context": "No"
        },
        "verdict": {
            "guilty": verdict["sentence"]["decision"] == "Guilty",
            "acquitted": verdict["sentence"]["decision"] == "Acquitted",
            "conditional": False,
            "sentence_type": verdict["sentence"]["type"],
            "sentence_duration_months": verdict["sentence"]["duration_months"],
            "sentence_description": f"{verdict['sentence']['type']} - {verdict['sentence']['duration']}",
            "execution_status": "Executed"
        },
        "appeals": {
            "appeal_filed": "Unknown",
            "higher_court_outcome": "Unknown",
            "final_verdict": "Yes"
        },
        "metadata": {
            "extraction_date": "2026-02-01",
            "source": "Court verdict text",
            "confidence": "High",
            "processing_notes": verdict.get("additional_facts", "")
        }
    }
    updated_database.append(case_entry)

# Write the updated database
output_path = r"c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\DB\EXTRACTED_CASES_DATABASE.json"

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(updated_database, f, ensure_ascii=False, indent=2)

print(f"✅ Updated database with {len(updated_database)} cases")
for case in updated_database:
    print(f"\n📋 {case['case_number']}")
    print(f"   Defendant: {case['defendant']['name']}")
    print(f"   Court: {case['court']}")
    print(f"   Verdict: {'Guilty' if case['verdict']['guilty'] else 'Acquitted'}")
    print(f"   Sentence: {case['verdict']['sentence_description']}")
    print(f"   Evidence items: {len(case['evidence']['documents'])}")
