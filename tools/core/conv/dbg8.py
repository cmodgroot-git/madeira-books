import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8791','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900})
            await pg.goto('http://127.0.0.1:8791/index.html'); await pg.wait_for_timeout(700)
            await pg.locator('#shelf .cover[data-open="0"]').click(); await pg.wait_for_timeout(900)
            for bk,pi,k in [(7,0,'telemovel'),(7,4,'telemovel'),(5,6,'cha'),(7,6,'sorri')]:
                await pg.evaluate(f'go({bk},{pi})'); await pg.wait_for_timeout(1500)
                print(bk,pi,k, await pg.evaluate(f'''(()=>{{const ws=[...document.querySelectorAll('#text .w')].map(w=>w.dataset.k);const svg=document.querySelector('#pic svg:last-of-type');return [ws.join(','),svg.querySelectorAll('.k-{k}').length]}})()'''))
                import numpy as np, io
                from PIL import Image
                a=np.asarray(Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('L'),float).mean()
                w=pg.locator(f'#text .w[data-k="{k}"]').first; await w.click(); await pg.wait_for_timeout(600)
                c=np.asarray(Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('L'),float).mean()
                await pg.evaluate(f"light('{k}')"); await pg.wait_for_timeout(600)
                d=np.asarray(Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('L'),float).mean()
                print('mean before',round(a),'after click',round(c),'after light()',round(d), await pg.evaluate("document.querySelectorAll('#pic svg').length"))
                await pg.locator('#pic').screenshot(path=f'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv/dbg_{bk}_{pi}_{k}.png')
            await b.close()
    finally: srv.terminate()
asyncio.run(main())
