const assert=require('node:assert/strict');
const G=require('../assets/geometry.js'),P=require('../assets/projection.js');
const checks=[];
function test(name,fn){fn();checks.push(name);}
function meshIsClosed(p){
 const edges=new Map();
 for(const triangle of p.triangles)for(let j=0;j<3;j++){const a=triangle[j],b=triangle[(j+1)%3];assert.ok(a>=0&&a<p.vertices.length);const key=[a,b].sort((a,b)=>a-b).join(':');edges.set(key,(edges.get(key)||0)+1);}
 for(const uses of edges.values())assert.equal(uses,2,'Every closed-mesh edge joins exactly two faces');
 for(const point of p.vertices)for(const value of point)assert.ok(Number.isFinite(value));
}
test('Projected circle samples honor plane, radius and chord tolerance',()=>{
 const u=G.unit([1,2,0]),v=[0,0,1],center=[4,5,6],radius=13,tolerance=.006;
 const points=G.ringPoints(center,radius,u,v,{tolerance});
 for(const p of points){const delta=G.sub(p,center);assert.ok(Math.abs(Math.hypot(...delta)-radius)<1e-10);assert.ok(Math.abs(G.dot(delta,G.cross(u,v)))<1e-10);}
 for(let i=1;i<points.length;i++){const middle=points[i].map((n,k)=>(n+points[i-1][k])/2);assert.ok(radius-Math.hypot(...G.sub(middle,center))<=tolerance+1e-10);}
 assert.throws(()=>G.ringPoints(center,radius,u,u));
});
test('Rounded housing profiles preserve width, height and corner radii',()=>{
 const points=G.roundedRectangle(80,50,5);
 assert.equal(Math.min(...points.map(p=>p[0])),-40);assert.equal(Math.max(...points.map(p=>p[0])),40);
 assert.equal(Math.min(...points.map(p=>p[1])),0);assert.equal(Math.max(...points.map(p=>p[1])),50);
 assert.throws(()=>G.roundedRectangle(10,10,6));
});
test('Hollow lathes preserve their bore and closed surface connectivity',()=>{
 const p=G.part('tube','Tube');G.lathe(p,[[0,5],[20,5],[20,3],[0,3]]);meshIsClosed(p);
 for(const v of p.vertices)assert.ok(Math.hypot(v[1],v[2])>=3-1e-10);
 assert.throws(()=>G.lathe(p,[[0,-1],[2,1],[2,0]]));
});
test('Spring wire is closed and fits its radial envelope',()=>{
 const p=G.part('spring','Spring');G.spring(p,{x0:0,x1:12,radius:3,wire:.3,turns:6});meshIsClosed(p);
 for(const v of p.vertices){const r=Math.hypot(v[1],v[2]);assert.ok(r>=2.7-1e-8&&r<=3.3+1e-8);}
 assert.throws(()=>G.spring(p,{x0:0,x1:2,radius:3,wire:.3,turns:6}));
});
test('Thread pitch and handedness repeat at the same angular phase',()=>{
 for(const hand of[-1,1]){const p=G.part('thread','Thread');G.helix(p,{x0:0,x1:8,radius:2,pitch:2,hand});const a=p.lines[0].a,b=p.lines[96].a;assert.ok(Math.abs(b[0]-a[0]-2)<1e-10);assert.ok(Math.hypot(b[1]-a[1],b[2]-a[2])<1e-10);assert.equal(Math.sign(p.lines[0].b[2]),hand);}
});
test('Knurl starts and screw proportions produce valid finite geometry',()=>{
 const p=G.part('grip','Grip');G.knurl(p,{x0:1,x1:19,radius:4,starts:8,pitch:30});assert.equal(p.lines.length,8*2*Math.ceil(18/30*96));
 const screw=G.part('screw','Screw');G.screw(screw,{length:10,radius:1.5,headRadius:3,headHeight:2});meshIsClosed(screw);
 assert.equal(Math.max(...screw.vertices.map(p=>p[0])),12);assert.ok(Math.abs(Math.max(...screw.vertices.map(p=>Math.hypot(p[1],p[2])))-3)<1e-10);
});
test('Isolation restores edges hidden by another complete solid',()=>{
 const back=G.part('back','Back',[0,30,0]);G.lathe(back,[[0,4],[12,4],[12,0],[0,0]]);
 const front=structuredClone(back);front.id='front';front.name='Front';front.explosion=[0,0,0];
 const offset=[-20/Math.sqrt(3),-20/Math.sqrt(3),20/Math.sqrt(3)];
 front.vertices=front.vertices.map(p=>G.add(p,offset));front.lines=front.lines.map(l=>({...l,a:G.add(l.a,offset),b:G.add(l.b,offset)}));
 const frozen=JSON.stringify([back,front]);
 const together=P.render([back,front],{explosion:0}).markup,isolated=P.render([back,front],{explosion:0,isolated:'back'}).markup;
 const hidden=together.match(/data-item="back"[^]*?<\/g>/)[0];
 assert.ok(isolated.length>hidden.length*2,'Isolated geometry must restore obscured lines');assert.ok(!isolated.includes('data-item="front"'));
 assert.equal(JSON.stringify([back,front]),frozen,'Projection must not mutate model geometry');
 assert.equal(P.render([back,front],{explosion:0}).markup,together,'Zero spacing must be deterministic');
 assert.notEqual(P.render([back,front],{explosion:1}).markup,together);
});
test('Edge-on cylinder facets retain both long silhouettes at different resolutions',()=>{
 for(const segments of[144,180,240]){
  const stem=G.part('stem','Upright stem');G.lathe(stem,[[0,3],[80,3],[80,0],[0,0]],{segments});
  const upright=([x,y,z])=>[y,z,x];stem.vertices=stem.vertices.map(upright);stem.lines=stem.lines.map(l=>({...l,a:upright(l.a),b:upright(l.b)}));
  const markup=P.render([stem]).markup,lengths=[...markup.matchAll(/M([-\d.]+) ([-\d.]+)L([-\d.]+) ([-\d.]+)/g)].map(m=>Math.hypot(m[3]-m[1],m[4]-m[2]));
  assert.ok(lengths.filter(length=>length>200).length>=2,`Missing stem outlines with ${segments} segments`);
 }
});
test('Camera angles preserve distances and keep world Z upright at zero roll',()=>{
 for(const elevation of[0,20,65,90]){
  const camera={azimuth:-125,elevation,roll:0},origin=P.project([0,0,0],camera),top=P.project([0,0,20],camera);
  assert.ok(Math.abs(top[0]-origin[0])<1e-10);assert.ok(Math.abs(Math.hypot(...top)-20)<1e-10);
  const axes=[[1,0,0],[0,1,0],[0,0,1]].map(p=>P.project(p,camera));
  for(const axis of axes)assert.ok(Math.abs(Math.hypot(...axis)-1)<1e-10);
  assert.ok(Math.abs(G.dot(axes[0],axes[1]))<1e-10);
 }
 assert.throws(()=>P.project([0,0,0],{elevation:100}));
});
test('Concave extrusions preserve volume, winding and open notches',()=>{
 const profile=[[0,0],[8,0],[8,2],[3,2],[3,7],[0,7]];
 for(const outline of[profile,[...profile].reverse(),[...profile,profile[0]]]){
  const p=G.part('bracket','Bracket');G.extrude(p,outline,{depth:4});meshIsClosed(p);
  const volume=p.triangles.reduce((sum,[a,b,c])=>sum+G.dot(p.vertices[a],G.cross(p.vertices[b],p.vertices[c]))/6,0);
  assert.ok(Math.abs(volume-124)<1e-8,'Cap triangles must exclude the concave notch');
  for(const face of p.triangles){const c=[0,1,2].map(k=>face.reduce((s,i)=>s+p.vertices[i][k],0)/3);assert.ok(!(c[0]>3+1e-9&&c[1]>2+1e-9),'No surface crosses the open notch');}
 }
 const invalid=G.part('invalid','Invalid');
 assert.throws(()=>G.extrude(invalid,[[0,0],[4,4],[0,4],[4,0]],{depth:3}));
 assert.equal(invalid.vertices.length,0,'Rejected contours must leave the part unchanged');
 assert.throws(()=>G.extrude(invalid,profile,{depth:0}));
 const rounded=G.part('rounded','Rounded');G.extrude(rounded,G.roundedRectangle(20,10,5),{depth:2});meshIsClosed(rounded);
});
test('Rigid placement moves every feature and rotates explosion vectors without translation',()=>{
 const p=G.part('tube','Tube',[5,0,0]);G.lathe(p,[[0,3],[12,3],[12,2],[0,2]]);
 const before=structuredClone(p),origin=[10,20,30];G.transform(p,{origin,xAxis:[0,0,1],yAxis:[1,0,0],zAxis:[0,1,0]});
 assert.deepEqual(p.vertices[0],[before.vertices[0][1]+10,before.vertices[0][2]+20,before.vertices[0][0]+30]);
 assert.deepEqual(p.explosion,[0,0,5]);
 assert.ok(Math.abs(Math.hypot(...G.sub(p.lines[0].a,p.lines[0].b))-Math.hypot(...G.sub(before.lines[0].a,before.lines[0].b)))<1e-10);
 assert.throws(()=>G.transform(p,{zAxis:[0,0,-1]}),'Reflections must not silently invert surface winding');
});
test('Paper anchors agree with rendered bounds after camera and explosion changes',()=>{
 const p=G.part('block','Block',[30,-10,5]);G.extrude(p,[[0,0],[8,0],[8,12],[0,12]],{depth:4});
 for(const explosion of[0,.7,1.5]){
  const camera={azimuth:-65,elevation:22,roll:0},result=P.render([p],{explosion,camera});
  const points=p.vertices.map(v=>P.project(G.add(v,p.explosion.map(n=>n*explosion)),camera).slice(0,2).map((n,i)=>n*result.scale+result.offset[i]));
  for(const[k,axis,size]of[[0,'x','width'],[1,'y','height']]){
   assert.ok(Math.abs(Math.min(...points.map(p=>p[k]))-result.bounds[axis])<1e-9);
   assert.ok(Math.abs(Math.max(...points.map(p=>p[k]))-result.bounds[axis]-result.bounds[size])<1e-9);
  }
 }
});
test('Missing or invalid geometry fails before producing a blank NaN drawing',()=>{
 assert.throws(()=>P.render([G.part('empty','Empty')]),/finite vertices/);
 const p=G.part('broken','Broken');p.vertices.push([0,0,0],[NaN,1,2]);
 assert.throws(()=>P.render([p]),/finite vertices/);
});
test('Small spring silhouettes are identical in millimeters and meters',()=>{
 const drawings=[1,.001].map(scale=>{
  const p=G.part('spring','Miniature spring');G.spring(p,{x0:0,x1:1.2*scale,radius:.3*scale,wire:.03*scale,turns:6});
  return P.render([p],{explosion:0}).markup;
 });
 assert.equal(drawings[0],drawings[1],'Changing model units must not erase small faces');
});
test('Submesh composition preserves indices, features and the complete part identity',()=>{
 const target=G.part('assembly-piece','One fabricated part',[0,0,20]),source=G.part('piece','Construction piece');
 const square=[[0,0],[4,0],[4,4],[0,4]];
 G.extrude(target,square,{depth:2});G.extrude(source,square,{depth:2});G.transform(source,{origin:[6,0,0]});
 const sourceBefore=JSON.stringify(source),count=target.vertices.length;G.merge(target,source);meshIsClosed(target);
 assert.equal(target.vertices.length,count+source.vertices.length);assert.deepEqual(target.explosion,[0,0,20]);assert.equal(target.id,'assembly-piece');
 assert.equal(JSON.stringify(source),sourceBefore,'Merging must leave reusable source geometry unchanged');
 const targetBefore=JSON.stringify(target);G.transform(source,{origin:[100,0,0]});assert.equal(JSON.stringify(target),targetBefore,'Merged features must not alias their source');
 const moving=G.part('moving','Moving piece',[1,0,0]);assert.throws(()=>G.merge(target,moving),/zero explosion/);assert.throws(()=>G.merge(target,target),/itself/);
});
console.log(JSON.stringify({passed:checks.length,checks},null,2));
