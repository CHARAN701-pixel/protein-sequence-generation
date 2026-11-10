"""Descriptive metrics for generated protein sequences."""
from collections import Counter
from itertools import combinations

from .validation import STANDARD_AA, validate_sequence


def mean_pairwise_identity(sequences: list[str]) -> float | None:
    """Mean positional identity across shared prefixes for sequence pairs.

    This deliberately simple metric is most interpretable for equal-length
    sequences. It is not an alignment-based biological sequence identity.
    """
    if len(sequences) < 2:
        return None

    identities = []
    for first, second in combinations(sequences, 2):
        overlap = min(len(first), len(second))
        if overlap == 0:
            continue
        matches = sum(a == b for a, b in zip(first[:overlap], second[:overlap]))
        identities.append(matches / overlap)

    return sum(identities) / len(identities) if identities else None


def evaluate_sequences(sequences: list[str]) -> dict:
    """Calculate basic sequence-level properties."""
    if not sequences:
        raise ValueError("No sequences supplied for evaluation")

    reports = [validate_sequence(sequence) for sequence in sequences]
    total_length = sum(len(sequence) for sequence in sequences)
    counts = Counter(
        aa
        for sequence in sequences
        for aa in sequence.upper()
        if aa in STANDARD_AA
    )
    residue_total = sum(counts.values())
    composition = (
        {aa: counts.get(aa, 0) / residue_total for aa in sorted(STANDARD_AA)}
        if residue_total
        else {}
    )

    return {
        "number_of_sequences": len(sequences),
        "all_valid": all(report["valid"] for report in reports),
        "valid_sequence_count": sum(report["valid"] for report in reports),
        "lengths": [len(sequence) for sequence in sequences],
        "mean_length": total_length / len(sequences),
        "unique_fraction": len(set(sequences)) / len(sequences),
        "mean_pairwise_identity": mean_pairwise_identity(sequences),
        "amino_acid_composition": composition,
    }
