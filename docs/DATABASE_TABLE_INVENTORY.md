# Database table inventory

Generated from SQLAlchemy metadata; includes columns and actual foreign keys.
Current schema has **24 application tables**, plus `alembic_version`.
Unique/check/index details remain authoritative in models and migrations.

## classrooms

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `name` | VARCHAR(100) | False |  |
| `latitude` | FLOAT | False |  |
| `longitude` | FLOAT | False |  |
| `radius_m` | FLOAT | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## policies

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `id` | INTEGER | False | PK  |
| `max_accuracy_m` | FLOAT | False |  |
| `max_location_age_s` | INTEGER | False |  |
| `wifi_unavailable` | VARCHAR(16) | False |  |
| `ios_presence` | VARCHAR(24) | False |  |
| `require_attestation` | BOOLEAN | False |  |
| `max_attempts` | INTEGER | False |  |

## rate_buckets

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `key` | VARCHAR(128) | False | PK  |
| `window_at` | DATETIME | False |  |
| `count` | INTEGER | False |  |

## users

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `email` | VARCHAR(254) | False |  |
| `name` | VARCHAR(120) | False |  |
| `password_hash` | TEXT | False |  |
| `role` | VARCHAR(16) | False |  |
| `active` | BOOLEAN | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## faculty

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `user_id` | VARCHAR(36) | False | PK users.id |
| `department` | VARCHAR(100) | False |  |

## refresh_tokens

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `user_id` | VARCHAR(36) | False | users.id |
| `token_hash` | VARCHAR(64) | False |  |
| `family` | VARCHAR(36) | False |  |
| `expires_at` | DATETIME | False |  |
| `used` | BOOLEAN | False |  |
| `revoked` | BOOLEAN | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## students

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `user_id` | VARCHAR(36) | False | PK users.id |
| `roll_number` | VARCHAR(40) | False |  |

## wifi_references

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `classroom_id` | VARCHAR(36) | False | classrooms.id |
| `bssid` | VARCHAR(17) | False |  |
| `min_rssi` | INTEGER | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## biometric_profiles

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `student_id` | VARCHAR(36) | False | PK students.user_id |
| `template_encrypted` | BLOB | False |  |
| `model_version` | VARCHAR(100) | False |  |
| `consent_at` | DATETIME | False |  |

## courses

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `code` | VARCHAR(30) | False |  |
| `name` | VARCHAR(160) | False |  |
| `faculty_id` | VARCHAR(36) | False | faculty.user_id |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## device_resets

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `student_id` | VARCHAR(36) | False | students.user_id |
| `reason` | TEXT | False |  |
| `status` | VARCHAR(16) | False |  |
| `reviewed_by` | VARCHAR(36) | True | users.id |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## devices

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `student_id` | VARCHAR(36) | False | students.user_id |
| `label` | VARCHAR(100) | False |  |
| `platform` | VARCHAR(16) | False |  |
| `secret_encrypted` | BLOB | False |  |
| `key_algorithm` | VARCHAR(24) | False |  |
| `public_key` | TEXT | True |  |
| `key_storage` | VARCHAR(40) | False |  |
| `active` | BOOLEAN | False |  |
| `revoked_at` | DATETIME | True |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## app_attest_keys

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `key_id` | VARCHAR(100) | False | PK  |
| `device_id` | VARCHAR(36) | False | devices.id |
| `public_key` | BLOB | False |  |
| `counter` | BIGINT | False |  |
| `environment` | VARCHAR(16) | False |  |
| `created_at` | DATETIME | False |  |

## attendance_sessions

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `course_id` | VARCHAR(36) | False | courses.id |
| `classroom_id` | VARCHAR(36) | False | classrooms.id |
| `starts_at` | DATETIME | False |  |
| `ends_at` | DATETIME | False |  |
| `closed` | BOOLEAN | False |  |
| `presence_enabled` | BOOLEAN | False |  |
| `presence_epoch` | INTEGER | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## enrollments

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `course_id` | VARCHAR(36) | False | PK courses.id |
| `student_id` | VARCHAR(36) | False | PK students.user_id |

## security_challenges

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `student_id` | VARCHAR(36) | False | students.user_id |
| `device_id` | VARCHAR(36) | True | devices.id |
| `purpose` | VARCHAR(24) | False |  |
| `nonce` | VARCHAR(64) | False |  |
| `expires_at` | DATETIME | False |  |
| `used` | BOOLEAN | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## challenges

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `student_id` | VARCHAR(36) | False | students.user_id |
| `device_id` | VARCHAR(36) | False | devices.id |
| `session_id` | VARCHAR(36) | True | attendance_sessions.id |
| `purpose` | VARCHAR(16) | False |  |
| `actions` | JSON | False |  |
| `enrollment_request_hash` | VARCHAR(64) | True |  |
| `expires_at` | DATETIME | False |  |
| `used` | BOOLEAN | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## presence_qr

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `session_id` | VARCHAR(36) | False | attendance_sessions.id |
| `classroom_id` | VARCHAR(36) | False | classrooms.id |
| `epoch` | INTEGER | False |  |
| `token` | VARCHAR(300) | False |  |
| `expires_at` | DATETIME | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## security_events

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `actor_id` | VARCHAR(36) | True | users.id |
| `session_id` | VARCHAR(36) | True | attendance_sessions.id |
| `kind` | VARCHAR(64) | False |  |
| `severity` | VARCHAR(16) | False |  |
| `details` | JSON | False |  |
| `reviewed` | BOOLEAN | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## attendance_attempts

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `student_id` | VARCHAR(36) | False | students.user_id |
| `session_id` | VARCHAR(36) | False | attendance_sessions.id |
| `challenge_id` | VARCHAR(36) | False | challenges.id |
| `idempotency_key` | VARCHAR(64) | False |  |
| `request_hash` | VARCHAR(64) | False |  |
| `state` | VARCHAR(24) | False |  |
| `reasons` | JSON | False |  |
| `risk_score` | INTEGER | False |  |
| `evidence_summary` | JSON | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## presence_proofs

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `challenge_id` | VARCHAR(36) | False | PK challenges.id |
| `student_id` | VARCHAR(36) | False | students.user_id |
| `qr_id` | VARCHAR(36) | False | presence_qr.id |
| `qr_verified_at` | DATETIME | False |  |
| `ready_at` | DATETIME | True |  |
| `audio_hash` | VARCHAR(64) | True |  |
| `audio_started_at` | DATETIME | True |  |
| `audio_expires_at` | DATETIME | True |  |
| `audio_verified_at` | DATETIME | True |  |
| `audio_consumed` | BOOLEAN | False |  |
| `audio_request_hash` | VARCHAR(64) | True |  |

## attendance_records

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `student_id` | VARCHAR(36) | False | students.user_id |
| `session_id` | VARCHAR(36) | False | attendance_sessions.id |
| `attempt_id` | VARCHAR(36) | True | attendance_attempts.id |
| `status` | VARCHAR(24) | False |  |
| `source` | VARCHAR(16) | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## disputes

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `student_id` | VARCHAR(36) | False | students.user_id |
| `attempt_id` | VARCHAR(36) | False | attendance_attempts.id |
| `reason` | TEXT | False |  |
| `status` | VARCHAR(16) | False |  |
| `resolution` | TEXT | True |  |
| `reviewed_by` | VARCHAR(36) | True | users.id |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |

## corrections

| Column | SQL type | Nullable | Key/reference |
| --- | --- | --- | --- |
| `record_id` | VARCHAR(36) | False | attendance_records.id |
| `actor_id` | VARCHAR(36) | False | users.id |
| `reason` | TEXT | False |  |
| `previous_status` | VARCHAR(24) | False |  |
| `new_status` | VARCHAR(24) | False |  |
| `id` | VARCHAR(36) | False | PK  |
| `created_at` | DATETIME | False |  |
