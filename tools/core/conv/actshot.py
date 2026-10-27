import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b10/act/'
import os; os.makedirs(O,exist_ok=True)
CASES=[(1,4,'passa')]
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8794','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch()
            for bk,pi,k in CASES:
                pg=await b.new_page(viewport={'width':1300,'height':900}); pg.on('pageerror',lambda e:errs.append(str(e)))
                await pg.goto('http://127.0.0.1:8794/index.html'); await pg.wait_for_timeout(1000)
                await pg.locator(f'#shelf .cover[data-open="{bk}"]').click(); await pg.wait_for_timeout(1000)
                await pg.locator('#tiles button, #tiles .tile').nth(pi).click(); await pg.wait_for_timeout(1200)
                await pg.locator(f'#text .w[data-k="{k}"]').first.click()
                for t,ms in enumerate([250,600,800]):
                    await pg.wait_for_timeout(ms); await pg.locator('.pic').first.screenshot(path=O+f'{k}{t}.png')
                await pg.locator('#text').screenshot(path=O+f'{k}_text.png')
                await pg.close()
            print('errors',errs)
    finally: srv.terminate()
asyncio.run(main())
