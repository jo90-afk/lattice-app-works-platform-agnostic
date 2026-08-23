# Shared State Authority

Lattice keeps two different state representations for different purposes:

- the operational store is authoritative while workers are running;
- `state/current.json` is the portable checkpoint and interchange contract.

For the default SQLite runtime these are normally co-located, so the local store can reconcile itself from the repository snapshot on startup.

For a shared Postgres runtime the rule is stricter. A repository checkout may be older than the live database, and multiple workers may not even share a filesystem. Therefore a Postgres store may import `state/current.json` automatically only when the operational database is empty. Once durable project state exists, connecting to Postgres never rewinds it from a repository snapshot.

Postgres workers also do not publish the repository checkpoint after every guarded mutation. `StateStore` methods may request an export as part of their local durability path, but `PostgresStateStore` treats those implicit exports as in-memory projections. A checkpoint file is written only when an explicit destination is supplied, such as a deliberate state export or release checkpoint.

This preserves one state authority under concurrent execution while retaining a backend-neutral portable snapshot for migration, disaster recovery, inspection, and version-controlled release checkpoints.
