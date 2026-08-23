# Capability negotiation

Lattice 0.1 exposes a small machine-readable capability document so execution hosts and wrappers can determine what this checkout actually supports without guessing from the public package version.

```bash
python3 scripts/capabilities.py
```

Use `--compact` for single-line JSON.

The document separates:

- public package `release`;
- `agency_version`, the Agency Kernel compatibility line;
- portable `state_snapshot_schema`;
- `host_adapter_protocol`;
- hosted delta schema;
- control read-model version;
- available state backends;
- supported host-adapter operations; and
- coarse feature capabilities.

A host should negotiate against the narrow contract it consumes. For example, a host-adapter client should check `host_adapter_protocol` and the operation list rather than assuming that every Lattice 0.1.x checkout has identical host integration behavior.

The public release version may advance while compatibility values remain stable. Conversely, a future incompatible state or protocol migration must change the relevant compatibility field rather than hiding the break behind the package version.

Capability output is descriptive. It does not grant role authority, enable tools, or change project state.
