#!/usr/bin/env python3
"""Build the portal and searchable catalog; preserve original report URLs and bodies."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import quote
from html import escape, unescape
import json, re, math, subprocess
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
BASE='https://globalbusinessinsight.github.io'
CATEGORIES={'industry':('产业与供应链','理解行业结构、竞争格局与运营方式。'), 'global':('企业出海','从市场选择到渠道、服务与本地运营。'), 'digital':('AI与数字化','把技术放回企业的真实业务流程。'), 'markets':('市场观察','从数据口径出发，观察市场与经济。'), 'archive':('综合资料','保留历史专题，按需查阅。')}
FEATURED={
'industry':['eu-ev-market-2026.html','50909us3pl.html','50906ussteel.html','50911usfurniture.html','etruck.html','zomlion_deep_dive_2025.html','reports/cat_visionlink_deep_dive.html'],
'global':['byd_global_2026.html','reports/sany-south-america/index.html','reports/zoomlion-series/index.html','51104eu.html','51103latin.html','antaglobal.html','51028cacn.html'],
'digital':['aierp.html','ai4og.html','51005aibanking.html','s4pp.html','50919costing.html','51020workflow.html'],
'markets':['usrate.html','useconomic.html','ustreasury.html']}
DESCS={
'50909us3pl.html':'从服务分类、客户结构与竞争格局，理解美国第三方仓储。历史资料含预测，使用数值前请核对原始来源。',
'50909us3plen.html':'An English-language overview of U.S. third-party warehousing, service models and competition. Historical analysis includes forecasts.',
'aierp.html':'围绕能源企业的SAP S/4HANA与AI应用，梳理流程、数据和实施问题。',
'aierpen.html':'Explore the relationship between energy operations, SAP S/4HANA and enterprise AI. An archived research report.',
'etruck.html':'从运输场景、能源补给和运营要素，观察电动重卡产业。',
'51005aibanking.html':'北美银行业务中的AI应用场景、技术路径与相关问题。',
'51104eu.html':'欧洲市场经营与合规主题的历史研究。具体政策应以当地官方最新信息为准。',
'51103latin.html':'南美市场经营主题的历史研究。跨国差异与政策有效日期需分别核验。',
'zomlion_deep_dive_2025.html':'围绕工程机械企业的海外渠道、服务和竞争策略展开比较。',
'50919costing.html':'理解生产成本核算如何支持业务分析与管理判断。',
's4pp.html':'沿着离散制造业务流程，理解SAP生产计划的主要环节。',
'usrate.html':'结合历史背景理解美联储利率决策；数据截止时间与口径以正文为准。'}
PAIRS=[('50909us3pl.html','50909us3plen.html'),('aierp.html','aierpen.html')]
ENGLISH=['50909us3plen.html','aierpen.html','51028cacn.html','xcmg.html','tariff2en.html']
TOPICS=[('warehousing','美国仓储与供应链','从服务模式、产业结构到数字化运营，建立一条可反复查阅的研究路线。','industry',['50909us3pl.html','50906ussteel.html','50911usfurniture.html','50919costing.html']),('global-machinery','工程机械的海外竞争','把海外业务拆成市场、渠道、服务和数字化四个问题。','global',['zomlion_deep_dive_2025.html','reports/sany-south-america/index.html','reports/zoomlion-series/index.html','reports/cat_visionlink_deep_dive.html']),('enterprise-ai','企业AI与数字化','先理解业务问题和数据条件，再比较系统能力与实施方式。','digital',['aierp.html','ai4og.html','51005aibanking.html','s4pp.html'])]
NAV=[('首页','/'),('产业与供应链','/category/industry/'),('企业出海','/category/global/'),('AI与数字化','/category/digital/'),('市场与工具','/markets/'),('English','/en/')]
AD='<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6214772877334340" crossorigin="anonymous"></script>'
# Leave this empty until the site owner supplies the Gmail address used for
# manual subscription requests. The browser form still works as a copyable
# email draft while this is blank.
MANUAL_SUBSCRIBE_EMAIL='paulhu@asu.edu'
def write(path,text):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def url(path):return '/'+quote(path,safe='/')
def canonical(path):return BASE+('/' if path=='index.html' else url(path).removesuffix('index.html') if path.endswith('/index.html') else url(path))
class Extract(HTMLParser):
 def __init__(self):super().__init__();self.title=[];self.in_title=False;self.lang='';self.paragraphs=[];self.p=None;self.ignore=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang','')
  if tag=='title':self.in_title=True
  if tag in ('script','style'):self.ignore+=1
  if tag=='p' and not self.ignore:self.p=[]
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
  if tag in ('script','style'):self.ignore=max(0,self.ignore-1)
  if tag=='p' and self.p is not None:self.paragraphs.append(' '.join(''.join(self.p).split()));self.p=None
 def handle_data(self,t):
  if self.in_title:self.title.append(t)
  if self.p is not None and not self.ignore:self.p.append(t)
def clean_generated(s):
 for name in ['metadata','reader']:
  s=re.sub(r'\s*<!-- GBI '+name+r' start -->.*?<!-- GBI '+name+r' end -->\s*', '\n',s,flags=re.S)
 return s

def classify(path,title):
 for cat,files in FEATURED.items():
  if path in files:return cat
 if path in ['50909us3plen.html']:return 'industry'
 if path=='aierpen.html':return 'digital'
 if re.search(r'出海|海外|全球化|国际化|going global|overseas|global analysis|trade|关税|贸易',title,re.I):return 'global'
 if re.search(r'数字|人工智能|\bAI\b|\bERP\b|SAP|S/4|工作流|协同|本体|软件|ontology|digital|workflow|software',title,re.I):return 'digital'
 if re.search(r'利率|美股|国债|宏观经济|GDP|美联储|货币|金融|债务|economic|treasur|federal reserve',title,re.I):return 'markets'
 if re.search(r'产业|行业|市场|物流|仓储|供应链|钢铁|家具|工程机械|电力|能源|石油|重卡|电池|制造|industry|market|supply|logistics|energy|manufactur',title,re.I):return 'industry'
 return 'archive'

def scan():
 records=[]
 for p in sorted(ROOT.rglob('*.html')):
  rel=p.relative_to(ROOT).as_posix()
  if rel.startswith(('.git/','_site/','assets/','tools/','category/','topics/','en/','about/','privacy/','editorial/','contact/','archive/','markets/')) or rel in ('index.html','404.html') or rel.startswith('mk/'):continue
  s=p.read_text(errors='replace')
  if '<!-- GBI generated -->' in s:continue
  s=clean_generated(s);x=Extract();x.feed(s);title=' '.join(''.join(x.title).split())
  if not title or not re.search(r'</head\s*>',s,re.I):continue
  lang=x.lang or ('zh-CN' if re.search('[\u4e00-\u9fff]',title) else 'en')
  cat=classify(rel,title)
  candidates=[t for t in x.paragraphs if len(t)>45 and not re.search(r'免责声明|Copyright|版权所有',t,re.I)]
  desc=DESCS.get(rel) or (candidates[0][:160] if candidates else title+'。历史资料，数据日期与适用范围请参阅正文。')
  desc=re.sub(r'\s+',' ',desc)
  records.append(dict(path=rel,url=url(rel),title=title,description=desc,language=lang,languageLabel='中文' if lang.startswith('zh') else 'English' if lang.startswith('en') else lang,category=cat,categoryLabel=CATEGORIES[cat][0]))
 return records

def head(title,desc,path,lang='zh-CN',ads=False,alternate=None,og_title=None,og_desc=None):
 alt=''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE+u}">' for l,u in (alternate or []))
 return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="index,follow"><title>{escape(title)} · 全球商业洞察</title><meta name="description" content="{escape(desc,quote=True)}"><link rel="canonical" href="{canonical(path)}">{alt}<meta property="og:title" content="{escape(og_title or title,quote=True)}"><meta property="og:description" content="{escape(og_desc or desc,quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical(path)}"><meta property="og:site_name" content="Global Business Insight"><link rel="icon" href="/assets/gbi/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/gbi/site.css"><script defer src="/assets/gbi/site.js"></script><script defer src="/assets/gbi/subscribe.js"></script>{AD if ads else ''}'''

def shell(title,desc,path,body,active='/',lang='zh-CN',ads=True,og_title=None,og_desc=None):
 english=lang.startswith('en')
 nav_items=[('Home','/'),('Industries','/category/industry/'),('Going global','/category/global/'),('Enterprise AI','/category/digital/'),('Markets & tools','/markets/'),('English','/en/')] if english else NAV
 menu=''.join(f'<a href="{u}"'+(' aria-current="page"' if active==u else '')+f'>{t}</a>' for t,u in nav_items)
 schema=json.dumps({'@context':'https://schema.org','@type':'WebSite' if path=='index.html' else 'CollectionPage','name':title,'url':canonical(path),'inLanguage':lang,'isPartOf':{'@type':'WebSite','name':'Global Business Insight','url':BASE+'/'}},ensure_ascii=False)
 evaluator = ('<section class="wrap brand-evaluator" aria-labelledby="brand-evaluator-title"><div><div class="eyebrow">OBB / BRAND VALUE CHECK</div><h2 id="brand-evaluator-title">输入网址，免费评估您的品牌全球价值。</h2><p>从品牌战略、数字可见度、信任资产、内容影响力与运营五个维度，了解下一步增长机会。</p></div><a class="action" href="https://obbdeep.com/" target="_blank" rel="noopener noreferrer">前往 OBB 免费体检 ↗</a></section>') if not english else ('<section class="wrap brand-evaluator" aria-labelledby="brand-evaluator-title"><div><div class="eyebrow">OBB / BRAND VALUE CHECK</div><h2 id="brand-evaluator-title">Evaluate your brand’s global value for free.</h2><p>Review your brand strategy, digital visibility, trust assets, content impact and operating readiness.</p></div><a class="action" href="https://obbdeep.com/" target="_blank" rel="noopener noreferrer">Open OBB brand check ↗</a></section>')
 footer_links = ('<a href="/about/">About</a><a href="/editorial/">Editorial standards</a><a href="/privacy/">Privacy & advertising</a><a href="/contact/">Contact</a><a href="/subscribe/">Subscribe</a><a href="/tools/">Tools</a><a href="/archive/">All reports</a><a href="https://obbdeep.com/" target="_blank" rel="noopener noreferrer">OBB</a><a href="https://inossem.com/" target="_blank" rel="noopener noreferrer">INOSSEM</a>') if english else ('<a href="/about/">关于我们</a><a href="/editorial/">编辑与来源标准</a><a href="/privacy/">隐私与广告说明</a><a href="/contact/">联系与纠错</a><a href="/subscribe/">订阅更新</a><a href="/tools/">更多工具</a><a href="/archive/">全部资料</a><a href="https://obbdeep.com/" target="_blank" rel="noopener noreferrer">OBB品牌增长</a><a href="https://inossem.com/" target="_blank" rel="noopener noreferrer">INOSSEM</a>')
 return f'''<!doctype html><!-- GBI generated --><html lang="{lang}"><head>{head(title,desc,path,lang,ads,og_title=og_title,og_desc=og_desc)}<script type="application/ld+json">{schema}</script></head><body><a class="skip" href="#content">{'Skip to content' if english else '跳到正文'}</a><div class="topline"><div class="wrap"><span>GLOBAL PERSPECTIVE · PRACTICAL CONTEXT</span><span>{'Selected English research' if english else '中文视角 · 全球商业'}</span></div></div><header class="wrap masthead"><a class="brand" href="/" aria-label="全球商业洞察首页"><span class="brand-mark" aria-hidden="true">GB</span><span><strong>全球商业洞察</strong><small>GLOBAL BUSINESS INSIGHT</small></span></a><div class="tagline">看懂产业变化，理解企业出海。<br>产业 · 市场 · 企业 · 技术</div></header><nav class="primary-nav" aria-label="主导航"><div class="wrap nav-inner">{menu}<a class="nav-search" href="/archive/">{'All reports / 搜索' if english else '报告目录 / 搜索'}</a></div></nav><main id="content" class="wrap">{body}</main>{evaluator}<footer class="site-footer"><div class="wrap"><div class="footer-main"><div><strong>Global Business Insight</strong><p>{'Put business questions in their wider context.' if english else '把商业问题放进更完整的背景。'}</p></div><nav class="footer-links" aria-label="{'Footer' if english else '页脚'}">{footer_links}</nav></div><div class="footer-bottom">{'Archived reports retain their original dates and assumptions. Check primary sources before relying on figures.' if english else '历史报告保留原文。数据日期、估计与预测请以正文和原始出处为准。'} · © Global Business Insight</div></div></footer></body></html>'''

def card(r):return f'<article class="report"><div class="eyebrow">{escape(r["categoryLabel"])} / {escape(r["languageLabel"])}</div><h3><a href="{r["url"]}">{escape(r["title"])}</a></h3><p>{escape(r["description"])}</p><small>历史资料 · 日期与口径见正文</small></article>'
def cards(paths,by):return ''.join(card(by[p]) for p in paths if p in by)
def share_card(r, kind):
 tracked=canonical(r['path'])+'?utm_source=homepage&utm_medium=social&utm_campaign=share_'+kind
 if kind=='industry':
  en='Europe’s EV transition is accelerating—but market share alone does not tell the whole story. Our briefing separates battery-electric growth from the broader powertrain mix, then examines what trade rules, country-level demand and local execution mean for market entry.'
  zh='中文补充：看懂欧盟电动车增长，先分清统计口径，再看贸易规则、国别需求与本地化能力。'
  tags='#EuropeanAuto #MarketEntry #ChinaGoingGlobal'
 elif r['path']=='byd_global_2026.html':
  en='BYD’s overseas growth is moving beyond exports. The next test is whether local manufacturing, product adaptation, R&D and service networks can turn shipment growth into a durable business. This source-led briefing separates company disclosures from what the numbers cannot yet prove.'
  zh='中文补充：比亚迪出海的下一阶段，不只是销量，而是本地制造、产品适配与服务网络能否形成可持续经营。'
  tags='#BYD #ChinaGoingGlobal #GlobalBusiness'
 else:
  en='What happens after a Chinese company wins customers abroad? This source-led briefing looks beyond headline growth at the company’s market-entry choices, local execution and the evidence available in the report.'
  zh='中文补充：从企业披露与案例信息出发，关注出海市场选择、本地执行及仍需核实的经营证据。'
  tags='#ChinaGoingGlobal #GlobalBusiness #MarketEntry'
 copy='\n'.join([en,zh,tracked,tags])
 li='https://www.linkedin.com/sharing/share-offsite/?url='+quote(tracked,safe='')
 fb='https://www.facebook.com/sharer/sharer.php?u='+quote(tracked,safe='')
 return '<article class="share-card"><div class="eyebrow">READY TO SHARE / LINKEDIN · FACEBOOK</div><h3><a href="'+r['url']+'">'+escape(r['title'])+'</a></h3><p class="share-en">'+escape(en)+'</p><p class="share-zh">'+escape(zh)+'</p><div class="share-tags">'+escape(tags)+'</div><div class="share-actions"><button type="button" class="action" data-copy-text="'+escape(copy,quote=True)+'">复制双语文案</button><a class="share-link" target="_blank" rel="noopener noreferrer" href="'+li+'">LinkedIn ↗</a><a class="share-link" target="_blank" rel="noopener noreferrer" href="'+fb+'">Facebook ↗</a></div><span class="copy-status" data-copy-status role="status" aria-live="polite"></span></article>'

def share_section(industry_path,company_path,by):
 industry=by.get(industry_path); company=by.get(company_path)
 if not industry or not company:return ''
 return '<section class="share-section" id="latest"><div class="section-head"><div><div class="eyebrow">GLOBAL BRIEFINGS / SHARE & READ</div><h2>Start with the signal. Share the full story.</h2></div><span>English-first · 中文补充</span></div><div class="share-grid">'+share_card(industry,'industry')+share_card(company,'company')+'</div><p class="share-help">Copy the bilingual post, then paste it into your LinkedIn or Facebook update. Social buttons open the sharing window. / 复制文案后粘贴到社交平台，分享按钮会打开发布窗口。</p></section>'

def intro(label,title,desc):return f'<div class="page-intro"><div class="eyebrow">{label}</div><h1>{title}</h1><p>{desc}</p></div>'
def topic_cards():return ''.join(f'<article class="topic"><span class="number">0{i+1}</span><h3><a href="/topics/{slug}/">{title}</a></h3><p>{desc}</p><a class="text-link" href="/topics/{slug}/">进入研究专题 →</a></article>' for i,(slug,title,desc,cat,paths) in enumerate(TOPICS))

def global_feature_paths(records):
 """Prioritize reports changed in the last 21 days; otherwise rotate evergreen picks daily."""
 by={r['path']:r for r in records}
 pool=[]
 for path in FEATURED['global']+[r['path'] for r in records if r['category']=='global' and r['language'].startswith('zh')]:
  if path in by and path not in pool:pool.append(path)
 if not pool:return []
 now=int(datetime.now(timezone.utc).timestamp());recent=[]
 for path in pool:
  result=subprocess.run(['git','log','-4','--format=%ct%x09%s','--',path],cwd=ROOT,text=True,capture_output=True)
  updated=None
  for line in result.stdout.splitlines():
   try:timestamp,subject=line.split('\t',1);timestamp=int(timestamp)
   except ValueError:continue
   # The initial portal migration changed navigation metadata on archived
   # reports; that maintenance pass is not a newly published research report.
   if subject.startswith('Restore business portal and relocate English learning tool'):continue
   updated=timestamp;break
  if updated is None:continue
  if now-updated<=21*86400:recent.append((updated,path))
 fresh=[p for _,p in sorted(recent,reverse=True)]
 evergreen=[p for p in pool if p not in fresh]
 day=datetime.now(timezone.utc).date().toordinal()
 if fresh:
  fresh_today=fresh[:2]
  rotating=evergreen or fresh[2:] or fresh
  start=day%len(rotating)
  return fresh_today+[rotating[(start+i)%len(rotating)] for i in range(min(2,len(rotating)))]
 start=day%len(pool)
 return [pool[(start+i)%len(pool)] for i in range(min(4,len(pool)))]

def subscribe_panel(compact=False):
 return f'''<section class="subscribe-band{' compact' if compact else ''}" aria-labelledby="subscribe-title"><div><div class="eyebrow">EMAIL / 邮件更新</div><h2 id="subscribe-title">订阅你真正关心的研究板块</h2><p>留下邮箱并选择主题。当前由站长手动发送精选文章，不使用自动营销或广告推送。</p></div><form class="manual-form" data-manual-subscribe data-destination="{escape(MANUAL_SUBSCRIBE_EMAIL,quote=True)}"><label>邮箱地址<input name="email" type="email" autocomplete="email" placeholder="you@example.com" required></label><fieldset><legend>选择板块</legend><label><input type="checkbox" name="topics" value="industry"> 产业与供应链</label><label><input type="checkbox" name="topics" value="global"> 企业出海</label><label><input type="checkbox" name="topics" value="digital"> AI与数字化</label><label><input type="checkbox" name="topics" value="markets"> 市场观察</label><label><input type="checkbox" name="topics" value="english"> English research</label></fieldset><label class="consent"><input type="checkbox" name="consent" required> 我同意接收所选板块的文章更新，可随时回复邮件退订。</label><input class="form-trap" name="website" tabindex="-1" autocomplete="off" aria-hidden="true"><button class="action" type="submit">生成订阅邮件 →</button><p class="form-status" data-subscribe-status role="status" aria-live="polite"></p></form></section>'''

def partner_panel():
 return '''<section class="partner-links" aria-labelledby="partner-title"><div class="eyebrow">CONNECTED RESOURCES / 合作入口</div><h2 id="partner-title">继续使用相关工具</h2><div class="partner-grid"><a class="partner-card" href="https://obbdeep.com/" target="_blank" rel="noopener noreferrer"><strong>OBB</strong><span>全球品牌增长与品牌体检</span><small>obbdeep.com ↗</small></a><a class="partner-card" href="https://inossem.com/" target="_blank" rel="noopener noreferrer"><strong>INOSSEM</strong><span>访问合作网站</span><small>inossem.com ↗</small></a></div></section>'''

def enhance(records):
 pairmap={}
 for cn,en in PAIRS:
  for path in (cn,en):pairmap[path]=[('zh-CN',url(cn)),('en',url(en))]
 for r in records:
  p=ROOT/r['path'];s=clean_generated(p.read_text());english=r['language'].startswith('en')
  metadata=[]
  if not re.search(r'<meta\b[^>]*name=["\']description["\']',s,re.I):metadata.append(f'<meta name="description" content="{escape(r["description"],quote=True)}">')
  metadata.extend([f'<link rel="canonical" href="{canonical(r["path"])}">',f'<meta property="og:title" content="{escape(r["title"],quote=True)}">',f'<meta property="og:description" content="{escape(r["description"],quote=True)}">',f'<meta property="og:url" content="{canonical(r["path"])}">','<link rel="stylesheet" href="/assets/gbi/reader.css">'])
  metadata.extend(f'<link rel="alternate" hreflang="{lang}" href="{BASE+u}">' for lang,u in pairmap.get(r['path'],[]))
  schema={'@context':'https://schema.org','@type':'WebPage','name':r['title'],'url':canonical(r['path']),'inLanguage':r['language'],'isPartOf':{'@type':'WebSite','name':'Global Business Insight','url':BASE+'/'}}
  metadata.append('<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>')
  block='\n<!-- GBI metadata start -->\n'+'\n'.join(metadata)+'\n<!-- GBI metadata end -->\n'
  s=re.sub(r'</head\s*>',lambda m:block+m[0],s,count=1,flags=re.I)
  # Keep one existing AdSense loader; do not add advertising to legacy pages without it.
  seen=False
  def dedup(m):
   nonlocal seen
   if seen:return ''
   seen=True;return m[0]
  s=re.sub(r'<script\b[^>]*src=["\']https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^"\']*["\'][^>]*>\s*</script>',dedup,s,flags=re.I)
  related=[v for v in FEATURED.get(r['category'],[]) if v!=r['path']][:2]
  links=''.join(f'<a href="{url(p)}">{escape(next(x["title"] for x in records if x["path"]==p))}</a>' for p in related if any(x['path']==p for x in records))
  alternate=''.join(f'<a href="{u}">{"English edition" if l=="en" else "中文版"}</a>' for l,u in pairmap.get(r['path'],[]) if u!=r['url'])
  caturl='/category/'+r['category']+'/' if r['category'] in ('industry','global','digital') else '/markets/' if r['category']=='markets' else '/archive/'
  panel=f'''<details id="gbi-reader"><summary>{'GBI · Explore' if english else '全球商业洞察 · 导航'}</summary><div class="gbi-reader-panel"><strong>{'Global Business Insight' if english else '全球商业洞察'}</strong><a href="/">{'Home / 中文首页' if english else '商业首页'}</a><a href="{caturl}">{escape(r['categoryLabel'])}</a><a href="/archive/">{'All reports / Search' if english else '报告目录与搜索'}</a>{alternate}{links}<p>{'Archived report. Check the original dates, sources and forecast assumptions before using figures.' if english else '历史报告：请核对正文的数据日期、原始出处与预测假设。'}</p><a href="/editorial/">{'Editorial standards' if english else '编辑与来源标准'}</a><a href="/privacy/">{'Privacy & advertising' if english else '隐私与广告说明'}</a><a href="/contact/">{'Report a correction' if english else '反馈与纠错'}</a></div></details>'''
  reader='\n<!-- GBI reader start -->\n'+panel+'\n<!-- GBI reader end -->\n'
  if re.search(r'</body\s*>',s,re.I):s=re.sub(r'</body\s*>',lambda m:reader+m[0],s,count=1,flags=re.I)
  elif re.search(r'</html\s*>',s,re.I):s=re.sub(r'</html\s*>',lambda m:reader+m[0],s,count=1,flags=re.I)
  else:s+=reader
  p.write_text(s)

def generate():
 records=scan();by={r['path']:r for r in records}
 write('assets/gbi/catalog.json',json.dumps(sorted(records,key=lambda r:(r['category']=='archive',r['title'])),ensure_ascii=False,separators=(',',':'))+'\n')
 hero='''<section class="hero"><div class="hero-copy"><div class="eyebrow">GLOBAL BUSINESS, IN CONTEXT · WEEKLY INTELLIGENCE</div><h1>Follow the shift.<br>Find your next market.</h1><p class="hero-cn">看懂全球产业变化，找到中国企业出海的下一步。</p><p>Source-led briefings on industries, regional markets and Chinese companies going global. English-first summaries, with Chinese context.</p><div class="hero-actions"><a class="action" href="#latest">Read this week’s briefings ↓</a><a class="action secondary" href="/category/global/">中国企业出海 →</a><a class="action secondary" href="/archive/">Browse research</a></div><div class="hero-signals"><span>INDUSTRY × REGION</span><span>CHINA GOING GLOBAL</span><span>MARKET DATA & TOOLS</span></div></div><aside class="tool-feature"><div class="eyebrow">MARKET & MACRO / RESEARCH TOOL</div><h2>Market Atlas</h2><p>Compare U.S. market and macro indicators on one timeline.</p><div class="tool-tags"><span>Market indices</span><span>Rates & Treasuries</span><span>Jobs & GDP</span></div><p>Choose a period, compare monthly changes, and review source definitions.</p><a class="action" href="/mk/">Open Market Atlas ↗</a><a class="tool-secondary" href="/markets/">浏览市场专题 / More market research →</a></aside></section>'''
 selected=FEATURED['industry'][:2]+FEATURED['global'][:2]+FEATURED['digital'][:2]
 global_paths=global_feature_paths(records)
 global_day=datetime.now(timezone.utc).strftime('%Y-%m-%d')
 company_path=global_paths[0] if global_paths else ''
 featured_industry=FEATURED['industry'][0]
 social=share_section(featured_industry,company_path,by)
 daily_cards=[p for p in global_paths if p!=company_path]
 global_section='<div class="section-head"><div><div class="eyebrow">CHINA GOING GLOBAL / DAILY WATCH</div><h2>中国企业全球化</h2></div><span>今日精选 · '+global_day+' · 每日更新</span></div><div class="collection global-daily">'+cards(daily_cards,by)+'</div><p class="global-daily-note">有新研究时优先呈现；暂无新稿时，每天轮换已有的企业出海与全球市场专题。<a href="/category/global/">查看全部企业出海资料 →</a></p>'
 body=hero+social+global_section+'<div class="section-head"><div><div class="eyebrow">RESEARCH PATHS / START HERE</div><h2>从一个重要问题开始</h2></div><span>先建立框架，再深入一个具体问题</span></div><section class="topics">'+topic_cards()+'</section><div class="section-head"><div><div class="eyebrow">MORE TO EXPLORE / ARCHIVE</div><h2>从资料库继续发现</h2></div><a href="/archive/">全部报告 →</a></div><div class="editorial-grid"><div class="report-list">'+cards(selected,by)+'</div><aside class="reading-note"><div class="eyebrow">READ WITH CONTEXT</div><h3>Research with context.</h3><p>读报告，也读它的边界。历史判断、情景预测和当前事实，需要分别看待。</p><ul><li>先确认数据年份与市场范围</li><li>区分事实、估计和预测</li><li>回到原始出处核对关键数字</li></ul><a class="text-link" href="/editorial/">编辑与来源标准 →</a><h3>Selected in English</h3><p>从仓储、企业技术与全球业务开始，查阅已有英文研究。</p><a class="text-link" href="/en/">Explore English reports →</a></aside></div>'+subscribe_panel()+partner_panel()
 write('index.html',shell('全球产业、企业出海与数字化研究','Source-led briefings on industry shifts, regional markets and Chinese companies expanding globally. 中文补充：产业研究、区域市场分析与中国企业出海案例。','index.html',body,og_title='Global Business Insight | Markets & China Going Global',og_desc='Source-led briefings on industry shifts, regional markets and Chinese companies expanding globally. 中文补充：产业研究、区域市场分析与中国企业出海案例。'))
 for cat in ['industry','global','digital']:
  title,desc=CATEGORIES[cat];items=[r for r in records if r['category']==cat];ordered=FEATURED[cat]+[r['path'] for r in items if r['path'] not in FEATURED[cat]]
  body=intro('RESEARCH / '+cat.upper(),title,desc)+'<div class="plain-links">'+''.join(f'<a class="text-link" href="/topics/{slug}/">{t} →</a>' for slug,t,d,c,ps in TOPICS if c==cat)+'</div><div class="collection">'+cards(ordered,by)+'</div>'
  path=f'category/{cat}/index.html';write(path,shell(title,desc,path,body,active=f'/category/{cat}/'))
 for slug,title,desc,cat,paths in TOPICS:
  if slug=='warehousing':sections='''<h2>先弄清楚：你要研究哪一种仓储？</h2><p>“第三方仓储”可能包含存储、订单履约、退货处理及其他服务。比较市场规模或供应商时，先统一服务范围、货物类型与目标地区，避免把不同口径的数字放在一起。</p><h2>沿着四个问题阅读</h2><ol><li><strong>谁是客户？</strong> 区分制造企业、零售商与电商卖家的需求。</li><li><strong>付费对应什么服务？</strong> 将存储、操作、运输与增值服务分开比较。</li><li><strong>成本受什么影响？</strong> 留意订单结构、库存周转、峰值需求与服务要求。</li><li><strong>技术解决什么问题？</strong> 将系统、自动化与具体业务指标联系起来。</li></ol><h2>如何使用下面的资料</h2><p>先读3PL概览，再结合具体行业报告观察货物与客户的差异，最后阅读成本核算专题。这里的行业报告不是同一统计口径的数据集；不能直接相加或替代最新市场调查。</p>'''
  elif slug=='global-machinery':sections='''<h2>海外竞争不止是产品比较</h2><p>阅读工程机械企业报告时，可以分别记录目标市场、销售渠道、售后服务与配件网络。先确定比较对象和业务范围，再评价策略差异。</p><h2>建立一张有依据的比较表</h2><ol><li><strong>市场：</strong> 比较相同地区与相同报告期间。</li><li><strong>渠道：</strong> 区分直营、代理、合作伙伴和租赁相关业务。</li><li><strong>服务：</strong> 查找维修、配件与本地运营的可核验信息。</li><li><strong>数字化：</strong> 区分已部署的产品能力与未来计划。</li></ol><h2>阅读顺序</h2><p>从竞争策略总览建立框架，再读南美与企业专题。涉及收入、份额、网点数量时，回到公司年度报告、公告和当地公开资料核对；不同会计期间或统计定义不能直接比较。</p>'''
  else:sections='''<h2>先定义业务问题，再讨论AI</h2><p>企业技术研究应从一个可以说明的业务任务开始：谁使用结果、现有流程有什么约束、哪些数据能够获得、如何检验效果。功能演示与可持续运行的业务系统，需要分别评估。</p><h2>用四个维度读案例</h2><ol><li><strong>流程：</strong> 输入、输出、审批和异常处理是什么？</li><li><strong>数据：</strong> 来源、质量、权限和更新频率是否明确？</li><li><strong>验证：</strong> 与什么基线比较，谁确认结果可用？</li><li><strong>运营：</strong> 系统集成、人工复核与维护成本由谁承担？</li></ol><h2>从行业场景回到流程</h2><p>可以先阅读能源或银行应用报告，再查阅ERP和制造流程专题。把方案中的能力说明与实际业务证据分开记录；历史文章中的产品版本与技术判断需要重新确认。</p>'''
  body='<div class="breadcrumb"><a href="/">首页</a> / <a href="/category/'+cat+'/">'+CATEGORIES[cat][0]+'</a> / 专题</div><article class="prose"><div class="eyebrow">RESEARCH GUIDE / 研究路线</div><h1>'+title+'</h1><p>'+desc+'</p>'+sections+'<p class="notice">以下为历史资料入口。涉及具体数字与政策时，请按正文日期和原始来源核验；专题编排不代表所有历史数据已更新。</p></article><div class="section-head"><h2>继续阅读</h2><a href="/category/'+cat+'/">查看栏目 →</a></div><div class="collection">'+cards(paths,by)+'</div>'
  path=f'topics/{slug}/index.html';write(path,shell(title,desc,path,body,active=f'/category/{cat}/'))
 body=intro('MARKET & TOOLS','市场与工具','从可追溯的数据出发，在同一条时间线上理解市场与宏观。')+'<div class="hero" style="padding-top:0"><section class="tool-feature"><div class="eyebrow">INTERACTIVE / 交互数据</div><h2>Market Atlas</h2><p>比较美国主要指数、联邦基金利率、国债收益率、就业与GDP。支持历史区间选择和CSV导出。</p><p>月度观察；当前月份可能为暂值。数据来源、日期和计算方法见工具内说明。</p><a class="action" href="/mk/">打开 Market Atlas →</a></section><aside class="reading-note"><h3>先看口径，再看曲线。</h3><p>市场价格与宏观数据的频率和发布时间不同。历史修订值不等于当时已知的信息，指数价格变化也不等于含分红的总回报。</p><a class="text-link" href="/mk/#method">数据来源与方法 →</a></aside></div><div class="section-head"><h2>背景阅读</h2></div><div class="collection">'+cards(FEATURED['markets'],by)+'</div>'
 write('markets/index.html',shell('市场与工具','美国市场与宏观数据工具，以及利率、国债和经济背景阅读。','markets/index.html',body,active='/markets/'))
 body=intro('SELECTED RESEARCH','Global business, in context.','Explore archived English-language research on supply chains, enterprise technology and international business.')+'<p>These reports retain their original scope and assumptions. Check dates and primary sources before relying on figures or forecasts.</p><div class="collection">'+cards(ENGLISH,by)+'</div><p><a class="text-link" href="/archive/?q=&category=">Browse the full research archive →</a></p>'
 write('en/index.html',shell('Selected English research','English-language reports on U.S. warehousing, enterprise AI and international business.','en/index.html',body,active='/en/',lang='en'))
 body=intro('MORE TOOLS','更多工具','研究之外，保留实用的小工具。')+'<div class="topics"><article class="topic"><div class="eyebrow">学习 / LEARNING</div><h3><a href="/tools/english/">30天英语口语训练</a></h3><p>每日听说练习、测验、错题复习与学习记录。进度保存在当前浏览器，建议定期导出备份。</p><a class="text-link" href="/tools/english/">继续今日练习 →</a></article><article class="topic"><div class="eyebrow">研究 / RESEARCH</div><h3><a href="/mk/">Market Atlas</a></h3><p>查看美国市场与宏观月度历史，比较趋势并导出数据。</p><a class="text-link" href="/mk/">打开数据工具 →</a></article></div>'
 write('tools/index.html',shell('更多工具','英语口语训练与市场研究工具入口。','tools/index.html',body,active='',ads=False))
 archive_records=sorted(records,key=lambda r:(r['category']=='archive',r['title']))
 pages=math.ceil(len(records)/48)
 for n in range(1,pages+1):
  path='archive/index.html' if n==1 else f'archive/page/{n}/index.html'
  options=''.join(f'<option value="{k}">{v[0]}</option>' for k,v in CATEGORIES.items())
  pagination=''.join(f'<a href="'+('/archive/' if i==1 else f'/archive/page/{i}/')+'"'+(' aria-current="page"' if i==n else '')+f'>{i}</a>' for i in range(1,pages+1))
  body=intro('RESEARCH ARCHIVE','报告目录','按主题查阅历史资料，或搜索行业、公司和关键词。')+f'<form class="search-form" data-search-form role="search"><label>搜索报告<input type="search" name="q" placeholder="例如：仓储、工程机械、ERP" autocomplete="off"></label><label>主题<select name="category"><option value="">全部主题</option>{options}</select></label><button class="action" type="submit">搜索</button></form><p class="search-status" data-search-status aria-live="polite">共 {len(records)} 篇资料 · 第 {n} / {pages} 页 · 历史资料不代表最新事实</p><div class="collection" data-search-results>'+''.join(card(r) for r in archive_records[(n-1)*48:n*48])+'</div><button type="button" class="search-more" data-search-more hidden>显示更多结果</button><nav class="pagination" data-pagination aria-label="目录分页">'+pagination+'</nav><noscript><p>当前显示静态目录。可通过分页继续浏览全部资料；关键词筛选需要启用JavaScript。</p></noscript>'
  write(path,shell('报告目录'+('' if n==1 else f' · 第{n}页'),'查找全球商业洞察的产业、出海、数字化与历史专题资料。',path,body,active='/archive/',ads=False))
 info={
 'about':('关于全球商业洞察','关于网站的内容方向与使用方式。','''<p>Global Business Insight（全球商业洞察）围绕产业与供应链、企业出海、AI与数字化整理专题资料，并提供美国市场与宏观数据工具。</p><h2>我们希望解决什么问题</h2><p>帮助中文商业读者理解行业背景、比较企业与市场，并找到继续研究的线索。英文精选提供已有英文报告的独立入口。</p><h2>怎样使用资料库</h2><p>从专题页建立阅读顺序，也可以在报告目录中搜索具体行业或公司。历史报告保留原有地址与内容，可能包含过时信息、估计或预测。请结合原始来源与当前情况使用。</p><p>本站不是实时新闻终端，也不提供个性化投资、法律或税务服务。关于来源、AI辅助与更正方式，请阅读<a href="/editorial/">编辑与来源标准</a>。</p><h2>广告与支持</h2><p>部分页面展示Google AdSense广告，广告收入支持网站维护。广告展示不代表本站对广告产品或观点的认可。</p>'''),
 'editorial':('编辑与来源标准','了解历史资料、来源核验、AI辅助与纠错方式。','''<p>读者应能够区分文章中的可核验事实、作者分析、估计和情景预测。以下是本站整理和维护内容时采用的标准。</p><h2>历史资料的状态</h2><p>本站保留不同时期的报告。增加导航、调整样式或重新编排专题，不代表原文事实已经重新核验，也不会被描述为研究内容更新。资料日期与范围以正文为准；缺少出处的数字应作为待核验信息。</p><h2>来源与数据</h2><ul><li>优先引用统计机构、监管机构、公司公告、年报和原始研究。</li><li>标明观察期间、单位、地区、统计口径和来源链接。</li><li>区分实际值、估计值和预测值，预测应解释假设。</li><li>产品、法律和政策内容需要确认版本、适用地区及有效日期。</li></ul><h2>AI辅助与责任</h2><p>内容整理、研究初稿、翻译和交互页面可能使用AI辅助。AI生成本身不是事实依据；关键结论应回到可核验材料。不将自动生成内容冒充实地调查或具名专家审查。</p><h2>更新与纠错</h2><p>内容发生实质修订时，应说明变更内容。读者发现问题，可通过<a href="/contact/">联系与纠错</a>提供文章地址、具体段落和参考来源。</p>'''),
 'privacy':('隐私与广告说明','网站广告、第三方资源、邮件订阅与浏览器本地存储说明。','''<p>本说明适用于Global Business Insight网站及其工具。更新日期：2026年10月4日。</p><h2>Google广告与第三方服务</h2><p>本站部分页面使用Google AdSense。Google及其他第三方广告供应商可能使用Cookie，根据您之前访问本站或其他网站的情况展示广告；Google的广告Cookie可使其及合作伙伴根据浏览活动投放广告。广告服务也可能使用网络信标、IP地址和设备信息。</p><p>您可以访问<a href="https://myadcenter.google.com/">Google广告设置</a>管理个性化广告，或访问<a href="https://optout.aboutads.info/">第三方广告退出工具</a>了解参与供应商的选择。更多信息见<a href="https://policies.google.com/technologies/partner-sites">Google在合作网站上使用数据的说明</a>。退出个性化广告不一定意味着停止所有广告或第三方请求。</p><h2>页面资源与托管</h2><p>网站由GitHub Pages托管。部分历史报告从字体、图表或其他资源提供方加载内容；这些请求可能向提供方传递IP地址和浏览器信息。相关服务按其自身隐私政策处理数据。参阅<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub隐私声明</a>。</p><h2>工具与本地记录</h2><p>英语训练的学习记录与笔记保存在当前浏览器的本地存储中，不通过该工具上传到本站服务器。录音功能需由您授权麦克风，录音在页面内临时保存，可自行下载。清除浏览器数据可能删除学习记录，请先导出备份。市场工具也可能保存界面偏好。</p><h2>邮件订阅</h2><p>订阅表单当前只在浏览器内生成邮件草稿或可复制的申请内容，不向本站专用服务器上传信息。站长收到邮件后会手动维护订阅名单，并仅用于发送读者选择的文章更新；可随时回复退订。Brevo尚未接入，接入后会更新本说明。</p><h2>搜索与反馈</h2><p>报告目录搜索在浏览器内进行，不将搜索词发送到本站专用搜索服务器。目录加载及访问仍会产生正常网页请求。通过GitHub提交的问题会公开显示，请勿填写密码、付款资料或其他敏感信息。</p><h2>您的选择</h2><p>您可以通过浏览器管理Cookie、本地存储及麦克风权限，通过广告提供方管理广告偏好。适用的广告隐私提示与选择以实际显示的界面为准。如需反馈隐私问题，请使用<a href="/contact/">联系入口</a>。</p>'''),
 'contact':('联系与纠错','提交文章问题、来源补充与网站使用反馈。','''<p>欢迎指出事实错误、失效链接、图表口径问题，或提出值得继续研究的主题。</p><h2>反馈时请提供</h2><ol><li>文章或工具的完整地址。</li><li>具体段落、图表或操作步骤。</li><li>您认为需要更正的内容及可核验来源。</li></ol><p><a class="action" href="https://github.com/GlobalBusinessInsight/globalbusinessinsight.github.io/issues/new">在GitHub提交反馈 ↗</a></p><p>提交需要GitHub账号，反馈默认公开。请勿提交个人敏感信息、账号密码或付款资料。广告展示和付款问题由相应服务提供方处理。</p>'''),
 'subscribe':('订阅更新','按板块接收全球商业洞察的精选文章。','''<p>留下邮箱并选择你想追踪的板块。当前阶段由站长手动发送精选文章；Brevo 接入后，再升级为自动分组和定期邮件。</p>'''+subscribe_panel()+'''<p class="notice">点击提交后，浏览器会生成一封订阅申请邮件。若尚未配置收件地址，请复制生成的内容并使用你的邮件客户端发送；配置完成后会直接打开收件地址。</p>''')}
 for slug,(title,desc,content) in info.items():
  path=f'{slug}/index.html';write(path,shell(title,desc,path,'<article class="prose"><div class="eyebrow">GLOBAL BUSINESS INSIGHT</div><h1>'+title+'</h1>'+content+'</article>',active='',ads=False))
 aliases={'category/index.html':('/archive/','报告目录'),'category/global-focus.html':('/category/global/','企业出海'),'category/digital-enterprise.html':('/category/digital/','AI与数字化'),'category/chinese-report.html':('/category/industry/','产业与供应链'),'category/selected-articles.html':('/archive/','报告目录')}
 for path,(target,title) in aliases.items():
  body=intro('RESEARCH DIRECTORY',title,'栏目已重新整理，原有文章地址继续保留。')+f'<p><a class="action" href="{target}">进入{title} →</a></p><section class="topics" style="margin-top:30px">'+topic_cards()+'</section>'
  write(path,shell(title,'全球商业洞察栏目导航。',path,body,active='',ads=False).replace(f'href="{canonical(path)}"',f'href="{BASE+target}"',1))
 write('404.html',shell('页面未找到','查找报告目录或返回全球商业洞察首页。','404.html',intro('404','这个地址暂时没有内容。','可以搜索报告标题，或从商业首页重新开始。')+'<p><a class="action" href="/archive/">搜索报告</a> <a class="action secondary" href="/">返回首页</a></p>',active='',ads=False).replace('<meta name="description"','<meta name="robots" content="noindex"><meta name="description"',1))
 enhance(records)
 # The root English app uses the same origin, JS and localStorage key after relocation.
 ep=ROOT/'tools/english/index.html';s=clean_generated(ep.read_text());block='\n<!-- GBI metadata start -->\n<link rel="canonical" href="'+BASE+'/tools/english/">\n<!-- GBI metadata end -->\n';s=s.replace('</head>',block+'</head>');ep.write_text(s)
 # Sitemap dates are deliberately omitted rather than inventing content update dates.
 locations=[]
 for p in sorted(ROOT.rglob('*.html')):
  path=p.relative_to(ROOT).as_posix()
  if path.startswith(('.git/','_site/')) or path=='404.html' or path in aliases:continue
  text=p.read_text(errors='replace')
  if not re.search(r'<title[^>]*>\s*[^<\s]',text,re.I):continue
  locations.append(canonical(path))
 write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+escape(u)+'</loc></url>\n' for u in sorted(set(locations)))+'</urlset>\n')
 robots='User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n';write('robots.txt',robots);write('robot.txt','# Legacy filename. Crawlers should use /robots.txt.\n'+robots)
 print(f'Built portal, {len(records)} catalog entries, {pages} archive pages and {len(set(locations))} sitemap URLs.')
if __name__=='__main__':generate()
