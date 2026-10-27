import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b10/fade/'
import os; os.makedirs(O,exist_ok=True)
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8801','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1366,'height':650})
            await pg.goto('http://127.0.0.1:8801/index.html'); await pg.wait_for_timeout(800)
            await pg.evaluate("go(9,0)"); await pg.wait_for_timeout(2500)
            await pg.keyboard.press('ArrowRight')
            for i in range(6):
                await pg.screenshot(path=O+f'f{i}.png',clip={'x':0,'y':90,'width':1000,'height':560})
                info=await pg.evaluate("()=>[...document.querySelectorAll('#pic > svg')].map(s=>getComputedStyle(s).opacity+(s.classList.contains('incoming')?'i':'')+(s.classList.contains('in')?'n':'')).join('|')")
                print(i,info); await pg.wait_for_timeout(110)
    finally: srv.terminate()
asyncio.run(main())
