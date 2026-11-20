# Security Policy

## Reporting a vulnerability

Please report security problems **privately** through GitHub's private vulnerability reporting:

1. Open the repository's **Security** tab.
2. Click **Report a vulnerability**.

Direct link: https://github.com/sandraschi/calibremcp/security/advisories/new

Please do **not** open a public issue, discussion or pull request for a security problem, and do not include working exploits or real secrets in anything public.

## What happens next

- You will get an acknowledgement in the private advisory thread.
- Confirmed issues are fixed and published as a GitHub Security Advisory (with a CVE where appropriate), crediting you unless you prefer otherwise.
- We follow coordinated disclosure and are happy to agree on a timeline with you.

## Scope

These projects are mostly MCP servers and tools that run locally with the privileges of the user who starts them. Issues that let a client, an agent or prompt-injected content reach beyond a tool's intended scope (for example file access outside a configured directory, command execution, or credential exposure) are in scope.
