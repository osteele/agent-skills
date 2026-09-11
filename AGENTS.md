# Repository guidance

This repository publishes the Research Notebook System, including its file
contracts, validator, examples, and portable Agent Skills.

## Development

- Keep each `SKILL.md` concise and imperative.
- Put detailed formats in the skill's `references/` directory.
- Keep references one link away from `SKILL.md`.
- Use only the `name` and `description` fields in SKILL.md frontmatter.
- Do not add agent-specific features to the core notebook format.
- Keep job-runner commands in the setup skill and project-local adapters.
- Support explicitly authorized bounded plan execution, including unattended
  reporting. Continuous execution removes routine conversational pauses only;
  preserve scientific, human-review, scope, budget, and permission gates.
- Keep plan preview and results walkthrough (replay) read-only. Do not launch
  jobs, regenerate missing evidence, or mutate execution state for either.
- Do not add unsolicited or open-ended autonomous research loops or code-audit
  behavior.
- Do not include personal paths, hosts, collaborators, unpublished results, or
  private project names.

Run `just check` before committing.
