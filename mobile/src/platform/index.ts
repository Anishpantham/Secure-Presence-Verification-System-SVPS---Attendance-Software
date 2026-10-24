import {PermissionsAndroid,Platform} from 'react-native';
import {requireOptionalNativeModule} from 'expo-modules-core';
import type {WifiResult} from '../contracts';
import type {NativeSecurity,PlatformAdapter} from './contracts';
const unavailable:WifiResult={status:'unavailable',source:'none',observations:[]};
const security=()=>{
 const module=requireOptionalNativeModule<NativeSecurity>('SpvsSecurity');
 if(!module)throw new Error('Install the SPVS development build. Expo Go cannot provide secure device keys.');
 return module;
};
const adapters:Record<string,PlatformAdapter>={
 android:{os:'android',security,wifi:async()=>{
  const module=requireOptionalNativeModule<{scan:()=>Promise<WifiResult>}>('SpvsWifi');
  if(!module)return {...unavailable,status:'unsupported'};
  const permissions=await PermissionsAndroid.requestMultiple([
   PermissionsAndroid.PERMISSIONS.ACCESS_COARSE_LOCATION,PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
  ]);
  if(permissions[PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION]!==PermissionsAndroid.RESULTS.GRANTED)return {...unavailable,status:'permission_denied'};
  try{const result=await module.scan();return {...result,source:result.status==='available'?'scan':'none'}}catch{return unavailable}
 }},
 ios:{os:'ios',security,wifi:async()=>{
  const module=requireOptionalNativeModule<{currentNetwork:()=>Promise<WifiResult>}>('SpvsWifi');
  if(!module)return {...unavailable,status:'unsupported'};
  try{return await module.currentNetwork()}catch{return unavailable}
 }},
};
export function platformAdapter():PlatformAdapter{
 const adapter=adapters[Platform.OS];
 if(!adapter)throw new Error('SPVS attendance requires the Android or iOS application.');
 return adapter;
}
export function defaultApiUrl(){return Platform.OS==='ios'?'http://localhost:8000/api/v1':'http://10.0.2.2:8000/api/v1'}
