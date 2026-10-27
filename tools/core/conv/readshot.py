import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
O='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b10/act/'
STUB="""
(()=>{const ss={speaking:false,_u:null,getVoices:()=>[],cancel(){if(this._u&&this._u.onend){const u=this._u;this._u=null;u.onend({})}},
 speak(u){this._u=u;setTimeout(()=>{u.onstart&&u.onstart({});
   if(window.__noBoundary)return;
   const re=/[\\p{L}\\p{N}]+/gu;let m,t=100;while((m=re.exec(u.text))){const i=m.index;setTimeout(()=>{if(this._u===u)u.onboundary&&u.onboundary({name:'word',charIndex:i})},t);t+=260}
   setTimeout(()=>{if(this._u===u){this._u=null;u.onend&&u.onend({})}},t+200)},50)}};
 Object.defineProperty(window,'speechSynthesis',{value:ss});window.SpeechSynthesisUtterance=function(t){this.text=t}})();
"""
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8796','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch()
            for nb in [False, True]:
                pg=await b.new_page(viewport={'width':1300,'height':900}); pg.on('pageerror',lambda e:errs.append(str(e)))
                await pg.add_init_script(STUB + ("window.__noBoundary=true;" if nb else ""))
                await pg.goto('http://127.0.0.1:8796/index.html'); await pg.wait_for_timeout(1000)
                await pg.locator('#shelf .cover[data-open="1"]').click(); await pg.wait_for_timeout(1000)
                await pg.locator('#tiles button, #tiles .tile').nth(4).click(); await pg.wait_for_timeout(1000)
                await pg.locator('body').click(position={'x':5,'y':5}); await pg.keyboard.press('l')
                seq=[]
                for t in range(6):
                    await pg.wait_for_timeout(260)
                    seq.append(await pg.evaluate("()=>{const e=document.querySelector('.say-on');return e?e.textContent:'-'}"))
                    if t==2: await pg.locator('.book, #reader').first.screenshot(path=O+f'read_{int(nb)}.png')
                await pg.keyboard.press('Space'); await pg.wait_for_timeout(600)
                after=await pg.evaluate("()=>[document.querySelectorAll('.say-on').length,document.querySelector('#say').classList.contains('reading')]")
                print('noBoundary' if nb else 'boundary', seq, 'after stop', after)
                await pg.close()
            print('errors',errs)
    finally: srv.terminate()
asyncio.run(main())
