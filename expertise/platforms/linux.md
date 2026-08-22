# Linux Desktop Platform Pack

Use this pack for a declared Linux desktop application. Select the relevant desktop, distribution, packaging, and display/session matrix rather than treating Linux as one UI platform.

## Platform rules

- Follow the target desktop's current human-interface guidance. GNOME and KDE have different conventions; preserve native navigation, shortcuts, menus, settings, windows, notifications, and help behavior where targeted.
- Integrate with declared desktop services and standards for files, URLs, MIME types, portals, themes, localization, accessibility, notifications, and session behavior.
- Support keyboard-first operation, scaling, high contrast/themes, screen readers, alternate input, and predictable focus.
- Prefer least-privilege sandbox/portal access where the packaging model supports it. Make filesystem, device, network, secret storage, and update access explicit.
- Define supported distributions/runtimes, CPU architectures, display servers/desktops, package formats, dependency strategy, signing, install/update/uninstall, and user-data retention.
- Test behavior in the actual supported environments; a successful build on one distribution is not Linux compatibility evidence.

## Evidence to add

Record distro/desktop/session/package/architecture matrix, keyboard and assistive-technology results, portal/permission cases, install/update/uninstall evidence, and dependency/runtime compatibility.

## Primary sources

- [GNOME Human Interface Guidelines](https://developer.gnome.org/hig/).
- [KDE Human Interface Guidelines](https://develop.kde.org/hig/).
