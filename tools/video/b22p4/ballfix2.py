# Ball path = circle finds (ballc.py -> ballhough.npy) where they sit on the ball, hand corrections where they missed.
# Each correction is (dx,dy,radius) measured on the ball contact sheet; frames between keyframes are interpolated.
import numpy as np
P=np.load('ballhough.npy'); N=len(P)
corr={28:(5,1,38),36:(-31,-10,34),40:(-7,5,35),44:(-2,35,34),48:(-6,8,36),60:(-16,8,33),68:(0,8,32),72:(7,-3,31),92:(3,-3,33)}
good=[0,4,8,12,16,20,24,32,52,56,64,76,80,84,88]
K={t:tuple(P[t]) for t in good}
for t,(dx,dy,r) in corr.items(): K[t]=(P[t][0]+dx,P[t][1]+dy,r)
K[N-1]=K[92]
ks=sorted(K); kv=np.array([K[k] for k in ks])
I=np.stack([np.interp(range(N),ks,kv[:,i]) for i in range(3)],1); out=I.copy()
for t in range(N):
    if t not in K and np.hypot(*(P[t][:2]-I[t][:2]))<6 and abs(P[t][2]-I[t][2])<4: out[t]=P[t]
sm=out.copy()
for t in range(1,N-1): sm[t]=0.25*out[t-1]+0.5*out[t]+0.25*out[t+1]
for t in K: sm[t]=K[t]
def nudge(t0,dx,dy,w=3):
    for t in range(max(0,t0-w),min(N,t0+w+1)):
        k=1-abs(t-t0)/(w+1); sm[t,0]+=dx*k; sm[t,1]+=dy*k
nudge(38,17,0,2); nudge(95,0,-8,3); nudge(92,0,-3,2)
np.save('ballpath.npy',sm)
