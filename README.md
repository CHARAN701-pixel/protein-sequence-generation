# Protein Sequence Generation

A reproducible learning project exploring generative approaches to protein sequences. The first milestone provides a transparent **first-order Markov baseline** trained on a user-supplied protein FASTA file. Later milestones will compare this baseline with pretrained protein language models.

> **Scope and caution:** Generated strings are computational candidates, not validated proteins. This baseline does not establish folding, stability, function, safety, or biological activity. Do not interpret generated sequences as suitable for laboratory use.

## Project goals

1. Load, validate, and document protein FASTA datasets.
2. Build a simple, explainable generative baseline.
3. Evaluate sequence-level properties such as length, uniqueness, pairwise identity, and amino-acid composition.
4. Make experiments reproducible.
5. Progress to a pretrained generative protein language model and more meaningful biological plausibility checks.

## Current status

- [x] Initial project plan
- [x] FASTA reader and writer
- [x] Protein alphabet validation
- [x] First-order Markov generator
- [x] Basic sequence metrics
- [x] Command-line workflow and unit tests
- [ ] Select and document a coherent protein-family dataset
- [ ] Add visualizations and experiment tracking
- [ ] Add a pretrained generative protein language model
- [ ] Add reference-database similarity and structure-based evaluation

## Quick start

Python 3.10 or newer is recommended.

```bash
git clone https://github.com/CHARAN701-pixel/protein-sequence-generation.git
cd protein-sequence-generation
python -m venv .venv
```

Activate the environment:

- Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Prepare a dataset

Place a protein FASTA file at `data/raw/proteins.fasta`. Prefer a coherent protein family or a clearly defined dataset over an arbitrary mixture of unrelated proteins.

Record the source database, accessions, retrieval date, organism, filtering decisions, and licence/usage terms. Do not commit downloaded datasets unless redistribution is permitted.

The FASTA parser accepts standard amino-acid letters and common ambiguity/special symbols for reporting. The current Markov baseline intentionally requires only the 20 standard amino acids; it stops with a clear message if the input contains other symbols rather than silently changing them.

## Run the baseline

From the repository root:

```bash
python -m src.cli --input data/raw/proteins.fasta --num-sequences 20 --seed 42
```

Optional arguments:

```bash
python -m src.cli --help
```

The default output directory is `results/`. It receives:

- `generated_sequences.fasta`
- `metrics.json`

The model learns amino-acid transition frequencies from the supplied training sequences. It is deliberately simple and is not a modern protein language model.

## Initial metrics

- **Validity:** whether all residues belong to the accepted protein alphabet.
- **Length:** generated sequence lengths and mean length.
- **Uniqueness:** fraction of generated sequences that are distinct.
- **Mean pairwise identity:** mean positional identity over the shared prefix of each pair. This simple baseline metric is descriptive and is not a substitute for alignment-based sequence identity.
- **Amino-acid composition:** relative frequency of each standard amino acid.

High uniqueness or low pairwise identity does not prove biological novelty or plausibility. Later evaluation should include appropriate alignment/search methods, protein-family/domain checks, and structure-based assessment.

## Tests

Run:

```bash
pytest
```

## Repository structure

```text
protein-sequence-generation/
├── data/
│   ├── raw/                 # User-provided FASTA (not committed)
│   └── processed/
├── docs/
│   └── PROJECT_PLAN.md
├── references/
│   └── references.md
├── results/                 # Generated outputs (not committed)
├── src/
│   ├── fasta.py
│   ├── validation.py
│   ├── markov.py
│   ├── metrics.py
│   └── cli.py
├── tests/
├── requirements.txt
└── README.md
```

## Limitations and responsible use

A statistical model can generate sequences that are nonfunctional, unstable, misfolded, or biologically inappropriate. Sequence-level metrics alone cannot establish function or safety. Any future experimental work requires qualified expert review, appropriate institutional approvals, and biosafety oversight.

## References

See [references/references.md](references/references.md). Model-specific details will be added when the pretrained-model phase begins.
