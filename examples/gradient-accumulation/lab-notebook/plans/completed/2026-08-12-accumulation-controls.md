---
status: completed
summary: Test synthetic gradient accumulation against true large batches
next_action: none
owner: example maintainer
reviewer: example reader
current_phase: Closed
created: 2026-08-12
updated: 2026-08-16
---

# Accumulation controls

## Objective

Determine whether the synthetic accumulated condition stays within 0.02 final
validation loss of the true-batch condition.

## Existing evidence

RQ1 was open when this plan was created. No result had been observed.

## Phases

### Phase 1: Cheap validation

Run seed 1 in both conditions. Continue only if both results are finite and the
paired difference is below 0.02. Record [[EXP-001]].

### Phase 2: Three-seed comparison

Run seeds 1 through 3 in both conditions. Support the scoped claim only if the
mean and every paired difference are below 0.02. Record [[EXP-002]].

## Risks and controls

- The simulator is not a training system; keep every conclusion synthetic.
- Write predictions and gates before recording outputs.
- Use separate job IDs and ledger records for the two phases.

## Terminal conditions

- Complete when both phases pass and their evidence is durable.
- Block if an output is non-finite or an artifact cannot be verified.
- Abandon if the simulator cannot represent both conditions deterministically.

## Human review

- The plan and Phase 1 design were approved before execution.
- Phase 1 evidence was reviewed at the pilot gate before Phase 2 was approved.
- Phase 2 evidence and the terminal disposition were reviewed before closure.

## Disposition

Completed. Both phases passed their preregistered gates. The conclusion remains
limited to the deterministic simulator.

## Evidence

- [[EXP-001-accumulation-pilot]]
- [[EXP-002-accumulation-comparison]]
- [[2026-08-16-accumulation-matches-large-batch]]
- Ledger records `jobs/processed/slurm/48152.json` and `48161.json`
