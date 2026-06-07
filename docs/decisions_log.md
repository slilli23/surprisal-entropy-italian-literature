# Decisions Log

## Corpus Construction Notes

**Project:** Misurare la creatività linguistica: sorpresa ed entropia 
come strumenti di analisi stilistica (AIUCD Premio Buzzetti)

---

## 1. Sources and Format

- Texts downloaded from [Liber Liber / Progetto Manuzio](https://www.liberliber.it)
- Converted to `.txt` using Calibre v9.9.0 (when not already available in plain text)

---

## 2. Paratextual Cleaning

Removed from all texts:
- Introductions, indices, glossaries, notes, dedications, prefaces
  (including authorial prefaces)

Retained:
- Section markers (numbers and titles)
- Title and author name

**Exception:** The "Preface by Dr. S." in Svevo's *La coscienza di Zeno*
was retained because it is internal to the narrative fiction.

---

## 3. Encoding

Encoding of files in `data/raw/` was detected using `chardet`. Files requiring
conversion were read with their source encoding and rewritten as UTF-8 in
`data/raw_utf8/`. Original files in `data/raw/` were not modified.

| File | Source encoding | Confidence | Note |
|------|----------------|------------|------|
| `1878_dossi_desinenza_a.txt` | Windows-1252 | 67% | spot-check performed |
| `1891_serao_paese_cuccagna.txt` | ISO-8859-1 | 61% | spot-check performed |
| `1919_tozzi_occhi_chiusi.txt` | ISO-8859-1 | 75% | |
| `1920_palazzeschi_il_codice_perela.txt` | UTF-8-SIG | 100% | BOM removed |
| All others | UTF-8 | 83–85% | no conversion needed |

Files with confidence below 70% (`1878_dossi_desinenza_a.txt`,
`1891_serao_paese_cuccagna.txt`) were manually verified after conversion:
accented characters and special characters rendered correctly.


## 4. Graphic Normalization (text-specific)

| Text | Author | Normalization applied |
|------|--------|-----------------------|
| *La desinenza in A* | Dossi | Removal of inverted punctuation (`¿`, `¡`); grave → acute accent on conjunctions, pronouns, numbers, non-standard oxytones, and passato remoto forms; non-standard accents on monosyllables and disyllables removed entirely.; Removal of accents on non-oxytone words (non-final position); replacement of semiconsonantal `j` with `i`; replacement of double comma `,,` with `,` |
| *Uno, nessuno e centomila* | Pirandello | Replacement of semiconsonantal `j` with `i` |
| *Fosca* | Tarchetti | Replacement of `í`/`ú` (acute accent) with `ì`/`ù` (grave accent) |

**Note on *La desinenza in A***: `tè` globally normalized to `te` (no accent). The single occurrence of the noun (*"una tazza di quella tepida aqua che chiamano il tè"*, occ. 130) was manually restored as `tè` in the normalized file.

---

*Last updated: 2026-06-07*
