# Portability

`state/current.json` is the cross-host state contract. It contains every durable table except leases. `.lattice/state.db` is a local transactional index and can be deleted and rebuilt from the snapshot.

Source code and human-facing artifacts stay in project capsules or in an explicitly external project workspace. Hosts do not need to understand each other's proprietary memory, filesystem layout, or agent configuration. They need only:

- root agency guidance;
- selectively resolved role and platform expertise;
- the guarded CLI or a scoped host projection;
- the current state revision; and
- exact project artifact references.

Repository-local artifacts use `projects/<project-id>/...` paths. Hosted work whose durable project files live outside the Lattice engine can instead submit a typed logical reference of the form `project-artifact://<project-id>/<project-relative-path>`, for example `project-artifact://first-project/platform/src/app.py`. Lattice applies the same `agency.yaml` role write domains to the project-relative path, rejects traversal and cross-project refs, and does not require the artifact to exist under the engine's own `projects/` directory.

Typed project artifact references assert governed project provenance, not engine-local file existence. Opaque URIs such as `artifact://build-output` remain external logical evidence and are not interpreted as project paths.

Generated ChatGPT Work packs are disposable. Chat memory, uploaded sources, and local database files never outrank the committed snapshot.
