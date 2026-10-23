import React from 'react';
import {act,create,type ReactTestRenderer} from 'react-test-renderer';
import {it,expect,vi} from 'vitest';
vi.mock('react-native',()=>({View:'View',Text:'Text'}));
import {VerificationProgress} from '../src/VerificationProgress';
(globalThis as any).IS_REACT_ACT_ENVIRONMENT=true;
for(const platform of ['Android','iOS'])it(`${platform} shared progress renders current stage without claiming attendance approval`,async()=>{
 let tree:ReactTestRenderer;
 await act(async()=>{tree=create(<VerificationProgress step={2}/>)});
 expect(tree!.root.findByProps({accessibilityLabel:'Identity: current'})).toBeTruthy();
 expect(tree!.root.findByProps({accessibilityLabel:'Presence: waiting'})).toBeTruthy();
 await act(async()=>tree!.update(<VerificationProgress step={4}/>));
 expect(tree!.root.findByProps({accessibilityLabel:'Decision: current'})).toBeTruthy();
 expect(JSON.stringify(tree!.toJSON())).not.toContain('approved');
 await act(async()=>tree!.unmount());
});
