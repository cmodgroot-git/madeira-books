import asyncio, subprocess, time, io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv/'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8781','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    tiles=[]; errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900})
            pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8781/index.html'); await pg.wait_for_timeout(700)
            await pg.screenshot(path=O+'b6_shelf.png')
            await pg.locator('#shelf .cover[data-open="5"]').click(); await pg.wait_for_timeout(900)
            await pg.add_style_tag(content='.pic svg.photo{animation:none!important}')
            for pi in range(8):
                await pg.evaluate(f'go(5,{pi})'); await pg.wait_for_timeout(900)
                ws=pg.locator('#text .w'); n=await ws.count(); seen=set()
                for k in range(n):
                    key=await ws.nth(k).get_attribute('data-k')
                    if key in seen: continue
                    seen.add(key); await ws.nth(k).click(); await pg.wait_for_timeout(750)
                    im=Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('RGB').resize((400,224))
                    ImageDraw.Draw(im).rectangle([0,0,400,16],fill=(0,0,0)); ImageDraw.Draw(im).text((4,2),f'p{pi+1} {key}',fill=(255,255,0))
                    tiles.append(im); await pg.wait_for_timeout(2000)
            # meaning check
            await pg.evaluate('go(5,4)'); await pg.wait_for_timeout(700)
            await pg.locator('#text .w').nth(1).click(modifiers=['Control']); await pg.wait_for_timeout(300)
            g=await pg.locator('.gloss').inner_text() if await pg.locator('.gloss').count() else None
            print('gloss:',g)
            await pg.screenshot(path=O+'b6_reader.png')
    finally: srv.terminate()
    cols=6; rows=(len(tiles)+cols-1)//cols; S=Image.new('RGB',(400*cols,224*rows))
    for n,t in enumerate(tiles): S.paste(t,((n%cols)*400,(n//cols)*224))
    S.save(O+'b6_taps.jpg',quality=80); print(len(tiles),'taps; errors',errs)
asyncio.run(main())
