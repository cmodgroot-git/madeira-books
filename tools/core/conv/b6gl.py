import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
W={0:['gorro'],1:['luzes'],2:['limpaparabrisas'],3:['branco'],4:['radar'],5:['pessoas'],6:['corrimao']}
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8783','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900})
            await pg.goto('http://127.0.0.1:8783/index.html'); await pg.wait_for_timeout(700)
            await pg.locator('#shelf .cover[data-open="5"]').click(); await pg.wait_for_timeout(900)
            for pi,ks in W.items():
                await pg.evaluate(f'go(5,{pi})'); await pg.wait_for_timeout(900)
                for k in ks:
                    w=pg.locator(f'#text .w[data-k~="{k}"]').first
                    await w.click(modifiers=['Control']); await pg.wait_for_timeout(500)
                    print(k, await pg.locator('.gloss').inner_text() if await pg.locator('.gloss').count() else None)
                    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    finally: srv.terminate()
asyncio.run(main())
