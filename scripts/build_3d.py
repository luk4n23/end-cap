import ezdxf, math, cadquery as cq
from ezdxf import path as ezp
from shapely.geometry import Polygon
W=17.0
doc=ezdxf.readfile('../cad/end-cap_profile.dxf'); e=next(iter(doc.modelspace()))
V=[(x,y,b) for x,y,s,_,b in e.get_points('xyseb')]
wp=cq.Workplane('XZ').moveTo(V[0][0],V[0][1])     # profile in the XZ plane, extruded along Y
n=len(V)
for i in range(n):
    x0,y0,b=V[i]; x1,y1,_=V[(i+1)%n]
    if abs(b)<1e-9: wp=wp.lineTo(x1,y1)
    else:
        mx,my=(x0+x1)/2,(y0+y1)/2
        wp=wp.threePointArc((mx+b*(y1-y0)/2, my-b*(x1-x0)/2),(x1,y1))
solid=wp.close().extrude(-W)
vol=solid.val().Volume()
P=Polygon([(v.x,v.y) for v in ezp.make_path(e).flattening(0.0005)])
print('volume %.2f mm3 vs area*17 %.2f, valid %s'%(vol,P.area*W,solid.val().isValid()))
bb=solid.val().BoundingBox(); print('bbox',round(bb.xlen,3),round(bb.ylen,3),round(bb.zlen,3))
cq.exporters.export(solid,'../cad/end-cap.step')
cq.exporters.export(solid,'../cad/end-cap.stl',tolerance=0.005,angularTolerance=0.05)
