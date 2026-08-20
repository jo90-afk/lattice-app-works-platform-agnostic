# Operational state

`current.json` is the portable, deterministic representation of Lattice's operational state. The guarded runtime loads it into local SQLite at `.lattice/state.db` and refreshes it after every durable mutation.

The SQLite file is deliberately ignored by Git. It contains local indexes and expiring action leases; `current.json` contains durable objectives, conditions, truth history, evidence, commitments, exceptions, and events. Do not edit either file by hand.

Use:

    python3 scripts/lattice.py status
    python3 scripts/lattice.py state-export
    python3 scripts/lattice.py state-import --file state/current.json --expected-revision <revision>

Run only one writable runtime against a project snapshot at a time. Simultaneous remote workers require a shared transactional service rather than independent SQLite copies.
