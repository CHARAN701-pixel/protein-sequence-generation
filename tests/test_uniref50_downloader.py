from scripts.download_uniref50_subset import extract_sequence, get_next_url


def test_extract_sequence_from_uniref_result():
    cluster = {
        "representativeMember": {
            "sequence": {"value": "acdefg"}
        }
    }
    assert extract_sequence(cluster) == "ACDEFG"


def test_extract_sequence_missing_value():
    assert extract_sequence({"representativeMember": {}}) is None


def test_get_next_url_from_link_header():
    class FakeResponse:
        headers = {
            "Link": '<https://rest.uniprot.org/uniref/search?cursor=abc>; rel="next", '
                    '<https://rest.uniprot.org/uniref/search?cursor=xyz>; rel="last"'
        }

    assert get_next_url(FakeResponse()) == (
        "https://rest.uniprot.org/uniref/search?cursor=abc"
    )
