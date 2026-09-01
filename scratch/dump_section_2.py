import zipfile
import xml.etree.ElementTree as ET
import sys

# Configure stdout to use utf-8 encoding to avoid Windows console errors
sys.stdout.reconfigure(encoding='utf-8')

path = r"E:\Sem - 4\Mini Projects\DBMS REPORT 2.docx"

with zipfile.ZipFile(path) as z:
    doc_xml = z.read("word/document.xml")
    root = ET.fromstring(doc_xml)
    
    paragraphs = []
    for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        p_text = "".join(node.text for node in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text)
        if p_text.strip():
            paragraphs.append(p_text.strip())
            
    print("Dumping paragraphs 750 to 830:")
    for idx in range(min(750, len(paragraphs)), min(830, len(paragraphs))):
        print(f"P{idx}: {paragraphs[idx]}")
