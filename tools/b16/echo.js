// ---------- echoes: a reported line brings back the words that were first said ----------
const ECHO=__ECHO__;
function echoWrap(){const E=ECHO[STORIES[si].id+':'+cur];if(!E)return;
  const sp=STORIES[si].pages[cur].replace(RX,'$1'),els=[...$('text').querySelectorAll('[data-s]')];
  E.forEach(e=>{const a=sp.indexOf(e.ph);if(a<0)return;const b=a+e.ph.length;
    const mine=els.filter(x=>+x.dataset.s>=a&&+x.dataset.e<=b);if(!mine.length)return;
    const wrap=document.createElement('span');wrap.className='echo';wrap.dataset.eco=e.id;wrap.setAttribute('role','button');wrap.tabIndex=0;
    mine[0].before(wrap);let n=mine[0];const last=mine[mine.length-1];
    while(n){const nx=n.nextSibling;wrap.appendChild(n);if(n===last)break;n=nx}
    e.pairs.forEach((p,j)=>{const rep=p[1].map(w=>w.toLowerCase());mine.forEach(x=>{if(rep.includes(x.textContent.toLowerCase()))x.dataset.ep=j})})})}
const echoOf=id=>{for(const k in ECHO){const e=ECHO[k].find(x=>x.id===id);if(e)return e}return null};
const echoLine=e=>e.o.replace(WRX,w=>{const j=e.pairs.findIndex(p=>p[0].some(x=>x.toLowerCase()===w.toLowerCase()));return j>=0?`<b data-ep="${j}">${w}</b>`:w});
let echoLast=null;
function echoHide(){clearTimeout(echoShow.t);document.querySelectorAll('.eco-pop').forEach(x=>x.remove());document.querySelectorAll('.echo.on').forEach(x=>x.classList.remove('on'))}
function echoShow(el,opt){const e=echoOf(el.dataset.eco);if(!e)return;opt=opt||{};
  document.querySelectorAll('.eco-pop').forEach(x=>x.remove());document.querySelectorAll('.echo.on').forEach(x=>x.classList.remove('on'));
  const b=document.createElement('div');b.className='eco-pop';b.setAttribute('role','status');
  b.innerHTML=`<i aria-hidden="true">«</i><span lang="pt-PT">${echoLine(e)}</span><i aria-hidden="true">»</i>`;
  document.body.appendChild(b);
  const r=el.getBoundingClientRect(),w=b.offsetWidth,h=b.offsetHeight;
  b.style.left=Math.max(8,Math.min(r.left+Math.min(r.width,260)/2-w/2,document.documentElement.clientWidth-w-8))+'px';
  b.style.top=(r.top-h-10>8?r.top-h-10:r.bottom+10)+'px';
  el.classList.add('on');light(e.id);
  if(opt.audio!==false)wordClip(e.o);
  window.addEventListener('scroll',()=>{b.remove();el.classList.remove('on')},{once:true,passive:true});
  clearTimeout(echoShow.t);echoShow.t=setTimeout(()=>{b.remove();el.classList.remove('on')},opt.audio===false?3000:4600)}
