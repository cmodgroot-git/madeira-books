import asyncio, subprocess, time, io
from playwright.async_api import async_playwright
from PIL import Image, ImageChops
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8775','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000})
            await pg.goto('http://127.0.0.1:8775/index.html'); await pg.wait_for_timeout(600)
            await pg.locator('#shelf .cover[data-open="3"]').click(); await pg.wait_for_timeout(500)
            await pg.locator('#tiles .tile').nth(0).click(); await pg.wait_for_timeout(3000)
            a=Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('RGB'); await pg.wait_for_timeout(2700)
            c=Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('RGB')
            d=ImageChops.difference(a,c).convert('L').point(lambda v:255 if v>7 else 0)
            o=a.copy(); o.paste((255,0,0),mask=d); Image.blend(a,o,.6).save('/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv/mot0.jpg',quality=85)
    finally: srv.terminate()
asyncio.run(main())
