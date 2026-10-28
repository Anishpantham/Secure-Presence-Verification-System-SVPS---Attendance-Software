# API documentation

## Policy-v2 classroom presence endpoints

The current schema includes staff-scoped
`POST /sessions/{sid}/presence/control`, `GET /sessions/{sid}/presence/display`,
and `POST /sessions/{sid}/presence/play/{attempt_id}`. Students submit signed
`qr`, `ready`, `audio` or `failure` messages through `POST /presence/evidence`.
Complete QR/audio proof is mandatory for new automatic attendance; declared
capture failure produces a review attempt with identity NOT_COMPLETED.

Attendance challenges use a 120-second lifetime; enrollment retains its configured
lifetime. Existing unconsumed attendance challenges may be reused, and the attempt
budget counts issued challenges. Five-second QR rotation, at most ten-second QR
validity, a server-clock five-second acoustic deadline, nonce binding, consumption
and idempotency are described in [the protocol](ACOUSTIC_DYNAMIC_QR.md).
Use `docs/openapi.json` for field-level contracts. Enrollment and previous records
are not retroactively changed by migration `9bd32a88f101`.

The authoritative machine-readable contract is `docs/openapi.json`, exported from the implemented application, and the live `/openapi.json`. The versioned API prefix is `/api/v1`. Protected operations use `Authorization: Bearer <access token>`.

## Endpoint groups

| Group | Main routes | Authorization |
|---|---|---|
| Authentication | POST `/auth/login`, `/auth/refresh`, `/auth/logout`; GET `/auth/me` | Public token exchange; authenticated profile |
| Registration | POST `/auth/register` | Disabled by default; student-only when enabled |
| Accounts | GET/POST `/users`; PATCH `/users/{id}` | Administrator |
| Academics | GET/POST `/courses`; GET/POST/DELETE enrollment routes | Course-scoped reads; administrator writes |
| Classrooms | GET/POST `/classrooms`; PUT `/classrooms/{id}` | Staff read; administrator write |
| Sessions | GET/POST `/sessions`; GET `/{id}`; POST `/{id}/close` | Enrolled student read; assigned faculty/admin manage |
| Biometrics | GET/DELETE `/biometrics`; POST `/biometrics/enroll` | Student's own template |
| Device | GET/POST `/devices`; reset request/list/approval routes | Student ownership; admin reset approval |
| Evidence | POST `/challenges`, `/attendance/verify` | Authenticated student and active bound device |
| Review | GET/POST `/disputes`; POST `/{id}/resolve`; GET/POST `/corrections` | Student ownership; scoped staff decisions |
| Audit | GET `/events`; POST `/{id}/review` | Scoped faculty or administrator |
| Records | GET `/attempts`, `/records` | Student own data or scoped staff data |
| Reporting | GET `/overview`, `/reports/attendance.csv` | Scoped staff |
| Policy | GET/PUT `/policy` | Authenticated read; administrator write with reason |

## Signing protocol

`POST /attendance/verify` and `/biometrics/enroll` accept the three required fields below and optional App Attest assertion/key fields:

```json
{
  "payload": "<exact serialized Evidence JSON string>",
  "signature": "<base64 DER ECDSA/SHA-256 signature>",
  "idempotency_key": "<16 to 64 characters: letters, digits, hyphens or underscores>"
}
```

P-256 ECDSA/SHA-256 signs the bytes of `idempotency_key + "." + payload`; the server verifies with the registered public key. Legacy devices retain the original hexadecimal HMAC protocol during migration. The inner `Evidence` schema has challenge/device IDs, 8–40 timestamped JPEG frames, consent, optional location, real Wi-Fi observations/status and optional integrity token. Coordinates, accuracy and timestamp are measurements; no `distance`, `inside_geofence`, `similarity` or `liveness_passed` field is accepted as proof. Clients should keep the same exact signed request and key after a network timeout to recover the original attendance decision.

Enrollment and attendance purposes are not interchangeable. An enrollment challenge cannot reference a session; an attendance challenge must bind an active, enrolled session and an existing biometric profile. An exact authenticated enrollment retry returns the recorded success while the profile exists; a different request cannot reuse a consumed enrollment challenge. The client can also query `/biometrics` for current status.

## Outcomes and errors

An attributable attendance attempt contains `id`, `state`, `reasons`, `risk_score` and `evidence_summary`. `PRESENT` creates one official record. `PENDING_REVIEW`, `REQUIRES_RETRY`, `REJECTED` and `EXPIRED` do not create a present record. Faculty may create an explicitly sourced correction later.

HTTP errors use `{"error":{"code":403,"message":"..."}}`. Validation responses include field locations without echoing sensitive input. Typical codes are 401 authentication failure, 403 role/device/signature denial, 404 missing resource, 409 conflict/replay, 413 body limit, 422 invalid evidence, 429 rate limit and 503 missing verification service/models. Never treat an HTTP failure as an attendance approval.

Enrollment vision failures additionally return optional `error.details` with
allowlisted stage/count fields: `completed_actions`, `expected_action`,
`frame_count`, `missing_landmark_frames`, and `frame_index`. No image, landmark
coordinate or embedding is returned. The client uses these fields for targeted
retry instructions. Rate-limit `Retry-After` reports the remaining bucket window.
Definitive 4xx rejections discard the saved request; network/5xx failures can
retain the same signed submission for idempotent recovery.

The mobile sign-in client now translates `body.email` and `body.password`
validation fields into specific guidance and rejects embedded email whitespace
before submission. The server's validation envelope is unchanged; no password
values are echoed. HTTP 401 authentication failures remain distinct from format
errors.

Review lifecycle: creating a student dispute does not update attendance.
`POST /corrections` creates/updates an official record with source CORRECTION and
an attributable reason/audit entry. `POST /disputes/{id}/resolve` closes the dispute
but does not create an attendance record by itself. The original attempt decision
is retained after both operations.

Most operational lists expose the latest 500 rows; course and enrollment lists are not paginated. CSV export includes all records in the authorized selection. Large institutions need cursor pagination, query optimization and retention jobs before deployment.


## Cross-platform completion update

`POST /devices/registration-challenge` issues a one-use nonce. `POST /devices` accepts public_key (base64 canonical P-256 SPKI), registration_challenge_id, registration_signature and reported key_storage in addition to password/label/platform. New registrations do not return a shared secret. See CROSS_PLATFORM_IMPLEMENTATION.md for exact signing bytes. `GET /attestation/capabilities`, `POST /attestation/challenge`, and `POST /attestation/register` implement the App Attest boundary. Signed requests may contain outer attestation_key_id and attestation_assertion; the assertion covers the exact idempotency/payload bytes. Evidence adds accuracy_authorization, wifi_source and current_bssid. `PUT /policy` accepts ios_presence=review|retry|dynamic with an audit reason. `GET /admin/devices` is administrator-only and explicitly labels reported storage versus verified app registration. The regenerated openapi.json is the field-level contract.

## Complete endpoint and request reference

The [generated inventory](API_ENDPOINT_INVENTORY.md) lists all 54 operations,
exact paths/methods, role requirements, request schemas, fields and declared codes.
The regenerated [OpenAPI JSON](openapi.json) is exported from the current app.
Runtime 401/403/404/409/413/422/429/503 errors are not all declared per operation;
most success responses lack explicit response_model typing. This is a documented
contract gap. Do not interpret an empty OpenAPI response schema as an empty body.

### Implemented response structures

- Login: access_token, refresh_token, token_type, expires_in and public user;
  refresh returns the four token fields; logout is HTTP 204.
- Academic/account/policy/device lists: arrays of public model projections, with
  current-user/course scope. Detail/create/update returns the public object.
  The [table inventory](DATABASE_TABLE_INVENTORY.md) defines the column fields;
  public() excludes password_hash, secret_encrypted, template_encrypted, token_hash
  and request_hash. Endpoint-specific additions/exclusions are in linked handlers.
- Challenge: public challenge plus server_time and capture_guide. Purpose/session
  bindings are mandatory; attendance expires in 120 seconds.
- Enrollment: enrolled, model and raw_images_retained=false. Biometric status:
  enrolled, model and consent_at. Deletion/enrollment require password/consent as applicable.
- Attendance: public attempt including id, state, reasons, risk_score and
  evidence_summary. PRESENT alone inserts an automatic attendance record.
- Presence control: enabled. Display: enabled, server_time, ends_at and queue,
  with token/rotate_at/expires_at only while active. Queue entries have attempt_id/label.
- Playback: payload, server_time, expires_at, duration_ms and codec; staff-scoped.
- Presence evidence: attempt_id and QR/audio status (idempotent replies may include
  fewer fields); capture failure returns a public review attempt, identity NOT_COMPLETED.
- Device registration adds storage and, only for enabled legacy mode, credential.
  Device lists add app_attest_registered; admin capabilities exclude public_key
  and explicitly return hardware_storage_verified=false.
- CSV reporting returns a scoped attachment; deletion operations return HTTP 204.
- Health: status/database. Ready: status/face_models/attestation. Its attestation
  field is a static not_configured label; use authenticated capabilities for provider
  configuration and a verified assertion for actual per-attempt integrity.

Success projections and optional fields should be consumed defensively. New typed
response models across the whole API would be a separate compatibility-reviewed change.
