# Research job runner

**Backend**: Slurm in the fictional run records; local Python for reproduction
**Experiment tag**: `--job-name EXP-NNN` and the experiment ID in output metadata

## Layers

| Role | Tool or convention |
|---|---|
| Provisioning and placement | Existing fictional cluster |
| Queue and scheduling | Slurm |
| Workflow dependencies | Manual phase gate in the campaign plan |
| Artifact storage | `results/<experiment>/<job-id>/` |
| Processed state | `jobs/processed/slurm/` |

## Capabilities

| Capability | Project command or procedure |
|---|---|
| Submit | `sbatch --job-name EXP-NNN ...` after authorization |
| Status | `sacct -j <job-id>` |
| Logs | Read the job's configured stdout and stderr files |
| Artifacts | Retrieve `results/<experiment>/<job-id>/` and its manifest |
| Cancel | `scancel <job-id>` after authorization |
| Processed check | Test for `jobs/processed/slurm/<job-id>.json` |
| Processed mark | Follow the ledger write protocol after the evidence commit |

## Identity and artifacts

The example records experiment ID, revision, command, seed, condition, and job
ID. Its artifact URIs are illustrative and are not included in this repository.

## Verification

The local simulator reproduces the recorded metrics without Slurm. The Slurm
commands are documentation only and must not be run as part of this example.
