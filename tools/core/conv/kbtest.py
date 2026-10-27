import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8800','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1366,'height':650}); pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8800/index.html'); await pg.wait_for_timeout(800)
            await pg.evaluate("go(9,0)"); await pg.wait_for_timeout(5000)
            await pg.keyboard.press('ArrowRight')
            out=[]
            for i in range(8):
                out.append(await pg.evaluate("()=>[...document.querySelectorAll('#pic > svg')].map(s=>getComputedStyle(s).transform.split(',')[0].slice(7,13)+(s.classList.contains('incoming')?'i':'')).join('|')"))
                await pg.wait_for_timeout(100)
            print(out, errs)
    finally: srv.terminate()
asyncio.run(main())
