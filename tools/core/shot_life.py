import asyncio, subprocess, time, io, sys
from playwright.async_api import async_playwright
from PIL import Image, ImageChops
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/gen/'
book,page,name=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8768','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1600,'height':1000}); errs=[]
            pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8768/index.html'); await pg.wait_for_timeout(500)
            await pg.add_style_tag(content='.pic svg.photo{animation:none!important}')  # freeze drift so frames compare
            await pg.locator(f'#shelf .cover[data-open="{book}"]').click(); await pg.wait_for_timeout(400)
            await pg.locator('#tiles .tile').nth(page).click(); await pg.wait_for_timeout(2600)
            fr=[]
            for i in range(3):
                fr.append(Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('RGB')); await pg.wait_for_timeout(1300)
            fr[0].save(O+f'{name}_a.png'); fr[2].save(O+f'{name}_b.png')
            diff=ImageChops.difference(fr[0],fr[2]).convert('L').point(lambda v:255 if v>6 else 0)
            diff.save(O+f'{name}_diff.png')
            # rough frame-rate check while the effects run
            fps=await pg.evaluate("new Promise(r=>{let n=0,t0=performance.now();function f(t){n++;if(t-t0<2000)requestAnimationFrame(f);else r(n/((t-t0)/1000))}requestAnimationFrame(f)})")
            print('fps~',round(fps),'errors:',errs); await b.close()
    finally: srv.terminate()
asyncio.run(main())
