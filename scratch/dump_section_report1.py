import zipfile
import xml.etree.ElementTree as ET
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

path = r"E:\Sem - 4\Mini Projects\DBMS REPORT 1.docx"

with zipfile.ZipFile(path) as z:
    try:
        doc_xml = z.read("word/document.xml")
        root = ET.fromstring(doc_xml)
        
        paragraphs = []
        for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            p_text = "".join(node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text)
            if p_text.strip():
                paragraphs.append(p_text.strip())
                
        print(f"Total paragraphs extracted: {len(paragraphs)}")
        
        section_idx = -1
        for idx, text in enumerate(paragraphs):
            if re.search(r"SCREENSHOTS", text, re.IGNORECASE):
                section_idx = idx
                print(f"Found heading at paragraph index {idx}: '{text}'")
                break
                
        if section_idx != -1:
            print("\n--- SECTION CONTENT FROM REPORT 1 ---")
            for i in range(section_idx, min(len(paragraphs), section_idx + 80)):
                print(f"P{i}: {paragraphs[i]}")
        else:
            print("\nScreenshots heading not found in Report 1.")
    except Exception as e:
        print(f"Error: {e}")
