"""mjs_ingest — lapisan ingest dan validasi SITREP MJ-Sentinel.

Dashboard tidak membaca DOCX secara langsung. Paket ini yang menormalkan
arsip terbit menjadi JSON sesuai ``schema/sitrep.schema.json``, lalu
memvalidasinya terhadap aturan doktrin sebelum dipakai antarmuka.
"""

from .msrm import METHODOLOGY, Band, band_of, composite, fill_of
from .validate import Finding, errors, passed, validate

__all__ = [
    "METHODOLOGY",
    "Band",
    "Finding",
    "band_of",
    "composite",
    "errors",
    "fill_of",
    "passed",
    "validate",
]
