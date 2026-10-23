#!/usr/bin/env bash
set -euo pipefail
SPVS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[[ "$(uname -s)" == Darwin ]] || { echo 'Native macOS builds require macOS and Xcode/Android Studio.' >&2; exit 1; }
cd "$SPVS_ROOT/mobile"
: "${EXPO_PUBLIC_API_URL:?Set EXPO_PUBLIC_API_URL to the reachable API /api/v1 URL before building}"
npm ci
case "${1:-}" in
 android)
  export JAVA_HOME="${JAVA_HOME:-$(/usr/libexec/java_home -v 17)}"
  export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
  npx expo prebuild --platform android --no-install
  (cd android && ./gradlew :app:assembleDebug --no-daemon)
  mkdir -p "$SPVS_ROOT/release/final"
  cp android/app/build/outputs/apk/debug/app-debug.apk "$SPVS_ROOT/release/final/SPVS_ANDROID_DEBUG.apk"
  ;;
 ios-simulator)
  xcodebuild -version
  npx expo prebuild --platform ios --no-install
  (cd ios && bundle exec pod install)
  xcodebuild -workspace ios/SPVSStudent.xcworkspace -scheme SPVSStudent -configuration Debug \
    -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' \
    -derivedDataPath "$SPVS_ROOT/work/ios-derived" CODE_SIGNING_ALLOWED=NO build
  ;;
 ios-device)
  xcodebuild -version
  npx expo prebuild --platform ios --no-install
  (cd ios && bundle exec pod install)
  echo 'Open ios/SPVSStudent.xcworkspace; select your Apple team and connected iPhone, then Run.'
  open ios/SPVSStudent.xcworkspace
  ;;
 *) echo 'Usage: scripts/build_mobile_macos.sh android|ios-simulator|ios-device' >&2; exit 2;;
esac
