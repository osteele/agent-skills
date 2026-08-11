# EXP-001: Accumulation pilot

**Created**: 2026-08-12
**Status**: completed
**Research questions**: [[RQ1]]

## Hypothesis

Both conditions produce finite loss, and their final validation losses differ
by less than 0.02 at seed 1.

## Method

- **Instrument**: deterministic `scripts/simulate.py` toy simulator
- **Conditions**: `true-batch` and `accumulated`
- **Metric**: absolute final-validation-loss difference
- **Revision**: `synthetic-code-v1`
- **Key command**: `python3 scripts/simulate.py --condition <condition> --seed 1`

## Preregistered predictions (a priori)

- **P1: Finite output**: both conditions report finite loss.
- **P2: Pilot equivalence**: absolute loss difference is below 0.02.

## Decision rule (a priori)

- **If P1 and P2 hold**: proceed to the three-seed comparison.
- **Otherwise**: block the campaign and inspect the instrument.

## Human review

- **Design**: approved for the synthetic instrument on 2026-08-12.
- **Preregistration**: predictions and the 0.02 threshold approved before the run.
- **Analysis and interpretation**: results and the Phase 2 recommendation reviewed
  before the follow-up was approved.

## Runs

| Backend | Job ID | Description | Status | Artifacts |
|---|---|---|---|---|
| Slurm | 48152 | Both conditions at seed 1 | completed | `results/EXP-001/48152/metrics.json` |

## Results

True-batch loss was 0.799 and accumulated loss was 0.803. Both were finite;
the absolute difference was 0.004.

### Outcomes against preregistered predictions

| Prediction | Verdict | Predicted | Observed |
|---|---|---|---|
| P1 | confirmed | Both finite | Both finite |
| P2 | confirmed | Difference < 0.02 | Difference = 0.004 |

## Conclusion

The bounded synthetic pilot passed both gates. It supports running the planned
three-seed comparison but says nothing about real training.

## Follow-ups

- [x] Run [[EXP-002-accumulation-comparison]].

## Artifacts

- `results/EXP-001/48152/metrics.json`, fictional artifact at revision `synthetic-code-v1`

## Findings

- [[2026-08-16-accumulation-matches-large-batch]]
