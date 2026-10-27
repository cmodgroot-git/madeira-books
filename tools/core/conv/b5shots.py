import asyncio, subprocess, time, io
from playwright.async_api import async_playwright
from PIL import Image
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8782','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    rows=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900})
            await pg.goto('http://127.0.0.1:8782/index.html'); await pg.wait_for_timeout(600)
            await pg.locator('#shelf .cover[data-open="4"]').click(); await pg.wait_for_timeout(600)
            await pg.add_style_tag(content='.pic svg.photo{animation:none!important}')
            for pi in (1,2,3,5):
                await pg.evaluate(f'go(4,{pi})'); await pg.wait_for_timeout(1500); row=[]
                for _ in range(3):
                    row.append(Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('RGB')); await pg.wait_for_timeout(330)
                rows.append(row)
    finally: srv.terminate()
    w,h=rows[0][0].size; o=Image.new('RGB',(w*3,h*len(rows)))
    for r,row in enumerate(rows):
        for c,im in enumerate(row): o.paste(im,(c*w,r*h))
    o.resize((w*3//2,h*len(rows)//2)).save('/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv/b5shots.jpg',quality=85)
asyncio.run(main())
