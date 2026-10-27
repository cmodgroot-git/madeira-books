import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8795','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900})
            await pg.goto('http://127.0.0.1:8795/index.html'); await pg.wait_for_timeout(1000)
            await pg.locator('#shelf .cover[data-open="1"]').click(); await pg.wait_for_timeout(1000)
            await pg.locator('#tiles button, #tiles .tile').nth(4).click(); await pg.wait_for_timeout(1200)
            await pg.locator('#text .w[data-k="passa"]').first.click(); await pg.wait_for_timeout(900)
            print(await pg.evaluate("""()=>{const s=[...document.querySelectorAll('#pic svg')];return s.map(x=>({cls:x.getAttribute('class'),fx:x.querySelectorAll('.actfx').length,d:[...x.querySelectorAll('.actfx path')].slice(0,2).map(p=>p.getAttribute('d')+' '+getComputedStyle(p).strokeDashoffset+' '+getComputedStyle(p).display),mv:x.querySelectorAll('.act-move').length, tr:[...x.querySelectorAll('.act-move')].map(e=>getComputedStyle(e).transform)}))}"""))
    finally: srv.terminate()
asyncio.run(main())
