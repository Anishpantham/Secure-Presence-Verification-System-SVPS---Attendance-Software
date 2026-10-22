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

`POST /attendance/verify` and `/biometrics/enroll` accept three fields:

```json
{
  "payload": "<exact serialized Evidence JSON string>",
  "signature": "<64 lowercase hexadecimal HMAC-SHA256 characters>",
  "idempotency_key": "<16 to 64 characters: letters, digits, hyphens or underscores>"
}
```

HMAC uses the UTF-8 device credential string as key and the bytes of `idempotency_key + "." + payload`. The inner `Evidence` schema has challenge/device IDs, 8–40 timestamped JPEG frames, consent, optional location, real Wi-Fi observations/status and optional integrity token. Coordinates, accuracy and timestamp are measurements; no `distance`, `inside_geofence`, `similarity` or `liveness_passed` field is accepted as proof. Clients should keep the same exact signed request and key after a network timeout to recover the original attendance decision.

Enrollment and attendance purposes are not interchangeable. An enrollment challenge cannot reference a session; an attendance challenge must bind an active, enrolled session and an existing biometric profile. Enrollment currently returns a conflict after a successful enrollment replay rather than supporting durable enrollment idempotency; the client can query `/biometrics` to resolve an uncertain enrollment response.

## Outcomes and errors

An attributable attendance attempt contains `id`, `state`, `reasons`, `risk_score` and `evidence_summary`. `PRESENT` creates one official record. `PENDING_REVIEW`, `REQUIRES_RETRY`, `REJECTED` and `EXPIRED` do not create a present record. Faculty may create an explicitly sourced correction later.

HTTP errors use `{"error":{"code":403,"message":"..."}}`. Validation responses include field locations without echoing sensitive input. Typical codes are 401 authentication failure, 403 role/device/signature denial, 404 missing resource, 409 conflict/replay, 413 body limit, 422 invalid evidence, 429 rate limit and 503 missing verification service/models. Never treat an HTTP failure as an attendance approval.

Most operational lists expose the latest 500 rows; course and enrollment lists are not paginated. CSV export includes all records in the authorized selection. Large institutions need cursor pagination, query optimization and retention jobs before deployment.
