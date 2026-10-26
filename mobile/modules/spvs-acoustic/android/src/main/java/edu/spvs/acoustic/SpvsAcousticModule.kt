package edu.spvs.acoustic

import android.Manifest
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import java.util.concurrent.atomic.AtomicBoolean

/** Foreground, bounded PCM capture only. No file or network access. */
class SpvsAcousticModule : Module() {
  private val running = AtomicBoolean(false)
  private var worker: Thread? = null
  override fun definition() = ModuleDefinition {
    Name("SpvsAcoustic")
    Events("pcm", "captureError")
    AsyncFunction("start") {
      val context = appContext.reactContext ?: error("AUDIO_CONTEXT_UNAVAILABLE")
      if (context.checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED)
        error("MICROPHONE_PERMISSION")
      if (worker?.isAlive == true) error("AUDIO_ALREADY_RUNNING")
      if (!running.compareAndSet(false, true)) error("AUDIO_ALREADY_RUNNING")
      val size = AudioRecord.getMinBufferSize(16000, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT)
      if (size <= 0) { running.set(false); error("AUDIO_UNAVAILABLE") }
      val recorder = try { AudioRecord(MediaRecorder.AudioSource.VOICE_RECOGNITION, 16000,
        AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_16BIT, maxOf(size, 8192)) }
        catch (e: Exception) { running.set(false); throw e }
      try {
        check(recorder.state == AudioRecord.STATE_INITIALIZED) { "AUDIO_UNAVAILABLE" }
        recorder.startRecording()
        check(recorder.recordingState == AudioRecord.RECORDSTATE_RECORDING) { "AUDIO_UNAVAILABLE" }
      } catch (e: Exception) { recorder.release(); running.set(false); throw e }
      worker = Thread {
        val buffer = ShortArray(1600)
        val deadline = System.nanoTime() + 30_000_000_000L
        try {
          while (running.get() && System.nanoTime() < deadline) {
            val count = recorder.read(buffer, 0, buffer.size)
            if (count <= 0) error("AUDIO_CAPTURE_FAILED")
            sendEvent("pcm", mapOf("samples" to buffer.take(count).map { it.toDouble() / 32768.0 }, "sampleRate" to 16000))
          }
        } catch (e: Exception) { sendEvent("captureError", mapOf("reason" to "AUDIO_CAPTURE_FAILED")) }
        finally { buffer.fill(0); recorder.stop(); recorder.release(); running.set(false) }
      }.also { it.start() }
    }
    AsyncFunction("stop") { running.set(false); worker?.join(500); if (worker?.isAlive != true) worker = null }
    OnActivityEntersBackground { running.set(false) }
    OnDestroy { running.set(false) }
  }
}
