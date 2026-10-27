import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8774','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1400,'height':1000})
            await pg.goto('http://127.0.0.1:8774/index.html'); await pg.wait_for_timeout(600)
            await pg.locator('#shelf .cover[data-open="0"]').click(); await pg.wait_for_timeout(500)
            await pg.locator('#tiles .tile').nth(0).click(); await pg.wait_for_timeout(2600)
            for k in ['rita','sol']:
                await pg.locator(f'#text .w[data-k="{k}"]').first.click(); await pg.wait_for_timeout(700)
                print(k, await pg.evaluate("""()=>{const s=document.querySelector('#pic svg.photo');return s.getAttribute('class')+' | '+[...s.querySelectorAll('.o')].map(g=>g.getAttribute('class')+':'+getComputedStyle(g).opacity).join(', ')}"""))
                print(await pg.evaluate("""()=>{const s=document.querySelector('#pic svg.photo');const g=s.querySelector('.o.hl');const u=g.querySelector('use');const cp=u.getAttribute('clip-path');const id=cp.slice(5,-1);return [cp,document.querySelectorAll('#'+id).length,document.getElementById(id).innerHTML.slice(0,200),getComputedStyle(g).transform,getComputedStyle(g).transformOrigin, getComputedStyle(s.querySelector('.dimmer')).opacity].join(' || ')}"""))
                await pg.locator('#pic').screenshot(path=f'conv/dbg_{k}.png')
                await pg.wait_for_timeout(2500)
            await b.close()
    finally: srv.terminate()
asyncio.run(main())
