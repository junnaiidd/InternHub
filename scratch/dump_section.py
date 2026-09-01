import zipfile
import re
import xml.etree.ElementTree as ET

path = r"E:\Sem - 4\Mini Projects\DBMS REPORT 2.docx"

def dump_section(path):
    print(f"Reading docx from {path}...")
    with zipfile.ZipFile(path) as z:
        doc_xml = z.read("word/document.xml")
        
        # Parse XML to maintain paragraph structures and styles
        root = ET.fromstring(doc_xml)
        
        # Namespaces used in docx XML
        namespaces = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }
        
        paragraphs = []
        for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            # Extract text from run elements
            p_text = "".join(node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text)
            if p_text.strip():
                paragraphs.append(p_text.strip())
                
        print(f"Total paragraphs extracted: {len(paragraphs)}")
        
        # Find where "SCREENSHOTS AND UI DESCRIPTION" or similar header occurs
        section_idx = -1
        for idx, text in enumerate(paragraphs):
            if re.search(r"SCREENSHOTS\s+AND\s+UI\s+DESCRIPTION", text, re.IGNORECASE):
                section_idx = idx
                print(f"Found heading at paragraph index {idx}: '{text}'")
                break
                
        if section_idx != -1:
            # Let's print the next 60 paragraphs to see the structure and style
            print("\n--- SECTION CONTENT ---")
            for i in range(section_idx, min(len(paragraphs), section_idx + 80)):
                print(f"P{i}: {paragraphs[i]}")
        else:
            # If not found, let's print first 50 paragraphs that contain screenshot or UI
            print("\nHeading not found exactly. Here are some paragraph titles:")
            for idx, text in enumerate(paragraphs):
                if len(text) < 100 and ("screenshot" in text.lower() or "ui" in text.lower() or "description" in text.lower()):
                    print(f"P{idx}: {text}")

dump_section(path)
