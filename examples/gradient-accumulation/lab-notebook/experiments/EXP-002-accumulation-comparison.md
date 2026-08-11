# EXP-002: Accumulation comparison

**Created**: 2026-08-12
**Status**: completed
**Research questions**: [[RQ1]]

## Hypothesis

Across seeds 1 through 3, the mean final-validation-loss difference between
accumulated and true batches is below 0.02.

## Method

- **Instrument**: deterministic `scripts/simulate.py` toy simulator
- **Conditions**: `true-batch` and `accumulated`
- **Seeds**: 1, 2, and 3
- **Primary metric**: mean paired final-validation-loss difference
- **Revision**: `synthetic-code-v1`
- **Key command**: `python3 scripts/simulate.py --condition <condition> --seed <seed>`

## Preregistered predictions (a priori)

- **P1: Mean equivalence**: the mean paired difference is below 0.02.
- **P2: Seed consistency**: every paired difference is below 0.02.

## Decision rule (a priori)

- **If P1 and P2 hold**: support a synthetic-scale equivalence finding.
- **Otherwise**: keep RQ1 open and report the failing seeds.

## Human review

- **Design**: paired-seed comparison approved after the pilot gate.
- **Preregistration**: predictions and threshold approved before the run.
- **Analysis and interpretation**: results, limitations, and proposed finding
  reviewed before synthesis.

## Runs

| Backend | Job ID | Description | Status | Artifacts |
|---|---|---|---|---|
| Slurm | 48161 | Both conditions at seeds 1 through 3 | completed | `results/EXP-002/48161/metrics.json` |

## Results

| Seed | True batch | Accumulated | Paired difference |
|---|---:|---:|---:|
| 1 | 0.799 | 0.803 | 0.004 |
| 2 | 0.803 | 0.807 | 0.004 |
| 3 | 0.796 | 0.800 | 0.004 |

The mean paired difference was 0.004.

### Outcomes against preregistered predictions

| Prediction | Verdict | Predicted | Observed |
|---|---|---|---|
| P1 | confirmed | Mean difference < 0.02 | 0.004 |
| P2 | confirmed | Every difference < 0.02 | All three were 0.004 |

## Conclusion

Both preregistered equivalence checks pass within the deterministic simulator.
The design does not test optimizer state, floating-point order, or a real model.

## Follow-ups

- [x] Synthesize the pilot and comparison in a finding.

## Artifacts

- `results/EXP-002/48161/metrics.json`, fictional artifact at revision `synthetic-code-v1`

## Findings

- [[2026-08-16-accumulation-matches-large-batch]]
