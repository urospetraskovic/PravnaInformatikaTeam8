#!/usr/bin/env python3
import xml.etree.ElementTree as ET

tree = ET.parse(r'c:\Users\Korisnik\Documents\GitHub\PravnaInformatikaTeam8\Project\data\cases\akomantoso\Case_122_12.xml')
root = tree.getroot()

print("All FRBRnumber elements:")
for num in root.findall('.//FRBRnumber'):
    print(f"  Attributes: {num.attrib}")
    print(f"  Text: '{num.text}'")

print("\nAll FRBRname elements:")
for name in root.findall('.//FRBRname'):
    print(f"  Attributes: {name.attrib}")
    print(f"  Text: '{name.text}'")
