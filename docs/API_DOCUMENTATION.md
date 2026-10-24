# API documentation

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

Most operational lists expose the latest 500 rows; course and enrollment lists are not paginated. CSV export includes all records in the authorized selection. Large institutions need cursor pagination, query optimization and retention jobs before deployment.


## Cross-platform completion update

`POST /devices/registration-challenge` issues a one-use nonce. `POST /devices` accepts public_key (base64 canonical P-256 SPKI), registration_challenge_id, registration_signature and reported key_storage in addition to password/label/platform. New registrations do not return a shared secret. See CROSS_PLATFORM_IMPLEMENTATION.md for exact signing bytes. `GET /attestation/capabilities`, `POST /attestation/challenge`, and `POST /attestation/register` implement the App Attest boundary. Signed requests may contain outer attestation_key_id and attestation_assertion; the assertion covers the exact idempotency/payload bytes. Evidence adds accuracy_authorization, wifi_source and current_bssid. `PUT /policy` accepts ios_presence=review|retry|gps_only with an audit reason. `GET /admin/devices` is administrator-only and explicitly labels reported storage versus verified app registration. The regenerated openapi.json is the field-level contract.
