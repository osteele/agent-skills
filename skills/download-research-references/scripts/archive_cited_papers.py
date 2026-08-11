#!/usr/bin/env python3
"""Archive cited papers for a research lab notebook.

Extract citation keys from a LaTeX or Typst file, read metadata from a BibTeX file,
download open-access PDFs into a notebook references directory, and write a
Markdown bibliography that links each local PDF or records why no PDF was saved.
"""

from __future__ import annotations

import argparse
import gzip
import io
import json
import pathlib
import re
import ssl
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request


PDF_HEADER = b"%PDF"
MANAGED_START = "<!-- download-research-references:start -->"
MANAGED_END = "<!-- download-research-references:end -->"
DEFAULT_PDF_MAX_BYTES = 100 * 1024 * 1024
SOURCE_MAX_BYTES = 8 * 1024 * 1024
SOURCE_MAX_UNPACKED_BYTES = 64 * 1024 * 1024
SOURCE_MAX_MEMBERS = 1000
SOURCE_EXT = {".tex", ".bib", ".bbl"}
ARXIV_UA = "agent-skills-reference-archiver/1.0 (+https://arxiv.org/help/api)"

LATEX_CITATION_RE = re.compile(
    r"\\(?:cite|parencite|textcite|autocite|footcite|smartcite|supercite|nocite)"
    r"[A-Za-z]*\*?(?:\s*\[[^]]*\]){0,2}\s*\{([^}]+)\}"
)
LATEX_INCLUDE_RE = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
TYPST_INCLUDE_RE = re.compile(r'#include\s+"([^"]+)"')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--source",
        action="append",
        type=pathlib.Path,
        help="LaTeX or Typst source to scan; repeat for multiple roots",
    )
    source_group.add_argument("--tex", type=pathlib.Path, help="Deprecated alias for --source")
    parser.add_argument("--bib", required=True, type=pathlib.Path, help="BibTeX file with cited metadata")
    parser.add_argument("--notebook", required=True, type=pathlib.Path, help="Lab-notebook directory")
    parser.add_argument(
        "--manifest",
        type=pathlib.Path,
        help="Optional JSON manifest of PDF/source URLs keyed by citation key",
    )
    parser.add_argument(
        "--references-dir",
        default="references",
        type=pathlib.Path,
        help="References directory, relative to notebook unless absolute",
    )
    parser.add_argument(
        "--bibliography",
        default="BIBLIOGRAPHY.md",
        type=pathlib.Path,
        help="Markdown bibliography path, relative to notebook unless absolute",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report actions without downloading or writing")
    parser.add_argument("--timeout", default=60, type=int, help="Per-download timeout in seconds")
    parser.add_argument(
        "--max-pdf-bytes",
        default=DEFAULT_PDF_MAX_BYTES,
        type=int,
        help="Maximum bytes accepted for one PDF",
    )
    parser.add_argument(
        "--report-json",
        type=pathlib.Path,
        help="Write a machine-readable outcome report, including during dry runs",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero when any requested PDF or source is unavailable",
    )
    parser.add_argument(
        "--fetch-source",
        action="store_true",
        help="Also fetch LaTeX source from arXiv into references/source/<key>/ "
             "(cleaner text than the PDF, and brings each paper's own .bib). "
             "Availability is per-paper; PDF-only submissions are reported, not retried.",
    )
    parser.add_argument(
        "--arxiv-delay",
        default=3.0,
        type=float,
        help="Seconds between arXiv e-print requests; arXiv asks callers not to hammer it",
    )
    return parser.parse_args()


def resolve_path(base: pathlib.Path, path: pathlib.Path) -> pathlib.Path:
    return path if path.is_absolute() else base / path


def latex_cited_keys(source: str) -> list[str]:
    keys: list[str] = []
    for match in LATEX_CITATION_RE.finditer(source):
        for key in match.group(1).split(","):
            key = key.strip()
            if key and key not in keys:
                keys.append(key)
    return keys


def typst_cited_keys(source: str, bib_keys: set[str]) -> list[str]:
    keys: list[str] = []
    for match in re.finditer(r"(?<![\w\\])@([A-Za-z][A-Za-z0-9_:\-]*)", source):
        key = match.group(1)
        if key in bib_keys and key not in keys:
            keys.append(key)
    return keys


def source_dependencies(source_path: pathlib.Path, source: str) -> list[pathlib.Path]:
    suffix = source_path.suffix.lower()
    matches: list[str] = []
    if suffix == ".tex":
        matches.extend(match.group(1).strip() for match in LATEX_INCLUDE_RE.finditer(source))
    elif suffix == ".typ":
        matches.extend(match.group(1).strip() for match in TYPST_INCLUDE_RE.finditer(source))

    dependencies: list[pathlib.Path] = []
    for value in matches:
        candidate = source_path.parent / value
        if not candidate.suffix:
            candidate = candidate.with_suffix(suffix)
        if candidate.is_file():
            dependencies.append(candidate)
    return dependencies


def source_tree(source_paths: list[pathlib.Path]) -> list[pathlib.Path]:
    ordered: list[pathlib.Path] = []
    seen: set[pathlib.Path] = set()

    def visit(path: pathlib.Path) -> None:
        resolved = path.resolve()
        if resolved in seen:
            return
        seen.add(resolved)
        ordered.append(resolved)
        source = resolved.read_text(encoding="utf-8")
        for dependency in source_dependencies(resolved, source):
            visit(dependency)

    for source_path in source_paths:
        visit(source_path)
    return ordered


def cited_keys(source_paths: list[pathlib.Path], bib_keys: set[str]) -> tuple[list[str], list[pathlib.Path]]:
    scanned = source_tree(source_paths)

    keys: list[str] = []
    for source_path in scanned:
        source = source_path.read_text(encoding="utf-8")
        suffix = source_path.suffix.lower()
        found = latex_cited_keys(source) if suffix == ".tex" else typst_cited_keys(source, bib_keys)
        if suffix not in {".tex", ".typ"}:
            found = latex_cited_keys(source) + typst_cited_keys(source, bib_keys)
        for key in found:
            if key not in keys:
                keys.append(key)
    return keys, scanned


def safe_path_component(value: str) -> str:
    if not value:
        raise ValueError("citation keys cannot be empty")
    encoded = urllib.parse.quote(value, safe="-_")
    if encoded in {".", ".."}:
        encoded = encoded.replace(".", "%2E")
    return encoded


def validated_http_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"unsupported URL {url!r}; expected http or https")
    return url


def strip_tex(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace(r"\&", "&")
    value = value.replace(r"\_", "_")
    value = value.replace("{", "").replace("}", "")
    return value


def read_balanced_value(text: str, start: int) -> tuple[str, int] | None:
    while start < len(text) and text[start].isspace():
        start += 1
    if start >= len(text):
        return None
    quote = text[start]
    if quote == '"':
        end = start + 1
        while end < len(text):
            if text[end] == '"' and text[end - 1] != "\\":
                return text[start + 1 : end], end + 1
            end += 1
        return None
    if quote != "{":
        end = start
        while end < len(text) and text[end] not in ",\n":
            end += 1
        return text[start:end].strip(), end
    depth = 0
    end = start
    while end < len(text):
        char = text[end]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : end], end + 1
        end += 1
    return None


def parse_bib_entries(bib_path: pathlib.Path) -> dict[str, dict[str, str]]:
    text = bib_path.read_text(encoding="utf-8")
    entries: dict[str, dict[str, str]] = {}
    starts = list(re.finditer(r"@(?P<type>\w+)\s*\{\s*(?P<key>[^,\s]+)\s*,", text))
    for index, start in enumerate(starts):
        key = start.group("key")
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        body = text[start.end() : end]
        fields: dict[str, str] = {"entrytype": start.group("type")}
        position = 0
        while True:
            match = re.search(r"(?P<field>[A-Za-z][A-Za-z0-9_-]*)\s*=", body[position:])
            if not match:
                break
            field = match.group("field").lower()
            value_start = position + match.end()
            parsed = read_balanced_value(body, value_start)
            if parsed is None:
                position = value_start + 1
                continue
            value, value_end = parsed
            fields[field] = strip_tex(value)
            position = value_end
        entries[key] = fields
    return entries


def load_manifest(path: pathlib.Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    raw = json.loads(path.read_text())
    manifest: dict[str, dict[str, str]] = {}
    for key, value in raw.items():
        if isinstance(value, str):
            manifest[key] = {"pdf": value}
        elif isinstance(value, dict):
            manifest[key] = {str(k): str(v) for k, v in value.items()}
        else:
            raise TypeError(f"manifest entry for {key!r} must be a string or object")
    return manifest


def arxiv_id(fields: dict[str, str]) -> str | None:
    for field in ("eprint", "journal", "note", "url", "doi"):
        value = fields.get(field, "")
        match = re.search(r"(?:arXiv[:./ ]|abs/)?(\d{4}\.\d{4,5})(?:v\d+)?", value, re.I)
        if match:
            return match.group(1)
    return None


def acl_id(fields: dict[str, str]) -> str | None:
    for field in ("url", "doi"):
        value = fields.get(field, "")
        match = re.search(r"(\d{4}\.[A-Za-z-]+(?:\.[A-Za-z-]+)?\.\d+)", value)
        if match:
            return match.group(1)
        match = re.search(r"10\.18653/v1/([^/\s]+)", value)
        if match:
            return match.group(1)
    return None


def infer_urls(key: str, fields: dict[str, str], manifest: dict[str, dict[str, str]]) -> tuple[str | None, str | None]:
    entry = manifest.get(key, {})
    pdf = entry.get("pdf")
    source = entry.get("source")
    if pdf and not source:
        source = source_from_pdf(pdf)
    if not pdf:
        aid = arxiv_id(fields)
        if aid:
            pdf = f"https://arxiv.org/pdf/{aid}"
            source = source or f"https://arxiv.org/abs/{aid}"
    if not pdf:
        acl = acl_id(fields)
        if acl:
            pdf = f"https://aclanthology.org/{acl}.pdf"
            source = source or f"https://aclanthology.org/{acl}/"
    if not source:
        source = fields.get("url")
    if not source and fields.get("doi"):
        source = f"https://doi.org/{fields['doi']}"
    return pdf, source


def source_from_pdf(pdf_url: str) -> str | None:
    if "arxiv.org/pdf/" in pdf_url:
        return pdf_url.replace("/pdf/", "/abs/").removesuffix(".pdf")
    if "aclanthology.org/" in pdf_url and pdf_url.endswith(".pdf"):
        return pdf_url.removesuffix(".pdf") + "/"
    return None


def is_pdf(path: pathlib.Path) -> bool:
    if not path.exists() or path.stat().st_size < 1024:
        return False
    with path.open("rb") as file:
        return file.read(4) == PDF_HEADER


def download_pdf(
    url: str,
    dest: pathlib.Path,
    timeout: int,
    max_bytes: int = DEFAULT_PDF_MAX_BYTES,
) -> tuple[bool, str]:
    if is_pdf(dest):
        return True, "exists"
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; agent-skills-reference-archiver/1.0)",
            "Accept": "application/pdf,*/*;q=0.8",
        },
    )
    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            exceeded = False
            with tmp.open("wb") as output:
                total = 0
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > max_bytes:
                        exceeded = True
                        break
                    output.write(chunk)
            if exceeded:
                tmp.unlink(missing_ok=True)
                return False, f"PDF exceeds {max_bytes} byte cap"
        if not is_pdf(tmp):
            size = tmp.stat().st_size if tmp.exists() else 0
            tmp.unlink(missing_ok=True)
            return False, f"not a PDF ({size} bytes)"
        tmp.replace(dest)
        time.sleep(0.2)
        return True, "downloaded"
    except (OSError, TimeoutError, urllib.error.URLError, ssl.SSLError) as error:
        tmp.unlink(missing_ok=True)
        return False, str(error)


def first_author(author_field: str) -> str:
    if not author_field:
        return "Unknown"
    first = author_field.split(" and ")[0].strip()
    parts = [part.strip() for part in first.split(",")]
    return parts[0] if parts else first


def venue(fields: dict[str, str]) -> str:
    return fields.get("booktitle") or fields.get("journal") or fields.get("publisher") or "Source"


def bibliography_entry(
    key: str,
    fields: dict[str, str],
    pdf_relpath: pathlib.Path,
    pdf_ok: bool,
    message: str,
    source_url: str | None,
) -> str:
    title = fields.get("title", key)
    if title.endswith("?") or title.endswith("!"):
        title_text = f'"{title}"'
    else:
        title_text = f'"{title}."'
    year = fields.get("year", "n.d.")
    local = f"[PDF]({pdf_relpath.as_posix()})" if pdf_ok else f"PDF unavailable ({message})"
    source = f" [Source]({source_url})." if source_url else ""
    citation = f"{first_author(fields.get('author', ''))} et al. ({year}), {title_text} {venue(fields)}. {local}.{source}"
    return f"### {key}\n\n{citation}"


def write_bibliography(
    path: pathlib.Path,
    keys: list[str],
    entries: dict[str, dict[str, str]],
    outcomes: dict[str, tuple[bool, str, pathlib.Path, str | None]],
    references_dir: pathlib.Path,
    notebook: pathlib.Path,
) -> None:
    refs_display = references_dir.relative_to(notebook) if references_dir.is_relative_to(notebook) else references_dir
    lines = [
        MANAGED_START,
        "## Archived Draft References",
        "",
        f"Local copies live in `{refs_display.as_posix()}/`.",
        "",
    ]
    for key in keys:
        pdf_ok, message, pdf_path, source_url = outcomes[key]
        pdf_relpath = pdf_path.relative_to(notebook) if pdf_path.is_relative_to(notebook) else pdf_path
        lines.append(bibliography_entry(key, entries.get(key, {}), pdf_relpath, pdf_ok, message, source_url))
        lines.append("")
    lines.append(MANAGED_END)
    managed = "\n".join(lines) + "\n"

    if path.exists():
        current = path.read_text()
        start = current.find(MANAGED_START)
        end = current.find(MANAGED_END)
        if start >= 0 and end >= start:
            end += len(MANAGED_END)
            updated = current[:start].rstrip() + "\n\n" + managed + current[end:].lstrip("\n")
        else:
            updated = current.rstrip() + "\n\n" + managed
    else:
        updated = "# Bibliography\n\n" + managed
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated)


def extract_eprint_payload(payload: bytes, aid: str, dest_dir: pathlib.Path) -> tuple[bool, str, list[str]]:
    """Extract bounded text sources from an arXiv e-print payload."""
    written: list[str] = []
    total = 0
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:*") as tar:
            members = tar.getmembers()
            if len(members) > SOURCE_MAX_MEMBERS:
                return False, f"e-print exceeds {SOURCE_MAX_MEMBERS} member cap", written
            seen: set[pathlib.PurePosixPath] = set()
            selected: list[tuple[tarfile.TarInfo, pathlib.PurePosixPath]] = []
            for member in members:
                name = pathlib.PurePosixPath(member.name)
                if (
                    not member.isfile()
                    or name.is_absolute()
                    or ".." in name.parts
                    or name in seen
                    or name.suffix.lower() not in SOURCE_EXT
                ):
                    continue
                seen.add(name)
                if member.size > SOURCE_MAX_UNPACKED_BYTES - total:
                    return False, f"e-print exceeds {SOURCE_MAX_UNPACKED_BYTES} byte unpacked cap", written
                total += member.size
                selected.append((member, name))
            total = 0
            for member, name in selected:
                handle = tar.extractfile(member)
                if handle is None:
                    continue
                data = handle.read(member.size + 1)
                if len(data) != member.size:
                    return False, f"short or oversized archive member {name}", written
                output = dest_dir.joinpath(*name.parts)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(data)
                total += len(data)
                written.append(name.as_posix())
    except tarfile.TarError:
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(payload)) as source:
                data = source.read(SOURCE_MAX_UNPACKED_BYTES + 1)
        except (OSError, EOFError):
            return False, "unrecognised e-print payload", written
        if len(data) > SOURCE_MAX_UNPACKED_BYTES:
            return False, f"e-print exceeds {SOURCE_MAX_UNPACKED_BYTES} byte unpacked cap", written
        name = f"{safe_path_component(aid)}.tex"
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / name).write_bytes(data)
        written.append(name)
    return True, f"{len(written)} files", written


def source_marker_valid(marker: pathlib.Path, dest_dir: pathlib.Path) -> bool:
    if not marker.is_file():
        return False
    try:
        entries = [line.strip() for line in marker.read_text(encoding="utf-8").splitlines()]
    except (OSError, UnicodeDecodeError):
        return False
    if not entries:
        return False
    for entry in entries:
        relative = pathlib.PurePosixPath(entry)
        if relative.is_absolute() or ".." in relative.parts:
            return False
        if not dest_dir.joinpath(*relative.parts).is_file():
            return False
    return True


def download_eprint(aid: str, dest_dir: pathlib.Path, timeout: int) -> tuple[bool, str]:
    """Fetch a reference's LaTeX source from arXiv, when the authors submitted any.

    Source beats the rendered PDF for everything downstream reads a reference *for*:
    the abstract and section text arrive without two-column extraction damage,
    hyphenation, or ligature loss, and the paper's own .bib comes along, which makes
    the citation graph free.

    Availability is per-paper and cannot be assumed: authors may submit a PDF with
    no source, and `/e-print/` then returns that PDF. The content type is sniffed
    and a PDF-only result is reported rather than treated as a failure.
    Only text-ish members are extracted; figures are the bulk of the bytes and are
    useless here.
    """
    marker = dest_dir / ".fetched"
    if source_marker_valid(marker, dest_dir):
        return True, "exists"
    request = urllib.request.Request(
        f"https://arxiv.org/e-print/{aid}",
        headers={"User-Agent": ARXIV_UA, "Accept": "application/gzip,application/x-eprint-tar,*/*"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read(SOURCE_MAX_BYTES + 1)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        return False, f"fetch failed: {type(exc).__name__}"
    if len(payload) > SOURCE_MAX_BYTES:
        return False, f"e-print exceeds {SOURCE_MAX_BYTES // (1024 * 1024)}MB cap"
    if payload[:4] == PDF_HEADER:
        return False, "PDF-only submission; no LaTeX source on arXiv"

    ok, message, written = extract_eprint_payload(payload, aid, dest_dir)
    if not ok:
        return False, message
    if not written:
        return False, "no .tex/.bib members in e-print"
    marker.write_text("\n".join(sorted(written)), encoding="utf-8")
    return True, f"{len(written)} files"


def write_sources_index(path: pathlib.Path, results: dict[str, tuple[bool, str]]) -> None:
    lines = ["# Reference sources", "",
             "LaTeX source for cited arXiv references, where the authors submitted it.",
             "Prefer these over the PDFs when summarising a reference or tracing what it",
             "cites; the text is clean and the paper's own `.bib` is included.", "",
             "| Key | Source | Notes |", "|---|---|---|"]
    for key, (ok, message) in sorted(results.items()):
        rel = pathlib.Path("source") / safe_path_component(key)
        link = f"[`{rel}/`]({rel}/)" if ok else "Unavailable"
        lines.append(f"| `{key}` | {link} | {message} |")
    got = sum(1 for ok, _ in results.values() if ok)
    lines += ["", f"{got}/{len(results)} references have LaTeX source."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    notebook = args.notebook.resolve()
    references_dir = resolve_path(notebook, args.references_dir).resolve()
    bibliography_path = resolve_path(notebook, args.bibliography).resolve()
    entries = parse_bib_entries(args.bib)
    source_paths = args.source or [args.tex]
    keys, scanned_sources = cited_keys(source_paths, set(entries))
    manifest = load_manifest(args.manifest)

    outcomes: dict[str, tuple[bool, str, pathlib.Path, str | None]] = {}
    for key in keys:
        pdf_url, source_url = infer_urls(key, entries.get(key, {}), manifest)
        component = safe_path_component(key)
        pdf_path = references_dir / f"{component}.pdf"
        if not pdf_url:
            if source_url:
                try:
                    source_url = validated_http_url(source_url)
                except ValueError as error:
                    outcomes[key] = (False, str(error), pdf_path, None)
                    continue
            outcomes[key] = (False, "no open PDF URL inferred; add to manifest if available", pdf_path, source_url)
            continue
        try:
            pdf_url = validated_http_url(pdf_url)
            if source_url:
                source_url = validated_http_url(source_url)
        except ValueError as error:
            outcomes[key] = (False, str(error), pdf_path, None)
            continue
        if args.dry_run:
            outcomes[key] = (pdf_path.exists(), f"would fetch {pdf_url}", pdf_path, source_url)
            continue
        references_dir.mkdir(parents=True, exist_ok=True)
        ok, message = download_pdf(pdf_url, pdf_path, args.timeout, args.max_pdf_bytes)
        outcomes[key] = (ok, message, pdf_path, source_url)

    if not args.dry_run:
        write_bibliography(bibliography_path, keys, entries, outcomes, references_dir, notebook)

    source_results: dict[str, tuple[bool, str]] = {}
    if args.fetch_source:
        for key in keys:
            aid = arxiv_id(entries.get(key, {}))
            if not aid:
                source_results[key] = (False, "not an arXiv reference")
                continue
            target = references_dir / "source" / safe_path_component(key)
            if args.dry_run:
                source_results[key] = (target.exists(), f"would fetch e-print {aid}")
                continue
            ok, message = download_eprint(aid, target, args.timeout)
            source_results[key] = (ok, message)
            if message != "exists":
                time.sleep(args.arxiv_delay)     # arXiv asks for a gap between requests
        if not args.dry_run and source_results:
            write_sources_index(references_dir / "SOURCES.md", source_results)

    ok_count = sum(1 for ok, _, _, _ in outcomes.values() if ok)
    print(f"{ok_count}/{len(keys)} PDFs available")
    if source_results:
        src_ok = sum(1 for ok, _ in source_results.values() if ok)
        print(f"{src_ok}/{len(source_results)} LaTeX sources available")
    for key, (ok, message, _, _) in outcomes.items():
        if not ok:
            print(f"FAILED {key}: {message}")
    if args.report_json:
        report_path = args.report_json.resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "schema_version": 1,
            "dry_run": args.dry_run,
            "sources_scanned": [str(path) for path in scanned_sources],
            "citations": [
                {
                    "key": key,
                    "pdf": {
                        "available": outcomes[key][0],
                        "message": outcomes[key][1],
                        "path": str(outcomes[key][2]),
                        "source_url": outcomes[key][3],
                    },
                    "source": (
                        {
                            "available": source_results[key][0],
                            "message": source_results[key][1],
                        }
                        if key in source_results
                        else None
                    ),
                }
                for key in keys
            ],
        }
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    failed = any(not ok for ok, _, _, _ in outcomes.values())
    source_failed = any(not ok for ok, _ in source_results.values())
    return 1 if args.strict and (failed or source_failed) else 0


if __name__ == "__main__":
    sys.exit(main())
