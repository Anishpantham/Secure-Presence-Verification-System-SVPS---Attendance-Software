#!/usr/bin/env bash
set -euo pipefail
SPVS_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[[ "$(uname -s)" == Darwin ]] || { echo 'Native macOS builds require macOS and Xcode/Android Studio.' >&2; exit 1; }
cd "$SPVS_ROOT/mobile"
: "${EXPO_PUBLIC_API_URL:?Set EXPO_PUBLIC_API_URL to the reachable API /api/v1 URL before building}"
# Use the opt-in only after a successful npm ci for the current lockfile.
if [[ "${SPVS_SKIP_NPM_CI:-0}" != 1 ]]; then
  npm ci --cache "$SPVS_ROOT/.runtime/npm-cache"
fi

install_ios_pods() {
  # Keep the system Ruby untouched; use the documented Homebrew Ruby if present.
  if [[ -d /opt/homebrew/opt/ruby@3.3/bin ]]; then
    export PATH="/opt/homebrew/opt/ruby@3.3/bin:$PATH"
  fi
  export BUNDLE_GEMFILE="$SPVS_ROOT/mobile/Gemfile"
  export BUNDLE_PATH="${BUNDLE_PATH:-$SPVS_ROOT/.runtime/bundle}"
  bundle check || bundle install
  (cd ios && bundle exec pod install)
}
case "${1:-}" in
 android)
  export JAVA_HOME="${JAVA_HOME:-$(/usr/libexec/java_home -v 17)}"
  export ANDROID_HOME="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
  npx expo prebuild --platform android --no-install --no-clean
  (cd android && ./gradlew :app:assembleDebug --no-daemon)
  mkdir -p "$SPVS_ROOT/release/final"
  cp android/app/build/outputs/apk/debug/app-debug.apk "$SPVS_ROOT/release/final/SPVS_ANDROID_DEBUG.apk"
  ;;
 ios-simulator)
  xcodebuild -version
  npx expo prebuild --platform ios --no-install --no-clean
  install_ios_pods
  mkdir -p "$SPVS_ROOT/work"
  SPVS_BUILD_LOG="$SPVS_ROOT/work/ios-simulator-build.log"
  if xcodebuild -workspace ios/SPVSStudent.xcworkspace -scheme SPVSStudent -configuration Debug \
    -sdk iphonesimulator -destination "${SPVS_IOS_DESTINATION:-generic/platform=iOS Simulator}" \
    -derivedDataPath "$SPVS_ROOT/work/ios-derived" CODE_SIGNING_ALLOWED=NO build > "$SPVS_BUILD_LOG" 2>&1; then
    tail -n 5 "$SPVS_BUILD_LOG"
  else
    tail -n 100 "$SPVS_BUILD_LOG"
    echo "Full build log: $SPVS_BUILD_LOG" >&2
    exit 1
  fi
  echo "Full build log: $SPVS_BUILD_LOG"
  ;;
 ios-device)
  xcodebuild -version
  npx expo prebuild --platform ios --no-install --no-clean
  install_ios_pods
  echo 'Open ios/SPVSStudent.xcworkspace; select your Apple team and connected iPhone, then Run.'
  open ios/SPVSStudent.xcworkspace
  ;;
 *) echo 'Usage: scripts/build_mobile_macos.sh android|ios-simulator|ios-device' >&2; exit 2;;
esac
