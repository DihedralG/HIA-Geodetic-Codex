const TAU=Math.PI*2, DEG=Math.PI/180;
const PLANETS={
  Mercury:{ecc:.205636,obl:.034,peri:257.46,year:87.97,day:4222.6,color:'#b7ada2'},
  Venus:{ecc:.006777,obl:177.36,peri:311.60,year:224.70,day:2802,color:'#e8c788'},
  Earth:{ecc:.016711,obl:23.439,peri:282.94,year:365.256,day:24,color:'#72e7e0'},
  Mars:{ecc:.093394,obl:25.19,peri:251.00,year:686.98,day:24.6597,color:'#d27349'},
  Jupiter:{ecc:.048386,obl:3.13,peri:194.73,year:4332.59,day:9.925,color:'#d7b28a'},
  Saturn:{ecc:.053862,obl:26.73,peri:272.60,year:10759.22,day:10.656,color:'#e5bd67'},
  Uranus:{ecc:.047257,obl:97.77,peri:350.95,year:30688.5,day:17.24,color:'#91e2e6'},
  Neptune:{ecc:.008590,obl:28.32,peri:224.96,year:60182,day:16.11,color:'#5f86ef'}
};
const $=id=>document.getElementById(id);
const state={planet:'Earth',mode:'preset',epoch:0,ecc:PLANETS.Earth.ecc,obl:PLANETS.Earth.obl,peri:PLANETS.Earth.peri,lat:44.4,time:12,samples:360,compare:true,points:false};
const els=['planet','epoch','ecc','obl','peri','lat','time','samples','compare','points'].reduce((a,k)=>(a[k]=$(k),a),{});
Object.keys(PLANETS).forEach(name=>els.planet.add(new Option(name,name)));

function wrap(a){return ((a%TAU)+TAU)%TAU} function wrapPi(a){return ((a+Math.PI)%TAU+TAU)%TAU-Math.PI}
function solveKepler(M,e){let E=M+e*Math.sin(M);for(let i=0;i<12;i++){const d=(M-(E-e*Math.sin(E)))/(1-e*Math.cos(E));E+=d;if(Math.abs(d)<1e-12)break}return E}
function deepParams(base,year){
  if(state.planet!=='Earth') return {...base,deepNote:'Epoch shifts perihelion phase only for non-Earth presets in v0.1.'};
  const t=year;
  const e=Math.max(.002,Math.min(.065,.016711+.012*Math.sin(TAU*t/100000)+.006*Math.sin(TAU*t/405000)));
  const o=23.439+1.15*Math.sin(TAU*t/41000);
  const p=wrap((base.peri+360*t/21000)*DEG)/DEG;
  return {...base,ecc:e,obl:o,peri:p,deepNote:'Exploratory sinusoidal Milankovitch proxy; not a long-term ephemeris.'}
}
function activeParams(){let p={...PLANETS[state.planet]};if(state.mode==='deep')p=deepParams(p,state.epoch);if(state.mode==='manual')p={...p,ecc:state.ecc,obl:state.obl,peri:state.peri};return p}
function generate(params,count=state.samples){
  const e=params.ecc,eps=params.obl*DEG,lp=params.peri*DEG,pts=[];
  for(let i=0;i<count;i++){
    const M=TAU*i/count,E=solveKepler(M,e),v=2*Math.atan2(Math.sqrt(1+e)*Math.sin(E/2),Math.sqrt(1-e)*Math.cos(E/2));
    const lambda=wrap(v+lp),mean=wrap(M+lp),ra=wrap(Math.atan2(Math.cos(eps)*Math.sin(lambda),Math.cos(lambda)));
    const dec=Math.asin(Math.sin(eps)*Math.sin(lambda)),eotAngle=wrapPi(mean-ra),eotHours=eotAngle/TAU*params.day;
    const H=TAU*(state.time/24-.5)+eotAngle,phi=state.lat*DEG;
    const alt=Math.asin(Math.sin(phi)*Math.sin(dec)+Math.cos(phi)*Math.cos(dec)*Math.cos(H));
    const az=wrap(Math.atan2(-Math.sin(H)*Math.cos(dec),Math.sin(dec)*Math.cos(phi)-Math.cos(dec)*Math.sin(phi)*Math.cos(H)));
    pts.push({i,yearFraction:i/count,meanAnomaly:M/DEG,eccentricAnomaly:E/DEG,trueAnomaly:wrap(v)/DEG,solarLongitude:lambda/DEG,rightAscension:ra/DEG,declination:dec/DEG,equationOfTimeHours:eotHours,altitude:alt/DEG,azimuth:az/DEG});
  }
  return pts
}
function fmtEpoch(y){if(y===0)return'0 CE';return y<0?`${Math.abs(y).toLocaleString()} BCE`:`${y.toLocaleString()} CE`}
function setStateFromControls(){['epoch','ecc','obl','peri','lat','time','samples'].forEach(k=>state[k]=+els[k].value);state.planet=els.planet.value;state.compare=els.compare.checked;state.points=els.points.checked;render()}
function syncControls(resetManual=true){
  const p=state.mode==='deep'?deepParams({...PLANETS[state.planet]},state.epoch):PLANETS[state.planet];
  if(resetManual){state.ecc=p.ecc;state.obl=p.obl;state.peri=p.peri;els.ecc.value=p.ecc;els.obl.value=p.obl;els.peri.value=p.peri}
  const locked=state.mode!=='manual';['ecc','obl','peri'].forEach(k=>els[k].disabled=locked);els.epoch.disabled=state.mode!=='deep';
  render()
}
function svg(tag,attrs={},text=''){const n=document.createElementNS('http://www.w3.org/2000/svg',tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(text)n.textContent=text;return n}
function scale(v,a,b,c,d){return c+(v-a)/(b-a)*(d-c)}
function pathFor(points,xfn,yfn){return points.map((p,i)=>`${i?'L':'M'}${xfn(p).toFixed(2)},${yfn(p).toFixed(2)}`).join(' ')}
function intersections(pts){
  const P=pts.map(p=>[p.equationOfTimeHours,p.declination]);let hits=0;
  const cross=(a,b,c,d)=>{const den=(d[1]-c[1])*(b[0]-a[0])-(d[0]-c[0])*(b[1]-a[1]);if(Math.abs(den)<1e-10)return false;const ua=((d[0]-c[0])*(c[1]-a[1])-(d[1]-c[1])*(c[0]-a[0]))/den,ub=((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/den;return ua>0&&ua<1&&ub>0&&ub<1};
  for(let i=0;i<P.length-1;i++)for(let j=i+3;j<P.length-1;j++){if(i===0&&j===P.length-2)continue;if(cross(P[i],P[i+1],P[j],P[j+1]))hits++}return hits
}
function shapeName(pts){const n=intersections(pts);if(n>0)return'crossed figure-eight';const x=pts.map(p=>p.equationOfTimeHours),y=pts.map(p=>p.declination),ratio=(Math.max(...x)-Math.min(...x))/(Math.max(...y)-Math.min(...y)+1e-6);return ratio>.08?'asymmetric loop':'compressed loop'}
function drawAnalemma(pts,base){
  const root=$('analemmaPlot');root.innerHTML='';const pad={l:60,r:22,t:22,b:45};
  const all=base?[...pts,...base]:pts,xv=all.map(p=>p.equationOfTimeHours),yv=all.map(p=>p.declination);let xmin=Math.min(...xv),xmax=Math.max(...xv),ymin=Math.min(...yv),ymax=Math.max(...yv);const xp=(xmax-xmin||1)*.15,yp=(ymax-ymin||1)*.12;xmin-=xp;xmax+=xp;ymin-=yp;ymax+=yp;
  const X=p=>scale(p.equationOfTimeHours,xmin,xmax,pad.l,760-pad.r),Y=p=>scale(p.declination,ymin,ymax,460-pad.b,pad.t);
  for(let i=0;i<=4;i++){const x=scale(i,0,4,pad.l,760-pad.r);root.append(svg('line',{x1:x,y1:pad.t,x2:x,y2:460-pad.b,class:'gridline'}));const val=scale(i,0,4,xmin,xmax);root.append(svg('text',{x,y:440,'text-anchor':'middle',class:'axis-label'},formatTime(val)))}
  for(let i=0;i<=4;i++){const y=scale(i,0,4,460-pad.b,pad.t);root.append(svg('line',{x1:pad.l,y1:y,x2:760-pad.r,y2:y,class:'gridline'}));const val=scale(i,0,4,ymin,ymax);root.append(svg('text',{x:50,y:y+4,'text-anchor':'end',class:'axis-label'},`${val.toFixed(0)}°`))}
  if(xmin<0&&xmax>0){const x=scale(0,xmin,xmax,pad.l,760-pad.r);root.append(svg('line',{x1:x,y1:pad.t,x2:x,y2:460-pad.b,class:'zero-line'}))}
  if(base)root.append(svg('path',{d:pathFor(base,X,Y)+' Z',class:'trace baseline'}));root.append(svg('path',{d:pathFor(pts,X,Y)+' Z',class:'trace'}));
  if(state.points)pts.filter((_,i)=>i%Math.max(1,Math.round(pts.length/72))===0).forEach(p=>root.append(svg('circle',{cx:X(p),cy:Y(p),r:2.1,class:'sample'})));
  root.append(svg('text',{x:410,y:457,'text-anchor':'middle',class:'axis-label'},`EQUATION OF TIME · ${PLANETS[state.planet].day>100?'hours':'hh:mm'} offset`));root.append(svg('text',{x:15,y:220,transform:'rotate(-90 15 220)','text-anchor':'middle',class:'axis-label'},'SOLAR DECLINATION'));
}
function formatTime(h){const sign=h<0?'−':'+';const a=Math.abs(h);if(PLANETS[state.planet].day>100)return`${sign}${a.toFixed(0)}h`;const m=a*60;return`${sign}${Math.floor(m/60)}:${String(Math.round(m%60)).padStart(2,'0')}`}
function drawSky(pts){
  const root=$('skyPlot');root.innerHTML='';const pad={l:55,r:25,t:20,b:50},X=p=>scale(p.azimuth,0,360,pad.l,760-pad.r),Y=p=>scale(p.altitude,-90,90,390-pad.b,pad.t);
  [0,90,180,270,360].forEach(v=>{const x=scale(v,0,360,pad.l,760-pad.r);root.append(svg('line',{x1:x,y1:pad.t,x2:x,y2:390-pad.b,class:'gridline'}));root.append(svg('text',{x,y:366,'text-anchor':'middle',class:'axis-label'},v===0||v===360?'N':v===90?'E':v===180?'S':'W'))});
  [-90,-45,0,45,90].forEach(v=>{const y=scale(v,-90,90,390-pad.b,pad.t);root.append(svg('line',{x1:pad.l,y1:y,x2:760-pad.r,y2:y,class:v===0?'horizon':'gridline'}));root.append(svg('text',{x:45,y:y+4,'text-anchor':'end',class:'axis-label'},`${v}°`))});
  let runs=[],current=[pts[0]];for(let i=1;i<pts.length;i++){if(Math.abs(pts[i].azimuth-pts[i-1].azimuth)>180){runs.push(current);current=[]}current.push(pts[i])}runs.push(current);
  runs.forEach(run=>root.append(svg('path',{d:pathFor(run,X,Y),class:'trace'})));const below=pts.filter(p=>p.altitude<0);if(below.length>1)root.append(svg('path',{d:pathFor(below,X,Y),class:'trace below'}));
  root.append(svg('text',{x:410,y:387,'text-anchor':'middle',class:'axis-label'},'AZIMUTH · LOCAL HORIZON FRAME'));
}
function renderMetrics(pts,p){const dec=pts.map(x=>x.declination),eot=pts.map(x=>x.equationOfTimeHours),above=pts.filter(x=>x.altitude>=0).length/pts.length;const entries=[[`${(Math.max(...dec)-Math.min(...dec)).toFixed(2)}°`,'declination span'],[formatTime(Math.max(...eot)-Math.min(...eot)),'time span'],[`${(above*100).toFixed(0)}%`,'samples above horizon'],[`${p.year.toLocaleString()} d`,'orbital period']];$('metrics').innerHTML=entries.map(([v,l])=>`<div class="metric"><b>${v}</b><span>${l}</span></div>`).join('')}
function renderClocks(p){const clocks=[['Daily rotation',p.day,'hours',Math.min(100,24/p.day*100)],['Annual orbit',p.year,'days',Math.min(100,365.256/p.year*100)],['Axial precession',state.planet==='Earth'?25772:'unmodeled','years',65],['Obliquity cycle',state.planet==='Earth'?41000:'unmodeled','years',41],['Eccentricity cycle',state.planet==='Earth'?'~100k':'unmodeled','years',28]];$('clockStack').innerHTML=clocks.map(([n,v,u,w])=>`<div class="clock-row"><div><b>${n}</b><small>${u}</small></div><div class="clock-bar"><i style="width:${w}%"></i></div><span>${typeof v==='number'?v.toLocaleString():v}</span></div>`).join('')}
function render(){
  const p=activeParams(),pts=generate(p),base=(state.compare&&(state.mode!=='preset'))?generate(PLANETS[state.planet]):null;
  $('epochOut').textContent=fmtEpoch(state.epoch);$('eccOut').textContent=p.ecc.toFixed(4);$('oblOut').textContent=`${p.obl.toFixed(2)}°`;$('periOut').textContent=`${p.peri.toFixed(1)}°`;$('latOut').textContent=`${Math.abs(state.lat).toFixed(1)}° ${state.lat>=0?'N':'S'}`;$('timeOut').textContent=`${String(Math.floor(state.time)).padStart(2,'0')}:${String(Math.round(state.time%1*60)).padStart(2,'0')}`;$('samplesOut').textContent=state.samples;
  $('analemmaTitle').textContent=`${state.planet} analemma`;$('siteMeta').textContent=`${Math.abs(state.lat).toFixed(1)}° ${state.lat>=0?'N':'S'} · ${$('timeOut').textContent}`;$('shapeBadge').textContent=shapeName(pts);
  drawAnalemma(pts,base);drawSky(pts);renderMetrics(pts,p);renderClocks(p);
  const solves=state.samples,transforms=state.samples*3,pairs=Math.round(state.samples*(state.samples-1)/2);$('computeStats').innerHTML=`<div class="compute-stat"><b>${solves.toLocaleString()}</b><span>independent Kepler solves</span></div><div class="compute-stat"><b>${transforms.toLocaleString()}</b><span>coordinate transforms</span></div><div class="compute-stat"><b>${pairs.toLocaleString()}</b><span>possible pair tests</span></div>`;if($('benchTier'))renderBenchmark();
}
function tracePayload(){const p=activeParams();return{instrument:'Planetary Chronometer Scale Lab',version:'0.2.0',boundary:'Exploratory scale harness. This output is not a P001 reference result and cannot modify P001.',createdAt:new Date().toISOString(),modelTier:state.mode,warning:state.mode==='deep'?'Exploratory periodic proxy; not a validated long-term ephemeris.':'Analytic two-body teaching/research model; validate against an authoritative ephemeris before scientific use.',planet:state.planet,epochYear:state.epoch,observer:{latitudeDeg:state.lat,localMeanTimeHours:state.time},parameters:p,method:{keplerEquation:'M = E - e sin(E)',declination:'asin(sin(obliquity) sin(solar longitude))',equationOfTime:'wrapped(mean solar longitude - apparent right ascension)',localProjection:'equatorial to horizontal transform'},samples:generate(p)}}
function download(name,type,data){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([data],{type}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500)}
function exportCSV(){const t=tracePayload(),cols=['planet','epochYear','sample','yearFraction','meanAnomaly','eccentricAnomaly','trueAnomaly','solarLongitude','rightAscension','declination','equationOfTimeHours','altitude','azimuth','eccentricity','obliquity','perihelionPhase'];const rows=[cols.join(',')];t.samples.forEach(p=>rows.push([t.planet,t.epochYear,p.i,p.yearFraction,p.meanAnomaly,p.eccentricAnomaly,p.trueAnomaly,p.solarLongitude,p.rightAscension,p.declination,p.equationOfTimeHours,p.altitude,p.azimuth,t.parameters.ecc,t.parameters.obl,t.parameters.peri].join(',')));download(`${state.planet.toLowerCase()}-analemma-${state.epoch}.csv`,'text/csv',rows.join('\n'))}

const BENCH={p001:{label:'P001 · Earth replay',defaults:[1,24,2,1],gate:'Validated P001 truth bundle required'},p002:{label:'P002 · Mars replay',defaults:[1,24,2,64],gate:'Held until P001 validates'},p003:{label:'P003 · catalog',defaults:[1000,120,24,64],gate:'Catalog uncertainty must remain explicit'},p004:{label:'P004 · synthetic',defaults:[10000,240,48,128],gate:'Ground truth generated before execution'},p005:{label:'P005 · renderer',defaults:[1000,120,24,8],gate:'Machine-readable coordinates are authoritative'}};
const benchIds=['objects','epochs','observers','draws'];
function human(n){if(n>=1e15)return`${(n/1e15).toFixed(2)} quadrillion`;if(n>=1e12)return`${(n/1e12).toFixed(2)} trillion`;if(n>=1e9)return`${(n/1e9).toFixed(2)} billion`;if(n>=1e6)return`${(n/1e6).toFixed(2)} million`;return Math.round(n).toLocaleString()}
function benchmarkSpec(){const tier=$('benchTier').value,vals=Object.fromEntries(benchIds.map(k=>[k,+$(k).value])),evaluations=vals.objects*vals.epochs*vals.observers*vals.draws,curvePoints=evaluations*state.samples;return{specification:'ChiR Planetary Chronometer Scale Benchmark',version:'0.2.0',createdAt:new Date().toISOString(),referenceContract:{dependency:'one-way from validated P001 truth bundle',p001Immutable:true,forbidden:['protected-date fitting','corridor fitting','preferred-star selection','site feedback into astronomy','discarding null or negative results'],mergeRule:'Solar and polar/stellar ledgers merge only after independent computation.'},tier,gate:BENCH[tier].gate,dimensions:{...vals,samplesPerCurve:state.samples},kernel:{id:'K-01',name:'Bounded inverse chronometer search',input:'Frozen truth bundle plus declared uncertainty bounds',parallelUnit:'candidate state × epoch × observer',synchronization:'after independent residual calculation',output:'residual ledger and uncertainty-preserving ranking',classicalBaselines:['vectorized CPU','GPU','distributed ensemble'],quantumStatus:'candidate subroutine only; no advantage claimed',quantumCandidates:['bounded search','amplitude estimation'],requiredAccounting:['logical qubits','circuit depth','fault-tolerant operations','data-loading cost','wall time','energy','solution quality','failure rate']},projected:{candidateEvaluations:evaluations,curvePoints,coordinateTransforms:curvePoints*3,approxOutputBytes:curvePoints*88}}}
function renderBenchmark(){const b=benchmarkSpec(),d=b.dimensions;$('objectsOut').textContent=d.objects.toLocaleString();$('epochsOut').textContent=d.epochs.toLocaleString();$('observersOut').textContent=d.observers.toLocaleString();$('drawsOut').textContent=d.draws.toLocaleString();$('tierBadge').textContent=BENCH[b.tier].label;$('candidateCount').textContent=human(b.projected.candidateEvaluations);$('runMetrics').innerHTML=`<div><span>curve points</span><b>${human(b.projected.curvePoints)}</b></div><div><span>frame transforms</span><b>${human(b.projected.coordinateTransforms)}</b></div><div><span>raw output estimate</span><b>${human(b.projected.approxOutputBytes)} bytes</b></div><div><span>release gate</span><b>${BENCH[b.tier].gate}</b></div>`;const big=b.projected.candidateEvaluations>=1e9;$('quantumVerdict').textContent=big?'HPC-scale workload; quantum unproven':'Classical baseline required';$('verdictCopy').textContent=big?'The run is large enough for serious distributed load testing. Size alone is not evidence of quantum advantage.':'Complete the deterministic classical baseline before proposing any alternate architecture.'}
function setBenchDefaults(){const cfg=BENCH[$('benchTier').value];benchIds.forEach((k,i)=>$(k).value=cfg.defaults[i]);renderBenchmark()}
els.planet.addEventListener('change',()=>{state.planet=els.planet.value;syncControls(true)});['epoch','ecc','obl','peri','lat','time','samples','compare','points'].forEach(k=>els[k].addEventListener('input',setStateFromControls));
document.querySelectorAll('.mode').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.mode').forEach(x=>x.classList.remove('active'));b.classList.add('active');state.mode=b.dataset.mode;syncControls(true)}));
$('resetBtn').addEventListener('click',()=>{Object.assign(state,{planet:'Earth',mode:'preset',epoch:0,lat:44.4,time:12,samples:360,compare:true,points:false});els.planet.value='Earth';els.epoch.value=0;els.lat.value=44.4;els.time.value=12;els.samples.value=360;els.compare.checked=true;els.points.checked=false;document.querySelectorAll('.mode').forEach(x=>x.classList.toggle('active',x.dataset.mode==='preset'));syncControls(true)});
$('csvBtn').addEventListener('click',exportCSV);$('jsonBtn').addEventListener('click',()=>download(`${state.planet.toLowerCase()}-trace-${state.epoch}.json`,'application/json',JSON.stringify(tracePayload(),null,2)));
$('benchTier').addEventListener('change',setBenchDefaults);benchIds.forEach(k=>$(k).addEventListener('input',renderBenchmark));$('manifestBtn').addEventListener('click',()=>download(`chir-${$('benchTier').value}-benchmark-manifest.json`,'application/json',JSON.stringify(benchmarkSpec(),null,2)));
syncControls(true);renderBenchmark();
