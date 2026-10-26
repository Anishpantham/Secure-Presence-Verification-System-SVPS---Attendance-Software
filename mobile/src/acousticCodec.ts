/** SPVS-FSK16-v1: 32-bit attempt tag + 64-bit nonce + CRC16-CCITT, 16 audible carriers, 2.7 s.
 * Shared by laptop encoder and phone decoder; CRC detects errors, not forgery.
 */
export const SYMBOL_SECONDS=0.075;
export const PREAMBLE=[0,15,0,15,3,12,5,10];
export const frequency=(symbol:number)=>1200+symbol*160;
export function crc16(bytes:number[]){let crc=0xffff;for(const b of bytes){crc^=b<<8;for(let k=0;k<8;k++)crc=(crc&0x8000)?(crc<<1)^0x1021:crc<<1;crc&=0xffff}return crc}
export function symbols(payload:string){
 if(!/^[a-f0-9]{24}$/.test(payload))throw new Error('Invalid acoustic payload');
 const bytes=payload.match(/../g)!.map(x=>parseInt(x,16)),crc=crc16(bytes);
 return [...PREAMBLE,...[...bytes,crc>>8,crc&255].flatMap(b=>[b>>4,b&15])];
}
export function encode(payload:string,sampleRate=16000):Float32Array{
 const tones=symbols(payload),size=Math.round(sampleRate*SYMBOL_SECONDS),out=new Float32Array(tones.length*size);
 tones.forEach((tone,s)=>{for(let i=0;i<size;i++){const ramp=Math.min(1,i/(sampleRate*.004),(size-1-i)/(sampleRate*.004));out[s*size+i]=.65*ramp*Math.sin(2*Math.PI*frequency(tone)*i/sampleRate)}});
 return out;
}
function toneAt(pcm:Float32Array,start:number,length:number,rate:number):number{
 let best=-1,peak=0,second=0,energy=0;
 for(let i=0;i<length;i++)energy+=pcm[start+i]**2;
 if(energy/length<1e-7)return -1;
 for(let tone=0;tone<16;tone++){
  const coeff=2*Math.cos(2*Math.PI*frequency(tone)/rate);let a=0,b=0;
  for(let i=0;i<length;i++){const v=pcm[start+i]+coeff*a-b;b=a;a=v}
  const power=a*a+b*b-coeff*a*b;
  if(power>peak){second=peak;peak=power;best=tone}else second=Math.max(second,power);
 }
 return peak>second*2.5?best:-1;
}
export function decode(pcm:Float32Array,rate:number):string|null{
 if(rate<8000||rate>96000)return null;
 const size=Math.round(rate*SYMBOL_SECONDS),window=Math.round(size*.6),margin=Math.round(size*.2),hop=Math.max(1,Math.round(rate*.008));
 // Search timing offsets; analyze symbol centers to tolerate echo and edge transients.
 for(let start=0;start+36*size<=pcm.length;start+=hop){
  let ok=true;
  for(let i=0;i<PREAMBLE.length;i++)if(toneAt(pcm,start+i*size+margin,window,rate)!==PREAMBLE[i]){ok=false;break}
  if(!ok)continue;
  const n:number[]=[];
  for(let i=8;i<36;i++)n.push(toneAt(pcm,start+i*size+margin,window,rate));
  if(n.some(x=>x<0))continue;
  const bytes=Array.from({length:14},(_,i)=>(n[i*2]<<4)|n[i*2+1]);
  if(crc16(bytes.slice(0,12))===((bytes[12]<<8)|bytes[13]))return bytes.slice(0,12).map(x=>x.toString(16).padStart(2,'0')).join('');
 }
 return null;
}
export class AcousticStream {
 private samples=new Float32Array(0);
 push(chunk:number[],rate:number){
  const next=new Float32Array(this.samples.length+chunk.length);next.set(this.samples);next.set(chunk,this.samples.length);
  this.samples=next.slice(-Math.ceil(rate*3.2));
  return decode(this.samples,rate);
 }
 clear(){this.samples=new Float32Array(0)}
}
