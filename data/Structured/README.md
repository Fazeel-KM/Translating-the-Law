#  Structured Data

This folder contains the final structured JSON outputs generated from OCR and LLM-based processing of legal documents. These files are formatted in **Alpaca-style JSON**, designed for training or fine-tuning legal language models.

---

### Contents

| File Name                            | Description                                                                 |
|-------------------------------------|-----------------------------------------------------------------------------|
| `combined_json_acts.json`           | Contains structured entries extracted only from the **Ministry of Road Transport and Highways Acts**. |
| `combine_json_rules.json`           | Contains structured entries from the **rules** associated with the extracted acts. |
| `combined_json_rules_and_acts.json` | A merged file that combines **both acts and rules** into a single dataset. Useful for end-to-end model training. |

---

### Format

Each JSON file is an array of entries with the following structure:

```json
{
  "instruction": "What does Rule 3(1) state about preliminary requirements?",
  "input": "Rule 3(1) of the XYZ Rules...",
  "output": "Rule 3(1) specifies that..."
}
