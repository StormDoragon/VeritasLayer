from veritaslayer.core.forensic import analyze_text_forensic


def test_forensic_signal_shape() -> None:
    signal = analyze_text_forensic("Simple factual sentence.")
    assert 0.0 <= float(signal["score"]) <= 1.0
    assert 0.0 <= float(signal["confidence"]) <= 1.0
