import fitz  # PyMuPDF
import os
import json
import re
from datetime import datetime

# === Directory Paths ===
input_dir = "input"
output_dir = "output"
output_path = os.path.join(output_dir, "challenge1b_output.json")

# === Load Persona JSON ===
persona_json_path = os.path.join(input_dir, "persona_input.json")
with open(persona_json_path, "r", encoding="utf-8") as f:
    persona_data = json.load(f)

persona = persona_data["persona"]
job_to_be_done = persona_data["job_to_be_done"]

# === Updated Keyword List ===
KEYWORDS = [
    "example", "problem", "q.", "find", "result", "question",
    "derivation", "formula", "application", "calculation",
    "numerical", "solve", "determine", "derive", "equation", "method"
]

# === Helper: Clean raw text lines ===
def clean_text(text):
    text = text.replace("", "")
    text = re.sub(r'[^A-Za-z0-9 .\-()/:]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# === Scoring Function ===
def keyword_match_score(text):
    text_lower = text.lower()
    return sum(1 for word in KEYWORDS if word in text_lower)

def estimate_complexity(text):
    # Higher complexity if more digits and mathematical symbols
    digit_count = sum(c.isdigit() for c in text)
    math_ops = len(re.findall(r'[=+\-*/^√∑∫()]', text))
    return digit_count + math_ops

def classify_section(text):
    text = text.lower()
    if "example" in text or "problem" in text:
        return "example"
    elif "derive" in text or "derivation" in text:
        return "derivation"
    elif "formula" in text or "equation" in text:
        return "formula"
    else:
        return "other"


# === Section Extraction ===
def extract_relevant_sections(doc_path, headings_by_page):
    doc = fitz.open(doc_path)
    relevant_sections = []
    subsection_analysis = []
    filename = os.path.basename(doc_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                line_text = " ".join([span["text"] for span in line["spans"] if span["text"].strip()])
                cleaned = clean_text(line_text)

                if len(cleaned.split()) < 4:
                    continue

                score = keyword_match_score(cleaned)
                if score >= 2:
                    complexity = estimate_complexity(cleaned)
                    weighted = 2 * score + complexity
                    section_type = classify_section(cleaned)

                    summary = cleaned.split('.')[0] + '.' if '.' in cleaned else ' '.join(cleaned.split()[:25]) + "..."

                    relevant_sections.append({
                        "document": filename,
                        "page_number": page_num + 1,
                        "section_title": cleaned,
                        "topic": get_topic_for_page(page_num + 1, headings_by_page),
                        "type": section_type,
                        "weighted_score": weighted
                    })

                    subsection_analysis.append({
                        "document": filename,
                        "refined_text": summary,
                        "page_number": page_num + 1
                    })



    return relevant_sections, subsection_analysis

# === Heading Outline Extraction ===
def extract_pdf_headings(pdf_path):
    doc = fitz.open(pdf_path)
    font_sizes = set()
    raw_headings = []
    seen_headings = set()
    pages_with_headings = set()

    # Get all font sizes
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes.add(span["size"])

    if not font_sizes:
        print(f"[!] No font sizes found in {os.path.basename(pdf_path)}. Skipping outline generation.")
        return []

    # Define thresholds
    font_sizes = sorted(list(font_sizes), reverse=True)
    h1 = font_sizes[0] - 1
    h2 = font_sizes[1] - 1 if len(font_sizes) > 1 else h1 - 2
    h3 = font_sizes[2] - 1 if len(font_sizes) > 2 else h2 - 2


    # Extract headings
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        size = span["size"]
                        if not text or len(text) < 2:
                            continue
                        if size >= h1:
                            level = "H1"
                        elif size >= h2:
                            level = "H2"
                        elif size >= h3:
                            level = "H3"
                        else:
                            continue

                        key = (text.lower(), level)
                        if key in seen_headings:
                            continue

                        seen_headings.add(key)
                        pages_with_headings.add(page_num + 1)
                        raw_headings.append({
                            "level": level,
                            "text": text,
                            "page": page_num + 1
                        })

    # Add "No heading" fallback
    for i in range(1, len(doc) + 1):
        if i not in pages_with_headings:
            raw_headings.append({
                "level": "None",
                "text": "No heading",
                "page": i
            })

    raw_headings.sort(key=lambda x: x["page"])
    return raw_headings

# === MAIN EXECUTION ===
all_sections = []
all_subsections = []
document_names = []
document_outlines = {}

def get_topic_for_page(page_num, headings_by_page):
    # Go backwards from page_num to find nearest H1 or H2
    for p in range(page_num, 0, -1):
        if p in headings_by_page:
            return headings_by_page[p]
    return "No topic"

for file in os.listdir(input_dir):
    if file.endswith(".pdf"):
        pdf_path = os.path.join(input_dir, file)
        document_names.append(file)

        print(f"Processing: {file}")

        # First generate and store heading outlines
        document_outlines[file] = extract_pdf_headings(pdf_path)

        # Build topic lookup by page (H1/H2 only)
        headings_by_page = {}
        for entry in document_outlines[file]:
            if entry["level"] in ["H1", "H2"]:
                headings_by_page[entry["page"]] = entry["text"]

        # Now pass the heading info to section extractor
        sections, subsections = extract_relevant_sections(pdf_path, headings_by_page)
        all_sections.extend(sections)
        all_subsections.extend(subsections)



# Rank and sort
all_sections.sort(key=lambda x: x["weighted_score"], reverse=True)
for rank, section in enumerate(all_sections, 1):
    section["importance_rank"] = rank
    section.pop("weighted_score")

# Final Output
output = {
    "metadata": {
        "input_documents": document_names,
        "persona": persona,
        "job_to_be_done": job_to_be_done,
        "processing_timestamp": datetime.utcnow().isoformat() + "Z"
    },
    "extracted_sections": all_sections,
    "subsection_analysis": all_subsections,
    "document_outlines": document_outlines
} 

os.makedirs(output_dir, exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n Extraction complete!!!!!. Output saved to: {output_path}")
