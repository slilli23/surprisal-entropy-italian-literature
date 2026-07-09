# Annotation protocol — lexical markedness

## 1. Scope and construct

This protocol governs the manual annotation of lexical markedness in the corpus, producing the gold standard against which language-model surprisal is validated.

The annotation target is **stylistic markedness as identified by a competent literary reader**: a retrospective, bidirectional judgment made with knowledge of the whole passage.

Markedness is operationalized as **foregrounding-through-deviation**. A word is marked when it constitutes a perceptually salient departure from the reader's expectation. *Parallelism* (foregrounding through excessive regularity) is out of scope: it is realized as low surprisal and cannot be captured by the measure under validation.

The reference norm is **contemporary** — that of a present-day competent reader — consistent with the LM's contemporary statistical norm. Markedness is judged against this norm throughout (see `decisions_log_3_annotation_foundations.md`, §5).

## 2. Unit and task

The unit of annotation is the **word**, defined as the canonical Stanza token (`tokenize,mwt,pos`). Every annotation is anchored to one such token; the LM comparison is token-to-token, with GePpeTto BPE sub-tokens aggregated to the Stanza word (see `decisions_log_3_annotation_foundations.md`, §4).

Annotation proceeds **one chunk at a time**. Before annotating, the annotator reads the target chunk in full together with its bidirectional context — the two adjacent sentences, consulted in the metadata file, not in INCEpTION. Only then are individual words marked. Judgment is therefore **retrospective and passage-bound**: a word is assessed in light of the whole passage, not as the text is first encountered left-to-right.

The bidirectional context is consulted to inform judgment but is **not annotated**. Within INCEpTION only the target chunk is present and annotable; keeping the context out of the annotation interface avoids conflating context with target.

## 3. Decision procedure

For each word in the target chunk, the annotator makes up to three decisions, in order.

**(a) Detection — marked / not marked.** The annotator decides whether the word is a perceptually salient departure from the reader's expectation, as defined in §1. Most words are not marked. Only marked words proceed to (b) and (c); unmarked words receive no annotation.

**(b) Grade — medium / high.** For a marked word, the annotator assigns a single grade reflecting the strength of the departure: *medium* or *high*. The grade is a property of the word as a whole — one grade per token — and is assigned independently of category.

**(c) Type — one or more categories.** The annotator assigns the deviation category or categories to which the marked word belongs (§4). More than one category is recorded when the word deviates on more than one dimension at once.

Where a deviation is not carried by a single token, the localization conventions in §5 determine which token(s) receive the mark.

## 4. Deviation categories

The scheme is derived from Leech (1969), adapted to Italian and to the present task. A separate *grade* (medium / high) is assigned independently (see §3).

### 1. Lexical
Departure in word-formation: the word is coined or formed against the productive resources of the standard lexicon.
- **Affixation** — derivation using affixes in non-standard, novel, or over-productive ways.
- **Compounding** — formation of new compounds, whether univerbated or analytic (on multiword realization, see §5).
- **Functional conversion** — shift of a word into a new grammatical class with zero affixation.

*Examples: [to be added]*

### 2. Grammatical
Departure in morphology or syntax.
- **Morphological** — non-standard inflection or morphological form.
- **Syntactic, surface** — marked word order (hyperbaton) or agrammaticality in the surface string.
- **Syntactic, deep** — mistaken or marked selection of word class (a word occupying a slot its class does not standardly fill).

*On localization of order-based deviation, see §5. Examples: [to be added]*

### 3. Phonological / Graphological
Departure in the sound or written form of the word. The two Leechian categories are merged: in Italian the phoneme–grapheme correspondence is close enough that phonological marking is, in prose, realized graphically and not reliably separable from graphological marking.

*Examples: [to be added]*

### 4. Semantic
Departure in meaning.
- **Transference** — metaphor and other figurative transfers of sense.
- **Non-sense / absurdity** — combinations that resist literal interpretation.

*On localization of relational (tenor–vehicle) deviation, see §5. Examples: [to be added]*

### 5. Dialectal
Use of dialectal form or lexicon against the standard-language norm.

*Examples: [to be added]*

### 6. of Register
Departure in register: a word whose register conflicts with its context (e.g. markedly high or low against a neutral surround).

*Examples: [to be added]*

### 7. of Historical Period
A word perceived as markedly dated by a contemporary reader. This category records markedness relative to the **contemporary** norm, not archaism relative to the text's own period (see `decisions_log_3_annotation_foundations.md`, §5).

*Examples: [to be added]*

### 8. Foreign-language insertion
Insertion of material from a language other than Italian (on multiword realization, see §5).

*Examples: [to be added]*

## 5. Localization conventions

Annotation is anchored to single tokens (§2). Most deviations are carried by one word and are marked on that word directly. Where a deviation is not localized on a single token, the following conventions determine which token(s) receive the mark. The governing principle is that the mark falls on the token that carries the perceptible effect of the deviation — the point accessible to the reader that corresponds to where the LM registers the departure.

**Single-token deviations (default).** Affixation, functional conversion, univerbated compounds, morphological deviation, deep-syntactic word-class misselection, phonological/graphological deviation, single-word dialectal forms, register, historical period, and single-word foreign insertions are marked on the token itself. No special convention applies.

**Multiword units.** Analytic compounds, multiword foreign insertions, and multiword dialectal expressions are marked on **every constituent word**, because the comparison is made at word level: the unit spans several Stanza words, each of which receives its own aggregated surprisal value and therefore requires its own gold label. The grade of the unit is replicated across all its constituents, unless the annotator perceives internal variation in the strength of the deviation.

**Order-based deviation (hyperbaton, surface reordering).** The markedness lies in the sequence, not in a single lexeme. The mark falls on the **single token at which the ordering violation becomes perceptible** — the point at which the reader registers the disruption. Any residual mismatch between this point and the token where the LM peaks is interpretable divergence, not annotation error.

**Relational semantic deviation (metaphor, transference).** The tension holds between tenor and vehicle. The mark falls on the **semantically incongruous token — typically the vehicle** — whose literal sense conflicts with the context. For non-sense / absurdity, the mark falls on the token(s) at which the incongruity is realized.

## 6. INCEpTION workflow

**Project setup.** The annotation is organized as a single INCEpTION project containing 55 target-only documents, one per chunk. The bidirectional context is not imported; it is consulted separately in the metadata file (§2).

**Layer.** Annotation uses one custom span layer, `Markedness`, anchored to single tokens. The layer carries two categorical features:
- **type** — multi-value: one or more of the eight deviation categories (§4). Labels: `lexical`, `grammatical`, `phon_graph`, `semantic`, `dialectal`, `register`, `historical_period`, `foreign`.
- **grade** — single-value: `medium` or `high`.

A span is created only on marked words; an unmarked word carries no span. Detection is thus the presence of a span; grade and type are its features.

**Per-word procedure.** For each marked word the annotator (a) selects the token, creating a span; (b) sets `grade`; (c) sets one or more `type` values. Multiword units and non-token-localized deviations follow the conventions in §5.

**Operational instructions.**

- **Detection threshold.** *[to be drafted — operational definition of the marked / not-marked boundary, grounded in the definition of foregrounding]*

- **Grade (medium / high).** The grade reflects the *perceived intensity* of the deviation, assigned by proximity to two poles:
  - **medium** — a recognizable deviation: it stands out against the surrounding text but is readily assimilated within an immediate reading of the language.
  - **high** — a strong deviation: it resists assimilation, prompting rereading or remaining perceived as alien even after interpretation.

  The judgment is perceptual and holistic. Where a case is uncertain, three observable dimensions can help bring its intensity into focus:
  - *distance from the norm* — how rare or impossible the form is in standard Italian;
  - *resistance to interpretation* — how much effort recovering a sense requires;
  - *salience in context* — how sharply the word breaks from the surrounding passage.

  A strong deviation on any one dimension is sufficient; they need not converge.

- **Anchor examples.** *[to be added from the corpus]*
