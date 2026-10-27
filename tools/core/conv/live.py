import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900})
        msgs=[]; pg.on('console',lambda m:msgs.append(m.text)); pg.on('pageerror',lambda e:msgs.append('ERR '+str(e)))
        try:
            r=await pg.goto('https://claude.ai/artifact/HnBxe4UhYPBTNUTFQuZfZV',timeout=40000); print('status',r.status if r else None)
        except Exception as e: print('goto fail',e); return
        await pg.wait_for_timeout(8000)
        print([f.url[:100] for f in pg.frames]); print(msgs[:20])
        await pg.screenshot(path='conv/live.png')
asyncio.run(main())
