// ---------- Water particles: small light marks that move like water (scene life) ----------
(function(){
  let RM=false;try{RM=matchMedia('(prefers-reduced-motion: reduce)').matches}catch(e){}
  if(RM)return;
  const NS='http://www.w3.org/2000/svg';
  const R=(a,b)=>a+Math.random()*(b-a), L=(a,b,t)=>a+(b-a)*t;
  const S=t=>{t=t<0?0:t>1?1:t;return t*t*(3-2*t)};               // smoothstep: every fade is smooth, nothing blinks
  const yAt=(ln,x)=>{for(let i=0;i<ln.length-1;i++){const[a,b]=ln[i],[c,d]=ln[i+1];if((x>=a&&x<=c)||(x>=c&&x<=a)){const t=c===a?0:(x-a)/(c-a);return[b+t*(d-b),(d-b)/((c-a)||1)]}}
    const e=x<ln[0][0]?[ln[0],ln[1]]:[ln[ln.length-2],ln[ln.length-1]];return[x<ln[0][0]?e[0][1]:e[1][1],(e[1][1]-e[0][1])/((e[1][0]-e[0][0])||1)]};
  const inPoly=(p,x,y)=>{let c=false;for(let i=0,j=p.length-1;i<p.length;j=i++){const[xi,yi]=p[i],[xj,yj]=p[j];if(((yi>y)!==(yj>y))&&(x<(xj-xi)*(y-yi)/(yj-yi)+xi))c=!c}return c};
  const sys=new Map();let last=0,tm=0;

  function make(g){
    let c;try{c=JSON.parse(g.getAttribute('data-pfx'))}catch(e){return null}
    const ps=[],gd=document.createElementNS(NS,'g'),gl=document.createElementNS(NS,'g');
    gd.setAttribute('stroke',c.dark||'#3E6470');gd.setAttribute('style','mix-blend-mode:multiply');
    gl.setAttribute('stroke',c.col||'#FFFDF2');gl.setAttribute('style','mix-blend-mode:screen');
    g.appendChild(gd);g.appendChild(gl);
    const mk=par=>{const e=document.createElementNS(NS,'path');e.setAttribute('fill','none');e.setAttribute('stroke-linecap','round');par.appendChild(e);return e};
    for(let i=0;i<c.n;i++)ps.push({c,d:c.dop?mk(gd):null,e:mk(gl)});
    const s={g,c,ps};
    if(c.t==='stream'||c.t==='fall'){
      const[ax,ay]=c.a,[bx,by]=c.b,dx=bx-ax,dy=by-ay,l=Math.hypot(dx,dy);
      s.ux=dx/l;s.uy=dy/l;s.nx=-s.uy;s.ny=s.ux;
      ps.forEach(p=>{p.s=Math.random();p.lat=R(-.42,.42);p.sp=R(.8,1.25);p.ph=R(0,6.28);p.k=R(.7,1.15)});
    }else if(c.t==='shore'){
      s.xa=Math.max(c.sea[0][0],c.shore[0][0]);s.xb=Math.min(c.sea[c.sea.length-1][0],c.shore[c.shore.length-1][0]);
      ps.forEach(p=>{p.t=Math.random();p.j=R(0,1);p.k=R(.75,1.2);p.prev=0});
    }else if(c.t==='sea'||c.t==='spray'){
      let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;(c.poly||[]).forEach(([x,y])=>{x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x);y1=Math.max(y1,y)});
      s.bb=[x0,y0,x1,y1];ps.forEach(p=>{spawn(s,p);p.age=R(0,p.life)});
    }
    return s;
  }
  function spawn(s,p){const c=s.c;
    if(c.t==='spray'){p.x=c.o[0]+R(-.5,.5)*c.sw;p.y=c.o[1];p.vx=R(-1,1)*c.v*.6;p.vy=-R(.4,1)*c.v;p.age=0;p.life=R(c.life[0],c.life[1]);p.k=R(.7,1.2);return}
    const[x0,y0,x1,y1]=s.bb;for(let i=0;i<30;i++){p.x=R(x0,x1);p.y=R(y0,y1);if(inPoly(c.poly,p.x,p.y))break}
    p.age=0;p.life=R(c.life[0],c.life[1]);p.k=R(.6,1.2);p.sp=R(.6,1.3);p.ph=R(0,6.28)}
  function arc(el,x,y,ang,len,w,a,bend){
    const cx=Math.cos(ang)*len/2,cy=Math.sin(ang)*len/2,bx=-Math.sin(ang)*bend,by=Math.cos(ang)*bend;
    el.setAttribute('d',`M${(x-cx).toFixed(2)},${(y-cy).toFixed(2)}Q${(x-bx).toFixed(2)},${(y-by).toFixed(2)} ${(x+cx).toFixed(2)},${(y+cy).toFixed(2)}`);
    el.setAttribute('stroke-width',w.toFixed(2));el.setAttribute('stroke-opacity',Math.max(0,a).toFixed(3))}
  // each particle: a soft dark crest in the water's own (darkened) colour + a faint light glint just above it
  const TRANS=.45;                                   // every particle is translucent: the picture always shows through
  function seg(p,x,y,ang,len,w,a){a*=TRANS;const c=p.c,b=(c.bend==null?.18:c.bend)*len;
    if(p.d)arc(p.d,x,y,ang,len,w,a*c.dop/c.op,b);
    const gx=-Math.sin(ang)*w*.9,gy=Math.cos(ang)*w*.9;
    arc(p.e,x-gx,y-gy,ang,len*.6,w*.8,a,b*.6)}
  function step(s,dt){const c=s.c;
    if(c.t==='stream'||c.t==='fall'){
      const fa=Math.atan2(s.uy,s.ux),ma=c.along?fa:fa+Math.PI/2;
      s.ps.forEach(p=>{
        p.s+=dt*c.v*p.sp*(c.t==='fall'?(.35+1.65*p.s):1);
        if(p.s>=1){p.s-=1;p.lat=R(-.42,.42);p.sp=R(.8,1.25);p.k=R(.7,1.15)}
        const w=L(c.wa,c.wb,p.s),k=w/c.wb,lat=p.lat*w+Math.sin(tm*1.1+p.ph)*.05*w;
        const x=L(c.a[0],c.b[0],p.s)+s.nx*lat,y=L(c.a[1],c.b[1],p.s)+s.ny*lat;
        const a=c.op*S(p.s/.18)*S((1-p.s)/.22)*(.7+.3*Math.sin(tm*.9+p.ph));
        seg(p,x,y,ma,c.len*p.k*(c.along?1:Math.max(k,.35)),c.w*Math.max(k,.4),a)});
    }else if(c.t==='shore'){
      s.ps.forEach(p=>{
        let ph=((tm/c.T)+p.t*c.roll+p.j*.25)%1;
        if(ph<p.prev){p.t=Math.random();p.j=R(0,1);p.k=R(.75,1.2);p.u0=null;ph=((tm/c.T)+p.t*c.roll+p.j*.25)%1}
        p.prev=ph;
        const x=L(s.xa,s.xb,p.t),[ys]=yAt(c.sea,x),[yh,sl]=yAt(c.shore,x);
        const A=c.amp==null?.9:c.amp, u0=(p.u0==null?(p.u0=R(.1,.9-A*.9)):p.u0);
        const inn=ph<.58,u=u0+A*(inn?(1-Math.pow(1-ph/.58,2.2)):1-.33*S((ph-.58)/.42));   // wash in, ease out, slide back (amp = share of the wash zone)
        const y=L(ys,yh,u),a=c.op*S(ph/.14)*(inn?1:1-S((ph-.58)/.42));
        const k=.55+.9*(y/260);
        seg(p,x,y,Math.atan(sl),c.len*p.k*k,c.w*k,a)});
    }else if(c.t==='sea'){
      const[x0,y0,x1,y1]=s.bb;
      s.ps.forEach(p=>{
        p.age+=dt;if(p.age>=p.life){spawn(s,p)}
        p.x+=c.d[0]*dt*p.sp;p.y+=c.d[1]*dt*p.sp+Math.sin(tm*.7+p.ph)*.02*dt;
        const u=p.age/p.life,a=c.op*Math.pow(Math.sin(Math.PI*u),2);
        const k=.6+.7*((p.y-y0)/((y1-y0)||1));
        seg(p,p.x,p.y,c.ang||0,c.len*p.k*k,c.w*k,a)});
    }else if(c.t==='spray'){
      s.ps.forEach(p=>{
        p.age+=dt;if(p.age>=p.life)spawn(s,p);
        p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy*=Math.pow(.6,dt);
        const u=p.age/p.life;seg(p,p.x,p.y,0,c.len*p.k,c.w*p.k,c.op*Math.pow(Math.sin(Math.PI*u),2))});
    }
  }
  function frame(now){
    const dt=Math.min(.05,last?(now-last)/1000:0);last=now;tm+=dt;
    if(!document.hidden){
      document.querySelectorAll('#pic .pfx').forEach(g=>{let s=sys.get(g);if(!s){s=make(g);if(!s)return;sys.set(g,s)}step(s,dt)});
      for(const g of sys.keys())if(!g.isConnected)sys.delete(g);
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
