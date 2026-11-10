import pytest

from src.fasta import read_fasta, write_fasta
from src.markov import MarkovProteinGenerator
from src.metrics import evaluate_sequences
from src.validation import validate_sequence


def test_validation_accepts_standard_protein_sequence():
    assert validate_sequence("ACDEFG")["valid"]


def test_validation_reports_invalid_symbols():
    report = validate_sequence("ACD-?")
    assert not report["valid"]
    assert report["invalid_characters"] == ["-", "?"]


def test_validation_rejects_empty_sequence():
    assert not validate_sequence("")["valid"]


def test_fasta_round_trip(tmp_path):
    path = tmp_path / "input.fasta"
    records = [("seq one", "ACDEFG"), ("seq two", "MNPQ")]
    write_fasta(records, path)
    assert read_fasta(path) == records


def test_fasta_requires_header(tmp_path):
    path = tmp_path / "bad.fasta"
    path.write_text("ACDEFG\n", encoding="utf-8")
    with pytest.raises(ValueError):
        read_fasta(path)


def test_markov_generator_is_reproducible():
    training = ["ACDEFGHIK", "ACDEYGHIK", "ACDDFGHIK"]
    first = MarkovProteinGenerator(seed=7).fit(training).generate_many(3, 12)
    second = MarkovProteinGenerator(seed=7).fit(training).generate_many(3, 12)
    assert first == second
    assert all(len(sequence) == 12 for sequence in first)


def test_markov_rejects_ambiguous_training_letters():
    with pytest.raises(ValueError):
        MarkovProteinGenerator().fit(["ACDBFG"])


def test_metrics_for_equal_length_sequences():
    result = evaluate_sequences(["ACDE", "ACDF"])
    assert result["number_of_sequences"] == 2
    assert result["unique_fraction"] == 1.0
    assert result["mean_pairwise_identity"] == 0.75
