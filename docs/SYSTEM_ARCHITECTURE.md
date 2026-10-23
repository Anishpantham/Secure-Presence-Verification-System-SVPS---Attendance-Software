# System architecture

## Component architecture

```mermaid
flowchart LR
  Student[Student Android / iOS app] -->|JWT + signed evidence| API[FastAPI /api/v1]
  Staff[Faculty / Admin React dashboard] -->|JWT + scoped requests| API
  API --> Auth[Authentication and authorization]
  API --> Identity[Layer 1: identity]
  Identity --> YuNet[YuNet face detection]
  YuNet --> SFace[SFace 128D embedding]
  Identity --> Mesh[MediaPipe temporal landmarks]
  Identity --> Device[P-256 device signature verification]
  API --> Presence[Layer 2: physical presence]
  Presence --> GPS[GPS uncertainty and geofence]
  Presence --> WiFi[Wi-Fi fingerprint policy]
  Identity --> Decision[Deterministic decision]
  Presence --> Decision
  Decision --> DB[(PostgreSQL)]
  DB --> Audit[Records, attempts and audit events]
```

The backend uses synchronous SQLAlchemy sessions in FastAPI synchronous route handlers, which execute in the framework's thread pool. This is deliberate: OpenCV/MediaPipe inference is synchronous and guarded by a process-local model lock. The application does not block an async endpoint with a synchronous database call. Multiple API workers share PostgreSQL rate limits and locks; each worker has its own model memory. Capacity and fair scheduling require load testing before institutional deployment.

The dashboard uses a same-origin `/api` route through Vite in development or nginx in containers. Tokens remain in dashboard memory. The mobile app stores tokens and per-user key metadata in SecureStore; new private keys stay in native Keystore/Secure Enclave storage. Its camera cache files are deleted after conversion; no raw frames are saved by the backend.

## Verification sequence

```mermaid
sequenceDiagram
  participant M as Student app
  participant A as API
  participant D as PostgreSQL
  participant V as Vision pipeline
  M->>A: Request challenge (JWT, device, session)
  A->>D: Check enrollment, device, session, attempt limit
  A-->>M: Random actions, challenge ID, expiry, server clock
  M->>M: Capture frames, GPS and available Wi-Fi
  M->>M: ECDSA(idempotency key + exact JSON payload)
  M->>A: Submit signed evidence
  A->>D: Lock student, challenge and session
  A->>A: Validate signature, purpose, ownership, replay and time
  A->>V: Detect, embed, compare, validate landmark sequence
  V-->>A: Match and temporal outcome or failure
  A->>A: Evaluate GPS/Wi-Fi and explainable rules
  A->>D: Consume challenge, store attempt and optional record atomically
  A-->>M: Structured decision and reasons
```

## Decision flow

```mermaid
flowchart TD
  Request[Authenticated signed request] --> Retry{Same idempotency key?}
  Retry -->|Same payload| Existing[Return existing attempt]
  Retry -->|Different payload| Conflict[409 conflict]
  Retry -->|New key| Gates{Enrollment / session / challenge / device valid?}
  Gates -->|No| Stop[Reject or expire; no new present record]
  Gates -->|Yes| Face{Face and temporal liveness pass?}
  Face -->|No| Reject[REJECTED]
  Face -->|Yes| Location{Fresh, accurate, non-mock GPS?}
  Location -->|Stale / inaccurate| Again[REQUIRES_RETRY]
  Location -->|Mock / clearly outside| Reject
  Location -->|Valid| Signals{Boundary, Wi-Fi, travel, attestation}
  Signals -->|Uncertainty| Review[PENDING_REVIEW]
  Signals -->|Required signals pass| Present[PRESENT + unique record]
```

Authentication, malformed payload and signature failures are HTTP errors; signed, attributable verification outcomes are persisted as attempts. This distinction prevents unauthenticated requests from inventing someone else's attempt history.


## Cross-platform completion update

Native device keys now live in `spvs-security` (Kotlin/Swift), with shared TypeScript adapters. App Attest registration uses dedicated one-use security challenges; assertions bind the exact signed request and advance a PostgreSQL counter. iOS current-network evidence is separate from Android scan measurements. See CROSS_PLATFORM_IMPLEMENTATION.md for trust boundaries and native-build limits.
