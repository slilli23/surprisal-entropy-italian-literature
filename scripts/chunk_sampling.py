"""
02 — Chunk sampling & INCEpTION export
Project: Misurare la creatività linguistica: sorpresa ed entropia come
strumenti di analisi stilistica (Premio di ricerca Dino Buzzetti, AIUCD)
Author: Silvia Lilli

Consumes one CANONICAL CoNLL-U file per text — produced by running Stanza
(tokenize + ssplit + pos) once on the FULL normalized text, so that
start_char/end_char in MISC are GLOBAL offsets into the normalized text.

Stratified exploratory sampling (default):
  - one chunk per quintile, by surface-word position;
  - random anchor sentence, constrained so that its start word index is
    <= (quintile_end_word - MIN_WORDS)  [the "confine-quinto - 500" rule];
  - target = whole sentences accumulated forward from the anchor until the
    surface-word count reaches >= MIN_WORDS (option (i): whole sentences,
    minimal tail overflow accepted; never an intra-sentence cut).

Word counting and offsets use the SURFACE level (multi-word tokens such as
"della" count as ONE word and carry the offsets); POS uses the syntactic
words. Punctuation is excluded from the word count, included in char spans.

Outputs (under out_dir/):
  - inception/{chunk_id}.conllu   target-only, 1 doc per chunk -> 1 project
  - metadata.json                 per-chunk records incl. readable passage
  - offset_map.csv                external realignment map (tool-independent)
  - appendix.md                   human-readable passages (rendered view)
"""

from __future__ import annotations
import csv
import json
import random
import sys
from dataclasses import dataclass, field
from pathlib import Path

# ----------------------------------------------------------------------------
# Parameters (override in __main__ / decisions_log.md)
# ----------------------------------------------------------------------------
SEED = 20260622          # arbitrary but FIXED — logged in decisions_log.md
N_QUINTILES = 5
MIN_WORDS = 500          # surface words, punctuation excluded
CONTEXT_SENTS = 2        # whole sentences of context per side (readable only)
TARGET_OPEN, TARGET_CLOSE = "⟦", "⟧"   # target delimiters in the readable view


# ----------------------------------------------------------------------------
# CoNLL-U parsing
# ----------------------------------------------------------------------------
def parse_misc(misc: str) -> dict:
    d = {}
    if misc and misc != "_":
        for kv in misc.split("|"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                d[k] = v
    return d


@dataclass
class Sent:
    raw_rows: list          # original token lines (verbatim, for export)
    comments: list          # original "# ..." lines
    # surface tokens for reconstruction/counting: (form, space_after, upos)
    surface: list = field(default_factory=list)
    word_count: int = 0     # surface words, excl. PUNCT
    char_start: int | None = None
    char_end: int | None = None
    word_start: int = 0     # cumulative surface words before this sentence
    index: int = 0


def parse_conllu(text: str) -> list[Sent]:
    sents: list[Sent] = []
    comments, rows = [], []

    def flush():
        if not rows:
            return
        s = Sent(raw_rows=list(rows), comments=list(comments))
        covered_until = 0
        for line in rows:
            cols = line.split("\t")
            idx, form, upos, misc = cols[0], cols[1], cols[3], cols[9]
            m = parse_misc(misc)
            sc = int(m["start_char"]) if "start_char" in m else None
            ec = int(m["end_char"]) if "end_char" in m else None
            if "-" in idx:                      # multi-word token (surface)
                lo, hi = (int(x) for x in idx.split("-"))
                covered_until = hi
                space_after = m.get("SpaceAfter") != "No"
                s.surface.append((form, space_after, upos))
                if sc is not None:
                    s.char_start = sc if s.char_start is None else s.char_start
                if ec is not None:
                    s.char_end = ec
                s.word_count += 1               # MWT is never punctuation
            elif "." in idx:                    # empty node — ignore
                continue
            else:
                i = int(idx)
                if i <= covered_until:          # syntactic word inside a MWT
                    continue                    # not a surface token
                space_after = m.get("SpaceAfter") != "No"
                s.surface.append((form, space_after, upos))
                if sc is not None:
                    s.char_start = sc if s.char_start is None else s.char_start
                if ec is not None:
                    s.char_end = ec
                if upos != "PUNCT":
                    s.word_count += 1
        sents.append(s)

    for line in text.splitlines():
        if line.startswith("#"):
            comments.append(line)
        elif line.strip() == "":
            flush()
            comments, rows = [], []
        else:
            rows.append(line)
    flush()

    cum = 0
    for i, s in enumerate(sents):
        s.index = i
        s.word_start = cum
        cum += s.word_count
    return sents


def render(sents: list[Sent]) -> str:
    """Reconstruct readable prose from surface tokens + SpaceAfter."""
    out = []
    for s in sents:
        for form, space_after, _ in s.surface:
            out.append(form + (" " if space_after else ""))
        out.append(" ")          # space between sentences
    return "".join(out).strip()


# ----------------------------------------------------------------------------
# Sampling
# ----------------------------------------------------------------------------
def sample_text(sents: list[Sent], text_id: str, rng: random.Random,
                n_quintiles=N_QUINTILES, min_words=MIN_WORDS,
                context_sents=CONTEXT_SENTS) -> tuple[list[dict], list[str]]:
    W = sum(s.word_count for s in sents)
    edges = [round(k * W / n_quintiles) for k in range(n_quintiles + 1)]
    chunks, flags = [], []

    for q in range(n_quintiles):
        lo_w, hi_w = edges[q], edges[q + 1]
        eligible = [s for s in sents
                    if lo_w <= s.word_start < hi_w
                    and s.word_start <= hi_w - min_words]
        if not eligible:
            flags.append(f"{text_id} q{q+1}: no eligible anchor "
                         f"(quintile span {hi_w-lo_w} < MIN_WORDS={min_words})")
            continue

        anchor = rng.choice(eligible)
        acc, words = [], 0
        for s in sents[anchor.index:]:
            acc.append(s)
            words += s.word_count
            if words >= min_words:
                break

        left = sents[max(0, anchor.index - context_sents):anchor.index]
        end = acc[-1].index
        right = sents[end + 1:end + 1 + context_sents]

        passage = " ".join(p for p in [
            render(left),
            TARGET_OPEN + render(acc) + TARGET_CLOSE,
            render(right)] if p).strip()

        chunks.append({
            "chunk_id": f"{text_id}_q{q+1}",
            "text_id": text_id,
            "quinto": q + 1,
            "anchor_sent_index": anchor.index,
            "target_sent_indices": [s.index for s in acc],
            "target_word_count": words,
            "target_char_start": acc[0].char_start,
            "target_char_end": acc[-1].char_end,
            "n_context_left_sents": len(left),
            "n_context_right_sents": len(right),
            "passage": passage,
            "_target_sents": acc,        # internal, stripped before JSON
        })

    # overlap detection (option (i) can let a tail reach the next anchor)
    for a, b in zip(chunks, chunks[1:]):
        if a["target_sent_indices"][-1] >= b["target_sent_indices"][0]:
            flags.append(f"{text_id}: overlap between {a['chunk_id']} "
                         f"and {b['chunk_id']}")
    return chunks, flags


# ----------------------------------------------------------------------------
# Outputs
# ----------------------------------------------------------------------------
def write_outputs(all_chunks: list[dict], out_dir: Path):
    (out_dir / "inception").mkdir(parents=True, exist_ok=True)

    # 1) target-only CoNLL-U, one document per chunk
    for c in all_chunks:
        lines = []
        for n, s in enumerate(c["_target_sents"], start=1):
            lines.append(f"# sent_id = {c['chunk_id']}_{n}")
            lines.append(f"# chunk_id = {c['chunk_id']}")
            lines.append(f"# quinto = {c['quinto']}")
            for cm in s.comments:
                if cm.startswith("# text ="):
                    lines.append(cm)
            lines.extend(s.raw_rows)
            lines.append("")
        (out_dir / "inception" / f"{c['chunk_id']}.conllu").write_text(
            "\n".join(lines) + "\n", encoding="utf-8")

    # 2) offset_map.csv — tool-independent realignment
    with (out_dir / "offset_map.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["chunk_id", "sent_local_id", "conllu_id", "form",
                    "upos", "start_char", "end_char"])
        for c in all_chunks:
            for n, s in enumerate(c["_target_sents"], start=1):
                for row in s.raw_rows:
                    cols = row.split("\t")
                    m = parse_misc(cols[9])
                    w.writerow([c["chunk_id"], n, cols[0], cols[1], cols[3],
                                m.get("start_char", ""), m.get("end_char", "")])

    # 3) metadata.json (strip internal field)
    meta = [{k: v for k, v in c.items() if not k.startswith("_")}
            for c in all_chunks]
    (out_dir / "metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # 4) appendix.md — readable view rendered from metadata
    md = ["# Annotation appendix — full passages (read-only context)\n",
          f"Target delimited by {TARGET_OPEN} … {TARGET_CLOSE}. "
          "Only target tokens are annotated in INCEpTION.\n"]
    for c in meta:
        md.append(f"\n## {c['chunk_id']}  (quinto {c['quinto']}, "
                  f"{c['target_word_count']} parole)\n\n{c['passage']}\n")
    (out_dir / "appendix.md").write_text("\n".join(md), encoding="utf-8")


def run(in_dir: Path, out_dir: Path, seed=SEED, **kw):
    rng = random.Random(seed)
    all_chunks, all_flags = [], []
    for path in sorted(in_dir.glob("*.conllu")):
        sents = parse_conllu(path.read_text(encoding="utf-8"))
        chunks, flags = sample_text(sents, path.stem, rng, **kw)
        all_chunks.extend(chunks)
        all_flags.extend(flags)
    write_outputs(all_chunks, out_dir)
    print(f"chunks: {len(all_chunks)}  | seed={seed}")
    for fl in all_flags:
        print("  FLAG:", fl)
    return all_chunks, all_flags


if __name__ == "__main__":
    in_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/chunks/canonical")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/chunks")
    run(in_dir, out_dir)
