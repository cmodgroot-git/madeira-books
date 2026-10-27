import asyncio, subprocess, time, json, os
from playwright.async_api import async_playwright
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
D=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O=S+'b10/actall/'; os.makedirs(O,exist_ok=True)
IDS=['manha','sabado','domingo','jantar','passeio','pico','seixal','casa','garajau','novacasa']
ACT=json.load(open(S+'gen/act.json'))
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8798','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    errs=[]; miss=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900}); pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8798/index.html'); await pg.wait_for_timeout(1000)
            for k in [x for x in sorted(ACT, key=lambda s:(IDS.index(s.split(':')[0]),int(s.split(':')[1]))) if x in ('domingo:2:caminhar','garajau:6:secam','garajau:7:palmas','novacasa:1:partese')]:
                sid,pi,key=k.split(':')
                await pg.evaluate(f"go({IDS.index(sid)},{pi})"); await pg.wait_for_timeout(900)
                w=pg.locator(f'#text .w[data-k="{key}"]')
                if await w.count()==0: miss.append(k); continue
                await w.first.click(); await pg.wait_for_timeout(800)
                n=await pg.evaluate("()=>[document.querySelectorAll('#pic .actfx path').length,document.querySelectorAll('#pic .act-move,#pic .act-hold,#pic .act-rest').length,document.querySelectorAll('#pic .actplate').length]")
                await pg.locator('#pic').screenshot(path=O+k.replace(':','_')+'.png')
                print(k,n)
            print('missing',miss,'errors',errs)
    finally: srv.terminate()
asyncio.run(main())
