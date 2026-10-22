import {hmac} from '@noble/hashes/hmac.js';
import {sha256} from '@noble/hashes/sha2.js';
import {bytesToHex,utf8ToBytes} from '@noble/hashes/utils.js';
import type {Action,Evidence,Session} from './contracts';
export function signEvidence(evidence:Evidence,credential:string,key:string){
 const payload=JSON.stringify(evidence);
 return {payload,signature:bytesToHex(hmac(sha256,utf8ToBytes(credential),utf8ToBytes(`${key}.${payload}`))),idempotency_key:key};
}
export const instructions:Record<Action,string>={CENTER:'Look straight at the camera',TURN_LEFT:'Turn your head to your left',TURN_RIGHT:'Turn your head to your right',BLINK:'Slowly close your eyes, then open them'};
export function activeSession(s:Session,time=Date.now()){return !s.closed&&Date.parse(s.starts_at)<=time&&time<Date.parse(s.ends_at)}
export function decisionText(state:string){return ({PRESENT:'Your attendance is recorded.',PENDING_REVIEW:'Your evidence needs a faculty review. Attendance is not yet approved.',REQUIRES_RETRY:'Please correct the issue and try a fresh verification.',EXPIRED:'The session or challenge has expired.',REJECTED:'Verification did not meet the required checks.'} as Record<string,string>)[state]||'Check your attendance history for the result.'}
