import asyncio, subprocess, time, io, sys, numpy as np
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv/'
PAGES=[(10,0)]
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8782','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    tiles=[]; heats=[]; errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900})
            pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8782/index.html'); await pg.wait_for_timeout(700)
            await pg.locator('#shelf .cover[data-open="0"]').click(); await pg.wait_for_timeout(900)
            await pg.add_style_tag(content='.pic svg.photo{animation:none!important}')
            for bk,pi in PAGES:
                await pg.evaluate(f'go({bk},{pi})'); await pg.wait_for_timeout(1500)
                shots=[]
                for k in range(10):
                    shots.append(np.asarray(Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('L'),np.float32)); await pg.wait_for_timeout(450)
                st=np.stack(shots); hm=np.clip((st.max(0)-st.min(0))*4,0,255).astype(np.uint8)
                base=Image.fromarray(shots[0].astype(np.uint8)).convert('RGB').resize((400,224)); hmi=Image.fromarray(hm).convert('RGB').resize((400,224))
                heats.append(Image.blend(base,hmi,.7))
                ws=pg.locator('#text .w'); n=await ws.count(); seen=set()
                for k in range(n):
                    key=await ws.nth(k).get_attribute('data-k')
                    if key in seen: continue
                    seen.add(key); await ws.nth(k).click(); await pg.wait_for_timeout(750)
                    im=Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('RGB').resize((400,224))
                    ImageDraw.Draw(im).rectangle([0,0,400,16],fill=(0,0,0)); ImageDraw.Draw(im).text((4,2),f'b{bk+1}p{pi+1} {key}',fill=(255,255,0))
                    tiles.append(im); await pg.wait_for_timeout(2000)
            await b.close()
    finally: srv.terminate()
    def sheet(ts,cols,f):
        S=Image.new('RGB',(400*cols,224*((len(ts)+cols-1)//cols)))
        for i,t in enumerate(ts): S.paste(t,((i%cols)*400,(i//cols)*224))
        S.save(O+f,quality=82)
    sheet(tiles,5,'chk11_taps.jpg'); sheet(heats,4,'chk11_heat.jpg'); print('words',len(tiles),'errors',errs)
asyncio.run(main())
