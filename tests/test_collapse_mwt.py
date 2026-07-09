"""Unit tests for scripts/collapse_mwt.collapse_conllu_text.

Run:  pytest tests/test_collapse_mwt.py -v

Tests the pure string->string transform on synthetic CoNLL-U, covering the
edge cases where renumbering / skip_until reset can break:
  - consecutive MWTs
  - MWT at sentence start and end
  - skip_until reset across sentence boundaries
plus offset recovery from children and idempotency.
"""

from scripts.collapse_mwt import collapse_conllu_text


def _row(*cols):
    """Build one tab-separated CoNLL-U line."""
    return "\t".join(cols)


def _tokens(conllu):
    """Return [(id, form, misc)] for the token lines of a CoNLL-U string."""
    rows = []
    for ln in conllu.split("\n"):
        if ln and not ln.startswith("#"):
            c = ln.split("\t")
            rows.append((c[0], c[1], c[9] if len(c) > 9 else "_"))
    return rows


def test_consecutive_mwts():
    """Two adjacent MWTs collapse to two surface tokens; ids renumber."""
    src = "\n".join([
        "# sent_id = 1",
        "# text = nel del casa",
        _row("1-2", "nel", "_", "_", "_", "_", "_", "_", "_", "start_char=0|end_char=3"),
        _row("1", "in", "in", "ADP", "_", "_", "_", "_", "_", "_"),
        _row("2", "il", "il", "DET", "_", "_", "_", "_", "_", "_"),
        _row("3-4", "del", "_", "_", "_", "_", "_", "_", "_", "start_char=4|end_char=7"),
        _row("3", "di", "di", "ADP", "_", "_", "_", "_", "_", "_"),
        _row("4", "il", "il", "DET", "_", "_", "_", "_", "_", "_"),
        _row("5", "casa", "casa", "NOUN", "_", "_", "_", "_", "_", "start_char=8|end_char=12"),
        "",
    ])
    toks = _tokens(collapse_conllu_text(src))
    assert [(i, f) for i, f, _ in toks] == [("1", "nel"), ("2", "del"), ("3", "casa")]
    # offsets on the surface tokens are preserved
    assert toks[0][2] == "start_char=0|end_char=3"
    assert toks[1][2] == "start_char=4|end_char=7"


def test_mwt_at_sentence_start_and_end_with_reset():
    """MWT at end of one sentence and start of the next; ids reset per sentence."""
    src = "\n".join([
        "# sent_id = a",
        _row("1", "Va", "andare", "VERB", "_", "_", "_", "_", "_", "_"),
        _row("2-3", "nella", "_", "_", "_", "_", "_", "_", "_", "start_char=3|end_char=8"),
        _row("2", "in", "in", "ADP", "_", "_", "_", "_", "_", "_"),
        _row("3", "la", "il", "DET", "_", "_", "_", "_", "_", "_"),
        "",
        "# sent_id = b",
        _row("1-2", "dei", "_", "_", "_", "_", "_", "_", "_", "start_char=9|end_char=12"),
        _row("1", "di", "di", "ADP", "_", "_", "_", "_", "_", "_"),
        _row("2", "i", "il", "DET", "_", "_", "_", "_", "_", "_"),
        _row("3", "libri", "libro", "NOUN", "_", "_", "_", "_", "_", "_"),
        "",
    ])
    toks = _tokens(collapse_conllu_text(src))
    assert [(i, f) for i, f, _ in toks] == [
        ("1", "Va"), ("2", "nella"),   # sentence a
        ("1", "dei"), ("2", "libri"),  # sentence b: id restarts at 1
    ]


def test_offset_recovery_from_children():
    """If the range line lacks offsets, they are recovered from first/last child."""
    src = "\n".join([
        "# sent_id = 1",
        _row("1-2", "nel", "_", "_", "_", "_", "_", "_", "_", "_"),
        _row("1", "in", "in", "ADP", "_", "_", "_", "_", "_", "start_char=0|end_char=1"),
        _row("2", "il", "il", "DET", "_", "_", "_", "_", "_", "start_char=1|end_char=3"),
        "",
    ])
    toks = _tokens(collapse_conllu_text(src))
    assert toks == [("1", "nel", "start_char=0|end_char=3")]


def test_idempotent_on_surface_only():
    """A file with no range lines (already collapsed) is left unchanged."""
    src = "\n".join([
        "# sent_id = 1",
        _row("1", "casa", "casa", "NOUN", "_", "_", "_", "_", "_", "start_char=0|end_char=4"),
        _row("2", "bianca", "bianco", "ADJ", "_", "_", "_", "_", "_", "start_char=5|end_char=11"),
        "",
    ])
    assert collapse_conllu_text(src) == src
