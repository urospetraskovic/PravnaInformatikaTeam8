#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Montenegrin Legal Case Reasoning Engine
Provides rule-based reasoning for court cases
"""

import sys
import json
import argparse
from pathlib import Path
import re
import io

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def extract_case_info(case_file):
    """Extract relevant info from case XML file"""
    try:
        content = Path(case_file).read_text(encoding='utf-8')
        
        # Extract basic info
        case_info = {}
        
        # Extract case number from brojPredmeta
        match = re.search(r'<brojPredmeta>([^<]+)</brojPredmeta>', content)
        if match:
            case_info['case_number'] = match.group(1).strip()
        
        # Extract verdict from vrstaPresude
        match = re.search(r'<vrstaPresude>([^<]+)</vrstaPresude>', content)
        if match:
            case_info['verdict'] = match.group(1).strip()
        
        # Extract articles - try multiple patterns
        articles = []
        
        # Pattern 1: <clanKZ>чl. 260 st. 2</clanKZ>
        for match in re.finditer(r'<clanKZ>([^<]+)</clanKZ>', content):
            article_text = match.group(1).strip()
            if article_text and article_text not in articles:
                articles.append(article_text)
        
        # Pattern 2: Look in articles section
        articles_match = re.search(r'<articles>(.*?)</articles>', content, re.DOTALL)
        if articles_match:
            for match in re.finditer(r'<article[^>]*>([^<]*čl\.[^<]*)</article>', articles_match.group(1)):
                article_text = match.group(1).strip()
                if article_text and article_text not in articles:
                    articles.append(article_text)
        
        case_info['articles'] = articles if articles else []
        
        # Extract sentence from kazna
        match = re.search(r'<kazna>([^<]+)</kazna>', content)
        if match:
            case_info['sentence'] = match.group(1).strip()
            
        return case_info
    except Exception as e:
        return {"error": str(e)}

def reason_about_case(case_file=None, facts=None):
    """
    Perform rule-based reasoning on a case or facts
    
    Args:
        case_file: Path to XML case file
        facts: JSON string containing case facts
    
    Returns:
        Dictionary with reasoning results
    """
    try:
        result = {
            "status": "success",
            "reasoning": "Rule-based reasoning system ready",
            "violated_rules": [],
            "applicable_articles": [],
            "penalty_range": {"min": "N/A", "max": "N/A"},
            "mitigating_factors": [],
            "aggravating_factors": [],
            "precedents": []
        }
        
        if case_file:
            case_info = extract_case_info(case_file)
            result["case_info"] = case_info
            result["reasoning"] = f"Analizirani slučaj: {case_info.get('case_number', 'Nepoznato')}"
            
            # Rule-based analysis based on verdict and articles
            if case_info.get('verdict'):
                verdict = case_info['verdict'].lower()
                articles = case_info.get('articles', [])
                
                if 'osud' in verdict or 'kriv' in verdict:
                    result["violated_rules"].append("Utvrđena krivična odgovornost")
                    result["applicable_articles"] = articles
                    
                    # Determine penalty range based on article
                    if articles:
                        result["penalty_range"] = {
                            "min": "3 mjeseca",
                            "max": "10 godina"
                        }
                        result["aggravating_factors"].append("Dokazana izvršenja krivičnog djela")
                
                if 'uslovna' in verdict:
                    result["mitigating_factors"].append("Uslovna osuda - okolnosti u prilog okrivljenom")
                
                if 'opomena' in verdict:
                    result["reasoning"] = "Sudska opomena - posebna vrsta presude"
                    result["penalty_range"] = {"min": "Upozorenje", "max": "Upozorenje"}
                
                if 'oslobod' in verdict:
                    result["verdict_analysis"] = "Okrivljeni oslobođen krivičnog pregona - nema dokazane krivice"
                    result["reasoning"] = "Oslobađajuća presuda"
        
        if facts:
            try:
                facts_data = json.loads(facts)
                result["facts"] = facts_data
                result["reasoning"] = "Činjenice slučaja analizirane prema pravilima"
            except json.JSONDecodeError:
                result["facts"] = facts
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "reasoning": "Greška tijekom pravnog rezonovanja"
        }

def main():
    parser = argparse.ArgumentParser(
        description="Montenegrin Legal Case Reasoning Engine"
    )
    parser.add_argument('--case', help='XML case file path')
    parser.add_argument('--facts', help='JSON facts string')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    result = reason_about_case(case_file=args.case, facts=args.facts)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result)

if __name__ == '__main__':
    main()

