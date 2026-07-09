# Decision log — Annotation, foundational decisions

## 1. Markedness construct
The gold standard operationalizes foregrounding-as-deviation only. Parallelism (foregrounding through regularity) is excluded.

## 2. Annotation scheme
Deviation-type inventory derived from Leech (1969), adapted:

```
1  Lexical
2  Grammatical
3  Phonological / Graphological
4  Semantic
5  Dialectal
6  of Register
7  of Historical Period
8  Foreign-language insertion
```

Phonological and graphological are merged into a single category (departure from Leech). Sub-type specifications are defined in the annotation protocol, not here.

## 3. Scale
Two binary decisions per word: detection (*marked / not marked*) and, conditional on detection, grade (*medium / high*). These combine into a derived per-word ordinal variable — 0 not marked, 1 medium, 2 high — used for rank-correlation with surprisal and for distributional comparison across levels. Type and grade are orthogonal.

## 4. Unit of annotation
The word (canonical Stanza token). Comparison with the LM is token-to-token; GePpeTto BPE sub-tokens are aggregated to the Stanza word (BPE→word). In INCEpTION: single-token spans carrying two categorical features  — type (multi-value: one or more categories per token) and grade (single-value: one per token).

## 5. Norm of reference
Contemporary for both poles — the annotator's perceptual norm and the LM's statistical norm — hence homogeneous in period and directly comparable. Consequence for the scheme: the *of Historical Period* category records markedness perceived as dated by a contemporary reader, not "archaic relative to the text's own period."

---

## Deferred to the paper (discursive justification)
- Theoretical grounding (Mukařovský, Šklovskij, Jakobson; Leech, Levin; Riffaterre; Contini).
- Merge of phonological/graphological: departure from Leech, motivated by the tighter phoneme–grapheme correspondence in Italian than in English.
- Graphologically-marked words under normalization: marked but non-surprising by construction.
- Single-annotator design.
- Norm choice: the reader's historical situatedness; declared limit (author-intended coeval markedness now read as neutral period-language); deferred contemporary control corpus to quantify the diachronic component.
- Comparability principle: LM reproduction governs *localization* (which token carries the effect), not *decision* (whether the word is marked); qualitatively-deviant-but-predictable words as informative divergence.

## Deferred to the annotation protocol
- Per-type localization conventions for non-token-localizable deviations (hyperbaton, multiword compounding, foreign-language insertion, metaphor).
- Annotator instructions: marked/not-marked threshold, medium/high boundary, anchor examples, retrospective bidirectional (passage-bound) reading.
