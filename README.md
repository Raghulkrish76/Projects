# PDF Table of Contents Extractor & Validator

This project extracts the **Table of Contents (ToC)** from a PDF (such as the *USB PD Specification*), saves it in structured formats, and validates the extracted ToC against parsed section data.

## Features
- Automatically detects the first PDF in the current folder.
- Extracts Table of Contents entries (up to the first 10 pages by default).
- Captures:
  - Section ID (e.g., `3.1.2`)
  - Title
  - Page number
  - Hierarchy (level + parent section)
- Saves extracted ToC as **JSONL** files.
- Validates ToC against the parsed spec and generates a validation report in **Excel**.

##  Project Structure
project/
│── main.py # Main script (this file)
│── requirements.txt # Python dependencies
│── output/ # Generated outputs (create manually before running)
│ ├── usb_pd_toc.jsonl
│ ├── usb_pd_spec.jsonl
│ └── validation_report.xlsx
│── README.md # Project documentation

##  Requirements
- Python 3.8+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
