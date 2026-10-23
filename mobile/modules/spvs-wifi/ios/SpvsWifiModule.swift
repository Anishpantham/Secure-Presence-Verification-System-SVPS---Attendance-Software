import ExpoModulesCore
import NetworkExtension

public class SpvsWifiModule: Module {
  public func definition() -> ModuleDefinition {
    Name("SpvsWifi")
    AsyncFunction("currentNetwork") { (promise: Promise) in
      // Requires Access Wi-Fi Information entitlement and Apple's privacy conditions.
      // iOS does not expose nearby AP scanning or RSSI here. Never synthesize either.
      NEHotspotNetwork.fetchCurrent { network in
        guard let network, network.bssid != "00:00:00:00:00:00", network.bssid != "02:00:00:00:00:00" else {
          promise.resolve(["status": "unavailable", "source": "none", "observations": []] as [String: Any]); return
        }
        promise.resolve(["status": "available", "source": "current_network", "currentBssid": network.bssid.lowercased(), "observations": []] as [String: Any])
      }
    }
  }
}
