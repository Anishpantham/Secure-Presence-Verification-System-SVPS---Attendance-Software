package edu.spvs.wifi

import android.content.Context
import android.content.BroadcastReceiver
import android.content.Intent
import android.content.IntentFilter
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.os.SystemClock
import expo.modules.kotlin.Promise
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

/** Real, recent Android scan results only. OS scan throttling may yield unavailable evidence. */
class SpvsWifiModule : Module() {
  private val handler = Handler(Looper.getMainLooper())
  private var pending: WifiScanSession? = null
  private val waiters = mutableListOf<Promise>()
  @Volatile private var destroyed = false

  override fun definition() = ModuleDefinition {
    Name("SpvsWifi")
    AsyncFunction("scan") { promise: Promise ->
      handler.post { scan(promise) }
    }
    OnDestroy {
      destroyed = true
      handler.post { pending?.cancel() }
    }
  }

  private fun scan(promise: Promise) {
    val context = appContext.reactContext?.applicationContext
    if (destroyed || context == null) {
      promise.resolve(mapOf("status" to "unavailable", "source" to "none", "observations" to emptyList<Any>()))
      return
    }
    waiters.add(promise)
    if (pending != null) return // Concurrent callers share a single scan and timeout.
    val manager = context.getSystemService(Context.WIFI_SERVICE) as WifiManager
    val session = WifiScanSession(
      read = {
        freshReadings(manager.scanResults.map { WifiReading(it.BSSID ?: "", it.level, it.timestamp) },
          SystemClock.elapsedRealtimeNanos() / 1000)
      },
      startScan = {
        @Suppress("DEPRECATION")
        manager.startScan()
      },
      listen = { completed ->
        val receiver = object : BroadcastReceiver() {
          override fun onReceive(context: Context, intent: Intent) {
            if (intent.action == WifiManager.SCAN_RESULTS_AVAILABLE_ACTION) {
              completed(intent.getBooleanExtra(WifiManager.EXTRA_RESULTS_UPDATED, false))
            }
          }
        }
        val filter = IntentFilter(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION)
        // Wi-Fi broadcasts may originate from privileged system components.
        if (Build.VERSION.SDK_INT >= 33) context.registerReceiver(receiver, filter, Context.RECEIVER_EXPORTED)
        else context.registerReceiver(receiver, filter)
        val unregister: () -> Unit = { context.unregisterReceiver(receiver) }
        unregister
      },
      scheduleTimeout = { expired ->
        val timeout = Runnable { expired() }
        handler.postDelayed(timeout, 8_000)
        val cancel: () -> Unit = { handler.removeCallbacks(timeout) }
        cancel
      },
      complete = { result ->
        pending = null
        val promises = waiters.toList()
        waiters.clear()
        promises.forEach { it.resolve(result) }
      }
    )
    pending = session
    session.start()
  }
}
