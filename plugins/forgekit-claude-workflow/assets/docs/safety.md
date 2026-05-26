# Safety

The ForgeKit plugin is a distribution package, not an automation switch.

It must not:

- Include `user-rules/`.
- Include external development records.
- Include credentials, tokens, private URLs, or machine-specific paths.
- Enable hooks by default.
- Enable MCP by default.
- Trigger issue, pull request, deployment, tag, push, or other external writes without explicit confirmation.

Before a team enables commands, hooks, plugins, MCP, CI, or issue tracker integrations, review the generated project's `governance/team-agent-rollout.md`.
