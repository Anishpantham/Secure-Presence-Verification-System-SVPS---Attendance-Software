import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';

// Local development credentials are read in memory and are never written to test output.
const password=process.env.DEMO_PASSWORD||readFileSync('../.env','utf8').split('\n').find(l=>l.startsWith('DEMO_PASSWORD='))!.slice('DEMO_PASSWORD='.length);
test('administrator configures a room, creates a session and exports real records',async({page})=>{
 await page.goto('/');await page.getByLabel('Email address').fill('admin@spvs.example');await page.getByLabel('Password').fill(password);await page.getByRole('button',{name:'Sign in to workspace'}).click();
 await expect(page.getByRole('heading',{name:'Presence overview'})).toBeVisible();
 await page.getByRole('link',{name:'Classrooms',exact:true}).click();
 await page.getByRole('button',{name:'Edit details →'}).first().click();
 await page.getByLabel('Latitude',{exact:true}).fill('12.9716');await page.getByLabel('Longitude',{exact:true}).fill('77.5946');
 await page.getByRole('button',{name:'Save changes'}).click();await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.getByRole('link',{name:'Sessions',exact:true}).click();await page.getByRole('button',{name:'Create session',exact:true}).click();
 await page.getByLabel('Course',{exact:true}).selectOption({label:'Applied Security Engineering'});
 await page.getByLabel('Classroom',{exact:true}).selectOption({label:'Demo lab — configure coordinates'});
 const local=(date:Date)=>new Date(date.getTime()-date.getTimezoneOffset()*60000).toISOString().slice(0,16);
 await page.getByLabel('Starts at (local time)').fill(local(new Date(Date.now()-60000)));
 await page.getByLabel('Ends at (local time)').fill(local(new Date(Date.now()+1800000)));
 const createdResponse=page.waitForResponse(response=>response.request().method()==='POST'&&new URL(response.url()).pathname==='/api/v1/sessions');
 await page.getByRole('button',{name:'Save changes'}).click();
 const response=await createdResponse;expect(response.ok()).toBeTruthy();const created=await response.json();
 await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.locator(`a[href="/sessions/${created.id}"]`).filter({hasText:"Open →"}).click();await expect(page.getByRole('heading',{name:'Verification attempts'})).toBeVisible();
 await page.getByRole('button',{name:'Start challenges',exact:true}).click();
 await expect(page.getByAltText('Scan this rotating attendance QR code')).toBeVisible();
 const firstQR=await page.getByAltText('Scan this rotating attendance QR code').getAttribute('src');
 await expect.poll(()=>page.getByAltText('Scan this rotating attendance QR code').getAttribute('src'),{timeout:10000}).not.toBe(firstQR);
 await page.getByRole('button',{name:'Stop challenges',exact:true}).click();
 await expect(page.getByAltText('Scan this rotating attendance QR code')).toHaveCount(0);
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'Export',exact:true}).click();expect((await download).suggestedFilename()).toBe('spvs-attendance.csv');
 await page.getByRole('button',{name:'Close session',exact:true}).click();await expect(page.getByRole('button',{name:'Session closed'})).toBeDisabled();
 await page.getByRole('link',{name:'Overview',exact:true}).click();await expect(page.getByRole('heading',{name:'Presence overview'})).toBeVisible();await page.screenshot({path:'../artifacts/dashboard-overview.png',fullPage:true});
});

test('faculty access is scoped and administrator route is unavailable',async({page})=>{
 await page.goto('/');await page.getByLabel('Email address').fill('faculty@spvs.example');await page.getByLabel('Password').fill(password);await page.getByRole('button',{name:'Sign in to workspace'}).click();
 await expect(page.getByRole('heading',{name:'Presence overview'})).toBeVisible();
 await expect(page.getByRole('link',{name:'Administration',exact:true})).toHaveCount(0);
 await page.getByRole('link',{name:'Courses',exact:true}).click();await page.waitForURL('**/courses');await expect(page.getByRole('heading',{name:'Courses',exact:true})).toBeVisible();await expect(page.getByText('Applied Security Engineering',{exact:true})).toBeVisible();
 await page.getByRole('button',{name:'Sign out'}).click();await expect(page.getByRole('heading',{name:'Welcome back'})).toBeVisible();
});

test('administrator configures the separate iPhone presence policy with an audit reason',async({page})=>{
 await page.goto('/');await page.getByLabel('Email address').fill('admin@spvs.example');await page.getByLabel('Password').fill(password);await page.getByRole('button',{name:'Sign in to workspace'}).click();
 await page.getByRole('link',{name:'Administration',exact:true}).click();
 await expect(page.getByRole('heading',{name:'Device capabilities'})).toBeVisible();
 await page.getByRole('button',{name:'Edit policy',exact:true}).click();
 await page.getByLabel('iPhone presence evidence',{exact:true}).selectOption('review');
 await page.getByLabel('Reason (required for the audit trail)').fill('Cross-platform browser check: retain manual review for iPhone presence.');
 const saved=page.waitForResponse(r=>r.request().method()==='PUT'&&new URL(r.url()).pathname==='/api/v1/policy');
 await page.getByRole('button',{name:'Save changes'}).click();
 const response=await saved;expect(response.ok()).toBeTruthy();expect((await response.json()).ios_presence).toBe('review');
 await expect(page.getByRole('dialog')).toHaveCount(0);
 await page.getByRole('link',{name:'Security events',exact:true}).click();
 await expect(page.getByText('POLICY CHANGED',{exact:true}).first()).toBeVisible();
});
