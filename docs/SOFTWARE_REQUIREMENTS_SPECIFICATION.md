# Software requirements specification

## Actors and access

Students access their own profile, enrolled courses, device records, biometric enrollment, eligible sessions, attempts, attendance and disputes. Faculty access assigned courses and their sessions, records, events, reports and corrections. Administrators manage institution accounts, classrooms, enrollment, device resets, policy and institution-wide data. Backend dependencies and per-course checks implement these restrictions independently of navigation visibility.

## Functional requirements

| ID | Requirement | Implemented entry point |
|---|---|---|
| AUTH-01 | Argon2id login, expiring JWT and rotating refresh sessions | `/auth/login`, `/auth/refresh`, `/auth/logout` |
| AUTH-02 | Institution-managed accounts; optional student-only registration | `/users`, `/auth/register` |
| ACAD-01 | Course assignment and student enrollment | `/courses`, `/courses/{id}/enrollments` |
| ACAD-02 | Classroom coordinates, radius and Wi-Fi references | `/classrooms` |
| ACAD-03 | Time-bounded session creation and closure | `/sessions` |
| ID-01 | Consent, real embeddings, protected storage and deletion | `/biometrics/enroll`, `/biometrics` |
| ID-02 | Random single-use temporal challenge | `/challenges`, `services/vision.py` |
| ID-03 | One active device, signed evidence and approved replacement | `/devices`, `/device-resets` |
| LOC-01 | Haversine, GPS accuracy/freshness and boundary uncertainty | `services/presence.py` |
| LOC-02 | Real Android AP observations and explicit unavailable policy | `mobile/modules/spvs-wifi`, `/policy` |
| DEC-01 | Deterministic decision with hard security gates | `/attendance/verify` |
| DEC-02 | Idempotent retry and atomic attendance record | `AttendanceAttempt`, `AttendanceRecord` constraints |
| AUD-01 | Explainable events, reasons and correction history | `/events`, `/corrections` |
| REV-01 | Student disputes and scoped resolution | `/disputes` |
| REP-01 | Real metrics and escaped CSV exports | `/overview`, `/reports/attendance.csv` |

## Non-functional requirements

Passwords and templates must not appear in logs or normal API responses. No raw biometric capture is persisted server-side. Secrets are generated locally and excluded from distribution. Input models reject unknown fields, non-finite numeric values, out-of-range coordinates and naive timestamps. Actual request bytes are bounded to 15 MB, with individual JPEG dimensions and sizes validated before decoding.

Database decisions must survive concurrent submissions through transactions and constraints. Test data is isolated in a `_test` database. Dependency lockfiles and model checksums make dependency and model selection reproducible. Dashboard controls provide visible labels, error states and keyboard focus. Native permissions must have understandable denial behavior.

## Configuration and operational constraints

The default Wi-Fi fallback is manual review. The default face cosine threshold is 0.5, an initial threshold requiring institutional calibration. GPS accuracy is limited to 35 m and age to 20 seconds by default. Challenge lifetime is 60 seconds and normal maximum attempts are five per session. Policy updates require administrator authority and an audit reason.

Platform attestation is a fail-closed integration boundary. Setting `require_attestation=true` routes otherwise passing attempts to review until a real provider is installed. There is no hidden pass mode or client-controlled integrity boolean.
