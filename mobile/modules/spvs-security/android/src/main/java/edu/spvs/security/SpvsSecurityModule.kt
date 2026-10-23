package edu.spvs.security

import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyInfo
import android.security.keystore.KeyProperties
import android.util.Base64
import java.security.KeyFactory
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.PrivateKey
import java.security.Signature
import java.security.spec.ECGenParameterSpec
import java.util.UUID
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

class SpvsSecurityModule : Module() {
  private fun alias(value: String): String {
    require(Regex("^[a-zA-Z0-9_-]{16,100}$").matches(value)) { "INVALID_KEY_ALIAS" }
    return "edu.spvs.device.$value"
  }
  private fun store() = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
  override fun definition() = ModuleDefinition {
    Name("SpvsSecurity")
    AsyncFunction("installationId") {
      val context = appContext.reactContext ?: error("NO_CONTEXT")
      val prefs = context.getSharedPreferences("spvs-installation", Context.MODE_PRIVATE)
      prefs.getString("id", null) ?: UUID.randomUUID().toString().also { prefs.edit().putString("id", it).commit() }
    }
    AsyncFunction("createKey") { identifier: String ->
      val name = alias(identifier)
      val ks = store()
      if (!ks.containsAlias(name)) {
        KeyPairGenerator.getInstance(KeyProperties.KEY_ALGORITHM_EC, "AndroidKeyStore").apply {
          initialize(KeyGenParameterSpec.Builder(name, KeyProperties.PURPOSE_SIGN)
            .setAlgorithmParameterSpec(ECGenParameterSpec("secp256r1"))
            .setDigests(KeyProperties.DIGEST_SHA256)
            .setUserAuthenticationRequired(false).build())
        }.generateKeyPair()
      }
      val privateKey = ks.getKey(name, null) as PrivateKey
      val info = KeyFactory.getInstance(privateKey.algorithm, "AndroidKeyStore").getKeySpec(privateKey, KeyInfo::class.java)
      @Suppress("DEPRECATION") val hardware = info.isInsideSecureHardware
      mapOf("publicKey" to Base64.encodeToString(ks.getCertificate(name).publicKey.encoded, Base64.NO_WRAP),
        "storage" to if (hardware) "android-hardware" else "android-keystore")
    }
    AsyncFunction("sign") { identifier: String, message: String ->
      val key = store().getKey(alias(identifier), null) as? PrivateKey ?: error("DEVICE_KEY_LOST_REQUEST_RESET")
      val signature = Signature.getInstance("SHA256withECDSA").apply { initSign(key); update(message.toByteArray(Charsets.UTF_8)) }.sign()
      Base64.encodeToString(signature, Base64.NO_WRAP)
    }
    AsyncFunction("attestationSupported") { false } // Play Integrity requires a configured provider adapter.
  }
}
