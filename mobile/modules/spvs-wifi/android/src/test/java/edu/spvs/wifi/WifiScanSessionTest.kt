package edu.spvs.wifi

import org.junit.Assert.*
import org.junit.Test

class WifiScanSessionTest {
  private val observation = mapOf<String, Any>("bssid" to "aa:bb:cc:dd:ee:ff", "rssi" to -55)

  private class Fixture {
    var readings: List<Map<String, Any>> = emptyList()
    var denied = false
    var accepted = true
    var requests = 0
    var listeners = 0
    var timers = 0
    var callback: ((Boolean) -> Unit)? = null
    var timeout: (() -> Unit)? = null
    val results = mutableListOf<Map<String, Any>>()
    val scan = WifiScanSession(
      read = { if (denied) throw SecurityException(); readings },
      startScan = { requests++; accepted },
      listen = { callback = it; listeners++; val cancel: () -> Unit = { listeners-- }; cancel },
      scheduleTimeout = { timeout = it; timers++; val cancel: () -> Unit = { timers-- }; cancel },
      complete = { results.add(it) }
    )
  }

  @Test fun waitsForCompletionInsteadOfReturningEmptyCache() {
    val f = Fixture()
    f.scan.start()
    assertTrue(f.results.isEmpty())
    assertEquals(1, f.requests)
    f.readings = listOf(observation)
    f.callback!!(true)
    assertEquals("available", f.results.single()["status"])
    assertEquals(listOf(observation), f.results.single()["observations"])
    assertEquals(0, f.listeners)
    assertEquals(0, f.timers)
  }

  @Test fun reusesFreshPlatformEvidenceWithoutRequestingAnotherScan() {
    val f = Fixture()
    f.readings = listOf(observation)
    f.scan.start()
    assertEquals("available", f.results.single()["status"])
    assertEquals(0, f.requests)
    assertEquals(0, f.listeners)
  }

  @Test fun timeoutResolvesOnceAndIgnoresLateBroadcasts() {
    val f = Fixture()
    f.scan.start()
    f.timeout!!()
    f.readings = listOf(observation)
    f.callback!!(true)
    f.scan.cancel()
    assertEquals("unavailable", f.results.single()["status"])
    assertEquals(emptyList<Any>(), f.results.single()["observations"])
    assertEquals(0, f.listeners)
    assertEquals(0, f.timers)
  }

  @Test fun throttledRequestCanUseLaterSystemScan() {
    val f = Fixture()
    f.accepted = false
    f.scan.start()
    f.callback!!(false)
    assertTrue(f.results.isEmpty())
    f.readings = listOf(observation)
    f.callback!!(true)
    assertEquals("available", f.results.single()["status"])
  }

  @Test fun permissionRevokedWhileWaitingCleansUp() {
    val f = Fixture()
    f.scan.start()
    f.denied = true
    f.callback!!(true)
    assertEquals("permission_denied", f.results.single()["status"])
    assertEquals(0, f.listeners)
    assertEquals(0, f.timers)
  }

  @Test fun permissionDeniedBeforeScanningMakesNoRequest() {
    val f = Fixture()
    f.denied = true
    f.scan.start()
    assertEquals("permission_denied", f.results.single()["status"])
    assertEquals(0, f.requests)
  }

  @Test fun cancellationRemovesListenerAndTimeout() {
    val f = Fixture()
    f.scan.start()
    f.scan.cancel()
    f.timeout!!()
    assertEquals("unavailable", f.results.single()["status"])
    assertEquals(0, f.listeners)
    assertEquals(0, f.timers)
  }

  @Test fun unsuccessfulBroadcastCannotReturnOldDataAsNew() {
    val f = Fixture()
    f.scan.start()
    f.readings = listOf(observation)
    f.callback!!(false)
    assertTrue(f.results.isEmpty())
    f.timeout!!()
    assertEquals("unavailable", f.results.single()["status"])
  }

  @Test fun filtersStaleFutureAndPlaceholderReadings() {
    val now = 30_000_000L
    val samples = listOf(
      WifiReading("AA:BB:CC:DD:EE:FF", -55, now-1),
      WifiReading("aa:bb:cc:dd:ee:ff", -65, now-2),
      WifiReading("aa:bb:cc:dd:ee:01", -40, now-15_000_001),
      WifiReading("aa:bb:cc:dd:ee:02", -40, now+1),
      WifiReading("00:00:00:00:00:00", -40, now),
      WifiReading("02:00:00:00:00:00", -40, now),
      WifiReading("ff:ff:ff:ff:ff:ff", -40, now),
      WifiReading("invalid", -40, now),
      WifiReading("aa:bb:cc:dd:ee:03", 42, now)
    )
    assertEquals(listOf(observation), freshReadings(samples, now))
  }

  @Test fun acceptsFreshnessBoundaryAndCapsStrongestAccessPoints() {
    val now = 30_000_000L
    val samples = (0..59).map {
      WifiReading("aa:bb:cc:dd:ee:%02x".format(it), -30-it, now-15_000_000)
    }
    val result = freshReadings(samples, now)
    assertEquals(50, result.size)
    assertEquals(-30, result.first()["rssi"])
    assertEquals(-79, result.last()["rssi"])
  }
}
