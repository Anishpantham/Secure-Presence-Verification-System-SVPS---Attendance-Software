import {defaultApiUrl} from './platform';
import * as SecureStore from 'expo-secure-store';
import type {DeviceCredential,User} from './contracts';
import {ApiError,requestErrorMessage,retryAfterSeconds} from './apiErrors';
const BASE=process.env.EXPO_PUBLIC_API_URL||defaultApiUrl();
if(!__DEV__&&!BASE.startsWith('https://'))throw new Error('Release builds require an HTTPS API endpoint');
type Tokens={access_token:string;refresh_token:string};
let tokens:Tokens|null=null;
let refreshPromise:Promise<void>|null=null;
export async function restore(){const saved=await SecureStore.getItemAsync('spvs.tokens');tokens=saved?JSON.parse(saved):null;return !!tokens}
async function save(value:Tokens){tokens=value;await SecureStore.setItemAsync('spvs.tokens',JSON.stringify(value),{keychainAccessible:SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY})}
export async function api<T>(path:string,options:RequestInit={},retry=true):Promise<T>{
 const response=await fetch(BASE+path,{...options,headers:{'Content-Type':'application/json',...(tokens?{Authorization:`Bearer ${tokens.access_token}`}:{})}});
 if(response.status===401&&tokens&&retry&&path!='/auth/login'){
  if(!refreshPromise)refreshPromise=(async()=>{const r=await fetch(BASE+'/auth/refresh',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh_token:tokens!.refresh_token})});if(!r.ok){await signOut();throw new Error('Session expired. Sign in again.')}await save(await r.json())})().finally(()=>{refreshPromise=null});
  await refreshPromise;return api(path,options,false);
 }
 if(!response.ok){const body=await response.json().catch(()=>({}));throw new ApiError(requestErrorMessage(path,response.status,body.error?.message||`Request failed (${response.status})`,body.error?.fields),response.status,retryAfterSeconds(response.headers.get('Retry-After')),body.error?.details)}
 if(response.status===204)return undefined as T;return response.json();
}
export const post=<T>(path:string,data:unknown={})=>api<T>(path,{method:'POST',body:JSON.stringify(data)});
export async function signIn(email:string,password:string){email=email.trim();if(/\s/.test(email))throw new Error('Enter an email address without spaces.');const result=await post<Tokens&{user:User}>('/auth/login',{email,password});if(result.user.role!=='student')throw new Error('Faculty and administrators use the web dashboard.');await save(result);return result.user}
export async function signOut(){const old=tokens;tokens=null;await SecureStore.deleteItemAsync('spvs.tokens');if(old)await fetch(BASE+'/auth/logout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh_token:old.refresh_token})}).catch(()=>{})}
// Per-user keys prevent an account switch on a shared phone from reusing another student's credential.
export async function getDevice(userId:string):Promise<DeviceCredential|null>{const value=await SecureStore.getItemAsync(`spvs.device.${userId}`);return value?JSON.parse(value):null}
export async function saveDevice(userId:string,value:DeviceCredential){await SecureStore.setItemAsync(`spvs.device.${userId}`,JSON.stringify(value),{keychainAccessible:SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY})}
