import spacy
import pandas as pd
from collections import defaultdict
import os
import sys
import re

def check_spacy_model():
    try:
        nlp = spacy.load("en_core_web_sm")
        return nlp
    except OSError:
        print("Error: spaCy model not found")
        print("Please install: python -m spacy download en_core_web_sm")
        sys.exit(1)

def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return None

def parse_answer_file(content):
    """Extract answers and their variations from answer files"""
    variations = defaultdict(set)
    lines = content.split('\n')
    
    for line in lines:
        # Match patterns like "Accept:" or "Do NOT accept:"
        if "Accept:" in line and "Do NOT" not in line:
            # Extract accepted variations
            accept_part = line.split("Accept:")[1].strip()
            # Split by / or , to get variations
            variants = re.split(r'[/,]', accept_part)
            for variant in variants:
                variant = variant.strip()
                if variant and "(" not in variant:  # Skip patterns with parentheses for now
                    # Store all variations together
                    base_form = variant.lower()
                    variations[base_form].add(variant)
        
        # Also look for main answer patterns (e.g., "1. answer text")
        elif re.match(r'^\d+\.', line):
            # Extract the main answer
            answer_match = re.match(r'^\d+\.\s*(.+?)(?:\s*Accept:|$)', line)
            if answer_match:
                answer = answer_match.group(1).strip()
                if answer and "/" in answer:
                    # Handle answers with slashes like "student(s) / classmate(s)"
                    parts = answer.split("/")
                    for part in parts:
                        part = part.strip()
                        # Handle parentheses - e.g., "student(s)" becomes "student" and "students"
                        if "(" in part and ")" in part:
                            base = re.sub(r'\([^)]+\)', '', part).strip()
                            inside = re.search(r'\(([^)]+)\)', part)
                            if inside:
                                suffix = inside.group(1)
                                variations[base.lower()].add(base)
                                variations[(base + suffix).lower()].add(base + suffix)
                        else:
                            variations[part.lower()].add(part)
    
    return variations

def get_syllable_count(word):
    """Better syllable counting"""
    word = word.lower()
    count = 0
    vowels = 'aeiouy'
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            count += 1
        previous_was_vowel = is_vowel
    
    # Adjust for silent e
    if word.endswith('e'):
        count -= 1
    if word.endswith('le') and len(word) > 2:
        count += 1
    
    if count == 0:
        count = 1
    return count

def generate_grammatical_forms(word, pos, nlp):
    """Generate grammatical forms based on POS using inflect and custom rules"""
    forms = {}
    
    try:
        import inflect
        p = inflect.engine()
        
        if pos == "NOUN":
            # Check if it's uncountable
            uncountable = {
                'water', 'blood', 'electricity', 'research', 'health', 
                'footwear', 'chlorine', 'advice', 'information', 'news',
                'equipment', 'evidence', 'homework', 'knowledge', 'money',
                'thinking', 'clothing', 'furniture', 'luggage'
            }
            
            if word in uncountable:
                forms['plural'] = ''  # Empty for uncountable
            else:
                plural = p.plural_noun(word)
                forms['plural'] = plural if plural else word + 's'
        
        elif pos == "VERB":
            # Common irregular verbs
            irregular_verbs = {
                'be': 'was/were', 'buy': 'bought', 'think': 'thought',
                'feel': 'felt', 'make': 'made', 'take': 'took',
                'come': 'came', 'go': 'went', 'give': 'gave',
                'see': 'saw', 'get': 'got', 'do': 'did',
                'say': 'said', 'know': 'knew', 'find': 'found',
                'tell': 'told', 'become': 'became', 'leave': 'left',
                'bring': 'brought', 'lead': 'led', 'let': 'let',
                'put': 'put', 'set': 'set', 'cut': 'cut', 'hit': 'hit'
            }
            
            if word in irregular_verbs:
                forms['past_tense'] = irregular_verbs[word]
            else:
                # Simple past tense rules
                if word.endswith('e'):
                    forms['past_tense'] = word + 'd'
                elif word.endswith('y') and len(word) > 2 and word[-2] not in 'aeiou':
                    forms['past_tense'] = word[:-1] + 'ied'
                else:
                    forms['past_tense'] = word + 'ed'
        
        elif pos == "ADJ":
            # Comprehensive adjective rules
            # 1. Irregular adjectives (check first)
            irregular_adj = {
                'good': ('better', 'best'),
                'bad': ('worse', 'worst'), 
                'far': ('farther/further', 'farthest/furthest'),
                'little': ('less', 'least'),
                'many': ('more', 'most'),
                'much': ('more', 'most'),
                'old': ('older/elder', 'oldest/eldest'),
                'well': ('better', 'best')
            }
            
            if word in irregular_adj:
                forms['comparative'] = irregular_adj[word][0]
                forms['superlative'] = irregular_adj[word][1]
            else:
                syllables = get_syllable_count(word)
                
                # One-syllable adjectives: use -er/-est
                if syllables == 1:
                    if word.endswith('e'):
                        forms['comparative'] = word + 'r'
                        forms['superlative'] = word + 'st'
                    elif word[-1] in 'bdfgklmnprstvz' and word[-2] in 'aeiou' and len(word) > 2:
                        # Double final consonant (big → bigger)
                        forms['comparative'] = word + word[-1] + 'er'
                        forms['superlative'] = word + word[-1] + 'est'
                    else:
                        forms['comparative'] = word + 'er'
                        forms['superlative'] = word + 'est'
                
                # Two-syllable adjectives with specific rules
                elif syllables == 2:
                    if word.endswith('y'):
                        # happy → happier/happiest
                        forms['comparative'] = word[:-1] + 'ier'
                        forms['superlative'] = word[:-1] + 'iest'
                    elif word.endswith('le'):
                        # simple → simpler/simplest
                        forms['comparative'] = word + 'r'
                        forms['superlative'] = word + 'st'
                    elif word.endswith(('er', 'ow')):
                        # clever → cleverer, narrow → narrower
                        forms['comparative'] = word + 'er'
                        forms['superlative'] = word + 'est'
                    else:
                        # Default for other two-syllable
                        forms['comparative'] = 'more ' + word
                        forms['superlative'] = 'most ' + word
                
                # Three+ syllables: use more/most
                else:
                    forms['comparative'] = 'more ' + word
                    forms['superlative'] = 'most ' + word
                
    except ImportError:
        print("Warning: inflect library not found. Install with: pip install inflect")
        # Return empty forms
        return forms
    
    return forms

def process_text(text, file_type, nlp, answer_variations=None):
    if not text:
        return []
    
    doc = nlp(text)
    vocab_data = []
    
    # Track which tokens are part of named entities
    entity_token_ids = set()
    for ent in doc.ents:
        for token in ent:
            entity_token_ids.add(token.i)
    
    # Process regular tokens
    for token in doc:
        if token.i not in entity_token_ids and not token.is_stop and not token.is_punct and len(token.text) > 2 and token.text.isalpha():
            vocab_data.append({
                "unit": token.text,
                "unit_lower": token.text.lower(),
                "lemma": token.lemma_.lower(),
                "pos": token.pos_,
                "type": "Word",
                "file_type": file_type,
                "answer_variations": answer_variations.get(token.text.lower(), set()) if answer_variations else set()
            })
    
    # Process noun chunks
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.strip()
        if 2 <= len(chunk_text.split()) <= 4:
            vocab_data.append({
                "unit": chunk_text,
                "unit_lower": chunk_text.lower(),
                "lemma": chunk.lemma_.lower(),
                "pos": "NOUN_PHRASE",
                "type": "Phrase",
                "file_type": file_type,
                "answer_variations": answer_variations.get(chunk_text.lower(), set()) if answer_variations else set()
            })
    
    # Process named entities
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "LOC"]:
            vocab_data.append({
                "unit": ent.text,
                "unit_lower": ent.text.lower(),
                "lemma": ent.text.lower(),
                "pos": "PROPN",
                "type": "Proper Noun",
                "file_type": file_type,
                "answer_variations": answer_variations.get(ent.text.lower(), set()) if answer_variations else set()
            })
    
    return vocab_data

def calculate_weighted_frequency(data_folder="dse_listening_data"):
    print("="*80)
    print("ENHANCED HKDSE VOCABULARY ANALYSIS (with inflect)")
    print("="*80)
    
    nlp = check_spacy_model()
    print("✓ spaCy model loaded")
    
    if not os.path.exists(data_folder):
        print(f"Error: Folder '{data_folder}' not found")
        sys.exit(1)
    
    files = [f for f in os.listdir(data_folder) if f.endswith(".txt")]
    script_files = [f for f in files if "_script" in f]
    answer_files = [f for f in files if "_answer" in f]
    
    print(f"Found {len(script_files)} script files and {len(answer_files)} answer files")
    
    # First, process answer files to extract variations
    all_answer_variations = defaultdict(set)
    
    for filename in answer_files:
        filepath = os.path.join(data_folder, filename)
        content = read_file(filepath)
        if content:
            variations = parse_answer_file(content)
            for key, values in variations.items():
                all_answer_variations[key].update(values)
    
    print(f"✓ Extracted answer variations from marking schemes")
    
    # Now process all files for vocabulary
    all_vocab = defaultdict(lambda: {
        "count_script": 0,
        "count_answer": 0,
        "lemma": "",
        "pos": "",
        "type": "",
        "sources": set(),
        "original_forms": set(),
        "answer_variations": set()
    })
    
    # Process all text files
    for filename in sorted(files):
        if "marking_rules" in filename:
            continue  # Skip marking rules files
            
        filepath = os.path.join(data_folder, filename)
        print(f"Processing: {filename}")
        
        content = read_file(filepath)
        if not content:
            continue
        
        year = filename[:4]
        file_type = "script" if "_script" in filename else "answer"
        
        vocab_list = process_text(content, file_type, nlp, all_answer_variations)
        
        for item in vocab_list:
            unit = item["lemma"]
            
            if file_type == "script":
                all_vocab[unit]["count_script"] += 1
            else:
                all_vocab[unit]["count_answer"] += 1
            
            all_vocab[unit]["lemma"] = unit
            all_vocab[unit]["pos"] = item["pos"]
            all_vocab[unit]["type"] = item["type"]
            all_vocab[unit]["sources"].add(year)
            all_vocab[unit]["original_forms"].add(item["unit"])
            all_vocab[unit]["answer_variations"].update(item["answer_variations"])
            # Also add variations from the marking schemes
            all_vocab[unit]["answer_variations"].update(all_answer_variations.get(unit, set()))
    
    print("-"*80)
    print("Calculating weighted scores (Script x2, Answer x3)")
    print("-"*80)
    
    results = []
    for unit, data in all_vocab.items():
        weighted_score = (data["count_script"] * 2) + (data["count_answer"] * 3)
        
        if weighted_score >= 4:
            # Generate display unit
            display_unit = unit
            if data["type"] == "Proper Noun" and data["original_forms"]:
                capitalized_forms = [f for f in data["original_forms"] if f[0].isupper()]
                if capitalized_forms:
                    display_unit = sorted(capitalized_forms)[0]
            
            # Generate grammatical forms
            forms = generate_grammatical_forms(unit, data["pos"], nlp)
            
            # Combine all variations
            all_variations = data["original_forms"].union(data["answer_variations"])
            
            results.append({
                "ID": 0,
                "Vocabulary Unit": display_unit,
                "Type": data["type"],
                "Part of Speech": data["pos"],
                "Plural": forms.get('plural', ''),
                "Past Tense": forms.get('past_tense', ''),
                "Comparative / Superlative": f"{forms.get('comparative', '')} / {forms.get('superlative', '')}" if 'comparative' in forms else '',
                "Accepted Answer Variations": ", ".join(sorted(all_variations))[:200],
                "Weighted Score": weighted_score,
                "Source": ", ".join(sorted(data["sources"]))
            })
    
    results.sort(key=lambda x: x["Weighted Score"], reverse=True)
    
    for i, item in enumerate(results, 1):
        item["ID"] = i
    
    return results[:500]

def create_raw_frequency_log(data_folder="dse_listening_data"):
    """Create the raw frequency log as required by the task"""
    nlp = check_spacy_model()
    files = [f for f in os.listdir(data_folder) if f.endswith(".txt") and "marking_rules" not in f]
    
    log_data = []
    
    for filename in sorted(files):
        filepath = os.path.join(data_folder, filename)
        content = read_file(filepath)
        if not content:
            continue
        
        year = filename[:4]
        file_type = "script" if "_script" in filename else "answer"
        
        # Count frequencies for this file
        vocab_count = defaultdict(int)
        doc = nlp(content.lower())
        
        for token in doc:
            if not token.is_stop and not token.is_punct and len(token.text) > 2 and token.text.isalpha():
                vocab_count[token.lemma_] += 1
        
        # Add to log
        for vocab, count in vocab_count.items():
            log_data.append({
                "Vocabulary Unit": vocab,
                "Year": year,
                "File Type": file_type,
                "Frequency in this file": count
            })
    
    return pd.DataFrame(log_data)

def create_output(data_folder="dse_listening_data"):
    results = calculate_weighted_frequency(data_folder)
    
    if not results:
        print("No vocabulary found")
        return None
    
    df = pd.DataFrame(results)
    
    print("="*80)
    print("TOP 20 VOCABULARY UNITS")
    print("="*80)
    
    display_df = df.head(20)[["ID", "Vocabulary Unit", "Type", "Weighted Score", "Source"]]
    print(display_df.to_string(index=False))
    
    print("="*80)
    print(f"Total units extracted: {len(results)}")
    print("="*80)
    
    os.makedirs("output", exist_ok=True)
    
    # Create main Excel file with both sheets
    excel_file = "output/dse_vocabulary_analysis.xlsx"
    
    try:
        with pd.ExcelWriter(excel_file) as writer:
            # Sheet 1: Top 500 Core Vocabulary
            df.to_excel(writer, sheet_name="Top 500 Core Vocabulary", index=False)
            
            # Sheet 2: Raw Data Log
            log_df = create_raw_frequency_log(data_folder)
            log_df.to_excel(writer, sheet_name="Raw Data Log", index=False)
            
        print(f"✓ Saved to: {excel_file}")
    except Exception as e:
        print(f"Excel save failed: {str(e)}")
    
    # Also save as CSV for compatibility
    try:
        df.to_csv("output/dse_vocab_top500.csv", index=False)
        log_df.to_csv("output/raw_frequency_log.csv", index=False)
        print("✓ Also saved CSV versions")
    except Exception as e:
        print(f"CSV save failed: {str(e)}")
    
    return df

if __name__ == "__main__":
    try:
        df = create_output()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)