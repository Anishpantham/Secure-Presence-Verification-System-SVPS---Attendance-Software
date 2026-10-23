import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./e2e',workers:1,use:{baseURL:'http://127.0.0.1:5173',headless:true,launchOptions:{executablePath:process.env.SPVS_CHROMIUM_PATH||(process.platform==='linux'?'/usr/bin/chromium':undefined),args:['--no-sandbox']}},reporter:[['list'],['junit',{outputFile:'../artifacts/browser-tests.xml'}]]});
