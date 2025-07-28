# 📘 PersonaPrep – Persona-Aligned Educational PDF Extractor

**PersonaPrep** intelligently extracts relevant example problems, derivations, and formulas from academic PDFs, aligned to a student persona’s learning goals.\
It is designed for exam revision scenarios using lightweight NLP and document structure heuristics.

---

## 🚀 Key Features

- 🎯 Persona-guided section extraction
- 🧠 Intelligent scoring: `2 × keyword_match + math_complexity`
- 🏷 Section tagging: `example`, `derivation`, `formula`, `other`
- 🔹 Page-to-topic mapping via heading inference
- 📄 Summarized previews for faster reading
- 📚 Multi-PDF batch support
- 🔢 Structured JSON output with rankings

---

## 📁 Folder Structure

```
.
├── persona_extractor.py       # Main extraction logic
├── requirements.txt           # Python dependency: PyMuPDF
├── Dockerfile                 # Container setup
├── input/                     # Input PDFs + persona JSON
│   ├── persona_input.json
│   └── *.pdf
├── output/                    # Output folder
│   └── challenge1b_output.json
```

---

## 🔧 Docker Build

```bash
docker build --platform=linux/amd64 -t adobe-solution:harshi1b .
```

---

## ▶️ Run the Extractor

```bash
docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" --network none adobe-solution:harshi1b
```

> ✅ On **Windows CMD**, replace `${PWD}` with `%cd%`

---

## 📥 Input Format

Place these in `/input/`:

- `persona_input.json` → defines the learner profile and exam focus
- `*.pdf` → one or more academic documents for processing

### Sample persona\_input.json

```json
{
  "persona": {
    "role": "Undergraduate Physics Student",
    "expertise": "Intermediate knowledge in wave optics and semiconductors",
    "goal": "Prepare for semester exams with focus on derivations, examples, and applications"
  },
  "job_to_be_done": "Identify and prioritize example problems and formula-based derivations to revise before exams"
}
```

---

## 📤 Output Format

The file `challenge1b_output.json` contains:

- `metadata` — persona, timestamp, input files
- `extracted_sections` — most relevant content sorted by importance
- `subsection_analysis` — concise previews of matches
- `document_outlines` — inferred heading structure per PDF

### Output Snippet

```json
{
  "extracted_sections": [
    {
      "document": "notes.pdf",
      "page_number": 33,
      "section_title": "Example Problem - 1",
      "topic": "Young’s Double Slit Experiment",
      "type": "example",
      "importance_rank": 1
    }
  ]
}
```

---

## 🧠 How It Works

### 1. Persona Alignment

Parses persona\_input.json to guide relevance detection.

### 2. Keyword Scoring

Uses a rich set of educational terms like `example`, `problem`, `derive`, `solve`, etc.

### 3. Complexity Estimation

Counts math symbols and digits to prioritize deeper problems.

### 4. Type Classification

Tags sections as `example`, `derivation`, `formula`, or `other`.

### 5. Topic Detection

Assigns topic to each match based on closest heading (`H1` or `H2`).

### 6. Ranking

Scores and ranks all matches using:

```
weighted_score = 2 × keyword_score + complexity_score
```

---

## ✅ Constraints Met

- No network access (`--network none`)
- Fully Dockerized, reproducible run
- Batch processing support
- Output follows Adobe challenge format

---

## 👨‍💼 Authors

- [Harshini Nadendla](https://github.com/Harshini2410)
- [Spurthi Inturu](https://github.com/Spurthi7904)
- [Chakrish Vejendla](https://github.com/Vejandlachakrish)

---

## 🏆 Acknowledgements

Developed for **Adobe Hackathon 2025 — Round 1B: Connecting the Dots**. Focus: student persona-based PDF content extraction for academic revision.

