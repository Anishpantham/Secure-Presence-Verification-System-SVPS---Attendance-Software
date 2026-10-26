import ExpoModulesCore
import AVFoundation

public class SpvsAcousticModule: Module {
  private var engine: AVAudioEngine?
  private var timeout: DispatchWorkItem?
  public func definition() -> ModuleDefinition {
    Name("SpvsAcoustic")
    Events("pcm", "captureError")
    AsyncFunction("requestPermission") { (promise: Promise) in
      AVAudioSession.sharedInstance().requestRecordPermission { allowed in promise.resolve(allowed) }
    }
    AsyncFunction("start") { () throws in
      guard self.engine == nil else { throw NSError(domain: "AUDIO_ALREADY_RUNNING", code: 1) }
      let session = AVAudioSession.sharedInstance()
      guard session.recordPermission == .granted else { throw NSError(domain: "MICROPHONE_PERMISSION", code: 1) }
      do {
        try session.setCategory(.record, mode: .measurement, options: [])
        try session.setActive(true)
        let engine = AVAudioEngine(), input = engine.inputNode
        let format = input.outputFormat(forBus: 0)
        guard format.sampleRate >= 8000, format.channelCount > 0 else { throw NSError(domain: "AUDIO_UNAVAILABLE", code: 1) }
        self.engine = engine
        // Keep PCM ephemeral; use an integer stride and report the exact resulting rate.
        let strideBy = max(1, Int(format.sampleRate / 16000))
        input.installTap(onBus: 0, bufferSize: 4096, format: format) { [weak self] buffer, _ in
          guard let channel = buffer.floatChannelData?[0] else { return }
          let samples = stride(from: 0, to: Int(buffer.frameLength), by: strideBy).map { Double(channel[$0]) }
          self?.sendEvent("pcm", ["samples": samples, "sampleRate": format.sampleRate / Double(strideBy)])
        }
        try engine.start()
        let timeout = DispatchWorkItem { [weak self] in self?.stopCapture() }
        self.timeout = timeout
        DispatchQueue.main.asyncAfter(deadline: .now() + 30, execute: timeout)
      } catch { self.stopCapture(); throw error }
    }.runOnQueue(.main)
    AsyncFunction("stop") { self.stopCapture() }.runOnQueue(.main)
    OnAppEntersBackground { self.stopCapture() }
    OnDestroy { self.stopCapture() }
  }
  private func stopCapture() {
    timeout?.cancel(); timeout = nil
    if let engine = engine { engine.stop(); engine.inputNode.removeTap(onBus: 0) }
    engine = nil
    try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
  }
}
