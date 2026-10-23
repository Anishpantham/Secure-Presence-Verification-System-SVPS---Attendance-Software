import {it,expect,describe} from 'vitest';
import {captureChallenge,friendlyVerificationError} from '../src/capture';
for(const platform of ['android','ios'])describe(`${platform} shared camera protocol`,()=>{
 function deps(){let time=1000;const prompts:string[]=[];return {prompts,now:()=>time,wait:async(ms:number)=>{time+=ms},cancelled:()=>false,capture:async()=>{time+=90;return 'jpeg'},prompt:(s:string)=>prompts.push(s)}}
 it('preserves server action ordering and strictly increasing timestamps',async()=>{const d=deps();const frames=await captureChallenge(['CENTER','BLINK','TURN_LEFT'],30000,0,d);expect(d.prompts).toEqual(['CENTER','BLINK','TURN_LEFT']);expect(frames).toHaveLength(18);for(let i=1;i<frames.length;i++)expect(Date.parse(frames[i].captured_at)-Date.parse(frames[i-1].captured_at)).toBeGreaterThanOrEqual(170)});
 it('stops on expiration without a success result',async()=>{await expect(captureChallenge(['CENTER','BLINK'],1500,0,deps())).rejects.toThrow('expired')});
 it('stops when the app backgrounds',async()=>{const d=deps();d.cancelled=()=>true;await expect(captureChallenge(['CENTER'],30000,0,d)).rejects.toThrow('interrupted')});
 it('propagates camera errors',async()=>{const d=deps();d.capture=async()=>{throw new Error('Camera unavailable')};await expect(captureChallenge(['CENTER'],30000,0,d)).rejects.toThrow('Camera unavailable')});
});
it('explains model quality and multiple-face failures',()=>{expect(friendlyVerificationError(new Error('EXACTLY_ONE_FACE_REQUIRED'))).toContain('exactly one face');expect(friendlyVerificationError(new Error('IMAGE_QUALITY_LOW'))).toContain('lighting')});
