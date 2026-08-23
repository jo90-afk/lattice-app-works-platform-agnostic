# Migration and rollback

Lattice 0.1 keeps the portable `state/current.json` snapshot as the migration boundary. Public package version, Agency compatibility version, and state schema version are separate values; upgrading the package does not imply a state migration.

Check the current relationship before changing runtime versions:

```bash
python3 scripts/migrate.py status
```

A status with `migration_required: false` means the current portable snapshot schema is already accepted by the installed runtime.

## Create a rollback point

Before any future state-schema migration or other consequential state maintenance, create a portable backup:

```bash
python3 scripts/migrate.py backup --output .lattice/backups/before-upgrade.json
```

The backup contains the full portable snapshot plus release, Agency compatibility version, schema version, creation time, and a snapshot hash. It does not include leases because leases are deliberately ephemeral and excluded from the portable state contract.

## Restore a portable backup

For the default local SQLite runtime:

```bash
python3 scripts/migrate.py restore --file .lattice/backups/before-upgrade.json
python3 scripts/lattice.py doctor
python3 scripts/lattice.py status
```

Restore refuses to proceed while local action leases are active. Finish, release, or recover those actions first; otherwise rollback could restore durable state underneath live execution authority.

Restore also refuses a backup whose schema does not match the currently running code. In that situation, roll the code/runtime back to a version that accepts the backup schema before restoring the snapshot.

## Shared Postgres deployments

When `LATTICE_DATABASE_URL` is configured, the live database is authoritative and repository snapshot restoration is intentionally disabled. A file-level snapshot rollback must not masquerade as a database rollback.

Put the shared runtime into maintenance, use the database platform's transactional backup/recovery procedure, restore a compatible Lattice runtime, then publish a new portable checkpoint. See `scripts/shared_state_checkpoint.py` for explicit checkpoint publication.

## Migration rule

A future migration must preserve these rollback properties:

1. state-schema changes are explicit and versioned;
2. a pre-migration backup is created before destructive transformation;
3. active execution authority cannot survive underneath restored older state;
4. shared Postgres recovery is performed at the authoritative database boundary;
5. public package version changes alone do not rewrite state.
