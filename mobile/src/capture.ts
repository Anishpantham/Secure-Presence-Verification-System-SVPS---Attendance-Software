import type {Action,Frame} from './contracts';
import {ApiError} from './apiErrors';
export type BlinkPhase='open'|'closed'|'reopen';
export type CaptureDependencies={
 now:()=>number;wait:(ms:number)=>Promise<void>;cancelled:()=>boolean;
 capture:()=>Promise<string>;prompt:(action:Action,phase?:BlinkPhase)=>void;
};
// The same capture protocol runs on both native camera implementations. Landmarks remain server-side.
export async function captureChallenge(actions:Action[],expiresAt:number,clockOffset:number,deps:CaptureDependencies):Promise<Frame[]>{
 const frames:Frame[]=[];
 let eyesClosed=false;
 try{
 for(const action of actions){
  deps.prompt(action,action==='BLINK'?'open':undefined);
  // Give a person time to see a new instruction before collecting evidence for that pose.
  await deps.wait(700);
  for(let i=0;i<(action==='BLINK'?8:5);i++){
   // Drive open/closed/open cues by completed photographs, not a short timed blink
   // that can fall entirely between slow native still-camera captures.
   if(action==='BLINK'&&(i===2||i===5)){
    eyesClosed=i===2;
    deps.prompt(action,i===2?'closed':'reopen');
    await deps.wait(700);
   }
   if(deps.cancelled())throw new Error('Capture interrupted. Start a fresh challenge.');
   const started=deps.now();
   if(started+clockOffset>=expiresAt)throw new Error('Challenge expired; start again.');
   const jpeg=await deps.capture();
   if(deps.cancelled()||deps.now()+clockOffset>=expiresAt)throw new Error('Capture interrupted or expired. Start again.');
   frames.push({jpeg,captured_at:new Date(started+clockOffset).toISOString()});
   await deps.wait(Math.max(0,170-(deps.now()-started)));
  }
 }
 return frames;
 }finally{if(eyesClosed)deps.prompt('BLINK','reopen')}
}
export function friendlyVerificationError(error:unknown):string{
 const raw=error instanceof Error?error.message:String(error);
 if(raw==='LIVENESS_SEQUENCE_FAILED'&&error instanceof ApiError){
  const action=error.details?.expected_action;
  if(action==='TURN_LEFT'||action==='TURN_RIGHT')return `We missed the ${action==='TURN_LEFT'?'left':'right'} turn. Turn gently toward your own ${action==='TURN_LEFT'?'left':'right'} shoulder and hold until the instruction changes.`;
  if(action==='BLINK')return 'We missed the blink. Close both eyes when asked, then open them when the phone vibrates.';
  if(action==='CENTER')return 'We missed the straight-ahead pose. Look back at the camera and hold until the instruction changes.';
 }
 const messages:Record<string,string>={EXACTLY_ONE_FACE_REQUIRED:'Keep exactly one face in the frame, then try again.',
  IMAGE_QUALITY_LOW:'Use even lighting and hold the camera steady, then try again.',FACE_TOO_SMALL:'Move closer until your face fills the guide.',
  LANDMARKS_UNAVAILABLE:'Keep your whole face visible in even lighting. Turn only slightly, then start a fresh verification.',
  FACE_MISMATCH:'Your face did not match the enrolled profile. Retry or request a faculty review.',
  LIVENESS_SEQUENCE_FAILED:'The blink or head-turn sequence was not detected. Follow each prompt and try again.',
  FRAME_TIMING_INVALID:'Camera capture was too slow or interrupted. Close other camera apps and retry.',
  DEVICE_SIGNATURE_INVALID:'This device could not authenticate. Request a device reset if its key was lost.'};
 return messages[raw]||raw;
}
