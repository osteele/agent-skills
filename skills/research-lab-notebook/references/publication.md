# Claims and publication tracking

## CLAIMS.md

Add a claim when it could appear in an abstract, contribution list, result
heading, or central figure caption. Do not add every observation.

```markdown
| ID | Role | Claim | Status | Evidence | Paper |
|---|---|---|---|---|---|
| C1 | major | One sentence at the tested scope | provisional | [[EXP-004]]; synthesis: [[finding]] | paper-key |
```

Allowed roles: `major`, `candidate major`, and `supporting`. A paper may have
several major claims when they form one coherent contribution. The `Paper` cell
contains the stable key for the paper that uses the claim. Keep venue,
readiness, deadline, and submission state out of this table.

Allowed statuses: `supported`, `provisional`, `blocked`, `refuted`, `retired`.
`live` and `withdrawn` are accepted as legacy spellings of `supported` and
`retired`, with a warning. Every row must cite at least one experiment record. A finding may also be cited
when its synthesis, correction, or interpretation is needed to recover the
claim, but it cannot replace experiment evidence. A paper section is an evidence
consumer, not an evidence source.

Cite the estimand, not only the record, when the experiment declares one:
`EXP-004:E1`. The validator resolves the reference and warns when the claim
draws on a `found` estimand (the claim is then a found result and must say so)
or on a `gate` (a precondition, not a result). See
[Experiments](experiments.md) for the registration grammar.

If a claim depends on an analysis that no experiment owns, create an analysis
experiment. Name its input experiments, method or script, artifacts, and result.
Label backfilled expectations as retrospective rather than preregistered.

State the tested population, instrument, model family, or workload in the claim
itself. Put a longer scope boundary or blocker in a detail block when the claim
sentence cannot carry it cleanly.

When evidence changes, update the row and link the new record. Retire a claim
that no longer belongs to the publication argument; do not keep stale claims in
the active set for historical completeness.

Promotion requires human review. Before changing a claim from provisional or
blocked to supported, or broadening its scope, present the direct experiments,
relevant synthesis, unresolved threats, and exact proposed wording. Record the
review decision in the claim update or publication plan. An agent may recommend
promotion but cannot approve it.

## PUBLICATION.md

Create this file when at least one paper is in active preparation. It answers
what blocks submission and where the paper might go.

```markdown
# Publication plan

**Last updated**: YYYY-MM-DD
**Status**: One sentence across active papers

## Paper: Working title

**Paper key**: paper-key
**Manuscript**: `lab-notebook/papers/paper-key.typ`; content-canonical, natural-length
**Packets**: path or link; venue; state; synced-as-of YYYY-MM-DD (omit until a packet exists)
**Target venue**: name, verified deadline, and source

### Headline result

The named claim IDs followed by concrete evidence links.

### Blocking issues

| Issue | Severity | State | Action |
|---|---|---|---|

### Venues

| Venue | Deadline | Format limit | Fit | Source checked |
|---|---|---|---|---|
```

Verify current venue facts from primary sources before recording them. Include
the source and date checked. Remove resolved blocking items. Version control
already preserves their history.

### Dates are external

Every date in a publication record is a venue's own published deadline,
traceable to its source. Internal target dates are not recorded. A reader who
finds invented dates beside genuine ones has to check each one, so fabricated
dates cost the genuine ones their authority. Where work needs to be parked
with urgency rather than scheduled, three fields carry it:

- **Urgency**: how strongly the work is urged, with the reason. An ordering
  claim on the next free capacity, not a promise.
- **Gate**: the condition that releases it, observable by a reader of the
  records ("when the coverage check lands"), never a date.
- **Ready since**: the date readiness was marked. A reader derives staleness
  from it ("ready since 2026-08-06, still unposted") without anyone inventing
  a target.

Keep paper prose in the paper draft, next actions in `PRIORITIES.md`, and result
details in experiments or findings.

## Manuscripts and submission packets

Each paper has up to two artifact roles:

- The **manuscript** is the content-canonical, natural-length lineage master.
  Its default home is `lab-notebook/papers/<name>.typ`, beside the evidence it
  uses. It remains editable through arXiv revisions, venue review, and
  post-publication updates.
- A **submission packet** is a venue-constrained derivative created only when
  preparing a specific submission. It applies the venue template, page limit,
  and anonymization rules. Keep it in the project's external paper workspace
  with its build and submission machinery. Freeze the submitted packet while
  it is under review and freeze the camera-ready packet permanently.

The content invariant is **packet ⊆ manuscript**. A packet may omit manuscript
content to meet a venue limit, but it must not contain content absent from the
manuscript. A frozen packet may fall behind an evolving manuscript.

The manuscript leads by default: make content changes there, then port them to
each packet in preparation. A revision request or camera-ready phase may make
the packet lead temporarily. Back-port every packet-led change into the
manuscript before manuscript editing resumes. Record each packet's state and
`synced-as-of` date in `PUBLICATION.md`.

When a venue accepts the manuscript format directly, create no packet. Freeze
the submitted build separately and keep the manuscript canonical. A legacy
external paper source may serve as the manuscript until its next major
revision; label it `(serving as manuscript)` in `PUBLICATION.md` rather than
creating a notebook copy as cleanup.

### Default manuscript template

Notebook manuscripts use Typst with
[`arkheion`](https://typst.app/universe/package/arkheion/) `0.1.2` by default.
Arkheion supplies a neutral author-manuscript layout rather than a venue
template. Preserve an established project-specific Typst template when one
already exists. Every manuscript in `papers/` cites the directory's shared
`papers/references.bib`; do not create per-paper bibliography files.

Copy `assets/lab-notebook/papers/paper.typ` when starting a manuscript. Its
minimal shape is:

```typst
#import "@preview/arkheion:0.1.2": arkheion

#show: arkheion.with(
  title: "Working title",
  authors: (
    (name: "Author Name", affiliation: "Institution", email: "author@example.org"),
  ),
  abstract: [Write the abstract here.],
)

= Introduction

#bibliography("references.bib")
```

Add `arkheion-appendices` only when the manuscript has appendices. Keep
paper-specific diagram and citation helpers in the manuscript instead of
turning them into another local template.

Keep each claim's role and paper key in `CLAIMS.md`. `PUBLICATION.md` owns the
paper's manuscript and packet pointers, readiness, gates, venues, deadlines,
submission state, and packet synchronization date. It may cite claim IDs, but
it does not duplicate their role mapping.
