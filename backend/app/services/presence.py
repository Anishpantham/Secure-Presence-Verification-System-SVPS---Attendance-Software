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


def evaluate(location, wifi, wifi_status, room, references, policy, current, previous=None):
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
    refs = {r.bssid.lower(): r.min_rssi for r in references}
    observations = {w.bssid.lower(): w.rssi for w in wifi}
    if wifi_status != "available" or not observations or not refs:
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
    if policy.require_attestation:
        reasons.append("ATTESTATION_NOT_CONFIGURED")
        score += 50
    return Decision("PENDING_REVIEW" if reasons else "PRESENT", reasons or ["ALL_REQUIRED_CHECKS_PASSED"], min(score, 100), summary)
