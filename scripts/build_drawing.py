import ezdxf, numpy as np, datetime
from ezdxf import path as ezp
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon as MPoly
from shapely.geometry import Polygon, Point, box
plt.rcParams['font.family']='DejaVu Sans'
MM=1/25.4; TH=3.5; LT,LN=0.5,0.25; AL,AW=3.0,1.0; PT=2.835
doc=ezdxf.readfile('../cad/end-cap_profile.dxf')
PRO=Polygon([(v.x,v.y) for e in doc.modelspace() for v in ezp.make_path(e).flattening(0.0005)])
H=19.67; YB=16.67; L=80.0; W=17.0
XO,XL,XI=1.6,2.6,4.6
TIP=1.8       # root outer, leg outer, leg inner (left leg)
PW,PH=420,297
fig=plt.figure(figsize=(PW*MM,PH*MM)); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,PW); ax.set_ylim(0,PH); ax.axis('off')
def ln(xs,ys,lw=LN,**k): ax.plot(xs,ys,color='k',lw=lw*PT,solid_capstyle='butt',**k)
def cl(xs,ys): ln(xs,ys,0.18,dashes=(12,2,2,2))
def tx(x,y,s,size=TH,rot=0,ha='center',va='center',**k): ax.text(x,y,s,fontsize=size/0.3528*0.92,rotation=rot,ha=ha,va=va,**k)
def arrow(x,y,ang):
    d=np.array([np.cos(ang),np.sin(ang)]); n=np.array([-d[1],d[0]]); t=np.array([x,y]); b=t-d*AL
    ax.add_patch(MPoly([t,b+n*AW/2,b-n*AW/2],closed=True,color='k',lw=0))
class View:
    def __init__(s,ox,oy,sc,px=0,py=0): s.ox,s.oy,s.sc,s.px,s.py=ox,oy,sc,px,py
    def P(s,x,y): return (s.ox+(x-s.px)*s.sc, s.oy+(y-s.py)*s.sc)
    def geom(s,g,lw=LT):
        if g.is_empty: return
        if g.geom_type in('LineString','LinearRing'):
            c=np.array([s.P(x,y) for x,y in g.coords]); ln(c[:,0],c[:,1],lw)
        elif g.geom_type=='Polygon': s.geom(g.exterior,lw); [s.geom(i,lw) for i in g.interiors]
        else: [s.geom(p,lw) for p in g.geoms]
    def ext_h(s,x,y,yd):          # extension line (vertical) from part point to dim level
        X,Y=s.P(x,y); _,Yd=s.P(0,yd)
        if abs(Y-Yd)>0.3: g=np.sign(Yd-Y); ln([X,X],[Y+g*1.0,Yd+g*2.0])
    def ext_v(s,x,y,xd):
        X,Y=s.P(x,y); Xd,_=s.P(xd,0)
        if abs(X-Xd)>0.3: g=np.sign(Xd-X); ln([X+g*1.0,Xd+g*2.0],[Y,Y])
    def hdim(s,x1,y1,x2,y2,yd,label,mode='in'):
        s.ext_h(x1,y1,yd); s.ext_h(x2,y2,yd)
        X1,_=s.P(x1,yd); X2,Yd=s.P(x2,yd); w=len(label)*TH*0.6
        if mode=='in':
            ln([X1,X2],[Yd,Yd]); arrow(X1,Yd,np.pi); arrow(X2,Yd,0); tx((X1+X2)/2,Yd+0.8,label,va='bottom')
        elif mode=='left':     # arrows outside, text left
            ln([X1-AL-w-3,X2+AL+3],[Yd,Yd]); arrow(X1,Yd,0); arrow(X2,Yd,np.pi); tx(X1-AL-2-w/2,Yd+0.8,label,va='bottom')
        elif mode=='in_right': # arrows inside, text right of the part
            ln([X1,X2+w+5],[Yd,Yd]); arrow(X1,Yd,np.pi); arrow(X2,Yd,0); tx(X2+3+w/2,Yd+0.8,label,va='bottom')
        elif mode=='right':    # arrows outside, text right
            ln([X1-AL-3,X2+AL+w+3],[Yd,Yd]); arrow(X1,Yd,0); arrow(X2,Yd,np.pi); tx(X2+AL+2+w/2,Yd+0.8,label,va='bottom')
    def vdim(s,x1,y1,x2,y2,xd,label,mode='in'):
        s.ext_v(x1,y1,xd); s.ext_v(x2,y2,xd)
        Xd,Y1=s.P(xd,y1); _,Y2=s.P(xd,y2); lo,hi=min(Y1,Y2),max(Y1,Y2); w=len(label)*TH*0.6
        if mode=='in':
            ln([Xd,Xd],[lo,hi]); arrow(Xd,lo,-np.pi/2); arrow(Xd,hi,np.pi/2); tx(Xd-0.8,(lo+hi)/2,label,rot=90,ha='right')
        else:                  # arrows outside, text above
            ln([Xd,Xd],[lo-AL-3,hi+AL+w+3]); arrow(Xd,lo,np.pi/2); arrow(Xd,hi,-np.pi/2); tx(Xd-0.8,hi+AL+2+w/2,label,rot=90,ha='right')
    def detail(s,c,r,label,lpos):
        C=s.P(*c); ax.add_patch(Circle(C,r*s.sc,fill=False,lw=LN*PT))
        tx(C[0]+lpos[0],C[1]+lpos[1],label,size=5)

# ---------------- frame + title block ----------------
FL,FR=20,10
ax.add_patch(Rectangle((FL,FR),PW-FL-FR,PH-2*FR,fill=False,lw=0.7*PT))
# ---------------- FRONT VIEW 2:1 ----------------
F=View(52,205,2.0)
F.geom(PRO)
cl([F.P(L/2,-3)[0]]*2,[F.P(0,-3)[1],F.P(0,H+3)[1]])
F.hdim(0,H,L,H,H+6,'80')
F.vdim(L,0,L,H,L+13,'19.67')
F.vdim(L,YB,L,H,L+6,'3',mode='out')
F.hdim(XO,YB,L-XO,YB,-6,'%g'%(L-2*XO))
F.hdim(XI,0,L-XI,0,-12,'%g'%(L-2*XI))
cA=(3.2,9.8); rA=11.0
F.detail(cA,rA,'A',(-19,-19))
# ---------------- SIDE VIEW 2:1 (first angle: left view to the right) ----------------
S=View(275,205,2.0)
S.geom(box(0,0,W,H))
ys=[YB,YB-6]+[YB-6-k for k in range(1,8)]
for y in ys:
    a,b=S.P(0,y),S.P(W,y); ln([a[0],b[0]],[a[1],b[1]],LT)
cl([S.P(W/2,0)[0]]*2,[S.P(0,-3)[1],S.P(0,H+3)[1]])
S.hdim(0,0,W,0,-6,'17')
# ---------------- DETAIL A 5:1 ----------------
D=View(112,100,5.0,cA[0],cA[1])
clipA=Point(cA).buffer(rA,quad_segs=256)
D.geom(PRO.boundary.intersection(clipA))
C=D.P(*cA); ax.add_patch(Circle(C,rA*D.sc,fill=False,lw=LN*PT))
tx(C[0],C[1]-rA*D.sc-8,'A (5:1)',size=5)
D.hdim(0,YB,XO,YB,YB-0.85,'1.6',mode='in')
D.hdim(XL,3.335,XI,3.335,3.335,'2',mode='in_right')
# R5 leader
# R2 (recess), 2x R2.5 (return), R7 (reinforcement)
def lead(c,r,deg,lab,dx=10,side=1):
    t=np.radians(deg); p=D.P(c[0]+r*np.cos(t),c[1]+r*np.sin(t)); o=D.P(c[0]+(r+1.8)*np.cos(t),c[1]+(r+1.8)*np.sin(t))
    ln([p[0],o[0],o[0]+side*dx],[p[1],o[1],o[1]]); arrow(p[0],p[1],t+np.pi); tx(o[0]+side*dx/2,o[1]+0.8,lab,va='bottom')
def leadin(c,r,deg,lab,dx=10,side=1,back=1.9):     # arrow from the centre side
    t=np.radians(deg); p=D.P(c[0]+r*np.cos(t),c[1]+r*np.sin(t)); o=D.P(c[0]+(r-back)*np.cos(t),c[1]+(r-back)*np.sin(t))
    ln([p[0],o[0],o[0]+side*dx],[p[1],o[1],o[1]]); arrow(p[0],p[1],t); tx(o[0]+side*dx/2,o[1]+0.8,lab,va='bottom')
leadin((XO,YB-2),2.0,10,'R2',8,-1,1.3)
leadin((XI+7,YB-7),7.0,135,'R7',10,1,2.2)
leadin((XL+1-2.5,YB-2),2.5,-50,'2× R2.5',18,-1,1.5)
D.vdim(XL,YB-5,XL,YB-5,XL,'',mode='in') if False else None

D.vdim(0,YB,XL,YB-6,-2.8,'6')
D.vdim(TIP,YB-6,XL,YB-13,-2.8,'7×1 (=7)')
D.vdim(XL,3.0,XL+1.7,0,-2.8,'3')
# radius R3.5: leader from arc mid-point outward (towards centre direction reversed)
cx,cy,R=XL+3.5,3.0,3.497; t=np.radians(222)
px,py=cx+R*np.cos(t),cy+R*np.sin(t); qx,qy=cx+(R+2.2)*np.cos(t),cy+(R+2.2)*np.sin(t)
P1=D.P(px,py); P2=D.P(qx,qy); ln([P1[0],P2[0],P2[0]-12],[P1[1],P2[1],P2[1]]); arrow(P1[0],P1[1],t+np.pi)
tx(P2[0]-6,P2[1]+0.8,'R3.5',va='bottom')
cB=((TIP+XL)/2,8.2); rB=1.5
D.detail(cB,rB,'B',(-11,6))
# ---------------- DETAIL B 10:1 ----------------
B=View(232,112,10.0,cB[0],cB[1])
clipB=Point(cB).buffer(rB,quad_segs=256)
B.geom(PRO.boundary.intersection(clipB))
C=B.P(*cB); ax.add_patch(Circle(C,rB*B.sc,fill=False,lw=LN*PT))
tx(C[0],C[1]-rB*B.sc-8,'B (10:1)',size=5)
yt=YB-6-3   # flat face of 4th tooth = 7.67
B.hdim(TIP,yt,XL,yt-1.0,cB[1]+rB+0.35,'0.8',mode='right')
B.vdim(TIP,yt+1,TIP,yt,cB[0]-rB-0.3,'1')
# ---------------- TITLE BLOCK ----------------
TW,TB=180,44; X0,Y0=PW-FR-TW,FR
ax.add_patch(Rectangle((X0,Y0),TW,TB,fill=False,lw=0.7*PT))
r1,r2,r3=Y0+TB-16,Y0+TB-26,Y0+TB-35
for yy in (r1,r2,r3): ln([X0,X0+TW],[yy,yy],0.35)
c1=X0+60; ln([c1,c1],[Y0,Y0+TB],0.35)
cs=[c1+30,c1+60,c1+90]
for c in cs: ln([c,c],[Y0,r1],0.35)
def cell(x,y,lab,val,vs=3.2):
    tx(x+1.2,y-1.2,lab,size=1.9,ha='left',va='top',color='#444'); tx(x+1.2,y-4.4,val,size=vs,ha='left',va='top')
tx(X0+30,Y0+TB-7,'ULAMEX',size=6,weight='bold'); tx(X0+30,Y0+TB-12.5,'Zawada 144',size=2.2,color='#444')
cell(c1,Y0+TB,'TITLE','END CAP',5); 
cell(X0,r1,'MATERIAL','—'); cell(c1,r1,'SCALE','2:1'); cell(cs[0],r1,'DETAILS','5:1 / 10:1'); cell(cs[1],r1,'UNITS','mm'); cell(cs[2],r1,'SHEET','A3  1/1')
cell(X0,r2,'GENERAL TOLERANCES','ISO 2768-m',2.8); cell(c1,r2,'DATE',datetime.date.today().isoformat(),2.8); cell(cs[0],r2,'QTY','—',2.8)
cell(cs[1],r2,'DRAWN',' ',2.8); cell(cs[2],r2,'CHECKED',' ',2.8)
cell(X0,r3,'DRAWING NO.','END-CAP-01',2.8); cell(c1,r3,'FILES','end-cap.step, end-cap_profile.dxf',2.4)
# first-angle projection symbol (ISO 5456-2): truncated cone (small end left), end view on the right
x=cs[1]; tx(x+1.2,r3-1.2,'PROJECTION',size=1.9,ha='left',va='top',color='#444')
yc=Y0+3.2
ax.add_patch(MPoly([(x+8,yc-1.1),(x+15,yc-2.2),(x+15,yc+2.2),(x+8,yc+1.1)],closed=True,fill=False,lw=0.35*PT))
ax.add_patch(Circle((x+22,yc),2.2,fill=False,lw=0.35*PT)); ax.add_patch(Circle((x+22,yc),1.1,fill=False,lw=0.35*PT))
cl([x+6.5,x+25.5],[yc,yc]); cl([x+22,x+22],[yc-3.0,yc+3.0])
fig.savefig('../drawings/end-cap_drawing.pdf')
