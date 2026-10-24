import {afterEach,it,expect,vi} from 'vitest';
vi.hoisted(()=>{Object.defineProperty(globalThis,'__DEV__',{value:true,configurable:true})});
vi.mock('../src/platform',()=>({defaultApiUrl:()=> 'http://localhost:8000/api/v1'}));
vi.mock('expo-secure-store',()=>({}));
import {api} from '../src/api';
import {ApiError,canRetrySubmission} from '../src/apiErrors';
afterEach(()=>vi.unstubAllGlobals());

it('preserves a server rejection so a failed capture is not offered as a network retry',async()=>{
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response(JSON.stringify({error:{message:'LIVENESS_SEQUENCE_FAILED',details:{expected_action:'TURN_LEFT'}}}),{status:422})));
 const error=await api('/biometrics/enroll').catch(e=>e);
 expect(error).toBeInstanceOf(ApiError);
 if(!(error instanceof ApiError))throw new Error('Expected a typed API rejection');
 expect(error.message).toBe('LIVENESS_SEQUENCE_FAILED');
 expect(error.details?.expected_action).toBe('TURN_LEFT');
 expect(canRetrySubmission(error)).toBe(false);
});
it('retains the server cooldown and prevents replay after rate limiting',async()=>{
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response(JSON.stringify({error:{message:'Too many requests'}}),{status:429,headers:{'Retry-After':'37'}})));
 const error=await api('/biometrics/enroll').catch(e=>e);
 if(!(error instanceof ApiError))throw new Error('Expected a typed rate-limit rejection');
 expect(error.retryAfterSeconds).toBe(37);
 expect(canRetrySubmission(error)).toBe(false);
});
it('still permits idempotent recovery after a lost network response',async()=>{
 vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new TypeError('Network request failed')));
 const error=await api('/biometrics/enroll').catch(e=>e);
 expect(canRetrySubmission(error)).toBe(true);
});
it('still permits recovery after a server failure',async()=>{
 vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response('{}',{status:503})));
 const error=await api('/biometrics/enroll').catch(e=>e);
 expect(canRetrySubmission(error)).toBe(true);
});
