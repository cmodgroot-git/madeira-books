import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv/'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8777','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':860},locale='en-GB')
            errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8777/index.html'); await pg.wait_for_timeout(700)
            await pg.click('#langbtn'); await pg.wait_for_timeout(300)
            await pg.screenshot(path=O+'lang_open.png',clip={'x':0,'y':0,'width':1200,'height':520})
            await pg.click('[data-lang="de"]'); await pg.wait_for_timeout(400)
            await pg.screenshot(path=O+'lang_de.png',clip={'x':0,'y':0,'width':1200,'height':520})
            await pg.locator('#shelf .cover[data-open="0"]').click(); await pg.wait_for_timeout(900)
            # ctrl click on first word
            await pg.locator('#text .w').nth(1).click(modifiers=['Control']); await pg.wait_for_timeout(500)
            await pg.screenshot(path=O+'lang_ctrl.png')
            # visit the page 5 times
            for _ in range(5):
                await pg.click('#next'); await pg.wait_for_timeout(150); await pg.click('#prev'); await pg.wait_for_timeout(150)
            await pg.wait_for_timeout(400)
            n=await pg.locator('.chip .gq').count(); print('hint buttons',n)
            if n: await pg.locator('.chip .gq').first.click(); await pg.wait_for_timeout(300)
            await pg.screenshot(path=O+'lang_hint.png')
            print('errors',errs)
    finally: srv.terminate()
asyncio.run(main())
