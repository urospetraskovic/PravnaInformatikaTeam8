"""
Mobbing Criminal Cases Data Processor
Project: Pravna Informatika Team 8
Purpose: Extract and structure data from court verdicts for CBR system
"""

import csv
import json
from datetime import datetime
from typing import Dict, List, Any

class MobbingCaseProcessor:
    """Process mobbing cases from court verdicts"""
    
    def __init__(self):
        self.cases = []
        self.articles_registry = {
            "Article 228": "Threatening or Humiliating",
            "Article 229": "Harassment, Threats, Intimidation",
            "Article 131": "Persecution",
            "Article 289": "Light Bodily Injury",
            "Article 290": "Medium Bodily Injury",
            "Article 297": "Serious Bodily Injury",
            "Article 55": "Mitigating/Aggravating Circumstances"
        }
    
    def create_case_entry(self) -> Dict[str, Any]:
        """Template for a single case entry"""
        return {
            "case_id": None,
            "court": None,
            "verdict_date": None,
            "perpetrator_name": None,
            "victim_name": None,
            "perpetrator_type": None,  # employer, supervisor, colleague, other
            "harassment_type": None,   # verbal, threats, discrimination, physical, psychological
            "duration": None,           # single, repeated
            "workplace_type": None,     # private, public, state
            "power_dynamic": None,      # superior-subordinate, peer, mob
            "witnesses": None,          # yes/no
            "evidence_type": None,      # documentation, testimony, recordings, etc
            "prior_incidents": None,    # first offense, repeat
            "physical_harm": None,      # none, minor, serious
            "psychological_harm": None, # mild, moderate, severe
            "articles_violated": [],    # list of articles
            "sentence_type": None,      # fine, imprisonment, conditional
            "sentence_duration": None,  # in months/years
            "fine_amount": None,        # in EUR/CZK
            "aggravating_factors": [],  # list
            "mitigating_factors": [],   # list
            "verdict_summary": None,    # short text description
        }
    
    def add_case_from_verdict(self, verdict_data: Dict) -> bool:
        """
        Add a case from parsed verdict data
        
        Args:
            verdict_data: Dictionary with extracted verdict information
        
        Returns:
            Boolean indicating success
        """
        try:
            case = self.create_case_entry()
            case.update(verdict_data)
            self.cases.append(case)
            return True
        except Exception as e:
            print(f"Error adding case: {e}")
            return False
    
    def export_to_csv(self, filename: str = "mobbing_cases.csv") -> bool:
        """Export cases to CSV for CBR system"""
        try:
            if not self.cases:
                print("No cases to export")
                return False
            
            # Flatten complex fields for CSV
            flattened_cases = []
            for case in self.cases:
                flat_case = case.copy()
                flat_case["articles_violated"] = "|".join(flat_case["articles_violated"])
                flat_case["aggravating_factors"] = "|".join(flat_case["aggravating_factors"])
                flat_case["mitigating_factors"] = "|".join(flat_case["mitigating_factors"])
                flattened_cases.append(flat_case)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = flattened_cases[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                writer.writerows(flattened_cases)
            
            print(f"Cases exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_json(self, filename: str = "mobbing_cases.json") -> bool:
        """Export cases to JSON format"""
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(self.cases, jsonfile, indent=2, ensure_ascii=False)
            print(f"Cases exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Generate statistics about the cases"""
        if not self.cases:
            return {}
        
        stats = {
            "total_cases": len(self.cases),
            "articles_frequency": {},
            "sentence_types": {},
            "harassment_types": {},
            "perpetrator_types": {},
            "workplace_types": {},
            "power_dynamics": {}
        }
        
        for case in self.cases:
            # Count articles
            for article in case.get("articles_violated", []):
                stats["articles_frequency"][article] = stats["articles_frequency"].get(article, 0) + 1
            
            # Count sentence types
            sent_type = case.get("sentence_type")
            if sent_type:
                stats["sentence_types"][sent_type] = stats["sentence_types"].get(sent_type, 0) + 1
            
            # Count harassment types
            harass_type = case.get("harassment_type")
            if harass_type:
                stats["harassment_types"][harass_type] = stats["harassment_types"].get(harass_type, 0) + 1
            
            # Count perpetrator types
            perp_type = case.get("perpetrator_type")
            if perp_type:
                stats["perpetrator_types"][perp_type] = stats["perpetrator_types"].get(perp_type, 0) + 1
            
            # Count workplace types
            work_type = case.get("workplace_type")
            if work_type:
                stats["workplace_types"][work_type] = stats["workplace_types"].get(work_type, 0) + 1
            
            # Count power dynamics
            power = case.get("power_dynamic")
            if power:
                stats["power_dynamics"][power] = stats["power_dynamics"].get(power, 0) + 1
        
        return stats
    
    def print_summary(self):
        """Print a summary of all cases"""
        if not self.cases:
            print("No cases loaded")
            return
        
        print("\n" + "="*80)
        print(f"MOBBING CASES SUMMARY - Total: {len(self.cases)} cases")
        print("="*80)
        
        for i, case in enumerate(self.cases, 1):
            print(f"\n[{i}] {case['case_id']} - {case['court']}")
            print(f"    Date: {case['verdict_date']}")
            print(f"    Perpetrator: {case['perpetrator_name']} ({case['perpetrator_type']})")
            print(f"    Victim: {case['victim_name']}")
            print(f"    Type: {case['harassment_type']}")
            print(f"    Articles: {', '.join(case['articles_violated'])}")
            print(f"    Sentence: {case['sentence_type']} - {case['sentence_duration']}")
            print(f"    Summary: {case['verdict_summary'][:100]}..." if case['verdict_summary'] else "    Summary: N/A")


if __name__ == "__main__":
    # Example usage
    processor = MobbingCaseProcessor()
    
    # Example case entry
    example_case = {
        "case_id": "K 22/2022",
        "court": "Osnovni sud u Podgorici",
        "verdict_date": "2023-05-16",
        "perpetrator_name": "Example Perpetrator",
        "victim_name": "Example Victim",
        "perpetrator_type": "supervisor",
        "harassment_type": "verbal",
        "duration": "repeated",
        "workplace_type": "private",
        "power_dynamic": "superior-subordinate",
        "witnesses": "yes",
        "evidence_type": "testimony, documentation",
        "prior_incidents": "no",
        "physical_harm": "none",
        "psychological_harm": "moderate",
        "articles_violated": ["Article 229", "Article 55"],
        "sentence_type": "fine",
        "sentence_duration": None,
        "fine_amount": "500 EUR",
        "aggravating_factors": ["Abuse of authority"],
        "mitigating_factors": [],
        "verdict_summary": "Example verdict summary text goes here..."
    }
    
    # Add the example case
    processor.add_case_from_verdict(example_case)
    
    # Print summary
    processor.print_summary()
    
    # Export
    processor.export_to_json()
    processor.export_to_csv()
