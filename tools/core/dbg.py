import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8771','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000})
            await pg.goto('http://127.0.0.1:8771/index.html'); await pg.wait_for_timeout(500)
            await pg.locator('#shelf .cover[data-open="1"]').click(); await pg.wait_for_timeout(500)
            await pg.locator('#tiles .tile').nth(3).click(); await pg.wait_for_timeout(2500)
            r=await pg.evaluate("""()=>{const s=document.querySelectorAll('#pic svg');const sv=s[s.length-1];
              return {n:s.length, label:sv.getAttribute('aria-label'), img:sv.querySelector('image').getAttribute('href'),
                life:!!sv.querySelector('.life'), uses:[...sv.querySelectorAll('.life use')].map(u=>u.getAttribute('href')),
                hasTarget:!!sv.querySelector('#sabado3ph'), page:document.getElementById('pno').textContent, title:document.getElementById('title').textContent}}""")
            print(r)
            import io
            from PIL import Image, ImageChops
            await pg.add_style_tag(content='.pic svg.photo{animation:none!important}')
            async def diff():
                a=Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('L'); await pg.wait_for_timeout(3000)
                c=Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('L')
                return ImageChops.difference(a,c).getextrema()
            print('as is', await diff())
            print('anim time', await pg.evaluate("document.querySelector('#pic svg:last-of-type').getCurrentTime()"))
            print('paused?', await pg.evaluate("document.querySelector('#pic svg:last-of-type').animationsPaused()"))
            await pg.evaluate("document.querySelector('#pic .life').setAttribute('data-x','1')")
            print('noop poke', await diff())
            await b.close()
    finally: srv.terminate()
asyncio.run(main())
