import {beforeEach,describe,it,expect,vi} from 'vitest';
const mock=vi.hoisted(()=>({os:'android',allowed:true,start:vi.fn(),stop:vi.fn(),listeners:{} as Record<string,(e:any)=>void>,remove:vi.fn()}));
vi.mock('react-native',()=>({Platform:{get OS(){return mock.os}},PermissionsAndroid:{PERMISSIONS:{RECORD_AUDIO:'mic'},RESULTS:{GRANTED:'granted'},request:async()=>mock.allowed?'granted':'denied'}}));
vi.mock('expo-modules-core',()=>({requireNativeModule:()=>({start:mock.start,stop:mock.stop,requestPermission:async()=>mock.allowed,addListener:(name:string,fn:(e:any)=>void)=>{mock.listeners[name]=fn;return {remove:mock.remove}}})}));
import {listen} from '../src/acoustic';
import {encode} from '../src/acousticCodec';
beforeEach(()=>{mock.allowed=true;mock.os='android';mock.start.mockReset();mock.stop.mockReset();mock.remove.mockReset();mock.listeners={}});
describe('foreground native capture adapter',()=>{
 it.each(['android','ios'])('denied microphone on %s never starts capture',async os=>{mock.os=os;mock.allowed=false;await expect(listen('12345678-0000',vi.fn(),vi.fn())).rejects.toThrow('MICROPHONE_PERMISSION');expect(mock.start).not.toHaveBeenCalled()});
 it.each(['android','ios'])('decodes only the matching attempt on %s and stops explicitly',async os=>{mock.os=os;const decoded=vi.fn();const stop=await listen('12345678-0000',decoded,vi.fn());
  const push=(payload:string)=>{const pcm=encode(payload);for(let i=0;i<pcm.length;i+=1600)mock.listeners.pcm({samples:Array.from(pcm.slice(i,i+1600)),sampleRate:16000})};
  push('876543210123456789abcdef');expect(decoded).not.toHaveBeenCalled();push('123456780123456789abcdef');expect(decoded).toHaveBeenCalledWith('123456780123456789abcdef');await stop();expect(mock.stop).toHaveBeenCalled();expect(mock.remove).toHaveBeenCalledTimes(2);
 });
 it('cleans listeners if hardware start fails',async()=>{mock.start.mockRejectedValue(new Error('AUDIO_UNAVAILABLE'));await expect(listen('id',vi.fn(),vi.fn())).rejects.toThrow('AUDIO_UNAVAILABLE');expect(mock.remove).toHaveBeenCalledTimes(2);expect(mock.stop).toHaveBeenCalled()});
 it('reports capture errors instead of passing verification',async()=>{const decoded=vi.fn(),failed=vi.fn();const stop=await listen('id',decoded,failed);mock.listeners.captureError({});expect(failed).toHaveBeenCalled();expect(decoded).not.toHaveBeenCalled();await stop()});
});
