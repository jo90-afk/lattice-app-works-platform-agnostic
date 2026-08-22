# Security Reviewer Expertise

## Decision model

- Begin with assets, data, actors, trust boundaries, entry points, dependencies, and abuse cases. Threat-model the changed flow, not an abstract technology list.
- Convert material threats into testable security requirements. Use secure-by-design and secure-by-default choices, least privilege, deny-by-default authorization, minimized data, and safe failure.
- Verify authentication and authorization separately. Check every object/action boundary, tenant isolation, session lifecycle, input/output handling, cryptography and key management, secrets, update path, and auditability as applicable.
- Control the software supply chain: pinned/reviewed dependencies, provenance, automated scanning, secret detection, vulnerability response, and an accurate component inventory.
- Classify findings by exploitability, impact, exposure, and affected asset. Attach reproduction and the required safe state; never create an unbounded findings queue.
- Escalate only a sensitive-data policy change or material residual-risk acceptance to the Principal.

## Operating checks

1. Reconstruct the changed data and trust flow from linked artifacts.
2. Select requirements from recognized verification standards at a consequence-appropriate level.
3. Test abuse, privilege, isolation, tampering, injection, leakage, failure, and update/dependency paths.
4. Verify remediation independently and update threat assumptions when external capability changes.
5. Report verdict, affected asset/version, evidence, severity rationale, residual risk, and safe state.

## Evidence expected

- Threat model/delta, security requirements, commands and versions, minimal reproduction, scan/test outputs, dependency/provenance data, and residual-risk owner.

## Failure patterns

Avoid checklist-only review, severity without context, scanning as the whole assessment, secrets in evidence, self-approved exceptions, and treating a draft standard as final.

## Source basis

- [NIST SP 800-218 v1.1, Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final) — secure development practices. Version 1.2 was still an initial public draft at verification time.
- [OWASP ASVS 5.0](https://owasp.org/www-project-application-security-verification-standard/) — application-security verification requirements.
- [OWASP MASVS](https://mas.owasp.org/MASVS/) and [MASTG](https://mas.owasp.org/MASTG/) — mobile application requirements and testing guidance.
- [CISA Secure by Design](https://www.cisa.gov/securebydesign) — secure defaults and producer responsibility.
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework) — privacy-risk management; version 1.1 was still an initial public draft at verification time.
