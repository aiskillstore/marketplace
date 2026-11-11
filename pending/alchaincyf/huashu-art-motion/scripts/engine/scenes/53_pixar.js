/* Original un-faced laundry appliance. Programmed 3D geometry and acting; no film assets. */
SCENES['53_pixar']=(()=>{
 let R,S,C,washer,drum,door,loose,clothGeo,clothes=[],bubbles=[],towelMeshes=[];
 const T=()=>window.THREE, clamp=x=>Math.max(0,Math.min(1,x)),smooth=x=>{x=clamp(x);return x*x*(3-2*x)},mix=(a,b,u)=>a+(b-a)*u;
 function mat(color,rough=.65,metal=0){return new THREE.MeshStandardMaterial({color,roughness:rough,metalness:metal});}
 function box(x,y,z,w,h,d,m,parent=S){let o=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);o.position.set(x,y,z);o.castShadow=o.receiveShadow=true;parent.add(o);return o;}
 function sphere(x,y,z,rx,ry,rz,m,parent=S){let o=new THREE.Mesh(new THREE.SphereGeometry(1,24,16),m);o.position.set(x,y,z);o.scale.set(rx,ry,rz);o.castShadow=true;parent.add(o);return o;}
 function cylinder(x,y,z,r,h,m,parent=S){let o=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,48),m);o.position.set(x,y,z);o.castShadow=o.receiveShadow=true;parent.add(o);return o;}
 function tube(points,r,m,parent=S){let curve=new THREE.CatmullRomCurve3(points.map(p=>new THREE.Vector3(...p)));let o=new THREE.Mesh(new THREE.TubeGeometry(curve,48,r,8,false),m);parent.add(o);return o;}
 function rounded(w,h,d,r,m,parent){let s=new THREE.Shape(),x=-w/2,y=-h/2;s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);let g=new THREE.ExtrudeGeometry(s,{depth:d,bevelEnabled:true,bevelThickness:r/3,bevelSize:r/3,bevelSegments:3,steps:1,curveSegments:12});g.translate(0,0,-d/2);let o=new THREE.Mesh(g,m);o.castShadow=o.receiveShadow=true;parent.add(o);return o;}
 function fabricMat(color){const cv=document.createElement('canvas');cv.width=cv.height=256;let g=cv.getContext('2d');g.fillStyle=color;g.fillRect(0,0,256,256);for(let i=0;i<256;i+=2){g.fillStyle=i%4?'rgba(255,255,255,.08)':'rgba(40,25,10,.10)';g.fillRect(i,0,1,256);g.fillRect(0,i,256,1)}let tx=new THREE.CanvasTexture(cv);tx.wrapS=tx.wrapT=THREE.RepeatWrapping;tx.repeat.set(3,3);tx.colorSpace=THREE.SRGBColorSpace;return new THREE.MeshStandardMaterial({map:tx,roughness:.95,side:THREE.DoubleSide,bumpMap:tx,bumpScale:.012})}
 function fabricGeometry(){const nx=24,ny=16,g=new THREE.BufferGeometry(),a=[],idx=[],uv=[];for(let j=0;j<=ny;j++)for(let i=0;i<=nx;i++){a.push(i/nx,j/ny,0);uv.push(i/nx,j/ny)}for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){let k=j*(nx+1)+i;idx.push(k,k+1,k+nx+1,k+1,k+nx+2,k+nx+1)}g.setAttribute('position',new THREE.Float32BufferAttribute(a,3));g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();return g;}
 function init(){if(R)return;const THREE=T();if(!THREE)throw Error('53_pixar requires lib/three.min.js');
 R=new THREE.WebGLRenderer({alpha:false,antialias:true,preserveDrawingBuffer:true});R.setSize(1280,720);R.setPixelRatio(1);R.shadowMap.enabled=true;R.shadowMap.type=THREE.PCFSoftShadowMap;R.outputColorSpace=THREE.SRGBColorSpace;R.toneMapping=THREE.ACESFilmicToneMapping;R.toneMappingExposure=1.05;
 S=new THREE.Scene();S.background=new THREE.Color('#bed1bd');C=new THREE.PerspectiveCamera(37,16/9,.1,100);C.position.set(7.3,5.1,10.4);C.lookAt(.25,1.75,0);
 S.add(new THREE.HemisphereLight('#fff1d5','#527674',1.15));let key=new THREE.DirectionalLight('#ffedcc',3.1);key.position.set(-4,8,6);key.castShadow=true;key.shadow.mapSize.set(2048,2048);key.shadow.camera.left=-9;key.shadow.camera.right=9;key.shadow.camera.top=9;key.shadow.camera.bottom=-9;key.shadow.normalBias=.035;S.add(key);let fill=new THREE.DirectionalLight('#bde4dc',.55);fill.position.set(6,4,-1);S.add(fill);
 const tile=mat('#94b7ab'),grout=mat('#d5ddce'),cream=mat('#efdfbd'),wood=mat('#ae6a3d'),orange=mat('#c76e42'),steel=mat('#b2bdb9',.27,.7),dark=mat('#243e3d',.45,.25),rubber=mat('#4d5953',.9),linen=mat('#eadfca');
 box(0,-.16,0,24,.25,18,mat('#d2c8ad'));for(let i=-8;i<=8;i++)for(let j=-5;j<=4;j++){let m=((i+j)%2)?mat('#d3cbb7'):mat('#c9bda3');box(i*.85,-.025,j*.85,.823,.025,.823,m)}
 box(0,3.5,-3.1,18,7,.25,grout);box(-5.6,3.5,1.2,.2,7,8.4,mat('#b8c5ae'));
 for(let i=-9;i<10;i++)for(let j=0;j<7;j++)box(i*.66,.37+j*.64,-2.945,.64,.615,.035,tile);
 // sunlit window and sill
 box(3.4,4.5,-2.8,3.5,2.65,.12,cream);box(3.4,4.5,-2.68,3.15,2.32,.12,mat('#d7eddd'));box(3.4,4.5,-2.57,.09,2.38,.1,wood);box(3.4,4.5,-2.57,3.2,.09,.1,wood);box(3.4,3.22,-2.45,3.8,.18,.72,cream);
 for(let k=0;k<4;k++){let pot=cylinder(2.3+k*.65,3.48,-2.25,.19,.38,orange);for(let v=0;v<5;v++){let leaf=sphere(2.3+k*.65+(v-2)*.1,3.9+.1*Math.sin(v),-2.25,.08,.32,.045,mat('#517c52'));leaf.rotation.z=(v-2)*.35}}
 // washing-machine body with rounded enamel, separate rubber and chrome
 washer=new THREE.Group();washer.position.set(-.7,1.95,.45);S.add(washer);rounded(3.25,3.65,2.55,.18,mat('#e8dfc8',.36),washer);box(0,1.33,1.35,2.94,.62,.13,cream,washer);
 for(let x of [-1.18,1.18])for(let z of [-.88,.88])cylinder(x,-1.84,z,.17,.24,rubber,washer);
 let dial=cylinder(.96,1.34,1.47,.19,.19,steel,washer);dial.rotation.x=Math.PI/2;box(-.7,1.35,1.46,.96,.25,.065,dark,washer);box(-.75,1.35,1.504,.5,.035,.01,mat('#d7c36a'),washer);
 let rim=new THREE.Mesh(new THREE.TorusGeometry(1.06,.12,20,72),steel);rim.position.set(0,-.12,1.4);washer.add(rim);let seal=new THREE.Mesh(new THREE.TorusGeometry(.91,.08,16,72),rubber);seal.position.set(0,-.12,1.43);washer.add(seal);
 let cavity=cylinder(0,-.12,1.32,.93,.18,dark,washer);cavity.rotation.x=Math.PI/2;
 drum=new THREE.Group();drum.position.set(0,-.12,1.47);washer.add(drum);for(let i=0;i<28;i++){let a=i*Math.PI*2/28;let hole=sphere(Math.cos(a)*.78,Math.sin(a)*.78,0,.035,.035,.025,steel,drum)}
 for(let i=0;i<8;i++){const col=['#cb6b47','#b9d4c1','#cfaf65','#e3d4b9'][i%4];let m=sphere(Math.cos(i*1.7)*.48,Math.sin(i*1.7)*.48,.035,.33,.20,.09,fabricMat(col),drum);m.rotation.z=i*.8;clothes.push(m)}
 door=new THREE.Group();door.position.set(-1.02,-.12,1.49);washer.add(door);let ring=new THREE.Mesh(new THREE.TorusGeometry(.99,.075,16,80),mat('#e5eee5',.2,.35));ring.position.set(1.02,0,0);door.add(ring);let glass=cylinder(1.02,0,-.015,.92,.045,new THREE.MeshPhysicalMaterial({color:'#d1e6de',transparent:true,opacity:.14,roughness:.08,metalness:.1,side:THREE.DoubleSide}),door);glass.rotation.x=Math.PI/2;
 box(1.85,.08,.09,.1,.4,.14,steel,door);
 // a trapped orange sleeve; cloth topology deforms continuously around the clamped edge
 clothGeo=fabricGeometry();loose=new THREE.Mesh(clothGeo,fabricMat('#c86239'));loose.castShadow=true;washer.add(loose);
 // Basket and lived-in room detail
 cylinder(2.35,.54,1.25,.82,1.05,mat('#9e7450'));for(let k=0;k<10;k++){let rr=new THREE.Mesh(new THREE.TorusGeometry(.83,.018,5,64),cream);rr.rotation.x=Math.PI/2;rr.position.set(2.35,.08+k*.1,1.25);S.add(rr)}
 for(let k=0;k<12;k++)sphere(2.35+Math.sin(k*4)*.51,1.03+Math.sin(k*1.2)*.09,1.25+Math.cos(k*4)*.4,.33,.19,.28,fabricMat(k%2?'#e5c67b':'#b8c6b5'));
 box(-3.7,1.13,-1.3,2.2,.14,2,wood);for(let x of [-4.6,-2.8])box(x,.55,-1.3,.12,1.1,1.7,cream);for(let k=0;k<4;k++)box(-3.7,1.3+k*.13,-1.3,1.5,.12,1.2,mat(['#adbdad','#e1cfb2','#be7957','#d8bea0'][k]));
 tube([[-4.8,4,-2],[-2.8,3.91,-2],[0,3.92,-2],[2,4,-2]],.025,wood);
 for(let k=0;k<3;k++){const g=fabricGeometry(),m=new THREE.Mesh(g,new THREE.MeshStandardMaterial({color:['#dcbd88','#b7ccc1','#cf8465'][k],roughness:1,side:THREE.DoubleSide}));S.add(m);towelMeshes.push({m,g,x:-4.5+k*1.03})}
 // Feet shadow and restrained machine details.
 let cv=document.createElement('canvas');cv.width=cv.height=128;let cg=cv.getContext('2d');let sg=cg.createRadialGradient(64,64,5,64,64,62);sg.addColorStop(0,'rgba(23,39,32,.48)');sg.addColorStop(1,'rgba(23,39,32,0)');cg.fillStyle=sg;cg.fillRect(0,0,128,128);let sh=new THREE.Mesh(new THREE.PlaneGeometry(5,4),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(cv),transparent:true,depthWrite:false}));sh.rotation.x=-Math.PI/2;sh.position.set(-.7,.015,.4);S.add(sh);
 for(let k=0;k<6;k++)box(-.95+k*.15,-1.4,1.35,.085,.018,.018,rubber,washer);
 let tc=document.createElement('canvas');tc.width=512;tc.height=128;let tg=tc.getContext('2d');tg.fillStyle='#eee4cc';tg.fillRect(0,0,512,128);tg.fillStyle='#52675e';tg.font='bold 38px sans-serif';tg.fillText('MORNING / 06',28,80);let tm=new THREE.Mesh(new THREE.PlaneGeometry(1.18,.29),new THREE.MeshBasicMaterial({map:new THREE.CanvasTexture(tc)}));tm.position.set(-.55,.91,1.45);washer.add(tm);
 // Small scuffs, seams, baseboards avoid an empty toy stage.
 box(0,.17,-2.78,18,.18,.12,wood);for(let k=0;k<9;k++)box(-5+1.1*k,.45,-2.73,.22,.025,.015,mat('#638e82'));
 }
 function draw(c,lt){init();const t=Math.max(0,Math.min(6,lt));
 let jam=smooth((t-.9)/.5)*(1-smooth((t-3.5)/.5));let release=smooth((t-3.7)/.7);
 washer.rotation.z=(Math.sin(t*31)*.028+Math.sin(t*17)*.016)*jam;washer.position.y=1.95+Math.abs(Math.sin(t*31))*.035*jam;washer.position.x=-.7+Math.sin(t*26)*.035*jam;
 drum.rotation.z=t<1.4?t*4.5:6.3+Math.sin((t-1.4)*18)*.07*jam-(smooth((t-3.2)/1.2))*2.5+(t>4.5?(t-4.5)*1.4:0);
 door.rotation.y=-smooth((t-3.25)/.65)*.68;
 let a=clothGeo.attributes.position,nx=24,ny=16;for(let j=0;j<=ny;j++)for(let i=0;i<=nx;i++){let u=i/nx,v=j/ny,idx=j*(nx+1)+i;let tug=Math.sin(t*24-v*3)*.07*jam*(v+.1);let xx=.45+(u-.5)*.48+Math.sin(v*5+t*3)*.06*v;let yy=Math.max(-1.928+.006*Math.sin(u*24+v*8),-.99-v*1.12-release*2.05);let zz=1.59+v*.7+Math.sin(u*16+v*9)*.045+Math.sin(v*7-t*4)*v*.075+tug; a.setXYZ(idx,xx,yy,zz)}a.needsUpdate=true;clothGeo.computeVertexNormals();
 for(const {g,x} of towelMeshes){let a=g.attributes.position;for(let j=0;j<=16;j++)for(let i=0;i<=24;i++){let u=i/24,v=j/16,idx=j*25+i;a.setXYZ(idx,x+u*.75,3.9-v*1.35,-2+Math.sin(u*15)*.045+Math.sin(t*1.9+v*3+x)*v*.08)}a.needsUpdate=true;g.computeVertexNormals()}
 // Deliberately held camera: movement is in the machine, drum and cloth.
 R.render(S,C);c.drawImage(R.domElement,0,0,1920,1080);
 }
 return {draw};
})();
