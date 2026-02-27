from __future__ import annotations

import argparse
import json
import sys

from veritaslayer.core.credibility import score_source_credibility
from veritaslayer.core.fingerprinting import ContentFingerprint
from veritaslayer.core.forensic import analyze_text_forensic
from veritaslayer.core.propagation import analyze_propagation
from veritaslayer.utils.report import AuthenticityReport, build_report

try:
    from rich.console import Console
    from rich.table import Table

    _RICH = True
except ModuleNotFoundError:
    _RICH = False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="veritaslayer",
        description="Probabilistic authenticity signals for digital content.",
    )
    parser.add_argument("text", nargs="?", help="Text content to evaluate.")
    parser.add_argument("--source-url", default="", help="Optional source URL")
    parser.add_argument("--repost-count", type=int, default=0)
    parser.add_argument("--source-count", type=int, default=1)
    parser.add_argument("--time-to-viral-minutes", type=int, default=0)
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Formatted table output (requires rich) or indented JSON.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Always emit raw JSON (overrides --pretty)."
    )
    return parser


def _render_rich(report: AuthenticityReport) -> None:
    console = Console()
    overall = report.overall_synthetic_probability
    colour = "red" if overall > 0.6 else "yellow" if overall > 0.35 else "green"

    console.print(
        f"\n[bold]VeritasLayer[/bold] — Synthetic probability: "
        f"[{colour} bold]{overall:.0%}[/{colour} bold]\n"
    )

    table = Table(title="Signal Breakdown", show_lines=True)
    table.add_column("Signal", style="bold")
    table.add_column("Synthetic %", justify="right")
    table.add_column("Confidence", justify="right")
    table.add_column("Explanation")

    for sig in report.signals:
        sp = sig.probability_synthetic
        sc = "red" if sp > 0.6 else "yellow" if sp > 0.35 else "green"
        table.add_row(
            sig.name,
            f"[{sc}]{sp:.0%}[/{sc}]",
            f"{sig.confidence:.0%}",
            sig.explanation,
        )

    console.print(table)
    console.print(f"[dim]Fingerprint SHA-256: {report.fingerprint.get('hashes', {}).get('sha256', 'n/a')}[/dim]")
    console.print(f"[dim]{report.security_note}[/dim]\n")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    text = args.text if args.text is not None else sys.stdin.read().strip()
    if not text:
        parser.error("No text provided.")

    fingerprint = ContentFingerprint.compute(text, source_url=args.source_url or "")
    forensic_signal = analyze_text_forensic(text)
    credibility_signal = score_source_credibility(args.source_url)
    propagation_signal = analyze_propagation(
        repost_count=args.repost_count,
        source_count=args.source_count,
        time_to_viral_minutes=args.time_to_viral_minutes,
    )

    report = build_report(
        text=text,
        source_url=args.source_url or None,
        fingerprint=fingerprint,
        forensic_signal=forensic_signal,
        credibility_signal=credibility_signal,
        propagation_signal=propagation_signal,
    )

    if args.json or not args.pretty:
        if hasattr(report, "model_dump_json"):
            print(report.model_dump_json())
        else:
            print(json.dumps(report.model_dump()))
    elif args.pretty and _RICH:
        _render_rich(report)
    else:
        # fallback pretty
        if hasattr(report, "model_dump"):
            print(json.dumps(report.model_dump(), indent=2))
        else:
            import dataclasses

            print(json.dumps(dataclasses.asdict(report), indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
