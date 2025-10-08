# HKDSE English Listening Vocabulary Analyzer

A Python-based NLP tool that analyzes HKDSE (Hong Kong Diploma of Secondary Education) English listening exam materials to identify and rank the most important vocabulary units using weighted frequency analysis.

This tool processes listening exam scripts and answer files to create a data-rich vocabulary list for students preparing for HKDSE English exams. The analysis applies weighted scoring where vocabulary from answer files receives higher priority (3x weight) compared to script files (2x weight).

## Features

- **Weighted Frequency Analysis**: Answer files weighted 3x, script files 2x
- **Multi-type Vocabulary Extraction**:
  - Single words (nouns, verbs, adjectives, etc.)
  - Phrases (2-4 word combinations)
  - Proper nouns (names, locations, organizations)
- **Automatic POS Tagging**: Part-of-speech identification using spaCy
- **Excel Export**: Results saved in spreadsheet format
- **Comprehensive Tracking**: Source files and variation tracking
- **Error Handling**: Robust file processing with clear error messages

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/charlie42/dse-vocab-analyzer.git
   cd dse-vocab-analyzer
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy English model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Project Structure

```
dse-vocab-analyzer/
├── README.md
├── requirements.txt
├── .gitignore
├── dse_vocab_analyzer.py       # Main analysis script
├── sample_data/                 # Sample input files (demo)
│   ├── 2023_script.txt
│   ├── 2023_answer.txt
│   ├── 2022_script.txt
│   └── 2022_answer.txt
└── output/                      # Generated output files
    └── dse_vocab_top500.xlsx
```

## Usage

### Basic Usage

1. **Prepare your data files**:
   - Place listening script files in `sample_data/` folder
   - Name them as: `YYYY_script.txt` (e.g., `2023_script.txt`)
   - Place answer files as: `YYYY_answer.txt` (e.g., `2023_answer.txt`)

2. **Run the analyzer**:
   ```bash
   python dse_vocab_analyzer.py
   ```

3. **View results**:
   - Console output shows top 30 vocabulary items
   - Full results saved in `dse_vocab_top500.xlsx`

### Expected File Format

**Script files** (`YYYY_script.txt`):
```
Section A: Part 1

Speaker 1: Welcome to today's discussion about...
Speaker 2: Thank you for having me...
```

**Answer files** (`YYYY_answer.txt`):
```
1.1  keyword one
1.2  keyword two
2.(a) short phrase
2.(b) another phrase
```

## Output Format

The Excel output contains the following columns:

| Column | Description |
|--------|-------------|
| Rank | Position in the ranking (1-500) |
| Vocabulary Unit | The lemmatized form of the word/phrase |
| Type | Word / Phrase / Proper Noun |
| Part of Speech | Grammatical category (NOUN, VERB, etc.) |
| Weighted Score | Calculated score (Script×2 + Answer×3) |
| Script Frequency | Number of occurrences in script files |
| Answer Frequency | Number of occurrences in answer files |
| Variations | Different forms found in the text |
| Source Files | Files where this vocabulary appears |