# Legal AI – Indian Regulatory Acts and Rules Structuring

This project automates the structuring and formatting of Indian legal documents, with a focus on central acts and road transport-related rules. It converts unstructured legal content into machine-readable formats to support fine-tuned language models (LLMs) and Retrieval-Augmented Generation (RAG) pipelines for compliance automation.

---

## Folder Structure

### `acts/`
Contains Jupyter notebooks to:
- Extract road transport-related central acts from a larger annotated acts dataset.
- Format the extracted legal acts into instruction-based prompts using FLAN-T5, aligned with the Alpaca format.

### `rules/`
Contains Python scripts for structuring motor vehicle-related rules from the Ministry of Road Transport and Highways.
- `rule_formatter_small(1-10pages).py`: For smaller rule PDFs.
- `rule_formatter_long(more_than_10pages).py`: For longer rule PDFs.
- Outputs structured JSONs suitable for legal LLM processing.

### `model/`
Will include code, checkpoints, and configurations for training or fine-tuning LLMs using techniques like LoRA or Unsloth.

---

## Project Goal

- Build a structured dataset of Indian legal content relevant to road transport and compliance.
- Enable efficient training and inference using LLMs on this structured data.
- Power legal AI tools for compliance checking, legal reasoning, and document understanding.

---

## Getting Started

Each module (`acts/`, `rules/`, and `model/`) includes its own `README` and `requirements.txt` file.

Suggested order of use:
1. Use the `rules/` scripts to format official rules into structured JSON.
2. Use the `acts/` notebooks to extract and structure relevant legal acts.
3. Use the `model/` folder for model training or inference tasks.

---

## Dependencies

Refer to the `requirements.txt` files inside each folder for module-specific dependencies.

---

## License

[Insert license information here, if applicable.]
