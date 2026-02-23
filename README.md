# Phase 1 – Python Text Cleaning Toolkit

A lightweight, dependency-free Python utility for cleaning and inspecting raw text data.

This project focuses on building a robust text preprocessing foundation using only the Python standard library. It is designed as the first phase of a structured NLP skills development plan.

---

## Features

### Text Cleaning
- Lowercasing
- ASCII punctuation normalization (converted to spaces)
- Whitespace normalization
- Unicode normalization (NFKC)
- Removal of standalone combining marks
- Token filtering (retain tokens containing letters or numbers)

### File Processing
- Safe UTF-8 file handling (`encoding="utf-8"`, `errors="replace"`)
- Line-by-line processing for memory efficiency
- Basic corpus statistics:
  - number of lines
  - number of characters
  - number of tokens
  - average tokens per line
  - vocabulary size
  - top-K token frequency

### CSV Utility
- Cleans a specified text column
- Writes a new CSV with an added cleaned column
- Supports configurable input/output delimiters
- Safe CSV writing with proper quoting

---

## Usage
```bash
### Clean a text file
python main.py clean-txt --in raw.txt --out clean.txt

### Compute corpus statistics
python main.py stats --in clean.txt --topk 15

### Clean a CSV column
python main.py clean-csv --in sample.csv --out sample_clean.csv --col title

### Run a demo
python main.py demo --topk 10
