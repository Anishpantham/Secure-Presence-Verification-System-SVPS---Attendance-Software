import {PermissionsAndroid,Platform} from 'react-native';
import {requireNativeModule} from 'expo-modules-core';
import {AcousticStream} from './acousticCodec';

type NativeCapture={start:()=>Promise<void>;stop:()=>Promise<void>;requestPermission?:()=>Promise<boolean>;addListener:(event:string,fn:(event:any)=>void)=>{remove:()=>void}};
export async function listen(attemptId:string,onDecoded:(payload:string)=>void,onError:(error:Error)=>void){
 const native=requireNativeModule<NativeCapture>('SpvsAcoustic');
 const allowed=Platform.OS==='android'?await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.RECORD_AUDIO)===PermissionsAndroid.RESULTS.GRANTED:await native.requestPermission?.();
 if(!allowed)throw new Error('MICROPHONE_PERMISSION');
 const decoder=new AcousticStream();let stopped=false;
 const subscription=native.addListener('pcm',(event:{samples:number[];sampleRate:number})=>{if(stopped)return;const value=decoder.push(event.samples,event.sampleRate);if(value?.startsWith(attemptId.replaceAll('-','').slice(0,8))){stopped=true;onDecoded(value)}});
 const errors=native.addListener('captureError',()=>onError(new Error('AUDIO_UNAVAILABLE')));
 async function stop(){stopped=true;subscription.remove();errors.remove();decoder.clear();await native.stop()}
 try{await native.start()}catch(error){await stop();throw error}
 return stop;
}
