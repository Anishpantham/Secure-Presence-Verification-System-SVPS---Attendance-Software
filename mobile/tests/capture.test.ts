import {it,expect,describe} from 'vitest';
import {captureChallenge,friendlyVerificationError} from '../src/capture';
import {ApiError} from '../src/apiErrors';
for(const platform of ['android','ios'])describe(`${platform} shared camera protocol`,()=>{
 function deps(){let time=1000;const prompts:string[]=[];return {prompts,now:()=>time,wait:async(ms:number)=>{time+=ms},cancelled:()=>false,capture:async()=>{time+=90;return 'jpeg'},prompt:(s:string)=>prompts.push(s)}}
 it('preserves server action ordering and strictly increasing timestamps',async()=>{const d=deps();const frames=await captureChallenge(['CENTER','BLINK','TURN_LEFT'],30000,0,d);expect(d.prompts).toEqual(['CENTER','BLINK','BLINK','BLINK','TURN_LEFT']);expect(frames).toHaveLength(18);for(let i=1;i<frames.length;i++)expect(Date.parse(frames[i].captured_at)-Date.parse(frames[i-1].captured_at)).toBeGreaterThanOrEqual(170)});
 it('stops on expiration without a success result',async()=>{await expect(captureChallenge(['CENTER','BLINK'],1500,0,deps())).rejects.toThrow('expired')});
 it('stops when the app backgrounds',async()=>{const d=deps();d.cancelled=()=>true;await expect(captureChallenge(['CENTER'],30000,0,d)).rejects.toThrow('interrupted')});
 it('propagates camera errors',async()=>{const d=deps();d.capture=async()=>{throw new Error('Camera unavailable')};await expect(captureChallenge(['CENTER'],30000,0,d)).rejects.toThrow('Camera unavailable')});
});
it('explains model quality and multiple-face failures',()=>{expect(friendlyVerificationError(new Error('EXACTLY_ONE_FACE_REQUIRED'))).toContain('exactly one face');expect(friendlyVerificationError(new Error('IMAGE_QUALITY_LOW'))).toContain('lighting')});
it('keeps blink phases visible until slow photographs complete',async()=>{
 let time=1000,phase:string|undefined;const capturedPhases:(string|undefined)[]=[];
 const frames=await captureChallenge(['BLINK'],30000,0,{
  now:()=>time,wait:async ms=>{time+=ms},cancelled:()=>false,
  prompt:(_action,next)=>{phase=next},
  capture:async()=>{capturedPhases.push(phase);time+=1100;return `frame-${time}`},
 });
 expect(capturedPhases).toEqual(['open','open','closed','closed','closed','reopen','reopen','reopen']);
 expect(frames).toHaveLength(8);
});
it('signals reopening if the camera fails while eyes are closed',async()=>{
 let time=1000,phase:string|undefined;
 await expect(captureChallenge(['BLINK'],30000,0,{
  now:()=>time,wait:async ms=>{time+=ms},cancelled:()=>false,
  prompt:(_action,next)=>{phase=next},
  capture:async()=>{if(phase==='closed')throw new Error('Camera unavailable');return 'jpeg'},
 })).rejects.toThrow('Camera unavailable');
 expect(phase).toBe('reopen');
});
it('explains a missing-landmark failure',()=>expect(friendlyVerificationError(new Error('LANDMARKS_UNAVAILABLE'))).toContain('Turn only slightly'));
it.each(['TURN_LEFT','TURN_RIGHT','CENTER','BLINK'])('gives specific guidance for a missed %s step',action=>{
 const result=friendlyVerificationError(new ApiError('LIVENESS_SEQUENCE_FAILED',422,undefined,{expected_action:action}));
 expect(result).toContain(action==='BLINK'?'blink':action==='CENTER'?'straight-ahead':action==='TURN_LEFT'?'own left shoulder':'own right shoulder');
});
it('gives time to read and settle into each new pose',async()=>{
 let time=0,promptedAt=0;const delays:number[]=[];let first=true;
 await captureChallenge(['CENTER','TURN_LEFT','CENTER','BLINK','CENTER'],60000,0,{
  now:()=>time,wait:async ms=>{time+=ms},cancelled:()=>false,
  prompt:()=>{promptedAt=time;first=true},
  capture:async()=>{if(first){delays.push(time-promptedAt);first=false}time+=1100;return `frame-${time}`},
 });
 expect(delays).toHaveLength(7);
 expect(delays.every(delay=>delay>=700)).toBe(true);
 expect(time).toBeLessThan(60000);
});
