# Cross-platform implementation

This completion extends commit `b19777df3cb3210330075c702e5e98f487213a5d`; FastAPI/PostgreSQL, React dashboard and Expo/React Native remain the architecture. The source supports Android and iOS. See [current status](CURRENT_STATUS.md) and [current verification](FINAL_COMPLETION_REPORT.md) for observed builds/tests. The historical cloud record is HISTORICAL_CLOUD_COMPLETION_2026-10-23.md. Source implementation is not physical-device validation.

## Shared application and platform adapters

Authentication, enrollment and deletion/re-enrollment, session selection, randomized camera capture, result, history and API recovery use the same screens. `src/platform` owns native device keys, OS selection, Wi-Fi APIs and simulator API defaults. `capture.ts` executes the server's action order and expiration, cancels on backgrounding, and records capture-start timestamps. It does not calculate a successful biometric verdict on the client. `signals.ts` requests foreground location, checks precise accuracy where available and submits the actual fix time and horizontal uncertainty. Failed requests display recovery instructions. Camera temporary files are deleted in finally blocks.

| Signal | Android | iOS | Server treatment |
|---|---|---|---|
| Face images | Expo Camera front camera | Expo Camera front camera | Same YuNet/SFace and MediaPipe inference |
| Liveness | JPEG still sequence, randomized prompts | Same protocol | Sequence, timing, duplicate-frame and identity gates |
| Device signature | Android Keystore P-256 | Secure Enclave P-256 on physical devices; Keychain on simulator | ECDSA SHA-256, DER signature, registered SPKI key |
| Nearby Wi-Fi | Recent OS readings or awaited scan-completion callback, measured BSSID/RSSI | Not available to ordinary apps | Never synthesized |
| Current Wi-Fi | Scan evidence | NEHotspotNetwork.fetchCurrent, BSSID only | Separate current-network signal; no invented RSSI |
| Location | Expo location provider; coarse/full permission | Core Location through Expo and native accuracyAuthorization | Freshness, uncertainty, geofence, mock flag, travel checks |
| App attestation | Play Integrity remains unconfigured | App Attest native API plus server verifier | Unverified evidence is never reported as verified |

## Permissions and reproducible projects

`app.config.js` and `plugins/withSpvs.js` configure bundle/package `edu.spvs.student`, display name SPVS Student, portrait orientation, icons, launch screen, iOS 16.4 minimum, camera/location/local-network descriptions and Android backup exclusion. Access Wi-Fi Information is disabled by default for Personal Team compatibility. Supported Apple Developer Team builds opt in with `SPVS_IOS_WIFI_INFO=1` before prebuild and require a matching provisioning profile. Unsetting it or setting `0` removes only the Wi-Fi entitlement, including one left by a previous build; the native current-network implementation remains. Set the same variable when running `scripts/verify_native_config.py`. App Attest is separately controlled by `SPVS_APP_ATTEST_ENV=development` or `production`; its existing behavior is unchanged. No background location, microphone or unrestricted iOS Wi-Fi scan is requested. Android location permission gates scan access; scan throttling and OEM restrictions can return unavailable.

Run `npm ci` then `npx expo prebuild --no-install --no-clean`. Expo 58 defaults to clearing native directories unless `--no-clean` is supplied. Generated Android and Xcode projects are derived artifacts; only the resolved iOS Podfile.lock is retained in Git. Local Swift/Kotlin Expo modules and podspecs are included. `python3 scripts/verify_native_config.py` checks generated files, not native compilation. The CocoaPods Gemfile pins 1.16.2; run `bundle install` before `bundle exec pod install`. The [local Mac validation](IOS_MAC_VALIDATION.md) records the genuine CocoaPods resolution and Xcode run; the original Linux report remains historical.

Release transport requires an HTTPS API endpoint. For an isolated local development network only, set `SPVS_DEV_HTTP=1` before prebuild and use a development client. Production configuration defaults to TLS and disables Android cleartext. Do not use local HTTP for real student data. Android emulator defaults to 10.0.2.2; iOS simulator defaults to localhost. Set EXPO_PUBLIC_API_URL explicitly for physical phones and release builds.

## Device binding and lifecycle

Registration requests a short-lived server nonce. The client signs `SPVS-REGISTER-v1.<nonce>.<platform>.<SHA256(SPKI bytes)>` using its newly generated P-256 key; the server verifies password confirmation, ownership, expiry, signature and the single-active-device constraint. Evidence signs the exact UTF-8 bytes `<idempotency_key>.<payload>`; the signature is base64 DER ECDSA/SHA-256. Neither platform exports a private key to JavaScript. The iOS physical-device path does not silently downgrade from Secure Enclave when key generation fails. Simulator Keychain keys have lower assurance.

A storage label is a client report, not proof of hardware protection. The server exposes this distinction in its admin device list. Old HMAC registrations continue to work for migration; new shared-secret registrations are disabled by default (`ALLOW_LEGACY_DEVICE_REGISTRATION=false`). Test fixtures explicitly enable legacy compatibility. Retire old devices through the audited reset process.

Native installation IDs and stored key aliases detect reinstall/key loss on submission. Signing never silently creates a replacement key. A lost/revoked credential requires an administrator-approved reset. iOS Keychain items can survive uninstall; an installation ID mismatch prevents their silent reuse. The existing device remains authorized until reset approval. Each student's local metadata is stored separately, device-only, in SecureStore. Native storage compromise, rooted devices or injected clients are not solved by a client-reported storage label.

## Apple App Attest setup and protocol

1. In the Apple Developer portal register the exact bundle ID and enable App Attest and Access Wi-Fi Information. Use a matching development/distribution provisioning profile. App Attest requires a supported physical device; simulators return unsupported.
2. Retrieve Apple's **App Attestation Root CA** from Apple's official certificate authority page over verified HTTPS. Independently verify its SHA-256 fingerprint through a trusted institutional setup process. Do not accept a root supplied by a client or a certificate from an arbitrary blog. Store the PEM outside the repository.
3. Configure the backend with `APPLE_APP_ID=<TeamID>.edu.spvs.student`, `APPLE_ATTEST_ENVIRONMENT=development` (or production), `APPLE_ATTEST_ROOT_PEM=/run/config/apple-app-attestation-root.pem` and `APPLE_ATTEST_ROOT_SHA256=<verified hex fingerprint>`. The certificate is public, but these are deployment trust settings. Mount the PEM read-only in Docker. All four values must be set; production/development separation is enforced.
4. Set the corresponding `SPVS_APP_ATTEST_ENV` before prebuild or use the EAS profile, sign and install the development build. Register the SPVS device, then choose Register Apple app attestation.
5. `/attestation/challenge` supplies a random one-use nonce bound to user and device. Native `attestKey` hashes `SPVS-ATTEST-v1.<nonce>.<device_id>.<key_id>`. The server decodes bounded CBOR, verifies the pinned certificate chain, validity, basic/key-usage constraints, nonce extension, app-ID hash, environment AAGUID, zero initial counter, credential ID, public-key hash and COSE key consistency. It stores the public key only on success; failed registration consumes its challenge.
6. Each attendance request generates an assertion over SHA256 of the exact signed request bytes. The backend checks the app hash and ECDSA signature and atomically advances a strictly increasing counter under a database lock. Replays and out-of-order assertions cannot pass. Exact authenticated attendance retries return the existing result without double counting.

The verifier is covered by synthetic certificate/signature tests. It has **not** been validated with a genuine Apple attestation object or physical iPhone. Apple receipt risk assessment and distribution-scale fraud monitoring are not implemented. Complete a provider interoperability review before enabling institutional attestation requirements. Apple's root and developer identity are intentionally not fabricated or bundled.

Play Integrity is a fail-closed boundary: no decoded client verdict is trusted. To finish its provider adapter, configure a Google Cloud project linked to Play Console, package identity and allowed signing-certificate digests, obtain a standard Integrity token bound to SHA256 of the exact request, decode it through Google's authenticated server API, enforce request package/hash/timestamp and app/device verdicts, and add replay/quota/error tests on Play-distributed physical devices. This release does not claim that integration is configured or verified.

## Presence policy and assurance

The Android scanner reuses readings at most 15 seconds old, otherwise waits up
to eight seconds for a successful system scan broadcast. Concurrent calls share
one scan; timeout/cancellation removes listeners. Coarse and precise location
permissions are requested together and precise access is required. Settings
includes a local-only Wi-Fi setup check for reference collection. See the
[field procedure](TESTING_STRATEGY.md#android-wi-fi-setup-and-field-test).

The current iOS `review` policy always requires review, including when the current
BSSID matches. There is no separate automatic Wi-Fi-match approval mode. The
Personal Team development build lacks the Wi-Fi entitlement, and the local demo
classroom currently has no AP references. These are configuration and policy
limits; the Android scan fix does not change them.

Android retains `wifi_unavailable=review|reject|gps_only`. iOS has a separate audited `ios_presence=review|retry|gps_only`, default review. A GPS-only opt-in applies only after mandatory identity, device, liveness and GPS gates; it never overrides failed identity or a required unverified attestation. Every attempt records platform, policy, reported key storage and presence assurance. Missing Wi-Fi is distinct from a mismatched observed network. A permitted iOS current BSSID does not raise GPS to multi-AP fingerprint assurance. Reduced-accuracy location requires retry even when a client reports a small numeric radius. GPS coordinates and Wi-Fi observations remain potentially spoofable client evidence.

## Camera protocol and limits

Both camera adapters return processed JPEGs at width 640, front camera with mirror disabled. Android YUV and iOS pixel-buffer formats do not cross the API; Expo handles sensor conversion and orientation before JPEG encoding. ImageManipulator resizes and recompresses, and the server validates JPEG dimensions, lighting, blur, exactly one face, landmarks and 128-dimensional normalized embeddings. The capture loop targets 170 ms intervals, allows a 350 ms prompt transition, and requests slow blink/open-close-open evidence. Actual capture speed and front-camera orientation are hardware dependent. Capture-start timestamps are adjusted by server clock offset; they are signed but not trusted hardware timestamps. Reject gaps outside server bounds and interrupted/expired captures; never forge timing to make a sequence pass.

Server inference and temporal tests do not establish live-camera usability, biometric accuracy, sophisticated presentation-attack resistance or injection resistance. Verify blink capture rate, left/right orientation, lens/mirroring, accessibility, reduced GPS, Wi-Fi throttling, airplane mode, key loss and network retry on real Android and iPhone hardware before a demonstration with students.

## Native build procedures

See SETUP_AND_DEMO_GUIDE.md and `scripts/build_mobile_macos.sh`. Android builds require JDK 17, the SDK/NDK versions emitted by the pinned Expo prebuild and Gradle's trusted repositories. iOS requires macOS, a supported Xcode version (the pinned React Native helper declares at least 16.1; use a current supported Xcode), command-line tools, Ruby/Bundler and CocoaPods. Simulator compilation does not verify Secure Enclave or App Attest. Physical iPhone builds require signing and matching capabilities. TestFlight requires an Apple Developer membership, App Store Connect record, distribution provisioning and a genuine archive/upload. No unsigned file is renamed to IPA.


Automatic iPhone GPS-only approval additionally requires a verified App Attest assertion, even if the global attestation requirement is off. The registered platform is client-reported; without this gate an unverified client could select a weaker platform policy. With App Attest unavailable/unconfigured, iPhone verification remains review/retry. GPS-only evidence still has lower presence assurance after app verification.
