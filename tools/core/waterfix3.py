exec(open('/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/waterfix.py').read().split("job=sys.argv[1]")[0])
BOX={'sabado:3':[[390,150,750,898],[840,140,1140,898],[1140,450,1440,898]],
     'sabado:4':[[680,90,1070,700],[1040,90,1370,700],[1100,420,1400,700]],
     'sabado:5':[[460,0,880,898],[820,0,1150,898],[730,600,1060,898]],
     'sabado:6':[[60,150,600,800],[450,150,900,800],[1110,520,1500,880]]}
for key,boxes in BOX.items():
    _,img=page(key); B=master(img).astype(np.float32); p=people(img,boxes)
    p=np.clip(cv2.GaussianBlur(cv2.dilate((p>.2).astype(np.uint8),np.ones((31,31),np.uint8)).astype(np.float32),(0,0),4)*1.3,0,1)
    r,g,b=B[...,0],B[...,1],B[...,2]; L=F.lum(B)
    water=(((b>r+4)&(b>=g-6))|((L>175)&(F.sat(B)<45))).astype(np.uint8)
    water=cv2.morphologyEx(water,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8)); water=np.clip(cv2.GaussianBlur(water.astype(np.float32),(0,0),2),0,1)
    keepall=(1-p)*water
    for (bx,by,bw,bh),fw,fh,stem,sw,sh in sheets(key):
        if not stem.endswith('_lw'): continue
        k=cv2.resize(keepall[by:by+bh,bx:bx+bw],(fw,fh)); edit(stem,fw,fh,sw,sh,lambda a,k=k: a*k); print(key,stem,'limited to water, people cleared')
