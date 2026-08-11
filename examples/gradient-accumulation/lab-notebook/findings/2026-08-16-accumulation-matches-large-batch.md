# Finding: Accumulation matches large batches in the synthetic example

**Date**: 2026-08-16
**Status**: supported
**Research questions**: [[RQ1]]
**Experiments**: [[EXP-001]], [[EXP-002]]

## Claim

Gradient accumulation is equivalent to true large-batch training under the
deterministic example's 0.02 final-validation-loss margin.

## Evidence

- [[EXP-001]] observed a 0.004 paired difference in the bounded pilot.
- [[EXP-002]] observed a 0.004 paired difference at each of three seeds.

## Synthesis

The pilot established that the instrument was finite and inside the planned
margin before the wider comparison. The comparison then showed that the same
scoped result held across all synthetic seeds.

## Scope and threats to validity

The simulator encodes a fixed condition effect. It does not model optimizer
state, numerical ordering, stochastic gradients, hardware, or real datasets.

## Consequences

- RQ1 is answered only for the synthetic example.
- Claim C1 is supported at the same scope.
- The bounded campaign can close.

## Sources

- `experiments/EXP-001-accumulation-pilot.md`
- `experiments/EXP-002-accumulation-comparison.md`
- Fictional job artifacts `results/EXP-001/48152/` and `results/EXP-002/48161/`
