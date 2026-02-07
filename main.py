import string
import unicodedata

def cleaner_v3(text: str) -> str:
    # Normalize unicode (helps make visually similar chars consistent)
    text = unicodedata.normalize("NFKC", text)

    # Lowercase
    text = text.lower()

    # Replace ASCII punctuation with spaces (keeps unicode punctuation like — for now)
    text = "".join(char if char not in string.punctuation else " " for char in text)

    # Token filter: keep tokens that contain at least one letter or number
    tokens = []
    for tok in text.split():
        if any(unicodedata.category(ch)[0] in {"L", "N"} for ch in tok):
            tokens.append(tok)

    return " ".join(tokens)


def clean_lines(in_path: str, out_path: str) -> None:
    with open(in_path, encoding="utf-8", errors="replace") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:
        for line in fin:
            cleaned = cleaner_v3(line)
            if cleaned:                 # drop empty lines after cleaning
                fout.write(cleaned + "\n")
from collections import Counter

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
clean_lines("sample_raw.txt", "clean.txt")
stats = basic_stats("clean.txt", top_k=15)
print(stats)
