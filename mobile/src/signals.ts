import {Platform,PermissionsAndroid} from 'react-native';
import * as Location from 'expo-location';
import {requireOptionalNativeModule} from 'expo-modules-core';
import type {LocationEvidence,WifiResult} from './contracts';

export async function collectLocation():Promise<LocationEvidence>{
 const permission=await Location.requestForegroundPermissionsAsync();
 if(permission.status!=='granted')throw new Error('Location permission is required. Enable it in system settings and retry.');
 if(!await Location.hasServicesEnabledAsync())throw new Error('Turn on location services to verify presence.');
 const fix=await Location.getCurrentPositionAsync({accuracy:Location.Accuracy.High});
 if(fix.coords.accuracy===null)throw new Error('GPS accuracy is unavailable. Try again outdoors or near a window.');
 return {latitude:fix.coords.latitude,longitude:fix.coords.longitude,accuracy_m:fix.coords.accuracy,captured_at:new Date(fix.timestamp).toISOString(),mocked:fix.mocked??false};
}
export async function collectWifi():Promise<WifiResult>{
 if(Platform.OS!=='android')return {status:'unsupported',observations:[]};
 const module=requireOptionalNativeModule<{scan:()=>Promise<WifiResult>}>('SpvsWifi');
 if(!module)return {status:'unsupported',observations:[]};
 const permission=await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION);
 if(permission!==PermissionsAndroid.RESULTS.GRANTED)return {status:'permission_denied',observations:[]};
 try{return await module.scan()}catch{return {status:'unavailable',observations:[]}}
}
