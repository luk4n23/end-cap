import cadquery as cq, json, numpy as np
sh=cq.importers.importStep('../cad/end-cap.step').val()
V,T=sh.tessellate(0.01,0.1)
V=np.round(np.array([[v.x,v.y,v.z] for v in V]),4); T=np.array(T,int)
# center: X (80) , Y (17 extrusion), Z (height)
V[:,0]-=40; V[:,1]+=8.5
data={'v':V.flatten().tolist(),'t':T.flatten().tolist()}
html=r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>End Cap 3D</title>
<style>
:root{--bg:#f2f2ef;--panel:#ffffffe8;--ink:#1d1d1d;--muted:#666;--line:#ddd}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#1b1c1e;--panel:#26282be8;--ink:#eee;--muted:#aaa;--line:#3a3c40}}
:root[data-theme="dark"]{--bg:#1b1c1e;--panel:#26282be8;--ink:#eee;--muted:#aaa;--line:#3a3c40}
html,body{margin:0;height:100%;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,sans-serif;overflow:hidden}
#c{position:fixed;inset:0;width:100%;height:100%;touch-action:none}
.p{position:fixed;left:16px;top:16px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 12px;max-width:300px}
.p h1{font-size:15px;margin:0 0 4px}.p div{font-size:12.5px;color:var(--muted)}
.b{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
button{font:inherit;font-size:12.5px;padding:5px 9px;border-radius:7px;border:1px solid var(--line);background:transparent;color:var(--ink);cursor:pointer}
button.on{background:#d9822b;border-color:#d9822b;color:#fff}
@media (max-width:600px){.p{left:8px;right:8px;top:8px;max-width:none}}
</style></head><body><canvas id="c"></canvas>
<div class="p"><h1>END CAP</h1><div>80 × 17 × 19.67 mm · 7 teeth per leg</div>
<div class="b"><button data-v="iso" class="on">Iso</button><button data-v="front">Front</button><button data-v="side">Side</button><button data-v="bottom">Bottom</button><button id="ed" class="on">Edges</button></div>
<div style="margin-top:6px;font-size:11.5px">Drag to rotate · wheel / pinch to zoom · right-drag to pan</div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const D=/*DATA*/null;
const cv=document.getElementById('c');const R=new THREE.WebGLRenderer({canvas:cv,antialias:true});R.setPixelRatio(Math.min(devicePixelRatio,2));
const S=new THREE.Scene();const cam=new THREE.PerspectiveCamera(30,1,1,2000);
S.add(new THREE.HemisphereLight(0xffffff,0x707070,1.0));const l=new THREE.DirectionalLight(0xffffff,0.6);l.position.set(60,120,90);S.add(l);
const l2=new THREE.DirectionalLight(0xffffff,0.25);l2.position.set(-80,-40,-60);S.add(l2);
const g=new THREE.BufferGeometry();
// CAD (x, y=extrusion, z=up) -> three (x, y=up, z)
const v=D.v,p=new Float32Array(v.length);for(let i=0;i<v.length;i+=3){p[i]=v[i];p[i+1]=v[i+2];p[i+2]=-v[i+1];}
g.setAttribute('position',new THREE.BufferAttribute(p,3));g.setIndex(D.t);g.computeVertexNormals();
const m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:0x4a6fa5,roughness:0.6,metalness:0.05,side:THREE.DoubleSide,polygonOffset:true,polygonOffsetFactor:1,polygonOffsetUnits:1}));
const E=new THREE.LineSegments(new THREE.EdgesGeometry(g,25),new THREE.LineBasicMaterial({color:0x111111,transparent:true,opacity:0.6}));
const root=new THREE.Group();root.add(m);root.add(E);root.position.y=-9.8;S.add(root);
const ed=document.getElementById('ed');ed.onclick=()=>{E.visible=!E.visible;ed.classList.toggle('on',E.visible);};
let th=0.7,ph=0.45,dist=150;const tgt=new THREE.Vector3(0,0,0);let rot=null,pan=null;
const views={iso:[0.7,0.45],front:[0,0.0],side:[Math.PI/2,0.0],bottom:[0.35,-1.3]};
document.querySelectorAll('[data-v]').forEach(b=>b.onclick=()=>{[th,ph]=views[b.dataset.v];document.querySelectorAll('[data-v]').forEach(x=>x.classList.toggle('on',x===b));});
cv.addEventListener('contextmenu',e=>e.preventDefault());
const ptr=new Map();let p0=0,d0=0;
cv.addEventListener('pointerdown',e=>{cv.setPointerCapture(e.pointerId);ptr.set(e.pointerId,[e.clientX,e.clientY]);
 if(ptr.size===2){const q=[...ptr.values()];p0=Math.hypot(q[0][0]-q[1][0],q[0][1]-q[1][1]);d0=dist;}
 if(e.button===2||e.shiftKey)pan=[e.clientX,e.clientY];else rot=[e.clientX,e.clientY];});
cv.addEventListener('pointermove',e=>{if(!ptr.has(e.pointerId))return;ptr.set(e.pointerId,[e.clientX,e.clientY]);
 if(ptr.size===2){const q=[...ptr.values()];const d=Math.hypot(q[0][0]-q[1][0],q[0][1]-q[1][1]);if(p0)dist=Math.max(40,Math.min(600,d0*p0/d));return;}
 if(rot){th-=(e.clientX-rot[0])*0.008;ph=Math.max(-1.5,Math.min(1.5,ph+(e.clientY-rot[1])*0.008));rot=[e.clientX,e.clientY];}
 if(pan){const k=dist/800;const r=new THREE.Vector3(Math.cos(th),0,-Math.sin(th));tgt.addScaledVector(r,-(e.clientX-pan[0])*k);tgt.y+=(e.clientY-pan[1])*k;pan=[e.clientX,e.clientY];}});
const up=e=>{ptr.delete(e.pointerId);if(ptr.size<2)p0=0;if(!ptr.size){rot=null;pan=null;}};cv.addEventListener('pointerup',up);cv.addEventListener('pointercancel',up);
cv.addEventListener('wheel',e=>{e.preventDefault();dist=Math.max(40,Math.min(600,dist*Math.exp(e.deltaY*0.001)));},{passive:false});
function rs(){R.setSize(innerWidth,innerHeight,false);cam.aspect=innerWidth/innerHeight;cam.updateProjectionMatrix();}addEventListener('resize',rs);rs();
const bg=()=>new THREE.Color(getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()||'#f2f2ef');S.background=bg();
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>S.background=bg());
(function f(){requestAnimationFrame(f);cam.position.set(tgt.x+dist*Math.sin(th)*Math.cos(ph),tgt.y+dist*Math.sin(ph),tgt.z+dist*Math.cos(th)*Math.cos(ph));cam.lookAt(tgt);R.render(S,cam);})();
</script></body></html>'''
open('../docs/index.html','w').write(html.replace('/*DATA*/null',json.dumps(data,separators=(',',':'))))
print(len(V),'verts',len(T),'tris')
