import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv/'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8792','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch()
            for name,vp in [('desk',{'width':1300,'height':900}),('phone',{'width':390,'height':844})]:
                pg=await b.new_page(viewport=vp); pg.on('pageerror',lambda e:errs.append(str(e)))
                await pg.goto('http://127.0.0.1:8792/index.html'); await pg.wait_for_timeout(1500)
                await pg.screenshot(path=O+f'b8_shelf_{name}.png',full_page=True)
                await pg.locator('#shelf .cover[data-open="9"]').click(); await pg.wait_for_timeout(1500)
                await pg.screenshot(path=O+f'b8_reader_{name}.png',full_page=True)
                w=pg.locator('#text .w[data-k="carrinha"]').first; await w.click(modifiers=['Control']); await pg.wait_for_timeout(500)
                print(name,'gloss:',await pg.locator('.gloss').inner_text() if await pg.locator('.gloss').count() else None)
                imgs=await pg.evaluate("[...document.querySelectorAll('#tiles img')].map(i=>i.complete&&i.naturalWidth>0)")
                print(name,'thumbs ok',all(imgs),len(imgs))
            await b.close()
    finally: srv.terminate()
    print('errors',errs)
asyncio.run(main())
