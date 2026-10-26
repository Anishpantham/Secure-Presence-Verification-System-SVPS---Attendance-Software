import {describe,it,expect} from 'vitest';
import {encode,decode,AcousticStream,symbols} from '../src/acousticCodec';
const payload='a1b2c3d4e5f60718293a4b5c';
describe('audible acoustic codec',()=>{
 it.each([16000,44100,48000])('round trips at %i Hz within 2–3 seconds',rate=>{const pcm=encode(payload,rate);expect(pcm.length/rate).toBeCloseTo(2.7,2);expect(decode(pcm,rate)).toBe(payload)});
 it('finds an unaligned signal with noise, attenuation, echo and clipping',()=>{
  const rate=16000,encoded=encode(payload,rate),pcm=new Float32Array(encoded.length+4300);let random=7;
  for(let i=0;i<pcm.length;i++){random=(1664525*random+1013904223)>>>0;const original=encoded[i-2117]||0,echo=encoded[i-2437]||0;pcm[i]=Math.max(-.2,Math.min(.2,.6*original+.12*echo))+(random/2**32-.5)*.045}
  expect(decode(pcm,rate)).toBe(payload);
 });
 it('rejects corrupted payload, silence, truncated and arbitrary audio',()=>{
  const pcm=encode(payload);pcm.fill(0,16000,18000);expect(decode(pcm,16000)).toBeNull();
  expect(decode(new Float32Array(50000),16000)).toBeNull();expect(decode(encode(payload).slice(0,20000),16000)).toBeNull();
  const tones=symbols(payload);expect(tones.length).toBe(36);
 });
 it('decodes bounded streaming chunks and clears retained samples',()=>{
  const pcm=encode(payload),stream=new AcousticStream();let result:string|null=null;
  for(let i=0;i<pcm.length;i+=1600)result=stream.push(Array.from(pcm.slice(i,i+1600)),16000)||result;
  expect(result).toBe(payload);stream.clear();expect(stream.push(Array(1600).fill(0),16000)).toBeNull();
 });
});
