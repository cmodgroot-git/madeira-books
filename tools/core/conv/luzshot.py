import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b10/'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8793','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900}); pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8793/index.html'); await pg.wait_for_timeout(1200)
            await pg.locator('#shelf .cover[data-open="9"]').click(); await pg.wait_for_timeout(1200)
            for _ in range(7):
                await pg.get_by_role('button',name='Next').click(); await pg.wait_for_timeout(400)
            await pg.locator('#text .w[data-k="luzes"]').first.click()
            pic=pg.locator('.pic').first
            for t in range(4):
                await pg.wait_for_timeout(400); await pic.screenshot(path=O+f'luz{t}.png')
            print('errors',errs)
    finally: srv.terminate()
asyncio.run(main())
