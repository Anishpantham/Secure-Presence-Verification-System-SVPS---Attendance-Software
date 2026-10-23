import type {Evidence,WifiResult,DeviceCredential} from '../contracts';
export type NativeKey={publicKey:string;storage:'secure-enclave'|'keychain'|'android-keystore'|'android-hardware'};
export type NativeSecurity={
 installationId:()=>Promise<string>;
 createKey:(alias:string)=>Promise<NativeKey>;
 sign:(alias:string,message:string)=>Promise<string>;
 accuracyAuthorization?:()=>Promise<'full'|'reduced'>;
 attestationSupported:()=>Promise<boolean>;
 generateAttestationKey?:()=>Promise<string>;
 attestKey?:(id:string,message:string)=>Promise<string>;
 assertKey?:(id:string,message:string)=>Promise<string>;
};
export type SignedRequest={payload:string;signature:string;idempotency_key:string;attestation_key_id?:string;attestation_assertion?:string};
export type PlatformAdapter={
 os:'android'|'ios';
 wifi:()=>Promise<WifiResult>;
 security:()=>NativeSecurity;
};
export type EvidenceSigner=(evidence:Evidence,device:DeviceCredential,key:string)=>Promise<SignedRequest>;
