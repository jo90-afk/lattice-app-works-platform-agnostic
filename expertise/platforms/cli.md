# Command-Line Platform Pack

Use this pack for terminal-first command-line interfaces, whether standalone or an administration surface for another system.

## Platform rules

- Make commands composable and predictable: stable exit status, stdout for requested results, stderr for diagnostics, and no interactive prompts when non-interactive operation is declared.
- Follow the target operating environment's argument conventions. Provide concise `--help`, useful usage errors, explicit defaults, consistent subcommands/options, and version information.
- Support both human-readable output and a versioned machine-readable format when automation is a requirement. Do not parse decoration as data.
- Detect terminal capabilities; respect non-TTY pipelines, terminal width, locale/encoding, `NO_COLOR` or an equivalent opt-out, and accessible alternatives to animation/color.
- Make destructive or irreversible operations explicit, scoped, previewable, and confirmable in interactive use. Provide an intentional non-interactive override rather than guessing.
- Define configuration precedence, environment-variable handling, secret redaction, timeouts, retries, idempotency, signal/cancellation behavior, and partial-failure output.

## Evidence to add

Record supported shells/operating systems, golden and property tests for parsing/output, exit-code matrix, pipe/redirection cases, narrow/non-color/non-TTY behavior, cancellation/signals, secret-redaction tests, and install/upgrade behavior.

## Primary sources

- [POSIX Utility Syntax Guidelines](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap12.html) — normative conventions for POSIX environments.
- [GNU command-line interface standards](https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html) — GNU project conventions; apply only where compatible with the target ecosystem.
