# Dynamic QR + acoustic attendance (policy v2)

This feature adds two mandatory presence factors to the existing identity, randomized
liveness, registered-device signature, GPS, review, dispute and audit workflows.
It reduces reliance on iOS Wi-Fi capabilities. It does **not** prove proximity:
QR screenshots, recordings and live relays can carry valid challenges off-site.

## Protocol and authority

1. The student selects a session and obtains `/challenges` with purpose attendance.
   The existing challenge UUID is the coordinated attempt ID throughout QR, audio,
   face capture and the final signed `/attendance/verify` request. It lasts 120 seconds.
   One unused, unexpired challenge per student/session is reused on interrupted requests.
   Issuance is bounded by the configured `max_attempts`, including abandoned attempts.
2. Authorized course faculty starts challenges. `/presence/display` produces a
   cryptographically random QR token on each five-second server clock boundary.
   The token has no student data; its HMAC binds its random ID/nonce to the persisted
   session, room and display epoch. Each challenge is valid for at most ten seconds;
   equality with expiry is rejected. The dashboard polls and hides stale codes.
3. The phone signs a QR redemption using its existing registered key. The server
   authenticates the student, device, enrollment, active session and token. A shared
   classroom QR may be redeemed by many students, but only once per student across
   attempts. Retrying the same bound attempt returns the previous acknowledgement.
4. After permission, the phone starts foreground microphone capture **before** sending
   signed `ready`. Faculty sees only waiting attempt labels and presses Play.
   The server issues one fresh answer for that attempt; only authorized faculty
   receives it over the API. Student-accessible responses never reveal it.
5. The laptop plays a 2.7-second signal. The phone decodes locally, ignores other
   attempt tags, and sends the decoded value in a device-signed message immediately.
   No caller-supplied pass flag is accepted. Wrong or expired answers burn the
   challenge. A correct response is persisted, and exact response retries return
   the same result without consuming another challenge.
6. Face/liveness, fresh GPS, available Wi-Fi and device proof use the existing flow.
   The final transaction checks all mandatory factors before creating a record.
   The immutable attempt retains reasons and the policy version; ordinary faculty
   correction/dispute workflows remain available and never rewrite the original decision.

## Timing and concurrency

The acoustic five-second deadline starts when the server issues the faculty play
response, **before network transit or browser scheduling**. It includes faculty
response latency, playback startup, 2.7 s transmission, phone processing/signing and
return transit. Approximately 2.3 s remain for those other operations. The dashboard
refuses to begin playback if its issuance round trip exceeds 1.2 s. There is no
client-clock grace period or deadline extension; slow networks require a fresh attempt
or review. Phone capture waits at most 28 s for faculty, native capture at most 30 s;
waiting does not start the acoustic deadline. HTTP requests time out after 20 s.

Database transactions lock student → device → liveness challenge → session → proof.
Faculty operations lock session then proof and never acquire student/challenge locks.
Final verification and corrections share the session lock. QR issuance is serialized
by that same lock, so multiple faculty tabs share one QR for the current interval.
Unique `(qr_id, student_id)` and existing attendance/idempotency constraints provide
additional replay/duplicate protection. The server clock is read after lock acquisition.
Rate buckets are shared PostgreSQL records, not per-process counters.

Stopping/restarting challenges advances a display epoch and invalidates all previously
bound proofs for unfinished attempts. Closing/expiring a session prevents acceptance
at every stage. It does not erase historical records. Audio is serialized per session
with a five-second channel reservation: maximum 12 individual playbacks/minute.
This first implementation intentionally exposes that capacity limit; large classes
need staggered students, longer sessions or a separately designed batch protocol.
A waiting student should only tap Listen when faculty can play within 28 seconds.

## Audible codec and phone capture

`mobile/src/acousticCodec.ts` is used by both the dashboard and student app:

- 16-FSK carriers: 1,200 Hz + 160 Hz × symbol (through 3,600 Hz).
- 75 ms symbols, an eight-symbol synchronization preamble, then a 12-byte message
  (32-bit public attempt routing tag + 64 unpredictable bits) and CRC16-CCITT.
- 36 symbols total: 2.7 seconds, with short amplitude ramps at symbol edges.
- Goertzel energy comparison on symbol centers; timing-offset search, carrier
  dominance threshold and checksum reject ambiguous/corrupt captures. Synthetic
  tests include unaligned capture, attenuation, clipping, additive noise and echo.
- CRC is error detection, **not authentication**. Server randomness, signature
  authentication, attempt binding, one guess and expiry provide protocol checks.
  No FEC is claimed; damaged frames require retry/review. Real microphone clock drift,
  reverberation and AGC performance require the physical-device guide.
- Kotlin uses mono 16 kHz PCM with `VOICE_RECOGNITION`; Swift uses AVAudioEngine
  measurement mode, reporting the actual sample rate after integer decimation.
  Native errors and missing permissions fail closed. Bluetooth routing, phone calls,
  backgrounding, aggressive audio processing or inaccessible audio may prevent capture.

Use local laptop speakers at a comfortable audible volume, never ultrasound. Do not
interpret successful decoding in a corridor or adjacent room as a software defect
that can be solved solely by higher volume or a shorter token lifetime.

## Policy migration and compatibility

Apply Alembic revision `9bd32a88f101` before deploying the API/clients. It adds
`presence_qr`, `presence_proofs`, and session enable/epoch fields. Historical attempts,
records, biometrics, devices and corrections are unchanged. Displays start **stopped**.
Old clients cannot auto-approve without QR/audio: they return PENDING_REVIEW with
specific reasons. Enrollment and legacy registered HMAC-device compatibility remain.
New device registrations still require the existing native-key flow.

Both Android and iOS require QR/audio unconditionally; there is no bypass switch.
For iOS, the new `dynamic` policy permits automatic attendance only after QR/audio
and all existing mandatory checks. Existing `review`/`retry` policies stay stricter.
The migration converts existing iOS `gps_only` to `dynamic`; new policies default
`dynamic`. A later API write of legacy `gps_only` still cannot bypass QR/audio and
retains its existing App Attest requirement. The dashboard offers `dynamic`, review
or retry. Required provider attestation remains a separate gate.
Android Wi-Fi scan evaluation and its existing `wifi_unavailable` policy remain:
review/reject or optional Wi-Fi with QR/audio/GPS. Optional iOS current-network
identity never becomes a nearby Wi-Fi scan or fabricated RSSI.

Deploy backend, dashboard and rebuilt development apps together. Native microphone
code requires a new Android/iOS build; Expo Go and existing APK/IPA artifacts do not
include it. The tracked historical Podfile.lock is preserved; `pod install` on the
Mac must regenerate it for the new local module. No Xcode compilation is implied
by Expo prebuild or an iOS JavaScript export.

## API additions

All paths below are under `/api/v1`, authenticated and course-scoped.

| Endpoint | Actor / purpose |
|---|---|
| POST `/sessions/{id}/presence/control` | Faculty/admin `{enabled}`; audited start/stop |
| GET `/sessions/{id}/presence/display` | Faculty/admin QR, authoritative timing, listening queue |
| POST `/sessions/{id}/presence/play/{attempt_id}` | Faculty/admin one-use audio payload and deadline |
| POST `/presence/evidence` | Student device-signed `qr`, `ready`, `audio`, or `failure` message |

Evidence uses the existing SignedEvidence envelope: exact `payload` JSON string,
`signature` over `idempotency_key + '.' + payload`, and a random idempotency key.
Presence payload always includes `device_id`, `challenge_id`, `action`;
QR adds `token`, audio adds `response`, failure adds an allowlisted reason.
A failure creates PENDING_REVIEW, with identity marked NOT_COMPLETED, and never an
attendance record. Explicit faculty corrections continue to require an audit reason.
HTTP 409 means invalid/expired/used/mismatched factor. HTTP 429 is a bounded limit.
Lost acknowledgements can retry exact evidence; expired challenges cannot be revived.

## Privacy and remaining security boundaries

Microphone samples live in a bounded JS/native memory buffer only. No audio file,
recording upload or microphone audit payload is created. Stop/unmount/background
clears buffers and ends capture. Audits retain attempt IDs, timestamps and reason
codes, not nonces, audio, biometric templates or face frames. QR tokens and audio
hashes live in protocol tables rather than audit details. The existing encrypted
biometric profile storage is unchanged. Operators should delete expired unused
protocol records under their institutional retention policy; retain referenced
records needed for disputes. No new automated deletion schedule is enabled.

A malicious modified client can submit a relayed answer; signed data proves the
registered key signed it, not that a real microphone captured it. A trusted faculty
account can also leak answers. The 32-bit routing tag is not a secret and is only a
receiver filter; the complete random response is checked. Live relay within five
seconds remains possible. GPS uncertainty, biometric spoof resistance, provider
attestation and device integrity retain their previously documented limitations.
Physical validation and institutional approval remain production release gates.
