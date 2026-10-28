# Complete API inventory

Generated from the imported FastAPI application and inspected route dependencies.
All paths below are exact, including `/api/v1`. Swagger is available at `/docs`.
Bearer authentication uses `Authorization: Bearer <access_token>`; staff must also
pass assigned-course scope. Student reads use enrollment/ownership scope.

Response codes below are those declared by OpenAPI, not an exhaustive runtime
error list. Most handlers return dictionaries/ORM projections without response_model;
OpenAPI therefore leaves their response schema unspecified. This is an existing
contract limitation, not a guarantee of empty responses. Follow source links and
the response catalog in [API documentation](API_DOCUMENTATION.md).

| Method and path | Access | JSON request schema; path/query fields | Declared responses | Implementation |
| --- | --- | --- | --- | --- |
| GET `/health` | Public/token exchange | —; — | 200 | [health](../backend/app/main.py#L56) |
| GET `/ready` | Public/token exchange | —; — | 200 | [ready](../backend/app/main.py#L63) |
| POST `/api/v1/auth/register` | Public/token exchange | CreateUser; — | 201, 422 | [register](../backend/app/api/auth.py#L31) |
| POST `/api/v1/auth/login` | Public/token exchange | Login; — | 200, 422 | [login](../backend/app/api/auth.py#L44) |
| POST `/api/v1/auth/refresh` | Public/token exchange | Refresh; — | 200, 422 | [refresh](../backend/app/api/auth.py#L60) |
| POST `/api/v1/auth/logout` | Public/token exchange | Refresh; — | 204, 422 | [logout](../backend/app/api/auth.py#L79) |
| GET `/api/v1/auth/me` | Bearer; role/ownership scoped | —; — | 200 | [me](../backend/app/api/auth.py#L87) |
| GET `/api/v1/courses` | Bearer; role/ownership scoped | —; — | 200 | [courses](../backend/app/api/academic.py#L22) |
| POST `/api/v1/courses` | Admin | CourseInput; — | 201, 422 | [add_course](../backend/app/api/academic.py#L32) |
| GET `/api/v1/courses/{course_id}/enrollments` | Faculty/admin; course scoped | —; course_id (path) | 200, 422 | [enrollments](../backend/app/api/academic.py#L42) |
| POST `/api/v1/courses/{course_id}/enrollments` | Admin | EnrollmentInput; course_id (path) | 201, 422 | [enroll](../backend/app/api/academic.py#L48) |
| DELETE `/api/v1/courses/{course_id}/enrollments/{student_id}` | Admin | —; course_id (path), student_id (path) | 204, 422 | [unenroll](../backend/app/api/academic.py#L59) |
| GET `/api/v1/classrooms` | Faculty/admin; course scoped | —; — | 200 | [classrooms](../backend/app/api/academic.py#L66) |
| POST `/api/v1/classrooms` | Admin | ClassroomInput; — | 201, 422 | [add_classroom](../backend/app/api/academic.py#L87) |
| PUT `/api/v1/classrooms/{room_id}` | Admin | ClassroomInput; room_id (path) | 200, 422 | [update_classroom](../backend/app/api/academic.py#L95) |
| GET `/api/v1/sessions` | Bearer; role/ownership scoped | —; — | 200 | [sessions](../backend/app/api/academic.py#L103) |
| POST `/api/v1/sessions` | Faculty/admin; course scoped | SessionInput; — | 201, 422 | [add_session](../backend/app/api/academic.py#L110) |
| GET `/api/v1/sessions/{session_id}` | Bearer; role/ownership scoped | —; session_id (path) | 200, 422 | [session_detail](../backend/app/api/academic.py#L124) |
| POST `/api/v1/sessions/{session_id}/close` | Faculty/admin; course scoped | —; session_id (path) | 200, 422 | [close_session](../backend/app/api/academic.py#L132) |
| GET `/api/v1/records` | Bearer; role/ownership scoped | —; session_id (query) | 200, 422 | [records](../backend/app/api/academic.py#L153) |
| GET `/api/v1/attempts` | Bearer; role/ownership scoped | —; session_id (query) | 200, 422 | [attempts](../backend/app/api/academic.py#L159) |
| GET `/api/v1/events` | Faculty/admin; course scoped | —; — | 200 | [events](../backend/app/api/academic.py#L165) |
| POST `/api/v1/events/{event_id}/review` | Faculty/admin; course scoped | —; event_id (path) | 200, 422 | [review_event](../backend/app/api/academic.py#L173) |
| GET `/api/v1/corrections` | Faculty/admin; course scoped | —; — | 200 | [corrections](../backend/app/api/academic.py#L209) |
| POST `/api/v1/corrections` | Faculty/admin; course scoped | CorrectionInput; — | 201, 422 | [correct](../backend/app/api/academic.py#L186) |
| GET `/api/v1/disputes` | Bearer; role/ownership scoped | —; — | 200 | [disputes](../backend/app/api/academic.py#L227) |
| POST `/api/v1/disputes` | Student; own data | DisputeInput; — | 201, 422 | [dispute](../backend/app/api/academic.py#L215) |
| POST `/api/v1/disputes/{dispute_id}/resolve` | Faculty/admin; course scoped | Resolve; dispute_id (path) | 200, 422 | [resolve_dispute](../backend/app/api/academic.py#L235) |
| GET `/api/v1/reports/attendance.csv` | Faculty/admin; course scoped | —; session_id (query) | 200, 422 | [export](../backend/app/api/academic.py#L251) |
| GET `/api/v1/overview` | Faculty/admin; course scoped | —; — | 200 | [overview](../backend/app/api/academic.py#L264) |
| GET `/api/v1/users` | Admin | —; — | 200 | [users](../backend/app/api/admin.py#L16) |
| POST `/api/v1/users` | Admin | CreateUser; — | 201, 422 | [add_user](../backend/app/api/admin.py#L21) |
| PATCH `/api/v1/users/{user_id}` | Admin | UserUpdate; user_id (path) | 200, 422 | [disable](../backend/app/api/admin.py#L29) |
| GET `/api/v1/policy` | Bearer; role/ownership scoped | —; — | 200 | [get_policy](../backend/app/api/admin.py#L59) |
| PUT `/api/v1/policy` | Admin | PolicyInput; — | 200, 422 | [set_policy](../backend/app/api/admin.py#L64) |
| GET `/api/v1/device-resets` | Bearer; role/ownership scoped | —; — | 200 | [resets](../backend/app/api/admin.py#L86) |
| POST `/api/v1/device-resets` | Student; own data | Reason; — | 201, 422 | [request_reset](../backend/app/api/admin.py#L75) |
| POST `/api/v1/device-resets/{reset_id}/approve` | Admin | Reason; reset_id (path) | 200, 422 | [approve_reset](../backend/app/api/admin.py#L94) |
| GET `/api/v1/admin/devices` | Admin | —; — | 200 | [device_capabilities](../backend/app/api/admin.py#L107) |
| GET `/api/v1/devices` | Student; own data | —; — | 200 | [devices](../backend/app/api/verification.py#L32) |
| POST `/api/v1/devices` | Student; own data | DeviceInput; — | 201, 422 | [register_device](../backend/app/api/verification.py#L38) |
| GET `/api/v1/biometrics` | Student; own data | —; — | 200 | [biometric_status](../backend/app/api/verification.py#L70) |
| DELETE `/api/v1/biometrics` | Student; own data | Login; — | 204, 422 | [delete_biometrics](../backend/app/api/verification.py#L77) |
| POST `/api/v1/challenges` | Student; own data | ChallengeInput; — | 201, 422 | [challenge](../backend/app/api/verification.py#L97) |
| POST `/api/v1/biometrics/enroll` | Student; own data | SignedEvidence; — | 201, 422 | [enroll_biometrics](../backend/app/api/verification.py#L162) |
| POST `/api/v1/attendance/verify` | Student; own data | SignedEvidence; — | 200, 422 | [verify_attendance](../backend/app/api/verification.py#L197) |
| POST `/api/v1/devices/registration-challenge` | Student; own data | —; — | 201 | [device_registration_challenge](../backend/app/api/verification.py#L298) |
| GET `/api/v1/attestation/capabilities` | Student; own data | —; — | 200 | [attestation_capabilities](../backend/app/api/verification.py#L304) |
| POST `/api/v1/attestation/challenge` | Student; own data | AttestationChallengeInput; — | 201, 422 | [attestation_challenge](../backend/app/api/verification.py#L310) |
| POST `/api/v1/attestation/register` | Student; own data | AttestationRegistration; — | 201, 422 | [register_attestation](../backend/app/api/verification.py#L320) |
| POST `/api/v1/sessions/{sid}/presence/control` | Faculty/admin; course scoped | Controls; sid (path) | 200, 422 | [control](../backend/app/api/classroom_presence.py#L69) |
| GET `/api/v1/sessions/{sid}/presence/display` | Faculty/admin; course scoped | —; sid (path) | 200, 422 | [display](../backend/app/api/classroom_presence.py#L83) |
| POST `/api/v1/sessions/{sid}/presence/play/{attempt_id}` | Faculty/admin; course scoped | —; sid (path), attempt_id (path) | 200, 422 | [play](../backend/app/api/classroom_presence.py#L110) |
| POST `/api/v1/presence/evidence` | Student; own data | SignedEvidence; — | 200, 422 | [redeem](../backend/app/api/classroom_presence.py#L163) |

## Request structures

### AttestationChallengeInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `device_id` | yes | `{"type": "string"}` |

### AttestationRegistration

| Field | Required | Type / constraints |
| --- | --- | --- |
| `device_id` | yes | `{"type": "string"}` |
| `challenge_id` | yes | `{"type": "string"}` |
| `key_id` | yes | `{"type": "string", "maxLength": 100, "minLength": 40}` |
| `attestation` | yes | `{"type": "string", "maxLength": 30000, "minLength": 100}` |

### ChallengeInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `device_id` | yes | `{"type": "string"}` |
| `purpose` | yes | `{"type": "string", "enum": ["attendance", "enrollment"]}` |
| `session_id` | no | `{"anyOf": [{"type": "string"}, {"type": "null"}]}` |

### ClassroomInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `name` | yes | `{"type": "string", "maxLength": 100, "minLength": 2}` |
| `latitude` | yes | `{"type": "number", "maximum": 90.0, "minimum": -90.0}` |
| `longitude` | yes | `{"type": "number", "maximum": 180.0, "minimum": -180.0}` |
| `radius_m` | yes | `{"type": "number", "maximum": 300.0, "minimum": 5.0}` |
| `wifi` | no | `{"items": {"$ref": "#/components/schemas/WifiInput"}, "type": "array", "maxItems": 50}` |

### Controls

| Field | Required | Type / constraints |
| --- | --- | --- |
| `enabled` | yes | `{"type": "boolean"}` |

### CorrectionInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `reason` | yes | `{"type": "string", "maxLength": 1000, "minLength": 10}` |
| `student_id` | yes | `{"type": "string"}` |
| `session_id` | yes | `{"type": "string"}` |
| `status` | yes | `{"type": "string", "enum": ["PRESENT", "ABSENT", "EXCUSED"]}` |

### CourseInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `code` | yes | `{"type": "string", "maxLength": 30, "minLength": 2}` |
| `name` | yes | `{"type": "string", "maxLength": 160, "minLength": 2}` |
| `faculty_id` | yes | `{"type": "string"}` |

### CreateUser

| Field | Required | Type / constraints |
| --- | --- | --- |
| `email` | yes | `{"type": "string", "format": "email"}` |
| `name` | yes | `{"type": "string", "maxLength": 120, "minLength": 2}` |
| `password` | yes | `{"type": "string", "maxLength": 128, "minLength": 12}` |
| `role` | no | `{"type": "string", "enum": ["student", "faculty", "admin"], "default": "student"}` |
| `roll_number` | no | `{"anyOf": [{"type": "string", "maxLength": 40, "minLength": 2}, {"type": "null"}]}` |

### DeviceInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `label` | yes | `{"type": "string", "maxLength": 100, "minLength": 2}` |
| `platform` | yes | `{"type": "string", "enum": ["android", "ios"]}` |
| `password` | yes | `{"type": "string", "maxLength": 128, "minLength": 1}` |
| `public_key` | no | `{"anyOf": [{"type": "string", "maxLength": 200}, {"type": "null"}]}` |
| `registration_challenge_id` | no | `{"anyOf": [{"type": "string"}, {"type": "null"}]}` |
| `registration_signature` | no | `{"anyOf": [{"type": "string", "maxLength": 200}, {"type": "null"}]}` |
| `key_storage` | no | `{"type": "string", "enum": ["secure-enclave", "keychain", "android-keystore", "android-hardware"], "default": "keychain"}` |

### DisputeInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `reason` | yes | `{"type": "string", "maxLength": 1000, "minLength": 10}` |
| `attempt_id` | yes | `{"type": "string"}` |

### EnrollmentInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `student_id` | yes | `{"type": "string"}` |

### Login

| Field | Required | Type / constraints |
| --- | --- | --- |
| `email` | yes | `{"type": "string", "format": "email"}` |
| `password` | yes | `{"type": "string", "maxLength": 128, "minLength": 1}` |

### PolicyInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `max_accuracy_m` | no | `{"type": "number", "maximum": 100.0, "minimum": 5.0, "default": 35}` |
| `max_location_age_s` | no | `{"type": "integer", "maximum": 60.0, "minimum": 5.0, "default": 20}` |
| `wifi_unavailable` | no | `{"type": "string", "enum": ["review", "gps_only", "reject"], "default": "review"}` |
| `ios_presence` | no | `{"type": "string", "enum": ["review", "retry", "gps_only", "dynamic"], "default": "dynamic"}` |
| `require_attestation` | no | `{"type": "boolean", "default": false}` |
| `max_attempts` | no | `{"type": "integer", "maximum": 10.0, "minimum": 1.0, "default": 5}` |
| `reason` | yes | `{"type": "string", "maxLength": 1000, "minLength": 10}` |

### Reason

| Field | Required | Type / constraints |
| --- | --- | --- |
| `reason` | yes | `{"type": "string", "maxLength": 1000, "minLength": 10}` |

### Refresh

| Field | Required | Type / constraints |
| --- | --- | --- |
| `refresh_token` | yes | `{"type": "string", "maxLength": 200, "minLength": 32}` |

### Resolve

| Field | Required | Type / constraints |
| --- | --- | --- |
| `resolution` | yes | `{"type": "string", "maxLength": 1000, "minLength": 10}` |

### SessionInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `course_id` | yes | `{"type": "string"}` |
| `classroom_id` | yes | `{"type": "string"}` |
| `starts_at` | yes | `{"type": "string", "format": "date-time"}` |
| `ends_at` | yes | `{"type": "string", "format": "date-time"}` |

### SignedEvidence

| Field | Required | Type / constraints |
| --- | --- | --- |
| `payload` | yes | `{"type": "string", "maxLength": 14100000, "minLength": 100}` |
| `signature` | yes | `{"type": "string", "maxLength": 200, "minLength": 40, "pattern": "^[a-zA-Z0-9+/=]+$"}` |
| `idempotency_key` | yes | `{"type": "string", "pattern": "^[a-zA-Z0-9_-]{16,64}$"}` |
| `attestation_key_id` | no | `{"anyOf": [{"type": "string", "maxLength": 100}, {"type": "null"}]}` |
| `attestation_assertion` | no | `{"anyOf": [{"type": "string", "maxLength": 10000}, {"type": "null"}]}` |

### UserUpdate

| Field | Required | Type / constraints |
| --- | --- | --- |
| `active` | no | `{"anyOf": [{"type": "boolean"}, {"type": "null"}]}` |
| `role` | no | `{"anyOf": [{"type": "string", "enum": ["student", "faculty", "admin"]}, {"type": "null"}]}` |
| `roll_number` | no | `{"anyOf": [{"type": "string", "maxLength": 40, "minLength": 2}, {"type": "null"}]}` |
| `reason` | no | `{"anyOf": [{"type": "string", "maxLength": 1000, "minLength": 10}, {"type": "null"}]}` |

### WifiInput

| Field | Required | Type / constraints |
| --- | --- | --- |
| `bssid` | yes | `{"type": "string", "pattern": "^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$"}` |
| `min_rssi` | no | `{"type": "integer", "maximum": -20.0, "minimum": -100.0, "default": -80}` |
