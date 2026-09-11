# Plans

A plan is a version-controlled contract for one bounded research objective. It
records scope, dependencies, decisions, handoffs, review gates, and exit
conditions across experiments, agents, harnesses, and sessions. Use `plans/`
when several experiments or phases serve that objective.

Use [Plan execution and read-only review](plan-execution.md) to preview a plan,
execute it in narrated, stepped, unattended, or handoff mode, or conduct a
results walkthrough (replay) of existing experiments. Preview and walkthrough
work on incomplete or completed plans without launching jobs, taking execution
ownership, or changing the records.

## Plans persist across sessions

A notebook plan preserves the research contract in version control. One agent
can draft it, a researcher can review it, another agent or harness can execute
an authorized phase, and a later agent can close it. Every participant reads
the same objective, evidence, dependencies, gates, risks, and terminal
conditions.

Claude Code and Codex planning surfaces organize and approve an agent's current
task. Use them to reason about creating or executing the notebook plan. Keep the
research contract in the plan file so it remains available across context
resets, products, collaborators, and sessions.

Plans are appropriate when at least one of these is true:

- the objective spans several experiments or decision-gated phases;
- creation, execution, and review may belong to different people or agents;
- work must resume after the current session or context window;
- a scheduler, CI job, or harness needs a stable machine-readable `next_action`;
- stopping, cost, or evidence gates must remain visible before execution.

## Frontmatter

```yaml
---
status: draft
summary: Determine whether the effect survives two control families
next_action: Design the first pilot
owner: researcher
reviewer: collaborator
current_phase: Phase 1
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

Required fields are `status`, `summary`, `next_action`, `created`, and `updated`.
Optional fields are `owner`, `reviewer`, and `current_phase`. Use `current_phase`
for active and blocked plans so a new executor can locate the live gate without
reconstructing the plan.

Statuses are `draft`, `active`, `blocked`, `gated`, `backlog`, `superseded`,
`completed`, and `abandoned`. Use a filename of the form
`YYYY-MM-DD-lowercase-topic.md`, where the date is the creation date. Active
plans live directly under `plans/`. Other plans live in the subdirectory named
for their status. `complete` (with a `plans/complete/` directory) and
`proposed` are accepted as legacy spellings of `completed` and `draft`, with a
warning.

Status-specific fields preserve why work is waiting or ended:

| Status | Required metadata |
|---|---|
| `gated` | `gate` and either `revisit_when` or `promote_when` |
| `backlog` | Either `revisit_when` or `promote_when` |
| `superseded` | `superseded_by` |
| `abandoned` | `abandoned_because` |

A gate is a testable external blocker: data, compute, a dependency, a
collaborator decision. "The user decides to run it" is not a gate. A plan that
is viable and waiting for someone to start it is `backlog` with a revisit
cadence.

`next_action` is a handoff pointer, not a task queue. Keep it bounded and update
it only after the owning phase's evidence and disposition are durable. It must
be non-empty for a nonterminal plan. Set it to an empty value, `none`, or
`null` when the status is `superseded`, `completed`, or `abandoned`.

### Completed versus abandoned

The distinction turns on whether the work was done, not on whether the answer
was welcome. A plan that ran its course and returned a negative result is
`completed`: the campaign answered its question, and the answer was no. A plan
whose own negative gate fired as designed is the clearest case, since the gate
firing is the experiment working. Reserve `abandoned` for plans that never got
their answer: the premise changed, the question stopped mattering, or the work
was judged not worth doing.

Filing a completed negative as `abandoned` has a cost. It reads to the next
person as "this was a mistake" rather than "this question is settled", so the
direction gets re-proposed by someone who cannot tell it was already closed by
evidence. Negative results are results; file them where they will be found.

## Body

```markdown
# Plan title

## Objective

A falsifiable outcome and the decision it informs.

## Existing evidence

Links to questions, experiments, findings, and claims.

## Phases

### Phase 1: Cheap validation

- Inputs and dependencies
- Bounded work
- Acceptance and stop conditions
- Expected notebook updates

### Phase 2: Full measurement

Created only after Phase 1 passes its gate.

## Risks and controls

Scientific, operational, cost, and data-loss risks.

## Terminal conditions

- Completed when ...
- Blocked when ...
- Abandoned when ...
```

Every plan requires `Objective`, `Existing evidence`, `Phases`, `Risks and
controls`, and `Terminal conditions`. Terminal plans add closing sections: a
completed plan carries a completion report and `## Evidence`; a superseded or
abandoned plan carries `## Disposition` and `## Evidence`.

```markdown
## Disposition

Why the plan ended and which terminal condition applied.

## Evidence

Links to the experiments, findings, claims, and revisions that support closure.
```

## Budget and accounting

Use an optional `## Budget and accounting` section to keep the plan's estimates,
approved limits, and dated decisions together. Prose, bullets, or a small table
can carry it. This is a human-readable recording pattern, not new frontmatter,
a required heading, a separate accounting ledger, or a validator-enforced
budget. See the [cost guide](https://research-notebook.osteele.com/guide/costs/)
for a worked campaign.

Choose the cheapest instrument sufficient for the scientific decision. Compare
analysis of existing data, an instrument check, a bounded pilot, a full
measurement, and independent confirmation. Record what each option can resolve
and why cheaper options are insufficient. Preserve necessary controls, valid
uncertainty, and independent confirmation. A pilot that checks the instrument
does not become evidence for a claim beyond its design.

Build the estimate from setup and data preparation, attempt counts, resource
quantities, rates, and conditional branches. Include likely operational
exposure such as failed attempts, retries, provisioning, idle time, storage,
and transfer when they are in scope. Separate:

- compute quantity, with units such as GPU-hours and the device count;
- money, with currency, rate source and date, billing unit, and billing scope;
- elapsed time, including queueing and parallelism assumptions; and
- human effort, including setup, review, and result processing.

State costs outside the estimate's scope. Local or prepaid compute can consume
resources even when incremental cash expense is zero. Explain uncertainty with
ranges, bounded scenarios, or unknowns; use outcome probabilities only when
there is evidence for them. Conditional scientific branches need explicit
costs and entry conditions, not invented expected-value probabilities.

Record the baseline estimate, approved ceiling and scope, monetary contingency,
retry policy, and dated approval with its author. Identify which branches are
authorized and where another decision is required. Contingency is capacity
within the approved ceiling; it is not spent cost and is not automatically
added again to the forecast. Keep it distinct from the statistical
[confirmation reserve](#confirmation-reserve): holding back evidence protects
inference, whereas holding back money covers financial uncertainty. Budget
room cannot replace either scientific or human-review gates.

Experiments own [per-attempt cost evidence](experiments.md#cost-and-resources).
The plan links those records and carries a dated rollup, with its as-of time,
scope, units, and unresolved gaps. Use three nonoverlapping quantities for the
same scope and as-of time:

| Quantity | Meaning |
|---|---|
| A: incurred to date | Usage or charges already incurred, including failed and running attempts. Label provider-reported versus usage-estimated amounts, and billed versus provisional amounts. |
| C: committed remainder | Additional forecast for running or submitted work only, excluding every portion already in A. |
| U: uncommitted forecast | Planned work not yet submitted. Approval alone is not an execution commitment. |

Forecast = A + C + U. Moving a planned attempt into the queue moves its forecast
from U to C; consumption moves the incurred portion into A. Do not add a
running job's full forecast to its incurred cost. Calculate separately for
each unit and currency; do not add GPU-hours to dollars. Currency conversions
need a dated exchange-rate basis and must preserve the original amounts.

Headroom after commitments = approved limit - A - C. It still has to cover U.
The margin against the full forecast is approved limit - (A + C + U).
Neither headroom nor an underspend grants approval for more work. Identify
unallocated shared charges and missing billing evidence alongside the rollup;
unknown is not zero, and an incomplete subtotal is not a settled total.

Before admitting work, use a conservative bound for concurrent attempts and
permitted retries, not just the nominal single-job price. Coordinate
reservations against the same approval so separate agents cannot each spend
the same headroom. A documented runner limit is a safeguard only if the runner
actually enforces it. If credible exposure exceeds the approved ceiling, or a
material unknown prevents bounding it, stop for a decision on scope, resources,
or budget. Record any approved change with its date; keep the original baseline.
See [execution preflight](plan-execution.md#execute-the-authorized-scope).

At closure, compare incurred costs with the baseline at matching scope, explain
variance, and link final or pending billing evidence. Retain the forecast
history and mark corrected estimates superseded rather than adding a bill as
new spend for the same usage. Name remaining commitments, pending charges,
unallocated costs, and the owner and next check for unresolved billing. A
scientifically completed plan can have financial settlement pending; say both.
Carry lessons about rates, idle time, and retries into successor estimates
without automatically authorizing successor jobs.

## Confirmation reserve

A plan that will end in a confirmatory claim carries a `## Confirmation
reserve` section, written at plan creation and before any exploration. It
names the evidence the plan is holding back and the rule that will judge it:

```markdown
## Confirmation reserve

**Held back:** seeds 7 and 11; eval tasks 40 to 60 of the held-out split

**Decision rule:** accept if reserve accuracy beats the baseline by more
than 2pp on the preregistered metric
```

Both markers are required, and the validator rejects a section carrying only
one. A reserve that names what is held back but not how it will be judged
leaves the rule to be written once the numbers are known, which is the failure
the reserve exists to prevent.

This is the one plan record that cannot be written later. Everything else in a
plan can be reconstructed from evidence that already exists; a reserve created
after exploration is not a reserve. Commit the section as soon as it exists so
version control fixes its date. Omit the section for plans that make no
confirmatory claim; an empty declaration is not a declaration.

## Completion report

A plan that reaches `completed` carries a `## Completion report` section,
written by the executing session before the terminal status is set. It is the
persisted form of the final handoff, so the summary survives the session. It
states:

- the terminal disposition and the evidence that caused it;
- per-goal outcomes (met, unmet, void), each linking the experiment or finding
  that carries the result;
- limitations and instrument caveats worth a future reader's attention;
- follow-ups left on the table, naming the successor plan when one exists;
- job and artifact status at closure;
- a link to the budget's actual-versus-baseline reconciliation, when costs are
  tracked, including any pending settlement and its follow-up owner.

Canonical numbers and interpretation still live in `experiments/` and
`findings/`; the report links them rather than restating them. A terminal
plan's report may run to a page, because it is the record a later reader uses
to decide whether the question is settled.

Write the heading exactly as `## Completion report`. Notebooks that predate
the convention record the same thing under other names, and the validator
recognizes those rather than requiring a rename: `Completion`, `Completion
note`, `Completion audit`, `Outcome`, `Execution outcome`, `Execution result`,
`Closed`, and `Disposition`. Matching is on the exact heading, case
insensitively, never on a keyword. `## Completion gates` and `## Outcome tree`
are prospective sections that belong in an open plan, and one word separates
them from their retrospective counterparts.

Do not rename an old heading into the prescribed spelling to make it match.
The rename asserts that the section states a terminal disposition, per-goal
outcomes, caveats, and follow-ups, which is a claim about text nobody has
re-read. Recognizing the heading costs nothing and claims nothing.

Do not compose findings the plan does not record. Where the recorded outcome
is too thin to promote into a report, inventory the plan for a decision
instead: abandon the follow-up, move the plan back from `completed`, or write
the report from the records it names, one plan at a time.

## Retraction notices on terminal plans

A completed plan is terminal, but the experiments it cites are not. When an
experiment record later corrects a result the plan stated as its outcome, the
plan keeps asserting the superseded value to every future reader. Nothing in
the frontmatter marks it, since `superseded_by` is for a plan replaced by
another plan.

Record a retraction notice directly beneath the affected passage, leaving the
original text untouched:

```markdown
> **Retracted YYYY-MM-DD.** EXP-NNN supersedes the figures above: mean 0.996,
> range 0.009 (was mean 0.987, range 0.031). The narrow-spread reading is
> withdrawn. Applied YYYY-MM-DD.
```

Four rules:

- **Annotate, never rewrite.** The original claim stays verbatim. Editing the
  numbers out destroys the record of what was believed and when.
- **Point, do not restate.** Corrected values and citations only. A notice that
  paraphrases the correction becomes a second claim to verify.
- **Apply, do not assume.** Write the notice when a correction is acted on,
  not when it is reported. A review finding can be wrong.
- **State the superseded values, then sweep.** The experiment that retracts
  writes the new value beside the old one, and the same session searches the
  notebook for the superseded values and the experiment ID, annotating whatever
  it finds.

Notebook edges point forward: a plan names its experiments, and a search for
the experiment ID is the computed reverse. At the moment a correction is
recorded, nothing asks who relied on the old value unless the sweep does.

## Execution boundary

A plan records intent and approved scope. An agent or harness may carry out only
the phase or actions the user authorized. Expensive, destructive, privileged,
publication, and external actions require their own authority. Keep
`next_action` bounded. Continuous or autonomous execution means following the
explicitly authorized bounded plan without routine conversational pauses; it
does not permit unsolicited or open-ended research loops.

Pause for human review before changing a draft plan to active. After each phase,
write its evidence and proposed disposition, then pause again. The reviewer
chooses whether to continue, revise, move the plan to `gated` or `backlog`, or
close it. A gated follow-up requires another explicit review before execution.
Record the gate and the condition that permits reconsideration.

The [execution mode](plan-execution.md#execution-modes) never removes these
human-review gates. Stepped mode adds a stop after every experiment: explain
the original design and setup before findings, discuss interpretation and the
next action, then wait for the user to say proceed. Do not prequeue another
experiment or bypass the stop through parallel branches.

When handing a phase to another agent or harness, pass the plan path and phase
name rather than copying its instructions into a prompt. The executor records
job IDs and outputs in experiment files, updates the plan's status and
`next_action`, and leaves scientific conclusions in experiments or findings.
The plan coordinates evidence production. Experiments and findings own the
evidence.

When the plan reaches a terminal state, write the completion report or
disposition and the evidence, update indexes and pointers, then remove it from
active queues.

Regenerate and validate the plan index with:

```bash
python3 <skill-directory>/scripts/validate-notebook.py <notebook> \
  --write-plan-index --strict
```

Use `--format json` when a dashboard, editor, or external research tool consumes
diagnostics. This interface is the integration boundary. The notebook format
remains application-independent.
