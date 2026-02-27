from veritaslayer.core.fingerprinting import fingerprint_text_sha256


def test_fingerprint_text_sha256_is_stable() -> None:
    text = "veritas"
    assert fingerprint_text_sha256(text) == fingerprint_text_sha256(text)
