# Android Wi-Fi test build on the local Mac

**27 October update:** a new arm64 APK containing SpvsAcoustic was built and
signature/module-verified after pulling the QR/audio feature. It replaces the
24 October APK at the delivery path. See [current runtime evidence](LOCAL_RUNTIME_UPDATE_2026-10-27.md).
The new APK has not been installed or physically tested; further trials wait
for user readiness. The original build and earlier phone observations below
remain dated historical evidence.

Measured on 2026-10-24. The original build checkpoint below predates physical
Android testing. The [26 October physical report](ANDROID_DEVICE_VALIDATION_2026-10-26.md)
supersedes its pending install/scan/enrollment/initial-submission items.

## Physical continuation through 26 October

Motorola Edge 50 Neo / Android 16 installation, login, registration, enrollment,
Wi-Fi scans and submission were observed. The hostel test's automated submission
required review because classroom AP references were not configured. An explicitly
labelled demo faculty API correction created one PRESENT/CORRECTION record and
resolved the dispute; the actual phone history and audit trail were verified.
The original PENDING_REVIEW attempt remains. Classroom automatic approval is not
established; the user clarified the hostel AP is outside, while the intended
classroom AP is reportedly inside.

The current mobile suite has 46 passing tests after the sign-in validation fix;
the ten native Wi-Fi tests passed again on 26 October. The existing development
APK remains the native host, with current JavaScript loaded from Metro. No native
code changed after its original build.

## Historical 24 October build checkpoint

## Build and checks

- Installed Homebrew Java 17.0.21 and Android command-line tools.
- SDK packages live in the ignored `.runtime/android-sdk`: platform 37.0,
  build tools 37.0.0 (and Gradle-installed 36.0.0), platform tools 37.0.1,
  NDK 27.1.12297006 and CMake 3.22.1.
- Gradle 9.4.1 uses the ignored `.runtime/gradle` cache. Its initial Java download
  timed out; the official distribution was fetched with curl and verified against
  SHA-256 `2ab2958f2a1e51120c326cad6f385153bb11ee93b3c216c5fccebfdfbb7ec6cb`.
- The **SPVS: Android debug build** VS Code task completed successfully in
  6 minutes 50 seconds. The build has upstream deprecation warnings.
- APK: [SPVS_ANDROID_DEBUG.apk](../release/final/SPVS_ANDROID_DEBUG.apk), about
  74 MB, package `edu.spvs.student`, **arm64-v8a**, minimum API 24, target API 36,
  compiled against API 37. APK signature verification passed (v2).
- The Wi-Fi module's 10 Kotlin unit tests passed with no skips or failures.
- All 42 mobile tests and TypeScript checking passed.
- ADB reported no connected device at this checkpoint. Installation, launch,
  radio readings and physical attendance outcomes are not established by this build.

This is a debug development-client APK using the local API and Metro server,
not a standalone production release. Rebuild for a different CPU architecture
with `SPVS_ANDROID_ARCHITECTURES`; the default build script supports all of
React Native's default architectures when that variable is omitted.

## Reproduce

Run the saved **SPVS: Android debug build** task, or set a reachable API URL and
invoke [build_mobile_macos.sh](../scripts/build_mobile_macos.sh) with `android`.
The script finds the installed Homebrew JDK and local SDK automatically.
`SPVS_SKIP_NPM_CI=1` is appropriate only when installed packages match the lockfile.

Native unit tests from `mobile/android`:

```sh
JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home \
ANDROID_HOME="$PWD/../../.runtime/android-sdk" \
GRADLE_USER_HOME="$PWD/../../.runtime/gradle" \
./gradlew :spvs-wifi:testDebugUnitTest --no-daemon
```

## Reproducing the initial physical check

1. Connect a compatible Android phone over USB, enable USB debugging and accept
   its authorization prompt. Confirm the phone appears in `adb devices -l`.
2. Install the APK. Keep the phone on the same reachable network as the Mac.
   Keep the API and Metro tasks running; at this checkpoint Metro is at
   `http://10.0.11.85:8081` and the API at `http://10.0.11.85:8000/api/v1`.
3. Sign in and open **Settings → Wi-Fi setup check**. This standalone check
   needs no device registration and does not submit attendance or upload scans.
4. Enable precise location and location services. Record the displayed AP
   identifiers and RSSI inside the room and in adjacent areas. Confirm classroom
   AP ownership before configuring references; do not copy the phone's MAC address.
5. Follow the [field-test procedure](./TESTING_STRATEGY.md#android-wi-fi-setup-and-field-test).
   Use a separate Android test student for full attendance if retaining the
   existing authorized iPhone. Do not bypass the one-device policy.

The scanner follows Android's [asynchronous scan workflow](https://developer.android.com/develop/connectivity/wifi/wifi-scan),
with a bounded wait and explicit unavailable results. Automated callback tests
cannot measure scan availability or RSSI reliability on a particular phone.
