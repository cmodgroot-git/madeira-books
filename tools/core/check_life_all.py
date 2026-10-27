import asyncio, subprocess, time, io
from playwright.async_api import async_playwright
from PIL import Image, ImageChops
D = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/gen/'
PAGES = [(0, i) for i in range(9)] + [(1, i) for i in range(8)] + [(2, i) for i in range(8)] + [(3, i) for i in range(8)]

async def main():
    srv = subprocess.Popen(['python3', '-m', 'http.server', '8769', '--bind', '127.0.0.1'], cwd=D,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
    tiles = []
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1600, 'height': 1000}); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8769/index.html'); await pg.wait_for_timeout(500)
            await pg.add_style_tag(content='.pic svg.photo{animation:none!important}')
            cur_book = None
            for book, page in PAGES:
                if book != cur_book:
                    if cur_book is not None:
                        await pg.locator('#back').click(); await pg.wait_for_timeout(300)
                    await pg.locator(f'#shelf .cover[data-open="{book}"]').click(); await pg.wait_for_timeout(400)
                    cur_book = book
                await pg.locator("#tiles .tile").nth(page).click(); await pg.wait_for_timeout(2600)
                a = Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('RGB')
                await pg.wait_for_timeout(2600)
                c = Image.open(io.BytesIO(await pg.locator('#pic').screenshot())).convert('RGB')
                fps = await pg.evaluate("new Promise(r=>{let n=0,t0=performance.now();function f(t){n++;if(t-t0<1200)requestAnimationFrame(f);else r(n/((t-t0)/1000))}requestAnimationFrame(f)})")
                d = ImageChops.difference(a, c).convert('L').point(lambda v: 255 if v > 7 else 0)
                tint = Image.new('RGB', a.size, (255, 40, 40))
                ov = Image.composite(tint, a, d.point(lambda v: 150 if v else 0))
                tiles.append((f'b{book+1}p{page+1}', ov.resize((480, 270)), round(fps)))
            print('errors:', errs)
            await b.close()
    finally:
        srv.terminate()
    for part in range(0, len(tiles), 6):
        sheet = Image.new('RGB', (960, 3 * 290), 'white')
        from PIL import ImageDraw
        d = ImageDraw.Draw(sheet)
        for i, (n, im, f) in enumerate(tiles[part:part + 6]):
            x, y = (i % 2) * 480, (i // 2) * 290
            sheet.paste(im, (x, y + 18)); d.text((x + 4, y + 2), f'{n}  fps~{f}', fill=(0, 0, 0))
        sheet.save(O + f'lifecheck_{part//6}.jpg', quality=85)
    print([(n, f) for n, _, f in tiles])

asyncio.run(main())
