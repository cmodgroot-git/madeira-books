import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8778','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page()
            await pg.goto('http://127.0.0.1:8778/index.html'); await pg.wait_for_timeout(600)
            await pg.locator('#shelf .cover[data-open="0"]').click(); await pg.wait_for_timeout(700)
            w=pg.locator('#text .w').nth(1)
            await w.click(modifiers=['Control']); await pg.wait_for_timeout(200)
            print('mac ctrl-click (contextmenu):', await pg.locator('.gloss').inner_text() if await pg.locator('.gloss').count() else None)
            await pg.keyboard.press('Escape')
            await w.click(modifiers=['Alt']); await pg.wait_for_timeout(200)
            print('option-click:', await pg.locator('.gloss').inner_text() if await pg.locator('.gloss').count() else None)
            await pg.keyboard.press('Escape')
            await w.click(modifiers=['Meta']); await pg.wait_for_timeout(200)
            print('bubble box', await pg.locator('.gloss').bounding_box() if await pg.locator('.gloss').count() else None)
            print('cmd-click:', await pg.locator('.gloss').inner_text() if await pg.locator('.gloss').count() else None)
    finally: srv.terminate()
asyncio.run(main())
