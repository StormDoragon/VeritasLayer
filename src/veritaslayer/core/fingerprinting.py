from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Union


class ContentFingerprint:
    """Cryptographically secure + perceptual fingerprint.

    Never trusts input blindly. All paths validate type before processing.
    No eval/exec — ever.
    """

    VERSION = "0.1.0"

    @staticmethod
    def compute(
        content: Union[str, bytes, Path],
        source_url: str = "",
    ) -> dict[str, Any]:
        """Return a fingerprint dict for text or binary content."""
        result: dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "version": ContentFingerprint.VERSION,
            "source_url": source_url,
            "hashes": {},
            "perceptual": {},
            "warnings": [],
        }

        try:
            if isinstance(content, str):
                data = content.encode("utf-8")
                result["type"] = "text"
            elif isinstance(content, bytes):
                data = content
                result["type"] = "bytes"
            elif isinstance(content, Path):
                if not content.exists():
                    raise FileNotFoundError(f"Path does not exist: {content}")
                data = content.read_bytes()
                result["type"] = "file"
            else:
                result["warnings"].append(
                    "Unsupported content type — partial fingerprint only"
                )
                result["type"] = "unknown"
                return result

            result["hashes"]["sha256"] = hashlib.sha256(data).hexdigest()
            result["hashes"]["sha3_256"] = hashlib.sha3_256(data).hexdigest()

            # Byte-level entropy proxy (std of byte values)
            byte_array = list(data)
            mean = sum(byte_array) / max(len(byte_array), 1)
            variance = sum((b - mean) ** 2 for b in byte_array) / max(len(byte_array), 1)
            result["perceptual"]["byte_entropy_proxy"] = round(variance ** 0.5, 4)

        except Exception as exc:  # noqa: BLE001
            result["warnings"].append(f"Fingerprint error: {exc}")
            result["error"] = True

        return result


# Lightweight convenience wrapper kept for backwards-compat with CLI
def fingerprint_text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
