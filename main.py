import csv
import string
import unicodedata
import argparse
from collections import Counter
from typing import Dict, Any


# ============================================================
# Cleaning Functions
# ============================================================

def strip_leading_marks(token: str) -> str:
    """
    Remove leading Unicode combining marks (category 'Mn')
    from a token.
    """
    i = 0
    while i < len(token) and unicodedata.category(token[i]) == "Mn":
        i += 1
    return token[i:]


def cleaner_v4(text: str) -> str:
    """
    Normalize and clean text:
    - Unicode normalization (NFKC)
    - Lowercasing
    - Replace ASCII punctuation with spaces
    - Remove leading combining marks
    - Keep tokens containing at least one letter or number
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()

    text = "".join(
        char if char not in string.punctuation else " "
        for char in text
    )

    tokens = []
    for tok in text.split():
        tok = strip_leading_marks(tok)

        if not tok:
            continue

        if any(unicodedata.category(ch)[0] in {"L", "N"} for ch in tok):
            tokens.append(tok)

    return " ".join(tokens)


# ============================================================
# File-Level Processing
# ============================================================

def clean_lines(in_path: str, out_path: str) -> None:
    """
    Clean a text file line-by-line and write output.
    """
    with open(in_path, encoding="utf-8", errors="replace") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:

        for line in fin:
            cleaned = cleaner_v4(line)
            if cleaned:
                fout.write(cleaned + "\n")


def basic_stats(path: str, top_k: int = 20) -> Dict[str, Any]:
    """
    Compute basic corpus statistics for a cleaned text file.
    """
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


# ============================================================
# CSV Utilities
# ============================================================

def clean_csv_column(
    in_path: str,
    out_path: str,
    text_column: str,
    new_column: str = "text_clean",
    in_delimiter: str = ",",
    out_delimiter: str = ",",
) -> None:
    """
    Clean a specified text column in a CSV file and
    write a new CSV with an added cleaned column.
    """
    with open(in_path, encoding="utf-8", errors="replace", newline="") as fin, \
         open(out_path, "w", encoding="utf-8", newline="") as fout:

        reader = csv.DictReader(fin, delimiter=in_delimiter)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header row (fieldnames).")

        if text_column not in reader.fieldnames:
            raise ValueError(
                f"Column '{text_column}' not found. "
                f"Available columns: {reader.fieldnames}"
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
            raw = row.get(text_column) or ""
            row[new_column] = cleaner_v4(raw)
            writer.writerow(row)


# ============================================================
# CLI (Command Line Interface)
# ============================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase 1: Text cleaning utilities (files + CSV)."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # clean-txt
    p_txt = subparsers.add_parser(
        "clean-txt",
        help="Clean a raw text file line-by-line."
    )
    p_txt.add_argument("--in", dest="in_path", required=True)
    p_txt.add_argument("--out", dest="out_path", required=True)

    # stats
    p_stats = subparsers.add_parser(
        "stats",
        help="Compute corpus statistics for a text file."
    )
    p_stats.add_argument("--in", dest="in_path", required=True)
    p_stats.add_argument("--topk", type=int, default=15)

    # clean-csv
    p_csv = subparsers.add_parser(
        "clean-csv",
        help="Add a cleaned text column to a CSV."
    )
    p_csv.add_argument("--in", dest="in_path", required=True)
    p_csv.add_argument("--out", dest="out_path", required=True)
    p_csv.add_argument("--col", dest="text_column", required=True)
    p_csv.add_argument("--newcol", dest="new_column", default="text_clean")
    p_csv.add_argument("--in-delim", dest="in_delimiter", default=",")
    p_csv.add_argument("--out-delim", dest="out_delimiter", default=",")

    # demo
    p_demo = subparsers.add_parser(
        "demo",
        help="Run built-in demo (raw.txt + sample.csv)."
    )
    p_demo.add_argument("--topk", type=int, default=10)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "clean-txt":
        clean_lines(args.in_path, args.out_path)
        print(f"Cleaned text written to: {args.out_path}")
        return 0

    if args.command == "stats":
        print(basic_stats(args.in_path, top_k=args.topk))
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
        clean_csv_column(
            "sample.csv",
            "sample_clean.csv",
            text_column="title",
        )
        print("Demo complete.")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())