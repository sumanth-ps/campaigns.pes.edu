/* ============================================================
   1. CONTENT MODEL — one object per program, all views read from it
   ============================================================ */
const ORDER = ['p1','p2','p3'];


const GROW = {
  p1:[
    ['Internships','1 major (4 months) + 2 short (2 months each).'],
    ['Placement & internship training from Year 3','Aptitude training, soft skill training, mock interviews and resume building.'],
  ],
  p2:[
    ['Internships','2 major (4 months each) + 2 short (2 months each).'],
    ['Placement & internship training from Year 3','Aptitude training, subject tests, soft skill training, mock interviews and resume building.'],
  ],
  p3:[
    ['Internships','2 major (4 months each) + 2 short (2 months each).'],
    ['Placement & internship training from Year 2','Aptitude training, soft skill training, mock interviews and resume building.'],
    ['Year 3 additions','Subject tests join the placement and internship training.'],
  ]
};

const DIFF = {
  p1:[
    ['Broad management foundation','Flexibility to explore marketing, Finance, HR, International Busines, Family Busines entrepreneurship and technology.'],
    ['Learning by doing','Case studies, internships, hackathons, conclaves, industry visits, peer learning and summits.'],
    ['Project management to ESG','Project management, supply chain, ESG, design thinking, digital marketing and communication sit alongside the functional core.'],
    ['Technology exposure','AI, Generative AI, business intelligence, data analytics, digital marketing, HR analytics, HRIS , financial technology, market intelligence tools and intelligent automation'],
    ['Internships','One major internship of four months and two short internships of two months each.'],
    ['Leadership & growth','B Talks, certifications, entrepreneurship week, management week, conclaves and summits.']
  ],
  p2:[
    ['Deeper specialisation','An Honours pathway with advanced learning in HR, Marketing, Finance, international business, family business and entrepreneurship, data science and ESG.'],
    ['Research and capstones','Research, live projects, capstone projects and research projects in the final years.'],
    ['Data toolkit','Python, R, Tableau, Power BI, AI, Generative AI and Excel.'],
    ['Four internships','Two major internships of four months each and two short internships of two months each.'],
    ['Built for higher studies','Prepares students for admission to higher education at top universities, with subject tests and research exposure.'],
    ['Leadership & growth','B Talks, certifications, entrepreneurship week, management week, conclaves and summits.']
  ],
  p3:[
    ['Management meets data','Business management, data analytics and technology in a single degree.'],
    ['Minors of your choice','Minors in Marketing, HR, Finance, Entrepreneurship or International Business.'],
    ['Modern analytics stack','Python, SQL, R, Tableau, Power BI, machine learning, AI, agentic AI, cloud computing, data engineering, NLP and big data.'],
    ['Projects that ship','Analytics projects, data visualisation, business cases, research, hackathons, industry projects, capstones and dissertations.'],
    ['Early placement training','Aptitude, soft skill and interview training start in Year 2, with subject tests added in Year 3.'],
    ['Honours pathway','Complete in three years, or continue into the four-year Honours route.']
  ]
};

const FOCUS = {
  p1:{
    'Core areas':['Project Management','Supply Chain','Human Resource','Marketing','Finance','International Business','Family Business & Entrepreneurship','ESG','Design Thinking','Digital Marketing','Communication'],
    'Technology exposure':['AI', 'Generative AI', 'Business Intelligence', 'Data Analytics', 'Digital Marketing', 'HR Analytics', 'HRIS', 'Financial Technology', 'Market Intelligence Tools', 'Intelligent Automation'],
    'Learning':['Case Studies','Internships','Hackathons','Conclaves','Industry Visits','Peer Learning','Summits']
  },
  p2:{
    'Core areas':['Human Resource','Marketing','Finance','International Business','Family Business & Entrepreneurship','Data Science','ESG'],
    'Technology exposure':['AI', 'Generative AI', 'Business Intelligence', 'Data Analytics', 'Digital Marketing', 'HR Analytics', 'HRIS', 'Financial Technology', 'Market Intelligence Tools', 'Intelligent Automation'],
    'Learning':['Advanced Case Studies','Research','Internships','Live Projects','Hackathons','Industry Exposure','Capstone Projects','Research Projects']
  },
  p3:{
    'Analytics tools':['Python','SQL','R','Tableau','Power BI','Machine Learning','AI','Agentic AI','Cloud Computing','Data Engineering','Social Media Analytics','NLP','Big Data'],
    'Business minors':['Marketing','HR','Finance','Entrepreneurship','International Business'],
    'Learning':['Analytics Projects','Data Visualisation','Business Cases','Research','Internships','Hackathons','Industry Projects','Capstones','Dissertations']
  }
};

const CAREERS = {
  p1:['Marketing','HR','Finance','Consulting','Business Development','Entrepreneurship','Investment Banking','Process Management'],
  p2:['Management','Consulting','Finance','Marketing','HR','Entrepreneurship','Business Analytics','Higher Studies'],
  p3:['Business Analyst','Data Analyst','Business Intelligence Analyst','Marketing Analyst','Financial Analyst','Analytics Consultant','HR Analyst','and many more']
};

const SEMS = [
  {label:'Semester 1', items:['Environmental Studies & Life Sciences','Financial Accounting with Tally','Principles & Practices of Management','Organizational Behaviour','Marketing Management','Production & Operations Management']},
  {label:'Semester 2', items:['Quantitative Techniques','Economics for Managers','Human Resource Management','Financial Management','International Business','Business Communication','Constitutional, Cyber & IP Law + Professional Ethics']},
  {label:'Semester 3', items:['Operations Research for Managers','Business Research Methods','Startup & Entrepreneurship Development','Essentials of Innovation & EDP – I','Social Internship','Sales and Distribution Management','Consumer Buying Behaviour','Cost Accounting','Indian Financial System and Market','Learning and Development','Managing Disruptive Tech in Talent Acquisition','Foreign Language (German)','Global Business Environment']},
  {label:'Semester 4', items:['Direct & Indirect Taxation','Business Law','Essentials of Innovation & EDP','Indian Philosophy & Management','Digital and Social Media Marketing','Brand Management','Investment and Portfolio Management','Management Accounting','Competency Mapping & Performance Mgmt','Organizational Change & Development','Cross Culture Management','Mergers and Acquisition']},
  {label:'Semester 5', items:['Corporate Internship','Project Management','Strategic Management','Ethics & Corporate Governance','Written Analysis & Communication','Strength & Conditioning','Yoga & Lifestyle Education – I','Integrated Marketing Communication','Retail Management','Derivatives and Risk Management','Foreign Exchange Management','Industrial Relations & Legal Aspects','Compensation and Reward Management','Data Visualization with Python & Tableau']},
  {label:'Semester 6', items:['Project Work','Social Media Analytics','Digital Design and Media Management','Intellectual Property Rights']},
  {label:'Semester 7', tag:'Honours', items:['Supply Chain Management','Information Security & Data Privacy','Spread Sheet Modelling','Data Engineering & Generative AI','Machine Learning & Artificial Intelligence','Term Paper']},
  {label:'Semester 8', tag:'Honours', items:['Dissertation']}
];
const withSub = (arr, i, sub) => arr.map((b,n)=> n===i ? {...b, sub} : b);

const CURRICULUM = {
  p1:{
    note:['BBA — 3 years','Six semesters of management fundamentals, functional electives and a corporate internship. Semester 6 is the final semester for the three-year exit.'],
    blocks: withSub(SEMS.slice(0,6), 5, 'Final semester of the 3-year BBA')
  },
  p2:{
    note:['BBA (Hons) — 4 years','Eight semesters. The first six match the BBA; semesters 7 and 8 add advanced learning, a term paper and a dissertation.'],
    blocks: SEMS
  },
  p3:{
    note:['BBA Business Analytics','Business management and analytics, three years with a four-year Honours pathway. The core semesters below are shared with BBA; the analytics majors and tools are listed under Subject groups. Confirm the exact analytics course map with admissions.'],
    blocks: SEMS
  }
};

/* ============================================================
   2. RENDER
   ============================================================ */
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

ORDER.forEach(k=>{
  const d = document.querySelector(`[data-diff="${k}"]`);
  if(d) d.innerHTML = DIFF[k].map((x,i)=>
    `<div class="diff-item"><p class="diff-num">${String(i+1).padStart(2,'0')}</p><div><h4>${esc(x[0])}</h4><p>${esc(x[1])}</p></div></div>`).join('');

  const f = document.querySelector(`[data-focus="${k}"]`);
  if(f) f.innerHTML = Object.entries(FOCUS[k]).map(([g,list])=>
    `<div class="focus-block"><h4>${esc(g)} <span class="count">${list.length}</span></h4>
     <div class="tag-cloud">${list.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div></div>`).join('');

  const c = document.querySelector(`[data-career="${k}"]`);
  if(c) c.innerHTML = CAREERS[k].map(x=>`<span class="career-chip">${esc(x)}</span>`).join('');

  const g = document.querySelector(`[data-grow="${k}"]`);
  if(g) g.innerHTML = GROW[k].map(x=>`<li><b>${esc(x[0])}</b>${esc(x[1])}</li>`).join('');
});

/* ---- curriculum panels ---- */
const curriMount = document.getElementById('curriMount');
curriMount.innerHTML = ORDER.map(k=>{
  const C = CURRICULUM[k];
  const blocks = C.blocks.map((b,i)=>{
    const items = b.items.map(t=>`<li>${esc(t)}</li>`).join('');
    return `<div class="acc-item${i===0?' open':''}">
      <button class="acc-head" aria-expanded="${i===0}">
        <span class="left">
          <span class="semnum">${esc(String(i+1).padStart(2,'0'))}</span>
          <span><span class="ttl">${esc(b.label)}${b.tag?`<span class="badge">${esc(b.tag)}</span>`:''}</span>${b.sub?`<span class="acc-sub" style="font-size:12.5px;color:var(--ink-soft);">${esc(b.sub)}</span>`:''}</span>
        </span>
        <span class="right"><span class="count">${b.items.length} ${b.items.length===1?'entry':'entries'}</span><span class="plus"></span></span>
      </button>
      <div class="acc-body"><div class="acc-body-inner"><ul class="course-grid">${items}</ul></div></div>
    </div>`;
  }).join('');
  return `<div class="curri-panel ${k}" data-panel="${k}">
    <div class="curri-note"><b>${esc(C.note[0])}</b>${esc(C.note[1])}</div>
    <div class="accordion">${blocks}</div>
  </div>`;
}).join('');
document.querySelector('.curri-panel[data-panel="p1"]').classList.add('active');

curriMount.addEventListener('click', e=>{
  const btn = e.target.closest('.acc-head');
  if(!btn) return;
  const item = btn.closest('.acc-item');
  const open = item.classList.toggle('open');
  btn.setAttribute('aria-expanded', String(open));
});

/* ============================================================
   3. PROGRAM FILTER — drives hero copy, section visibility, curriculum tab
   ============================================================ */
const curriTabs = [...document.querySelectorAll('.curri-tabs button')];

function setFilter(mode, opts={}){
  document.body.className = 'f-' + mode;
  document.querySelectorAll('.track-slot.open').forEach(s=> s.classList.remove('open'));

  document.querySelectorAll('.hero-copy').forEach(el=>el.classList.remove('active'));
  const hero = document.querySelector('.hero-' + mode);
  if(hero) hero.classList.add('active');

  if(mode !== 'all') setCurriculum(mode);

  if(opts.scrollTo) document.querySelector(opts.scrollTo)?.scrollIntoView({behavior:'smooth', block:'start'});
}

function setCurriculum(key){
  curriTabs.forEach(b=>{
    const on = b.dataset.curri === key;
    b.classList.toggle('active', on);
    b.setAttribute('aria-selected', String(on));
  });
  document.querySelectorAll('.curri-panel').forEach(p=>p.classList.toggle('active', p.dataset.panel === key));
}

curriTabs.forEach(b=> b.addEventListener('click', ()=> setCurriculum(b.dataset.curri)));
document.querySelectorAll('.foot-track').forEach(a=>
  a.addEventListener('click', e=>{ e.preventDefault(); setFilter(a.dataset.set); window.scrollTo({top:0,behavior:'smooth'}); }));

/* ---- hero track cards: arrow / click explores the program ---- */
document.querySelectorAll('.tc-arrow').forEach(btn=>
  btn.addEventListener('click', ()=> setFilter(btn.dataset.jump, {scrollTo:'#overview'})));

document.querySelectorAll('.track-card').forEach(card=>{
  const e = document.createElement('span'); e.className = 'tc-explore'; e.textContent = 'Explore program';
  card.appendChild(e);
  card.addEventListener('click', ev=>{
    if(!document.body.classList.contains('f-all') || ev.target.closest('.tc-arrow')) return;
    card.querySelector('.tc-arrow').click();
  });
});

document.querySelectorAll('.pb-go').forEach(b=> b.addEventListener('click', ()=>{ setFilter(b.dataset.set); window.scrollTo({top:0,behavior:'smooth'}); }));

/* ---- landing picker: panels open one by one on a loop; hover / focus takes over ---- */
(function(){
  const wrap = document.getElementById('track-cards');
  const slots = [...wrap.querySelectorAll('.track-slot')];
  let cur = 0, timer = null;
  const show = n => { cur = n; slots.forEach((sl,i)=> sl.classList.toggle('is-active', i===n)); };
  const stop = () => { clearInterval(timer); timer = null; };
  const start = () => {
    stop();
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    timer = setInterval(()=>{ if(document.body.classList.contains('f-all')) show((cur+1)%slots.length); }, 3200);
  };
  slots.forEach((sl,i)=>{
    sl.addEventListener('mouseenter', ()=>{ stop(); show(i); });
    sl.addEventListener('focusin', ()=>{ stop(); show(i); });
  });
  slots.forEach((sl,i)=> sl.addEventListener('click', ev=>{
    if(window.matchMedia('(max-width:900px)').matches && document.body.classList.contains('f-all') && !sl.classList.contains('is-active')){
      ev.preventDefault(); ev.stopPropagation(); stop(); show(i);
    }
  }, true));
  wrap.addEventListener('mouseleave', start);
  wrap.addEventListener('focusout', e=>{ if(!wrap.contains(e.relatedTarget)) start(); });
  show(0); start();
})();

setFilter('all');

/* ============================================================
   4. RECRUITER CAROUSEL
   ============================================================ */
(function(){
  const marquee = document.querySelector('.recruiter-marquee');
  const track = document.getElementById('placementTrack');
  if(!marquee || !track) return;
  const cards = [...track.querySelectorAll('.logo-item')];
  if(!cards.length) return;

  let i = 0, autoId = null, paused = false;
  const setActive = n => cards.forEach((c,x)=>c.classList.toggle('active', x===n));
  const scrollToCard = n => {
    i = n; const c = cards[i]; if(!c) return;
    marquee.scrollTo({left: c.offsetLeft - (marquee.clientWidth - c.clientWidth)/2, behavior:'smooth'});
    setActive(i);
  };
  const start = () => { clearInterval(autoId); autoId = setInterval(()=>scrollToCard((i+1)%cards.length), 2600); };
  marquee.addEventListener('mouseenter', ()=>{ paused = true; clearInterval(autoId); });
  marquee.addEventListener('mouseleave', ()=>{ if(paused){ paused = false; start(); } });
  marquee.addEventListener('scroll', ()=>requestAnimationFrame(()=>{
    const cx = marquee.getBoundingClientRect().left + marquee.clientWidth/2;
    let best = 0, min = Infinity;
    cards.forEach((c,x)=>{ const r = c.getBoundingClientRect(); const d = Math.abs(r.left + r.width/2 - cx); if(d<min){min=d;best=x;} });
    i = best; setActive(best);
  }), {passive:true});
  cards.forEach((c,x)=> c.addEventListener('click', ()=>{ paused = true; clearInterval(autoId); scrollToCard(x); }));
  scrollToCard(0);
  if(!window.matchMedia('(prefers-reduced-motion: reduce)').matches) start();
})();

/* ============================================================
   5. STICKY MENU
   ============================================================ */
(function(){
  const fab = document.getElementById('menuFab'), grid = document.getElementById('menuGrid');
  const chev = '<svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 6 15 12 9 18"/></svg>';
  const items = [
    {set:'all', cls:'p1', img:'../assets/img/campaigns/bba-ba-1.jpg', t:'BBA All Programs', d:'Home · All three programs'},
    {set:'p1', cls:'p1', img:'../assets/img/campaigns/BBA-Square-v1.jpg', t:'BBA', d:'Foundation · 3 yrs'},
    {set:'p2', cls:'p2', img:'../assets/img/campaigns/BBAGH-Square-v1.jpg', t:'BBA (Hons)', d:'Honours · 4 yrs'},
    {set:'p3', cls:'p3', img:'../assets/img/campaigns/bba-ba-3.jpg', t:'BBA Business Analytics', d:'Analytics · 3 yrs + Hons pathway'}
  ];
  grid.innerHTML = items.map((x,n)=>
    `<button type="button" class="menu-tile ${x.cls}" data-n="${n}"><span class="ic"><img src="${x.img}" alt="" loading="lazy"></span><span class="tx"><b>${x.t}</b><small>${x.d}</small></span><span class="here"><i></i>You are here</span>${chev}</button>`).join('');
  const open = o => {
    document.body.classList.toggle('menu-open', o);
    fab.setAttribute('aria-expanded', String(o));
    if(o){
      const cur = document.body.className.match(/f-(\w+)/);
      grid.querySelectorAll('.menu-tile').forEach(t=>{
        t.classList.toggle('on', !!cur && items[t.dataset.n].set === cur[1]);
      });
    }
  };
  fab.addEventListener('click', ()=>open(true));
  document.getElementById('menuClose').addEventListener('click', ()=>open(false));
  document.getElementById('menuOverlay').addEventListener('click', ()=>open(false));
  document.addEventListener('keydown', e=>{ if(e.key==='Escape') open(false); });
  grid.addEventListener('click', e=>{
    const t = e.target.closest('.menu-tile'); if(!t) return;
    open(false);
    setFilter(items[t.dataset.n].set); window.scrollTo({top:0,behavior:'smooth'});
  });
})();

/* ============================================================
   6. REVEAL / TO TOP
   ============================================================ */
const io = new IntersectionObserver(entries=>{
  entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
},{threshold:.12});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));

(function(){
  const top = document.getElementById('toTop');
  const onScroll = ()=>{ top.classList.toggle('show', window.scrollY > 600); };
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();
  top.addEventListener('click', ()=> window.scrollTo({top:0, behavior:'smooth'}));
})();
