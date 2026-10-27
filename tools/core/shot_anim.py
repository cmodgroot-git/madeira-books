import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/gen/'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8766','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':800}); errs=[]
            pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8766/index.html'); await pg.wait_for_timeout(150)
            await pg.screenshot(path=O+'an_lib_early.png'); await pg.wait_for_timeout(900)
            await pg.locator('#shelf .cover[data-open="0"]').hover(); await pg.wait_for_timeout(600)
            await pg.screenshot(path=O+'an_lib.png')
            await pg.locator('#shelf .cover[data-open="0"]').click(); await pg.wait_for_timeout(200)
            await pg.screenshot(path=O+'an_page_early.png'); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=O+'an_page.png')
            t=await pg.evaluate("getComputedStyle(document.querySelector('.pic svg')).animationName")
            await pg.locator('#text .w').first.click(); await pg.wait_for_timeout(500)
            await pg.screenshot(path=O+'an_tap.png')
            print('anim:',t,'errors:',errs); await b.close()
    finally: srv.terminate()
asyncio.run(main())
