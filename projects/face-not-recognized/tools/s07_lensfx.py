# S07 post fix (2026-09-27): tracks both pupils, adds a faint flickering lens ring, removes the misplaced mole.
# Usage: python projects/face-not-recognized/tools/s07_lensfx.py media/FNR/incoming/FNR_S07_v2.mp4 media/FNR/incoming/FNR_S07_v3.mp4 2.0 4.0
import sys, subprocess, numpy as np
from scipy import ndimage as nd
import imageio_ffmpeg
FF=imageio_ffmpeg.get_ffmpeg_exe()
src, out, t0, dur = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
W,H=720,1280
raw=subprocess.run([FF,'-loglevel','error','-ss',str(t0),'-i',src,'-t',str(dur),'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
fr=np.frombuffer(raw,np.uint8).reshape(-1,H,W,3).copy()
n=len(fr); fps=24
eyes=[np.array([272.,460.]),np.array([490.,455.])]; mole=np.array([427.,562.])
R=21.0
yy,xx=np.mgrid[0:H,0:W]
rng=np.random.default_rng(7)
def env(t):
    # off, stutter on, then weak unstable
    if t<0.25: return 0
    pat=[(0.25,0.33,0.9),(0.33,0.45,0),(0.45,0.52,0.8),(0.52,0.70,0),(0.70,0.78,0.7)]
    for a,b,v in pat:
        if a<=t<b: return v
    return 0.42+0.12*np.sin(t*23)+rng.uniform(-0.1,0.1)
track=[]
for i in range(n):
    f=fr[i].astype(float); g=nd.gaussian_filter(f.mean(2),3)
    for k in range(2):
        x,y=eyes[k].astype(int); s=14
        sub=g[y-s:y+s,x-s:x+s]; dy,dx=np.unravel_index(sub.argmin(),sub.shape)
        new=np.array([x-s+dx,y-s+dy],float); eyes[k]=0.6*eyes[k]+0.4*new
    x,y=mole.astype(int); s=10
    sub=g[y-s:y+s,x-s:x+s]; dy,dx=np.unravel_index(sub.argmin(),sub.shape)
    mole=0.5*mole+0.5*np.array([x-s+dx,y-s+dy],float)
    track.append((eyes[0].copy(),eyes[1].copy(),mole.copy(),sub.min()))
    # mole removal: replace a disc with blurred surroundings
    mx,my=mole; md=np.hypot(xx-mx,yy-my)
    if sub.min()<90:
        patch=nd.median_filter(f[int(my)-20:int(my)+20,int(mx)-20:int(mx)+20],size=(15,15,1))
        a=np.clip((9-md[int(my)-20:int(my)+20,int(mx)-20:int(mx)+20])/3,0,1)[...,None]
        f[int(my)-20:int(my)+20,int(mx)-20:int(mx)+20]=f[int(my)-20:int(my)+20,int(mx)-20:int(mx)+20]*(1-a)+patch*a
    e=env(i/fps)
    if e>0:
        ring=np.zeros((H,W))
        for c in eyes:
            d=np.hypot(xx-c[0],yy-c[1])
            ring=np.maximum(ring,np.exp(-((d-R)/1.1)**2))
        glow=nd.gaussian_filter(ring,3)*0.6
        rb=f[...,0]-f[...,2]
        notskin=np.clip((75-rb)/35,0,1)
        a=np.clip((ring+glow)*e,0,1)*notskin
        col=np.array([90,200,255.])
        f=f+a[...,None]*col*0.9
    fr[i]=np.clip(f,0,255).astype(np.uint8)
p=subprocess.Popen([FF,'-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r','24','-i','-','-ss',str(t0),'-t',str(dur),'-i',src,'-map','0:v','-map','1:a','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-shortest',out],stdin=subprocess.PIPE)
p.stdin.write(fr.tobytes()); p.stdin.close(); p.wait()
for i in range(0,n,12): print(i/fps, np.round(track[i][0]),np.round(track[i][1]),np.round(track[i][2]),round(track[i][3]))
