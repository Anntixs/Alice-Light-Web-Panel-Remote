import json, os, secrets, subprocess, time, ipaddress
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT=Path(__file__).resolve().parent.parent
DATA=Path(os.getenv('ALICE_DATA_DIR',ROOT/'data')); DATA.mkdir(parents=True,exist_ok=True)
CONFIG=DATA/'settings.json'
app=FastAPI(title='Alice Light Web Panel Remote',docs_url=None,redoc_url=None)

def settings():
    try:return json.loads(CONFIG.read_text())
    except (OSError,ValueError):return {'ip':'','mode':'mock','interval':5}

def save(value):
    temp=CONFIG.with_suffix('.tmp');temp.write_text(json.dumps(value));os.chmod(temp,0o600);temp.replace(CONFIG)

class QuasarAdapter:
    def capabilities(self):return {'status':False,'player':False,'text':False,'lighting':False}
class GlagolAdapter:
    def capabilities(self):return {'player':False,'text':False}
class ADBAdapter:
    def capabilities(self):return {'system':False,'lighting':False}
class SSHAdapter:
    def __init__(self,ip):self.ip=ip
    def run(self,command):
        if command not in ('system','probe'):raise ValueError('Unsupported command')
        script={'probe':'true','system':'cat /proc/uptime /proc/meminfo; cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null; df -k / 2>/dev/null; cat /proc/net/wireless 2>/dev/null'}[command]
        return subprocess.run(['ssh','-F','/dev/null','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','ConnectTimeout=3','-o','ConnectionAttempts=1','root@'+self.ip,script],capture_output=True,text=True,timeout=5,check=True).stdout
    def capabilities(self):
        try:self.run('probe');return {'system':True}
        except Exception:return {'system':False}
class LightingAdapter:
    def capabilities(self):return {'color':False,'brightness':False,'zones':False,'restore':False}
class SystemAdapter:
    def __init__(self,ssh):self.ssh=ssh
    def read(self):
        raw=self.ssh.run('system'); lines=raw.splitlines(); result={'uptime_seconds':None,'ram_total_kb':None,'ram_available_kb':None,'temperature_c':None,'free_kb':None,'wifi_dbm':None,'cpu_percent':None,'quasar_version':None}
        try:result['uptime_seconds']=float(lines[0].split()[0])
        except (IndexError,ValueError):pass
        for line in lines:
            for key,field in [('MemTotal:','ram_total_kb'),('MemAvailable:','ram_available_kb')]:
                if line.startswith(key):result[field]=int(line.split()[1])
            if line.isdigit() and 10000<int(line)<150000:result['temperature_c']=int(line)/1000
            if line.startswith('/dev/'):
                parts=line.split()
                if len(parts)>3 and parts[3].isdigit():result['free_kb']=int(parts[3])
        return result
class Config(BaseModel):
    ip:str='';mode:str='mock';interval:int=Field(default=5,ge=5,le=300)
class Control(BaseModel):
    action:str
class Lighting(BaseModel):
    enabled:bool=True;color:str='#ff7417';brightness:int=Field(default=100,ge=0,le=100);zone:str='all'

def auth(req):
    token=os.getenv('ALICE_PANEL_TOKEN','')
    if not token:raise HTTPException(503,'Set ALICE_PANEL_TOKEN on the PC')
    supplied=req.headers.get('X-Panel-Token','')
    if not secrets.compare_digest(supplied,token):raise HTTPException(401,'Unauthorized')
    if req.method not in ('GET','HEAD') and req.headers.get('Origin'):
        raise HTTPException(403,'Cross-origin writes are disabled')

@app.middleware('http')
async def guard(req,call_next):
    if req.url.path.startswith('/api/'):
        try:auth(req)
        except HTTPException as e:return Response(json.dumps({'detail':e.detail}),status_code=e.status_code,media_type='application/json')
    return await call_next(req)

def probe():
    s=settings(); cap={'quasar':QuasarAdapter().capabilities(),'glagol':GlagolAdapter().capabilities(),'adb':ADBAdapter().capabilities(),'lighting':LightingAdapter().capabilities()}
    if s['mode']=='mock':return {'connected':True,'mode':'mock','capabilities':cap,'device':'Mock Station Light'}
    if s['mode']=='ssh' and s['ip']:
        cap['ssh']=SSHAdapter(s['ip']).capabilities();return {'connected':cap['ssh']['system'],'mode':'ssh','capabilities':cap,'device':s['ip']}
    return {'connected':False,'mode':s['mode'],'capabilities':cap,'device':s['ip']}
@app.get('/api/status')
def status():return probe()
@app.get('/api/system')
def system():
    s=settings()
    if s['mode']=='mock':return {'uptime_seconds':10420,'ram_total_kb':238000,'ram_available_kb':105000,'temperature_c':52,'free_kb':520000,'wifi_dbm':None,'cpu_percent':None,'quasar_version':None,'mock':True}
    if s['mode']=='ssh' and s['ip']:
        try:return SystemAdapter(SSHAdapter(s['ip'])).read()
        except Exception:raise HTTPException(503,'Device unavailable')
    raise HTTPException(501,'System monitoring unsupported for this connection')
@app.get('/api/player')
def player():return {'supported':False,'playing':None,'title':None,'artist':None,'cover':None,'progress':None,'volume':None}
@app.post('/api/player/control')
def control(body:Control):
    if body.action not in ('play','pause','next','previous','mute','volume','text'):raise HTTPException(422,'Unsupported action')
    raise HTTPException(501,'Player command not verified for first-generation Light')
@app.get('/api/lighting')
def lighting():return {'supported':False,'color':None,'brightness':None,'zones':[],'restore':False}
@app.post('/api/lighting')
def set_lighting(body:Lighting):raise HTTPException(501,'LED sysfs interface not verified for first-generation Light')
@app.get('/api/settings')
def get_settings():return settings()
@app.post('/api/settings')
def set_settings(body:Config):
    if body.mode not in ('mock','ssh'):raise HTTPException(422,'Connection method unsupported')
    if body.mode=='ssh':
        try:
            addr=ipaddress.ip_address(body.ip)
            if not addr.is_private:raise ValueError()
        except ValueError:raise HTTPException(422,'A private IPv4 or IPv6 address is required')
    save(body.model_dump());return {'saved':True,'status':probe()}
@app.get('/api/health')
def health():return {'ok':True}
@app.get('/')
def home():return FileResponse(ROOT/'web'/'index.html')
