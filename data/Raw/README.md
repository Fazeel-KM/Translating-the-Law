#  Data Overview

This project uses multiple datasets to process and structure Indian legal documents related to the **Ministry of Road Transport and Highways**. The datasets are organized into zipped folders for modularity and storage efficiency.

---

### 1. `rules_categorised.zip`

- **Source**: [India Code](https://www.indiacode.nic.in/)
- **Description**: Contains a sample of official **rules**, categorized by:
  - The **Act** they are associated with
  - The **size** of the document (e.g., small or long rules)

These rule PDFs are preprocessed using OCR and converted into structured Alpaca-style format as part of this pipeline.

---

### 2. `annotatedCentralActs.zip`

- **Source**: [Zenodo Record #5088102](https://zenodo.org/records/5088102)
- **Description**: A complete archive of **all Indian legislative acts**.
  -  This collection is not limited to road transport–related laws.
  - A filtering script (`extract_road_transport_acts.ipynb`) was used to extract only acts relevant to the **Ministry of Road Transport and Highways**.

---

### 3. `Ministry_of_Road_Transport_and_Highways_acts.zip`

- **Source**: Extracted from `all_indian_acts.zip`
- **Description**: A curated subset of acts **specifically relevant** to the Ministry of Road Transport and Highways.
  - This dataset forms the legal basis for training and structuring tasks in this project.

---

### Note

Due to GitHub’s file size limits, these ZIP files are **not committed** directly to the repository.  
Please ensure they are downloaded and extracted manually before executing the relevant notebooks or scripts.


