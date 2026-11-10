"""Download a capped set of representative UniRef50 sequences from UniProt.

Example:
    python -m scripts.download_uniref50_subset \
        --max-records 5000 \
        --output data/raw/uniref50_subset.fasta

The default query is a broad length-filtered UniRef50 query. The first N
matches returned by the API are an exploratory subset, not a random sample
of the entire UniRef50 database.
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

API_URL = "https://rest.uniprot.org/uniref/search"
DEFAULT_QUERY = "identity:0.5 AND length:[50 TO 500]"
USER_AGENT = "protein-sequence-generation-learning-project/0.1"


def get_next_url(response: requests.Response) -> str | None:
    """Read the next-page URL from UniProt's HTTP Link header."""
    link_header = response.headers.get("Link", "")
    for link in requests.utils.parse_header_links(link_header):
        if link.get("rel") == "next":
            return link.get("url")
    return None


def extract_sequence(cluster: dict[str, Any]) -> str | None:
    """Get the representative-member sequence from a UniRef search result."""
    representative = cluster.get("representativeMember") or {}
    sequence_data = representative.get("sequence") or {}
    if isinstance(sequence_data, dict):
        sequence = sequence_data.get("value")
    elif isinstance(sequence_data, str):
        sequence = sequence_data
    else:
        sequence = None
    return sequence.upper() if sequence else None


def download_subset(
    query: str,
    max_records: int,
    output_path: Path,
    page_size: int = 500,
    pause_seconds: float = 0.2,
) -> dict[str, Any]:
    """Fetch up to max_records cluster representatives and save FASTA + metadata."""
    if max_records < 1:
        raise ValueError("max_records must be at least 1")
    if not 1 <= page_size <= 500:
        raise ValueError("page_size must be between 1 and 500")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update(
        {"Accept": "application/json", "User-Agent": USER_AGENT}
    )

    next_url: str | None = API_URL
    params: dict[str, Any] | None = {
        "query": query,
        "size": page_size,
    }
    records: list[tuple[str, str]] = []
    pages = 0
    skipped_without_sequence = 0
    release = None
    release_date = None

    with session:
        while next_url and len(records) < max_records:
            response = session.get(
                next_url,
                params=params,
                timeout=(15, 120),
            )
            response.raise_for_status()
            pages += 1
            release = response.headers.get("X-UniProt-Release", release)
            release_date = response.headers.get(
                "X-UniProt-Release-Date", release_date
            )
            payload = response.json()
            clusters = payload.get("results", [])

            for cluster in clusters:
                sequence = extract_sequence(cluster)
                cluster_id = cluster.get("id")
                if not sequence or not cluster_id:
                    skipped_without_sequence += 1
                    continue
                name = (cluster.get("name") or "").strip()
                header = f"{cluster_id} {name}".strip()
                records.append((header, sequence))
                if len(records) >= max_records:
                    break

            next_url = get_next_url(response)
            params = None  # The next URL already contains its cursor and parameters.
            if next_url and pause_seconds > 0:
                time.sleep(pause_seconds)

            if not clusters:
                break

    if not records:
        raise RuntimeError(
            "No representative sequences were returned. Check the query "
            "or the UniProt API response."
        )

    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for header, sequence in records:
            handle.write(f">{header}\n")
            for start in range(0, len(sequence), 60):
                handle.write(sequence[start : start + 60] + "\n")

    metadata = {
        "source": "UniProt UniRef50 REST API",
        "api_endpoint": API_URL,
        "query": query,
        "cluster_identity": "50%",
        "records_downloaded": len(records),
        "max_records_requested": max_records,
        "pages_requested": pages,
        "records_skipped_without_sequence": skipped_without_sequence,
        "uniprot_release": release,
        "uniprot_release_date": release_date,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "output_file": str(output_path).replace("\\", "/"),
        "sampling_note": (
            "Capped subset of API search results, not a random or "
            "statistically representative sample of all UniRef50 clusters."
        ),
    }
    metadata_path = output_path.with_suffix(".metadata.json")
    metadata_path.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download a capped UniRef50 FASTA subset from UniProt."
    )
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--max-records", type=int, default=5000)
    parser.add_argument("--page-size", type=int, default=500)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw/uniref50_subset.fasta"),
    )
    parser.add_argument("--pause", type=float, default=0.2)
    args = parser.parse_args()

    try:
        metadata = download_subset(
            query=args.query,
            max_records=args.max_records,
            output_path=args.output,
            page_size=args.page_size,
            pause_seconds=args.pause,
        )
    except (requests.RequestException, ValueError, RuntimeError) as error:
        raise SystemExit(f"Download failed: {error}") from error

    print(json.dumps(metadata, indent=2))
    print(f"\nFASTA saved to: {args.output}")
    print(f"Metadata saved to: {args.output.with_suffix('.metadata.json')}")


if __name__ == "__main__":
    main()
