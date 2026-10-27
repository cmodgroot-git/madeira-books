import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
W={1:['banco','cao','estrada'],2:['carro'],7:['guardasol']}
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8784','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900})
            await pg.goto('http://127.0.0.1:8784/index.html'); await pg.wait_for_timeout(700)
            await pg.locator('#shelf .cover[data-open="5"]').click(); await pg.wait_for_timeout(900)
            for pi,ks in W.items():
                await pg.evaluate(f'go(5,{pi})'); await pg.wait_for_timeout(900)
                for k in ks:
                    w=pg.locator(f'#text .w[data-k~="{k}"]').first
                    await w.scroll_into_view_if_needed(); await pg.wait_for_timeout(300); y0=await pg.evaluate('scrollY')
                    await pg.evaluate('window.__n=0;addEventListener("scroll",()=>window.__n++)')
                    await w.click(modifiers=['Control']); await pg.wait_for_timeout(500)
                    print('scrollY',y0,await pg.evaluate('scrollY'),'scroll events',await pg.evaluate('__n'))
                    print(k, await pg.locator('.gloss').inner_text() if await pg.locator('.gloss').count() else None)
                    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
    finally: srv.terminate()
asyncio.run(main())
