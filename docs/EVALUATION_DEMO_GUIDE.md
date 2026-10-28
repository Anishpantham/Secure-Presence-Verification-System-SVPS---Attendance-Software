# Evaluation demonstration guide

## Start safely

Use the recovered environment without setup/seeding/reset. Confirm the host API
targets spvs_recovery and the schema is at 9bd32a88f101. From the repository root:

```sh
docker compose up -d db
make api
```

Docker is backgrounded; API remains in terminal 1. Run `make dashboard` in terminal 2.
In terminal 3, `cd mobile` then `npm start`. Do not start duplicate servers on busy
ports. Rebuilt native development clients are required; Expo Go is insufficient.
Check `/health`, `/ready`, dashboard connectivity and the phone's private API URL.
Keep credentials, records and raw sensor readings off the presentation screen.

## Faculty preparation

Log in, choose the assigned course and existing C003 classroom, create an active
session and start challenges. Do not edit C003 coordinates or fingerprints. Keep
the rotating QR visible and laptop speakers audible. Each student taps Listen;
play only the matching queued attempt. Playback reservations are five seconds.

## Android demonstration

Use Motorola Edge 50 Neo with camera, microphone, precise location and Wi-Fi access.
Log in; reuse the existing bound device and consented profile. Scan QR, tap Listen,
have faculty play the matching challenge, then complete face/liveness and location
capture. Show the final reasons, own attempt history and official record separately.

## iOS demonstration

Use iPhone 16 Pro with Local Network, camera, microphone and precise location access.
Repeat QR/audio and available identity checks. Explain that current-network BSSID
is optional and is not an Android scan. Observe actual iOS policy; an unchanged
review policy can legitimately prevent automatic approval even inside the classroom.
Do not turn on dynamic policy or lower requirements merely for a successful demo.

## Negative test

Use a separate active session/eligible attempt outside C003. Complete prerequisites
and record the gate that decides rejection. A hostel OUTSIDE_GEOFENCE is expected
and creates no approved attendance. QR/audio expiry or failed identity is a distinct
result; it does not isolate GPS or Wi-Fi. The historical user tests are observations,
not a claim that this guide was rerun by the audit agent.

## Positive test — outcome pending

Only when physically inside C003 and ready, repeat on both platforms with a fresh
session, current builds and unchanged calibrated settings. Record GPS quality and
Android Wi-Fi availability/match summary; inspect iOS policy. Require PRESENT with
policy version 2, completed QR/audio, identity and liveness, an official record with
source VERIFICATION, and the matching faculty dashboard entry. If it returns review,
record review honestly. A later faculty correction is not automatic approval.

Use the [checklist](EVALUATION_CHECKLIST.md) to record date, operator, app build,
expected/actual outcome and redacted evidence. No physical trials are started by
this audit. Do not publish screenshots containing students or private configuration.
