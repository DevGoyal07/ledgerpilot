// LedgerPilot pitch deck — FinTechathon 2026, Topic E.
// Ledger identity: ink-green, warm paper, brass accent.
const pptxgen = require("pptxgenjs");
const path = require("path");

const INK="14241C", PAPER="FBF8F1", PAPER2="F3EEE2", BRASS="B08D3F",
      BRASSD="8A6D2C", TEXT="1E2A24", MUTE="6B7A70", LINE="E2DBCB",
      RED="B23A2E", AMBER="C08A2D", GREEN="3E7A4E", WHITE="FFFFFF", ICE="C9D2CC";

const HEAD="Cambria", BODY="Calibri";
const DIR = __dirname;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";            // 13.3 x 7.5
pres.theme = { headFontFace: HEAD, bodyFontFace: BODY };
pres.author = "LedgerPilot Team";
pres.company = "FinTechathon 2026 International Track";
const W = 13.3, H = 7.5;

// ---- helpers ----
function tb(slide, text, opts){ slide.addText(text, Object.assign({isTextBox:true}, opts)); }
function footer(slide, dark){
  tb(slide, "LedgerPilot · SME Finance Copilot", {x:0.5,y:H-0.42,w:7,h:0.3,
    fontFace:BODY,fontSize:9,color: dark?ICE:MUTE, align:"left"});
  tb(slide, "FinTechathon 2026 · Topic E", {x:W-4.5,y:H-0.42,w:4,h:0.3,
    fontFace:BODY,fontSize:9,color: dark?ICE:MUTE, align:"right"});
}
function chip(slide, text, x, y, fill, tcol){
  slide.addShape(pres.ShapeType.roundRect,{x,y,w:0.14+0.085*text.length,h:0.32,
    rectRadius:0.16, fill:{color:fill}, line:{type:"none"}});
  tb(slide, text, {x:x,y:y,w:0.14+0.085*text.length,h:0.32,align:"center",valign:"middle",
    fontFace:BODY,fontSize:10,bold:true,color:tcol,margin:0});
}
function card(slide, x, y, w, h){
  slide.addShape(pres.ShapeType.roundRect,{x,y,w,h,rectRadius:0.07,
    fill:{color:WHITE}, line:{color:LINE,width:1}, shadow:{type:"outer",blur:7,offset:2,angle:90,color:"BBBBBB",opacity:0.3}});
}

// ============ 1. TITLE ============
let s = pres.addSlide();
s.background = {color:INK};
s.addShape(pres.ShapeType.rect,{x:0,y:0,w:W,h:H,fill:{color:INK}});
tb(s,"LedgerPilot",{x:0.9,y:2.15,w:11,h:1.2,fontFace:HEAD,fontSize:66,bold:true,color:PAPER,charSpacing:1});
// brass "Pilot" accent via a second overlay word
tb(s,[{text:"Ledger",options:{color:PAPER}},{text:"Pilot",options:{color:BRASS}}],
   {x:0.9,y:2.15,w:11,h:1.2,fontFace:HEAD,fontSize:66,bold:true,charSpacing:1});
tb(s,"An AI finance copilot for small-business owners",
   {x:0.92,y:3.5,w:11,h:0.6,fontFace:HEAD,italic:true,fontSize:23,color:ICE});
tb(s,"It watches the cash, flags trouble early, and finds the right financing — and it never acts without your yes.",
   {x:0.92,y:4.2,w:10.5,h:0.6,fontFace:BODY,fontSize:14,color:ICE});
chip(s,"Topic E · SME Finance Copilot",0.92,5.3,BRASS,WHITE);
chip(s,"WeBank FinTechathon 2026 · International Track",4.3,5.3,PAPER2,INK);
tb(s,"\"AI as a Financial Participant\"",{x:0.92,y:6.2,w:9,h:0.4,fontFace:BODY,italic:true,fontSize:12,color:MUTE});
s.addNotes("Open: Meet LedgerPilot — an AI finance copilot for small-business owners, our entry for Topic E. One line to remember: it watches the cash, flags trouble early, finds the right financing — and never acts without your yes. ~30 sec.");

// ============ 2. PROBLEM ============
s = pres.addSlide(); s.background={color:PAPER};
tb(s,"Small businesses fly blind on money",{x:0.6,y:0.5,w:12,h:0.8,fontFace:HEAD,fontSize:34,bold:true,color:INK});
tb(s,"The owner is the CEO, the salesperson, and the accountant — so the finance job gets done last, if at all.",
   {x:0.62,y:1.3,w:11.5,h:0.5,fontFace:BODY,fontSize:14,color:MUTE});
const probs = [
  ["Cash crunches arrive unannounced","Money looks fine until payroll week. By the time the gap is obvious, the options are bad and expensive."],
  ["Financing is a guessing game","Dozens of loan types, opaque terms. Owners pick what a relative suggested, not what fits — and overpay."],
  ["No one is reading the numbers","Margins slip and costs creep with no analyst watching. The trend is only clear once it has already hurt."],
];
let x=0.6;
probs.forEach(([t,d])=>{
  card(s,x,2.1,3.95,3.6);
  slide_icon(s,x+0.32,2.45);
  tb(s,t,{x:x+0.3,y:3.25,w:3.4,h:0.8,fontFace:HEAD,fontSize:16.5,bold:true,color:INK});
  tb(s,d,{x:x+0.3,y:4.05,w:3.4,h:1.5,fontFace:BODY,fontSize:12.5,color:TEXT});
  x+=4.2;
});
tb(s,"63M+ MSMEs in India alone — most without a single finance hire.",
   {x:0.6,y:6.1,w:12,h:0.4,fontFace:BODY,italic:true,fontSize:13,color:BRASSD,bold:true});
footer(s,false);
s.addNotes("The problem. An SME owner wears every hat, so finance comes last. Three consequences: cash crunches that arrive with no warning; financing chosen by guesswork and overpaid for; and nobody actually reading the numbers until a trend has already hurt. This is a huge market — 63M+ MSMEs in India alone, almost none with a finance hire. ~1 min.");
function slide_icon(slide,x,y){ // simple brass circle motif
  slide.addShape(pres.ShapeType.ellipse,{x,y,w:0.62,h:0.62,fill:{color:PAPER2},line:{color:BRASS,width:2}});
  slide.addShape(pres.ShapeType.ellipse,{x:x+0.19,y:y+0.19,w:0.24,h:0.24,fill:{color:BRASS},line:{type:"none"}});
}

// ============ 3. SOLUTION ============
s = pres.addSlide(); s.background={color:PAPER};
tb(s,"One copilot, three jobs",{x:0.6,y:0.5,w:12,h:0.8,fontFace:HEAD,fontSize:34,bold:true,color:INK});
tb(s,"LedgerPilot is an agent, not a chatbot: it decides which tools to run, executes them, and can take action — with a human in the loop.",
   {x:0.62,y:1.3,w:12,h:0.5,fontFace:BODY,fontSize:14,color:MUTE});
const jobs = [
  ["01","Cash-flow management with alerts","Reconstructs monthly cash flow, projects the next 30 days, and speaks up early — shortfall risk, thin buffer, expense spikes, overdue invoices."],
  ["02","Financing-option matching","Matches the business to the right instrument with an explainable fit score, estimated cost, and the reasons behind every pick — and why some are off the table."],
  ["03","Business financial analysis","Computes margin, leverage, trend and cost drivers into one explainable 0–100 health score you can actually act on."],
];
let jy=2.2;
jobs.forEach(([n,t,d])=>{
  card(s,0.6,jy,12.1,1.5);
  tb(s,n,{x:0.9,y:jy+0.2,w:1.1,h:1.1,fontFace:HEAD,fontSize:40,bold:true,color:BRASS,align:"center",valign:"middle"});
  tb(s,t,{x:2.2,y:jy+0.22,w:10,h:0.5,fontFace:HEAD,fontSize:18,bold:true,color:INK});
  tb(s,d,{x:2.2,y:jy+0.72,w:10.2,h:0.7,fontFace:BODY,fontSize:12.5,color:TEXT});
  jy+=1.62;
});
footer(s,false);
s.addNotes("The solution: one copilot, three jobs — cash-flow alerts, financing matching, financial analysis. The key framing for the judges: this is an AGENT, not a chatbot. It decides which tools to run, runs them, and can take action — always with a human in the loop. ~45 sec.");

// ============ 4. PRODUCT (hero screenshot) ============
s = pres.addSlide(); s.background={color:INK};
tb(s,"The product, working today",{x:0.6,y:0.42,w:12,h:0.7,fontFace:HEAD,fontSize:30,bold:true,color:PAPER});
tb(s,"A live snapshot of the business on the left; a copilot you just talk to on the right.",
   {x:0.62,y:1.08,w:12,h:0.4,fontFace:BODY,fontSize:13,color:ICE});
s.addImage({path:path.join(DIR,"ui_hero.png"),x:0.6,y:1.6,w:12.1,h:5.45,
  sizing:{type:"contain",w:12.1,h:5.45}});
footer(s,true);
s.addNotes("This is the working product. Left: a live snapshot of the business — health score, cash, proactive alerts. Right: you just talk to it. Note the header — guarded autonomy, actions need your OK, and the engine indicator. Everything shown here runs today. If doing a live demo, switch to the app now. ~1 min.");

// ============ 5. CAPABILITY — CASH FLOW ============
s = pres.addSlide(); s.background={color:PAPER};
tb(s,"It warns you before the gap, not after",{x:0.6,y:0.5,w:12,h:0.8,fontFace:HEAD,fontSize:30,bold:true,color:INK});
tb(s,"Cash-flow engine · proactive alerting",{x:0.62,y:1.22,w:12,h:0.4,fontFace:HEAD,italic:true,fontSize:15,color:BRASSD});
// left: how it works
tb(s,"How it works",{x:0.6,y:2.0,w:5.5,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:INK});
const cf=[
 "Buckets 6 months of transactions into monthly inflow / outflow and net",
 "Runway = cash ÷ monthly burn; flagged red under 3 months",
 "Expense-spike detection: a category beyond 2σ of its own history",
 "30-day projection with a conservative half-collection on near invoices",
];
tb(s, cf.map((t,i)=>({text:t,options:{bullet:{code:"2022"},breakLine:true,paraSpaceAfter:8}})),
   {x:0.6,y:2.5,w:5.7,h:3,fontFace:BODY,fontSize:13,color:TEXT});
// right: example alert card
card(s,6.7,2.0,6,4.1);
tb(s,"Live example — ThreadCraft Apparel",{x:7.0,y:2.2,w:5.4,h:0.4,fontFace:HEAD,fontSize:14,bold:true,color:INK});
tb(s,"Profitable on paper, but cash-starved by 60–90 day client terms.",{x:7.0,y:2.6,w:5.4,h:0.5,fontFace:BODY,italic:true,fontSize:11.5,color:MUTE});
function alertRow(slide,y,sev,txt){
  const c = sev==="HIGH"?RED:AMBER;
  slide.addShape(pres.ShapeType.roundRect,{x:7.0,y,w:0.12,h:0.78,rectRadius:0.05,fill:{color:c},line:{type:"none"}});
  chip(slide,sev,7.25,y,c,WHITE);
  tb(slide,txt,{x:8.1,y:y-0.02,w:4.35,h:0.82,fontFace:BODY,fontSize:11,color:TEXT,valign:"top"});
}
alertRow(s,3.25,"HIGH","Cash on hand ₹2.4L is under half of average monthly outflow (₹25.2L). Thin buffer against a bad month.");
alertRow(s,4.25,"MED","2 overdue invoices worth ₹9.8L — collecting these is the fastest cash win.");
alertRow(s,5.25,"MED","Raw-materials spend last month ran well above its usual range.");
footer(s,false);
s.addNotes("Capability 1 — cash flow. Left: the mechanics (monthly buckets, runway, 2-sigma spike detection, a conservative 30-day projection). Right: real output for ThreadCraft — profitable on paper but cash-starved by long client terms. The agent speaks up unprompted: thin buffer, overdue invoices, expense spike. ~1 min 15 sec.");

// ============ 6. CAPABILITY — FINANCING ============
s = pres.addSlide(); s.background={color:PAPER};
tb(s,"The right financing, with the reasons",{x:0.6,y:0.5,w:12,h:0.8,fontFace:HEAD,fontSize:30,bold:true,color:INK});
tb(s,"Explainable matcher · 6 product types · eligibility + fit scoring",{x:0.62,y:1.22,w:12,h:0.4,fontFace:HEAD,italic:true,fontSize:15,color:BRASSD});
tb(s,"Ask: \"I need ₹15 lakh to bridge a cash gap.\"  LedgerPilot ranks what actually fits — and shows its work.",
   {x:0.6,y:1.95,w:12,h:0.4,fontFace:BODY,fontSize:13.5,color:TEXT});
const fin=[
 ["Invoice Financing","90","Large open receivables suit it; built for short-term cash-gap bridging.",GREEN],
 ["Govt MSME Scheme","70","GST-registered MSME → eligible for low-cost, collateral-free credit.",AMBER],
 ["Working Capital Loan","65","Positive net cash flow supports fixed EMIs.",AMBER],
];
let fy=2.6;
fin.forEach(([t,score,why,col])=>{
  card(s,0.6,fy,12.1,1.15);
  tb(s,t,{x:0.95,y:fy+0.18,w:3.7,h:0.8,fontFace:HEAD,fontSize:16,bold:true,color:INK,valign:"middle"});
  // fit meter
  s.addShape(pres.ShapeType.roundRect,{x:4.8,y:fy+0.42,w:3.2,h:0.3,rectRadius:0.15,fill:{color:PAPER2},line:{type:"none"}});
  s.addShape(pres.ShapeType.roundRect,{x:4.8,y:fy+0.42,w:3.2*score/100,h:0.3,rectRadius:0.15,fill:{color:col},line:{type:"none"}});
  tb(s,"fit "+score,{x:8.05,y:fy+0.33,w:0.9,h:0.4,fontFace:BODY,fontSize:12,bold:true,color:col,valign:"middle"});
  tb(s,why,{x:9.05,y:fy+0.18,w:3.5,h:0.85,fontFace:BODY,fontSize:11,color:TEXT,valign:"middle"});
  fy+=1.27;
});
tb(s,"Every reply ends: \"explainable suggestions, not a credit offer.\"  Transparency is the compliance feature.",
   {x:0.6,y:6.5,w:12,h:0.4,fontFace:BODY,italic:true,fontSize:12,color:BRASSD,bold:true});
footer(s,false);
s.addNotes("Capability 2 — financing. Ask in plain language; it ranks what actually fits with an explainable score and shows the reasons. Invoice financing tops the list for a receivables-driven cash gap. Crucially, every reply says explainable suggestions, not a credit offer — transparency is the compliance feature, not a disclaimer bolted on. ~1 min.");

// ============ 7. CAPABILITY — HEALTH SCORE ============
s = pres.addSlide(); s.background={color:PAPER};
tb(s,"A health score that shows its math",{x:0.6,y:0.5,w:12,h:0.8,fontFace:HEAD,fontSize:30,bold:true,color:INK});
tb(s,"Financial analysis · explainable 0–100 score",{x:0.62,y:1.22,w:12,h:0.4,fontFace:HEAD,italic:true,fontSize:15,color:BRASSD});
// big score dial (donut via pie chart)
s.addChart(pres.ChartType.doughnut,[{name:"score",labels:["score","rest"],values:[89.5,10.5]}],
  {x:0.8,y:2.1,w:3.6,h:3.6,holeSize:68,showLegend:false,showValue:false,showTitle:false,
   chartColors:[GREEN,"EDE7D8"]});
tb(s,"89.5",{x:0.8,y:3.45,w:3.6,h:0.7,align:"center",fontFace:HEAD,fontSize:40,bold:true,color:INK});
tb(s,"Strong",{x:0.8,y:4.15,w:3.6,h:0.4,align:"center",fontFace:HEAD,fontSize:16,italic:true,color:GREEN});
tb(s,"PixelForge Studios",{x:0.8,y:5.7,w:3.6,h:0.4,align:"center",fontFace:BODY,fontSize:12,color:MUTE});
// components
tb(s,"Four weighted components — each defensible",{x:5.0,y:2.1,w:7.5,h:0.5,fontFace:HEAD,fontSize:16,bold:true,color:INK});
const comps=[["Margin","30%","25% net margin → 100"],["Liquidity","25%","2 months of cash → 100"],
  ["Leverage","25%","debt-free → 100"],["Growth","20%","flat revenue → 50"]];
let cy=2.8;
comps.forEach(([n,w2,d])=>{
  tb(s,n,{x:5.0,y:cy,w:2.2,h:0.4,fontFace:BODY,fontSize:14,bold:true,color:INK});
  chip(s,w2,7.1,cy-0.02,PAPER2,BRASSD);
  tb(s,d,{x:8.2,y:cy,w:4.3,h:0.4,fontFace:BODY,fontSize:12.5,color:TEXT});
  cy+=0.8;
});
tb(s,"The score returns its components and weights — so an owner (or an auditor) sees exactly why.",
   {x:5.0,y:6.1,w:7.5,h:0.5,fontFace:BODY,italic:true,fontSize:12,color:BRASSD,bold:true});
footer(s,false);
s.addNotes("Capability 3 — the health score. One number, but it shows its math: four weighted components — margin, liquidity, leverage, growth — each independently defensible. The tool returns the components and weights, so an owner or an auditor can see exactly why the score is what it is. ~45 sec.");

// ============ 8. ARCHITECTURE ============
s = pres.addSlide(); s.background={color:INK};
tb(s,"How it works under the hood",{x:0.6,y:0.5,w:12,h:0.8,fontFace:HEAD,fontSize:30,bold:true,color:PAPER});
tb(s,"A four-stage agent loop over typed tools, with every step logged.",{x:0.62,y:1.25,w:12,h:0.4,fontFace:BODY,fontSize:13,color:ICE});
// loop boxes
const loop=["Plan","Permission gate","Execute","Narrate"];
let lx=0.8;
loop.forEach((t,i)=>{
  s.addShape(pres.ShapeType.roundRect,{x:lx,y:2.1,w:2.5,h:0.9,rectRadius:0.1,fill:{color:PAPER2},line:{type:"none"}});
  tb(s,t,{x:lx,y:2.1,w:2.5,h:0.9,align:"center",valign:"middle",fontFace:HEAD,fontSize:15,bold:true,color:INK});
  if(i<3) tb(s,"→",{x:lx+2.5,y:2.1,w:0.6,h:0.9,align:"center",valign:"middle",fontFace:BODY,fontSize:24,bold:true,color:BRASS});
  lx+=3.1;
});
// tool row
const tools=[["analyze_cashflow","T0 · read"],["financial_analysis","T0 · read"],["match_financing","T1 · recommend"],["schedule_action","T2 · act"]];
let tx=0.8;
tools.forEach(([t,tier])=>{
  s.addShape(pres.ShapeType.roundRect,{x:tx,y:3.55,w:2.85,h:1.1,rectRadius:0.08,fill:{color:"1C2E25"},line:{color:BRASSD,width:1}});
  tb(s,t,{x:tx+0.1,y:3.72,w:2.65,h:0.5,align:"center",fontFace:BODY,fontSize:12.5,bold:true,color:PAPER});
  tb(s,tier,{x:tx+0.1,y:4.18,w:2.65,h:0.4,align:"center",fontFace:BODY,fontSize:11,color: t==="schedule_action"?AMBER:ICE});
  tx+=3.1;
});
// datastore + dual backend
s.addShape(pres.ShapeType.roundRect,{x:0.8,y:5.05,w:5.9,h:1.3,rectRadius:0.08,fill:{color:"1C2E25"},line:{color:LINE,width:1}});
tb(s,"Read-only datastore",{x:1.0,y:5.2,w:5.5,h:0.4,fontFace:HEAD,fontSize:14,bold:true,color:PAPER});
tb(s,"3 sample SMEs · 6 months of transactions · invoices · financing catalog. One seam to swap in live accounting/bank data.",
   {x:1.0,y:5.6,w:5.5,h:0.7,fontFace:BODY,fontSize:11.5,color:ICE});
s.addShape(pres.ShapeType.roundRect,{x:6.9,y:5.05,w:5.8,h:1.3,rectRadius:0.08,fill:{color:"1C2E25"},line:{color:LINE,width:1}});
tb(s,"Dual LLM backend",{x:7.1,y:5.2,w:5.4,h:0.4,fontFace:HEAD,fontSize:14,bold:true,color:PAPER});
tb(s,"Any OpenAI-compatible API for the live demo; a deterministic offline engine runs the whole loop with no key — reproducible evidence.",
   {x:7.1,y:5.6,w:5.4,h:0.7,fontFace:BODY,fontSize:11.5,color:ICE});
footer(s,true);
s.addNotes("Architecture. A four-stage loop — plan, permission gate, execute, narrate — over four typed tools, each tagged with its permission tier. A read-only datastore (the one seam to swap in live bank/accounting data) and a dual LLM backend: live API for the demo, deterministic offline engine for reproducible evidence. ~1 min.");

// ============ 9. SECURITY ============
s = pres.addSlide(); s.background={color:PAPER};
tb(s,"Security is the design, not a wrapper",{x:0.6,y:0.5,w:12,h:0.8,fontFace:HEAD,fontSize:30,bold:true,color:INK});
tb(s,"30% of the score — and the hardest thing to retrofit",{x:0.62,y:1.22,w:12,h:0.4,fontFace:HEAD,italic:true,fontSize:15,color:BRASSD});
// permission tiers
const tiers=[["T0","Read-only analysis","No side effects. Always allowed.",GREEN],
  ["T1","Recommend / draft","No side effects. Allowed up to the ceiling.",AMBER],
  ["T2","State-changing action","Always needs explicit confirmation — the agent never self-approves.",RED]];
let ty=2.05;
tiers.forEach(([n,t,d,c])=>{
  card(s,0.6,ty,6.0,1.3);
  s.addShape(pres.ShapeType.roundRect,{x:0.85,y:ty+0.3,w:0.75,h:0.7,rectRadius:0.1,fill:{color:c},line:{type:"none"}});
  tb(s,n,{x:0.85,y:ty+0.3,w:0.75,h:0.7,align:"center",valign:"middle",fontFace:HEAD,fontSize:20,bold:true,color:WHITE});
  tb(s,t,{x:1.8,y:ty+0.22,w:4.6,h:0.45,fontFace:HEAD,fontSize:14.5,bold:true,color:INK});
  tb(s,d,{x:1.8,y:ty+0.66,w:4.65,h:0.6,fontFace:BODY,fontSize:11,color:TEXT});
  ty+=1.42;
});
// right column: pillars
const pillars=[["Confirmation-always","Every money-adjacent action stops for a human yes. Proven live in three cases."],
  ["Full audit trail","Every message, plan, tool call, result and denial is logged to JSONL."],
  ["Explainable & non-advice","Reasons on every recommendation; a clear not-a-credit-offer disclaimer."],
  ["No hallucinated numbers","All figures come from deterministic tools, never the model."]];
let py=2.05;
pillars.forEach(([t,d])=>{
  slide_icon(s,6.95,py+0.1);
  tb(s,t,{x:7.75,y:py,w:5,h:0.4,fontFace:HEAD,fontSize:15,bold:true,color:INK});
  tb(s,d,{x:7.75,y:py+0.4,w:4.9,h:0.6,fontFace:BODY,fontSize:11.5,color:TEXT});
  py+=1.1;
});
footer(s,false);
s.addNotes("Security — 30% of the score and the part you cannot retrofit. Three permission tiers; T2 actions ALWAYS need explicit confirmation and the agent never self-approves. Plus a full audit trail, explainable non-advice, and no hallucinated numbers — all figures come from deterministic tools, never the model. ~1 min 15 sec.");

// ============ 10. SCORING ALIGNMENT ============
s = pres.addSlide(); s.background={color:PAPER};
tb(s,"Built straight to the rubric",{x:0.6,y:0.5,w:12,h:0.8,fontFace:HEAD,fontSize:32,bold:true,color:INK});
const rub=[["Task completion","40%","All three capabilities implemented with real financial logic and verified end-to-end.",BRASS],
  ["Security & compliance","30%","3-tier permissions, confirmation-always, full audit log, explainable non-advice.",INK],
  ["Innovation & interaction","30%","Live snapshot panel, proactive alerts, purpose-aware matching, pluggable offline/live engine.",BRASSD]];
let ry=1.7;
rub.forEach(([t,p,d,c])=>{
  card(s,0.6,ry,12.1,1.5);
  tb(s,p,{x:0.9,y:ry+0.25,w:2.0,h:1.0,fontFace:HEAD,fontSize:40,bold:true,color:c,align:"center",valign:"middle"});
  tb(s,t,{x:3.1,y:ry+0.28,w:9.3,h:0.5,fontFace:HEAD,fontSize:19,bold:true,color:INK});
  tb(s,d,{x:3.1,y:ry+0.82,w:9.3,h:0.55,fontFace:BODY,fontSize:13,color:TEXT});
  ry+=1.68;
});
tb(s,"Plus: runs today with no setup, 12 passing tests, and reproducible execution evidence in the repo.",
   {x:0.6,y:6.8,w:12,h:0.4,fontFace:BODY,italic:true,fontSize:12.5,color:BRASSD,bold:true});
footer(s,false);
s.addNotes("We built straight to the rubric: task completion (all three capabilities, verified end-to-end), security and compliance (tiers, confirmation, audit, non-advice), innovation and interaction (live snapshot, proactive alerts, purpose-aware matching, offline/live engine). Plus it runs today with no setup, 12 passing tests, and reproducible evidence. ~45 sec.");

// ============ 11. EVIDENCE / WHAT'S REAL ============
s = pres.addSlide(); s.background={color:PAPER};
tb(s,"What's real, and what's sandbox",{x:0.6,y:0.5,w:12,h:0.8,fontFace:HEAD,fontSize:30,bold:true,color:INK});
tb(s,"We're upfront about the line — judges value that.",{x:0.62,y:1.22,w:12,h:0.4,fontFace:HEAD,italic:true,fontSize:14,color:BRASSD});
card(s,0.6,2.0,6.0,4.2);
tb(s,"Real and working",{x:0.9,y:2.2,w:5.4,h:0.5,fontFace:HEAD,fontSize:17,bold:true,color:GREEN});
const real=["The full agent loop — plan, gate, execute, narrate","All three capabilities with genuine financial logic",
  "The permission system — all three cases proven live","Complete audit log + actions ledger as evidence",
  "12 automated tests, all passing","Web app + offline engine, runnable with no key"];
tb(s, real.map(t=>({text:t,options:{bullet:{code:"2713"},breakLine:true,paraSpaceAfter:7,color:TEXT}})),
   {x:0.9,y:2.75,w:5.4,h:3.3,fontFace:BODY,fontSize:12.5});
card(s,6.7,2.0,6.0,4.2);
tb(s,"Simulated for the sandbox",{x:7.0,y:2.2,w:5.4,h:0.5,fontFace:HEAD,fontSize:17,bold:true,color:AMBER});
const sand=["SME data stands in for live accounting/bank feeds","Financing catalog is representative; APRs are ranges",
  "Actions write to a ledger instead of firing real alerts","No real account, customer, or money is ever touched"];
tb(s, sand.map(t=>({text:t,options:{bullet:{code:"25CB"},breakLine:true,paraSpaceAfter:9,color:TEXT}})),
   {x:7.0,y:2.75,w:5.4,h:3.3,fontFace:BODY,fontSize:12.5});
footer(s,false);
s.addNotes("Integrity slide — judges value honesty about the line. What is real: the whole agent loop, all three capabilities, the permission system proven live, the audit log, 12 tests, the runnable app. What is simulated: the data sources and the financing catalog; actions write to a ledger rather than firing. No real money is ever touched. ~45 sec.");

// ============ 12. ROADMAP + CLOSE ============
s = pres.addSlide(); s.background={color:INK};
tb(s,"Where this goes next",{x:0.6,y:0.55,w:12,h:0.8,fontFace:HEAD,fontSize:30,bold:true,color:PAPER});
const road=[["Connect","Live accounting & bank connectors (Tally, Zoho, account aggregator) replacing the sandbox."],
  ["Quote","Lender-API integration for real, binding financing quotes instead of indicative ranges."],
  ["Guard","Input-policy layer in front of the planner; per-field data scoping for tighter privacy."],
  ["Reach","Multi-currency for cross-border SMEs; background alerts that reach the owner between sessions."]];
let rx=0.8;
road.forEach(([t,d],i)=>{
  s.addShape(pres.ShapeType.roundRect,{x:rx,y:1.8,w:2.85,h:3.0,rectRadius:0.08,fill:{color:"1C2E25"},line:{color:BRASSD,width:1}});
  tb(s,String(i+1),{x:rx+0.25,y:2.0,w:0.8,h:0.7,fontFace:HEAD,fontSize:30,bold:true,color:BRASS});
  tb(s,t,{x:rx+0.25,y:2.75,w:2.4,h:0.45,fontFace:HEAD,fontSize:16,bold:true,color:PAPER});
  tb(s,d,{x:rx+0.25,y:3.25,w:2.45,h:1.4,fontFace:BODY,fontSize:11.5,color:ICE});
  rx+=3.1;
});
tb(s,"LedgerPilot",{x:0.6,y:5.5,w:6,h:0.6,fontFace:HEAD,fontSize:26,bold:true,color:PAPER});
tb(s,"The finance teammate every small business deserves.",{x:0.62,y:6.1,w:9,h:0.5,fontFace:HEAD,italic:true,fontSize:16,color:BRASS});
tb(s,"Thank you — questions welcome.",{x:0.62,y:6.65,w:9,h:0.4,fontFace:BODY,fontSize:13,color:ICE});
footer(s,true);
s.addNotes("Roadmap and close. Next: live connectors, real lender quotes, a stronger input-policy guard, and multi-currency for cross-border SMEs. Close on the line: the finance teammate every small business deserves. Invite questions. ~45 sec.");

// ---- speaker notes ----
pres.getSlide ? null : null;

pres.writeFile({ fileName: path.join(DIR,"LedgerPilot_Deck.pptx") }).then(f=>console.log("WROTE",f));
