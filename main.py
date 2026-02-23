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
    new_column: str = "text_clean",
    in_delimiter: str = ",",
    out_delimiter: str = ",",
) -> None:
    with open(in_path, encoding="utf-8", errors="replace", newline="") as fin, \
         open(out_path, "w", encoding="utf-8", newline="") as fout:

        reader = csv.DictReader(fin, delimiter=in_delimiter)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header row (fieldnames).")

        if text_column not in reader.fieldnames:
            raise ValueError(
                f"Column '{text_column}' not found. Available: {reader.fieldnames}"
            )

        fieldnames = list(reader.fieldnames)
        if new_column not in fieldnames:
            fieldnames.append(new_column)

        writer = csv.DictWriter(
    fout,
    fieldnames=fieldnames,
    delimiter=out_delimiter,
    quoting=csv.QUOTE_MINIMAL,
)
        writer.writeheader()

        for row in reader:
            raw = row.get(text_column, "") or ""
            row[new_column] = cleaner_v4(raw)   # uses your Phase 1 cleaner
            writer.writerow(row)

import argparse

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase 1: Text cleaning utilities (files + CSV)."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_txt = subparsers.add_parser("clean-txt", help="Clean a raw text file line-by-line.")
    p_txt.add_argument("--in", dest="in_path", required=True, help="Input .txt path")
    p_txt.add_argument("--out", dest="out_path", required=True, help="Output .txt path")

    p_stats = subparsers.add_parser("stats", help="Compute basic corpus stats for a text file.")
    p_stats.add_argument("--in", dest="in_path", required=True, help="Input .txt path")
    p_stats.add_argument("--topk", type=int, default=15, help="Top-K tokens to display")

    p_csv = subparsers.add_parser("clean-csv", help="Add a cleaned text column to a CSV.")
    p_csv.add_argument("--in", dest="in_path", required=True, help="Input CSV path")
    p_csv.add_argument("--out", dest="out_path", required=True, help="Output CSV path")
    p_csv.add_argument("--col", dest="text_column", required=True, help="Name of text column to clean")
    p_csv.add_argument("--newcol", dest="new_column", default="text_clean", help="Name of new cleaned column")
    p_csv.add_argument("--in-delim", dest="in_delimiter", default=",", help="Input delimiter, e.g. ',' or ';'")
    p_csv.add_argument("--out-delim", dest="out_delimiter", default=",", help="Output delimiter, e.g. ',' or ';'")

    # optional demo flag (so you can run quick checks intentionally)
    p_demo = subparsers.add_parser("demo", help="Run the built-in demo on raw.txt and sample.csv (if present).")
    p_demo.add_argument("--topk", type=int, default=10, help="Top-K tokens for stats in demo")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "clean-txt":
        clean_lines(args.in_path, args.out_path)
        print(f"Cleaned text written to: {args.out_path}")
        return 0

    if args.command == "stats":
        s = basic_stats(args.in_path, top_k=args.topk)
        print(s)
        return 0

    if args.command == "clean-csv":
        clean_csv_column(
            args.in_path,
            args.out_path,
            text_column=args.text_column,
            new_column=args.new_column,
            in_delimiter=args.in_delimiter,
            out_delimiter=args.out_delimiter,
        )
        print(f"Cleaned CSV written to: {args.out_path}")
        return 0

    if args.command == "demo":
        clean_lines("raw.txt", "clean.txt")
        print(basic_stats("clean.txt", top_k=args.topk))
        clean_csv_column("sample.csv", "sample_clean.csv", text_column="title")
        print("Demo complete: clean.txt and sample_clean.csv written.")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())