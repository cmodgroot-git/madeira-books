exec(open('/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/waterfix.py').read().split("job=sys.argv[1]")[0])
def save_ppl(key,boxes):
    _,img=page(key); p=people(img,boxes); B=master(img).astype(np.float32)
    o=B*.35; o[p>.3]=B[p>.3]*.6+np.array([255,0,0])*.4; Image.fromarray(o.astype(np.uint8)).resize((800,449)).save(S+'city2/ppl_'+key.replace(':','_')+'.jpg'); return p
job=sys.argv[1]
BOX={'sabado:3':[[390,150,750,898],[840,140,1140,898],[1140,450,1440,898]],
     'sabado:4':[[680,90,1070,700],[1040,90,1370,700],[1100,420,1400,700]],
     'sabado:5':[[460,0,880,898],[820,0,1150,898],[730,600,1060,898]],
     'sabado:6':[[60,150,600,800],[450,150,900,800],[1110,520,1500,880]],
     'jantar:7':[[200,230,640,898],[700,0,1010,898],[1000,220,1400,898]],
     'jantar:6':[[180,0,880,898],[860,0,1560,898]],
     'manha:3':[[680,0,1300,898]]}
if job=='check':
    from PIL import Image as I
    ims=[I.open(S+'city2/ppl_'+k.replace(':','_')+'.jpg') if save_ppl(k,b) is not None else None for k,b in BOX.items()]
    sh=I.new('RGB',(1600,449*4))
    for j,t in enumerate(ims): sh.paste(t,((j%2)*800,(j//2)*449))
    sh.save(S+'city2/pplcheck.jpg',quality=80)
if job=='apply':
    for k,b in BOX.items(): hold(k,b,skip=('lg','ls') if k=='manha:3' else ('lg',))
    f=sorted(glob.glob(S+'gen/hlcache/manha_1_*.pkl'),key=os.path.getmtime)[-1]; R={k:v for k,v in pickle.load(open(f,'rb'))[1]}
    nav=cv2.dilate(R['navio'].astype(np.uint8),np.ones((15,15),np.uint8))
    sea_rebuild('manha:1','b1p2_ls',(R['mar']>0).astype(np.uint8),nav)
    sea_rebuild('manha:3','b1p4_ls',rect(330,230,760,420),near=1.6)
    for k in ['domingo:1','domingo:2','domingo:3','domingo:4','domingo:6']: feather(k,('_lb',))
