# surprisal-entropy-italian-literature

A computational study of linguistic creativity in Italian literary prose,
using surprisal and entropy as stylistic analysis tools.

## Description

This repository contains the data and code developed for the research project
*Misurare la creatività linguistica: sorpresa ed entropia come strumenti di
analisi stilistica*, winner of the Dino Buzzetti Research Prize (AIUCD 2026).

The project investigates whether information-theoretic measures — word-level
surprisal and context entropy — can identify deliberate linguistic deviation
in Italian literary texts, with a focus on 20th-century experimental prose.
Surprisal and entropy values are combined with POS distribution analysis to
detect and interpret stylistically marked passages.

## Repository Structure

    surprisal-entropy-italian-literature/
    │
    ├── data/
    │   ├── raw/              # Original texts (plain text, libre license)
    │   ├── normalized/       # Texts after graphic normalization
    │   └── chunks/           # Segmented texts for annotation and processing
    │
    ├── notebooks/            # Jupyter notebooks (processing pipeline)
    ├── scripts/              # Python utility functions
    ├── docs/
    │   └── decisions_log.md  # Documentation of methodological choices
    └── README.md
    
## Corpus

The corpus comprises Italian literary prose texts with open licenses,
drawn primarily from the [Progetto Manuzio / Liber Liber](https://www.liberliber.it)
digital library. Texts span a range of literary registers, from standard
to experimentally marked prose, to ensure the method is tested across
different degrees of linguistic deviation.

> ⚠️ The corpus is under active development and subject to change.
> See `docs/decisions_log.md` for the current selection criteria
> and any updates to the corpus composition.

## Methods

- **Surprisal**: computed using [GePpeTto](https://github.com/LoreDema/GePpeTto),
  a BERT-based Italian language model
- **POS tagging**: [Stanza](https://stanfordnlp.github.io/stanza/)
- **Manual annotation**: gold standard subset annotated on an ordinal scale for degree of linguistic markedness

## License

- Code: [GNU General Public License v3.0](LICENSE)
- Data and documentation: [Creative Commons Attribution 4.0 International](LICENSE-DATA)

## Citation

If you use this repository in your research, please cite:

```bibtex
@misc{lilli2025surprisal,
  author       = {Lilli, Silvia},
  title        = {surprisal-entropy-italian-literature},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/slilli23/surprisal-entropy-italian-literature}
}
```

## Author

**Silvia Lilli**  
Independent researcher — Italian Literature and Digital Humanities  
Contact: silvialilli@hotmail.it
