import * as Crypto from 'expo-crypto';
import {sha256} from '@noble/hashes/sha2.js';
import {bytesToHex} from '@noble/hashes/utils.js';
import {api,post,saveDevice} from '../api';
import {platformAdapter} from './index';
import {signEvidence} from '../protocol';
import type {DeviceCredential,Evidence} from '../contracts';
import type {SignedRequest} from './contracts';
// SPKI is public material. Avoid browser-only atob/Buffer assumptions in Hermes.
export function decodeBase64(text:string):Uint8Array{
 const alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
 const result:number[]=[];let bits=0,value=0;
 for(const char of text.replace(/=+$/,'')){const n=alphabet.indexOf(char);if(n<0)throw new Error('Invalid public key');value=(value<<6)|n;bits+=6;if(bits>=8){bits-=8;result.push((value>>bits)&255)}}
 return new Uint8Array(result);
}
export async function registerNativeDevice(userId:string,label:string,password:string){
 const adapter=platformAdapter(),native=adapter.security(),alias=Crypto.randomUUID();
 const key=await native.createKey(alias);
 const challenge=await post<{id:string;nonce:string}>('/devices/registration-challenge');
 const message=`SPVS-REGISTER-v1.${challenge.nonce}.${adapter.os}.${bytesToHex(sha256(decodeBase64(key.publicKey)))}`;
 const result=await post<{id:string}>('/devices',{label,password,platform:adapter.os,public_key:key.publicKey,
  key_storage:key.storage,registration_challenge_id:challenge.id,registration_signature:await native.sign(alias,message)});
 const device:DeviceCredential={id:result.id,keyAlias:alias,installationId:await native.installationId(),storage:key.storage};
 await saveDevice(userId,device);return device;
}
export async function registerAppAttest(userId:string,device:DeviceCredential){
 const native=platformAdapter().security();
 const capabilities=await api<{apple_app_attest:string}>('/attestation/capabilities');
 if(platformAdapter().os!=='ios'||!await native.attestationSupported())throw new Error('App Attest is unavailable on this device. Server policy still applies.');
 if(capabilities.apple_app_attest!=='configured')throw new Error('Your institution has not configured Apple App Attest.');
 const challenge=await post<{id:string;nonce:string}>('/attestation/challenge',{device_id:device.id});
 // Persist an unregistered key for transient network retry; only mark registered after server success.
 const keyId=device.attestationKeyId||await native.generateAttestationKey!();
 const updated={...device,attestationKeyId:keyId};await saveDevice(userId,updated);
 const object=await native.attestKey!(keyId,`SPVS-ATTEST-v1.${challenge.nonce}.${device.id}.${keyId}`);
 await post('/attestation/register',{device_id:device.id,challenge_id:challenge.id,key_id:keyId,attestation:object});
 await saveDevice(userId,{...updated,attestationRegistered:true});
}
export async function signNativeEvidence(evidence:Evidence,device:DeviceCredential,idempotencyKey:string):Promise<SignedRequest>{
 if(device.credential)return signEvidence(evidence,device.credential,idempotencyKey); // Existing installations only.
 const native=platformAdapter().security();
 if(!device.keyAlias||device.installationId!==await native.installationId())throw new Error('Device key was lost or the app was reinstalled. Request an administrator-approved device reset.');
 const payload=JSON.stringify(evidence),message=`${idempotencyKey}.${payload}`;
 const result:SignedRequest={payload,signature:await native.sign(device.keyAlias,message),idempotency_key:idempotencyKey};
 if(device.attestationRegistered&&device.attestationKeyId){
  result.attestation_key_id=device.attestationKeyId;
  result.attestation_assertion=await native.assertKey!(device.attestationKeyId,message);
 }
 return result;
}
