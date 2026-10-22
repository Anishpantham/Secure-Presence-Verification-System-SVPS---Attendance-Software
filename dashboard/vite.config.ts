import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({plugins:[react(),tailwindcss()],server:{proxy:{'/api':'http://127.0.0.1:8000','/health':'http://127.0.0.1:8000'}},build:{rolldownOptions:{output:{codeSplitting:{groups:[{name:'charts',test:/node_modules\/(recharts|d3-|victory)/},{name:'vendor',test:/node_modules/}]}}}},test:{environment:'jsdom',include:['tests/**/*.test.tsx'],setupFiles:'./tests/setup.ts',css:true}});
