package edu.spvs.wifi

import android.content.Context
import android.net.wifi.WifiManager
import android.os.SystemClock
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

/** Real, recent Android scan results only. OS scan throttling may yield unavailable evidence. */
class SpvsWifiModule : Module() {
  override fun definition() = ModuleDefinition {
    Name("SpvsWifi")
    AsyncFunction("scan") {
      val context = appContext.reactContext ?: throw IllegalStateException("No React context")
      val manager = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
      try {
        @Suppress("DEPRECATION")
        manager.startScan() // Asynchronous hint; never pretend the scan completed immediately.
        val nowMicros = SystemClock.elapsedRealtimeNanos() / 1000
        val observations = manager.scanResults.filter {
          val age = nowMicros - it.timestamp
          age >= 0 && age <= 15_000_000 && it.BSSID != "02:00:00:00:00:00"
        }.take(50).map { mapOf("bssid" to it.BSSID.lowercase(), "rssi" to it.level) }
        mapOf("status" to if (observations.isEmpty()) "unavailable" else "available", "observations" to observations)
      } catch (e: SecurityException) {
        mapOf("status" to "permission_denied", "observations" to emptyList<Any>())
      }
    }
  }
}
