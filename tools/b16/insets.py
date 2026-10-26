"""Book 16 insets: the phone message (p1 crisp, p2 faded) and faded 'earlier' insets with speech bubbles (p5, p8).
All drawn on 1600x898 masters. Writes gen/m_pN.jpg and insets.json (inset boxes in 1600x898 px)."""
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
CAV='Caveat.ttf'; SANS='Alegreya+Sans.ttf'
INK=(58,40,28); CREAM=(250,244,230)
MSG='Querias uma coisa com os pés no chão? Sábado vamos jogar golfe no Santo da Serra. A minha amiga Inês vai ensinar-nos.'
def load(k): return Image.open(f'gen/{k}.png').convert('RGB').resize((1600,898),Image.LANCZOS)
def wrap(d,text,font,w):
    out,line=[],''
    for word in text.split():
        t=(line+' '+word).strip()
        if d.textlength(t,font=font)<=w: line=t
        else: out.append(line); line=word
    out.append(line); return out
def rmask(size,r):
    m=Image.new('L',size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,size[0]-1,size[1]-1),r,fill=255); return m
def phone(w,h,avatar,fs=None):
    """Smartphone with one chat message from Tiago."""
    im=Image.new('RGBA',(w,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,w-1,h-1),int(w*.12),fill=(40,40,46,255),outline=INK+(255,),width=3)
    m=int(w*.05); sx0,sy0,sx1,sy1=m,int(h*.06),w-m,h-int(h*.06)
    d.rounded_rectangle((sx0,sy0,sx1,sy1),int(w*.07),fill=(246,243,236,255))
    # header
    hh=int(h*.13); d.rectangle((sx0,sy0+int(w*.05),sx1,sy0+hh),fill=(226,236,233,255))
    d.rounded_rectangle((sx0,sy0,sx1,sy0+hh),int(w*.07),fill=(226,236,233,255))
    ad=int(hh*.7); av=ImageOps.fit(avatar,(ad,ad)); am=Image.new('L',(ad,ad),0); ImageDraw.Draw(am).ellipse((0,0,ad-1,ad-1),fill=255)
    ax,ay=sx0+int(w*.05),sy0+(hh-ad)//2+2; im.paste(av,(ax,ay),am); d.ellipse((ax,ay,ax+ad,ay+ad),outline=INK+(255,),width=2)
    f=ImageFont.truetype(SANS,int(hh*.42)); d.text((ax+ad+int(w*.04),sy0+hh//2+2),'Tiago',font=f,fill=INK+(255,),anchor='lm')
    # bubble
    fs=fs or int(w*.072); f=ImageFont.truetype(SANS,fs); bw=int((sx1-sx0)*.86)
    lines=wrap(d,MSG,f,bw-2*int(w*.04)); lh=int(fs*1.18)
    bx0,by0=sx0+int(w*.04),sy0+hh+int(h*.05); bh=lh*len(lines)+2*int(w*.035)
    d.rounded_rectangle((bx0,by0,bx0+bw,by0+bh),int(w*.05),fill=(255,255,255,255),outline=(150,140,125,255),width=2)
    d.polygon([(bx0+6,by0+bh-18),(bx0-10,by0+bh+4),(bx0+26,by0+bh-4)],fill=(255,255,255,255))
    for i,l in enumerate(lines): d.text((bx0+int(w*.04),by0+int(w*.035)+i*lh),l,font=f,fill=(30,30,30,255))
    d.text((bx0+bw-int(w*.03),by0+bh+int(h*.025)),'9:12',font=ImageFont.truetype(SANS,int(fs*.75)),fill=(120,115,105,255),anchor='ra')
    return im
def fade(im):
    """The 'earlier' look: warm, pale, a little desaturated."""
    im=ImageEnhance.Color(im).enhance(.55)
    return Image.blend(im,Image.new('RGB',im.size,(244,226,196)),.30)
def frame(base,content,box,r=22,faded=True):
    x0,y0,x1,y1=box; w,h=x1-x0,y1-y0
    c=content.resize((w,h),Image.LANCZOS).convert('RGB')
    if faded: c=fade(c)
    sh=Image.new('L',base.size,0); ImageDraw.Draw(sh).rounded_rectangle((x0+6,y0+8,x1+6,y1+8),r,fill=110)
    sh=sh.filter(ImageFilter.GaussianBlur(10)); base.paste((60,45,30),(0,0),sh)
    b=10; d=ImageDraw.Draw(base); d.rounded_rectangle((x0-b,y0-b,x1+b,y1+b),r+b,fill=CREAM)
    base.paste(c,(x0,y0),rmask((w,h),r)); d.rounded_rectangle((x0-b,y0-b,x1+b,y1+b),r+b,outline=INK,width=3)
    d.rounded_rectangle((x0,y0,x1,y1),r,outline=(150,120,90),width=1)
def bubble(base,text,anchor,tail,fs=40,maxw=420,side="bottom"):
    """Speech bubble; anchor = (cx, top y); tail = point it aims at."""
    d=ImageDraw.Draw(base); f=ImageFont.truetype(CAV,fs); lines=wrap(d,text,f,maxw); lh=int(fs*1.05)
    tw=max(d.textlength(l,font=f) for l in lines); pw,ph=22,14
    cx,ty=anchor; x0,y0=int(cx-tw/2-pw),ty; x1,y1=int(cx+tw/2+pw),ty+lh*len(lines)+2*ph
    bxm=(x0+x1)//2; bym=(y0+y1)//2
    if side=='bottom': d.polygon([(bxm-18,y1-4),(bxm+18,y1-4),tail],fill=(255,255,255),outline=INK)
    else: d.polygon([(x1-4,bym-16),(x1-4,bym+16),tail],fill=(255,255,255),outline=INK)
    d.rounded_rectangle((x0,y0,x1,y1),26,fill=(255,255,255),outline=INK,width=3)
    if side=='bottom': d.rectangle((bxm-15,y1-6,bxm+15,y1-1),fill=(255,255,255))
    else: d.rectangle((x1-6,bym-13,x1-1,bym+13),fill=(255,255,255))
    for i,l in enumerate(lines): d.text((cx,y0+ph+i*lh+lh//2),l,font=f,fill=INK,anchor='mm')
    return (x0,y0,x1,y1)
OUT={}
tiago=Image.open('gen/i8.png').convert('RGB'); s=2736/1200; tface=tiago.crop((int(615*s),int(70*s),int(735*s),int(190*s)))
# p1: crisp phone, bottom right over the roofs
p=load('p1'); ph=phone(330,560,tface); p.paste(ph,(1235,318),ph); OUT['p1']={'phone':[1235,318,1565,878]}; p.save('gen/m_p1.jpg',quality=93)
# p2: the same message, faded, upper-left wall (the 'echo' inset)
p=load('n2'); scr=Image.new('RGB',(560,300),(238,230,214)); ph=phone(560,300,tface,fs=27); scr.paste(ph,(0,0),ph)
box=(40,30,40+520,30+279); frame(p,scr,box,r=26); OUT['p2']={'echo':list(box)}; p.save('gen/m_p2.jpg',quality=93)
# p5: workshop memory, top centre
p=load('r5c')
src=Image.open('gen/i5.png').convert('RGB'); W5,H5=src.size; sc=W5/1200
mem=src.crop((int(300*sc),int(0*sc),int(1200*sc),int(600*sc)))
box=(450,22,450+480,22+320); frame(p,mem,box)
bb=bubble(p,'Já joguei golfe muitas vezes!',(box[0]+105,box[1]+14),(box[0]+215,box[1]+92),fs=36,maxw=170)
OUT['p5']={'echo':list(box)}; p.save('gen/m_p5.jpg',quality=93)
# p8: Tiago whispering to Ines, top right
p=load('r8'); src=Image.open('gen/i8.png').convert('RGB'); sc=src.size[0]/1200
mem=src.crop((int(300*sc),int(20*sc),int(900*sc),int(420*sc)))
box=(1262,20,1262+318,20+212); frame(p,mem,box)
bubble(p,'Nunca trouxe ninguém aqui.',(1090,28),(1262+200,20+86),fs=36,maxw=230,side='right')
OUT['p8']={'echo':list(box)}; p.save('gen/m_p8.jpg',quality=93)
json.dump(OUT,open('insets.json','w'))
