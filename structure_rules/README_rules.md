# Legal Rules Structuring Script

This repository includes two Python scripts designed to process and structure legal rule PDFs into Alpaca-style JSON format. These scripts are tailored specifically for legal **rules** (not Acts).

## Scripts

- **`rule_formatter_small(1-10pages)`** – For PDFs less than 10 pages
- **`rule_formatter_long(more_than_10pages)`** – For PDFs longer than 10 pages (includes advanced chunking to handle token limits)


## Features
- OCR processing of scanned legal rule PDFs
- Cleans non-English/Hindi content
- Splits content into token-limited chunks
- Generates detailed JSON entries in `instruction`, `input`, and `output` format for each legal rule, sub-rule, procedure, or definition
- Uses retry logic for stable API calls

## Folder Setup
- Place input PDFs in the `your input folder`
- Output structured JSON files will be saved in the `your output folder`

## How to Use
1. Add your DeepSeek and Mistral API keys to a `.env` file:
2. Update the `input_folders` and `output_dirs` lists in the script.
3. Run the script:

