# Road Transport Acts – Extraction & Structuring

This folder contains two Jupyter notebooks used to extract and format legal acts related to road transport from a larger dataset of central annotated acts.

## Overview

### 1. extract_road_transport_acts.ipynb
This notebook extracts relevant acts from a zipped archive of central acts.

- Input: `annotatedCentralActs.zip`
- Workflow:
  - Unzips the archive to `legal_acts/`
  - Filters acts whose `act_title` matches known road transport-related acts
  - Copies the matching JSONs to the `matching_jsons/` folder after cleaning filenames

### 2. legal_acts_formatter.ipynb
This notebook structures the filtered acts using the Hugging Face `flan-t5-large` model.

- Input: JSON files from `matching_jsons/`
- Workflow:
  - Extracts act definitions and section contents
  - Generates 3 legal questions per section using the FLAN-T5 model
  - Saves the output in Alpaca-style format to `formatted_acts/`

## Folder Structure

