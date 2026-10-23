"""Static generated-project checks; not a substitute for Xcode/Gradle compilation."""
import json
import plistlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'mobile'
props=json.loads((root/'ios/Podfile.properties.json').read_text())
assert props['ios.deploymentTarget']=='16.4'
info=plistlib.loads((root/'ios/SPVSStudent/Info.plist').read_bytes())
for key in ('NSCameraUsageDescription','NSLocationWhenInUseUsageDescription','NSLocalNetworkUsageDescription'):
    assert info.get(key),key
entitlements=plistlib.loads((root/'ios/SPVSStudent/SPVSStudent.entitlements').read_bytes())
assert entitlements['com.apple.developer.networking.wifi-info'] is True
for name in ('spvs-security','spvs-wifi'):
    config=json.loads((root/f'modules/{name}/expo-module.config.json').read_text())
    assert 'apple' in config['platforms'] and 'android' in config['platforms']
manifest=(root/'android/app/src/main/AndroidManifest.xml').read_text()
assert 'android:allowBackup="false"' in manifest
assert 'android.permission.CAMERA' in manifest and 'android.permission.ACCESS_FINE_LOCATION' in manifest
print('Generated iOS/Android configuration checks passed; native compilation is a separate check.')
