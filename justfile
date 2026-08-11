default:
    @just --list

check:
    python3 scripts/validate-skills.py
    python3 skills/research-lab-notebook/scripts/validate-notebook.py --self-test
    python3 -B -m unittest discover -s tests
    python3 skills/research-lab-notebook/scripts/validate-notebook.py --strict examples/gradient-accumulation
    python3 -B examples/gradient-accumulation/scripts/simulate.py --condition true-batch --seed 1

check-spec:
    uvx --from skills-ref agentskills validate skills/research-lab-notebook
    uvx --from skills-ref agentskills validate skills/download-research-references

check-site site:
    python3 scripts/check-site-contract.py {{site}}
