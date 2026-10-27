import asyncio, subprocess, time, io
from playwright.async_api import async_playwright
from PIL import Image, ImageStat
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/gen/'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8767','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':800}); errs=[]
            pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8767/index.html'); await pg.wait_for_timeout(600)
            await pg.locator('#shelf .cover[data-open="0"]').click(); await pg.wait_for_timeout(1500)
            frames=[]
            await pg.locator('#next').click()
            t0=time.time()
            for i in range(14):
                buf=await pg.locator('#pic').screenshot(); frames.append((round(time.time()-t0,2),Image.open(io.BytesIO(buf)).convert('L')))
                await pg.wait_for_timeout(60)
            for t,im in frames: print(t, round(ImageStat.Stat(im).mean[0],1))
            strip=Image.new('L',(14*160,90))
            for i,(t,im) in enumerate(frames): strip.paste(im.resize((160,90)),(i*160,0))
            strip.save(O+'trans_strip.png')
            n=await pg.evaluate("document.querySelectorAll('#pic svg').length")
            await pg.locator('#text .w').first.click(); await pg.wait_for_timeout(400)
            hl=await pg.evaluate("document.querySelectorAll('#pic svg .hl').length")
            print('svgs after:',n,'highlighted:',hl,'errors:',errs); await b.close()
    finally: srv.terminate()
asyncio.run(main())
