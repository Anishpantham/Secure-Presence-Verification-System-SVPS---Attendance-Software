import {describe,it,expect,vi,beforeEach,afterEach} from 'vitest';
import {render,screen,waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {QueryClient,QueryClientProvider} from '@tanstack/react-query';
import {MemoryRouter} from 'react-router-dom';
import App,{Login} from '../src/App';
import {DataTable,FormDialog} from '../src/components';
import {api,setTokens} from '../src/api';

const user={id:'u1',name:'Test Faculty',email:'faculty@spvs.example',role:'faculty',active:true};
const response=(body:unknown,status=200)=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json'}});
function wrap(node:React.ReactNode){return render(<QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}><MemoryRouter>{node}</MemoryRouter></QueryClientProvider>)}
beforeEach(()=>{setTokens(null)});
afterEach(()=>vi.restoreAllMocks());

describe('Authentication',()=>{
 it('submits credentials to the actual versioned API contract',async()=>{const login=vi.fn();const fetcher=vi.spyOn(globalThis,'fetch').mockResolvedValue(response({user,access_token:'access',refresh_token:'refresh'}));wrap(<Login onLogin={login}/>);await userEvent.type(screen.getByLabelText('Email address'),'faculty@spvs.example');await userEvent.type(screen.getByLabelText('Password'),'correct password');await userEvent.click(screen.getByRole('button',{name:/Sign in to/}));await waitFor(()=>expect(login).toHaveBeenCalledWith(user));expect(fetcher.mock.calls[0][0]).toBe('/api/v1/auth/login');expect(JSON.parse(fetcher.mock.calls[0][1]!.body as string)).toEqual({email:'faculty@spvs.example',password:'correct password'})});
 it('shows an API authentication failure',async()=>{vi.spyOn(globalThis,'fetch').mockResolvedValue(response({error:{message:'Invalid email or password'}},401));wrap(<Login onLogin={vi.fn()}/>);await userEvent.type(screen.getByLabelText('Email address'),'wrong@spvs.example');await userEvent.type(screen.getByLabelText('Password'),'wrong');await userEvent.click(screen.getByRole('button',{name:/Sign in to/}));expect(await screen.findByRole('alert')).toHaveTextContent('Invalid email or password')});
 it('directs students to the mobile application',async()=>{const login=vi.fn();vi.spyOn(globalThis,'fetch').mockResolvedValue(response({user:{...user,role:'student'},access_token:'a',refresh_token:'r'}));wrap(<Login onLogin={login}/>);await userEvent.type(screen.getByLabelText('Email address'),'student@spvs.example');await userEvent.type(screen.getByLabelText('Password'),'password');await userEvent.click(screen.getByRole('button',{name:/Sign in to/}));expect(await screen.findByRole('alert')).toHaveTextContent('mobile application');expect(login).not.toHaveBeenCalled()});
 it('hides administrator navigation for faculty after login',async()=>{vi.spyOn(globalThis,'fetch').mockImplementation(async(path)=>String(path).endsWith('/auth/login')?response({user,access_token:'a',refresh_token:'r'}):String(path).endsWith('/overview')?response({sessions:0,active_sessions:0,present_records:0,pending_review:0,attempts_by_state:{}}):response([]));wrap(<App/>);await userEvent.type(screen.getByLabelText('Email address'),'faculty@spvs.example');await userEvent.type(screen.getByLabelText('Password'),'password');await userEvent.click(screen.getByRole('button',{name:/Sign in to/}));await screen.findByRole('navigation');expect(screen.queryByRole('link',{name:'Administration'})).not.toBeInTheDocument();expect(screen.getByRole('link',{name:'Sessions'})).toBeInTheDocument()});
});
describe('Forms and records',()=>{
 it('filters rows by actual record content',async()=>{wrap(<DataTable rows={[{id:'1',name:'Alice'},{id:'2',name:'Bob'}]} columns={[{label:'Student',render:r=>r.name}]}/>);await userEvent.type(screen.getByLabelText('Filter rows'),'Alice');expect(screen.getByText('Alice')).toBeInTheDocument();expect(screen.queryByText('Bob')).not.toBeInTheDocument()});
 it('requires an audit reason and sends form values',async()=>{const save=vi.fn().mockResolvedValue({});wrap(<FormDialog title="Correct attendance" fields={[{name:'reason',label:'Audit reason',min:10}]} onSave={save} onClose={vi.fn()}/>);await userEvent.click(screen.getByRole('button',{name:'Save changes'}));expect(save).not.toHaveBeenCalled();await userEvent.type(screen.getByLabelText('Audit reason'),'Verified presence with course faculty');await userEvent.click(screen.getByRole('button',{name:'Save changes'}));await waitFor(()=>expect(save).toHaveBeenCalledWith({reason:'Verified presence with course faculty'}))});
 it('keeps failed mutations visible for correction',async()=>{wrap(<FormDialog title="Create course" fields={[{name:'name',label:'Course name'}]} onSave={async()=>{throw new Error('Course code already exists')}} onClose={vi.fn()}/>);await userEvent.type(screen.getByLabelText('Course name'),'Security');await userEvent.click(screen.getByRole('button',{name:'Save changes'}));expect(await screen.findByRole('alert')).toHaveTextContent('already exists')});
});
describe('API token lifecycle',()=>{
 it('rotates an expired token then retries the request',async()=>{setTokens({access_token:'old',refresh_token:'refresh'});const f=vi.spyOn(globalThis,'fetch').mockResolvedValueOnce(response({error:{message:'Expired'}},401)).mockResolvedValueOnce(response({access_token:'new',refresh_token:'rotated'})).mockResolvedValueOnce(response([{id:'course'}]));expect(await api('/courses')).toEqual([{id:'course'}]);expect(f.mock.calls[1][0]).toBe('/api/v1/auth/refresh');expect((f.mock.calls[2][1]!.headers as Record<string,string>).Authorization).toBe('Bearer new')});
});
