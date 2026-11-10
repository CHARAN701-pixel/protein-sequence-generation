"""Protein sequence validation utilities."""
from collections import Counter

STANDARD_AA = set("ACDEFGHIKLMNPQRSTVWY")
ACCEPTED_AA = STANDARD_AA | set("BXZJUO*")


def validate_sequence(sequence: str) -> dict:
    """Return validation details without silently modifying the sequence."""
    seq = sequence.strip().upper()
    invalid = sorted(set(seq) - ACCEPTED_AA)
    return {
        "valid": bool(seq) and not invalid,
        "non_empty": bool(seq),
        "length": len(seq),
        "invalid_characters": invalid,
        "contains_ambiguous": any(aa in seq for aa in "BXZJ"),
        "contains_unknown_or_special": any(aa in seq for aa in "UO*"),
    }


def validate_records(records: list[tuple[str, str]]) -> list[dict]:
    """Validate FASTA records and include their headers in each report."""
    reports = []
    for header, sequence in records:
        report = validate_sequence(sequence)
        report["header"] = header
        reports.append(report)
    return reports


def amino_acid_counts(sequences: list[str]) -> Counter:
    """Count standard amino acids across a collection of sequences."""
    counts: Counter = Counter()
    for sequence in sequences:
        counts.update(aa for aa in sequence.upper() if aa in STANDARD_AA)
    return counts
