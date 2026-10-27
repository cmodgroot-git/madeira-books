import asyncio, subprocess, time
from playwright.async_api import async_playwright
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4'
STUB="""(()=>{window.__rates=[];const ss={getVoices:()=>[],cancel(){const u=this._u;this._u=null;if(u&&u.onend)u.onend({})},speak(u){window.__rates.push(u.rate);this._u=u;setTimeout(()=>{u.onstart&&u.onstart({})},30)}};
Object.defineProperty(window,'speechSynthesis',{value:ss});window.SpeechSynthesisUtterance=function(t){this.text=t}})();"""
async def main():
    srv=subprocess.Popen(['python3','-m','http.server','8803','--bind','127.0.0.1'],cwd=D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
    errs=[]
    try:
        async with async_playwright() as p:
            b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1366,'height':650}); pg.on('pageerror',lambda e:errs.append(str(e)))
            await pg.add_init_script(STUB)
            await pg.goto('http://127.0.0.1:8803/index.html'); await pg.wait_for_timeout(800)
            await pg.evaluate("go(9,1)"); await pg.wait_for_timeout(1200)
            await pg.locator('body').click(position={'x':5,'y':5})
            await pg.keyboard.press('l'); await pg.wait_for_timeout(300)
            await pg.keyboard.press('s'); await pg.wait_for_timeout(300)
            st=await pg.evaluate("()=>[window.__rates, document.getElementById('slow').getAttribute('aria-pressed'), document.getElementById('slowlbl').textContent, document.getElementById('say').classList.contains('reading')]")
            await pg.locator('#reader .tools').screenshot(path='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b10/slowbtn.png')
            await pg.reload(); await pg.wait_for_timeout(800); await pg.evaluate("go(9,1)"); await pg.wait_for_timeout(800)
            st2=await pg.evaluate("()=>document.getElementById('slow').getAttribute('aria-pressed')")
            print(st, 'after reload', st2, errs)
    finally: srv.terminate()
asyncio.run(main())
