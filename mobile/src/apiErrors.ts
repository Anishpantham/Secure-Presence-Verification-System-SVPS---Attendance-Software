export class ApiError extends Error {
 constructor(message:string,public readonly status:number,public readonly retryAfterSeconds?:number,public readonly details?:Record<string,unknown>){
  super(message);this.name='ApiError';
 }
}

export function retryAfterSeconds(value:string|null):number|undefined{
 if(!value)return undefined;
 const seconds=/^\d+$/.test(value)?Number(value):(Date.parse(value)-Date.now())/1000;
 return Number.isFinite(seconds)?Math.max(1,Math.ceil(seconds)):undefined;
}

// A definitive client-error response must not replay a rejected challenge.
// Network failures and server failures may have lost an otherwise valid response.
export function canRetrySubmission(error:unknown):boolean{
 return !(error instanceof ApiError)||error.status>=500;
}
