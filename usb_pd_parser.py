import os
import re
import json
import pdfplumber
import pandas as pd
from pathlib import Path


class PDFHandler:
    """Handles finding and opening PDF files."""
    def __init__(self, folder="."):
        self.folder = folder

    def find_pdf(self):
        for file in os.listdir(self.folder):
            if file.lower().endswith(".pdf"):
                return Path(self.folder) / file
        return None


class TOCExtractor:
    """Extracts Table of Contents (TOC) from PDF."""
    def __init__(self, pdf_path, doc_title="USB PD Specification Rev X"):
        self.pdf_path = pdf_path
        self.doc_title = doc_title
        self.regex = r"^(\d+(\.\d+)*)(\s+)([^\n.]+)(.+)\s+(\d+)$"

    def extract(self, max_pages=10):
        toc_data = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages[:max_pages]:
                text = page.extract_text()
                if not text:
                    continue
                for line in text.split("\n"):
                    match = re.match(self.regex, line.strip())
                    if match:
                        section_id = match.group(1)
                        title = match.group(4).strip()
                        page_no = int(match.group(6))
                        level = section_id.count(".") + 1
                        parent_id = ".".join(section_id.split(".")[:-1]) if "." in section_id else None
                        toc_data.append({
                            "doc_title": self.doc_title,
                            "section_id": section_id,
                            "title": title,
                            "full_path": f"{section_id} {title}",
                            "page": page_no,
                            "level": level,
                            "parent_id": parent_id,
                            "tags": []
                        })
        return toc_data


class JSONLWriter:
    """Writes extracted data into JSONL format."""
    @staticmethod
    def save(data, filename):
        with open(filename, "w", encoding="utf-8") as f:
            for entry in data:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class Validator:
    """Validates extracted TOC data against the specification."""
    @staticmethod
    def validate(toc_data, spec_data, output_file):
        toc_sections = {item["section_id"] for item in toc_data}
        spec_sections = {item["section_id"] for item in spec_data}

        report = {
            "total_toc": len(toc_sections),
            "total_spec": len(spec_sections),
            "missing_in_spec": list(toc_sections - spec_sections),
            "extra_in_spec": list(spec_sections - toc_sections)
        }

        df = pd.DataFrame([report])
        df.to_excel(output_file, index=False, engine="openpyxl")


class TOCParserApp:
    """Main application class."""
    def __init__(self, output_dir="output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def run(self):
        pdf_handler = PDFHandler()
        pdf_file = pdf_handler.find_pdf()

        if not pdf_file:
            print("No PDF file found in the current folder. Please add one and try again.")
            return

        print(f"📄 Using PDF: {pdf_file.name}")
        extractor = TOCExtractor(pdf_file)
        toc_data = extractor.extract()

        JSONLWriter.save(toc_data, self.output_dir / "usb_pd_toc.jsonl")

        print("Extracting all sections... (placeholder)")
        spec_data = toc_data  # Replace later with real section parsing
        JSONLWriter.save(spec_data, self.output_dir / "usb_pd_spec.jsonl")

        print("Validating...")
        Validator.validate(toc_data, spec_data, self.output_dir / "validation_report.xlsx")

        print("\n✅ Parsing complete!")
        print(f"ToC entries: {len(toc_data)}")
        print(f"Files saved in: {self.output_dir.resolve()}")


if __name__ == "__main__":
    app = TOCParserApp()
    app.run()
