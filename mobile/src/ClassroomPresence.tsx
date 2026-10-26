import React,{useEffect,useRef,useState} from 'react';
import {ActivityIndicator,AppState,Button,Linking,ScrollView,Text,View} from 'react-native';
import {CameraView,useCameraPermissions} from 'expo-camera';
import * as Crypto from 'expo-crypto';
import {getDevice,post} from './api';
import {signNativeEvidence} from './platform/device';
import {listen} from './acoustic';
import type {Attempt,Challenge,DeviceCredential} from './contracts';
import type {SignedRequest} from './platform/contracts';

type Props={userId:string;sessionId:string;onReady:(challenge:Challenge)=>void;onReview:(attempt:Attempt)=>void};
export function ClassroomPresence({userId,sessionId,onReady,onReview}:Props){
 const [permission,requestPermission]=useCameraPermissions(),[challenge,setChallenge]=useState<Challenge|null>(null),[phase,setPhase]=useState('Preparing attempt'),[error,setError]=useState(''),[qr,setQr]=useState(false),[busy,setBusy]=useState(false),[torch,setTorch]=useState(false);
 const device=useRef<DeviceCredential|null>(null),stop=useRef<(()=>Promise<void>)|null>(null),scanLock=useRef(false),active=useRef(true),timer=useRef<ReturnType<typeof setTimeout>|null>(null),pending=useRef<SignedRequest|null>(null),interrupted=useRef(false),operation=useRef(false);
 async function cleanup(){if(timer.current)clearTimeout(timer.current);timer.current=null;await stop.current?.();stop.current=null}
 useEffect(()=>{active.current=true;void (async()=>{try{device.current=await getDevice(userId);if(!device.current)throw new Error('Register this phone first.');const c=await post<Challenge>('/challenges',{device_id:device.current.id,purpose:'attendance',session_id:sessionId});if(active.current){setChallenge({...c,clockOffset:Date.parse(c.server_time)-Date.now()});setPhase('Scan the classroom QR')}}catch(e){if(active.current)setError(String(e))}})();
  const listener=AppState.addEventListener('change',state=>{if(state==='background'){interrupted.current=true;void cleanup();setError('INTERRUPTED · Request review, then start a fresh attempt.');setPhase('Capture interrupted');setBusy(false)}});
  return()=>{active.current=false;listener.remove();void cleanup()};
 },[userId,sessionId]);
 async function signed(action:string,extra:Record<string,unknown>={}){if(!challenge||!device.current)throw new Error('Attempt not ready');return signNativeEvidence({challenge_id:challenge.id,device_id:device.current.id,action,...extra},device.current,Crypto.randomUUID())}
 async function scan(token:string){if(scanLock.current||qr||!challenge||interrupted.current)return;scanLock.current=true;setBusy(true);try{
  if(!token.startsWith('SPVS1.'))throw new Error('Scan the SPVS code displayed by your faculty.');
  await post('/presence/evidence',await signed('qr',{token}));if(active.current&&!interrupted.current){setQr(true);setPhase('QR verified · ready for sound');setError('')}
 }catch(e){if(active.current)setError(`${String(e)} · Hold steady, improve lighting, or scan the next code.`)}finally{if(active.current)setBusy(false);setTimeout(()=>{scanLock.current=false},1500)}}
 async function accept(body:SignedRequest){await post('/presence/evidence',body);pending.current=null;await cleanup();if(active.current&&!interrupted.current)onReady(challenge!)}
 async function capture(){if(operation.current||!challenge||interrupted.current)return;operation.current=true;setBusy(true);setError('');setPhase('Requesting microphone access');try{
  stop.current=await listen(challenge.id,async response=>{if(!active.current||interrupted.current)return;try{setPhase('Verifying decoded sound');pending.current=await signed('audio',{response});await accept(pending.current)}catch(e){await cleanup();if(active.current){setError(String(e));setPhase('Audio not verified');setBusy(false)}}},e=>{void cleanup();if(active.current){setError(e.message);setBusy(false)}});
  if(!active.current||interrupted.current){await cleanup();return}
  await post('/presence/evidence',await signed('ready'));if(!active.current||interrupted.current){await cleanup();return}setPhase(`Listening · ask faculty to play attempt ${challenge.id.slice(0,8)}`);
  timer.current=setTimeout(()=>{void cleanup();if(active.current){setError('AUDIO_DECODE_FAILED · No matching sound was verified. Request review or finish this attempt before retrying.');setBusy(false);setPhase('Listening timed out')}},28000);
 }catch(e){await cleanup();if(active.current){setError(String(e));setBusy(false)}}finally{operation.current=false}}
 async function review(){if(operation.current||!challenge)return;operation.current=true;setBusy(true);try{await cleanup();const reason=interrupted.current?'INTERRUPTED':!permission?.granted?'CAMERA_PERMISSION':error.includes('MICROPHONE_PERMISSION')?'MICROPHONE_PERMISSION':qr?'AUDIO_DECODE_FAILED':'QR_UNAVAILABLE';const result=await post<Attempt>('/presence/evidence',await signed('failure',{reason}));if(active.current)onReview(result)}catch(e){if(active.current)setError(String(e))}finally{operation.current=false;if(active.current)setBusy(false)}}
 return <ScrollView contentContainerStyle={{padding:24,gap:18}}><Text accessibilityRole="header" style={{fontSize:24}}>Classroom presence</Text><Text accessibilityLiveRegion="polite">{phase}</Text>
 <Text>Scan the current QR, then listen to a short audible signal. Microphone samples stay in memory on this phone and are discarded. Face and location checks follow.</Text>
 {!permission?.granted?<><Button title="Allow camera" onPress={()=>void requestPermission()}/><Button title="Open permissions" onPress={()=>void Linking.openSettings()}/></>:!qr&&!interrupted.current&&<><View style={{height:320}}><CameraView style={{flex:1}} facing="back" enableTorch={torch} barcodeScannerSettings={{barcodeTypes:['qr']}} onBarcodeScanned={busy?undefined:({data})=>void scan(data)} onMountError={e=>setError(e.message)}/></View><Button title={torch?'Turn torch off':'Improve lighting with torch'} onPress={()=>setTorch(!torch)}/></>}
 {busy&&qr&&<Button title="Stop listening" onPress={()=>{interrupted.current=true;void cleanup();setBusy(false);setPhase('Listening stopped');setError('INTERRUPTED · Finish this attempt for faculty review before retrying.')}}/>}
 {error&&<Text accessibilityRole="alert">{error}</Text>}{busy&&<ActivityIndicator/>}
 {qr&&<Button title="Listen for classroom sound" disabled={busy||interrupted.current} onPress={()=>void capture()}/>}
 {pending.current&&!busy&&!interrupted.current&&<Button title="Retry same decoded response" onPress={async()=>{if(operation.current)return;operation.current=true;setBusy(true);try{await accept(pending.current!)}catch(e){setError(String(e))}finally{operation.current=false;setBusy(false)}}}/>}
 <Text>Use your phone microphone, keep the app open, and disconnect Bluetooth headphones. The faculty plays one waiting attempt at a time. If audio is inaccessible or permissions are unavailable, request faculty review; attendance is not automatically approved.</Text>
 <Button title="Finish attempt & request faculty review" disabled={!challenge||busy} onPress={()=>void review()}/>
 </ScrollView>
}
