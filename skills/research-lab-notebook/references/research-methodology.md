# Research methodology

Apply these rules before reporting a number or turning a run into a claim.

## Validate the instrument first

A manipulation is an empirical claim. Test it on the cheapest sufficient
instrument before paying for a large run. Examples include a small API sweep, a
short pilot, a reduced dataset, a synthetic control, or a low-cost model.

Record what the validation establishes and what it does not. A direction that
holds on one model, dataset, or population may reverse on another.

## Ask whether the instrument reaches the phenomenon

Validating one instrument against one manipulation leaves a question no single
experiment can ask: whether the set of experiments shares a blind spot. Ask it
at every phase boundary of a campaign and before committing spend to a batch.

- When several planned or running experiments share one instrument, one
  substrate, one corpus, or one intervention family, that shared factor is
  invisible to every one of them. A factor held constant cannot discriminate
  hypotheses about the contrast.
- A recorded limitation is either a limit on the claim or a limit on the
  instrument. A limit on the claim is a disclosure and belongs in the record.
  A limit on the instrument belongs in the queue, ahead of everything
  downstream of it, since work queued behind a blind instrument inherits the
  blindness. Writing the caveat down feels like having dealt with it.
- If a rival method exists and has never been run on the same material, the
  disagreement between them has been inferred rather than observed. Running
  both on one corpus is usually cheaper than another experiment on either.

Ask it while work is in flight. A full queue is the condition under which
stepping back feels like idling, and the condition under which a shared blind
spot costs the most. If the last several corrections all changed what was
written and none changed what would run next, that is the signal.

## Sort limits by durability

An external instrument (an estimator, a backend, a lookup table, someone
else's simulator) will have things it cannot do. Each limit is one of two
kinds, with opposite reporting rules.

- **Structural**: the limit follows from the interface, so it holds for any
  implementation and survives every future data release. State it as an
  impossibility and name the interface property that causes it. A lookup keyed
  on tensor shapes cannot see a modifier that changes cost while leaving shapes
  identical, no matter how much data is collected.
- **Contingent**: the limit is this artifact's current coverage, such as a
  table with no rows for the case at hand. It expires with the next data drop.
  Report it as a dated disclosure naming the artifact version and the date
  coverage was checked, so a later reader knows what to re-test.

Keep the two out of one "limitations" sentence. Merging buries a general
result under an artifact accident, or inflates an accident into a law, and it
destroys the reader's ability to tell which limits a newer artifact has already
fixed. A structural limit is a contribution and belongs in the paper's claims;
a contingent one belongs in the artifact's coverage record.

## Match the magnitude, then vary the dose

Two design rules for interventional experiments. Both are cheap at design time
and expensive to retrofit, because both change which arms run.

**Compare an intervention against an equivalent-magnitude non-intervention,
never against nothing.** An intervention differs from the untouched condition
in two ways at once: the thing that was meant to change, and the fact that
something was perturbed at all. A no-op baseline confounds them, and the
confound lands in the contrast. The control arm perturbs as much, in the same
place, without carrying the manipulation; its effect is the cost of perturbing,
and subtracting it leaves the manipulation. The control must be on
distribution (a norm-matched random direction is not a magnitude control), and
it should differ from the treated condition in the fewest other respects.

**Turn a binary check into a dose ladder.** A single comparison answers "does
this break the result?" A graded series (n, n+1, n+2) answers "how much of
this is safe, and where does it break?", which is usually the question at hand.
Every level carries the perturbation's fixed cost, so only the increment
varies; the safe range is measured rather than asserted; and a non-linearity
locates the boundary instead of invalidating the method. Let the ladder govern
the real experiment too: apply k to one side and k plus the increment to the
other, so the categorical factor is constant everywhere.

For a reviewer, two questions: what does the control arm hold constant, and
what does it fail to hold constant? And is a binary check standing in for a
graded one, so that a method validated at one operating point is used across
a range?

## Separate planned and exploratory analysis

Analyze preregistered primary outcomes first. Label additional analyses as
exploratory. Do not edit a priori predictions or thresholds after seeing the
result.

## Review analysis and interpretation

Pause after primary analysis and before synthesis. Give the human reviewer the
preregistration, exclusions, checks, observed values, uncertainty, exploratory
analyses, and proposed interpretation. Record corrections and the scope the
review licenses. A follow-up selected by a decision rule still waits for human
approval before new work is submitted.

## Report enough to assess the claim

Include, when applicable:

- sample size and independent unit;
- central estimate and uncertainty interval;
- effect size, not only a p-value;
- multiple-comparison procedure and the family of tests;
- seed, model, dataset, or subgroup variation;
- missing data and excluded runs;
- manipulation and negative controls;
- cost and runtime when they constrain interpretation; and
- exact code and data revisions.

Do not call a single seed, model, prompt family, or dataset a general result.
State the tested scope in the finding sentence.

## Check aggregation

Inspect subgroup results before relying on a pooled effect. Look for Simpson's
paradox, mixture shifts, class imbalance, duplicated observations, leakage, and
pseudoreplication. The independent unit must match the statistical test.

## Treat nulls carefully

A null result may indicate absence, low power, a failed manipulation, a noisy
instrument, or an insensitive outcome. Report sensitivity or detectable effect
size when possible. A failed counting or retrieval check must report its
false-void rate before it can justify abandoning a line of work.

## Attribute reversals

When a finding negates a claim, name who or what made the earlier claim: a paper,
an experiment, a preregistered prediction, or a working hypothesis. Avoid vague
phrasing that implies a consensus no source held.

## Keep claims proportional to evidence

- `supported`: direct evidence at the named scope with required checks.
- `provisional`: evidence exists but generality, power, or a key control is
  missing.
- `blocked`: the current instrument cannot adjudicate the claim.
- `refuted`: an adequately sensitive test contradicts the prediction at the
  named scope.

Use the narrowest label that remains true if the reader opens only the linked
evidence.
