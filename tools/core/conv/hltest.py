import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8779','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch()
            for scheme in ['light','dark']:
                pg=await b.new_page(viewport={'width':1300,'height':900},color_scheme=scheme)
                await pg.goto('http://127.0.0.1:8779/index.html'); await pg.wait_for_timeout(600)
                await pg.locator('#shelf .cover[data-open="1"]').click(); await pg.wait_for_timeout(800)
                await pg.locator('#text .w').nth(2).click(); await pg.wait_for_timeout(500)
                await pg.locator('.page').screenshot(path=f'conv/hl_{scheme}.png')
    finally: srv.terminate()
asyncio.run(main())
