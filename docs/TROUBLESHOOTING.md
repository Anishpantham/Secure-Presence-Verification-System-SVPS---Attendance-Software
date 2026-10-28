# Troubleshooting

| Symptom | Check and safe action |
| --- | --- |
| Docker unavailable | Start Docker Desktop, check `docker info`, then `docker compose up -d db`; never down -v |
| Database connection error | Verify service health, port and private host DATABASE_URL target; container uses SPVS_BACKEND_DB; never print secrets |
| Missing tables/migration | Inspect `bash scripts/backend.sh alembic current` and `heads`; back up and review target before upgrade; recovered DB is already at 9bd32a88f101 |
| Invalid credentials | Verify institution account/role and typing; do not reseed recovered data; rate limits require waiting |
| Dashboard cannot reach API | Check API 8000, Vite proxy and browser network status; use make api/make dashboard in separate terminals |
| Phone cannot reach Mac | Same reachable LAN, host bind 0.0.0.0, firewall/Local Network permission and API URL ending /api/v1 |
| LAN IP changed | Update private mobile URL, restart Metro; rebuild when embedded release configuration changes |
| Expo/Metro module missing | Install locked dependencies and rebuild native development client; Expo Go cannot load modules |
| CocoaPods missing | Install Homebrew CocoaPods or documented locked Bundler environment; verify pod --version |
| Xcode signing fails | Open xcworkspace, select team/device and supported entitlements; Personal Team may lack Wi-Fi Information/App Attest |
| GPS inaccurate/reduced | Grant precise location, obtain a fresh stable fix; do not enlarge geofence to pass |
| Outside geofence | Inspect actual location/distance/accuracy and selected classroom; hostel rejection is expected |
| QR expired | Scan a fresh displayed token in active session; refresh display/network; do not reuse screenshots |
| Acoustic failure | Grant microphone, disconnect headphones, keep foreground, match queue ID, enable browser audio and check speaker level/noise/network |
| Audio already consumed/expired | Finish or request review and obtain a fresh allowed attempt; retry identical response only for uncertain transport completion |
| Face enrollment failure | Consent, one evenly lit face, unmirrored capture, slow blink/hold turns; follow capture diagnostics and wait for rate limit |
| Device key lost | Request audited administrator reset; do not delete the server binding or copy private keys |
| Pending review | Inspect reasons and official records separately; a correction must have an attributable reason |
| Model unavailable | Check pinned model files/checksums and MODEL_DIR; `/ready` loads the models |
| Test fixture safety | Use explicit disposable *_test DB; browser suite must target isolated services, never recovered accounts/classrooms |

Support evidence should contain error code, app/build/version, timestamp and sanitized
steps. Exclude passwords, tokens, face frames/templates, raw audio, coordinates and BSSIDs.
