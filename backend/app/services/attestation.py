"""Fail-closed boundary for a future provider verifier, never a boolean supplied by a client."""
from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrityVerdict:
    verified: bool
    reason: str


def verify_integrity(token: str | None, challenge_id: str, platform: str) -> IntegrityVerdict:
    # No project/package/certificate or provider credentials configured in this college distribution.
    # A real adapter must verify Google/Apple signatures, app identity, nonce, freshness and verdict.
    return IntegrityVerdict(False, "ATTESTATION_NOT_CONFIGURED")
