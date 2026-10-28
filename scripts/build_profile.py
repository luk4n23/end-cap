import ezdxf, math, numpy as np
from ezdxf import path as ezp
from shapely.geometry import Polygon, box, LineString
from shapely import affinity
H=19.67; TP=3.0; YB=H-TP; L=80.0; T=2.0
XO=1.6; XL=2.6; XI=XL+T          # leg root (76.8), leg outer / inner face
RC=2.0                           # recess arc into the root: R2 (2 mm in from the root)
SH=3.0                           # S-curve back to the leg face (2x R2.5)
RF=7.0                           # inner reinforcing fillet
TD,TPITCH,NT,CH=0.8,1.0,7,6.0
q=math.tan(math.radians(90)/4)
half=[]
def add(x,y,b=0.0): half.append([x,y,b])
add(0,H); add(0,YB)
add(XO,YB,-q)                                   # R2 quarter arc into the material
xd,yd=XO+RC,YB-RC
dx=xd-XL; ch=math.degrees(math.atan2(SH/2,dx/2)); bs=math.tan(math.radians(2*(90-ch))/4)
add(xd,yd,-bs); add((xd+XL)/2,yd-SH/2,bs); add(XL,yd-SH)
y=YB-CH; add(XL,y)
for k in range(NT): add(XL-TD,y); y-=TPITCH; add(XL,y)
AH=3.0; DX=T-0.3; R=(DX**2+AH**2)/(2*DX); cx,cy=XL+R,AH
sw=(math.degrees(math.atan2(0-cy,XL+DX-cx))%360)-180
add(XL,AH,math.tan(math.radians(sw)/4)); add(XL+DX,0); add(XI,0)
add(XI,YB-RF,-q); add(XI+RF,YB)                 # inner fillet RF
n=len(half)-1
pts=half+[[L-half[n-j][0],half[n-j][1],(half[n-j-1][2] if j<n else 0.0)] for j in range(n+1)]
doc=ezdxf.new('R2010',setup=True); doc.header['$INSUNITS']=4; doc.layers.add('CIECIE',color=7)
e=doc.modelspace().add_lwpolyline([(x,y,0,0,b) for x,y,b in pts],format='xyseb',close=True,dxfattribs={'layer':'CIECIE'})
doc.saveas('../cad/end-cap_profile.dxf')
P=Polygon([(v.x,v.y) for v in ezp.make_path(e).flattening(0.001)])
print('valid',P.is_valid,'sym %.5f'%P.symmetric_difference(affinity.scale(P,-1,1,origin=(40,0))).area,'S arcs R%.3f'%((math.hypot(dx/2,SH/2))/(2*math.sin(math.radians(90-ch)))))
pocket=box(XO,YB-CH,XI,YB)
print('free in pocket zone %.2f mm2 (%.0f mm3/17mm)'%(pocket.difference(P).area,pocket.difference(P).area*17))
# minimum wall thickness at the leg root
leg=P.intersection(box(0,YB-CH,12,YB+0.0))
leg=max(getattr(leg,'geoms',[leg]),key=lambda g:g.area)
for yy in np.arange(YB-0.2,YB-CH,-0.25):
    pass
from shapely.ops import nearest_points
B=P.exterior
out=[(x,y) for x,y in np.asarray(B.coords) if XO-1e-6<=x<=xd+1e-6 and YB-CH<=y<=YB+1e-6 and x>=XO]
inn=LineString([(x,y) for x,y in np.asarray(B.coords) if XI-1e-6<=x<=XI+RF+1e-6 and YB-CH<=y<=YB+1e-6 and y<YB-1e-6])
from shapely.geometry import Point
d=[Point(p).distance(inn) for p in out if p[1]<YB-0.05]
print('min wall thickness near root %.2f mm'%min(d))
