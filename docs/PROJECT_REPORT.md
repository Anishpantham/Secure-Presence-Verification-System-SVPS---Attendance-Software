# Secure Presence Verification System

Current validation and publication are recorded in
[current status](CURRENT_STATUS.md) and the
[27 October synchronization checkpoint](REPOSITORY_SYNC_2026-10-27.md).
Delivery PDFs are regenerated for that checkpoint. The 24 October ecosystem
audit remains a historical record of the earlier local/remote gap.

## Title page

The current attendance protocol adds mandatory rotating QR and acoustic proof to
the identity/location checks. See [protocol details](ACOUSTIC_DYNAMIC_QR.md),
[Mac runtime integration](LOCAL_RUNTIME_UPDATE_2026-10-27.md), and
[C003 evidence scope](C003_CLASSROOM_VALIDATION_2026-10-27.md). Earlier physical
results do not establish the new acoustic channel's classroom performance.

**A two-layer attendance verification platform for educational institutions**

College / University: **[Enter institution name]**

Department: **[Enter department]**

Submitted by: **[Enter student name(s)]**

Roll number(s): **[Enter roll number(s)]**

Project supervisor: **[Enter supervisor name and designation]**

Academic year / semester: **[Enter academic year and semester]**

Project abbreviation: **SPVS**. Source repository: Secure-Presence-Verification-System-SVPS---Attendance-Software. The inherited repository name uses SVPS; the implemented product and API use SPVS consistently.

## Abstract

SPVS is an integrated student attendance system that combines biometric identity evidence with physical-presence evidence. The backend validates a randomized temporal face challenge, a real pretrained face embedding, a device-held signing credential, current GPS measurements and available Wi-Fi observations. It produces explicit present, rejected, review, retry or expired decisions. PostgreSQL transactions and unique constraints prevent duplicate successful attendance, while faculty corrections require attributable reasons.

The implementation uses FastAPI, SQLAlchemy, PostgreSQL, OpenCV SFace/YuNet, MediaPipe, a React institutional dashboard and an Expo student application. It includes actual API integration, migrations, automated tests, model checksums, dependency locks and submission artifacts. Verification evidence is separated from claims that require a physical phone or external attestation configuration. The system demonstrates layered resistance and accountable review without claiming to prevent every spoofing or collusion attack.

## 1. Introduction

Attendance is both an academic record and a security-sensitive institutional workflow. A presence claim affects eligibility, evaluation and student disputes. A simple token or register makes recording convenient but may provide little evidence about who submitted the claim or where that person was located. At the same time, a complex verification system can harm usability if it silently rejects students or overstates the reliability of noisy sensor data.

SPVS approaches the problem through two primary layers. Identity verification evaluates a consented face template, a fresh challenge and an authorized device. Physical presence verification evaluates location quality, the classroom geofence and supported Wi-Fi signals. Supporting authentication, academic configuration, reports and auditing make those layers usable in an actual college workflow.

## 2. Problem statement

Traditional methods allow shared tokens, proxy responses, remote submissions and unaccountable edits. A mobile client is an untrusted input source; it must not declare its own face similarity or distance from a classroom. Shared tokens, expired sessions and repeated requests require server-side controls.

Software-only verification cannot absolutely prove presence against a fully compromised phone or coordinated attackers. The engineering problem is therefore to enforce meaningful gates, expose uncertainty, preserve accountability and evaluate the limitations honestly. SPVS excludes surveillance cameras and additional beacon hardware, keeping the project reproducible with normal student phones.

## 3. Objectives

1. Implement a complete role-based academic attendance workflow.
2. Use actual model-generated face embeddings with consent and protected template storage.
3. Validate randomized temporal challenges on the server.
4. Bind evidence to an authorized device credential and a fresh session.
5. Calculate geofence and signal decisions from submitted measurements on the server.
6. Make retries, replay, concurrency and corrections deterministic and testable.
7. Provide understandable student outcomes and an accountable faculty review process.
8. Deliver source, documentation, measured test evidence and reproducible setup.

## 4. Existing systems and limitations

Manual registers are simple but allow proxy marks and require transcription. Static QR or code-based systems are convenient but shared tokens can travel beyond the classroom. Pure GPS systems are affected by indoor uncertainty and spoofing. Face-only systems may accept photograph/video presentation if identity matching is confused with liveness. Device identifiers can be copied and do not establish cryptographic possession.

Adding more signals does not automatically establish strong assurance. A high weighted score can conceal a failed security gate if the decision algorithm is poorly designed. SPVS instead enforces mandatory identity/session/device conditions before evaluating supporting location evidence, then routes ambiguity to review or retry.

## 5. Proposed system

The student receives an institution-managed account, registers one device and consents to biometric enrollment. Faculty open a session for a course and configured classroom. The student requests a bound challenge, performs a short face sequence and collects real foreground location and supported Wi-Fi data. The app signs exact evidence bytes and submits them to FastAPI.

The server checks access, enrollment, session timing, device signature and challenge ownership. It detects and aligns the face, calculates SFace embeddings, compares each frame and analyzes temporal landmarks. Only after these gates pass does it evaluate geofence uncertainty, freshness, Wi-Fi policy and anomalies. A successful decision inserts one attendance record; other states remain attempts that can be disputed and reviewed.

## 6. Related work and implementation references

The system builds on documented OpenCV face detection/recognition APIs, MediaPipe facial landmarks, modern password hashing and relational transaction controls. OpenCV's published face tutorial supplies an example matching baseline, not an experimental result from this project. Android documentation explains why Wi-Fi scanning and location permissions cannot be assumed to work uniformly. Google and Apple attestation guides describe provider verification boundaries that require external configuration.

The bibliography lists official documentation, pinned model source and actual test-image provenance. No invented publication, benchmark accuracy, institutional deployment or user study is claimed.

## 7. System requirements

The backend requires Python 3.11/3.12-compatible dependencies, PostgreSQL 15+ (16 in Compose), the pinned model files and generated JWT/Fernet secrets. The dashboard requires a supported Node runtime and a modern browser. Student verification requires a camera-equipped Android/iOS phone, foreground location permission and a reachable API. Android native testing needs a development build, compatible JDK/SDK and the included local Wi-Fi module. iOS requires macOS/Xcode signing and exposes no general Wi-Fi scan API in this implementation.

The primary developer target is a MacBook Air M4. Native ARM64 Python/Node and Docker Desktop are documented. Automated execution in this submission occurred on Linux x86_64; that does not establish Apple Silicon runtime testing.

## 8. Architecture

The architecture has client, API/service and persistence tiers. The dashboard performs staff operations through a same-origin API proxy. The student app holds credentials in OS secure storage and sends signed evidence. FastAPI enforces roles and scopes, coordinates verification services and records outcomes in PostgreSQL.

The architectural, sequence and decision diagrams in `SYSTEM_ARCHITECTURE.md` are part of this report's generated PDF appendices. OpenCV and MediaPipe inference are synchronous; FastAPI synchronous handlers use its worker thread pool. A per-worker lock guards model instances. Database rate limits and transactional locks remain shared across API workers.

## 9. Database design

Twenty normalized application tables cover accounts/subtypes, courses/enrollment, classrooms/Wi-Fi, policy, devices/resets, templates, sessions/challenges, attempts/records, events/corrections/disputes, refresh tokens and rate buckets. Foreign keys preserve ownership and attribution. Unique student/session records prevent duplicate official attendance. A partial unique active-device index enforces the normal one-device limit.

Attempts retain reasons and a coarse evidence summary rather than raw images. Corrections retain the actor, reason and previous/new status. Refresh tokens are hashed and grouped into revocable families. The explicit Alembic migration and ER diagram are included in the database appendix.

## 10. Implementation methodology

Development proceeded from relational/authentication foundations to academic workflows, identity/presence services, client integration, tests and documentation. Each API operation uses a Pydantic input contract. Unknown fields, invalid coordinates and malformed timestamps are rejected. Role-scoped queries and object checks protect backend data independently of UI navigation.

The dashboard provides labeled forms, searchable tables, status labels, real aggregate charts and scoped exports. The mobile app provides enrollment consent, permission handling, sequential camera capture, location acquisition, signing and result/history screens. Android reads recent real scan results; iOS reads only permitted current-network BSSID. Both report unavailable evidence explicitly.

## 11. Identity verification design

YuNet detects exactly one usable face; SFace generates a normalized 128-dimensional embedding from the aligned crop. The enrolled template is encrypted under a key separate from JWT signing. Every frame must match the reference at the configured threshold. Enrollment frames also match one another before averaging.

MediaPipe supplies facial landmarks. A blink requires open/closed/open eye-aspect transitions. Head actions use normalized nose displacement and stable consecutive observations. Frames must be ordered, within the challenge period and separated by plausible time intervals. Challenge IDs are unpredictable and single-use. These controls provide basic replay resistance, not certified capture provenance or comprehensive deepfake resistance.

## 12. Physical presence design

Haversine distance is calculated on the server. Location age, future timestamps, uncertainty and reported mock indicators are checked before accepting a geofence. An uncertainty circle fully outside the radius rejects; an overlapping boundary routes to review. Android Wi-Fi observations are matched by known BSSID and minimum RSSI, requiring at least half of configured references when available.

An explicit Android policy controls missing Wi-Fi: review, reject or reduced-assurance GPS-only. The separate iOS policy defaults to review, with explicit retry/GPS-only options. A coarse travel rule flags implausible movement over short periods. Unconfigured platform attestation never returns a verified result. Numerical risk communicates concern and never bypasses a failed mandatory gate.

## 13. Security design

Passwords use Argon2id. JWTs validate issuer, audience, expiry and token type. Refresh sessions rotate transactionally and revoke their family after reuse. Device signatures cover both an idempotency key and exact JSON bytes, using a native P-256 private key and registered server-side public key (legacy HMAC remains readable for migration).

Student/challenge/session locks protect the attendance transaction. A retry returns the existing attempt only when the signed evidence matches. A changed payload conflicts, and a consumed challenge cannot be reused with a new key. A faculty correction uses the same session lock and produces a separate audit trail. Input body/decoded-image bounds and shared rate buckets constrain abuse.

## 14. Testing and validation

The project includes unit, database integration, client interaction, browser and real-model smoke tests. PostgreSQL-backed tests run the migration and verify role restrictions, CRUD, refresh replay, device mismatch/revocation, consent, session expiry, duplicates and concurrent retries. Rule tests cover location and temporal sequences. Browser tests interact with the actual running API and database. Mobile logic tests check signing interoperability and decision wording; Metro/Hermes export checks bundle construction.

The API happy-path tests explicitly replace vision to isolate transaction behavior. Real-model tests separately compare public portraits and reject zero/multiple faces. Neither proves full live-phone verification. Current commands, counts and outcomes are included from `TEST_RESULTS.md` in the generated report. Failed intermediate runs were investigated and are not represented as passing results.

## 15. Actual results

The source contains functional backend, dashboard and student app implementations rather than generated placeholders. Authentication, academic configuration, sessions, reports and audits have been exercised against PostgreSQL. Real pretrained face-model inference has been executed. Verification state handling is connected to the API and constrained database writes. The dashboard builds and browser workflows connect to actual endpoints; mobile logic and bundle checks are recorded separately.

The final result table is generated from executed test result files. No population biometric accuracy, real-device liveness success rate, production latency, enrollment count or deployment adoption is reported because those studies were not performed. Native build status, remaining upstream dependency advisories and provider limitations appear in the verification appendix.

## 16. Limitations

The system cannot guarantee presence against compromised clients or coordinated credential sharing. Basic landmark liveness can be attacked, GPS has indoor uncertainty, Wi-Fi is platform-dependent and attestation is unconfigured. Thresholds need institution-specific calibration and a consented evaluation dataset. Access tokens have an expiry window after logout; audit storage is not externally immutable. Large-class performance, retention automation, key rotation and fully managed production deployment require further engineering.

The current Expo dependency tree has unresolved upstream advisories recorded in the limitations appendix. These must remain visible in a college evaluation and future release decision. Real-device and Apple Silicon checks remain separate from cloud test results.

## 17. Future enhancements

Priorities are provider-backed integrity validation, stronger capture provenance/presentation-attack detection, accessible alternative attendance workflows, calibrated thresholds, measured false-accept/false-reject behavior, pagination, operational retention and protected external audit export. Future work should be based on observed weaknesses and institutional requirements. Excluded beacon, ultrasound, surveillance and blockchain hardware/systems are not proposed as hidden dependencies of this implementation.

## 18. Conclusion

SPVS demonstrates how identity and location evidence can be combined with server-side enforcement and attributable review in an actual attendance application. The strongest implemented properties are explicit decision gates, relational consistency, evidence-bound retries and accountable corrections. Its practical value depends on honest handling of uncertainty and measured device behavior rather than an absolute anti-proxy claim.

## 19. References

The full bibliography is in `REFERENCES.md` and is included in the report appendix. It contains official framework, model, operating-system and security documentation plus the actual public test-image sources and relevant unresolved advisories.

## 20. Appendices

The generated PDF appends architecture/ER/sequence diagrams, the API map, biometric and security design, threat model, current test results, requirements traceability and known limitations. Editable source Markdown and the packaging script are included in the ZIP so that the student can add genuine institutional measurements and academic details without rebuilding the software from scratch.


## Cross-platform completion update

This continuation adds native Android Keystore/iOS Secure Enclave P-256 signing, nonce-based device registration, Apple App Attest verification architecture, current-network-only iOS Wi-Fi evidence, precise-location handling and a separate audited iPhone presence policy. Shared enrollment/liveness/session screens continue to use the real backend model pipeline. Automated evidence distinguishes real-model smoke tests from synthetic API/certificate tests, native compilation from JS exports, and unperformed physical-device validation. The appended cross-platform chapter and final verification report are authoritative for release outcomes; no biometric accuracy or provider-backed success has been invented.


Automatic iPhone GPS-only approval additionally requires a verified App Attest assertion, even if the global attestation requirement is off. The registered platform is client-reported; without this gate an unverified client could select a weaker platform policy. With App Attest unavailable/unconfigured, iPhone verification remains review/retry. GPS-only evidence still has lower presence assurance after app verification.
