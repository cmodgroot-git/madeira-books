import asyncio, subprocess, time, re, os
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
h=open(D+'/index.html').read()
refs=sorted(set(re.findall(r'img/[A-Za-z0-9_/]+\.(?:jpg|webp)',h)))
missing=[r for r in refs if not os.path.exists(D+'/'+r)]
print('image refs',len(refs),'missing on disk',missing[:10])
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8791','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    errs=[]; bad=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1300,'height':900})
            pg.on('pageerror',lambda e:errs.append(str(e)))
            pg.on('response',lambda r: bad.append(r.url) if r.status>=400 else None)
            await pg.goto('http://127.0.0.1:8791/index.html'); await pg.wait_for_timeout(800)
            n=await pg.evaluate('STORIES.length'); print('books',n)
            for si in range(n):
                np_=await pg.evaluate(f'STORIES[{si}].pages.length')
                await pg.locator(f'#shelf .cover[data-open="{si}"]').click(); await pg.wait_for_timeout(500)
                for pi in range(np_):
                    await pg.evaluate(f'go({si},{pi})'); await pg.wait_for_timeout(350)
                print('book',si+1,'pages',np_,'ok')
                await pg.goto('http://127.0.0.1:8791/index.html'); await pg.wait_for_timeout(500)
    finally: srv.terminate()
    print('page errors',errs[:5]); print('failed loads',sorted(set(bad))[:10])
asyncio.run(main())
