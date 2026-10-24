package edu.spvs.wifi

/** One bounded scan, driven by Android callbacks (all calls on the main thread). */
internal class WifiScanSession(
  private val read: () -> List<Map<String, Any>>,
  private val startScan: () -> Boolean,
  private val listen: ((Boolean) -> Unit) -> (() -> Unit),
  private val scheduleTimeout: (() -> Unit) -> (() -> Unit),
  private val complete: (Map<String, Any>) -> Unit
) {
  private var finished = false
  private var stopListening: (() -> Unit)? = null
  private var stopTimeout: (() -> Unit)? = null

  fun start() {
    try {
      // Recent platform scans are useful evidence and avoid unnecessary throttling.
      val cached = read()
      if (cached.isNotEmpty()) {
        finish("available", cached)
        return
      }
      stopListening = listen { updated ->
        if (!finished && updated) readCompletedScan()
      }
      stopTimeout = scheduleTimeout { if (!finished) finish("unavailable") }
      // A throttled request can still receive another platform scan before timeout.
      if (!startScan()) return // Keep the listener and timeout for a passive scan.
    } catch (_: SecurityException) {
      finish("permission_denied")
    } catch (_: RuntimeException) {
      finish("unavailable")
    }
  }

  private fun readCompletedScan() {
    try {
      val observations = read()
      finish(if (observations.isEmpty()) "unavailable" else "available", observations)
    } catch (_: SecurityException) {
      finish("permission_denied")
    } catch (_: RuntimeException) {
      finish("unavailable")
    }
  }

  fun cancel() = finish("unavailable")

  private fun finish(status: String, observations: List<Map<String, Any>> = emptyList()) {
    if (finished) return
    finished = true
    stopTimeout?.invoke()
    stopListening?.invoke()
    stopTimeout = null
    stopListening = null
    complete(mapOf("status" to status, "source" to if (status == "available") "scan" else "none",
      "observations" to observations))
  }
}

internal data class WifiReading(val bssid: String, val rssi: Int, val timestampMicros: Long)

internal fun freshReadings(readings: List<WifiReading>, nowMicros: Long): List<Map<String, Any>> =
  readings.filter {
    val age = nowMicros - it.timestampMicros
    it.timestampMicros > 0 && age in 0..15_000_000L && it.rssi in -127..0 &&
      Regex("^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$").matches(it.bssid) &&
      it.bssid.lowercase() !in setOf("00:00:00:00:00:00", "02:00:00:00:00:00", "ff:ff:ff:ff:ff:ff")
  }.sortedByDescending { it.timestampMicros }.distinctBy { it.bssid.lowercase() }
    .sortedByDescending { it.rssi }.take(50)
    .map { mapOf("bssid" to it.bssid.lowercase(), "rssi" to it.rssi) }
