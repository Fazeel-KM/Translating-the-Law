from mistralai import Mistral, DocumentURLChunk
from openai import OpenAI  # For DeepSeek API
from pathlib import Path
import json
import os
from dotenv import load_dotenv
import re
import time
import random

# Load API keys from .env file
print("Loading API keys from .env file...")
load_dotenv()
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
deepseek_client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
print("API keys loaded successfully.")

# Define input and output folders as lists
input_folders = [Path(r"your input folder")]
output_dirs = [Path(r"your output folder")]
def process_with_retry(client, method, max_retries=5, base_delay=10, max_delay=60, **kwargs):
    """Helper function to handle API calls with exponential backoff."""
    for attempt in range(max_retries):
        try:
            if method == "mistral_chat":
                return client.chat.complete(**kwargs)
            elif method == "deepseek_chat":
                return client.chat.completions.create(**kwargs)
            elif method == "upload":
                return client.files.upload(**kwargs)
            elif method == "ocr":
                return client.ocr.process(**kwargs)
            elif method == "signed_url":
                return client.files.get_signed_url(**kwargs)
        except Exception as e:
            if "Status 429" in str(e) or "rate limit" in str(e).lower():
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                print(f"Rate limit exceeded (attempt {attempt + 1}/{max_retries}). Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print(f"Unexpected error: {e}")
                raise
    print(f"Max retries ({max_retries}) reached. Skipping this operation.")
    return None

# Simple token estimation function (approximate)
def estimate_tokens(text):
    """Estimate token count: ~1.3 tokens per word + 1 token per newline."""
    words = len(text.split())
    newlines = text.count('\n')
    return int(words * 1.3 + newlines)

# Process each input folder and its corresponding output directory
for input_folder, output_dir in zip(input_folders, output_dirs):
    print(f"\nProcessing input folder: {input_folder}")
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(input_folder.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files in {input_folder}")

    # Process each PDF file in the current input folder
    for pdf_file_path in pdf_files:
        print(f"\nProcessing file: {pdf_file_path.name}")

        # Upload the PDF file to Mistral AI for OCR
        print("Uploading PDF to Mistral AI...")
        with open(pdf_file_path, "rb") as pdf_file:
            uploaded_file = process_with_retry(
                mistral_client,
                "upload",
                file={
                    "file_name": pdf_file_path.stem,
                    "content": pdf_file.read(),
                },
                purpose="ocr"
            )
        if not uploaded_file:
            print(f"Failed to upload {pdf_file_path.name}. Skipping.")
            continue
        print(f"PDF uploaded successfully. File ID: {uploaded_file.id}")

        # Get signed URL for the uploaded PDF
        print("Retrieving signed URL for the uploaded PDF...")
        signed_url = process_with_retry(
            mistral_client,
            "signed_url",
            file_id=uploaded_file.id,
            expiry=1
        )
        if not signed_url:
            print(f"Failed to retrieve signed URL for {pdf_file_path.name}. Skipping.")
            continue
        print(f"Signed URL retrieved: {signed_url.url}")

        # Process the PDF using OCR
        print("Processing PDF with OCR...")
        pdf_response = process_with_retry(
            mistral_client,
            "ocr",
            document=DocumentURLChunk(document_url=signed_url.url),
            model="mistral-ocr-latest",
            include_image_base64=True
        )
        if not pdf_response:
            print(f"Failed to process OCR for {pdf_file_path.name}. Skipping.")
            continue
        print("OCR processing completed.")

        # Convert OCR response to dictionary
        print("Converting OCR response to dictionary...")
        response_dict = pdf_response.model_dump()
        print("OCR response converted to dictionary.")

        # Extract text from the 'markdown' key in each page, preserving paragraph structure
        print("Extracting text from OCR response...")
        try:
            if 'pages' in response_dict:
                extracted_text = "\n\n".join(page.get('markdown', '') for page in response_dict['pages'])
            else:
                extracted_text = response_dict.get('markdown', '') or response_dict.get('text', '') or response_dict.get('content', '')
            if not extracted_text.strip():
                raise ValueError("No text extracted from OCR response")
            print("Text extracted successfully.")
        except Exception as e:
            print(f"Error extracting text: {e}")
            extracted_text = ""  # Fallback to empty string

        # Filter out Hindi Unicode and non-English text
        print("Filtering out Hindi and non-English text...")
        extracted_text = re.sub(r'\\u[0-9A-Fa-f]{4}', '', extracted_text)  # Remove Unicode escapes
        extracted_text = re.sub(r'[^\x00-\x7F]+', '', extracted_text)      # Remove non-ASCII characters
        extracted_text = re.sub(r'\s+', ' ', extracted_text).strip()       # Normalize whitespace
        print("Hindi and non-English text removed.")

        # Split text into paragraphs
        print("Splitting text into paragraphs...")
        paragraphs = []
        for p in extracted_text.split('\n\n'):
            p = p.strip()
            if p:
                para_tokens = estimate_tokens(p)
                if para_tokens > 5000:  # Split large paragraphs
                    words = p.split()
                    sub_chunk = []
                    sub_token_count = 0
                    for word in words:
                        word_tokens = estimate_tokens(word)
                        if sub_token_count + word_tokens > 5000 and sub_chunk:
                            paragraphs.append(" ".join(sub_chunk))
                            sub_chunk = [word]
                            sub_token_count = word_tokens
                        else:
                            sub_chunk.append(word)
                            sub_token_count += word_tokens
                    if sub_chunk:
                        paragraphs.append(" ".join(sub_chunk))
                else:
                    paragraphs.append(p)
        print(f"Extracted {len(paragraphs)} paragraphs.")

        # Group paragraphs into chunks with token limit
        print("Grouping paragraphs into chunks...")
        chunks = []
        current_chunk = []
        current_token_count = 0
        max_tokens = 15000  # Further reduced for smaller chunks

        for para in paragraphs:
            para_token_count = estimate_tokens(para)
            print(f"Paragraph tokens: {para_token_count}")
            if current_token_count + para_token_count > max_tokens and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_token_count = para_token_count
            else:
                current_chunk.append(para)
                current_token_count += para_token_count
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        print(f"Split into {len(chunks)} chunks.")

        # Process each chunk with DeepSeek API and save as separate JSON files
        print("Processing chunks with DeepSeek API...")
        for i, chunk in enumerate(chunks):
            chunk_tokens = estimate_tokens(chunk)
            print(f"Processing chunk {i + 1}/{len(chunks)}: {chunk[:100]}... (Estimated tokens: {chunk_tokens})")

            # Skip non-substantive or oversized chunks
            if len(chunk.split()) < 50 or "rule" not in chunk.lower():
                print(f"Skipping chunk {i + 1}: insufficient substantive content.")
                continue
            if chunk_tokens > max_tokens:
                print(f"Skipping chunk {i + 1}: exceeds token limit ({chunk_tokens} > {max_tokens}).")
                continue

            # Original prompt (unchanged)
            prompt = f"""
You are an expert legal analyst tasked with structuring the following English text into an exhaustive set of Alpaca-style JSON entries for training a language model on legal rule documents. Each entry must include an 'instruction', 'input', and 'output', using the exact English words from the text without summarizing, altering, or omitting any information. Your goal is to capture all substantive legal content—such as rules, sub-rules, procedures, definitions, actions, and changes—in its full context, with the relevant rule or section explicitly referenced in both the 'input' and 'output' where applicable.

Follow these steps:

1. **Focus exclusively on substantive legal content:**
   - Create separate entries for each distinct rule, sub-rule, definition, procedure, action, or change introduced in the text.
   - Include the full context by referencing the rule number, sub-rule designation, or section in both the 'input' and 'output'.
   - For each rule or significant provision, ensure entries address:
     - What the rule or provision states
     - The specific procedure, action, or change it introduces
     - Any conditions, exceptions, or definitions tied to it
   - For definitions, create individual entries stating the term and its exact definition.

2. **Structure each entry as a question-answer pair:**
   - The 'instruction' field must be a question querying a specific legal detail, such as a rule, procedure, definition, or action (e.g., "What does rule 3(1) state about preliminary scrutiny?", "What is the definition of 'Tribunal'?", "What procedure does rule 4(2) establish?").
   - The 'output' field must provide a complete answer using the exact text from the document, with the rule number or section referenced for clarity.

3. **Minimize non-substantive details:**
   - Do not create entries for publication details (e.g., draft publication date, objection process, final enactment process) unless they directly tie to a rule or legal action.
   - Limit foundational context to a single entry (e.g., "What is the purpose of these rules?") only if it clarifies the substantive content.

4. **Ensure exhaustiveness:**
   - Every rule, sub-rule, definition, procedure, action, or change must be accounted for in at least one entry.
   - Generate as many entries as necessary to cover all substantive legal content, with a minimum of 15 entries to reflect the document’s complexity.

5. **Return only a valid JSON array:**
   - The output must be a JSON array containing all entries, with no additional text outside the array.

Text:
{chunk}
"""
            prompt_tokens = estimate_tokens(prompt)
            total_tokens = prompt_tokens + chunk_tokens
            print(f"Prompt tokens: {prompt_tokens}, Total tokens: {total_tokens}")

            if total_tokens > 65536:
                print(f"Skipping chunk {i + 1}: Total tokens ({total_tokens}) exceeds 65536.")
                continue

            # Call DeepSeek API for this chunk
            response = process_with_retry(
                deepseek_client,
                "deepseek_chat",
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=8192  # Increased to allow longer outputs
            )
            if not response:
                print(f"Failed to generate JSON for chunk {i + 1} of {pdf_file_path.name}. Skipping.")
                continue
            alpaca_json = response.choices[0].message.content
            print(f"DeepSeek API response received for chunk {i + 1}.")
            print(f"Raw API response: {alpaca_json[:200]}...")  # Log start of response for debugging

            # Save this chunk’s JSON to a separate file
            output_file_path = output_dir / f"{pdf_file_path.stem}_chunk{i + 1}_alpaca.json"
            try:
                alpaca_data = json.loads(alpaca_json)
                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    json.dump(alpaca_data, output_file, indent=4)
                print(f"JSON saved successfully to: {output_file_path}")
            except json.JSONDecodeError:
                print(f"Failed to parse Alpaca JSON for chunk {i + 1}, saving raw response")
                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(alpaca_json)
                print(f"Raw response saved to: {output_file_path}")

    print(f"All files in {input_folder} processed. Structured JSON files saved in: {output_dir}")

print("\nAll input folders processed.")