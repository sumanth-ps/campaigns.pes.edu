/* ============================================================
   1. CONTENT MODEL — one object per program, all views read from it
   ============================================================ */
const PROGRAMS = {
  p1:{ key:'p1', name:'B.Com (General/Hons)', short:'B.Com (General/Hons)' },
  p2:{ key:'p2', name:'B.Com (Hons) with ACCA', short:'Hons with ACCA' },
  p3:{ key:'p3', name:'B.Com (Hons) with CMA', short:'Hons with CMA' },
  p4:{ key:'p4', name:'B.Com (Hons) with CFA', short:'Hons with CFA' },
  p5:{ key:'p5', name:'B.Com (Hons.) CA', short:'B.Com (Hons.) CA' }
};
const ORDER = ['p1','p2','p3','p4','p5'];

/* ---- differentiators ---- */
const DIFF = {
  p1:[
    ['Integrated learning','B.Com subjects are aligned with CA — Foundation in year 1, Intermediate in years 2 and 3, and Finals in year 4.'],
    ['Expert faculty','Learn from experienced CA professionals, industry leaders and academic experts.'],
    ['Real-world skills','Case studies, internships, financial modelling and corporate simulations included.'],
    ['Career-ready','Graduate not just with a degree, but with an edge that employers demand.'],
    ['PES advantage','Strong industry connections, placement support and a vibrant learning environment.'],
    ['Optional CA training','CA training is available in the afternoon, 2:00 to 4:00 PM, at an extra payment — registration-based after classes begin.']
  ],
  p2:[
    ['ACCA collaboration','The department works directly with ACCA, UK, so the degree is built to the qualification rather than bolted onto it.'],
    ['Nine paper exemptions','All three Knowledge-level papers and all six Skills-level papers are exempted on completing the program.'],
    ['Two exits','A semester-pattern elite program offering two exit points, following the prerequisites of the New Education Policy.'],
    ['Mock ACCA exams','Mock exams and practice questions familiarise students with the format and demands of the professional assessments.'],
    ['Industry tie-ups','Collaborations with ACCA UK, Tally for certification programmes, and the BFSI sector for banking and financial depth.'],
    ['Professional exposure','Industry-standard accounting practice, international accounting standards, internships, guest lectures and networking events.']
  ],
  p3:[
    ['Research papers','Students are encouraged to author research papers that blend academic rigour with industry relevance.'],
    ['Case studies','Real-world business problems analysed to a practical solution, with peer-to-peer learning throughout.'],
    ['Worksheets','Application-based problem solving worked through in class, not only set as homework.'],
    ['CMA exam support','Additional preparation support, pre-examination test series and library access to online study text.'],
    ['Certification','Python, Tableau, JMP, Excel and Power BI, advanced Excel, risk management, commodity markets, EXIM documentation, financial modelling.'],
    ['Mentoring','Two one-on-one mentoring sessions every semester.']
  ],
  p4:[
    ['100% CFA integration','The syllabus is fully aligned to the CFA curriculum across all three levels, not taught as a parallel coaching track.'],
    ['No extra tutoring charge','CFA tuition is included. No additional tutoring fee is levied on top of the program fee.'],
    ['Handholding across all levels','Complete support through Levels 1, 2 and 3, with a pre-examination test series for better results.'],
    ['Experiential learning','Hands-on training in the subjects the industry actually asks for, built around competencies rather than coverage.'],
    ['Professors of practice','Experienced faculty members and practitioners who have worked in the markets they teach.'],
    ['Three internships','A social internship, an audit internship and a final internship spread across the four years.']
  ],
  p5:[
    ['Integrated learning','CA subjects are incorporated directly into the B.Com (Hons) structure, so the degree and the CA syllabus are studied as one.'],
    ['Exclusive CA coaching','Classes run 8:00 AM to 1:00 PM; CA-exclusive coaching follows from 1:45 PM to 5:30 PM on the same campus.'],
    ['Expert faculty','Learn from experienced CA professionals, industry leaders and academic experts.'],
    ['Real-world skills','Case studies, internships, financial modelling and corporate simulations included.'],
    ['Career-ready','Graduate not just with a degree, but with an edge that employers demand.'],
    ['PES advantage','Strong industry connections, placement support and a vibrant learning environment.']
  ]
};

/* ---- subject groups ---- */
const FOCUS = {
  p1:{
    'Knowledge areas':['Accounting Principles','Financial Management','Export & Import Laws','Economic Policies','Trade & Business Environment','Business Skills','Analytical Abilities'],
    'How you learn it':['Interactive Lectures','Case Studies','Guest Lectures & Industry Insights','Workshops & Seminars','Professional Certification Support','Internships & Practical Experience','Technology Integration','Research Projects','Continuous Assessment'],
    'Industry tools':['MS Excel','Tableau','JMP','SPSS','Tally','R','SQL','Python']
  },
  p2:{
    'ACCA modules':['Accountant in Business','Business & Corporate Law','Audit and Assurance','Advanced Business Accounting','Management Accounting','Financial Reporting','Financial Management','Performance Management','UK Taxation','Advanced Performance Management','Strategic Business Reporting','Strategic Business Leadership','Advanced Financial Management'],
    'Commerce core':['Business Communication','Business Economics','Indian Financial System','Cost Accounting','Banking Operations Management','Direct Tax','GST','Foreign Exchange Management','Strategic Management','Business Ethics & Corporate Governance'],
    'Applied & emerging':['Data and Decisions for Managers','Social Media Analytics','Introduction to Fintech','Forensic Accounting & Fraud Detection','Financial Derivatives','Personal & Behavioural Finance']
  },
  p3:{
    'CMA Part 1 — Planning, performance & analytics':['External Financial Reporting Decisions','Cost Management','Internal Controls','Planning, Budgeting & Forecasting','Technology & Analytics','Performance Management'],
    'CMA Part 2 — Strategic financial management':['Financial Statement Analysis','Corporate Finance','Risk Management','Investment Decisions','Decision Analysis','Professional Ethics'],
    'Commerce & tools':['Direct Tax','GST Compliance & Customs','Business Law','Business Economics','Entrepreneurial Finance','Advanced Excel','SQL','Tableau','Power BI']
  },
  p4:{
    'CFA Level 1':['Quantitative Methods','Financial Statement Analysis','Corporate Issuers','Equity Investments','Fixed Income','Derivatives','Alternative Investments','Portfolio Management','Business Economics'],
    'CFA Level 2':['Advanced Quantitative Methods','Advanced Financial Statement Analysis','Applied Economics','Advanced Corporate Issuers','Advanced Equity Investment','Advanced Fixed Income','Advanced Derivatives','Advanced Alternative Investments','Advanced Portfolio Management'],
    'CFA Level 3':['Asset Allocation','Portfolio Construction','Performance Measurement','Derivatives & Risk Management','Private Markets','Private Wealth'],
    'Commerce & tools':['Direct Tax','GST Compliance & Customs','Business Law','Advanced Excel','SQL','Tableau','Power BI']
  },
  p5:{
    'CA Foundation subjects':['Accounting','Business Law','Quantitative Aptitude','Business Economics'],
    'CA Intermediate subjects':['Advanced Accounting','Corporate and Other Laws','Income Tax','Goods and Services Tax','Cost and Management Accounting','Audit and Ethics','Financial Management','Strategic Management'],
    'CA Final subjects':['Financial Reporting','Advanced Financial Management','Advanced Auditing, Assurance & Professional Ethics','Direct Tax Laws & International Taxation','Indirect Tax Laws','Insolvency and Bankruptcy Code','Forensic Accounting'],
    'Industry tools':['MS Excel','Tableau','JMP','SPSS','Tally','R','SQL','Python']
  }
};

/* ---- careers ---- */
const CAREERS = {
  p1:['Chartered Accountant','Company Secretary','Financial Management','Investment Banking','Financial Analyst','Banking','Cost Accounting','Economics','Statistics','Actuarial Science','Foreign Trade','Civil Services'],
  p2:['Auditor','Corporate Reporting Analyst','Tax Consultant','Wealth Manager','Risk & Security Analyst','Market Analyst','Banking & Insurance','Researcher & Policy Maker','International Finance','Accountancy'],
  p3:['Management Accountant','Financial Analyst','Corporate Finance Professional','Tax Consultant','Business Consultant','Financial Planner','Auditor','Entrepreneurial Ventures'],
  p4:['Equity Research Analyst','Investment Banker','Risk Analyst / Manager','Credit Analyst','Private Wealth Manager','Chief Investment Officer','Quantitative Analyst','Investment Consultant','Trader / Forex Trader','Data Scientist'],
  p5:['Chartered Accountant','Tax Auditor','Internal Auditor','Company Secretary','Compliance Officer','Financial Analyst','Investment Banker','Cost Accountant','Financial Advisor','Risk Management Analyst']
};

/* ---- certifications ---- */
const CERTS = {
  p1:['Advanced Excel and Python','Fintech courses','Business simulation for entrepreneurship and capital markets','Crypto and blockchain technologies','Two vocational trainings in three years','Training for banking examinations','Additional training for the CA examination','Actuarial Science, EXIM Documentation and Commodity Market Operations workshops'],
  p2:['ACCA Knowledge level — 3 papers exempted','ACCA Skills level — 6 papers exempted','Tally certification, through the departmental tie-up','BFSI certification in banking, financial services and insurance','Mock ACCA exams and practice question banks','International accounting standards exposure'],
  p3:['Python','Tableau','JMP','Excel and Power BI','Advanced Excel','Risk Management','Commodity Markets','Export & Import Documentation','Financial Modelling','CMA Parts 1 and 2, fully integrated','Pre-examination test series','Library access to online CMA study text'],
  p4:['Advanced Excel','Commodity Markets','Financial Modelling','Export & Import Documentation','Aptitude Skill Development','Actuarial Science','Python','CFA Levels 1, 2 and 3, fully embedded','Pre-examination test series','No additional CFA tutoring charge'],
  p5:['Additional training for the CA examination','Advanced Excel and Python','Fintech courses','Business simulation for entrepreneurship and capital markets','Crypto and blockchain technologies','Two vocational trainings in three years','Training for banking examinations','Actuarial Science, EXIM Documentation and Commodity Market Operations workshops']
};

/* ---- curriculum. A leading * marks a course that belongs to the professional qualification ---- */
const CURRICULUM = {
  p1:{
    note:['B.Com (General / Hons) — semester-wise curriculum','A three-year B.Com or a four-year B.Com (Hons), run at the Ring Road and Electronic City campuses. Students who exit after three years receive a B.Com degree; only those completing all four years are awarded B.Com (Hons). Subject to change.'],
    blocks:[
      {label:'Semester 1', items:['Business Regulatory Framework','Research Methodology and Statistics','Accounting for Business','Indian Financial System','Business Communication','Indian Constitution']},
      {label:'Semester 2', items:['Management Accounting','Financial Management and Modelling','Business Economics','Strategic Management','Data Visualization','Environmental Studies & Life Sciences']},
      {label:'Semester 3', items:['Direct Tax-I','Advanced Accounting-I','Cost Accounting','Goods and Services Tax-I','EIE','Social Internship']},
      {label:'Semester 4', items:['Direct Tax-II','GST Compliance and Customs','Advanced Accounting-II','Corporate and Other Laws','Elective-I','EIE']},
      {label:'Semester 5', items:['Audit and Ethics','Elective-II','Elective-III','Financial Analytics (Hons. Only)','SQL (Hons. Only)','Corporate Internship','Organisational Behaviour (Hons. Only)']},
      {label:'Semester 6', items:['Internship']},
      {label:'Semester 7', tag:'Honours', items:['Elective-IV','Elective-V','Elective-VI','Risk Management','Term Paper','Python']},
      {label:'Semester 8', tag:'Honours', items:['Internship']}
    ]
  },
  p2:{
    note:['B.Com (Hons) — International Accounting & Finance','Core subjects in accounting, finance, economics and business management are augmented with ACCA modules covering financial reporting, taxation, audit and assurance, and strategic business leadership. Courses marked with a plus are ACCA papers.'],
    blocks:[
      {label:'Semester 1', items:['Business Communication','Business Economics','Indian Financial System','*ACCA — Accountant in Business','*ACCA — Business and Corporate Law','Data and Decisions for Managers']},
      {label:'Semester 2', items:['Business Communication','Cost Accounting','Banking Operations Management','Social Media Analytics','*ACCA — Audit and Assurance','*ACCA — Advanced Business Accounting']},
      {label:'Semester 3', items:['Business Communication','Direct Tax I','Start-up and Entrepreneurship Management','*ACCA — Management Accounting','*ACCA — Financial Reporting','*ACCA — Financial Management']},
      {label:'Semester 4', items:['Business Communication','GST','Direct Tax II','*ACCA — Performance Management','*ACCA — UK Taxation','Foreign Exchange Management']},
      {label:'Semester 5', items:['Business Research Methods','GST Compliance and Customs','Strategic Management','Business Ethics & Corporate Governance','*ACCA — Advanced Performance Management','*ACCA — Strategic Business Reporting']},
      {label:'Semester 6', items:['Project / Dissertation']},
      {label:'Semester 7', tag:'Honours', items:['Introduction to Fintech','Forensic Accounting & Fraud Detection','Financial Derivatives','*ACCA — Strategic Business Leadership','*ACCA — Advanced Financial Management','Personal & Behavioural Finance']},
      {label:'Semester 8', tag:'Honours', items:['Internship / Placement / Audit firm']}
    ]
  },
  p3:{
    note:['B.Com (Hons) — Strategic Finance','160 credits across eight semesters, with the CMA syllabus mapped course by course. Courses marked with a plus carry a CMA part and section reference. Two of the eight semesters are corporate internships.'],
    blocks:[
      {label:'Semester 1', items:['*Cost Management — CMA Part 1 D-1,2','*Financial Statement Reporting — CMA Part 1 A-1','*Financial Planning and Control — CMA Part 1 B-2,3','Data Analysis and Interpretation','Advanced Excel','Constitution of India, Cyber Law and Professional Ethics']},
      {label:'Semester 2', items:['Direct Tax','*Performance Management — CMA Part 1 C-1,2','*Corporate Reporting Practices — CMA Part 1 A-2','*Strategic Planning & Control — CMA Part 1 B-1','Entrepreneurial Finance','Environmental Studies and Life Sciences']},
      {label:'Semester 3', items:['*Strategic Cost Management — CMA Part 1 D-3,4,5','*Budgetary Control — CMA Part 1 B-4,5,6','*Governance, Risk & Compliance — CMA Part 1 E-1','Computer Applications in Business','Social Internship']},
      {label:'Semester 4', items:['*Performance Measurements — CMA Part 1 C-3','*Control & Security Measures — CMA Part 1 E-2','*Financial Statement Analysis I — CMA Part 2 A-1,2,3','Business Economics','GST Compliance and Customs','SQL']},
      {label:'Semester 5', items:['*Technology & Analytics — CMA Part 1 F-1,2,3,4','*Financial Statement Analysis II — CMA Part 2 A-4','*Corporate Finance — CMA Part 2 B-1,2','*Business Decision Analysis — CMA Part 2 C-1,2','Business Law','Tableau']},
      {label:'Semester 6', items:['*Professional Ethics — CMA Part 2 F-1,2,3','*Corporate Decision Analysis — CMA Part 2 B-3,4','*Marginal Analysis — CMA Part 2 C-3','Research Methodology','Internship & Project']},
      {label:'Semester 7', tag:'Honours', items:['*Corporate Finance — CMA Part 2 B-5,6','*Risk Management — CMA Part 2 D','*Investment Decisions — CMA Part 2 E-1,2','Power BI']},
      {label:'Semester 8', tag:'Honours', items:['Internship','Project']}
    ]
  },
  p4:{
    note:['B.Com (Hons) with CFA','160 credits across eight semesters. Level 1 is covered in depth, with Levels 2 and 3 taught alongside core finance, data analysis and visualisation. Courses marked with a plus are CFA papers.'],
    blocks:[
      {label:'Semester 1', items:['*Quantitative Methods','*Financial Statement Analysis','*Corporate Issuers','Data Analysis and Interpretation','Advanced Excel','Constitution of India, Cyber Law and Professional Ethics']},
      {label:'Semester 2', items:['Direct Tax','*Equity Investments','*Fixed Income','*Derivatives','Entrepreneurial Finance','Environmental Studies and Life Sciences']},
      {label:'Semester 3', items:['*Alternative Investments','*Portfolio Management','*Business Economics — CFA Level 1','Computer Applications in Business','Social Internship']},
      {label:'Semester 4', items:['*Advanced Quantitative Methods','*Advanced Financial Statement Analysis','*Applied Economics','*Advanced Corporate Issuers','GST Compliance and Customs','SQL']},
      {label:'Semester 5', items:['*Advanced Equity Investment','*Advanced Fixed Income','*Advanced Derivatives','*Advanced Alternative Investments','Business Law','Tableau']},
      {label:'Semester 6', items:['*Advanced Portfolio Management','*Asset Allocation','*Portfolio Construction','Research Methodology','Internship & Project']},
      {label:'Semester 7', tag:'Honours', items:['*Performance Measurement','*Derivatives and Risk Management','*Portfolio Management, Private Markets or Private Wealth','Power BI']},
      {label:'Semester 8', tag:'Honours', items:['Internship','Project']}
    ]
  },
  p5:{
    note:['B.Com (Hons) in Finance and Accounting (CA Embedded)','Eight semesters over four years at the Ring Road campus. Students who exit after three years receive a B.Com degree; only those completing all four years are awarded B.Com (Hons). Courses marked with a plus are CA subjects.'],
    blocks:[
      {label:'Semester 1', items:['*Business Economics','*Business Law','*Accounting-I','*Quantitative Aptitude-I','General Management and Communication Skills','Indian Constitution']},
      {label:'Semester 2', items:['*Accounting-II','*Quantitative Aptitude-II','*Corporate and Other Laws-I','*Income Tax-I','*Financial Management-I','Environmental Studies & Life Sciences']},
      {label:'Semester 3', items:['*Corporate and Other Laws-II','*Income Tax-II','*Goods and Services Tax-I','*Cost and Management Accounting-I','Social Internship','EIE']},
      {label:'Semester 4', items:['*Goods and Services Tax-II','*Advanced Accounting-I','*Cost and Management Accounting-II','*Strategic Management-I','*Financial Management-II','EIE-II']},
      {label:'Semester 5', items:['*Financial Reporting-I','*Advanced Accounting-II','*Audit and Ethics','*Insolvency and Bankruptcy Code','*Advanced Financial Management-I','Corporate Internship']},
      {label:'Semester 6', items:['Internship','*Advanced Auditing, Assurance and Professional Ethics']},
      {label:'Semester 7', tag:'Honours', items:['*Advanced Financial Management-II','*Financial Reporting-II','*Direct Tax Laws & International Taxation','*Forensic Accounting','*Indirect Tax Laws']},
      {label:'Semester 8', tag:'Honours', items:['Internship']}
    ]
  }
};

/* ---- FAQ ---- */
const FAQS = [
  ['Do I need to have studied commerce in Class 12?','No. All five programs accept 50% aggregate in 10+2 or equivalent from any stream and any recognised board. The first-year syllabus is built to bring students from science, arts and vocational backgrounds to the same footing.'],
  ['What is the difference between B.Com and B.Com (Hons)?','B.Com is the three-year exit. B.Com (Hons) is the four-year degree — you leave with a B.Com if you exit after three years, and with Honours only if you complete all four. The ACCA, CMA and CFA programs are four-year Honours degrees from the start.'],
  ['What do the ACCA, CMA and CFA programs add over a plain B.Com?','Each embeds a global professional qualification inside the degree. ACCA exempts nine papers and is delivered with ACCA, UK. CMA integrates both parts of the IMA (USA) qualification and awards a B.Com (Hons) in Strategic Finance. CFA covers all three levels of the CFA curriculum within the four years. The B.Com (General/Hons) stays general, with subjects aligned to CA and optional afternoon CA training, leaving every professional route open.'],
  ['What is B.Com (Hons.) CA?','B.Com (Hons) in Finance and Accounting (CA Embedded) is a four-year Honours degree at the Ring Road campus with CA subjects incorporated into the syllabus. Degree classes run 8:00 AM to 1:00 PM, followed by exclusive CA coaching from 1:45 PM to 5:30 PM. The CA qualification itself is awarded by ICAI, whose examinations students take separately.'],
  ['Is there an extra fee for the ACCA, CMA or CFA coaching?','The professional syllabus is integrated into the degree rather than taught as separate coaching. For the CFA program, PES states that no additional tutoring charges are levied. Confirm the current fee position for each program with the admissions office.'],
  ['How many ACCA papers are exempted?','Nine — all three papers at the Knowledge level and all six at the Skills level. Students need to clear the corresponding subjects while pursuing the B.Com (Hons) with ACCA in order to claim the exemption.'],
  ['How do I apply?','Registration for all five programs runs through admissions.pes.edu. PES lists the PES Entrance Process as the admissions route for these commerce degrees; the admissions office will confirm the current format, dates and any interview stage for the intake you are applying to.'],
  ['Which campus will I study at?','B.Com and B.Com (Hons) run at the Ring Road campus, and B.Com also runs at Electronic City. The ACCA, CMA and CFA programs run at the Ring Road campus only.'],
  ['How much internship experience will I get?','It depends on the program. The CMA program places students in the corporate sector for two internship semesters, in the third and fourth years. The CFA program runs three: a social internship with an NGO in semester three, an audit internship in semester six and a final internship in semester eight. The ACCA program carries an internship, placement or audit-firm term in semester eight.'],
  ['Are scholarships available?','Yes. The Prof. MRD Scholarship refunds 50% of tuition for the top 5% by CGPA, and the Prof. CNR Rao Scholarship refunds 40% for the next 20% by SGPA. The Loyalty Program offers 10–30% fee benefits to PES families, alumni and siblings.'],
  ['Can I change program after I register?','Register first and speak to an advisor. Because all five programs share the same eligibility criteria and entrance route, the program decision is usually made during counselling rather than at the point of registration.']
];

/* ============================================================
   2. RENDER
   ============================================================ */
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function renderContent(){
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

  const ce = document.querySelector(`[data-cert="${k}"]`);
  if(ce) ce.innerHTML = CERTS[k].map(x=>`<li>${esc(x)}</li>`).join('');
});

/* ---- curriculum panels ---- */
const curriMount = document.getElementById('curriMount');
if(curriMount){
curriMount.innerHTML = ORDER.map(k=>{
  const C = CURRICULUM[k];
  const blocks = C.blocks.map((b,i)=>{
    const items = b.items.map(raw=>{
      const pro = raw.startsWith('*');
      const text = pro ? raw.slice(1) : raw;
      return `<li${pro?' class="pro"':''}>${esc(text)}</li>`;
    }).join('');
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
}

/* ---- FAQ ---- */
document.getElementById('faqMount').innerHTML = FAQS.map((f,i)=>
  `<div class="faq-item">
     <button class="faq-head" aria-expanded="false" aria-controls="faq-b-${i}"><span>${esc(f[0])}</span><span class="plus"></span></button>
     <div class="faq-body" id="faq-b-${i}"><div class="faq-body-inner">${esc(f[1])}</div></div>
   </div>`).join('');
document.getElementById('faqMount').addEventListener('click', e=>{
  const btn = e.target.closest('.faq-head');
  if(!btn) return;
  const item = btn.closest('.faq-item');
  const open = item.classList.toggle('open');
  btn.setAttribute('aria-expanded', String(open));
});
}
renderContent();

/* ============================================================
   3. PROGRAM FILTER — drives hero copy, section visibility, curriculum tab
   ============================================================ */
const switchBtns = [...document.querySelectorAll('.switch [data-set]')];
let curriTabs  = [...document.querySelectorAll('.curri-tabs button')];

function setFilter(mode, opts={}){
  document.body.className = 'f-' + mode;

  switchBtns.forEach(b=>{
    const on = b.dataset.set === mode;
    b.classList.toggle('active', on);
    b.setAttribute('aria-selected', String(on));
    // the switch scrolls horizontally on narrow screens — keep the active pill in view
    if(on) b.scrollIntoView({inline:'center', block:'nearest'});
  });

  document.querySelectorAll('.hero-copy').forEach(el=>el.classList.remove('active'));
  const hero = document.querySelector('.hero-' + mode);
  if(hero) hero.classList.add('active');

  if(mode !== 'all') setCurriculum(mode, true);

  if(opts.scrollTo) document.querySelector(opts.scrollTo)?.scrollIntoView({behavior:'smooth', block:'start'});
}

function setCurriculum(key, silent){
  curriTabs.forEach(b=>{
    const on = b.dataset.curri === key;
    b.classList.toggle('active', on);
    b.setAttribute('aria-selected', String(on));
  });
  document.querySelectorAll('.curri-panel').forEach(p=>p.classList.toggle('active', p.dataset.panel === key));
  if(!silent) document.getElementById('curriculum')?.scrollIntoView({behavior:'smooth', block:'start'});
}

/* switch pills are page links now — each program has its own page */
function bindCurriTabs(){
  curriTabs = [...document.querySelectorAll('.curri-tabs button')];
  curriTabs.forEach(b=> b.addEventListener('click', ()=> setCurriculum(b.dataset.curri, true)));
}
bindCurriTabs();
document.querySelectorAll('.foot-track').forEach(a=>
  a.addEventListener('click', e=>{ e.preventDefault(); setFilter(a.dataset.set); window.scrollTo({top:0,behavior:'smooth'}); }));


/* ============================================================
   5. RECRUITER CAROUSEL
   ============================================================ */
function initRecruiters(){
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
}
initRecruiters();

/* ============================================================
   6. REVEAL / TO TOP
   ============================================================ */
const io = new IntersectionObserver(entries=>{
  entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
},{threshold:.12});
document.querySelectorAll('.reveal').forEach(el=>io.observe(el));

(function(){
  const top = document.getElementById('toTop');
  const onScroll = ()=>{
    const y = window.scrollY;
    top.classList.toggle('show', y > 600);
  };
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();
  top.addEventListener('click', ()=> window.scrollTo({top:0, behavior:'smooth'}));
})();
/* ============================================================
   7. MOBILE MENU — floating pill opens a sheet; All Programs (home) + every program listed directly
   ============================================================ */
(function(){
  const sheet = document.getElementById('msheet');
  const btn = document.getElementById('menuBtn');
  if(!sheet || !btn) return;
  function open(){
    sheet.classList.add('open'); sheet.setAttribute('aria-hidden','false');
    btn.setAttribute('aria-expanded','true');
    document.body.classList.add('sheet-open');
  }
  function close(focusBtn=true){
    sheet.classList.remove('open'); sheet.setAttribute('aria-hidden','true');
    btn.setAttribute('aria-expanded','false');
    document.body.classList.remove('sheet-open');
    if(focusBtn) btn.focus({preventScroll:true});
  }
  btn.addEventListener('click', open);
  sheet.querySelectorAll('[data-mclose]').forEach(el => el.addEventListener('click', ()=> close()));
  document.addEventListener('keydown', e=>{ if(e.key === 'Escape' && sheet.classList.contains('open')) close(); });
})();

/* ============================================================
   HERO PROGRAM SLIDER — circular: after program 5 comes program 1 again
   ============================================================ */
(function(){
  const slider = document.getElementById('tcSlider');
  const track = document.getElementById('track-cards');
  if(!slider || !track) return;
  const real = [...track.querySelectorAll('.track-slot')];
  const N = real.length;
  real.forEach((s,x)=>{ const t = s.querySelector('.tc-top'); if(t) t.dataset.n = String(x+1).padStart(2,'0'); });

  // one cloned set before and one after the real set, so both sides are always filled
  const makeClone = s => {
    const c = s.cloneNode(true);
    c.classList.add('is-clone'); c.removeAttribute('id');
    c.querySelectorAll('a,button').forEach(el=> el.setAttribute('tabindex','-1'));
    return c;
  };
  real.slice().reverse().forEach(s=> track.insertBefore(makeClone(s), track.firstChild));
  real.forEach(s=> track.appendChild(makeClone(s)));
  const slides = [...track.querySelectorAll('.track-slot')];   // 3 × N, real set at N … 2N-1

  const dots = [...slider.querySelectorAll('.tc-dots button')];
  const now = document.getElementById('tcNow');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let pos = N, timer = null, raf = 0, settle = 0, lock = null, lockUntil = 0;

  const leftOf = n => slides[n].offsetLeft - (track.clientWidth - slides[n].offsetWidth)/2;
  const mark = n => {
    const k = ((n % N) + N) % N;
    slides.forEach((s,x)=>{ const on = x===n; s.classList.toggle('is-active', on); s.setAttribute('aria-hidden', String(!on)); });
    dots.forEach((d,x)=>{ d.classList.toggle('on', x===k); d.setAttribute('aria-selected', String(x===k)); });
    if(now) now.textContent = String(k+1).padStart(2,'0');
  };
  const jump = n => {               // silent jump between identical slides
    track.classList.add('no-anim');
    pos = n; mark(n);
    track.scrollTo({left: leftOf(n), behavior:'instant'});
    void track.offsetWidth;
    requestAnimationFrame(()=> track.classList.remove('no-anim'));
  };
  const normalize = () => { if(lock !== null) return; if(pos < N) jump(pos + N); else if(pos >= 2*N) jump(pos - N); };
  const go = n => {
    pos = Math.max(0, Math.min(slides.length-1, n));
    lock = pos; lockUntil = Date.now() + 1400;      // ignore in-flight positions until we arrive
    mark(pos);
    track.scrollTo({left: leftOf(pos), behavior: reduce ? 'instant' : 'smooth'});
  };
  const nearest = () => {
    const c = track.scrollLeft + track.clientWidth/2;
    let best = pos, min = Infinity;
    slides.forEach((s,x)=>{ const d = Math.abs(s.offsetLeft + s.offsetWidth/2 - c); if(d<min){min=d;best=x;} });
    return best;
  };
  const start = () => { if(reduce) return; stop(); timer = setInterval(()=>go(pos+1), 4200); };
  const stop = () => { clearInterval(timer); timer = null; };

  track.addEventListener('scroll', ()=>{
    if(track.classList.contains('no-anim')) return;
    clearTimeout(settle);
    if(lock !== null){
      if(Math.abs(track.scrollLeft - leftOf(lock)) < 3 || Date.now() > lockUntil) lock = null;
      else return;
    }
    cancelAnimationFrame(raf);
    raf = requestAnimationFrame(()=>{ const n = nearest(); if(n!==pos){ pos = n; mark(pos); } });
    settle = setTimeout(normalize, 160);
  }, {passive:true});

  slider.querySelectorAll('.tc-navbtn').forEach(b=> b.addEventListener('click', ()=>{ normalize(); go(pos + Number(b.dataset.dir)); start(); }));
  dots.forEach((d,x)=> d.addEventListener('click', ()=>{ normalize(); go(N + x); start(); }));
  slides.forEach((s,x)=> s.addEventListener('click', e=>{ if(x!==pos){ e.preventDefault(); go(x); start(); } }));
  slider.addEventListener('mouseenter', stop);
  slider.addEventListener('mouseleave', start);
  slider.addEventListener('touchstart', stop, {passive:true});
  slider.addEventListener('focusin', stop);
  document.addEventListener('keydown', e=>{
    if(!slider.contains(document.activeElement)) return;
    if(e.key==='ArrowRight'){ normalize(); go(pos+1); } if(e.key==='ArrowLeft'){ normalize(); go(pos-1); }
  });
  window.addEventListener('resize', ()=> jump(pos));
  window.__tcReset = ()=>{ jump(N + (((pos % N) + N) % N)); start(); };
  requestAnimationFrame(()=>{ jump(N); start(); });
})();

/* ============================================================
   8. SINGLE-PAGE ROUTER — every program opens inside this one index file
   ============================================================ */
(function(){
  const ROUTES = {'home':'all','bcom-general-hons':'p1','bcom-hons-acca':'p2','bcom-hons-cma':'p3','bcom-hons-cfa':'p4','bcom-hons-ca':'p5'};
  const TITLES = {
    all:'B.Com Programs — PES University',
    p1:'B.Com (General/Hons) — PES University',
    p2:'B.Com (Hons) with ACCA — PES University',
    p3:'B.Com (Hons) with CMA — PES University',
    p4:'B.Com (Hons) with CFA — PES University',
    p5:'B.Com (Hons.) CA — PES University'
  };
  const root = document.documentElement;
  const homeMain = document.querySelector('main[data-view="home"]');
  let progMain = null, current = homeMain, first = true;

  function mount(view){
    if(view === 'prog' && !progMain){
      progMain = document.getElementById('tpl-prog').content.querySelector('main').cloneNode(true);
      current.replaceWith(progMain); current = progMain;
      renderContent(); bindCurriTabs(); initRecruiters();
      progMain.querySelectorAll('.reveal').forEach(el=>io.observe(el));
      return;
    }
    const want = view === 'home' ? homeMain : progMain;
    if(current !== want){
      current.replaceWith(want); current = want;
      if(view === 'home' && window.__tcReset) requestAnimationFrame(()=> window.__tcReset());
    }
  }

  function closeSheet(){
    const sheet = document.getElementById('msheet'), btn = document.getElementById('menuBtn');
    if(sheet && sheet.classList.contains('open')){
      sheet.classList.remove('open'); sheet.setAttribute('aria-hidden','true');
      if(btn) btn.setAttribute('aria-expanded','false');
    }
  }

  function route(mode){
    if(!TITLES[mode]) mode = 'all';
    const view = mode === 'all' ? 'home' : 'prog';
    closeSheet();
    root.classList.toggle('v-home', view === 'home');
    root.classList.toggle('v-prog', view === 'prog');
    mount(view);

    if(view === 'prog'){
      const track = progMain.querySelector('#track-cards');
      const slot = track.querySelector('.track-slot.' + mode);
      track.prepend(slot);
      track.querySelectorAll('.hero-cta').forEach(el=> el.removeAttribute('id'));
      const cta = slot.querySelector('.hero-cta'); if(cta) cta.id = 'enquire';
      const fr = slot.querySelector('iframe[data-src]');
      if(fr && !fr.getAttribute('src')) fr.setAttribute('src', fr.dataset.src);
    }

    setFilter(mode);
    document.title = TITLES[mode];
    document.querySelectorAll('.mnav .mprog').forEach(a=>{
      const on = mode === 'all' ? a.classList.contains('mhome') : a.classList.contains(mode);
      if(on) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current');
    });

    if(!first) window.scrollTo({top:0, behavior:'instant'});
    root.classList.remove('route-pending');
    first = false;
  }

  /* program links (data-go) switch the view in place — the address stays /bcom-compare/;
     in-page anchors (#faq, #curriculum, #enquire …) scroll without adding a #hash to the URL */
  document.addEventListener('click', e=>{
    if(e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const a = e.target.closest('a[href^="#"]');
    if(!a) return;
    e.preventDefault();
    if(a.dataset.go){ route(a.dataset.go); return; }
    closeSheet();
    const id = decodeURIComponent(a.getAttribute('href').slice(1));
    if(!id || id === 'top'){ window.scrollTo({top:0, behavior:'smooth'}); return; }
    const t = document.getElementById(id);
    if(t) t.scrollIntoView({block:'start'});
  });

  /* first load: old #program links still open the right program, then the #hash is removed */
  const h = decodeURIComponent(location.hash.slice(1));
  route(ROUTES[h] || 'all');
  if(location.hash && (h in ROUTES)) history.replaceState(null, '', location.pathname + location.search);
})();
