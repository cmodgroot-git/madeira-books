import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8802','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch()
            for vp in [{'width':800,'height':520},{'width':1150,'height':900}]:
                pg=await b.new_page(viewport=vp)
                await pg.goto('http://127.0.0.1:8802/index.html'); await pg.wait_for_timeout(800)
                await pg.evaluate("go(9,0)"); await pg.wait_for_timeout(2500)
                await pg.keyboard.press('ArrowRight'); xs=[]
                for i in range(25):
                    r=await pg.evaluate("()=>[...document.querySelectorAll('#pic > svg')].map(s=>{const b=s.getBoundingClientRect();return Math.round(b.left)+':'+Math.round(b.width)}).join('|')")
                    xs.append(r); await pg.wait_for_timeout(30)
                print(vp['width'],xs); await pg.close()
    finally: srv.terminate()
asyncio.run(main())
