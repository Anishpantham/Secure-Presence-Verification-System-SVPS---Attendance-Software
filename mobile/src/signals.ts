import * as Location from 'expo-location';
import {platformAdapter} from './platform';
import type {LocationEvidence} from './contracts';
export async function collectLocation():Promise<LocationEvidence>{
 const permission=await Location.requestForegroundPermissionsAsync();
 if(permission.status!=='granted')throw new Error('Location permission is required. Enable it in system settings and retry.');
 if(!await Location.hasServicesEnabledAsync())throw new Error('Turn on location services to verify presence.');
 const adapter=platformAdapter();
 const authorization=adapter.os==='ios'?await adapter.security().accuracyAuthorization!():permission.android?.accuracy==='coarse'?'reduced':'full';
 if(authorization==='reduced')throw new Error('Enable Precise Location for SPVS in Settings, then retry. Approximate location cannot verify classroom presence.');
 const fix=await Location.getCurrentPositionAsync({accuracy:Location.Accuracy.High});
 if(fix.coords.accuracy===null||fix.coords.accuracy<0)throw new Error('GPS accuracy is unavailable. Try again outdoors or near a window.');
 if(Date.now()-fix.timestamp>20000||fix.timestamp-Date.now()>3000)throw new Error('Location is stale. Retry with a fresh location fix.');
 return {latitude:fix.coords.latitude,longitude:fix.coords.longitude,accuracy_m:fix.coords.accuracy,
  captured_at:new Date(fix.timestamp).toISOString(),mocked:fix.mocked??false,accuracy_authorization:authorization};
}
export const collectWifi=()=>platformAdapter().wifi();
