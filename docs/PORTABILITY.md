# Portability

`state/current.json` is the cross-host state contract. It contains every durable table except leases. `.lattice/state.db` is a local transactional index and can be deleted and rebuilt from the snapshot.

Source code and human-facing artifacts stay in project capsules. Hosts do not need to understand each other's proprietary memory or agent configuration. They need only:

- root agency guidance;
- selectively resolved role and platform expertise;
- the guarded CLI or a scoped host projection;
- the current state revision; and
- exact project artifact paths.

Generated ChatGPT Work packs are disposable. Chat memory, uploaded sources, and local database files never outrank the committed snapshot.
