from veritaslayer.core.credibility import score_source_credibility


def test_credibility_for_trusted_domain() -> None:
    signal = score_source_credibility("https://reuters.com/example")
    assert float(signal["score"]) >= 0.8
