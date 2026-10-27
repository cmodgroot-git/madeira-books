import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b10/fit/'
import os; os.makedirs(O,exist_ok=True)
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8797','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch()
            for name,vp in [('big',{'width':1920,'height':1080}),('phone',{'width':390,'height':844})]:
                pg=await b.new_page(viewport=vp); pg.on('pageerror',lambda e:errs.append(str(e)))
                await pg.goto('http://127.0.0.1:8797/index.html'); await pg.wait_for_timeout(1000)
                await pg.locator('#shelf .cover[data-open="9"]').click(); await pg.wait_for_timeout(1500)
                await pg.keyboard.press('ArrowRight'); await pg.wait_for_timeout(1200)
                r=await pg.evaluate("()=>{const p=document.getElementById('pic').getBoundingClientRect(),t=document.querySelector('#reader .tools').getBoundingClientRect(),x=document.getElementById('text').getBoundingClientRect();return {picTop:Math.round(p.top),picBot:Math.round(p.bottom),textBot:Math.round(x.bottom),toolsBot:Math.round(t.bottom),vh:innerHeight}}")
                print(name,r)
                await pg.screenshot(path=O+f'{name}.png')
                await pg.close()
            print('errors',errs)
    finally: srv.terminate()
asyncio.run(main())
