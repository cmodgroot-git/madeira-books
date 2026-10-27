import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8771','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
            pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text))
            await pg.goto('http://127.0.0.1:8771/index.html'); await pg.wait_for_timeout(800)
            await pg.locator('#shelf .cover[data-open="3"]').click(); await pg.wait_for_timeout(600)
            for i in [3]:
                await pg.locator('#tiles .tile').nth(i).click(); await pg.wait_for_timeout(4000)
                info=await pg.evaluate("""()=>{const p=document.querySelector('#pic');const v=p.querySelector('g.life svg');return v?[getComputedStyle(v).overflow,v.getAttribute('overflow'),v.parentNode.tagName,JSON.stringify(v.getBoundingClientRect())].join(' '):'none'}""")
                print(i,info)
                await pg.locator('#pic').screenshot(path=f'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv/dom{i}.png')
            print(errs[:10])
    finally: srv.terminate()
asyncio.run(main())
