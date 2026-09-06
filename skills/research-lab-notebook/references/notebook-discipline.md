# Notebook discipline

## One owner for each fact

Every fact has one authoritative home. Other files point to it.

| Information | Owner |
|---|---|
| Current project orientation | `STATUS.md` |
| Open research questions | `QUESTIONS.md` |
| Next actions and predictions to test | `PRIORITIES.md` |
| One experiment's design, runs, and interpretation | its experiment file |
| A synthesis that needs several experiments | `findings/` |
| Research events and decisions over time | `CHANGELOG.md` |
| A bounded objective and its exit conditions | `plans/` |
| Claim roles, paper keys, and publication evidence | `CLAIMS.md` |
| Paper readiness and venue strategy | `PUBLICATION.md` |

Use this placement test:

> If this paragraph disappeared, which question would become unanswerable?

Move the paragraph to the file that owns that question. Split a paragraph that
answers two questions, then link the two records.

## Report by pointer

`STATUS.md` gives a short synthesis with links. It does not duplicate result
tables, paper trackers, or work queues. `QUESTIONS.md` carries a status and a
one-line answer for a resolved question, followed by a link to the evidence.
`PRIORITIES.md` names work and rationale, not result summaries.

## Preserve time direction

- Preserve a priori predictions and decision rules after results arrive.
- Keep raw outputs immutable.
- Put corrections beside a conclusion or supersede it with a linked record.
- Use version control for edit history. Use `CHANGELOG.md` for research history.
- Keep completed work out of active roadmaps and queues.

## Two facts only the design moment can supply

Name each estimand and say what was fixed about it in advance. A registration
that does not name the quantity it covers cannot tell a licensed citation from
an opportunistic one. Write each as `E1`, `E2`, and so on, with the statistic,
the expected direction, and the label every outcome reaches, including the
outcome that refutes the hypothesis. An estimand with nothing fixed in advance
is written as such and marked `found`. That is a normal thing for a run to
produce; mislabeling it as registered is the failure the rule prevents.

Record what the design was informed by, in an `## Informed by` section, at
design time and again at each amendment. Say explicitly where a previous run's
unregistered facet is among the inputs. Everything else about an experiment is
recoverable by audit: provenance from the artifact, replication breadth by
counting cells, the job from the runner. These two are not, and they decay
silently. The grammar for both is in [Experiments](experiments.md).

## Corrections propagate by search

When an experiment retracts a value, it writes the new value beside the old
one, and the same session searches the notebook for the superseded numbers and
the experiment ID. Findings that cite the experiment get a correction pointer
or a superseding record; terminal plans that stated the value get a retraction
notice beneath the passage. Notebook edges point forward, so nothing asks who
relied on the old value unless the sweep does.

## Prefer durable evidence

A job log may expire. A chat transcript may be unavailable to the next agent.
A metric tracker may omit the reason a condition existed. Transfer the durable
parts into the experiment record: provenance, observed values, interpretation,
decision, and follow-up.

## Avoid shadow state

Do not maintain a second table of running jobs if the backend already provides
one. Do not create `SESSION.md` for facts available from the runner, version
control, experiment files, or `STATUS.md`. Shadow state goes stale because no
single system knows which copy is authoritative.
