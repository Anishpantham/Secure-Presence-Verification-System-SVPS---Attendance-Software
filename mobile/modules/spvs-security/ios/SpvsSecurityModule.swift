import ExpoModulesCore
import Security
import DeviceCheck
import CryptoKit
import CoreLocation

public class SpvsSecurityModule: Module {
  private func failure(_ message: String) -> NSError {
    NSError(domain: "SPVS", code: 1, userInfo: [NSLocalizedDescriptionKey: message])
  }
  private func tag(_ identifier: String) throws -> Data {
    guard identifier.range(of: "^[a-zA-Z0-9_-]{16,100}$", options: .regularExpression) != nil else { throw failure("INVALID_KEY_ALIAS") }
    return Data("edu.spvs.device.\(identifier)".utf8)
  }
  private func lookup(_ identifier: String) throws -> SecKey? {
    let query: [CFString: Any] = [kSecClass: kSecClassKey, kSecAttrApplicationTag: try tag(identifier),
                                kSecAttrKeyType: kSecAttrKeyTypeECSECPrimeRandom, kSecReturnRef: true]
    var result: CFTypeRef?
    let status = SecItemCopyMatching(query as CFDictionary, &result)
    if status == errSecItemNotFound { return nil }
    guard status == errSecSuccess, let result else { throw failure("KEYCHAIN_UNAVAILABLE_\(status)") }
    return (result as! SecKey)
  }
  private func makeKey(_ identifier: String, enclave: Bool) throws -> SecKey {
    var error: Unmanaged<CFError>?
    guard let access = SecAccessControlCreateWithFlags(nil, kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
                                                      enclave ? .privateKeyUsage : [], &error) else {
      throw error!.takeRetainedValue() as Error
    }
    var attributes: [CFString: Any] = [kSecAttrKeyType: kSecAttrKeyTypeECSECPrimeRandom, kSecAttrKeySizeInBits: 256,
      kSecPrivateKeyAttrs: [kSecAttrIsPermanent: true, kSecAttrApplicationTag: try tag(identifier), kSecAttrAccessControl: access]]
    if enclave { attributes[kSecAttrTokenID] = kSecAttrTokenIDSecureEnclave }
    guard let key = SecKeyCreateRandomKey(attributes as CFDictionary, &error) else { throw error!.takeRetainedValue() as Error }
    return key
  }
  public func definition() -> ModuleDefinition {
    Name("SpvsSecurity")
    AsyncFunction("installationId") { () -> String in
      let defaults = UserDefaults.standard
      if let identifier = defaults.string(forKey: "spvs.installation") { return identifier }
      let identifier = UUID().uuidString
      defaults.set(identifier, forKey: "spvs.installation")
      return identifier
    }
    AsyncFunction("createKey") { (identifier: String) -> [String: String] in
      let key: SecKey
      if let existing = try self.lookup(identifier) { key = existing }
      else {
        #if targetEnvironment(simulator)
        key = try self.makeKey(identifier, enclave: false)
        #else
        // Physical-device failures are surfaced; no silent downgrade from Secure Enclave.
        key = try self.makeKey(identifier, enclave: true)
        #endif
      }
      var error: Unmanaged<CFError>?
      guard let pub = SecKeyCopyPublicKey(key), let raw = SecKeyCopyExternalRepresentation(pub, &error) as Data? else { throw self.failure("PUBLIC_KEY_UNAVAILABLE") }
      // SecKey exports ANSI X9.63; server accepts canonical P-256 SubjectPublicKeyInfo.
      let prefix: [UInt8] = [0x30,0x59,0x30,0x13,0x06,0x07,0x2a,0x86,0x48,0xce,0x3d,0x02,0x01,0x06,0x08,0x2a,0x86,0x48,0xce,0x3d,0x03,0x01,0x07,0x03,0x42,0x00]
      let attrs = SecKeyCopyAttributes(key) as NSDictionary?
      let enclave = (attrs?[kSecAttrTokenID] as? String) == (kSecAttrTokenIDSecureEnclave as String)
      return ["publicKey": (Data(prefix) + raw).base64EncodedString(), "storage": enclave ? "secure-enclave" : "keychain"]
    }
    AsyncFunction("sign") { (identifier: String, message: String) -> String in
      guard let key = try self.lookup(identifier) else { throw self.failure("DEVICE_KEY_LOST_REQUEST_RESET") }
      var error: Unmanaged<CFError>?
      guard let signature = SecKeyCreateSignature(key, .ecdsaSignatureMessageX962SHA256, Data(message.utf8) as CFData, &error) as Data? else { throw error!.takeRetainedValue() as Error }
      return signature.base64EncodedString()
    }
    AsyncFunction("accuracyAuthorization") { () -> String in
      CLLocationManager().accuracyAuthorization == .fullAccuracy ? "full" : "reduced"
    }.runOnQueue(.main)
    AsyncFunction("attestationSupported") { DCAppAttestService.shared.isSupported }
    AsyncFunction("generateAttestationKey") { (promise: Promise) in
      guard DCAppAttestService.shared.isSupported else { promise.reject("APP_ATTEST_UNSUPPORTED", "App Attest requires a supported physical Apple device"); return }
      DCAppAttestService.shared.generateKey { identifier, error in
        if let error { promise.reject(error) } else if let identifier { promise.resolve(identifier) }
        else { promise.reject("APP_ATTEST_FAILED", "No key returned") }
      }
    }
    AsyncFunction("attestKey") { (identifier: String, message: String, promise: Promise) in
      DCAppAttestService.shared.attestKey(identifier, clientDataHash: Data(SHA256.hash(data: Data(message.utf8)))) { object, error in
        if let error { promise.reject(error) } else if let object { promise.resolve(object.base64EncodedString()) }
        else { promise.reject("APP_ATTEST_FAILED", "No attestation returned") }
      }
    }
    AsyncFunction("assertKey") { (identifier: String, message: String, promise: Promise) in
      DCAppAttestService.shared.generateAssertion(identifier, clientDataHash: Data(SHA256.hash(data: Data(message.utf8)))) { assertion, error in
        if let error { promise.reject(error) } else if let assertion { promise.resolve(assertion.base64EncodedString()) }
        else { promise.reject("APP_ATTEST_FAILED", "No assertion returned") }
      }
    }
  }
}
