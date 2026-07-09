# Decisions Log — Chunking & Annotation Design

**Session date:** 2026-06-23
**Scope:** design of the exploratory annotation phase (gold standard) and of the chunking/sampling pipeline that feeds it. Covers the validation target, the annotation unit, the sampling strategy, the canonical tokenization, the INCEpTION setup, the output artefacts, and the code architecture.

---

## 1. What the gold standard is meant to validate

The central clarification of this session is *which construct the annotation measures*, because every downstream choice follows from it. Two distinct constructs were on the table:

- **Construct A — incremental processing difficulty / expectation violation.** This is left-to-right and word-by-word: the difficulty a reader experiences at the moment of encountering a word, given only the preceding context. It is the construct that surprisal predicts in reading-time studies (Hale, Levy), and it is the theoretical mechanism that motivates the whole project.
- **Construct B — critical stylistic markedness.** This is what a competent literary reader identifies as stylistically marked: a neologism, a syntactic anomaly, a code-switch. It is not purely incremental — the critic can recognise markedness retrospectively, integrating information from both sides of the point in question.

**Decision: the validation target is Construct B, not Construct A.** The project's research question is one of *detection* — "do surprisal and entropy locate the points a competent critic would judge stylistically marked?" The gold standard is therefore the set of genuinely marked points, and surprisal is the *retriever* being tested against it. Construct A is not the object of annotation; it is the explanatory bridge (deviation → processing difficulty → foregrounding) that explains *why* we expect surprisal to work at all.

**Why this matters and how we got here.** We first considered constraining the annotator to left-only context, on the grounds that reading is incremental and the model is left-only, so the annotator should see what the model sees. That reasoning was rejected, in two steps:

1. A first objection — that giving the annotator right context would be "circular" because it diverges from the model's information — was found to be **mis-stated**. It confused the *information available* with the *judgement mechanism*. Independence of the validation does not come from matching the information window; it comes from the mechanism: the human judges with comprehension, literary competence, and world knowledge, whereas the model judges with a distributional probability. These mechanisms are incommensurable, so the human judgement is a genuine external test even on the same information.
2. The decisive point is that **the target is B, and B is not constrained to left-only reading.** Crippling the ground truth to match the retriever (left-only, "surprise at first occurrence") would build the measure's own limitation into the gold standard, making it impossible to use that gold standard to validate the measure. We therefore must *not* cripple the ground truth to fit the retriever.

**Consequences for design:**

- **Context window is bidirectional.** The annotator reads the passage in natural conditions, with both preceding and following context available (read-only).
- **Markedness is judged at the passage level** (identifiable from the chunk plus its immediate context), for the exploratory phase. This keeps the test fair to a *local* measure: judging with full-oeuvre or author-system knowledge would penalise surprisal for deviations that no local measure could capture, understating its real performance on what it *can* capture. A caveat noted by the annotator: for a competent reader the passage-bound vs extra-textual distinction is not mechanical, so we keep passage-bound as the instruction and will decide later whether to *flag* cases that required extra-passage knowledge (turning them into data rather than noise).

**This decision was reached argumentatively and should not be reopened without strong justification.**

---

## 2. Annotation design

- **Single annotator** (bibliographic justification already in hand). **TO BE EVALUATED**
- **Ordinal scale** rather than binary, to align with the continuous nature of surprisal. The operational definition of the levels is still open (see §8).
- **Independent annotation before comparison.** The annotator marks markedness on the ordinal scale *independently* of the model's output. Letting the annotator merely rate model-selected candidates would reintroduce circularity: it would measure agreement on an already-filtered set, not the model's ability to *recover* deviation (recall).
- **Blind-to-surprisal sampling.** The sampled chunks must *not* be stratified on the model's surprisal values. Preferentially annotating where the model already flags peaks would make the validation self-confirming. Sampling is therefore random/systematic and blind to the computational values.
- **Intra-annotator reliability.** **TO BE EVALUATED**


---

## 3. Chunking / sampling strategy

**Annotation unit: fixed-minimum-length passages of 500 surface words, closed at the end of the first sentence that reaches the threshold.** The unit is therefore always a whole number of sentences — never an intra-sentence cut — and its length varies only upward.

**Why minimum-length-plus-whole-sentences rather than a hard fixed length.** A strict "fixed length + a few words to finish the sentence" rule breaks precisely on the texts of interest. In some authors a single sentence can exceed the target by hundreds of words, so "a few words" is not an adequate margin, and cutting mid-sentence would destroy the long-range dependencies that *produce* the deviation. Accumulating whole sentences from an anchor until the threshold is reached handles long and short sentences symmetrically and preserves the syntactic spans the analysis is about.

**Why 500 words.** Long enough to establish local context for a markedness judgement; an earlier candidate of ~100 words was judged too short to support the ordinal judgement reliably.

**Stratified sampling by quintiles.** Five chunks per text, one per quintile of the text (by surface-word position), to cover narrative position (opening, development, close), where stylistic intensity may vary systematically — preferable to pure random sampling at n = 5.

**Random anchor with the "quintile-boundary − 500" constraint.** Within each quintile, the anchor sentence is drawn at random *only* from sentences whose start word-index is ≤ (quintile_end − 500 words). Applied to the fifth quintile (whose boundary is the end of the text) this rule also automatically prevents the chunk from overrunning the end of the text. Because we close at the first sentence crossing the threshold, the tail may exceed the quintile boundary by a few words; we accept this (**option (i)**: whole sentences, ≥ 500 words, minimal tail overflow) rather than the stricter alternative that could yield sub-500 chunks when a single very long sentence straddles a boundary.

**Guards.** The implementation flags (without interrupting) two conditions: a quintile narrower than 500 words (no eligible anchor — relevant for future short texts such as novellas or poetry collections, not for the 11 long novels of the exploratory phase) and any overlap between adjacent chunks.


---

## 4. Canonical tokenization (Stanza)

**One canonical CoNLL-U file per text, produced by a single Stanza pass over the full normalized text.** This file is the single source of truth for tokenization, sentence segmentation, and POS, reused by chunking, annotation preparation, later POS analysis, and surprisal realignment. A single tokenization upstream guarantees no misalignment downstream.

**Why the full text in one pass.** Passing the whole normalized string as one document makes `start_char`/`end_char` (written by Stanza into the MISC field by default) *global, absolute* offsets into the normalized text. Tokenizing sentence-by-sentence would reset offsets to zero per sentence and make realignment impossible.

**Surface vs syntactic levels.** Word counting (for the 500 threshold) and character offsets use the **surface** level: a multi-word token such as *della* counts once and carries the offsets, via the CoNLL-U range row (e.g. `3-4 della`). POS uses the **syntactic** words (the expansion rows `3 di`, `4 la`). Punctuation is excluded from the word count but included in character spans. This must be applied uniformly.

**Processors:** `tokenize,mwt,pos`. `mwt` is essential for Italian; `pos` populates UPOS so that POS analysis later needs no second Stanza pass.

---

## 5. INCEpTION setup

- **One project for the whole exploratory phase**, so the ordinal tagset is configured once and inherited by all documents.
- **55 target-only documents, one per chunk.** Using one document per chunk makes the chunk boundary *structural* — the annotator cannot read across it, because it is a different file.
- **Context is not imported into INCEpTION.** Only the target tokens are imported as the annotable unit. The read-only bidirectional context is provided separately as a readable passage (see §6). This eliminates both the read-only-lock problem (INCEpTION has no per-token read-only lock within an editable document) and the risk of wasting the annotator's effort on annotations that would later be discarded.
- **Naming:** each canonical filename stem becomes the `text_id`, which is the prefix of the `chunk_id` (e.g. `1900_dossi_desinenza.conllu` → `1900_dossi_desinenza_q1`). Stable, descriptive IDs should be set already in the normalized `.txt` filenames, because they propagate through to INCEpTION and the offset map.

---

## 6. Output artefacts and reproducibility

- **`metadata.json`** — one record per chunk, and the **single source** for the readable passage (context_left + target + context_right, with the target delimited). The annotator reads the full passage here / in the derived appendix, then marks only the target tokens in INCEpTION.
- **`offset_map.csv`** — an **external, tool-independent** realignment map (`chunk_id`, local sentence id, CoNLL-U id, form, UPOS, global `start_char`/`end_char`). It does not depend on INCEpTION preserving MISC through its round-trip, so realignment of surprisal/entropy/POS with the annotation is robust regardless of tool behaviour.
- **`appendix.md`** — a human-readable rendering of the passages, *derived* from `metadata.json` (never hand-edited), because JSON is not comfortable to read while annotating.
- **`inception/{chunk_id}.conllu`** — the 55 target-only documents for import.
- **Fixed parameters** (logged for reproducibility): `SEED = 20260622` (the value is arbitrary), `MIN_WORDS = 500`, `CONTEXT_SENTS = 2`, `N_QUINTILES = 5`.


---

### 6.1 — MWT collapse: surface-token view for INCEpTION import

**Decision.** The `inception/{chunk_id}.conllu` files are post-processed to collapse Stanza multi-word tokens (MWT) to their surface orthographic form: each `N-M` range line is retained as a single token and its expanded syntactic words are dropped, with per-sentence renumbering. The annotation unit in INCEpTION is therefore the orthographic word, not the syntactic word.

**Rationale.** The gold standard (Construct B) is a retrospective, reader-based judgment over the surface text; the annotation unit must match what the reader sees on the page. An expanded MWT (e.g. *del* → *di* + *il*) would split a single orthographic word into two annotable units, mismatched both with the surface reading and with GePpeTto, whose BPE operates on the orthographic form.
Collapsing to surface tokens removes this mismatch at the annotation layer.

**Source of truth unchanged.** The collapse is applied only to the INCEpTION-facing derivation. The `canonical/{text_id}.conllu` files remain intact and MWT-expanded: the syntactic-word representation is still required downstream for POS and for surprisal aggregation. 

**Implementation.** Isolated as a separate stage, `scripts/collapse_mwt.py`, invoked after `chunk_sampling.py` in `notebooks/02_chunking.ipynb`, with its own unit tests on synthetic CoNLL-U (cases: consecutive MWTs; MWT at sentence start/end; `skip_until` reset across sentence boundaries). Character offsets (`start_char`/`end_char`) are verified to survive on collapsed tokens; where Stanza places them only on expanded words, they are recovered from the first child.

---

## 7. Code architecture

Three single-responsibility modules, orchestrated by a thin notebook:

- **`scripts/build_canonical.py`** — runs Stanza once per text and writes the canonical CoNLL-U files. Kept separate so the chunking logic does not depend on Stanza (heavy: model download, slow).
- **`scripts/chunk_sampling.py`** — consumes the canonical CoNLL-U files and produces the four output artefacts. Pure, fast, unit-testable (its sampling logic was tested on synthetic CoNLL-U: surface-word counting with MWT and punctuation handling, global offset propagation, one chunk per quintile, the boundary−500 anchor constraint, whole-sentence accumulation, and seed determinism).
- **`scripts/collapse_mwt.py`** — post-processes the `inception/` documents, collapsing Stanza MWTs to their surface orthographic form (one token per `N-M` range line, expanded syntactic words dropped, per-sentence renumbering). Applied only to the INCEpTION-facing derivation; the canonical files are left MWT-expanded. Pure, unit-tested on synthetic CoNLL-U (consecutive MWTs; MWT at sentence start/end; `skip_until` reset across sentence boundaries; offset preservation on collapsed tokens).
- **`notebooks/02_chunking.ipynb`** — narrative entry point: calls `build_canonical(...)`, then `run(...)`, then `collapse_mwt(...)`, and inspects the returned flags. It contains no logic of its own.

---

## 8. Operational procedure to remember

**The canonical-build idempotency guard keys on file existence, not on content.** `build_canonical` skips a text whose `.conllu` already exists (so re-running the notebook does not re-tokenize the whole corpus needlessly). It therefore will *not* notice if a normalized `.txt` has changed while its old canonical remains in place, leaving a canonical misaligned with its source. The source must be invalidated manually — delete that single `.conllu`, or call with `overwrite=True` — whenever an upstream text changes. **For this reason, every regeneration of a canonical file should be logged together with the normalization change that motivated it**, so the alignment between normalized `.txt` and `.conllu` stays traceable.

---

## 9. Open items (next session)

- **Operational definition of the ordinal scale**: number of levels, distinguishing criteria, and annotator instructions (including the passage-bound markedness instruction). Needed before annotation begins, but not needed to generate the chunk files. Configured as a custom span layer with a categorical feature in INCEpTION.
- **Extra-passage markedness flag**: whether to let the annotator flag cases that required knowledge beyond the passage — to be evaluated during annotation, treating such cases as data rather than noise.
