"""Collapse Stanza multi-word tokens (MWT) to surface orthographic tokens.

Post-processes the INCEpTION-facing CoNLL-U documents so that the annotation
unit is the orthographic word (surface form) rather than the expanded
syntactic word. Each MWT range line (``N-M``) is kept as a single token, its
expanded syntactic words are dropped, and token IDs are renumbered per
sentence. Character offsets (``start_char``/``end_char``) are preserved on the
collapsed token; where Stanza stores them only on the expanded words, they are
recovered from the first/last child.

Applied only to the ``inception/`` derivation. The canonical CoNLL-U files are
left MWT-expanded: the syntactic-word representation is still required
downstream for POS and for surprisal aggregation.

The transformation is idempotent: a file with no range lines is left unchanged.
"""

from pathlib import Path


def _misc_get(misc, key):
    """Return the value of ``key`` in a CoNLL-U MISC field, or None."""
    if not misc or misc == "_":
        return None
    for kv in misc.split("|"):
        if kv.startswith(key + "="):
            return kv.split("=", 1)[1]
    return None


def _misc_set(misc, updates):
    """Return a MISC field with ``updates`` (key->value) applied, order-preserving."""
    items, seen = [], set()
    if misc and misc != "_":
        for kv in misc.split("|"):
            if "=" in kv:
                k, v = kv.split("=", 1)
            else:
                k, v = kv, None
            if k in updates:
                v, _ = updates[k], seen.add(k)
            items.append((k, v))
    for k, v in updates.items():
        if k not in seen:
            items.append((k, v))
    if not items:
        return "_"
    return "|".join(k if v is None else f"{k}={v}" for k, v in items)


def collapse_conllu_text(text):
    """Collapse MWTs in a CoNLL-U string; pure function, unit-testable.

    - MWT range line (``N-M``): kept as one surface token, offsets recovered
      from children if absent.
    - Expanded syntactic words inside a range: dropped.
    - Regular tokens: kept, HEAD/DEPREL/DEPS blanked (stale after renumbering).
    - IDs renumbered per sentence.
    """
    lines = text.split("\n")
    out = []
    new_id = 0
    skip_until = 0
    i, n = 0, len(lines)

    while i < n:
        s = lines[i].rstrip("\r")

        if s == "" or s.startswith("#"):
            out.append(s)
            if s == "":                 # sentence boundary → reset counters
                new_id, skip_until = 0, 0
            i += 1
            continue

        cols = s.split("\t")
        tid = cols[0]

        if "-" in tid:                  # MWT range line = surface token
            start, end = (int(x) for x in tid.split("-"))
            # collect children (following word lines with id in start..end)
            children = []
            j = i + 1
            while j < n:
                cs = lines[j].rstrip("\r")
                if cs == "" or cs.startswith("#"):
                    break
                ccols = cs.split("\t")
                if ccols[0].isdigit() and start <= int(ccols[0]) <= end:
                    children.append(ccols)
                    j += 1
                else:
                    break
            # ensure offsets survive on the collapsed token
            misc = cols[9] if len(cols) > 9 else "_"
            updates = {}
            if _misc_get(misc, "start_char") is None and children:
                sc = _misc_get(children[0][9] if len(children[0]) > 9 else "_", "start_char")
                if sc is not None:
                    updates["start_char"] = sc
            if _misc_get(misc, "end_char") is None and children:
                ec = _misc_get(children[-1][9] if len(children[-1]) > 9 else "_", "end_char")
                if ec is not None:
                    updates["end_char"] = ec
            if updates:
                while len(cols) < 10:
                    cols.append("_")
                cols[9] = _misc_set(misc, updates)

            new_id += 1
            cols[0] = str(new_id)
            out.append("\t".join(cols))
            skip_until = end            # children skipped by the digit branch
            i += 1
            continue

        if tid.isdigit():
            if int(tid) <= skip_until:  # expanded word inside a range → drop
                i += 1
                continue
            new_id += 1
            cols[0] = str(new_id)
            if len(cols) > 8:           # HEAD/DEPREL/DEPS invalid after renumbering
                cols[6] = cols[7] = cols[8] = "_"
            out.append("\t".join(cols))
            i += 1
            continue

        out.append(s)                   # any unexpected line: pass through
        i += 1

    return "\n".join(out)


def _collapse_file(path):
    """Collapse one file in place; returns True if the file was rewritten."""
    original = path.read_text(encoding="utf-8")
    collapsed = collapse_conllu_text(original)
    if collapsed != original:
        path.write_text(collapsed, encoding="utf-8")
        return True
    return False


def collapse_mwt(folder, pattern="*.conllu"):
    """Collapse MWTs in place across all CoNLL-U files in ``folder``.

    Returns the list of processed file paths (rewritten or already collapsed).
    """
    folder = Path(folder)
    processed = []
    for path in sorted(folder.glob(pattern)):
        _collapse_file(path)
        processed.append(path)
    return processed