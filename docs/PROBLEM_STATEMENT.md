# Problem statement

Paper registers and token-based attendance capture a declaration of presence without independently evaluating the claimant's identity, device or location. A student can share a token, transmit an expired screenshot, give credentials to another student, or submit a request outside the classroom. An institution may also lack a record of who changed an attendance result and why.

SPVS must evaluate evidence close to the attendance session, preserve accountability and distinguish uncertainty from acceptance. A device request cannot authoritatively declare its own face similarity, liveness result or geofence status. The server must evaluate the submitted data and enforce enrollment, session expiry, device authorization and duplicate protection.

The environment imposes limits. Consumer GPS cannot reliably distinguish every indoor classroom. Wi-Fi access differs by operating system and permissions. A compromised phone can invent coordinates or inject images. Basic landmark sequences do not establish cryptographic capture provenance. Consequently, ambiguous signals must support retries or human review, and the final report must state what was measured and what remains unverified.

The project excludes additional hardware and surveillance. Its success criterion is a reproducible, testable two-layer system with honest outcomes and a complete audit path, not an unsupported claim of zero proxy attendance.
