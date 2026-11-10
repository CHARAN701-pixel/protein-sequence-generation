"""Minimal FASTA reader/writer for protein sequences."""
from pathlib import Path
from typing import Iterable


def read_fasta(path: str | Path) -> list[tuple[str, str]]:
    """Read FASTA records as (header, sequence), preserving header text."""
    records: list[tuple[str, str]] = []
    header: str | None = None
    chunks: list[str] = []

    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(chunks).upper()))
                header = line[1:].strip()
                if not header:
                    raise ValueError(f"Empty FASTA header at line {line_number}")
                chunks = []
            else:
                if header is None:
                    raise ValueError(
                        f"Sequence data before first FASTA header at line {line_number}"
                    )
                chunks.append("".join(line.split()))

    if header is not None:
        records.append((header, "".join(chunks).upper()))
    if not records:
        raise ValueError(f"No FASTA records found in {path}")
    return records


def write_fasta(
    records: Iterable[tuple[str, str]],
    path: str | Path,
    line_width: int = 60,
) -> None:
    """Write FASTA records, wrapping sequences at line_width."""
    if line_width < 1:
        raise ValueError("line_width must be positive")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for header, sequence in records:
            handle.write(f">{header}\n")
            for start in range(0, len(sequence), line_width):
                handle.write(sequence[start : start + line_width] + "\n")
