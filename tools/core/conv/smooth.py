import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8799','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':430,'height':700})
            await pg.goto('http://127.0.0.1:8799/index.html'); await pg.wait_for_timeout(800)
            await pg.evaluate("go(9,6)"); await pg.wait_for_timeout(1200)
            await pg.evaluate("go(9,1)")
            ws=[]
            for i in range(10):
                ws.append(await pg.evaluate("()=>[...document.querySelectorAll('#pic > svg')].map(s=>Math.round(s.getBoundingClientRect().width)+(s.classList.contains('incoming')?'i':'')).join('|')")); await pg.wait_for_timeout(50)
            print(ws)
    finally: srv.terminate()
asyncio.run(main())
