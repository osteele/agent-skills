# Reference manifest

Use a JSON manifest when BibTeX metadata does not identify an open PDF. Each key
must match a citation key. A string supplies the PDF URL:

```json
{
  "smith2025": "https://example.org/papers/smith2025.pdf"
}
```

An object can record separate PDF and landing-page URLs:

```json
{
  "smith2025": {
    "pdf": "https://example.org/papers/smith2025.pdf",
    "source": "https://example.org/papers/smith2025"
  }
}
```

Use only open-access or otherwise authorized URLs. Prefer stable author,
institutional-repository, conference, and preprint links over temporary signed
download URLs.
