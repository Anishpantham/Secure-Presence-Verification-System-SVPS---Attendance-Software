# SPVS delivery

**Historical baseline delivery.** Start with [current local status](docs/CURRENT_STATUS.md)
for the Mac/iPhone/Android continuation and publication status.

Start with `README.md` inside the ZIP or the setup/demo PDF.

- `SPVS_COMPLETE_PROJECT.zip` — actual backend, dashboard, mobile source, migration, tests, lockfiles, documentation, verified models and recorded evidence.
- `SPVS_PROJECT_REPORT.pdf` — editable-source college report with diagrams, implementation details and measured test evidence.
- `SPVS_SETUP_AND_DEMO_GUIDE.pdf` — installation, configuration, demonstration and troubleshooting instructions.
- `SPVS_VERIFICATION_REPORT.md` — exact validation results and remaining limits.
- `SPVS_DELIVERY_README.md` — this delivery map.

Unpack `spvs-root`, then run `make setup`, `make db`, `make migrate`, and `make seed`. Start the API and dashboard using separate `make api` and `make dashboard` terminals, or follow the Docker instructions. Local secrets and demo passwords are generated into `.env`; none are included here.

The project includes real face-model inference and server-side gates. Physical-phone verification, Apple Silicon runtime testing and external attestation are not claimed as completed. The current Expo dependency tree has two unpatched upstream advisories. Read the verification report before deployment or evaluation.

If an Android debug APK accompanies this delivery, it is a development build requiring Metro and a suitable API endpoint, not a production-signed release or evidence of physical-device testing.
