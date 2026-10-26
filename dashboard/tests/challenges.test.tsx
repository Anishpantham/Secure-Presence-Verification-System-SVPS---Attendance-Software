import {afterEach,it,expect,vi} from 'vitest';
import {render,screen,waitFor,cleanup} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {ClassroomChallenges} from '../src/ClassroomChallenges';
import {api,post} from '../src/api';
vi.mock('../src/api',()=>({api:vi.fn(),post:vi.fn()}));
vi.mock('qrcode',()=>({default:{toDataURL:async()=> 'data:image/png;base64,test'}}));
afterEach(()=>{cleanup();vi.resetAllMocks()});
it('shows active QR and waiting phones with an authoritative countdown',async()=>{
 vi.mocked(api).mockResolvedValue({enabled:true,server_time:new Date().toISOString(),rotate_at:new Date(Date.now()+5000).toISOString(),token:'SPVS1.token',queue:[{attempt_id:'abc',label:'abc'}]});
 render(<ClassroomChallenges sessionId="sid"/>);expect(await screen.findByAltText(/rotating attendance QR/)).toBeInTheDocument();expect(screen.getByRole('button',{name:'Play acoustic challenge'})).toBeEnabled();expect(screen.getByRole('button',{name:'Start challenges'})).toBeDisabled();
 await userEvent.click(screen.getByRole('button',{name:'Stop challenges'}));expect(post).toHaveBeenCalledWith('/sessions/sid/presence/control',{enabled:false});
 await waitFor(()=>expect(screen.queryByAltText(/rotating attendance QR/)).toBeNull());
});
it('hides QR and exposes connection failure',async()=>{vi.mocked(api).mockRejectedValue(new Error('Network interrupted'));render(<ClassroomChallenges sessionId="sid"/>);expect(await screen.findByRole('alert')).toHaveTextContent('Network interrupted');expect(screen.queryByAltText(/rotating attendance QR/)).toBeNull()});
it('hides expired QR even if the request returned a token',async()=>{vi.mocked(api).mockResolvedValue({enabled:true,server_time:new Date().toISOString(),rotate_at:new Date(Date.now()-1).toISOString(),token:'expired',queue:[]});render(<ClassroomChallenges sessionId="sid"/>);await screen.findByText('Refreshing code…');expect(screen.queryByAltText(/rotating attendance QR/)).toBeNull()});
