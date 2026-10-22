import {describe,it,expect} from 'vitest';
import {createHmac} from 'node:crypto';
import {signEvidence,activeSession,decisionText} from '../src/protocol';
import type {Evidence,Session} from '../src/contracts';
describe('Device signing protocol',()=>{
 const evidence:Evidence={challenge_id:'challenge',device_id:'device',frames:[],consent:false,location:null,wifi:[],wifi_status:'unsupported',integrity_token:null};
 it('matches the backend HMAC byte protocol',()=>{const signed=signEvidence(evidence,'abc123','idempotency123456');expect(signed.signature).toBe(createHmac('sha256','abc123').update('idempotency123456.'+signed.payload).digest('hex'))});
 it('binds the idempotency key',()=>{expect(signEvidence(evidence,'key','one').signature).not.toBe(signEvidence(evidence,'key','two').signature)});
 it('binds all evidence fields',()=>{expect(signEvidence(evidence,'key','one').signature).not.toBe(signEvidence({...evidence,device_id:'other'},'key','one').signature)});
});
describe('Attendance UI decisions',()=>{
 const session:Session={id:'1',course_name:'course',classroom_name:'room',starts_at:'2026-01-01T10:00:00Z',ends_at:'2026-01-01T11:00:00Z',closed:false};
 it('opens at the inclusive start boundary',()=>expect(activeSession(session,Date.parse(session.starts_at))).toBe(true));
 it('expires at the exclusive end boundary',()=>expect(activeSession(session,Date.parse(session.ends_at))).toBe(false));
 it('never opens a closed session',()=>expect(activeSession({...session,closed:true},Date.parse(session.starts_at))).toBe(false));
 it('does not describe review as approval',()=>expect(decisionText('PENDING_REVIEW')).toContain('not yet approved'));
});
