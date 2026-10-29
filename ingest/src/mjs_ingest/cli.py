"""Antarmuka baris perintah mjs-ingest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import archive
from .parse_docx import DocxSupportMissing, parse
from .validate import Finding, errors, validate

SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schema" / "sitrep.schema.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mjs-ingest",
        description="Ingest dan validasi SITREP MJ-Sentinel.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="periksa satu SITREP JSON terhadap doktrin")
    p_validate.add_argument("path", type=Path)
    p_validate.add_argument(
        "--no-schema",
        action="store_true",
        help="lewati pemeriksaan skema JSON, hanya jalankan aturan doktrin",
    )

    p_index = sub.add_parser("index", help="pindai folder arsip menjadi indeks dashboard")
    p_index.add_argument("directory", type=Path)
    p_index.add_argument("-o", "--output", type=Path, help="tulis ke berkas, bawaan stdout")

    p_parse = sub.add_parser("parse", help="ekstraksi DOCX terbit menjadi JSON")
    p_parse.add_argument("path", type=Path)

    args = parser.parse_args(argv)

    if args.command == "validate":
        return _cmd_validate(args.path, skip_schema=args.no_schema)
    if args.command == "index":
        return _cmd_index(args.directory, args.output)
    if args.command == "parse":
        return _cmd_parse(args.path)
    return 2


def _cmd_validate(path: Path, *, skip_schema: bool) -> int:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"gagal membaca {path}: {exc}", file=sys.stderr)
        return 2

    findings = list(validate(doc))

    if not skip_schema:
        schema_findings, checked = _schema_check(doc)
        findings = schema_findings + findings
        if not checked:
            print(
                "catatan: pemeriksaan skema dilewati karena jsonschema belum terpasang "
                "(pip install -e 'ingest[schema]'); hanya aturan doktrin yang dijalankan",
                file=sys.stderr,
            )

    for finding in findings:
        print(finding)

    error_count = len(errors(findings))
    warning_count = len(findings) - error_count

    if error_count:
        print(f"\nFAILED — {error_count} error, {warning_count} warning")
        return 1

    print(f"\nPASSED — 0 error, {warning_count} warning")
    return 0


def _schema_check(doc: dict[str, Any]) -> tuple[list[Finding], bool]:
    try:
        import jsonschema  # noqa: PLC0415 — opsional, hanya untuk pemeriksaan skema
    except ModuleNotFoundError:
        return [], False

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    findings = [
        Finding(
            "error",
            "SCHEMA",
            "$" + "".join(f"[{p!r}]" for p in error.absolute_path),
            error.message,
        )
        for error in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path))
    ]
    return findings, True


def _cmd_index(directory: Path, output: Path | None) -> int:
    try:
        records = archive.scan(directory)
    except NotADirectoryError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    payload = archive.to_index(records)
    if output:
        output.write_text(payload, encoding="utf-8")
        print(f"indeks ditulis ke {output} ({len(records)} entri)", file=sys.stderr)
    else:
        sys.stdout.write(payload)

    flagged = [r for r in records if r.issues]
    for record in flagged:
        for issue in record.issues:
            print(f"[WARNING] {record.edition_id}: {issue}", file=sys.stderr)
    return 0


def _cmd_parse(path: Path) -> int:
    try:
        doc = parse(path)
    except (DocxSupportMissing, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(doc, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
