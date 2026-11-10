"""Command-line interface for the Markov protein baseline."""
import argparse
import json
from pathlib import Path

from .fasta import read_fasta, write_fasta
from .markov import MarkovProteinGenerator
from .metrics import evaluate_sequences
from .validation import validate_records


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train a first-order Markov baseline on protein FASTA sequences."
    )
    parser.add_argument("--input", required=True, help="Input protein FASTA file")
    parser.add_argument("--num-sequences", type=int, default=20)
    parser.add_argument(
        "--length",
        type=int,
        default=None,
        help="Generated length; defaults to rounded mean input length",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args()

    if args.num_sequences < 1:
        parser.error("--num-sequences must be at least 1")
    if args.length is not None and args.length < 1:
        parser.error("--length must be at least 1")

    records = read_fasta(args.input)
    reports = validate_records(records)
    invalid = [report for report in reports if not report["valid"]]
    if invalid:
        details = "; ".join(
            f"{report['header']}: invalid={report['invalid_characters']}, "
            f"length={report['length']}"
            for report in invalid
        )
        raise SystemExit(f"Input validation failed: {details}")

    sequences = [sequence for _, sequence in records]
    if any(not sequence for sequence in sequences):
        raise SystemExit("Input contains an empty protein sequence.")

    nonstandard = [
        (header, sorted(set(sequence) - set("ACDEFGHIKLMNPQRSTVWY")))
        for header, sequence in records
        if set(sequence) - set("ACDEFGHIKLMNPQRSTVWY")
    ]
    if nonstandard:
        details = "; ".join(f"{header}: {chars}" for header, chars in nonstandard)
        raise SystemExit(
            "The Markov baseline requires only the 20 standard amino acids. "
            f"Resolve/filter these records explicitly: {details}"
        )

    target_length = args.length or round(
        sum(map(len, sequences)) / len(sequences)
    )
    model = MarkovProteinGenerator(seed=args.seed).fit(sequences)
    generated = model.generate_many(args.num_sequences, target_length)
    metrics = evaluate_sequences(generated)
    metrics.update(
        {
            "training_sequence_count": len(sequences),
            "training_total_residues": sum(map(len, sequences)),
            "seed": args.seed,
            "generated_length": target_length,
            "model": "first_order_amino_acid_markov",
        }
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_fasta(
        [
            (f"markov_baseline_seed{args.seed}_sample{i + 1}", sequence)
            for i, sequence in enumerate(generated)
        ],
        output_dir / "generated_sequences.fasta",
    )
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps(metrics, indent=2))
    print(f"\nSaved outputs to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
