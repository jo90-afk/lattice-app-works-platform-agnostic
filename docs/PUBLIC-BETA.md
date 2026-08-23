# Lattice 0.1 public beta

Lattice 0.1 is designed to be initialized from the sanitized repository without depending on an existing conversation, hidden host state, or a pre-existing local database.

## Supported local bootstrap environments

The dependency-free local path supports CPython 3.10 or newer on macOS, Windows, and Linux. The repository uses `pathlib`, the Python standard library, and SQLite for the default runtime. Platform-specific shell features are not part of the initialization contract.

From a fresh clone, run:

```text
python scripts/lattice.py doctor
python scripts/lattice.py initialize --principal-alias "Repository Owner" --project-id first-project --project-name "First Project"
python scripts/lattice.py validate
```

On systems where `python` does not resolve to Python 3, use `python3` instead. The commands themselves are the same on all three operating systems.

`doctor` is non-destructive. Initialization is intentionally one-time for the neutral starter capsule: it replaces `example-001` with the chosen project identity and updates the portable state and generated host projection. Do not repeatedly initialize an already initialized repository.

## Repository privacy boundary

The public repository is a sanitized seed and may be forked or cloned publicly. Real project state should normally live in a private repository unless every durable record, truth, source, artifact, evidence reference, and event is suitable for publication.

Treat `state/current.json` as potentially sensitive even though it is structured state rather than free-form conversation. Commit it in the repository that owns the project because it is the portable state contract. Do not commit `.lattice/`; it contains operational local state and leases.

Do not place credentials, access tokens, private source documents, addresses, calendars, health information, financial information, or direct personal identifiers in a public project capsule or its truth ledger. A source reference can itself disclose private information even when the source body is stored elsewhere.

When converting an initialized public experiment into real work, create a private repository before adding private project material. Do not rely on later deletion as a privacy control; Git history may retain removed content.

## Stable 0.1 interfaces

The following interfaces are the supported public-beta contracts for the 0.1 line:

- `state/current.json`: portable snapshot, schema version 1;
- `runtime/host-adapter.schema.json`: host-adapter envelope, protocol version 1;
- hosted deltas accepted by `scripts/lattice.py apply-delta`;
- the machine-readable supervision/read model exposed by `scripts/lattice.py inspect` and `/api/state`;
- `scripts/capabilities.py`: machine-readable package and capability negotiation;
- `scripts/migrate.py`: snapshot compatibility, backup, and guarded local restore.

Additive fields may appear within the 0.1 line. An incompatible change to one of these contracts requires an explicit version change rather than silent reinterpretation.

## Initialization reproducibility

CI runs a fresh-seed bootstrap smoke test on Ubuntu, Windows, and macOS. The smoke test copies the tracked seed to a temporary path, initializes a neutral project using only Python, validates the resulting repository contract, and checks that a frontier can be derived from the initialized state. This catches path, subprocess, encoding, and platform assumptions before a public-beta change can merge.

The cross-platform smoke test validates the local SQLite bootstrap path. Postgres is an optional shared-writer deployment and is exercised separately in the primary Linux CI job.

## Recovery and migration

Before changing package versions or experimenting with state tooling, inspect compatibility and create a portable backup:

```text
python scripts/migrate.py status
python scripts/migrate.py backup --output lattice-backup.json
```

Local rollback is guarded. Restore refuses to run while active leases exist. When `LATTICE_DATABASE_URL` selects Postgres, file-level rollback is refused because the shared database is authoritative; use an operational database backup/restore procedure instead.

## Public-beta claim boundary

Lattice 0.1 may be described as a local-first, host-agnostic control plane for durable project state, frontier-derived work, bounded authority, independent verification, recovery, and exception-based human supervision.

The public beta does not claim universal provider independence, compatibility with every execution host, or production-grade autonomy for consequential systems. Host portability is an evidence question and remains measured through bounded evaluation rather than assumed from interface similarity.
