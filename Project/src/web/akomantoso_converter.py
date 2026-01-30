#!/usr/bin/env python3
"""
AkomaNtoso XML Converter for Montenegrin Legal Cases
Converts JSON case data to AkomaNtoso 3.0 XML format
"""

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from datetime import datetime

class AkomaNtosoConverter:
    """Converts case data to AkomaNtoso XML format"""
    
    AKOMANTOSO_NS = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0/WD17"
    XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
    
    def __init__(self):
        self.cases = []
        
    def load_cases(self, json_file):
        """Load cases from JSON file"""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.cases = json.load(f)
        print(f"Loaded {len(self.cases)} cases from {json_file}")
        
    def case_to_akomantoso(self, case):
        """Convert a single case to AkomaNtoso XML"""
        
        # Root element
        judgment = ET.Element('judgment')
        judgment.set('name', f"Case {case.get('case_number', 'Unknown')}")
        judgment.set('{http://www.w3.org/XML/1998/namespace}lang', 'sr')
        
        # Add namespace declarations
        judgment.set('xmlns', self.AKOMANTOSO_NS)
        judgment.set('xmlns:xsi', self.XSI_NS)
        judgment.set('xsi:schemaLocation', 
                    'https://docs.oasis-open.org/legaldocml/akn-core/v1.0/os/part2-specs/schemas/akomantoso30.xsd')
        
        # METADATA
        meta = self._create_metadata(case)
        judgment.append(meta)
        
        # BODY
        body = self._create_body(case)
        judgment.append(body)
        
        # CONCLUSIONS
        conclusions = ET.SubElement(judgment, 'conclusions')
        conc_p = ET.SubElement(conclusions, 'p')
        conc_p.text = self._get_conclusion_text(case)
        
        return judgment
    
    def _create_metadata(self, case):
        """Create <meta> section"""
        meta = ET.Element('meta')
        
        # IDENTIFICATION
        identification = ET.SubElement(meta, 'identification')
        identification.set('source', '#court')
        
        # FRBR Work
        frbr_work = ET.SubElement(identification, 'FRBRWork')
        self._add_element(frbr_work, 'FRBRthis', 
                         {'value': f"/akn/me/judgment/{case.get('case_id', 'unknown')}/!main"})
        self._add_element(frbr_work, 'FRBRuri', 
                         {'value': f"/akn/me/judgment/{case.get('case_id', 'unknown')}"})
        self._add_element(frbr_work, 'FRBRdate', 
                         {'date': case.get('verdict_date', '2024')})
        self._add_element(frbr_work, 'FRBRauthor', 
                         {'href': '#judge', 'as': '#judge'})
        self._add_element(frbr_work, 'FRBRcountry', {'value': 'me'})
        self._add_element(frbr_work, 'FRBRsubtype', {'value': 'judgment'})
        self._add_element(frbr_work, 'FRBRnumber', 
                         {'value': case.get('case_number', 'K 0000/00')})
        self._add_element(frbr_work, 'FRBRname', 
                         {'value': case.get('case_type', 'Judgment')})
        
        # FRBR Expression
        frbr_expr = ET.SubElement(identification, 'FRBRExpression')
        self._add_element(frbr_expr, 'FRBRthis', 
                         {'value': f"/akn/me/judgment/{case.get('case_id')}/sr@{case.get('verdict_date')}/!main"})
        self._add_element(frbr_expr, 'FRBRuri', 
                         {'value': f"/akn/me/judgment/{case.get('case_id')}/sr@{case.get('verdict_date')}"})
        self._add_element(frbr_expr, 'FRBRdate', 
                         {'date': case.get('verdict_date', '2024')})
        self._add_element(frbr_expr, 'FRBRauthor', 
                         {'href': '#court', 'as': '#issuer'})
        self._add_element(frbr_expr, 'FRBRlanguage', {'language': 'sr'})
        
        # FRBR Manifestation
        frbr_manif = ET.SubElement(identification, 'FRBRManifestation')
        self._add_element(frbr_manif, 'FRBRthis', 
                         {'value': f"/akn/me/judgment/{case.get('case_id')}/sr@{case.get('verdict_date')}/!main.xml"})
        self._add_element(frbr_manif, 'FRBRuri', 
                         {'value': f"/akn/me/judgment/{case.get('case_id')}/sr@{case.get('verdict_date')}/!main.akn"})
        self._add_element(frbr_manif, 'FRBRdate', 
                         {'date': datetime.now().strftime('%Y-%m-%d')})
        self._add_element(frbr_manif, 'FRBRauthor', 
                         {'href': '#court', 'as': '#generator'})
        self._add_element(frbr_manif, 'FRBRformat', {'value': 'xml'})
        
        # PUBLICATION
        pub = ET.SubElement(meta, 'publication')
        pub.set('name', 'court')
        pub.set('date', case.get('verdict_date', '2024'))
        pub.set('showAs', case.get('court', 'Montenegrin Court'))
        pub.set('number', case.get('case_number', 'K 0000/00'))
        
        # CLASSIFICATION
        classification = ET.SubElement(meta, 'classification')
        classification.set('source', '#court')
        keyword = ET.SubElement(classification, 'keyword')
        keyword.set('value', case.get('case_type', 'criminal').lower().replace(' ', '_'))
        keyword.set('showAs', case.get('case_type', 'Criminal Case'))
        keyword.set('dictionary', 'ME')
        
        # REFERENCES
        references = ET.SubElement(meta, 'references')
        references.set('source', '#court')
        
        # Roles
        self._add_element(references, 'TLCRole', 
                         {'eId': 'judge', 'href': '/akn/me/ontology/role/judge', 'showAs': 'Judge'})
        self._add_element(references, 'TLCRole', 
                         {'eId': 'author', 'href': '/akn/me/ontology/role/author', 'showAs': 'Author'})
        self._add_element(references, 'TLCRole', 
                         {'eId': 'issuer', 'href': '/akn/me/ontology/role/issuer', 'showAs': 'Issuer'})
        self._add_element(references, 'TLCRole', 
                         {'eId': 'generator', 'href': '/akn/me/ontology/role/generator', 'showAs': 'Generator'})
        
        # Organizations
        self._add_element(references, 'TLCOrganization', 
                         {'eId': 'court', 'href': '/akn/me/ontology/organization/court', 
                          'showAs': case.get('court', 'Montenegrin Court')})
        
        # Persons
        judge_name = case.get('judge', 'Judge Unknown')
        self._add_element(references, 'TLCPerson', 
                         {'eId': 'judge', 'href': '/akn/me/ontology/person/judge', 'showAs': judge_name})
        
        return meta
    
    def _create_body(self, case):
        """Create <body> section with chapters"""
        body = ET.Element('body')
        
        # CHAPTER I: BACKGROUND
        ch1 = self._create_chapter(1, 'BACKGROUND AND FACTS')
        
        # Section 1: Defendant
        sec1 = self._create_section('chp_1__sec_1', 1, 'Defendant Information')
        art1 = self._create_article('art_bg_1', '1.1', 'Personal Details')
        
        defendant = case.get('defendant', {})
        def_text = f"Defendant: {defendant.get('name', 'Not specified')}, "
        def_text += f"Age: {defendant.get('age', 'Unknown')}, "
        def_text += f"Occupation: {defendant.get('occupation', 'Unknown')}, "
        def_text += f"Employment: {defendant.get('employment_status', 'Unknown')}"
        
        para1 = self._create_paragraph('art_bg_1__para_1', def_text)
        art1.append(para1)
        
        # Prior convictions
        art2 = self._create_article('art_bg_2', '1.2', 'Prior Criminal Record')
        convictions = defendant.get('prior_convictions', 'Unknown')
        prior_text = f"Prior convictions: {convictions}"
        para2 = self._create_paragraph('art_bg_2__para_1', prior_text)
        art2.append(para2)
        
        sec1.append(art1)
        sec1.append(art2)
        ch1.append(sec1)
        
        # Section 2: Victim
        sec2 = self._create_section('chp_1__sec_2', 2, 'Victim Information')
        art3 = self._create_article('art_bg_3', '2.1', 'Personal Details')
        
        victim = case.get('victim', {})
        vic_text = f"Victim: {victim.get('name', 'Not specified')}, "
        vic_text += f"Relationship: {victim.get('relationship_to_defendant', 'Unknown')}, "
        vic_text += f"Workplace relation: {victim.get('workplace_relationship', 'Unknown')}"
        
        para3 = self._create_paragraph('art_bg_3__para_1', vic_text)
        art3.append(para3)
        
        # Harm
        art4 = self._create_article('art_bg_4', '2.2', 'Harm Assessment')
        harm_text = f"Physical Harm: {victim.get('harm_physical', 0)}/5, "
        harm_text += f"Psychological Harm: {victim.get('harm_psychological', 0)}/5"
        para4 = self._create_paragraph('art_bg_4__para_1', harm_text)
        art4.append(para4)
        
        sec2.append(art3)
        sec2.append(art4)
        ch1.append(sec2)
        
        # Section 3: Incident
        sec3 = self._create_section('chp_1__sec_3', 3, 'Incident Details')
        art5 = self._create_article('art_bg_5', '3.1', 'Circumstances')
        
        incident = case.get('incident', {})
        inc_text = f"Date: {incident.get('date', 'Unknown')}, "
        inc_text += f"Location: {incident.get('location', 'Unknown')}, "
        inc_text += f"Context: {incident.get('context_indicator', 'Unknown')}"
        
        para5 = self._create_paragraph('art_bg_5__para_1', inc_text)
        art5.append(para5)
        
        # Narrative
        art6 = self._create_article('art_bg_6', '3.2', 'Factual Narrative')
        narrative = incident.get('narrative', 'Not specified')
        para6 = self._create_paragraph('art_bg_6__para_1', narrative)
        art6.append(para6)
        
        sec3.append(art5)
        sec3.append(art6)
        ch1.append(sec3)
        
        body.append(ch1)
        
        # CHAPTER II: MOTIVATION
        ch2 = self._create_chapter(2, 'MOTIVATION AND LEGAL ANALYSIS')
        
        sec4 = self._create_section('chp_2__sec_1', 1, 'Articles Charged')
        art7 = self._create_article('art_mot_1', '1.1', 'Applicable Criminal Law')
        
        legal = case.get('legal', {})
        articles = ', '.join(legal.get('articles_charged', ['Article Unknown']))
        art_text = f"Charged under: {articles}"
        
        para7 = self._create_paragraph('art_mot_1__para_1', art_text)
        art7.append(para7)
        
        # Legal theory
        art8 = self._create_article('art_mot_2', '1.2', 'Legal Theory')
        theory_text = legal.get('legal_theory', 'Not specified')
        para8 = self._create_paragraph('art_mot_2__para_1', theory_text)
        art8.append(para8)
        
        sec4.append(art7)
        sec4.append(art8)
        ch2.append(sec4)
        
        # Section 2: Evidence
        sec5 = self._create_section('chp_2__sec_2', 2, 'Evidence Presented')
        art9 = self._create_article('art_mot_3', '2.1', 'Evidence Summary')
        
        evidence = case.get('evidence', {})
        evid_text = f"Witnesses: {evidence.get('witness_count', 0)}, "
        evid_text += f"Documentary evidence: {len(evidence.get('documentary', []))}, "
        evid_text += f"Expert findings: {evidence.get('expert_findings', 0)}"
        
        para9 = self._create_paragraph('art_mot_3__para_1', evid_text)
        art9.append(para9)
        
        sec5.append(art9)
        ch2.append(sec5)
        
        body.append(ch2)
        
        # CHAPTER III: DECISION
        ch3 = self._create_chapter(3, 'COURT DECISION')
        
        sec6 = self._create_section('chp_3__sec_1', 1, 'Verdict')
        art10 = self._create_article('art_dec_1', '1.1', 'Finding')
        
        verdict = case.get('verdict', {})
        if verdict.get('guilty'):
            verdict_text = "THE DEFENDANT IS FOUND GUILTY"
        elif verdict.get('acquitted'):
            verdict_text = "THE DEFENDANT IS ACQUITTED"
        else:
            verdict_text = "CONDITIONAL VERDICT"
        
        para10 = self._create_paragraph('art_dec_1__para_1', verdict_text)
        art10.append(para10)
        
        sec6.append(art10)
        ch3.append(sec6)
        
        # Section 2: Sentence
        sec7 = self._create_section('chp_3__sec_2', 2, 'Sentence')
        art11 = self._create_article('art_dec_2', '2.1', 'Imposed Penalty')
        
        sentence = f"{verdict.get('sentence_type', 'Unknown')}: {verdict.get('sentence_duration_months', 'Unknown')} months"
        para11 = self._create_paragraph('art_dec_2__para_1', sentence)
        art11.append(para11)
        
        sec7.append(art11)
        ch3.append(sec7)
        
        body.append(ch3)
        
        return body
    
    def _create_chapter(self, num, heading):
        """Create a chapter element"""
        chapter = ET.Element('chapter')
        chapter.set('eId', f'chp_{num}')
        
        num_elem = ET.SubElement(chapter, 'num')
        num_elem.text = self._roman_numeral(num)
        
        head_elem = ET.SubElement(chapter, 'heading')
        head_elem.text = heading
        
        return chapter
    
    def _create_section(self, eid, num, heading):
        """Create a section element"""
        section = ET.Element('section')
        section.set('eId', eid)
        
        num_elem = ET.SubElement(section, 'num')
        num_elem.text = str(num)
        
        head_elem = ET.SubElement(section, 'heading')
        head_elem.text = heading
        
        return section
    
    def _create_article(self, eid, num, heading):
        """Create an article element"""
        article = ET.Element('article')
        article.set('eId', eid)
        
        num_elem = ET.SubElement(article, 'num')
        num_elem.text = num
        
        head_elem = ET.SubElement(article, 'heading')
        head_elem.text = heading
        
        return article
    
    def _create_paragraph(self, eid, content):
        """Create a paragraph element"""
        paragraph = ET.Element('paragraph')
        paragraph.set('eId', eid)
        
        content_elem = ET.SubElement(paragraph, 'content')
        content_elem.set('eId', f'{eid}__content')
        
        p = ET.SubElement(content_elem, 'p')
        p.text = content
        
        return paragraph
    
    def _add_element(self, parent, tag, attribs):
        """Add element with attributes"""
        elem = ET.SubElement(parent, tag)
        for key, value in attribs.items():
            elem.set(key, value)
        return elem
    
    def _roman_numeral(self, num):
        """Convert number to roman numeral"""
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
        roman_num = ''
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syms[i]
                num -= val[i]
            i += 1
        return roman_num
    
    def _get_conclusion_text(self, case):
        """Generate conclusion text based on verdict"""
        verdict = case.get('verdict', {})
        case_num = case.get('case_number', 'K 0000/00')
        
        if verdict.get('guilty'):
            return f"The court finds the defendant guilty as charged and imposes the penalties as outlined above in case {case_num}."
        elif verdict.get('acquitted'):
            return f"The court acquits the defendant in case {case_num}."
        else:
            return f"The court renders a conditional verdict in case {case_num}."
    
    def convert_all(self, json_file, output_dir):
        """Convert all cases to AkomaNtoso XML files"""
        self.load_cases(json_file)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for case in self.cases:
            case_id = case.get('case_id', 'Unknown')
            
            # Convert to AkomaNtoso
            judgment = self.case_to_akomantoso(case)
            
            # Pretty print
            xml_str = minidom.parseString(ET.tostring(judgment)).toprettyxml(indent="    ")
            # Remove extra blank lines
            xml_str = '\n'.join([line for line in xml_str.split('\n') if line.strip()])
            
            # Write to file
            output_file = output_path / f"{case_id}_akomantoso.xml"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xml_str)
            
            print(f"✓ Converted {case_id} → {output_file}")
        
        print(f"\n✅ Converted {len(self.cases)} cases to AkomaNtoso XML format")

if __name__ == '__main__':
    converter = AkomaNtosoConverter()
    
    json_file = 'data/cases/DB/EXTRACTED_CASES_DATABASE.json'
    output_dir = 'data/cases/akomantoso'
    
    converter.convert_all(json_file, output_dir)
