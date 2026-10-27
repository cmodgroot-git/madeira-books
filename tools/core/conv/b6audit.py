"""Book 6 audit: motion heat maps from real browser frames, every new word's meaning (Ctrl-click), phone layout."""
import asyncio, subprocess, time, io, json, numpy as np
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv/'
NEW=set(json.load(open(O+'gloss6.json')).keys())
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8782','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    heat=[]; gl={}; errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900})
            pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8782/index.html'); await pg.wait_for_timeout(700)
            await pg.locator('#shelf .cover[data-open="5"]').click(); await pg.wait_for_timeout(900)
            for pi in range(8):
                await pg.evaluate(f'go(5,{pi})'); await pg.wait_for_timeout(1800)
                fr=[]
                for k in range(10):
                    fr.append(np.asarray(Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('RGB'),np.float32)); await pg.wait_for_timeout(450)
                A=np.stack(fr); h=(A.max(0)-A.min(0)).max(2)
                base=Image.fromarray(fr[0].astype(np.uint8)); hm=np.clip(h*6,0,255).astype(np.uint8)
                ov=Image.fromarray((fr[0]*.35).astype(np.uint8)); red=Image.new('RGB',ov.size,(255,40,40))
                ov.paste(red,(0,0),Image.fromarray(hm))
                ov=ov.resize((480,int(480*ov.height/ov.width))); ImageDraw.Draw(ov).text((4,2),f'p{pi+1} moving px {int((h>12).sum())}',fill=(255,255,0)); heat.append(ov)
                ws=pg.locator('#text .w'); n=await ws.count()
                for k in range(n):
                    key=await ws.nth(k).get_attribute('data-k')
                    for kk in key.split():
                        if kk in NEW and kk not in gl:
                            await ws.nth(k).click(modifiers=['Control']); await pg.wait_for_timeout(250)
                            gl[kk]=await pg.locator('.gloss').inner_text() if await pg.locator('.gloss').count() else None
                            await pg.mouse.click(5,5); await pg.wait_for_timeout(150)
            ph=await b.new_page(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
            await ph.goto('http://127.0.0.1:8782/index.html'); await ph.wait_for_timeout(700)
            await ph.screenshot(path=O+'b6_phone_shelf.png')
            await ph.locator('#shelf .cover[data-open="5"]').click(); await ph.wait_for_timeout(900)
            for pi in (1,4):
                await ph.evaluate(f'go(5,{pi})'); await ph.wait_for_timeout(900); await ph.screenshot(path=O+f'b6_phone_p{pi+1}.png',full_page=True)
    finally: srv.terminate()
    S=Image.new('RGB',(480*4,heat[0].height*2))
    for n,t in enumerate(heat): S.paste(t,((n%4)*480,(n//4)*heat[0].height))
    S.save(O+'b6_heat.jpg',quality=85)
    miss=[k for k in sorted(NEW) if not gl.get(k)]
    print('meanings shown',len([k for k in gl if gl[k]]),'of',len(NEW),'missing',miss); print(json.dumps(gl,ensure_ascii=False)[:1500]); print('errors',errs)
asyncio.run(main())
