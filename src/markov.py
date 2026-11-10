"""A transparent first-order amino-acid Markov baseline."""
from collections import Counter, defaultdict
import random

ALPHABET = "ACDEFGHIKLMNPQRSTVWY"


class MarkovProteinGenerator:
    """Generate residue strings using observed first-order transitions."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.transitions: dict[str, Counter] = defaultdict(Counter)
        self.starts: Counter = Counter()
        self.fitted = False

    def fit(self, sequences: list[str]) -> "MarkovProteinGenerator":
        usable = [sequence.upper() for sequence in sequences if sequence]
        if not usable:
            raise ValueError("At least one non-empty training sequence is required")

        for sequence in usable:
            invalid = set(sequence) - set(ALPHABET)
            if invalid:
                raise ValueError(
                    "Training sequences must contain only the 20 standard "
                    f"amino acids; found: {''.join(sorted(invalid))}"
                )
            self.starts[sequence[0]] += 1
            for left, right in zip(sequence, sequence[1:]):
                self.transitions[left][right] += 1

        self.fitted = True
        return self

    def _sample(self, counts: Counter) -> str:
        residues = list(counts.keys())
        weights = list(counts.values())
        return self.rng.choices(residues, weights=weights, k=1)[0]

    def generate(self, length: int) -> str:
        if not self.fitted:
            raise RuntimeError("Call fit() before generate()")
        if length < 1:
            raise ValueError("length must be at least 1")

        current = self._sample(self.starts)
        output = [current]
        for _ in range(length - 1):
            options = self.transitions.get(current)
            current = self._sample(options) if options else self._sample(self.starts)
            output.append(current)
        return "".join(output)

    def generate_many(self, count: int, length: int) -> list[str]:
        if count < 1:
            raise ValueError("count must be at least 1")
        return [self.generate(length) for _ in range(count)]
