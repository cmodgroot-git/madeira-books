import asyncio, subprocess, time
from playwright.async_api import async_playwright
D = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
OUT = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/gen/'

async def shoot(page, book, pageno, word, name):
    await page.goto('http://127.0.0.1:8765/index.html')
    await page.wait_for_timeout(500)
    await page.locator('#shelf .cover[data-open="%d"]' % book).click()
    await page.wait_for_timeout(300)
    await page.locator('#tiles .tile').nth(pageno).click()
    await page.wait_for_timeout(800)
    await page.locator('#text .w', has_text=word).first.click()
    await page.wait_for_timeout(700)
    await page.locator('#pic').screenshot(path=OUT + name)

async def main():
    srv = subprocess.Popen(['python3', '-m', 'http.server', '8765', '--bind', '127.0.0.1'], cwd=D,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch()
            page = await b.new_page(viewport={'width': 1200, 'height': 800})
            errs = []
            page.on('pageerror', lambda e: errs.append(str(e)))
            await shoot(page, 0, 8, 'olha', 'gaze_b1p9.png')
            await shoot(page, 1, 4, 'Olha', 'gaze_b2p5.png')
            await shoot(page, 0, 6, 'bananas', 'hl_b1p7.png')
            await shoot(page, 0, 3, 'manteiga', 'hl_b1p4.png')
            print('errors:', errs)
            await b.close()
    finally:
        srv.terminate()

asyncio.run(main())
