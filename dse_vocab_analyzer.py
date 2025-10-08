import spacy
import pandas as pd
from collections import defaultdict
import os
import sys

def check_spacy_model():
    try:
        nlp = spacy.load("en_core_web_sm")
        return nlp
    except OSError:
        print("Error: spaCy model not found")
        sys.exit(1)

def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return None

def process_text(text, file_type, nlp):
    if not text:
        return []
    
    doc = nlp(text.lower())
    vocab_data = []
    
    for token in doc:
        if not token.is_stop and not token.is_punct and len(token.text) > 2 and token.text.isalpha():
            vocab_data.append({
                "unit": token.text,
                "lemma": token.lemma_,
                "pos": token.pos_,
                "type": "Word",
                "file_type": file_type
            })
    
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.strip()
        if 2 <= len(chunk_text.split()) <= 4:
            vocab_data.append({
                "unit": chunk_text,
                "lemma": chunk.lemma_,
                "pos": "NOUN_PHRASE",
                "type": "Phrase",
                "file_type": file_type
            })
    
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC"]:
            vocab_data.append({
                "unit": ent.text,
                "lemma": ent.text,
                "pos": "PROPN",
                "type": "Proper Noun",
                "file_type": file_type
            })
    
    return vocab_data

def calculate_weighted_frequency(data_folder="sample_data"):
    print("="*80)
    print("HKDSE VOCABULARY ANALYSIS")
    print("="*80)
    
    nlp = check_spacy_model()
    print("Model loaded")
    
    if not os.path.exists(data_folder):
        print("Error: Folder not found")
        sys.exit(1)
    
    files = [f for f in os.listdir(data_folder) if f.endswith(".txt")]
    
    if not files:
        print("Error: No files found")
        sys.exit(1)
    
    print("Found", len(files), "files")
    
    all_vocab = defaultdict(lambda: {
        "count_script": 0,
        "count_answer": 0,
        "lemma": "",
        "pos": "",
        "type": "",
        "sources": set(),
        "original_forms": set()
    })
    
    for filename in sorted(files):
        filepath = os.path.join(data_folder, filename)
        print("Processing:", filename)
        
        content = read_file(filepath)
        if not content:
            continue
        
        name_parts = filename.replace(".txt", "").split("_")
        file_type = name_parts[1] if len(name_parts) >= 2 else "script"
        
        vocab_list = process_text(content, file_type, nlp)
        
        for item in vocab_list:
            unit = item["lemma"]
            
            if file_type == "script":
                all_vocab[unit]["count_script"] += 1
            elif file_type == "answer":
                all_vocab[unit]["count_answer"] += 1
            
            all_vocab[unit]["lemma"] = unit
            all_vocab[unit]["pos"] = item["pos"]
            all_vocab[unit]["type"] = item["type"]
            all_vocab[unit]["sources"].add(filename)
            all_vocab[unit]["original_forms"].add(item["unit"])
    
    print("-"*80)
    print("Calculating scores (Script x2, Answer x3)")
    print("-"*80)
    
    results = []
    for unit, data in all_vocab.items():
        weighted_score = (data["count_script"] * 2) + (data["count_answer"] * 3)
        
        if weighted_score >= 4:
            results.append({
                "Rank": 0,
                "Vocabulary Unit": unit,
                "Type": data["type"],
                "Part of Speech": data["pos"],
                "Weighted Score": weighted_score,
                "Script Frequency": data["count_script"],
                "Answer Frequency": data["count_answer"],
                "Variations": ", ".join(sorted(data["original_forms"]))[:100],
                "Source Files": ", ".join(sorted(data["sources"]))
            })
    
    results.sort(key=lambda x: x["Weighted Score"], reverse=True)
    
    for i, item in enumerate(results, 1):
        item["Rank"] = i
    
    return results[:500]

def create_output(data_folder="sample_data"):
    results = calculate_weighted_frequency(data_folder)
    
    if not results:
        print("No vocabulary found")
        return None
    
    df = pd.DataFrame(results)
    
    print("="*80)
    print("TOP 30 VOCABULARY UNITS")
    print("="*80)
    
    display_df = df.head(30)[["Rank", "Vocabulary Unit", "Type", "Weighted Score", 
                                "Script Frequency", "Answer Frequency"]]
    print(display_df.to_string(index=False))
    
    print("="*80)
    print("Total units:", len(results))
    print("="*80)
    
    output_file_xls = "output/dse_vocab_top500.xlsx"
    output_file_csv = "output/dse_vocab_top500.csv"
    try:
        df.to_excel(output_file_xls, index=False, sheet_name="Top 500 Vocabulary")
        df.to_csv(output_file_csv, index=False)
        print(f"Saved to: {output_file_xls} and {output_file_csv}")
    except Exception as e:
        print("File save failed:", str(e))
    
    return df

if __name__ == "__main__":
    try:
        df = create_output("sample_data")
    except Exception as e:
        print("Error:", str(e))
        sys.exit(1)
