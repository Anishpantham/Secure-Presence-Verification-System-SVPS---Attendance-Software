"""Deterministic Layer 2 rules; a score never overrides a mandatory gate."""
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt


@dataclass
class Decision:
    state: str
    reasons: list[str]
    risk_score: int
    summary: dict


def haversine(lat1, lon1, lat2, lon2):
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 6371000 * 2 * asin(min(1, sqrt(a)))


def evaluate(location, wifi, wifi_status, room, references, policy, current, previous=None, *, platform="android", wifi_source="scan", current_bssid=None, attestation_verified=False):
    if location is None:
        return Decision("REQUIRES_RETRY", ["LOCATION_MISSING"], 30, {})
    age = (current - location.captured_at).total_seconds()
    distance = haversine(location.latitude, location.longitude, room.latitude, room.longitude)
    summary = {"distance_m": round(distance, 1), "accuracy_m": location.accuracy_m, "age_s": round(age, 1),
               "wifi_status": wifi_status, "attestation": "UNVERIFIED"}
    if location.mocked:
        return Decision("REJECTED", ["MOCK_LOCATION_REPORTED"], 100, summary)
    if age < -3 or age > policy.max_location_age_s:
        return Decision("REQUIRES_RETRY", ["LOCATION_STALE"], 30, summary)
    if getattr(location, 'accuracy_authorization', 'unknown') == 'reduced':
        return Decision("REQUIRES_RETRY", ["PRECISE_LOCATION_REQUIRED"], 30, summary)
    if location.accuracy_m > policy.max_accuracy_m:
        return Decision("REQUIRES_RETRY", ["LOCATION_INACCURATE"], 30, summary)
    if distance - location.accuracy_m > room.radius_m:
        return Decision("REJECTED", ["OUTSIDE_GEOFENCE"], 80, summary)
    reasons, score = [], 0
    if distance + location.accuracy_m > room.radius_m:
        reasons.append("GEOFENCE_BOUNDARY_UNCERTAIN")
        score += 35
    if previous:
        elapsed = (current - previous["time"]).total_seconds()
        travel = haversine(location.latitude, location.longitude, previous["latitude"], previous["longitude"])
        if 0 < elapsed < 300 and travel / elapsed > 55:
            reasons.append("IMPLAUSIBLE_TRAVEL")
            score += 60
    # Current-network identity has no measured RSSI and is never a multi-AP fingerprint.
    if platform == 'ios':
        summary['presence_assurance'] = 'GPS_WITH_CURRENT_NETWORK' if current_bssid else 'GPS_ONLY'
        summary['current_network_match'] = bool(current_bssid and any(r.bssid.lower() == current_bssid.lower() for r in references))
        if wifi or wifi_source == 'scan' and wifi_status == 'available':
            return Decision('REQUIRES_RETRY', ['IOS_WIFI_SCAN_UNSUPPORTED'], 40, summary)
        ios_policy = getattr(policy, 'ios_presence', 'review')
        summary['ios_policy'] = ios_policy
        if ios_policy == 'retry':
            return Decision('REQUIRES_RETRY', ['IOS_PRESENCE_EVIDENCE_INSUFFICIENT'], 30, summary)
        # A client-reported platform must not select a weaker automatic policy.
        if ios_policy == 'gps_only' and not attestation_verified:
            reasons.append('IOS_PLATFORM_ATTESTATION_REQUIRED')
            score += 50
        if ios_policy != 'gps_only':
            reasons.append('IOS_PRESENCE_REVIEW_REQUIRED')
            score += 25
        if current_bssid and references and not summary['current_network_match']:
            reasons.append('CURRENT_NETWORK_MISMATCH')
            score += 40
    else:
        summary['presence_assurance'] = 'GPS_AND_WIFI_SCAN' if wifi_status == 'available' else 'GPS_ONLY'
    refs = {r.bssid.lower(): r.min_rssi for r in references}
    observations = {w.bssid.lower(): w.rssi for w in wifi}
    if platform == "ios":
        summary["wifi_match"] = "NOT_A_SCAN"
    elif wifi_status != "available" or not observations or not refs:
        summary["wifi_match"] = "UNAVAILABLE"
        if policy.wifi_unavailable == "reject":
            return Decision("REJECTED", ["WIFI_REQUIRED"], 70, summary)
        if policy.wifi_unavailable == "review":
            reasons.append("WIFI_UNAVAILABLE")
            score += 25
    else:
        matches = sum(b in observations and observations[b] >= rssi for b, rssi in refs.items())
        ratio = matches / len(refs)
        summary["wifi_match_ratio"] = round(ratio, 3)
        # At least half of configured reference APs must meet their minimum signal strength.
        if ratio < 0.5:
            reasons.append("WIFI_GPS_DISAGREEMENT")
            score += 50
    if policy.require_attestation and not attestation_verified:
        reasons.append("ATTESTATION_NOT_CONFIGURED")
        score += 50
    return Decision("PENDING_REVIEW" if reasons else "PRESENT", reasons or ["ALL_REQUIRED_CHECKS_PASSED"], min(score, 100), summary)
