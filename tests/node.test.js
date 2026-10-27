'use strict';
const test=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const os=require('node:os');const path=require('node:path');
process.env.ALICE_DATA_DIR=fs.mkdtempSync(path.join(os.tmpdir(),'alice-test-'));process.env.ALICE_PANEL_TOKEN='test-secret';
const {server,privateIP,parseSystem}=require('../node/server');
test('private device addresses only',()=>{assert.equal(privateIP('192.168.1.10'),true);assert.equal(privateIP('8.8.8.8'),false);assert.equal(privateIP('localhost'),false);});
test('system parsing',()=>{let s=parseSystem('123.00 2.00\nMemTotal: 238000 kB\nMemAvailable: 105000 kB\n52000\n/dev/root 1 2 500 4 /');assert.equal(s.uptime_seconds,123);assert.equal(s.temperature_c,52);assert.equal(s.ram_available_kb,105000);});
test('API authentication and unsupported controls',async()=>{await new Promise(r=>server.listen(0,'127.0.0.1',r));let url='http://127.0.0.1:'+server.address().port;try{assert.equal((await fetch(url+'/api/status')).status,401);let h={'X-Panel-Token':'test-secret'};assert.equal((await fetch(url+'/api/status',{headers:h})).status,200);assert.equal((await fetch(url+'/api/player/control',{method:'POST',headers:h})).status,501);assert.equal((await fetch(url+'/api/lighting',{method:'POST',headers:h})).status,501);}finally{server.close();}});
