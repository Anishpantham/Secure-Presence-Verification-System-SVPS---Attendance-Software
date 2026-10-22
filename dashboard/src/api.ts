export type User={id:string;name:string;email:string;role:'admin'|'faculty'|'student';active:boolean};
export type Row={id:string;[key:string]:any};
export type Tokens={access_token:string;refresh_token:string;user?:User};
// Tokens live only in memory. Reloading the dashboard requires login; no localStorage credentials.
let tokens:Tokens|null=null;
let refreshing:Promise<void>|null=null;
export function setTokens(value:Tokens|null){tokens=value;}
export async function api<T=Row[]>(path:string, options:RequestInit={}, retry=true):Promise<T>{
  const response=await fetch(`/api/v1${path}`,{...options,headers:{'Content-Type':'application/json',...(tokens?{Authorization:`Bearer ${tokens.access_token}`} : {}),...options.headers}});
  if(response.status===401 && retry && tokens && path!='/auth/login'){
    if(!refreshing) refreshing=(async()=>{
      const r=await fetch('/api/v1/auth/refresh',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh_token:tokens!.refresh_token})});
      if(!r.ok){tokens=null;window.dispatchEvent(new Event('spvs-logout'));throw new Error('Your session expired. Please sign in again.');}
      tokens=await r.json();
    })().finally(()=>{refreshing=null;});
    await refreshing;return api(path,options,false);
  }
  if(!response.ok){const body=await response.json().catch(()=>({}));throw new Error(body.error?.message||`Request failed (${response.status})`);}
  if(response.status===204)return undefined as T;
  if(response.headers.get('content-type')?.includes('text/csv'))return await response.text() as T;
  return response.json();
}
export const post=<T=Row>(path:string,data:unknown={})=>api<T>(path,{method:'POST',body:JSON.stringify(data)});
export async function logout(){if(tokens)await post('/auth/logout',{refresh_token:tokens.refresh_token}).catch(()=>{});tokens=null;}
export async function downloadReport(sessionId?:string){
  const csv=await api<string>('/reports/attendance.csv'+(sessionId?`?session_id=${sessionId}`:''));
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
  const a=document.createElement('a');a.href=url;a.download='spvs-attendance.csv';a.click();URL.revokeObjectURL(url);
}
