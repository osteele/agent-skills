# Gradient accumulation example

This fictional project shows a complete research-notebook evidence chain. A
deterministic standard-library script stands in for training, so the commands
are safe and fast:

```bash
python3 scripts/simulate.py --condition true-batch --seed 1
python3 scripts/simulate.py --condition accumulated --seed 1
```

The notebook records a pilot, a three-seed comparison, two processed Slurm job
records, a cross-experiment finding, a scoped claim, and a completed plan. Job
IDs, revisions, and results are illustrative.

Validate it with the skill's bundled validator:

```bash
python3 ../../skills/research-lab-notebook/scripts/validate-notebook.py \
  --strict lab-notebook
```
