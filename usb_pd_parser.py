import pdfplumber
import re
import json
import pandas as pd
from pathlib import Path

def find_pdf_in_folder():
    for file in os.listdir():
        if file.lower().endswith(".pdf"):
            return file
    return None

def extract_toc(pdf_path):
    toc_data = []
    regex = r"^(\d+(\.\d+)*)(\s+)([^\n.]+)(.+)\s+(\d+)$"

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages[:10]:
            text = page.extract_text()
            if text:
                for line in text.split("\n"):
                    match = re.match(regex, line.strip())
                    if match:
                        section_id = match.group(1)
                        title = match.group(4).strip()
                        page_no = int(match.group(6))
                        level = section_id.count(".") + 1
                        parent_id = ".".join(section_id.split(".")[:-1]) if "." in section_id else None
                        toc_data.append({
                            "doc_title": "USB PD Specification Rev X",
                            "section_id": section_id,
                            "title": title,
                            "full_path": f"{section_id} {title}",
                            "page": page_no,
                            "level": level,
                            "parent_id": parent_id,
                            "tags": []
                        })
    return toc_data

def save_jsonl(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def validate_toc_vs_spec(toc_data, spec_data):
    toc_sections = {item["section_id"] for item in toc_data}
    spec_sections = {item["section_id"] for item in spec_data}

    report = {
        "total_toc": len(toc_sections),
        "total_spec": len(spec_sections),
        "missing_in_spec": list(toc_sections - spec_sections),
        "extra_in_spec": list(spec_sections - toc_sections)
    }
    df = pd.DataFrame([report])
    df.to_excel("output/validation_report.xlsx", index=False, engine="openpyxl")

def main():
    pdf_file = find_pdf_in_folder()
    if not pdf_file:
        print("❌ No PDF file found in the current folder. Please add one and try again.")
        return

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    print(f"📄 Using PDF: {pdf_file}")
    toc_data = extract_toc(pdf_file)
    save_jsonl(toc_data, output_dir / "usb_pd_toc.jsonl")

    print("Extracting all sections... (placeholder)")
    spec_data = toc_data  # Replace later with real section parsing
    save_jsonl(spec_data, output_dir / "usb_pd_spec.jsonl")

    print("Validating...")
    validate_toc_vs_spec(toc_data, spec_data)

    print("\n✅ Parsing complete!")
    print(f"ToC entries: {len(toc_data)}")
    print(f"Files saved in: {output_dir.resolve()}")

if __name__ == "__main__":
    main()
