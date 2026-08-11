from __future__ import annotations

import gzip
import importlib.util
import io
import json
import pathlib
import sys
import tarfile
import tempfile
import unittest
from contextlib import redirect_stdout


ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = (
    ROOT
    / "skills"
    / "download-research-references"
    / "scripts"
    / "archive_cited_papers.py"
)
SPEC = importlib.util.spec_from_file_location("archive_cited_papers", SCRIPT)
assert SPEC and SPEC.loader
archiver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archiver)


class CitationDiscoveryTests(unittest.TestCase):
    def test_latex_cite_family_with_optional_arguments(self) -> None:
        source = r"""
        \cite{alpha}
        \parencite[see][p. 3]{beta, gamma}
        \textcite*{delta}
        \citealp{epsilon}
        """
        self.assertEqual(
            archiver.latex_cited_keys(source),
            ["alpha", "beta", "gamma", "delta", "epsilon"],
        )

    def test_recursively_follows_latex_and_typst_includes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            sections = root / "sections"
            sections.mkdir()
            (root / "main.tex").write_text(
                r"\cite{alpha}\input{sections/method}", encoding="utf-8"
            )
            (sections / "method.tex").write_text(
                r"\parencite{beta}\input{../main}", encoding="utf-8"
            )
            (root / "main.typ").write_text(
                '#include "sections/result.typ"\n@alpha', encoding="utf-8"
            )
            (sections / "result.typ").write_text("@gamma", encoding="utf-8")

            keys, scanned = archiver.cited_keys(
                [root / "main.tex", root / "main.typ"],
                {"alpha", "beta", "gamma"},
            )

            self.assertEqual(keys, ["alpha", "beta", "gamma"])
            self.assertEqual(len(scanned), 4)


class ArchiveSafetyTests(unittest.TestCase):
    def test_safe_path_component_cannot_escape_directory(self) -> None:
        component = archiver.safe_path_component("../paper/key")
        self.assertNotIn("/", component)
        self.assertNotEqual(component, "..")
        self.assertEqual(archiver.safe_path_component(".."), "%2E%2E")

    def test_rejects_non_http_urls(self) -> None:
        with self.assertRaises(ValueError):
            archiver.validated_http_url("file:///tmp/paper.pdf")

    def test_tar_extraction_preserves_safe_directories(self) -> None:
        payload = io.BytesIO()
        with tarfile.open(fileobj=payload, mode="w:gz") as archive:
            for name, data in {
                "paper/main.tex": b"text",
                "paper/references.bib": b"bib",
                "../escape.tex": b"escape",
                "paper/figure.png": b"image",
            }.items():
                member = tarfile.TarInfo(name)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))

        with tempfile.TemporaryDirectory() as temporary:
            destination = pathlib.Path(temporary)
            ok, _, written = archiver.extract_eprint_payload(
                payload.getvalue(), "2401.00001", destination
            )
            self.assertTrue(ok)
            self.assertEqual(written, ["paper/main.tex", "paper/references.bib"])
            self.assertTrue((destination / "paper" / "main.tex").is_file())
            self.assertFalse((destination.parent / "escape.tex").exists())

    def test_gzip_extraction_enforces_unpacked_limit(self) -> None:
        previous = archiver.SOURCE_MAX_UNPACKED_BYTES
        archiver.SOURCE_MAX_UNPACKED_BYTES = 8
        self.addCleanup(
            setattr, archiver, "SOURCE_MAX_UNPACKED_BYTES", previous
        )
        with tempfile.TemporaryDirectory() as temporary:
            ok, message, _ = archiver.extract_eprint_payload(
                gzip.compress(b"more than eight bytes"),
                "2401.00001",
                pathlib.Path(temporary),
            )
        self.assertFalse(ok)
        self.assertIn("unpacked cap", message)

    def test_source_marker_requires_every_listed_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = pathlib.Path(temporary)
            marker = destination / ".fetched"
            marker.write_text("paper/main.tex\n", encoding="utf-8")
            self.assertFalse(archiver.source_marker_valid(marker, destination))
            (destination / "paper").mkdir()
            (destination / "paper" / "main.tex").write_text("text", encoding="utf-8")
            self.assertTrue(archiver.source_marker_valid(marker, destination))


class BibliographyTests(unittest.TestCase):
    def test_managed_section_preserves_manual_notes_and_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            notebook = pathlib.Path(temporary)
            bibliography = notebook / "BIBLIOGRAPHY.md"
            bibliography.write_text("# Bibliography\n\nMy reading notes.\n", encoding="utf-8")
            references = notebook / "references"
            outcomes = {
                "alpha": (
                    False,
                    "unavailable",
                    references / "alpha.pdf",
                    "https://example.org/alpha",
                )
            }
            entries = {"alpha": {"title": "A Paper", "author": "Smith", "year": "2026"}}

            archiver.write_bibliography(
                bibliography, ["alpha"], entries, outcomes, references, notebook
            )
            first = bibliography.read_text(encoding="utf-8")
            archiver.write_bibliography(
                bibliography, ["alpha"], entries, outcomes, references, notebook
            )
            second = bibliography.read_text(encoding="utf-8")

            self.assertIn("My reading notes.", second)
            self.assertEqual(first, second)
            self.assertEqual(second.count(archiver.MANAGED_START), 1)

    def test_strict_dry_run_writes_json_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            source = root / "main.tex"
            bib = root / "refs.bib"
            notebook = root / "lab-notebook"
            report = root / "report.json"
            source.write_text(r"\cite{alpha}", encoding="utf-8")
            bib.write_text(
                "@article{alpha, title={A Paper}, author={Smith}, year={2026}}",
                encoding="utf-8",
            )
            previous_argv = sys.argv
            sys.argv = [
                str(SCRIPT),
                "--source",
                str(source),
                "--bib",
                str(bib),
                "--notebook",
                str(notebook),
                "--dry-run",
                "--strict",
                "--report-json",
                str(report),
            ]
            self.addCleanup(setattr, sys, "argv", previous_argv)

            with redirect_stdout(io.StringIO()):
                self.assertEqual(archiver.main(), 1)
            data = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], 1)
            self.assertEqual(data["citations"][0]["key"], "alpha")
            self.assertFalse(data["citations"][0]["pdf"]["available"])


if __name__ == "__main__":
    unittest.main()
