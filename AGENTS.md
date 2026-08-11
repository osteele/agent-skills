# Repository guidance

This repository publishes portable Agent Skills for file-based research
notebooks.

## Development

- Keep each `SKILL.md` concise and imperative.
- Put detailed formats in the skill's `references/` directory.
- Keep references one link away from `SKILL.md`.
- Use only the `name` and `description` fields in SKILL.md frontmatter.
- Do not add agent-specific features to the core notebook format.
- Keep job-runner commands in the setup skill and project-local adapters.
- Do not add autonomous execution or code-audit behavior.
- Do not include personal paths, hosts, collaborators, unpublished results, or
  private project names.

Run `just check` before committing.
