from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = (
    ROOT
    / "skills"
    / "research-lab-notebook"
    / "scripts"
    / "validate-notebook.py"
)
SPEC = importlib.util.spec_from_file_location("validate_notebook", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


COMPLETED_EXPERIMENT = """# EXP-001: Synthetic check

**Status**: completed

## Hypothesis

The synthetic condition changes the primary metric.

## Method

Run two deterministic conditions.

## Preregistered predictions (a priori)

- **P1**: The metric increases.

## Decision rule (a priori)

- **If P1 holds**: Record the scoped result.

## Runs

| Backend | Job ID |
|---|---|
| local | job-1 |

## Results

The metric increased.

### Outcomes against preregistered predictions

| Prediction | Verdict |
|---|---|
| P1 | confirmed |

## Conclusion

The result supports the synthetic claim.

## Artifacts

- `results/metrics.json`
"""

FINDING = """# Finding: Synthetic result holds twice

**Date**: 2026-08-11
**Status**: supported
**Experiments**: [[EXP-001]], [[EXP-002]]

## Claim

The result holds in both synthetic experiments.

## Evidence

- [[EXP-001]] supports the claim.
- [[EXP-002]] supports the claim.

## Synthesis

The two conditions agree.

## Scope and threats to validity

This is synthetic evidence only.

## Consequences

Use the example to test validation.

## Sources

- `experiments/EXP-001-synthetic-check.md`
"""

PLAN = """---
status: active
summary: Decide whether the synthetic result survives a control
next_action: Run Phase 1
current_phase: Phase 1
created: 2026-08-11
updated: 2026-08-11
---

# Synthetic control campaign

## Objective

Decide whether the result survives a control.

## Existing evidence

- [[EXP-001]]

## Phases

### Phase 1

Run the bounded control.

## Risks and controls

Use synthetic data only.

## Terminal conditions

- Complete when the control is recorded.
"""


class NotebookFixture:
    def __init__(self, root: pathlib.Path) -> None:
        self.root = root
        for relative in validator.REQUIRED_FILES:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# Index\n", encoding="utf-8")

    def add_experiment(self, name: str = "EXP-001-synthetic-check.md") -> pathlib.Path:
        path = self.root / "experiments" / name
        path.write_text(COMPLETED_EXPERIMENT, encoding="utf-8")
        (self.root / "experiments" / "README.md").write_text(
            f"# Experiments\n\n- [{path.stem}]({path.name})\n", encoding="utf-8"
        )
        return path


class NotebookValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name) / "lab-notebook"
        self.fixture = NotebookFixture(self.root)

    def messages(self) -> list[str]:
        return [issue.message for issue in validator.validate(self.root)[1]]

    def test_minimum_notebook_is_valid(self) -> None:
        self.assertEqual(self.messages(), [])

    def test_completed_experiment_requires_outcome_table(self) -> None:
        path = self.fixture.add_experiment()
        path.write_text(
            COMPLETED_EXPERIMENT.replace(
                "### Outcomes against preregistered predictions",
                "### Prediction notes",
            ),
            encoding="utf-8",
        )
        self.assertTrue(
            any("Outcomes against" in message for message in self.messages())
        )

    def test_experiment_must_be_in_index(self) -> None:
        self.fixture.add_experiment()
        (self.root / "experiments" / "README.md").write_text(
            "# Experiments\n", encoding="utf-8"
        )
        self.assertIn("not listed in README.md", self.messages())

    def test_finding_contract_and_index(self) -> None:
        path = self.root / "findings" / "2026-08-11-synthetic-result.md"
        path.write_text(FINDING, encoding="utf-8")
        (self.root / "findings" / "README.md").write_text(
            f"# Findings\n\n- [{path.stem}]({path.name})\n", encoding="utf-8"
        )
        self.assertEqual(self.messages(), [])

    def test_finding_date_must_match_filename(self) -> None:
        path = self.root / "findings" / "2026-08-10-synthetic-result.md"
        path.write_text(FINDING, encoding="utf-8")
        (self.root / "findings" / "README.md").write_text(
            path.name, encoding="utf-8"
        )
        self.assertIn("Date field does not match filename", self.messages())

    def test_claim_requires_direct_experiment_evidence(self) -> None:
        self.fixture.add_experiment()
        finding = self.root / "findings" / "2026-08-11-synthetic-result.md"
        finding.write_text(FINDING, encoding="utf-8")
        (self.root / "findings" / "README.md").write_text(
            finding.name, encoding="utf-8"
        )
        (self.root / "CLAIMS.md").write_text(
            """# Claims

| ID | Role | Claim | Status | Evidence | Paper |
|---|---|---|---|---|---|
| C1 | major | Synthetic result | supported | findings/2026-08-11-synthetic-result.md | synthetic-paper |
""",
            encoding="utf-8",
        )
        self.assertTrue(
            any("findings cannot replace it" in message for message in self.messages())
        )

    def test_claim_may_add_finding_context_to_experiment_evidence(self) -> None:
        self.fixture.add_experiment()
        finding = self.root / "findings" / "2026-08-11-synthetic-result.md"
        finding.write_text(FINDING, encoding="utf-8")
        (self.root / "findings" / "README.md").write_text(
            finding.name, encoding="utf-8"
        )
        (self.root / "CLAIMS.md").write_text(
            """# Claims

| ID | Role | Claim | Status | Evidence | Paper |
|---|---|---|---|---|---|
| C1 | major | Synthetic result | supported | [[EXP-001]]; synthesis: findings/2026-08-11-synthetic-result.md | synthetic-paper |
""",
            encoding="utf-8",
        )
        self.assertEqual(self.messages(), [])

    def test_claim_accepts_project_specific_experiment_id(self) -> None:
        experiment = self.fixture.add_experiment("ACC-E1-synthetic-check.md")
        experiment.write_text(
            COMPLETED_EXPERIMENT.replace("# EXP-001:", "# ACC-E1:"),
            encoding="utf-8",
        )
        (self.root / "CLAIMS.md").write_text(
            """# Claims

| ID | Role | Claim | Status | Evidence | Paper |
|---|---|---|---|---|---|
| C1 | major | Synthetic result | supported | [[ACC-E1]] | synthetic-paper |
""",
            encoding="utf-8",
        )
        self.assertEqual(self.messages(), [])

    def test_claim_requires_valid_role_and_paper_key(self) -> None:
        self.fixture.add_experiment()
        (self.root / "CLAIMS.md").write_text(
            """# Claims

| ID | Role | Claim | Status | Evidence | Paper |
|---|---|---|---|---|---|
| C1 | headline | Synthetic result | supported | [[EXP-001]] | |
""",
            encoding="utf-8",
        )
        messages = self.messages()
        self.assertTrue(
            any("invalid claim role 'headline'" in message for message in messages)
        )
        self.assertTrue(any("paper key is empty" in message for message in messages))

    def test_ledger_record_validates_evidence_and_identity(self) -> None:
        experiment = self.fixture.add_experiment()
        ledger = self.root / "jobs" / "processed" / "slurm" / "job-1.json"
        ledger.parent.mkdir(parents=True)
        ledger.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "backend": "slurm",
                    "job_id": "job-1",
                    "experiment_id": "EXP-001",
                    "terminal_status": "succeeded",
                    "processed_at": "2026-08-11T14:25:00Z",
                    "evidence": [str(experiment.relative_to(self.root))],
                    "notebook_revision": "abc123",
                }
            ),
            encoding="utf-8",
        )
        self.assertEqual(self.messages(), [])

    def test_ledger_rejects_escaping_evidence(self) -> None:
        ledger = self.root / "jobs" / "processed" / "Slurm" / "wrong.json"
        ledger.parent.mkdir(parents=True)
        ledger.write_text(
            json.dumps(
                {
                    "schema_version": 2,
                    "backend": "Slurm",
                    "job_id": "../job",
                    "experiment_id": "",
                    "terminal_status": "done",
                    "processed_at": "2026-08-11",
                    "evidence": ["../outside.md"],
                    "notebook_revision": "",
                }
            ),
            encoding="utf-8",
        )
        messages = self.messages()
        self.assertIn("invalid normalized backend 'Slurm'", messages)
        self.assertIn("unsupported schema_version", messages)
        self.assertTrue(any("stay inside notebook" in message for message in messages))

    def test_active_plan_contract(self) -> None:
        plans = self.root / "plans"
        plans.mkdir()
        (plans / "2026-08-11-synthetic-control.md").write_text(
            PLAN, encoding="utf-8"
        )
        self.assertEqual(self.messages(), [])

    def test_plan_created_date_must_match_filename(self) -> None:
        plans = self.root / "plans"
        plans.mkdir()
        (plans / "2026-08-10-synthetic-control.md").write_text(
            PLAN, encoding="utf-8"
        )
        self.assertIn("created date does not match filename", self.messages())

    def test_terminal_plan_requires_closure_and_no_next_action(self) -> None:
        plans = self.root / "plans" / "completed"
        plans.mkdir(parents=True)
        (plans / "2026-08-11-synthetic-control.md").write_text(
            PLAN.replace("status: active", "status: completed"),
            encoding="utf-8",
        )
        messages = self.messages()
        self.assertIn("terminal plan next_action must be empty or none", messages)
        self.assertIn("terminal plan lacks ## Disposition", messages)
        self.assertIn("terminal plan lacks ## Evidence", messages)

    def test_terminal_plan_with_disposition_is_valid(self) -> None:
        plans = self.root / "plans" / "completed"
        plans.mkdir(parents=True)
        terminal = PLAN.replace("status: active", "status: completed").replace(
            "next_action: Run Phase 1", "next_action: none"
        )
        terminal += "\n## Disposition\n\nThe control passed.\n\n## Evidence\n\n- [[EXP-001]]\n"
        (plans / "2026-08-11-synthetic-control.md").write_text(
            terminal, encoding="utf-8"
        )
        self.assertEqual(self.messages(), [])

    def test_plan_status_directory_and_gate_metadata(self) -> None:
        plans = self.root / "plans" / "gated"
        plans.mkdir(parents=True)
        gated = PLAN.replace("status: active", "status: gated").replace(
            "current_phase: Phase 1",
            "current_phase: Phase 1\ngate: Human review of pilot evidence\nrevisit_when: Reviewer approves Phase 2",
        )
        (plans / "2026-08-11-synthetic-control.md").write_text(
            gated, encoding="utf-8"
        )
        self.assertEqual(self.messages(), [])

        path = plans / "2026-08-11-synthetic-control.md"
        path.write_text(
            gated.replace("gate: Human review of pilot evidence\n", "").replace(
                "revisit_when: Reviewer approves Phase 2\n", ""
            ),
            encoding="utf-8",
        )
        messages = self.messages()
        self.assertIn("gated plan requires gate", messages)
        self.assertIn(
            "gated plan requires one of: revisit_when, promote_when", messages
        )

    def test_plan_status_must_match_directory(self) -> None:
        plans = self.root / "plans"
        plans.mkdir()
        (plans / "2026-08-11-synthetic-control.md").write_text(
            PLAN.replace("status: active", "status: draft"), encoding="utf-8"
        )
        self.assertIn("status 'draft' belongs in draft/", self.messages())

    def test_plan_link_must_resolve(self) -> None:
        plans = self.root / "plans"
        plans.mkdir()
        linked = PLAN.replace(
            "- [[EXP-001]]", "- [missing experiment](experiments/EXP-999.md)"
        )
        (plans / "2026-08-11-synthetic-control.md").write_text(
            linked, encoding="utf-8"
        )
        self.assertIn(
            "broken plan link experiments/EXP-999.md", self.messages()
        )

    def test_json_diagnostics_are_stable(self) -> None:
        root, issues = validator.validate(self.root)
        report = validator.diagnostics_report(root, issues, strict=False)
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(
            report["notebook_schema_version"], validator.SCHEMA["schema_version"]
        )
        self.assertTrue(report["valid"])
        self.assertEqual(report["counts"], {"errors": 0, "warnings": 0})

    def test_plan_index_is_deterministic(self) -> None:
        plans = self.root / "plans"
        plans.mkdir()
        (plans / "2026-08-11-synthetic-control.md").write_text(
            PLAN, encoding="utf-8"
        )
        first = validator.render_plan_index(self.root)
        second = validator.render_plan_index(self.root)
        self.assertEqual(first, second)
        self.assertIn("## Active", first)
        self.assertIn("[Synthetic control campaign]", first)


if __name__ == "__main__":
    unittest.main()
