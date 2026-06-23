"""
02a — Build canonical CoNLL-U
Project: Misurare la creatività linguistica: sorpresa ed entropia come
strumenti di analisi stilistica (Premio di ricerca Dino Buzzetti, AIUCD)
Author: Silvia Lilli

Runs Stanza ONCE per normalized text and writes one canonical CoNLL-U file
per text. The canonical file is the single source of truth for the whole
phase (tokenization + sentence segmentation + POS), consumed by
chunk_sampling.py and reused later for POS analysis and surprisal alignment.

Critical: each text is passed to Stanza as a SINGLE document (the full
normalized string), so start_char/end_char in MISC are GLOBAL offsets into
the normalized text. Never tokenize sentence-by-sentence — offsets would
reset and become unusable for realignment.

The 'mwt' processor is required for Italian (e.g. "della" -> "di" + "la");
'pos' populates UPOS. Stanza writes start_char/end_char into MISC by default.

Run once:  python scripts/build_canonical.py data/normalized data/chunks/canonical
"""

from __future__ import annotations
import sys
from pathlib import Path

DEFAULT_PROCESSORS = "tokenize,mwt,pos"


def build_canonical(in_dir: Path, out_dir: Path,
                    lang: str = "it",
                    processors: str = DEFAULT_PROCESSORS,
                    overwrite: bool = False) -> list[Path]:
    """Tokenize/segment/tag each *.txt in in_dir; write one *.conllu per text.

    Returns the list of written (or pre-existing) canonical paths.
    """
    import stanza
    from stanza.utils.conll import CoNLL

    out_dir.mkdir(parents=True, exist_ok=True)
    texts = sorted(in_dir.glob("*.txt"))
    if not texts:
        print(f"No .txt found in {in_dir}")
        return []

    # Pipeline initialized ONCE — model loading is the expensive part.
    nlp = stanza.Pipeline(lang=lang, processors=processors, verbose=False)

    written = []
    for txt in texts:
        dst = out_dir / f"{txt.stem}.conllu"
        if dst.exists() and not overwrite:
            print(f"skip (exists): {dst.name}")
            written.append(dst)
            continue

        doc = nlp(txt.read_text(encoding="utf-8"))   # full text as ONE document
        CoNLL.write_doc2conll(doc, str(dst))

        # contract check: GLOBAL offsets must be present in MISC
        head = dst.read_text(encoding="utf-8")[:5000]
        if "start_char=" not in head:
            print(f"  WARNING: no start_char in MISC for {dst.name} — "
                  f"check Stanza version / processors")
        n_sent = sum(1 for ln in dst.read_text(encoding="utf-8").splitlines()
                     if ln.startswith("# sent_id") or ln.startswith("# text"))
        print(f"ok: {dst.name}  ({n_sent} sentence blocks)")
        written.append(dst)

    print(f"\ncanonical files: {len(written)}  | in {out_dir}")
    return written


if __name__ == "__main__":
    in_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/normalized")
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/chunks/canonical")
    build_canonical(in_dir, out_dir)
