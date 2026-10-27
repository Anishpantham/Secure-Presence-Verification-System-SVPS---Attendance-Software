# C003 classroom calibration and attendance observations

Record date: **27 October 2026, Asia/Kolkata**. Physical observations below were
made on 26 October, before the local QR/acoustic policy-v2 runtime update.
They do not establish physical operation of the new QR/audio flow.

## Classroom configuration

Created a separate **120 seater C003** classroom using the user's Maps coordinates,
retaining a 50 m GPS radius. The earlier hostel test room remains separate so its
history keeps the original configuration. Precise coordinates, database IDs,
SSID and raw BSSIDs remain local and are excluded from this public record.

The user reports two physical routers and a door at the far-left front. Mapping
the observed BSSIDs to individual physical routers was not independently verified.
Multiple advertised network names/radios must not be counted as independent routers.

## Collected calibration samples

| Anonymous student-network radio | Initial inside | Far-right back | Far-left back | Outside doorway, door closed |
| --- | ---: | ---: | ---: | ---: |
| A, 2.4 GHz | -46 | Not observed | -66 | Not observed |
| B, 5 GHz | -52 | -60 | -60 | -96 |
| C, 2.4 GHz | -54 | -63 | -76 | Not observed |
| D, 5 GHz | -57 | -56 | -54 | -98 |
| Total displayed BSSIDs | 17 | 12 | 36 | 8 |

Values are dBm, read from the SPVS diagnostic UI. The user moved to each position,
scanned and returned without rescanning; the result was preserved before any
subsequent check. The 36-entry result was scrolled and captured completely.
Positions and the closed door are user-reported, not independent location tracking.
UI inspection times are not independent radio-acquisition timestamps. Absence
from one scan does not prove an AP is physically absent.

Two consistently observed 5 GHz radio identifiers (B and D) were selected as
**provisional references at -70 dBm each**. This is 10 dB below the weakest selected
inside observation (-60). The existing rule is unchanged: at least half the
configured references must meet their minima, so **one of these two is enough**.
No stricter two-router co-presence or cryptographic proximity claim is made.

Offline checks using these measured scans and identical synthetic eligible GPS
returned PRESENT for all three inside samples and PENDING_REVIEW with
WIFI_GPS_DISAGREEMENT for the corridor sample. Those checks did not submit
attendance. The threshold was fitted to these samples; fresh independent tests
are required and no statistical accuracy rate is claimed.

## Fresh attendance submissions under the earlier flow

| Case | Server outcome | Evidence | Official record |
| --- | --- | --- | --- |
| Inside C003, 26 October 18:34:48 IST | PRESENT / ALL_REQUIRED_CHECKS_PASSED | GPS distance 13.5 m, uncertainty 20 m, age 0.6 s; liveness passed; scan available; Wi-Fi match ratio 0.5 | PRESENT, source VERIFICATION |
| Hostel room, 26 October 23:57:53 IST | REJECTED / OUTSIDE_GEOFENCE | GPS distance 151.1 m, uncertainty about 26.4 m, age 0.7 s; liveness passed; scan available | None |

The inside session was closed with its automatic record intact. A separate
outside-test session avoided duplicate-attendance rejection. The user later
clarified that the second attempt was made from the **hostel room**, not just
outside C003. The test notes were corrected accordingly.

The server's geofence check returned before Wi-Fi matching in that hostel attempt.
It is therefore evidence of a far-location GPS rejection, not proof that Wi-Fi
excluded a person just outside the classroom. The earlier closed-door corridor
diagnostic scan and the later hostel attendance submission are distinct cases.

## Preserved state after the upstream update

The new database migration preserved C003, its two references, prior attempts,
automatic record, and the separate hostel demo correction/dispute history. The
old evidence remains unchanged. New attendance now requires mandatory QR/audio
proof before face/GPS/Wi-Fi decisions; enrollment retains its own flow.

## Pending physical work

**Do not start another physical test until the user explicitly says they are in
the classroom and ready.** The next test plan must account for the new QR/audio
flow, install the rebuilt native clients, use a fresh session and start faculty
challenges. Record which gate determines any outside result; a QR/audio/GPS failure
does not isolate the contribution of Wi-Fi. Include open-door/closed-door and
adjacent-room conditions and new samples, not just the calibration readings above.

The immediate-doorway fresh Wi-Fi-specific attendance comparison was never
completed under the older flow. Physical QR/audio interoperability, acoustic
leakage/relay, and classroom automatic acceptance/rejection under policy v2 all
remain unverified. See [the physical plan](ACOUSTIC_DEVICE_VALIDATION.md).

Sanitized evidence: [c003-validation.json](evidence/local-2026-10-27/c003-validation.json).
Raw identifiers, coordinates and UI snapshots remain in the ignored local work
directory. No policy was weakened to force an attendance result.
