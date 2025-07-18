import json
from pathlib import Path
import os

import requests

MODEL_NAME = "mistral"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
BOOK_FILE = Path("book_text.txt")
OUTPUT_FILE = Path("characters.json")
SAVE_EVERY = 10

# Create output file
if not OUTPUT_FILE.exists():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def split_into_paragraphs(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]

def process_paragraph(paragraph):
    prompt = f"""
    You are an expert in fictional character profiling.

    From the following paragraph, extract a structured character description in this JSON format:

    {{
    "character_id": "...",
    "name": "...",
    "dialogue_samples": [{{"quote": "...", "context": "...", "book": "...", "emotional_state": "...", "topic": "..."}}],
    "personality_traits": {{"trait": 0.0}},
    "speaking_patterns": {{"formality": "...", "vocabulary_complexity": "...", "sentence_length": "..."}},
    "knowledge_domains": ["..."]
    }}

    If the paragraph contains no character activity or dialogue, respond with just the single word:
    **skip**

    Paragraph:
    \"\"\"
    {paragraph}
    \"\"\"

    Output:
    """
    
    try:
        response = requests.post(OLLAMA_API_URL, json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        })
        
        response.raise_for_status()
        raw_result = response.json().get("response", "").strip()
        
        if raw_result.lower() == "skip":
            return "skip"
        
        try:
            return json.loads(raw_result)
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            return {"error": "Failed to parse JSON", "raw_response": raw_result}
    
    except requests.RequestException as e:  # ✅ Fixed typo
        print(f"Request Error: {e}")
        return {"error": "Request failed", "details": str(e)}
 
def save_batch_to_file(batch, output_file="all_characters.json"):
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    existing = []
                else:
                    existing = json.loads(content)
        except json.JSONDecodeError:
            print(f" Warning: {output_file} is not valid JSON. Replacing it.")
            existing = []
    else:
        existing = []

    existing.extend(batch)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

        
def main():
    # Load full book
    with open(BOOK_FILE, "r", encoding="utf-8") as f:
        full_text = f.read()
        
    paragraphs = split_into_paragraphs(full_text)
    total_paras = len(paragraphs)
    print(paragraphs[0])
    
    print(f"Total paragraphs: {total_paras}")
    
    batch = []
    process_count = 0
    
    for idx, para in enumerate(paragraphs, start=1):
        print(f"Processing paragraph {idx}/{total_paras}") 
        result = process_paragraph(para)
        
        if result == 'skip':
            print(f"Paragraph {idx} skipped")
            continue
        
        batch.append(result)
        process_count += 1
        
        if process_count % SAVE_EVERY == 0:
            save_batch_to_file(batch)
            print(f"Saved {len(batch)} items to {OUTPUT_FILE}")
            batch = []
    
    # Save any leftover paragraphs after loop ends
    if batch:
        save_batch_to_file(batch)
        print(f"✅ Saved final {len(batch)} items to {OUTPUT_FILE}")

    print(f"Processing complete. Total processed paragraphs: {process_count}")

if __name__ == "__main__":
    main()