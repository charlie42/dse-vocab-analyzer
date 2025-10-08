# HKDSE English Listening Vocabulary Analyzer

A Python-based NLP tool that analyzes HKDSE (Hong Kong Diploma of Secondary Education) English listening exam materials to identify and rank the most important vocabulary units using weighted frequency analysis.

## 🎯 Project Overview

This tool processes listening exam scripts and answer files to create a data-rich vocabulary list for students preparing for HKDSE English exams. The analysis applies weighted scoring where vocabulary from answer files receives higher priority (3x weight) compared to script files (2x weight).

## ✨ Features

- **Weighted Frequency Analysis**: Answer files weighted 3x, script files 2x
- **Multi-type Vocabulary Extraction**:
  - Single words (nouns, verbs, adjectives, etc.)
  - Phrases (2-4 word combinations)
  - Proper nouns (names, locations, organizations)
- **Automatic POS Tagging**: Part-of-speech identification using spaCy
- **Excel Export**: Results saved in spreadsheet format
- **Comprehensive Tracking**: Source files and variation tracking
- **Error Handling**: Robust file processing with clear error messages

## 📋 Requirements

- Python 3.8+
- Required packages:
  ```
  spacy>=3.0.0
  pandas>=1.3.0
  openpyxl>=3.0.0
  ```

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/dse-vocab-analyzer.git
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

## 📁 Project Structure

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

## 💻 Usage

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

## 📊 Output Format

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

## 🔧 Customization

### Change Data Folder
Edit the `DATA_FOLDER` variable in `dse_vocab_analyzer.py`:
```python
DATA_FOLDER = 'your_custom_folder'
```

### Adjust Weighted Scoring
Modify the weights in the `calculate_weighted_frequency()` function:
```python
weighted_score = (data['count_script'] * 2) + (data['count_answer'] * 3)
```

### Change Threshold
Adjust minimum score requirement:
```python
if weighted_score >= 4:  # Change this value
```

## 📈 Demo Results

Using the provided sample data (2022-2023), the analyzer identifies:
- ~200-300 unique vocabulary units
- Top items include exam-relevant terms like:
  - Academic vocabulary (pseudoscience, alternative, deficiencies)
  - Action verbs (switch, release, promote)
  - Common exam phrases (brown color, scientific evidence)

## 🤝 Use Cases

- **For Students**: Focus study efforts on high-frequency exam vocabulary
- **For Teachers**: Identify core vocabulary for teaching materials
- **For Researchers**: Analyze vocabulary trends across exam years
- **For Test Prep Companies**: Create targeted vocabulary lists

## 🛠️ Technical Details

### NLP Pipeline
1. Text preprocessing and cleaning
2. Tokenization using spaCy
3. Lemmatization for word grouping
4. POS tagging for grammatical classification
5. Named Entity Recognition for proper nouns
6. N-gram extraction for phrases
7. Frequency counting with weighted scoring
8. Ranking and export

### Weighting Rationale
- **Answer files (3x)**: These contain the exact vocabulary examiners expect
- **Script files (2x)**: Context-rich but includes more noise
- Result: Answer vocabulary naturally ranks higher in importance

## 📝 Future Enhancements

- [ ] Add support for PDF file input
- [ ] Generate grammar forms (plural, past tense, comparatives)
- [ ] Implement answer variation detection per DSE marking rules
- [ ] Create Google Sheets integration
- [ ] Add visualization dashboard
- [ ] Support for multiple languages
- [ ] Batch processing for 100+ files

## 🐛 Troubleshooting

**Error: "spaCy English model not found"**
```bash
python -m spacy download en_core_web_sm
```

**Error: "No .txt files found"**
- Check that files are in `sample_data/` folder
- Verify files have `.txt` extension
- Ensure folder path is correct

**Error: "Module not found"**
```bash
pip install -r requirements.txt
```

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 👤 Author

Created for HKDSE English exam preparation

## 🙏 Acknowledgments

- spaCy for NLP capabilities
- HKEAA for exam format reference
- Open-source Python community

---

**Note**: This is a demonstration project showing NLP analysis capabilities. For production use with 13+ years of exam data, additional optimization and error handling would be implemented.
