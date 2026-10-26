import {useEffect,useRef,useState} from 'react';
import QRCode from 'qrcode';
import {api,post} from './api';
import {encode} from '../../mobile/src/acousticCodec';

type Display={enabled:boolean;server_time:string;ends_at:string;token?:string;rotate_at?:string;expires_at?:string;queue:{attempt_id:string;label:string}[]};
export function ClassroomChallenges({sessionId}:{sessionId:string}){
 const [display,setDisplay]=useState<Display|null>(null),[error,setError]=useState(''),[image,setImage]=useState(''),[clock,setClock]=useState(Date.now()),[status,setStatus]=useState('Audio idle'),[busy,setBusy]=useState(false);
 const offset=useRef(0),audio=useRef<AudioContext|null>(null),mounted=useRef(true),playing=useRef(false);
 useEffect(()=>{mounted.current=true;let cancelled=false;let timer:ReturnType<typeof setTimeout>;
  async function poll(){try{const start=Date.now();const next=await api<Display>(`/sessions/${sessionId}/presence/display`);if(cancelled)return;
   // Conservative estimate includes the full round trip; stale QR is hidden early.
   offset.current=Date.parse(next.server_time)-start;setDisplay(next);setError('');
   if(next.token)setImage(await QRCode.toDataURL(next.token,{width:360,margin:4,errorCorrectionLevel:'M'}));else setImage('');
  }catch(e){if(!cancelled){setError(String(e));setDisplay(null);setImage('')}}finally{if(!cancelled)timer=setTimeout(poll,1000)}}
  void poll();const tick=setInterval(()=>setClock(Date.now()),100);
  return()=>{cancelled=true;mounted.current=false;clearTimeout(timer);clearInterval(tick);void audio.current?.close();audio.current=null};
 },[sessionId]);
 async function control(enabled:boolean){setBusy(true);try{await post(`/sessions/${sessionId}/presence/control`,{enabled});if(!enabled){setDisplay(null);setImage('');void audio.current?.suspend();setStatus('Playback stopped')}}catch(e){setError(String(e))}finally{setBusy(false)}}
 async function play(id:string){if(playing.current)return;playing.current=true;setBusy(true);setError('');try{
  audio.current??=new AudioContext();await audio.current.resume();if(audio.current.state!=='running')throw new Error('Enable browser audio and try again.');
  setStatus('Requesting fresh challenge…');const start=Date.now();
  const signal=await post<{payload:string;server_time:string;expires_at:string}>(`/sessions/${sessionId}/presence/play/${id}`);
  if(!mounted.current)return;
  if(Date.now()-start>1200)throw new Error('Network too slow for playback. Ask the student to retry.');
  const pcm=encode(signal.payload,audio.current.sampleRate),buffer=audio.current.createBuffer(1,pcm.length,audio.current.sampleRate);buffer.copyToChannel(pcm,0);
  const source=audio.current.createBufferSource();source.buffer=buffer;source.connect(audio.current.destination);source.start();setStatus(`Playing audible challenge for ${id.slice(0,8)} · 2.7 seconds`);
  await new Promise<void>(resolve=>{source.onended=()=>resolve()});setStatus('Playback complete · awaiting server verification');
 }catch(e){setError(String(e));setStatus('Playback failed · student must retry')}finally{playing.current=false;if(mounted.current)setBusy(false)}}
 const remaining=display?.rotate_at?Math.max(0,(Date.parse(display.rotate_at)-clock-offset.current)/1000):0;
 return <section className="panel" aria-label="Classroom challenges"><h2>Classroom QR & audio</h2><p>Students scan the code, then tap Listen. Play the matching attempt below. Keep laptop speakers audible.</p>
 <div className="button-group"><button disabled={busy||!!display?.enabled} onClick={()=>void control(true)}>Start challenges</button><button className="secondary" disabled={busy||!display?.enabled} onClick={()=>void control(false)}>Stop challenges</button></div>
 <p role="status">{display?.enabled?'Session active':'Challenges stopped, unavailable, or session expired'} · {status}</p>
 {error&&<p role="alert">{error}</p>}
 {display?.enabled&&image&&remaining>0?<><img src={image} width="300" height="300" alt="Scan this rotating attendance QR code"/><p>New code in {remaining.toFixed(1)} seconds · valid for at most 10 seconds</p></>:display?.enabled&&<p>Refreshing code…</p>}
 <h3>Phones ready to listen</h3>{display?.queue.length===0&&<p>No phones waiting. Students should scan and tap Listen.</p>}
 {display?.queue.map(p=><div key={p.attempt_id}><span>Attempt {p.label} </span><button disabled={busy} onClick={()=>void play(p.attempt_id)}>Play acoustic challenge</button></div>)}
 <p>QR and sound can be relayed. Identity, liveness, device signatures and GPS are still required. If sound is inaccessible, use an audited faculty review.</p></section>
}
