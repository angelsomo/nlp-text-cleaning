import csv
import string
import unicodedata
from collections import Counter

# ---------- Cleaning functions ----------

def strip_leading_marks(token: str) -> str:
    # Remove combining marks at the start of the token
    i = 0
    while i < len(token) and unicodedata.category(token[i]) == "Mn":
        i += 1
    return token[i:]

def cleaner_v4(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()

    text = "".join(char if char not in string.punctuation else " " for char in text)

    tokens = []
    for tok in text.split():
        tok = strip_leading_marks(tok)
        if not tok:
            continue
        # keep tokens that contain at least one letter/number
        if any(unicodedata.category(ch)[0] in {"L", "N"} for ch in tok):
            tokens.append(tok)

    return " ".join(tokens)

# ---------- File-level processing ----------


def clean_lines(in_path: str, out_path: str) -> None:
    with open(in_path, encoding="utf-8", errors="replace") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:
        for line in fin:
            cleaned = cleaner_v4(line)
            if cleaned:                 # drop empty lines after cleaning
                fout.write(cleaned + "\n")


def basic_stats(path: str, top_k: int = 20):
    n_lines = 0
    n_chars = 0
    n_tokens = 0
    vocab = Counter()

    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            n_lines += 1
            n_chars += len(line)
            tokens = line.split()
            n_tokens += len(tokens)
            vocab.update(tokens)

    avg_tokens_per_line = (n_tokens / n_lines) if n_lines else 0

    return {
        "lines": n_lines,
        "chars": n_chars,
        "tokens": n_tokens,
        "avg_tokens_per_line": avg_tokens_per_line,
        "vocab_size": len(vocab),
        "top_tokens": vocab.most_common(top_k),
    }

# ---------- CSV utilities ----------

def clean_csv_column(
    in_path: str,
    out_path: str,
    text_column: str,
    new_column: str = "text_clean"
) -> None:
    with open(in_path, encoding="utf-8", errors="replace", newline="") as fin, \
         open(out_path, "w", encoding="utf-8", newline="") as fout:

        reader = csv.DictReader(fin)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row (fieldnames).")

        if text_column not in reader.fieldnames:
            raise ValueError(
                f"Column '{text_column}' not found. Available: {reader.fieldnames}"
            )

        fieldnames = list(reader.fieldnames)
        if new_column not in fieldnames:
            fieldnames.append(new_column)

        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            raw = row.get(text_column, "") or ""
            row[new_column] = cleaner_v4(raw)   # uses your Phase 1 cleaner
            writer.writerow(row)

if __name__ == "__main__":
    # text file demo
    clean_lines("raw.txt", "clean.txt")
    print(basic_stats("clean.txt"))

    # CSV demo
    clean_csv_column("sample.csv", "sample_clean.csv", text_column="title")
