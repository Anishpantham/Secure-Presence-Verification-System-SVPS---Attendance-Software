# Requirements traceability

| Requirement | Implementation | Automated evidence | Remaining validation |
|---|---|---|---|
| Persistent normalized storage | 20 SQLAlchemy tables + explicit Alembic migration | Migration/table/constraint tests on PostgreSQL | Deployment backups and restore drill |
| Password/JWT/refresh security | `core/security.py`, `api/auth.py` | Login, invalid JWT, rotation, reuse and logout tests | Operational key rotation |
| Backend role restrictions | `roles`, `access_course`, `session_ids` | Student/staff denial, cross-course checks and role-change tests | Institution-specific account lifecycle |
| Academic management | `api/academic.py`, dashboard courses/classrooms/sessions | CRUD/session lifecycle and browser workflow | Real campus data entry |
| Actual face recognition | YuNet + SFace in `services/vision.py` | Real same-face/different-person/no-face/multi-face tests | Consented local calibration |
| Enrollment consent/deletion | `/biometrics/enroll`, DELETE `/biometrics` | API consent/storage/deletion contract tests | Live student enrollment |
| Temporal liveness | MediaPipe landmarks + sequence validator | EAR/pose sequence, timing, expiry tests | Physical phone spoofing/usability matrix |
| Device binding | Random key + HMAC + unique active-device index | Signature/device mismatch, second-device denial and reset tests | SecureStore on physical Android/iOS |
| Platform integrity | `services/attestation.py` fail-closed boundary | Unconfigured policy never passes as verified | Provider accounts, verifier, nonce and verdict tests |
| GPS evidence | Haversine + uncertainty/freshness gates | Boundary/stale/inaccurate/mock/travel tests | Indoor GPS field measurements |
| Wi-Fi evidence | Native Android scan module + reference matching | Matching/weak/unavailable policy tests | Kotlin build and real AP scans; see current report |
| Deterministic decision | `/attendance/verify` + presence service | Hard-gate and decision API tests | Full real-device happy path |
| Concurrency/idempotency | Transaction locks + unique constraints | Simultaneous identical requests, replay and duplicates | Load testing |
| Auditing/anomalies | Structured events and correction ledger | Repeated failures, device reset, policy/role/correction audit | External immutable sink if required |
| Faculty reports | Aggregates, Recharts and scoped CSV | CSV escaping, live browser export, actual API counts | Large data export performance |
| Student disputes | Mobile history + scoped dispute API | Ownership and resolution tests | Real student support process |
| Dashboard quality | React, router, query, labeled forms and responsive CSS | Interaction tests, production build, Chromium workflow | Assistive technology and usability study |
| Student app integration | Expo camera/location/SecureStore/API signing | TypeScript, HMAC/boundary tests, Metro/Hermes export | Physical sensor/permission tests |
| Documentation/artifacts | Markdown, diagrams, PDF/ZIP packaging script | PDF text/page and ZIP CRC/contents checks | Fill academic identity placeholders |

“Automated” in this table does not imply manually tested. The generated verification report identifies the current counts and commands. No fake biometric approval or sensor measurement is used by application code.
