import React from 'react';
import {act,create,type ReactTestRenderer} from 'react-test-renderer';
import {beforeEach,afterEach,it,expect,vi} from 'vitest';
const m=vi.hoisted(()=>({granted:true,post:vi.fn(),listen:vi.fn(),stop:vi.fn(),change:((_:string)=>{}) as (v:string)=>void}));
vi.mock('react-native',()=>({ActivityIndicator:'ActivityIndicator',Button:'Button',ScrollView:'ScrollView',Text:'Text',View:'View',Linking:{openSettings:vi.fn()},AppState:{addEventListener:(_:string,fn:(v:string)=>void)=>{m.change=fn;return {remove:vi.fn()}}}}));
vi.mock('expo-camera',()=>({CameraView:'CameraView',useCameraPermissions:()=>[{granted:m.granted},vi.fn()]}));
vi.mock('expo-crypto',()=>({randomUUID:()=> 'test-idempotency-key'}));
vi.mock('../src/api',()=>({getDevice:async()=>({id:'device'}),post:m.post}));
vi.mock('../src/platform/device',()=>({signNativeEvidence:async(e:unknown)=>({payload:JSON.stringify(e)})}));
vi.mock('../src/acoustic',()=>({listen:m.listen}));
import {ClassroomPresence} from '../src/ClassroomPresence';
(globalThis as any).IS_REACT_ACT_ENVIRONMENT=true;
let tree:ReactTestRenderer;const ready=vi.fn(),review=vi.fn();
beforeEach(()=>{m.granted=true;ready.mockReset();review.mockReset();m.post.mockReset();m.listen.mockReset();m.stop.mockReset();m.listen.mockResolvedValue(m.stop);m.post.mockImplementation(async path=>path==='/challenges'?{id:'12345678-attempt',server_time:new Date().toISOString(),expires_at:new Date(Date.now()+120000).toISOString()}:{});});
afterEach(async()=>{if(tree)await act(async()=>tree.unmount())});
async function mount(){await act(async()=>{tree=create(<ClassroomPresence userId="student" sessionId="session" onReady={ready} onReview={review}/>)});}
function button(title:string){return tree.root.findAllByType('Button' as any).find(x=>x.props.title===title)!}
async function scan(){await act(async()=>tree.root.findByType('CameraView' as any).props.onBarcodeScanned({data:'SPVS1.test'}))}
it('denied camera offers review and cannot start listening',async()=>{m.granted=false;await mount();expect(button('Allow camera')).toBeTruthy();expect(tree.root.findAllByType('CameraView' as any)).toHaveLength(0);expect(m.listen).not.toHaveBeenCalled()});
it('microphone denial leaves identity navigation blocked and allows review',async()=>{await mount();await scan();m.listen.mockRejectedValue(new Error('MICROPHONE_PERMISSION'));await act(async()=>button('Listen for classroom sound').props.onPress());expect(ready).not.toHaveBeenCalled();m.post.mockResolvedValue({id:'review',state:'PENDING_REVIEW'});await act(async()=>button('Finish attempt & request faculty review').props.onPress());expect(JSON.parse(m.post.mock.calls.at(-1)![1].payload).reason).toBe('MICROPHONE_PERMISSION');expect(review).toHaveBeenCalled()});
it('backgrounding stops capture and blocks decoded evidence',async()=>{await mount();await scan();await act(async()=>button('Listen for classroom sound').props.onPress());await act(async()=>m.change('background'));expect(m.stop).toHaveBeenCalled();await act(async()=>m.listen.mock.calls[0][1]('123456780123456789abcdef'));expect(ready).not.toHaveBeenCalled()});
it('only a server verified sound advances to face capture',async()=>{await mount();await scan();await act(async()=>button('Listen for classroom sound').props.onPress());expect(ready).not.toHaveBeenCalled();await act(async()=>m.listen.mock.calls[0][1]('123456780123456789abcdef'));expect(ready).toHaveBeenCalledWith(expect.objectContaining({id:'12345678-attempt'}));expect(m.stop).toHaveBeenCalled()});
it('lost audio acknowledgement resends identical signed evidence',async()=>{await mount();await scan();await act(async()=>button('Listen for classroom sound').props.onPress());m.post.mockRejectedValueOnce(new Error('Network interrupted'));await act(async()=>m.listen.mock.calls[0][1]('123456780123456789abcdef'));const original=m.post.mock.calls.at(-1)![1];expect(ready).not.toHaveBeenCalled();await act(async()=>button('Retry same decoded response').props.onPress());expect(m.post.mock.calls.at(-1)![1]).toBe(original);expect(ready).toHaveBeenCalledOnce()});

it('temporary iOS inactive permission sheet does not cancel the attempt',async()=>{await mount();await act(async()=>m.change('inactive'));await act(async()=>m.change('active'));await scan();expect(button('Listen for classroom sound').props.disabled).toBe(false)});
