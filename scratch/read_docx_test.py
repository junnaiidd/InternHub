import zipfile
import re
import os

files = [
    r"E:\Sem - 4\Mini Projects\DBMS Report.docx",
    r"E:\Sem - 4\Mini Projects\DBMS REPORT 1.docx",
    r"E:\Sem - 4\Mini Projects\DBMS REPORT 2.docx"
]

def search_docx(path):
    print(f"\nSearching: {path}")
    if not os.path.exists(path):
        print("File does not exist")
        return
    try:
        with zipfile.ZipFile(path) as z:
            doc_xml = z.read("word/document.xml").decode("utf-8")
            # Let's remove XML tags to get raw text
            text = re.sub(r'<[^>]+>', ' ', doc_xml)
            # Find occurrences of "Screenshot" or "UI"
            matches = list(re.finditer(r"(?i)screenshot|ui description|user interface", text))
            print(f"Total characters: {len(text)}")
            print(f"Matches count: {len(matches)}")
            # Show a snippet of the first few matches
            for m in matches[:5]:
                start = max(0, m.start() - 100)
                end = min(len(text), m.end() + 100)
                print(f"Snippet: ... {text[start:end].strip()} ...")
    except Exception as e:
        print(f"Error: {e}")

for f in files:
    search_docx(f)
