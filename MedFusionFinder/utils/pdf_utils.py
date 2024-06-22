import fitz
import re

def extract_text_from_pdf(file_path):
    document = fitz.open(file_path)
    text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def parse_pdf_text(text):
    patterns = {
        "PID": r"(\d+)\s*\(",  # Captures the PID before the parenthesis
        "Birthdate": r"\(([\d\.]+),\s*([MF])\)",  # Captures the birthdate and gender inside the parenthesis
        "Title": r"([^\n]+)\nIndication",  # Capture the text before the "Indication" section
        "Indication": r"Indication\s*([\s\S]*?)(?=Technique|Description|Epreuve de stress|Rehaussement tardif|Conclusion)",
        "Technique": r"Technique\s*([\s\S]*?)(?=Indication|Description|Epreuve de stress|Rehaussement tardif|Conclusion)",
        "Description": r"Description\s*([\s\S]*?)(?=Indication|Technique|Epreuve de stress|Rehaussement tardif|Conclusion)",
        "Epreuve de stress": r"Epreuve de stress\s*([\s\S]*?)(?=Indication|Technique|Description|Rehaussement tardif|Conclusion|$)",
        "Rehaussement tardif": r"Rehaussement tardif\s*([\s\S]*?)(?=Indication|Technique|Description|Epreuve de stress|Conclusion|$)",
        "Conclusion": r"Conclusion\s*([\s\S]*?)(?=Indication|Technique|Description|Epreuve de stress|Rehaussement tardif|$)"
    }

    data = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        if match:
            if field == "PID":
                data["PID"] = int(match.group(1).strip())
            elif field == "Birthdate":
                data["Birthdate"] = match.group(1).strip()
                data["Gender"] = match.group(2).strip()
            elif field == "Title":
                data["Title"] = match.group(1).strip()
            else:
                data[field] = match.group(1).strip()
    
    return data
