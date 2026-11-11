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
'industry':['eu-steel-import-rules-2026.html','us-aircraft-mro-workforce-2026.html','us-semiconductor-market-2026.html','thailand-ev-market-2026.html','eu-sustainable-aviation-fuel-market-2026.html','thailand-medical-devices-market-2026.html','north-america-battery-market-2026.html','latin-america-copper-market-2026.html','west-africa-cocoa-market-2026.html','latin-america-battery-storage-market-2026.html','us-hvac-refrigerant-transition-2026.html','mexico-auto-north-america-2026.html','eu-packaging-ppwr-market-2026.html','eu-data-centre-grid-2026.html','middle-east-solar-storage-market-2026.html','eu-heat-pump-market-2026.html','north-america-transformers-market-2026.html','latin-america-power-resilience-2026.html','asean-power-grid-2026.html','middle-east-aviation-2026.html','eu-solar-grid-flexibility-2026.html','latin-american-manufacturing-fdi-2026.html','north-america-freight-rail-2026.html','middle-east-desalination-2026.html','us-manufacturing-orders-2026.html','us-datacenter-power-2026.html','asean-cooling-market-2026.html','eu-ev-market-2026.html','50909us3pl.html','50906ussteel.html','50911usfurniture.html','etruck.html','zomlion_deep_dive_2025.html','reports/cat_visionlink_deep_dive.html'],
'global':['hangcha-thailand-manufacturing-2026.html','sinovac-global-h1-2026.html','sanhua-global-q3-2026.html','geely-global-q3-2026.html','lenovo-global-q1-2026-2027.html','yofc-global-q3-2026.html','jinko-global-q3-2026.html','tcl-electronics-global-2026.html','xiaomi-global-2026.html','longi-global-2026.html','h3c-global-2026.html','gree-global-2026.html','yutong-global-2026.html','popmart-global-2026.html','catl-globalization-q3-2026.html','midea-global-2026.html','sungrow-global-2026.html','superhi-global-2026.html','xpeng-global-2026.html','transsion-global-2026.html','zte-global-2026.html','alibaba-global-2026.html','huhutech-global-2026.html','catl-global-2026.html','xcmg-global-2026.html','anker-global-2026.html','haier-global-2026.html','byd_global_2026.html','reports/sany-south-america/index.html','reports/zoomlion-series/index.html','51104eu.html','51103latin.html','antaglobal.html','51028cacn.html'],
'digital':['reports/e-invoicing/05-e-invoicing-architecture.html','reports/e-invoicing/04-e-invoice-lifecycle.html','reports/e-invoicing/03-why-e-invoicing-matters.html','reports/e-invoicing/02-from-paper-to-digital-reporting.html','reports/e-invoicing/01-what-is-an-e-invoice.html','aierp.html','ai4og.html','51005aibanking.html','s4pp.html','50919costing.html','51020workflow.html'],
'markets':['import-complexity-processgo-bilingual.html','usrate.html','useconomic.html','ustreasury.html']}
DESCS={
'eu-steel-import-rules-2026.html':'依据欧盟钢铁条例2026/1384、配额分配事实说明与实施条例，解释2026年配额、超额关税、熔炼地证明与CBAM之间的边界。',
'hangcha-thailand-manufacturing-2026.html':'依据杭叉集团2026年半年度报告、公司海外业务披露及泰国工厂公告，分析海外收入、本地制造进度和规划产能的区别。',
'us-aircraft-mro-workforce-2026.html':'依据GAO、BLS、FAA及航空维修行业劳动力资料，分析美国航空维修技师培养、认证、招聘与留任之间的差距。',
'sinovac-global-h1-2026.html':'依据科兴生物向SEC提交的2026年上半年未经审计业绩，分析海外销售增长、产品来源、市场准入与亏损变化。',
'us-semiconductor-market-2026.html':'依据SIA引用WSTS的2026年第三季度全球销售数据及SIA/BCG产能情景，区分美国企业市场份额、本土制造能力和投资公告。',
'sanhua-global-q3-2026.html':'依据三花智控2026年半年报和三季报，梳理海外收入、地区毛利、产品结构、汇兑影响与出海业务的经营表现。',
'thailand-ev-market-2026.html':'依据泰国工业联合会2026年前九个月乘用车注册、产量与出口数据，以及BOI电动车政策，分析纯电需求、本地制造和整车出口之间的差距。',
'geely-global-q3-2026.html':'依据吉利汽车2026年前三季度未经审计业绩、上半年出口公告及十月销量，分析海外扩张、收入利润口径与盈利披露边界。',
'eu-sustainable-aviation-fuel-market-2026.html':'依据EASA 2026年度技术报告，分析欧盟ReFuelEU Aviation首年SAF供应、进口原料、价格差距、2030年目标和合成燃料建设进度。',
'lenovo-global-q1-2026-2027.html':'依据联想集团2026/27财年第一季度业绩，分析AI相关收入、三大业务分部、服务器增长、全球本地供应链，以及法定亏损与调整后利润的差异。',
'thailand-medical-devices-market-2026.html':'依据泰国医疗器械情报单位（MEDIU）数据、泰国FDA规则与BOI资料，分析泰国医疗器械贸易规模、进口结构、本地制造和产品准入。',
'north-america-battery-market-2026.html':'基于美国能源信息署、能源部与加拿大能源监管机构数据，分析电网级储能部署、共址趋势、制造产能及美国与加拿大的市场差异。',
'yofc-global-q3-2026.html':'依据长飞光纤2026年三季报和半年报，分析前三季度业绩增长、海外收入占比、多国生产网络及地区利润披露边界。',
'jinko-global-q3-2026.html':'依据晶科控股2026年第三季度未经审计业绩，分析海外出货、组件毛利修复、储能业务和地区利润披露边界。',
'latin-america-copper-market-2026.html':'结合COCHILCO铜供需预测、智利实际产量与能源水资源数据，以及秘鲁生产指数和矿业项目组合，分析拉美铜供应的短期波动和增量约束。',
'west-africa-cocoa-market-2026.html':'依据加纳、科特迪瓦官方新季收购价、ICCO全球供需修订和欧盟零毁林条例，解释西非可可价格机制、农户收入与出口追溯要求。',
'xiaomi-global-2026.html':'依据小米2026年中期报告，分析中国大陆以外收入、海外手机市场与零售网络，并说明印度事项和披露边界。',
'latin-america-battery-storage-market-2026.html':'依据OLACDE 2026年8月区域储能数据、巴西ANEEL最终招标文件和墨西哥官方接网规定，比较拉美电池储能的规模、收入机制与国别差异。',
'longi-global-2026.html':'依据隆基绿能2026年半年度报告和国家能源局资料，分析海外组件销量、BC产品结构及集团收入、利润和现金流压力。',
'us-hvac-refrigerant-transition-2026.html':'依据美国EPA 2026年修订后的HFC限制表与AHRI 2026年8月出货数据，说明住宅与轻商用空调换冷媒的规则边界、旧库存安装安排和渠道影响。',
'h3c-global-2026.html':'依据紫光股份2026年半年报，分析新华三海外收入增速、市场覆盖、行业项目与本地交付的经营条件。',
'mexico-auto-north-america-2026.html':'依据INEGI 2026年9月轻型汽车统计，比较生产、出口和国内销量的不同变化，并结合USMCA规则说明北美供应链背景。',
'gree-global-2026.html':'依据格力电器2026年半年报，分析海外主营收入下降、自主品牌出口占比及部分区域增长，并说明披露口径的局限。',
'import-complexity-processgo-bilingual.html':'结合全球进口复杂度比较与各国海关规则，分析商品准入、税费、许可、申报及放行后财务流程如何衔接。','eu-packaging-ppwr-market-2026.html':'依据欧盟包装与包装废弃物法规、Eurostat 2024年数据及委员会实施指南，分析包装设计、再生料、标签和各国回收差异。',
'yutong-global-2026.html':'依据宇通客车2025年年报、2026年三季报与产销快报，分析海外收入、地区毛利率、服务网络、本地组装和最新经营节奏。',
'eu-data-centre-grid-2026.html':'依据欧盟委员会和爱尔兰统计局资料，分析数据中心用电预测、电网接入、效率规则与国家差异。',
'middle-east-solar-storage-market-2026.html':'依据沙特、阿联酋政府目标及ACWA Power、Masdar项目公告，区分政策规划、融资关闭与商业运营，分析光伏储能并网、融资与本地交付门槛。',
'catl-globalization-q3-2026.html':'依据宁德时代2026年三季报、半年报及欧洲项目公告，分析海外收入、经营现金流、匈牙利模组装配和西班牙项目的本地化进度与回报风险。',
'eu-heat-pump-market-2026.html':'依据欧盟委员会与欧洲热泵协会资料，分析欧洲热泵销量复苏、国家差异、能源价格、安装服务与供应商进入门槛。',
'midea-global-2026.html':'依据美的集团2025年年报及2026年中期报告，分析海外收入、OBM品牌化、本地研发制造、服务网络及全球经营风险。',
'north-america-transformers-market-2026.html':'依据美国能源部与NERC公开资料，分析配电变压器需求、交付周期、规格碎片化、能效标准与供应商准入；区分美国行业数据与北美区域预测。',
'sungrow-global-2026.html':'依据阳光电源2025年年报与2026年半年报，分析境外收入、地区毛利率、海外服务网络、产品认证及集团业绩变化。',
'latin-america-power-resilience-2026.html':'依据IEA 2026年10月拉美电力系统评估与气候资料，分析厄尔尼诺对水电、备用电源、区域互联和电网投资的影响。',
'superhi-global-2026.html':'依据特海国际2026年中期报告，分析海底捞海外门店、地区收入、翻台率、同店销售及集团利润变化。',
'reports/e-invoicing/01-what-is-an-e-invoice.html':'从数据结构、自动处理和交易链路，解释PDF、扫描件与结构化电子发票的区别。',
'reports/e-invoicing/02-from-paper-to-digital-reporting.html':'沿着纸面凭证、EDI、语义标准、互联网络与税务数字报告，解释电子发票体系如何逐层演进。',
'reports/e-invoicing/03-why-e-invoicing-matters.html':'结合企业调查、欧盟评估和秘鲁研究，分析电子发票的效率、合规、征管与数据价值及其实现条件。',
'reports/e-invoicing/04-e-invoice-lifecycle.html':'从交易证据、开具校验、传输回执、接收审批到入账归档，拆解电子发票端到端流程、状态边界、异常处理与留存证据；监管平台并非所有国家的必经环节。',
'reports/e-invoicing/05-e-invoicing-architecture.html':'解释企业ERP、数据映射、集成服务、税务机关平台、交换网络与买方系统的职责，并比较意大利、巴西和Peppol的不同交换路径。',
'asean-power-grid-2026.html':'依据东盟能源中心第九版《东盟能源展望》、IEA《东盟能源安全评估》及东盟电网互联研究，分析区域电力需求、数据中心、灵活性与投资落地。',
'middle-east-aviation-2026.html':'依据IATA 2026年8月客运统计与迪拜机场上半年运营披露，分析中东航司需求、运力、客座率及枢纽恢复。',
'middle-east-desalination-2026.html':'基于沙特官方项目资料，分析海水淡化采购、私营融资、反渗透能效及水务基础设施投资风险。',
'xpeng-global-2026.html':'依据小鹏汽车2026年中期报告及截至10月15日的欧洲业务公告，分析海外收入、交付增长、奥地利合作生产与盈利验证。',
'transsion-global-2026.html':'依据传音控股在港交所披露的2023至2025年审计财务资料及2026年前四个月数据，分析多品牌布局、区域收入、售后网络与现金流。',
'eu-solar-grid-flexibility-2026.html':'依据SolarPower Europe、Eurostat和欧盟电力市场法规，分析欧盟太阳能装机、发电结构、并网灵活性与项目收益兑现。',
'north-america-freight-rail-2026.html':'基于AAR、USDOT与STB公开资料，分析北美铁路联运、跨境货运结构、关键通道和服务约束。',
'zte-global-2026.html':'依据中兴通讯2025年年报及2026年半年报披露，分析国际收入、区域布局、网络与算力业务、本地执行及盈利兑现风险。',
'latin-american-manufacturing-fdi-2026.html':'依据ECLAC 2026年报告，拆解拉美和加勒比FDI总量、制造业与服务业分化、资金来源和投资项目公告变化。',
'alibaba-global-2026.html':'依据阿里巴巴FY2026年报及2026年6月季度SEC披露，分析国际零售增长、分部亏损收窄、AliExpress盈利信号与报告口径变化。',
'huhutech-global-2026.html':'依据HUHUTECH向SEC提交的未经审计2026年中期资料，分析新市场收入、项目结构、利润与现金回收。',
'middle-east-desalination-2026.html':'基于沙特官方项目资料，分析海水淡化采购、私营融资、反渗透能效及水务基础设施投资风险。',
'us-manufacturing-orders-2026.html':'基于美国人口普查局与美联储2026年8月数据，拆解工厂订单、资本设备、制造业产出和产能利用率。',
'us-datacenter-power-2026.html':'基于LBNL、EIA、FERC与美国能源部资料，拆解美国数据中心用电情景、电网接入和商业机会。',
'catl-global-2026.html':'依据宁德时代2026年半年度报告及德布勒森公告，分析海外收入、欧洲本地化生产和量产兑现风险。',
'xcmg-global-2026.html':'依据徐工机械2026年半年度报告，分析境外收入占比、本地服务网络、汇兑影响与利润转换。',
'anker-global-2026.html':'依据安克创新2026年半年度报告，分析海外收入、区域与渠道结构、研发投入及现金流风险。',
'asean-cooling-market-2026.html':'基于IEA与东盟能源中心资料，分析东南亚空调需求、能效要求、国家差异与本地化经营。',
'haier-global-2026.html':'依据海尔智家2026年中期业绩披露，梳理区域经营表现、产品本地化与全球供应链策略。',
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
 def __init__(self):
  super().__init__();self.title=[];self.in_title=False;self.lang='';self.paragraphs=[];self.p=None;self.ignore=0;self.text=[];self.headings=[];self.heading=None;self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html':self.lang=a.get('lang','')
  if tag=='title':self.in_title=True
  if tag in ('script','style'):self.ignore+=1
  if tag in ('h1','h2','h3') and not self.ignore:self.heading=[]
  if tag=='a' and not self.ignore and a.get('href'):self.links.append(a['href'])
  if tag=='p' and not self.ignore:self.p=[]
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
  if tag in ('script','style'):self.ignore=max(0,self.ignore-1)
  if tag in ('h1','h2','h3') and self.heading is not None:
   self.headings.append(' '.join(''.join(self.heading).split()));self.heading=None
  if tag=='p' and self.p is not None:self.paragraphs.append(' '.join(''.join(self.p).split()));self.p=None
 def handle_data(self,t):
  if self.in_title:self.title.append(t)
  if not self.ignore:
   self.text.append(t)
   if self.heading is not None:self.heading.append(t)
   if self.p is not None:self.p.append(t)
def clean_generated(s):
 for name in ['metadata','reader']:
  s=re.sub(r'\s*<!-- GBI '+name+r' start -->.*?<!-- GBI '+name+r' end -->\s*', '\n',s,flags=re.S)
 return s

def quality_score(source,parsed):
 text=' '.join(''.join(parsed.text).split())
 plain=re.sub(r'\s+',' ',text)
 chars=len(re.sub(r'\s','',plain))
 h2=sum(1 for h in parsed.headings if h)
 paragraphs=[p for p in parsed.paragraphs if len(p)>45]
 external=[]
 for href in parsed.links:
  if href.startswith('https://') and not any(x in href.lower() for x in ('globalbusinessinsight.github.io','facebook.com','linkedin.com','twitter.com','x.com','googlesyndication','google.com','w3.org','schema.org','fonts.')):
   external.append(href)
 score=0
 # Completeness and substance (30 points)
 if re.search(r'<h1\b',source,re.I):score+=5
 score+=15 if chars>=1800 else 10 if chars>=1000 else 5 if chars>=500 else 0
 score+=10 if len(paragraphs)>=7 else 7 if len(paragraphs)>=4 else 3 if len(paragraphs)>=2 else 0
 # Argument and structure (25 points)
 score+=15 if h2>=4 else 10 if h2>=2 else 4 if h2>=1 else 0
 score+=5 if re.search(r'摘要|核心判断|结论|总结|summary|conclusion|key takeaways|executive summary',plain,re.I) else 0
 score+=5 if re.search(r'风险|局限|限制|不确定|风险提示|limitations?|risks?|caveat',plain,re.I) else 0
 # Evidence and auditability (30 points)
 score+=15 if len(set(external))>=4 else 11 if len(set(external))>=2 else 6 if external else 0
 score+=7 if re.search(r'来源|参考资料|数据来源|sources|references|methodology|资料口径',plain,re.I) else 0
 score+=4 if re.search(r'20\d{2}年|20\d{2}\s*年|as of 20\d{2}|20\d{2}年\d{1,2}月',plain,re.I) else 0
 score+=4 if re.search(r'\d[\d,.]*\s*(%|％|亿美元|亿元|万|亿|GW|MW|吨|台|辆|家|人|billion|million|\$|€|£)',plain,re.I) else 0
 # Editorial clarity (15 points), with a penalty for generic filler.
 score+=5 if re.search(r'关键在于|这意味着|核心问题|决定.*是否|the question is|the test is|what matters',plain,re.I) else 0
 score+=5 if re.search(r'结论|建议|因此|优先|进入门槛|盈利兑现|our view|the implication|we conclude',plain,re.I) else 0
 score+=5 if re.search(r'而非|不等于|不能.*混为|相比|相较|条件是|取决于|rather than|not the same as|depends on',plain,re.I) else 0
 filler=len(re.findall(r'值得注意的是|总的来说|综上所述|在当今快速变化的|随着全球化不断深入|it is worth noting|in today.s rapidly changing|in conclusion',plain,re.I))
 score=max(0,min(100,score-min(12,filler*3)))
 return score

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
  if rel.startswith(('.git/','_site/','assets/','tools/','category/','topics/','en/','about/','privacy/','editorial/','contact/','archive/','markets/')) or rel in ('index.html','404.html','reports/e-invoicing/index.html') or rel.startswith('mk/'):continue
  s=p.read_text(errors='replace')
  if '<!-- GBI generated -->' in s:continue
  s=clean_generated(s);x=Extract();x.feed(s);title=' '.join(''.join(x.title).split())
  if not title or not re.search(r'</head\s*>',s,re.I):continue
  lang=x.lang or ('zh-CN' if re.search('[\u4e00-\u9fff]',title) else 'en')
  qualityScore=quality_score(s,x)
  cat='archive' if qualityScore<70 else classify(rel,title)
  candidates=[t for t in x.paragraphs if len(t)>45 and not re.search(r'免责声明|Copyright|版权所有',t,re.I)]
  desc=DESCS.get(rel) or (candidates[0][:160] if candidates else title+'。历史资料，数据日期与适用范围请参阅正文。')
  desc=re.sub(r'\s+',' ',desc)
  archived=qualityScore<70 or cat=='archive'
  records.append(dict(path=rel,url=url(rel),title=title,description=desc,language=lang,languageLabel='中文' if lang.startswith('zh') else 'English' if lang.startswith('en') else lang,category=cat,categoryLabel=CATEGORIES[cat][0],qualityScore=qualityScore,editorialStatus='archive' if archived else 'active'))
 return records

def head(title,desc,path,lang='zh-CN',ads=False,alternate=None,og_title=None,og_desc=None):
 alt=''.join(f'<link rel="alternate" hreflang="{l}" href="{BASE+u}">' for l,u in (alternate or []))
 home_style='<link rel="stylesheet" href="/assets/gbi/home.css">' if path=='index.html' else ''
 return f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="index,follow"><title>{escape(title)}</title><meta name="description" content="{escape(desc,quote=True)}"><link rel="canonical" href="{canonical(path)}">{alt}<meta property="og:title" content="{escape(og_title or title,quote=True)}"><meta property="og:description" content="{escape(og_desc or desc,quote=True)}"><meta property="og:type" content="website"><meta property="og:url" content="{canonical(path)}"><meta property="og:site_name" content="Global Business Insight"><link rel="icon" href="/assets/gbi/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/gbi/site.css">{home_style}<script defer src="/assets/gbi/site.js"></script><script defer src="/assets/gbi/subscribe.js"></script><script defer src="/assets/gbi/analytics-consent.js"></script>{AD if ads else ''}'''

def shell(title,desc,path,body,active='/',lang='zh-CN',ads=True,og_title=None,og_desc=None):
 english=lang.startswith('en')
 nav_items=[('Home','/'),('Industries','/category/industry/'),('Going global','/category/global/'),('Enterprise AI','/category/digital/'),('Markets & tools','/markets/'),('English','/en/')] if english else NAV
 menu=''.join(f'<a href="{u}"'+(' aria-current="page"' if active==u else '')+f'>{t}</a>' for t,u in nav_items)
 schema=json.dumps({'@context':'https://schema.org','@type':'WebSite' if path=='index.html' else 'CollectionPage','name':title,'url':canonical(path),'inLanguage':lang,'isPartOf':{'@type':'WebSite','name':'Global Business Insight','url':BASE+'/'}},ensure_ascii=False)
 evaluator = ('<section class="wrap brand-evaluator" aria-labelledby="brand-evaluator-title"><div><div class="eyebrow">OBB / BRAND VALUE CHECK</div><h2 id="brand-evaluator-title">输入网址，免费评估您的品牌全球价值。</h2><p>从品牌战略、数字可见度、信任资产、内容影响力与运营五个维度，了解下一步增长机会。</p></div><a class="action" href="https://obbdeep.com/" target="_blank" rel="noopener noreferrer">前往 OBB 免费体检 ↗</a></section>') if not english else ('<section class="wrap brand-evaluator" aria-labelledby="brand-evaluator-title"><div><div class="eyebrow">OBB / BRAND VALUE CHECK</div><h2 id="brand-evaluator-title">Evaluate your brand’s global value for free.</h2><p>Review your brand strategy, digital visibility, trust assets, content impact and operating readiness.</p></div><a class="action" href="https://obbdeep.com/" target="_blank" rel="noopener noreferrer">Open OBB brand check ↗</a></section>')
 footer_links = ('<a href="/about/">About</a><a href="/editorial/">Editorial standards</a><a href="/privacy/">Privacy & advertising</a><a href="/contact/">Contact</a><a href="/subscribe/">Subscribe</a><a href="/tools/">Tools</a><a href="/archive/">All reports</a><a href="https://obbdeep.com/" target="_blank" rel="noopener noreferrer">OBB</a><a href="https://inossem.com/" target="_blank" rel="noopener noreferrer">INOSSEM</a>') if english else ('<a href="/about/">关于我们</a><a href="/editorial/">编辑与来源标准</a><a href="/privacy/">隐私与广告说明</a><a href="/contact/">联系与纠错</a><a href="/subscribe/">订阅更新</a><a href="/tools/">更多工具</a><a href="/archive/">全部资料</a><a href="https://obbdeep.com/" target="_blank" rel="noopener noreferrer">OBB品牌增长</a><a href="https://inossem.com/" target="_blank" rel="noopener noreferrer">INOSSEM</a>')
 return f'''<!doctype html><!-- GBI generated --><html lang="{lang}"><head>{head(title,desc,path,lang,ads,og_title=og_title,og_desc=og_desc)}<script type="application/ld+json">{schema}</script></head><body><a class="skip" href="#content">{'Skip to content' if english else '跳到正文'}</a><div class="topline"><div class="wrap"><span>GLOBAL PERSPECTIVE · PRACTICAL CONTEXT</span><span>{'Independent research · English-first' if english else '中文视角 · 全球商业'}</span></div></div><header class="wrap masthead"><a class="brand" href="/" aria-label="{'Global Business Insight home' if english else '全球商业洞察首页'}"><span class="brand-mark" aria-hidden="true">GB</span><span><strong>{'Global Business Insight' if english else '全球商业洞察'}</strong><small>{'MARKETS · INDUSTRY · GLOBAL BUSINESS' if english else 'GLOBAL BUSINESS INSIGHT'}</small></span></a><div class="tagline">{'Clear research on markets, industry and business across borders.' if english else '看懂产业变化，理解企业出海。<br>产业 · 市场 · 企业 · 技术'}</div></header><nav class="primary-nav" aria-label="{'Main navigation' if english else '主导航'}"><div class="wrap nav-inner">{menu}<a class="nav-search" href="/archive/">{'Search research' if english else '报告目录 / 搜索'}</a></div></nav><main id="content" class="wrap">{body}</main>{evaluator}<footer class="site-footer"><div class="wrap"><div class="footer-main"><div><strong>Global Business Insight</strong><p>{'Put business questions in their wider context.' if english else '把商业问题放进更完整的背景。'}</p></div><nav class="footer-links" aria-label="{'Footer' if english else '页脚'}">{footer_links}</nav></div><div class="footer-bottom">{'Archive pages are reference material, not current research. Check original dates, sources and forecast assumptions.' if english else '历史报告保留原文。数据日期、估计与预测请以正文和原始出处为准。'} · © Global Business Insight</div></div></footer></body></html>'''

def card(r):
 status=f'档案 / {r.get("qualityScore",0)}分（未达70分）' if r.get('qualityScore',100)<70 else '历史资料 / 原始日期与口径见正文' if r.get('editorialStatus')=='archive' else '原始日期与口径见正文'
 return f'<article class="report"><div class="eyebrow">{escape(r["categoryLabel"])} / {escape(r["languageLabel"])}</div><h3><a href="{r["url"]}">{escape(r["title"])}</a></h3><p>{escape(r["description"])}</p><small>{status}</small></article>'
def cards(paths,by):return ''.join(card(by[p]) for p in paths if p in by and by[p].get('qualityScore',100)>=70 and by[p].get('editorialStatus')!='archive')
HOME_COPY={
 'eu-steel-import-rules-2026.html':('EU Steel Imports: Quotas, Origin Records and Carbon Rules Are Separate Checks','The new safeguard changes both quota exposure and origin reporting. This briefing separates the tariff-rate quota from melt-and-pour documentation and the EU carbon mechanism.'),
 'hangcha-thailand-manufacturing-2026.html':('Hangcha’s Thailand Plant Moves Overseas Growth Closer to Local Production','The company opened its first self-owned overseas factory in Thailand. The 10,000-unit annual capacity figure is a 2028 target, not current output.'),
 'us-semiconductor-market-2026.html':('U.S. Chip Sales Are Strong; Domestic Capacity Takes Longer to Build','Market share, announced investment and operating production are different measures. The briefing puts recent U.S. and global figures in their proper context.'),
 'catl-globalization-q3-2026.html':('CATL’s Overseas Expansion: Growth Meets the Test of Local Delivery','Recent filings show overseas growth and a European plant entering trial operation. Planned capacity is not yet commercial output.'),
 'asean-cooling-market-2026.html':('Southeast Asia’s Cooling Market: Demand Growth Meets Efficiency and Power Constraints','Demand prospects vary by country. Energy rules, grid capacity, affordability and service networks shape how the market develops.'),
 'middle-east-desalination-2026.html':('Saudi Desalination: New Capacity Brings Financing and Efficiency Questions','The briefing follows public project data through procurement, financing, reverse-osmosis performance and delivery risk.'),
 'eu-heat-pump-market-2026.html':('Europe’s Heat-Pump Recovery Is Uneven Across National Markets','Sales growth alone does not explain market conditions. Electricity prices, incentives, installer capacity and after-sales service differ across countries.'),
 'reports/e-invoicing/04-e-invoice-lifecycle.html':('An E-Invoice’s Lifecycle: From Transaction Evidence to Records','A plain-language guide to issue, transmit, receive, approve, post and archive an e-invoice—and to the distinct systems behind each step.'),
 'us-aircraft-mro-workforce-2026.html':('More U.S. Aircraft Mechanic Certificates Do Not Automatically Mean More Technicians','Certification counts do not reveal how many people enter or remain in aviation maintenance. The briefing examines the workforce pipeline.'),
 'north-america-freight-rail-2026.html':('North American Freight: Stronger Rail Volumes Meet Corridor Limits','Rail units and cross-border trade values describe different parts of the freight system. Terminal and corridor performance shape the operating picture.'),
 'eu-packaging-ppwr-market-2026.html':('The EU Packaging Rules Connect Product Design to Local Recovery Systems','The new framework phases in requirements for packaging design, recycled material, labels and recycling across member states.'),
 'latin-america-battery-storage-market-2026.html':('Latin America’s Battery-Storage Market Is Taking Different Routes','Chile, Brazil and Mexico offer different procurement and grid arrangements. Regional demand should not be treated as one market.'),
}
def home_card(path,by):
 r=by.get(path);copy=HOME_COPY.get(path)
 if not r or r.get('qualityScore',0)<70 or not copy:return ''
 category={'industry':'Industry × Region','global':'China Going Global','digital':'Technology & Operations','markets':'Markets & Macro'}.get(r['category'],'Research archive')
 return f'<article class="feed-item" data-category="{escape(r["category"])}" data-search="{escape((r["title"]+" "+r["description"]+" "+copy[0]+" "+copy[1]).lower(),quote=True)}"><div class="feed-date"><span>RESEARCH</span><b>BRIEF</b></div><div class="feed-copy"><div class="feed-tags"><span>{category}</span><span class="feed-type">{escape(r["languageLabel"])}</span></div><h3><a href="{r["url"]}">{escape(copy[0])}</a></h3><p>{escape(copy[1])}</p></div><div class="feed-source"><b>Global Business Insight</b><span>Open briefing ↗</span></div></article>'
def home_card_zh(path,by):
 r=by.get(path)
 if not r or r.get('qualityScore',0)<70 or r.get('editorialStatus')=='archive':return ''
 category={'industry':'产业与市场','global':'中国企业出海','digital':'技术与运营','markets':'市场观察'}.get(r['category'],'研究简报')
 return f'<article class="feed-item" data-category="{escape(r["category"])}" data-search="{escape((r["title"]+" "+r["description"]).lower(),quote=True)}"><div class="feed-date"><span>研究</span><b>简报</b></div><div class="feed-copy"><div class="feed-tags"><span>{category}</span><span class="feed-type">{escape(r["languageLabel"])}</span></div><h3><a href="{r["url"]}">{escape(r["title"])}</a></h3><p>{escape(r["description"])}</p></div><div class="feed-source"><b>全球商业洞察</b><span>阅读全文 ↗</span></div></article>'
def homepage(records,by):
 industry_paths=[p for p in FEATURED['industry'] if p in by and by[p].get('qualityScore',0)>=70]
 lead_path=next((p for p in industry_paths if p in by and by[p].get('language','').startswith('zh')),'eu-steel-import-rules-2026.html')
 if lead_path not in by:lead_path=next((p for p in industry_paths if p in by),'')
 if not lead_path:return intro('GLOBAL BUSINESS INSIGHT','Research across markets and industries.','Source-led reporting on global business.')
 lead=by[lead_path]
 dynamic=global_feature_paths(records)
 paths=[]
 for p in dynamic+industry_paths+FEATURED['global']+FEATURED['digital']+['reports/e-invoicing/04-e-invoice-lifecycle.html']:
  if p in HOME_COPY and p!=lead_path and p not in paths and p in by and by[p].get('qualityScore',0)>=70:paths.append(p)
 stories=''.join(home_card_zh(p,by) for p in paths[:9] if by[p].get('language','').startswith('zh'))
 english_paths=[p for p in paths if p in HOME_COPY and by[p].get('language','').startswith('en')][:5]
 if len(english_paths)<4:
  english_paths += [p for p in paths if p in HOME_COPY and p not in english_paths][:4-len(english_paths)]
 english_cards=''.join(f'<article class="english-story"><span class="english-kicker">{escape(HOME_COPY[p][0] and {"industry":"INDUSTRY × REGION","global":"CHINA GOING GLOBAL","digital":"TECHNOLOGY","markets":"MARKETS"}.get(by[p]["category"],"RESEARCH"))}</span><h3><a href="{by[p]["url"]}">{escape(HOME_COPY[p][0])}</a></h3><p>{escape(HOME_COPY[p][1])}</p><a class="english-link" href="{by[p]["url"]}">Read briefing ↗</a></article>' for p in english_paths)
 body=f'''<div class="home-ticker"><span>研究台</span><b>产业 · 市场 · 企业全球化</b><a href="/archive/">浏览全部研究 →</a></div>
 <div class="home-newspaper-grid"><div class="home-main-column">
 <section class="home-intro"><div><div class="home-eyebrow">GLOBAL BUSINESS INSIGHT / 编辑部</div><h1>看懂产业变化，<br>找到出海方向。</h1><p>聚焦产业、区域市场与中国企业全球化。先把事实和口径说清，再解释它们意味着什么。</p><a class="home-cta" href="#latest">浏览最新研究 <span>↓</span></a></div><div class="home-intro-note"><span class="pulse"></span><div><b>研究，不追噪音。</b><small>用数据和现场变化理解跨境商业。</small></div></div></section>
 <section class="home-feature" aria-label="重点研究"><div class="feature-main"><div class="home-eyebrow">本期重点 · 行业 × 区域</div><h2><a href="{lead['url']}">{escape(lead['title'])}</a></h2><p>{escape(lead['description'])}</p><div class="feature-meta"><span>{escape(lead['categoryLabel'])}</span><span>{escape(lead['languageLabel'])}</span><span>数据与来源见正文</span></div><a class="home-read" href="{lead['url']}">阅读全文 ↗</a></div><aside class="feature-rail"><div class="rail-title">文章要点 <span>研究摘要</span></div><div class="rail-signal"><small>市场</small><b>看清需求与贸易规则</b><span>区分配额、来源追溯与碳成本。</span></div><div class="rail-signal"><small>执行</small><b>回到国家与企业层面</b><span>制度、服务和本地经营条件各不相同。</span></div><div class="rail-signal"><small>判断</small><b>数字必须放在口径里读</b><span>市场规模不等于企业收入或利润。</span></div></aside></section>
 <section class="feed-section" id="latest"><div class="feed-heading"><div><div class="home-eyebrow">研究简报</div><h2>最新文章</h2><p>按产业、企业出海与技术主题快速查找。</p></div><a href="/archive/">全部文章 →</a></div><div class="feed-toolbar"><div class="feed-tabs" role="group" aria-label="按主题筛选"><button class="feed-tab active" data-home-filter="all">全部</button><button class="feed-tab" data-home-filter="industry">产业与市场</button><button class="feed-tab" data-home-filter="global">企业出海</button><button class="feed-tab" data-home-filter="digital">技术与运营</button></div><label class="feed-search"><span aria-hidden="true">⌕</span><input type="search" id="home-search" placeholder="搜索文章" aria-label="搜索文章"></label></div><div class="feed-list" id="home-feed">{stories}<p class="feed-empty" hidden>没有找到相关文章，请换个关键词。</p></div></section>
 <section class="home-desks" id="topics"><div class="feed-heading"><div><div class="home-eyebrow">研究专题</div><h2>按问题进入</h2></div><a href="/archive/">搜索全部资料 →</a></div><div class="desk-grid"><a class="desk-card" href="/category/industry/"><span>01 / 产业</span><b>产业与供应链</b><small>制造、物流、能源与贸易规则。</small></a><a class="desk-card" href="/category/global/"><span>02 / 企业</span><b>中国企业出海</b><small>海外市场、渠道服务与本地经营。</small></a><a class="desk-card" href="/category/digital/"><span>03 / 技术</span><b>企业数字化</b><small>AI、电子发票与业务流程。</small></a><a class="desk-card" href="/markets/"><span>04 / 数据</span><b>市场观察</b><small>美国市场、利率、就业与GDP。</small></a></div></section>
 </div><aside class="english-column" aria-labelledby="english-column-title"><div class="english-column-head"><span>GLOBAL BUSINESS INSIGHT</span><h2 id="english-column-title">English Desk</h2><p>Selected reporting for readers following global markets and cross-border business.</p></div>{english_cards}<a class="english-all" href="/en/">All English research <span>↗</span></a></aside></div>
 <section class="home-subscribe"><div><div class="home-eyebrow">邮件更新</div><h2>订阅你关心的研究主题</h2><p>选择板块后，站长会手动发送精选文章；可随时回复邮件退订。</p><small>中文为主 · English research available</small></div><form class="home-subscribe-form" data-manual-subscribe data-destination="{escape(MANUAL_SUBSCRIBE_EMAIL,quote=True)}"><label class="home-email">邮箱地址<input name="email" type="email" autocomplete="email" placeholder="you@example.com" required></label><fieldset><legend>选择研究板块</legend><label><input type="checkbox" name="topics" value="industry"> 产业与供应链</label><label><input type="checkbox" name="topics" value="global"> 中国企业出海</label><label><input type="checkbox" name="topics" value="digital"> 技术与运营</label><label><input type="checkbox" name="topics" value="markets"> 市场观察</label><label><input type="checkbox" name="topics" value="english"> English research</label></fieldset><label class="home-consent"><input type="checkbox" name="consent" required> 我同意接收所选主题的文章更新，可随时回复邮件退订。</label><input class="form-trap" name="website" tabindex="-1" autocomplete="off" aria-hidden="true"><button type="submit">订阅</button><p class="home-status" data-subscribe-status role="status" aria-live="polite"></p></form></section>'''
 body+='<script>(function(){const tabs=[...document.querySelectorAll("[data-home-filter]")],rows=[...document.querySelectorAll(".feed-item")],input=document.getElementById("home-search"),empty=document.querySelector(".feed-empty");let cat="all";function update(){let n=0;rows.forEach(row=>{const ok=(cat==="all"||row.dataset.category===cat)&&(!input.value||row.dataset.search.includes(input.value.trim().toLowerCase()));row.hidden=!ok;if(ok)n++});empty.hidden=!!n}tabs.forEach(b=>b.addEventListener("click",()=>{tabs.forEach(x=>x.classList.toggle("active",x===b));cat=b.dataset.homeFilter;update()}));input.addEventListener("input",update)})()</script>'
 return body,lead_path
def share_card(r, kind):
 tracked=canonical(r['path'])+'?utm_source=homepage&utm_medium=social&utm_campaign=share_'+kind
 if r['path']=='us-aircraft-mro-workforce-2026.html':
  en='The FAA issued 11,100+ mechanic certificates in 2025, nearly double 2016. But the FAA does not track how many certificate holders work in aviation maintenance. U.S. training capacity is growing; jobs, experience and retention remain the real constraints.'
  zh='美国2025年新增航空维修技师证书超过1.1万张，接近2016年的两倍；FAA却没有追踪持证者是否进入维修行业。培训在扩张，岗位转化、经验和留任仍是约束。'
  tags='#AviationMaintenance #Workforce #NorthAmerica'
 elif r['path']=='sinovac-global-h1-2026.html':
  en='Sinovac’s H1 2026 overseas sales rose 82.3% to US$66.5m, or 45.2% of total sales, led by varicella and sIPV vaccines. The company still posted a US$91.4m net loss. Market access is expanding; profit conversion is not yet established.'
  zh='科兴生物2026年上半年海外收入增长82.3%至6,650万美元，占总销售45.2%，主要由水痘和sIPV疫苗带动；公司同期净亏损9,140万美元。市场准入在扩张，利润转化仍待验证。'
  tags='#Sinovac #ChinaGoingGlobal #Biopharma'
 elif r['path']=='eu-steel-import-rules-2026.html':
  en='The EU’s 2026 steel regime separates quota exposure from origin traceability. The 50% out-of-quota duty applies only after the relevant product-and-country quota is exhausted. Since 1 October, importers must also declare and document where steel was melted and poured. CBAM is a separate carbon-cost obligation.'
  zh='欧盟2026年钢铁规则把配额与来源追溯分开处理：相关产品和来源国配额用尽后，超额部分才适用50%关税。10月起，进口商还需申报并证明钢材熔炼与浇铸地。CBAM另行核算碳成本。'
  tags='#EUTrade #Steel #SupplyChain'
 elif r['path']=='hangcha-thailand-manufacturing-2026.html':
  en='Hangcha’s H1 2026 revenue rose 8.65% to RMB10.10bn; its company-reported overseas revenue rose 12.69% in USD terms. The group opened its first self-owned overseas plant in Thailand in June. The 10,000-unit annual capacity target is for 2028—not current output—and overseas project returns are not yet disclosed.'
  zh='杭叉集团2026年上半年收入增长8.65%至101.0亿元，公司披露的美元口径海外收入增长12.69%。6月，首个自有海外工厂在泰国揭幕。年产约1万台是2028年目标，不是当前产量；项目回报尚未披露。'
  tags='#Hangcha #ChinaGoingGlobal #IndustrialVehicles'
 elif r['path']=='us-semiconductor-market-2026.html':
  en="U.S. semiconductor firms held 53.4% of global sales in 2025; worldwide sales reached US$517.7bn in Q3 2026 (+24.1% q/q). More than US$770bn in announced U.S. ecosystem investment is not operating capacity. We separate market share, production and project delivery."
  zh="美国总部企业2025年占全球芯片销售额53.4%；2026年Q3全球销售额达5,177亿美元、环比增长24.1%。美国投资公告超过7,700亿美元，但公告不等于产能。"
  tags='#USSemiconductors #Chips #MarketResearch'
 elif r['path']=='sanhua-global-q3-2026.html':
  en="Sanhua reported H1 2026 overseas sales of RMB7.05bn (-2.2%), 41.7% of core revenue, with a 29.77% gross margin vs 26.84% in China. 9M revenue rose 5.18%, while attributable profit fell 5.4%. Regional operating profit is not disclosed."
  zh="三花智控上半年境外销售70.52亿元、同比下降2.2%，占主营业务41.7%；境外毛利率29.77%，高于国内，但地区营业利润未完整披露。前三季度收入增长、归母净利润下降。"
  tags='#Sanhua #ChinaGoingGlobal #Manufacturing'
 elif r['path']=='thailand-ev-market-2026.html':
  en='Thailand registered 165,040 new battery-electric passenger cars in Jan–Sep 2026 (+95.2% y/y), while BEV passenger-car exports were 13,002 units. Total vehicle exports fell 4.9%, and pickups remained 61.2% of shipments. Demand is moving faster than the export mix.'
  zh='泰国2026年1—9月新注册纯电乘用车165,040辆，同比增长95.2%；同期纯电乘用车出口13,002辆。整车出口总量下降4.9%，皮卡仍占61.2%。需求变化快于出口结构转型。'
  tags='#Thailand #ElectricVehicles #SoutheastAsia'
 elif r['path']=='geely-global-q3-2026.html':
  en='Geely Auto’s 9M 2026 sales rose 3% to 2.235m vehicles, revenue grew 13% to RMB272.6bn, and HKFRS attributable profit rose 7%. Company-defined core profit rose 41%, partly reflecting FX comparisons. October exports reached 107,153; overseas profitability is not disclosed.'
  zh='吉利汽车2026年前三季度销量增长3%至223.55万辆，收入增长13%至2,725.64亿元，HKFRS归母利润增长7%；公司定义的核心利润增长41%，部分受汇兑比较影响。十月出口107,153辆，海外利润未披露。'
  tags='#Geely #ChinaGoingGlobal #Automotive'
 elif r['path']=='thailand-medical-devices-market-2026.html':
  en='Thailand is both a medical-device manufacturing base and an import market. MEDIU-based estimates put the 2024 market at US$8.25bn; imports were about THB96bn in 2025 (-1.4%), and H1 2026 imports and exports both declined. Product mix matters: high-tech equipment relies more on imports, while local output is stronger in selected consumables.'
  zh='泰国医疗器械市场同时包含本地制造、进口和出口。MEDIU口径下2024年市场估算约82.46亿美元；2025年进口约960亿泰铢、下降1.4%，2026年上半年进出口均回落。高技术设备与本地耗材制造的结构不同。'
  tags='#Thailand #MedicalDevices #SoutheastAsia'
 elif r['path']=='yofc-global-q3-2026.html':
  en='YOFC reported 9M 2026 revenue of RMB19.12bn (+86.1%) and attributable profit of RMB6.13bn. The company cites data-centre demand, product mix and changes in volumes and prices. Overseas revenue exceeded 40% in FY2025 and H1 2026; nine overseas plants span seven countries. Q3 figures are unaudited, and regional profit is not disclosed.'
  zh='长飞光纤2026年前三季度收入191.25亿元、增长86.12%，归母净利润61.28亿元。公司将增长归因于数据中心需求、产品结构及销量价格变化。2025年与2026年上半年境外收入占比均超过四成；三季报未经审计，也未披露地区利润。'
  tags='#YOFC #ChinaGoingGlobal #OpticalFiber'
 elif r['path']=='eu-sustainable-aviation-fuel-market-2026.html':
  en='EASA reports that supplier filings put EU SAF at 2.79% of aviation fuel supplied in 2025, above the 2% mandate. About 85% of feedstocks came from outside the EU, while the SAF reference price was nearly three times conventional jet fuel. The first-year threshold was met; feedstock dependence, cost and synthetic-fuel scale remain unresolved.'
  zh='EASA供应商申报数据显示，欧盟2025年SAF占航空燃料供应2.79%，高于2%的最低比例。约85%的原料来自欧盟以外，SAF参考价接近传统航油三倍。首年目标已跨过，原料、成本和合成燃料规模仍是难点。'
  tags='#EU #SustainableAviationFuel #Aviation'
 elif r['path']=='lenovo-global-q1-2026-2027.html':
  en='Lenovo’s Q1 FY2026/27 revenue rose 43% to US$26.94bn, with AI-related revenue at US$9.3bn. ISG revenue nearly doubled, but operating expenses grew 123%; statutory net loss attributable to shareholders was US$609m, alongside US$1.075bn adjusted net income. The distinction matters when reading global growth.'
  zh='联想FY2026/27一季度收入增长43%至269.43亿美元，AI相关收入93亿美元。ISG收入接近翻倍，但营业费用增长123%；股东应占净亏损6.09亿美元，同时调整后净利润为10.75亿美元。两种口径必须并列看。'
  tags='#Lenovo #ChinaGoingGlobal #AIInfrastructure'
 elif r['path']=='north-america-battery-market-2026.html':
  en='North American battery markets are at different stages. U.S. grid-scale storage reached nearly 52 GW by June 2026, and batteries accompanied over 16% of new utility-scale solar capacity added through September. Canada is growing from a smaller base. DOE’s 179-to-707 GWh demand projection spans transport and storage; it is not a grid-storage order book. Local module assembly also does not mean local cells and materials are fully supplied.'
  zh='北美电池市场进度不一：美国电网级储能截至2026年6月接近52 GW，9月前新增公用事业太阳能中超过16%已与可运营电池共址；加拿大仍处较小规模。DOE的179至707 GWh预测覆盖交通与储能，不是电网储能订单。本地组装也不代表电芯和材料已实现自给。'
  tags='#NorthAmerica #BatteryStorage #EnergyTransition'
 elif r['path']=='jinko-global-q3-2026.html':
  en='Jinko Holdings’ Q3 2026 module shipments fell 25% year over year and revenue declined 15.7%, but gross margin recovered to 12.3% from 4.2% in Q2. Overseas markets accounted for about 70% of shipments; 1.75 GWh of storage shipments were recognized as revenue. The company still reported a net loss, and regional profits were not disclosed.'
  zh='晶科控股2026年三季度组件出货同比下降25%、收入下降15.7%，毛利率却从Q2的4.2%回升至12.3%。海外市场约占出货七成，1.75 GWh储能系统出货确认为收入；公司仍录得净亏损，未披露地区利润。'
  tags='#Jinko #ChinaGoingGlobal #SolarStorage'
 elif r['path']=='latin-america-copper-market-2026.html':
  en='Latin American copper supply is not one number. Cochilco projects a 0.5% refined-copper surplus in 2026, while Chile’s Jan–Sep mine output fell 8.5%; Peru’s copper production index rose 2.14% in Jan–Jul. Different periods and measures, one clear point: projects and reserves do not equal near-term supply.'
  zh='拉美铜供应不能只看一个总数。COCHILCO预计2026年精炼铜盈余仅占需求0.5%；智利1—9月产量下降8.5%，秘鲁1—7月铜矿生产指数增长2.14%。指标和期间不同，但都说明储量与项目不等于近期新增供应。'
  tags='#LatinAmerica #Copper #Mining'
 elif r['path']=='tcl-electronics-global-2026.html':
  en='TCL Electronics’ international TV revenue rose 29.6% in H1 2026, while gross profit grew 70.6% and margin reached 18.9%. Larger screens and Mini LED lifted the mix. Q1–Q3 group figures are still preliminary estimates; country-level profit has not been disclosed.'
  zh='TCL电子2026年上半年国际电视收入增长29.6%，毛利增长70.6%，毛利率升至18.9%；大屏和Mini LED产品占比提高。前三季度集团数据仍是预估，各国利润尚未披露。'
  tags='#TCL #ChinaGoingGlobal #ConsumerElectronics'
 elif r['path']=='west-africa-cocoa-market-2026.html':
  en='Côte d’Ivoire set its 2026/27 main-crop cocoa farmgate price at CFA 1,200/kg, down from CFA 2,800 last season; Ghana set GH¢42,400/tonne, or 71.18% of realised gross FOB. ICCO’s latest public balance covers 2024/25, not the new crop. The price resets and traceability rules now shape West African cocoa trade.'
  zh='科特迪瓦2026/27主季可可收购价为1,200西非法郎/公斤，低于上季2,800；加纳定价为42,400塞地/吨，占实现FOB值71.18%。ICCO最新公开全球平衡表仍对应2024/25产季。价格重设与欧盟追溯要求共同影响西非贸易。'
  tags='#WestAfrica #Cocoa #AgriculturalTrade'
 elif r['path']=='xiaomi-global-2026.html':
  en='Xiaomi generated RMB78.8bn outside mainland China in H1 2026, 37.9% of group revenue; the company says most of that revenue comes from Europe and India. It shipped 65m smartphones and had 640+ overseas new-retail stores. India-related proceedings remain unresolved, with RMB3.54bn in restricted cash equivalents disclosed. Scale is clear; local profitability is not.'
  zh='小米2026年上半年中国大陆以外收入788.2亿元，占集团收入37.9%，公司称主要来自欧洲和印度；手机出货6,500万台，海外新零售门店超过640家。印度相关案件仍在审理，受限资金折合约35.36亿元人民币。海外规模已形成，地区盈利仍未单独披露。'
  tags='#Xiaomi #ChinaGoingGlobal #ConsumerElectronics'
 elif r['path']=='middle-east-solar-storage-market-2026.html':
  en='Saudi Arabia has closed financing for seven renewables projects totaling 15 GW; the UAE has financed a 5.2 GW solar-plus-storage project targeting 1 GW of continuous clean power. Both remain execution stories, not operating results. Grid access, dispatch, finance and long-term service are the commercial gates.'
  zh='沙特7个可再生能源项目合计15GW，已完成融资关闭；阿联酋5.2GW光伏与19GWh储能项目规划提供1GW连续清洁电力。两者都仍待建设投运。本文关注并网、调度、融资和长期服务。'
  tags='#MiddleEast #SolarStorage #EnergyInfrastructure'
 elif r['path']=='catl-globalization-q3-2026.html':
  en='CATL’s nine-month 2026 revenue grew 56.2%, while attributable profit rose 31.6% and operating cash flow fell 23.6%. H1 overseas revenue was RMB87.1bn, or 31.46% of total, but the Q3 filing gives no regional split. Hungary module assembly has started; cell production still awaits permits, and Spain remains under construction. The next test is local cash and returns.'
  zh='宁德时代前三季度收入增长56.2%、归母净利增长31.6%，经营现金流下降23.6%。上半年境外收入871.3亿元，占31.46%，但三季报未披露地区拆分。匈牙利已启动模组装配，电芯生产仍待许可；西班牙项目仍在建设。'
  tags='#CATL #ChinaGoingGlobal #BatterySupplyChain'
 elif r['path']=='eu-heat-pump-market-2026.html':
  en='European heat-pump sales rose 13% to 2.9 million units across 21 countries in 2025, but the recovery is uneven. Electricity pricing, stable incentives, installers, compliance and service determine whether regional demand becomes profitable local business.'
  zh='欧洲21国热泵销量2025年增长13%至290万台，但各国复苏并不同步。电力与燃气价格、补贴稳定性、安装能力、合规与售后决定区域需求能否转化为可盈利的本地业务。'
  tags='#Europe #HeatPumps #MarketEntry'
 elif r['path']=='midea-global-2026.html':
  en='Midea earned RMB113.1bn outside mainland China in H1 2026, up 5.5% and about 43.3% of group revenue by calculation. Owned-brand business exceeded 50% of overseas smart-home revenue. The next proof points are country-level profit, service economics and cash conversion.'
  zh='美的2026年上半年中国大陆以外收入1131亿元，同比增长5.5%，按集团收入计算约占43.3%；智能家居海外收入中OBM占比超过50%。下一步要验证国别利润、服务成本和现金转换。'
  tags='#Midea #ChinaGoingGlobal #GlobalBrands'
 elif r['path']=='north-america-transformers-market-2026.html':
  en='DOE says U.S. distribution-transformer demand is up 41% since 2019, while 2024 lead times remained 1–2+ years. With 80,000+ configurations and rising replacement needs, qualification and procurement standardization matter as much as factory capacity.'
  zh='DOE称美国配电变压器需求较2019年升41%，2024年交期仍达1–2年以上；约8万种配置、老旧设备更换与新增负荷共同挤压供应。标准化、资质与交付能力决定供应商能否进入。'
  tags='#NorthAmerica #GridInfrastructure #Transformers'
 elif r['path']=='sungrow-global-2026.html':
  en='Sungrow’s 2025 overseas revenue rose 48.8% to RMB54.0bn, about 60.5% of total by calculation; overseas gross margin was 40.36%. Yet H1 2026 group revenue fell 29.0%. Local service is visible; current overseas growth and country-level returns still need proof.'
  zh='阳光电源2025年境外收入539.9亿元、同比增长48.76%，按地区收入合计推算约占60.5%；境外毛利率40.36%。但2026年上半年集团收入下降28.99%、归母净利下降32.01%，不能把2025海外增长直接外推。'
  tags='#Sungrow #ChinaGoingGlobal #EnergyStorage'
 elif r['path']=='latin-america-power-resilience-2026.html':
  en='IEA warns the 2026–27 El Niño may stress Latin American power systems where hydropower supplies over half of generation in several countries. Drought, heat and flooding risks vary by location; resilience depends on prepared emergency measures, reserve resources, grid links and tested coordination.'
  zh='IEA指出，2026—2027年厄尔尼诺可能冲击部分水电依赖度高的拉美电力系统。旱涝风险因地而异，备用资源、跨境互联、应急治理和演练决定韧性。'
  tags='#LatinAmerica #PowerSystems #ClimateResilience'
 elif r['path']=='superhi-global-2026.html':
  en='Super Hi’s H1 2026 revenue rose 12.1% to US$444.8m and operating margin improved to 5.0%, yet net profit fell to US$2.1m from US$28.3m. Southeast Asia accounts for 73 of 129 Haidilao restaurants. Regional store metrics diverge—growth needs to be tested against same-store sales and group-level profit.'
  zh='特海国际上半年收入增长12.1%至4.448亿美元，经营利润率升至5.0%，净利润却由2,827万美元降至212万美元。129家海外门店中73家位于东南亚；区域同店与翻台指标分化，扩张质量仍需集团利润验证。'
  tags='#Haidilao #ChinaGoingGlobal #RestaurantBusiness'
 elif r['path']=='asean-power-grid-2026.html':
  en='IEA projects Southeast Asian electricity demand to grow 5.4% a year in 2026–2030; ASEAN’s new Energy Outlook says data centres account for about one-fifth of power-demand growth to 2030. The opportunity depends on grids, flexibility, project bankability and cross-border rules—not demand forecasts alone.'
  zh='IEA预计东南亚2026—2030年电力需求年均增长5.4%；东盟第九版能源展望估算，数据中心约占未来五年新增用电增长的五分之一。并网、灵活性、融资和跨境规则决定需求能否兑现。'
  tags='#ASEAN #PowerGrid #EnergyInvestment'
 elif r['path']=='middle-east-aviation-2026.html':
  en='Middle East carriers saw August 2026 passenger demand (RPK) fall 14.6% year over year, while capacity (ASK) fell 9.3% and load factor slipped 4.9 points to 78.9%. Dubai International welcomed 31.5m passengers in H1, down 31.3%, despite a month-by-month Q2 rebound. Route reopening is not the same as hub recovery.'
  zh='中东航司2026年8月RPK同比下降14.6%，ASK下降9.3%，客座率同比降4.9个百分点至78.9%。迪拜机场上半年客流下降31.3%，Q2逐月回升；航线恢复不等于枢纽网络完全恢复。'
  tags='#MiddleEastAviation #AirTransport #MarketBrief'
 elif r['path']=='xpeng-global-2026.html':
  en='XPENG’s H1 2026 overseas revenue rose 62.2% to RMB8.23bn, and Q2 overseas deliveries topped 20,000. Graz partner production and a new European launch deepen localization, but group losses widened and overseas profit was not disclosed. Can growth become durable local economics?'
  zh='小鹏2026年上半年境外收入增长62.2%至82.26亿元，Q2海外交付超过2万辆；格拉茨合作生产和欧洲新车发布深化本地化，但集团亏损扩大，海外利润未单独披露。'
  tags='#XPENG #ChinaGoingGlobal #EuropeanEV'
 elif r['path']=='transsion-global-2026.html':
  en='Transsion’s 2025 revenue fell 4.5%, while attributable profit dropped 53.5%. Revenue rebounded 30.1% in the four months to April 2026, but operating cash flow was negative RMB5.28bn, largely alongside inventory build. Its multi-brand and after-sales footprint is real; durable cash conversion is the next test.'
  zh='传音2025年收入下降4.5%、归母利润下降53.5%；2026年前四个月收入回升30.1%，经营现金流仍净流出52.8亿元，存货增加占用现金。多品牌与售后网络已形成，盈利恢复还需现金流验证。'
  tags='#Transsion #ChinaGoingGlobal #EmergingMarkets'
 elif r['path']=='eu-packaging-ppwr-market-2026.html':
  en='EU packaging rules began applying in August 2026, but the commercial change will unfold over several years. Eurostat recorded 81.5m tonnes of packaging waste in 2024; plastic packaging recycling was 42.4%, with wide country differences. The new regime connects package design, recycled materials and local recovery systems.'
  zh='欧盟PPWR自2026年8月起适用，但要求分阶段落地。2024年欧盟包装废弃物达8,150万吨，塑料包装回收率为42.4%，成员国差异明显。包装设计、再生料与当地回收体系将被放到同一条链路上。'
  tags='#EU #Packaging #CircularEconomy'
 elif r['path']=='yutong-global-2026.html':
  en='Yutong’s overseas core-business revenue rose 38.9% in 2025, with a 29.62% gross margin. In the first nine months of 2026, total bus sales fell 7.83% and group revenue fell 2.09%; filings do not break out current overseas sales. Its 400+ service outlets and 40+ parts warehouses show the operating footprint behind exports.'
  zh='宇通客车2025年海外主营收入增长38.87%、毛利率29.62%；2026年前三季度集团销量下降7.83%、营收下降2.09%，但没有单列海外销售。公司披露海外服务网点超400个、配件库40余个，出口后的服务网络正在形成。'
  tags='#Yutong #ChinaGoingGlobal #PublicTransport'
 elif r['path']=='eu-data-centre-grid-2026.html':
  en='EU data centres used an estimated 68 TWh of electricity in 2024; the Commission projects 114 TWh by 2030. That forecast is not committed demand. Grid access, location, energy and water performance are shaping where new capacity can operate. Minimum performance standards are still under consultation.'
  zh='欧盟数据中心2024年用电估算为68 TWh，委员会预测2030年升至114 TWh。预测不等于已落地需求；并网、选址、能效与用水将影响项目落地。最低能效标准仍在咨询中。'
  tags='#EUDataCentres #PowerGrid #EnergyEfficiency'
 elif r['path']=='popmart-global-2026.html':
  en='POP MART’s H1 2026 group revenue rose 23.8%, but overseas revenue fell 11.1%. Store counts grew in the Americas and Europe; online sales declined sharply in both the Americas and Asia Pacific. The interim report shows how store expansion and overseas sales momentum can diverge.'
  zh='泡泡玛特2026年上半年集团收入增长23.8%，海外收入下降11.1%。美洲、欧洲门店增加，但美洲和亚太线上销售明显下滑。中期披露显示，扩店与海外销售动能并不总是同步。'
  tags='#PopMart #ChinaGoingGlobal #ConsumerBrands'
 elif r['path']=='eu-solar-grid-flexibility-2026.html':
  en='EU solar added an estimated 33.8 GWdc in H1 2026 (+1.9% year over year), while solar made up 41.6% of renewable electricity generation in Q2. These are different measures. The next market test is grid access, flexibility and revenue capture—not capacity alone.'
  zh='欧盟2026年上半年新增太阳能装机估算33.8 GWdc、同比增长1.9%；Q2太阳能占可再生电力发电量41.6%，并非全部发电量。并网、储能与收益兑现将决定下一阶段竞争。'
  tags='#EuropeanSolar #EnergyStorage #GridFlexibility'
 elif r['path']=='zte-global-2026.html':
  en='ZTE’s international revenue grew 12.39% in 2025 and 33.1% in H1 2026, reaching 35.7% of first-half group revenue. Networks, devices and computing offer several growth paths, but overseas margins, local customer mix and cash conversion remain key proof points.'
  zh='中兴通讯国际收入2025年增长12.39%，2026年上半年增长33.1%，占同期总收入35.7%。网络、终端与算力形成多条增长路径，海外利润、客户结构和现金回收仍待验证。'
  tags='#ZTE #ChinaGoingGlobal #GlobalBusiness'
 elif r['path']=='north-america-freight-rail-2026.html':
  en='U.S. intermodal rail reached a monthly record in August, while June cross-border freight value rose 19.9% year over year. The measures cover different scopes: U.S. rail units versus cross-border trade value. Corridor capacity, terminal dwell and first/last-mile execution will shape service quality.'
  zh='美国铁路联运8月创月度纪录，6月跨境货运金额同比增长19.9%。两项指标口径不同；口岸、场站和两端短驳决定增长能否转化为稳定交付。'
  tags='#NorthAmericanFreight #Intermodal #SupplyChain'
 elif r['path']=='latin-american-manufacturing-fdi-2026.html':
  en='Latin America and the Caribbean attracted US$194.2bn of FDI in 2025 (+1.7%), but manufacturing inflows fell 17.2% as services rose 19.5%. Announced project value dropped 34.3%—a reminder that capital flows, project announcements and factory investment are different signals.'
  zh='拉美和加勒比2025年FDI流入增长1.7%，但制造业下降17.2%，服务业增长19.5%；公告项目金额下降34.3%。资金流、项目公告与实际建厂不能混为一谈。'
  tags='#LatinAmerica #Manufacturing #ForeignDirectInvestment'
 elif r['path']=='alibaba-global-2026.html':
  en='Alibaba’s FY2026 international retail revenue grew 9%, while the international digital commerce group’s adjusted EBITA loss narrowed to RMB2.05bn. In the June quarter, international e-commerce revenue fell 1% year over year even as AliExpress reported operating profit and local product supply grew. Profitability is improving, but growth remains uneven.'
  zh='阿里巴巴FY2026国际零售收入增长9%，国际数字商业集团经调整EBITA亏损收窄；但截至6月季度国际电商收入同比下降1%，AliExpress单平台称实现经营利润。本地化与持续增长仍待验证。'
  tags='#Alibaba #CrossBorderEcommerce #ChinaGoingGlobal'
 elif r['path']=='huhutech-global-2026.html':
  en='HUHUTECH reported US$10.67m in H1 2026 revenue, up 8.6%; new U.S., German and Singapore operations supplied 34.6% of sales. Yet GAAP net loss widened to US$16.65m, receivables rose to US$10.94m and operating cash outflow reached US$3.36m. Expansion is visible; repeatable delivery and cash conversion remain unproven.'
  zh='HUHUTECH上半年营收增长8.6%，美国、德国和新加坡贡献34.6%；但GAAP净亏损扩大，应收账款上升、经营现金流流出。出海质量仍需回款与项目表现验证。'
  tags='#ChinaGoingGlobal #IndustrialAutomation #GlobalBusiness'
 elif r['path']=='middle-east-desalination-2026.html':
  en='Saudi Arabia’s water procurement system has contracted desalination capacity above 10 million m³/day, with SAR 56bn in privately financed projects. This briefing examines project stages, reverse-osmosis energy use, water-purchase agreements and delivery risks.'
  zh='沙特淡化水已签约能力超过每日1,000万立方米，私营项目投资累计560亿里亚尔。本文拆解项目阶段、反渗透能耗、购水协议与交付风险。'
  tags='#Desalination #SaudiArabia #WaterInfrastructure'
 elif r['path']=='catl-global-2026.html':
  en='CATL reported H1 2026 overseas revenue of RMB87.1bn, up 42.35%, with a 29.97% overseas gross margin. Its Debrecen cell plant entered trial operations in September. The briefing separates trial production from planned capacity and examines the next proof points: customer qualification, yield and returns.'
  zh='宁德时代2026年上半年境外收入871.29亿元，同比增长42.35%，境外毛利率29.97%。德布勒森电芯厂于9月启动试运行；规划产能不等于当前产量。'
  tags='#CATL #ChinaGoingGlobal #Battery'
 elif r['path']=='us-manufacturing-orders-2026.html':
  en='U.S. factory orders edged up 0.1% in August, while manufacturing output fell 0.3%. Nondefense capital-goods orders excluding aircraft rose 1.6%, but capacity utilization remained below its long-run average. This is an uneven demand signal, not proof of a broad production boom.'
  zh='美国2026年8月工厂订单环比增长0.1%，制造业产出下降0.3%；非国防、除飞机资本品订单增长1.6%。订单回升尚未全面传导为产出增长。'
  tags='#USManufacturing #FactoryOrders #MarketBrief'
 elif r['path']=='xcmg-global-2026.html':
  en='XCMG reported H1 2026 overseas revenue of RMB30.9bn, 50.48% of group revenue and up 21.03%. Attributable net profit fell 9.09%, while finance costs swung with foreign-exchange losses. The briefing looks at local service, profit conversion and the limits of the company’s disclosures.'
  zh='徐工机械2026年上半年境外收入309.17亿元，占总收入50.48%，同比增长21.03%；归母净利润下降9.09%，汇兑影响推高财务费用。'
  tags='#XCMG #ChinaGoingGlobal #Machinery'
 elif r['path']=='us-datacenter-power-2026.html':
  en='U.S. data-center electricity demand is rising, but forecasts are not firm loads or supplier orders. This briefing separates modeled scenarios from reported estimates and examines grid interconnection, transmission and project execution.'
  zh='美国数据中心用电预测不等于已落地负荷或供应商订单。本文拆解情景预测、并网、输电和项目执行。'
  tags='#DataCenters #PowerGrid #USMarket'
 elif r['path']=='asean-cooling-market-2026.html':
  en='Southeast Asia’s residential air-conditioner stock is projected to triple by 2035, but national markets differ in efficiency rules, affordability, grid capacity and service networks. This briefing maps the opportunity and its execution constraints.'
  zh='东南亚住宅空调存量预计到2035年增至三倍，但各国能效规则、购买力、电网和售后条件差异显著。'
  tags='#SoutheastAsia #Cooling #MarketEntry'
 elif r['path']=='eu-ev-market-2026.html':
  en='Europe’s EV transition is accelerating, but market share depends on how powertrains and registrations are defined. This briefing separates battery-electric vehicles from the broader mix and examines trade rules, country-level demand and local execution.'
  zh='分析欧盟电动车市场时，需先区分纯电与其他动力类型，再看贸易规则、国别需求和本地执行。'
  tags='#EuropeanAuto #MarketEntry #ChinaGoingGlobal'
 elif r['path']=='anker-global-2026.html':
  en='Anker Innovations reported H1 2026 revenue growth and a high overseas revenue share. This briefing examines the company’s region and channel disclosures alongside R&D, inventory, receivables and cash conversion.'
  zh='本文根据安克创新2026年半年报梳理海外收入、区域与渠道结构，并关注研发、库存、应收账款和现金回收。'
  tags='#Anker #ChinaGoingGlobal #ConsumerTech'
 elif r['path']=='haier-global-2026.html':
  en='Haier Smart Home’s H1 2026 disclosures point to a model built on regional brands, localized products and supply-chain capabilities. The briefing reviews regional growth while identifying what remains unknown about profitability and returns.'
  zh='本文梳理海尔智家区域收入、本地产品与供应链布局，并指出地区盈利和投资回报仍缺少完整披露。'
  tags='#Haier #ChinaGoingGlobal #GlobalBusiness'
 elif r['path']=='byd_global_2026.html':
  en='BYD’s overseas growth is moving beyond exports. This briefing examines whether local manufacturing, product adaptation, R&D and service networks can turn shipments into durable operations, separating company disclosures from unproven outcomes.'
  zh='比亚迪全球化的重点正从出口销量延伸到本地制造、产品适配、研发和服务网络；本文区分公司披露与尚待验证的经营结果。'
  tags='#BYD #ChinaGoingGlobal #GlobalBusiness'
 elif r['path']=='mexico-auto-north-america-2026.html':
  en='Mexico produced 301,803 light vehicles and exported 277,369 in September 2026; both fell year over year, while domestic sales rose 7.9%. The three series tell different stories. USMCA negotiations matter as context, but INEGI does not attribute the monthly decline to them.'
  zh='墨西哥2026年9月轻型汽车生产和出口同比下降，国内销量增长7.9%。三组数据方向不同；USMCA谈判是背景，INEGI并未将单月下降归因于谈判。'
  tags='#Mexico #NorthAmerica #Automotive'
 elif r['path']=='gree-global-2026.html':
  en='Gree’s overseas core-business revenue fell 21.98% in H1 2026 to RMB12.744bn. The company says own brands made up 70% of exports and reported growth in parts of Europe. Those pockets of progress have not reversed the overall decline.'
  zh='格力上半年海外主营收入下降21.98%；公司称自主品牌占出口总额七成，部分欧洲市场增长，但还未扭转整体收缩。'
  tags='#Gree #ChinaGoingGlobal #ConsumerAppliances'
 else:
  en='A source-led briefing on '+r['title']+'. Read the full analysis for the evidence, market context, assumptions and risks.'
  zh=r['description']
  tags='#GlobalBusiness #MarketResearch'
 if r['path']=='us-aircraft-mro-workforce-2026.html':
  xcopy='FAA mechanic certificates hit 11,100+ in 2025, but certification is not employment. School seats, practical experience and retention still constrain aviation maintenance capacity. '+tracked+' #AviationMaintenance'
 elif r['path']=='sinovac-global-h1-2026.html':
  xcopy='Sinovac H1 2026 overseas revenue +82.3% to US$66.5m; total sales +12.9%, but net loss was US$91.4m. Product registrations are expanding; profitability remains unproven. '+tracked+' #ChinaGoingGlobal'
 elif r['path']=='eu-steel-import-rules-2026.html':
  xcopy='EU steel imports now face separate quota and traceability checks. The 50% duty applies only after the relevant quota is exhausted; melt-and-pour evidence has been required since 1 Oct. CBAM is separate. '+tracked+' #EUTrade #Steel'
 elif r['path']=='hangcha-thailand-manufacturing-2026.html':
  xcopy='Hangcha H1 revenue +8.65% to RMB10.10bn; company-reported overseas revenue +12.69% in USD terms. Its Thailand plant opened in June; 10,000 units/year is a 2028 target, not current output. '+tracked+' #ChinaGoingGlobal'
 elif r['path']=='us-semiconductor-market-2026.html':
  xcopy='U.S. firms held 53.4% of global chip sales in 2025; Q3 2026 global sales reached US$517.7bn. Announced investment is not operating capacity. '+tracked+' #Semiconductors'
 elif r['path']=='sanhua-global-q3-2026.html':
  xcopy='Sanhua H1 2026 overseas sales fell 2.2% to RMB7.05bn; 9M group revenue rose, attributable profit fell. Regional operating profit is not disclosed. '+tracked+' #ChinaGoingGlobal'
 elif r['path']=='thailand-ev-market-2026.html':
  xcopy='Thailand BEV registrations +95% in Jan–Sep 2026; passenger BEV exports were 13,002 units. Overall vehicle exports fell 4.9%, with pickups still 61.2% of exports. '+tracked+' #ElectricVehicles'
 elif r['path']=='geely-global-q3-2026.html':
  xcopy='Geely 9M 2026 sales +3%, revenue +13%, HKFRS profit +7%; company-defined core profit +41%. October exports: 107,153. Overseas profitability remains undisclosed. '+tracked+' #ChinaGoingGlobal'
 elif r['path']=='thailand-medical-devices-market-2026.html':
  xcopy='Thailand medtech: 2025 imports fell 1.4%; H1 2026 imports and exports both declined. Production is stronger in selected consumables, while advanced equipment still relies on imports. '+tracked+' #MedicalDevices'
 elif r['path']=='yofc-global-q3-2026.html':
  xcopy='YOFC 9M 2026 revenue +86.1%; overseas revenue share >40% in FY25 and H1 2026. Q3 is unaudited; regional profit remains undisclosed. '+tracked+' #ChinaGoingGlobal'
 elif r['path']=='eu-sustainable-aviation-fuel-market-2026.html':
  xcopy='EASA: EU SAF was 2.79% of supplier-reported fuel in 2025 vs a 2% mandate. 85% of feedstocks came from outside the EU; SAF reference prices were ~3x conventional jet fuel. '+tracked+' #AviationFuel'
 elif r['path']=='lenovo-global-q1-2026-2027.html':
  xcopy='Lenovo Q1 FY26/27: revenue +43%; AI revenue US$9.3bn. Operating expenses +123%; HKFRS attributable loss US$609m vs US$1.075bn adjusted profit. Metrics differ. '+tracked+' #Lenovo'
 elif r['path']=='north-america-battery-market-2026.html':
  xcopy='U.S. grid batteries reached nearly 52 GW by Jun 2026; co-located storage topped 16% of new utility solar through Sep. Demand forecasts are not orders. '+tracked+' #BatteryStorage'
 elif r['path']=='jinko-global-q3-2026.html':
  xcopy='Jinko Q3 2026: module shipments −25% y/y, gross margin 12.3% vs 4.2% in Q2; net loss remains. Overseas shipments ~70%. '+tracked+' #Solar'
 elif r['path']=='latin-america-copper-market-2026.html':
  xcopy='Latin America copper: Chile Jan–Sep output fell 8.5%, Peru’s Jan–Jul production index rose 2.14%. Different measures; projects are not near-term supply. '+tracked+' #Copper #LatinAmerica'
 elif r['path']=='tcl-electronics-global-2026.html':
  xcopy='TCL Electronics H1 international TV revenue +29.6%, gross profit +70.6%, margin 18.9%. Q1–Q3 group figures remain preliminary estimates. '+tracked+' #ChinaGoingGlobal'
 elif r['path']=='north-america-transformers-market-2026.html':
  xcopy='U.S. transformer demand is up 41% since 2019, while 2024 lead times remained 1–2+ years. Qualification and standardization are key entry gates. '+tracked+' #GridInfrastructure'
 elif r['path']=='mexico-auto-north-america-2026.html':
  xcopy='Mexico Sep 2026: vehicle production and exports fell, domestic sales rose 7.9%. The three series tell different stories; USMCA is context, not a proven cause. '+tracked+' #Mexico #Automotive'
 elif r['path']=='gree-global-2026.html':
  xcopy='Gree H1 2026 overseas core revenue fell 21.98%. Own brands were 70% of exports, per company disclosure; regional growth has not reversed the overall decline. '+tracked+' #ChinaGoingGlobal'
 elif r['path']=='sungrow-global-2026.html':
  xcopy='Sungrow 2025 overseas revenue rose 48.8% to RMB54.0bn. H1 2026 group revenue fell 29.0%; local service and overseas returns remain the test. '+tracked+' #ChinaGoingGlobal'
 else:
  xcopy=en[:180]+' '+tracked
 x='https://twitter.com/intent/tweet?text='+quote(xcopy,safe='')
 if zh.startswith('中文补充：'):zh=zh[len('中文补充：'):]
 copy='\n'.join([en,zh,tracked,tags])
 li='https://www.linkedin.com/sharing/share-offsite/?url='+quote(tracked,safe='')
 fb='https://www.facebook.com/sharer/sharer.php?u='+quote(tracked,safe='')
 repost_icon='<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path d="M7 7h10l-2.5-2.5M17 7l-2.5 2.5M17 17H7l2.5 2.5M7 17l2.5-2.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
 return '<article class="share-card"><div class="eyebrow">READY TO SHARE / LINKEDIN · FACEBOOK</div><h3><a href="'+r['url']+'">'+escape(r['title'])+'</a></h3><p class="share-en">'+escape(en)+'</p><p class="share-zh">'+escape(zh)+'</p><div class="share-tags">'+escape(tags)+'</div><div class="share-actions"><button type="button" class="action repost-action" aria-label="Repost" title="Repost / copy bilingual post" data-copy-text="'+escape(copy,quote=True)+'">'+repost_icon+'</button><a class="share-link" target="_blank" rel="noopener noreferrer" href="'+li+'">LinkedIn ↗</a><a class="share-link" target="_blank" rel="noopener noreferrer" href="'+fb+'">Facebook ↗</a><a class="share-link" target="_blank" rel="noopener noreferrer" href="'+x+'">X ↗</a></div><span class="copy-status" data-copy-status role="status" aria-live="polite"></span></article>'

def share_section(industry_path,company_path,by):
 industry=by.get(industry_path); company=by.get(company_path)
 if not industry or not company or industry.get('qualityScore',0)<70 or company.get('qualityScore',0)<70:return ''
 return '<section class="share-section" id="latest"><div class="section-head"><div><div class="eyebrow">GLOBAL BRIEFINGS / SHARE & READ</div><h2>Start with the signal. Share the full story.</h2></div><span>English first · bilingual summaries</span></div><div class="share-grid">'+share_card(industry,'industry')+share_card(company,'company')+'</div><p class="share-help">Use the repost icon to copy a bilingual post, then share it on your platform. / 点击 repost 图标复制双语文案，再自行发布。</p></section>'

def intro(label,title,desc):return f'<div class="page-intro"><div class="eyebrow">{label}</div><h1>{title}</h1><p>{desc}</p></div>'
def desk_tiles():
 entries=[
  ('SOUTHEAST ASIA / COOLING','东南亚空调市场','需求增长、能效规则与本地运营。','/asean-cooling-market-2026.html'),
  ('LATIN AMERICA / MACHINERY','三一南美市场','经销网络、设备服务与本地执行。','/reports/sany-south-america/index.html'),
  ('AI / OPERATIONS','企业AI与流程转型','从业务流程和数据基础评估落地条件。','/aierp.html'),
  ('U.S. DATA / MARKET ATLAS','美国市场观察','指数、利率、就业与GDP放在同一条线上。','/mk/'),
  ('E-INVOICING / KNOWLEDGE SERIES','电子发票专题','从结构化数据和制度规则，读到企业系统、税务平台与交换网络如何协作。','/reports/e-invoicing/')
 ]
 tiles=''.join('<article class="desk-tile"><div class="eyebrow">'+label+'</div><h3><a href="'+href+'">'+title+'</a></h3><p>'+desc+'</p><a class="desk-cta" href="'+href+'">查看专题 →</a></article>' for label,title,desc,href in entries)
 return '<section class="research-desk"><div class="section-head"><div><div class="eyebrow">RESEARCH DESK / EXPLORE BY LENS</div><h2>五条研究线索，快速进入</h2></div><a href="/archive/">打开完整资料库 →</a></div><div class="desk-grid">'+tiles+'</div></section>'

def topic_cards():return ''.join(f'<article class="topic"><span class="number">0{i+1}</span><h3><a href="/topics/{slug}/">{title}</a></h3><p>{desc}</p><a class="text-link" href="/topics/{slug}/">进入研究专题 →</a></article>' for i,(slug,title,desc,cat,paths) in enumerate(TOPICS))

def global_feature_paths(records):
 """Prioritize reports changed in the last 21 days; otherwise rotate evergreen picks daily."""
 by={r['path']:r for r in records}
 pool=[]
 for path in FEATURED['global']+[r['path'] for r in records if r['category']=='global' and r['language'].startswith('zh')]:
  if path in by and by[path].get('qualityScore',0)>=70 and path not in pool:pool.append(path)
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
  if r.get('editorialStatus')=='archive':
   s=re.sub(r'<meta\b[^>]*name=["\']robots["\'][^>]*>', '', s, flags=re.I)
   metadata.append('<meta name="robots" content="noindex,follow">')
  if not re.search(r'<meta\b[^>]*name=["\']description["\']',s,re.I):metadata.append(f'<meta name="description" content="{escape(r["description"],quote=True)}">')
  metadata.extend([f'<link rel="canonical" href="{canonical(r["path"])}">',f'<meta property="og:title" content="{escape(r["title"],quote=True)}">',f'<meta property="og:description" content="{escape(r["description"],quote=True)}">',f'<meta property="og:url" content="{canonical(r["path"])}">','<link rel="stylesheet" href="/assets/gbi/reader.css">','<script defer src="/assets/gbi/analytics-consent.js"></script>'])
  metadata.extend(f'<link rel="alternate" hreflang="{lang}" href="{BASE+u}">' for lang,u in pairmap.get(r['path'],[]))
  schema={'@context':'https://schema.org','@type':'WebPage','name':r['title'],'url':canonical(r['path']),'inLanguage':r['language'],'isPartOf':{'@type':'WebSite','name':'Global Business Insight','url':BASE+'/'}}
  metadata.append('<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('</','<\\/')+'</script>')
  block='\n<!-- GBI metadata start -->\n'+'\n'.join(metadata)+'\n<!-- GBI metadata end -->\n'
  s=re.sub(r'</head\s*>',lambda m:block+m[0],s,count=1,flags=re.I)
  # Ensure every editorial report page loads AdSense exactly once.
  seen=False
  def dedup(m):
   nonlocal seen
   if seen:return ''
   seen=True;return m[0]
  s=re.sub(r'[ \t]*<script\b[^>]*src=["\']https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^"\']*["\'][^>]*>\s*</script>[ \t]*',dedup,s,flags=re.I)
  if not seen:
   s=re.sub(r'</head\s*>',lambda m:AD+'\n'+m[0],s,count=1,flags=re.I)
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
 body,lead_path=homepage(records,by)
 write('index.html',shell('全球商业洞察｜产业、市场与中国企业出海','全球产业与市场研究，聚焦中国企业出海、供应链、技术与区域商业变化。中文首页，右侧设英文研究专栏。','index.html',body,active='/',lang='zh-CN',og_title='全球商业洞察｜产业、市场与中国企业出海',og_desc='全球产业与市场研究，聚焦中国企业出海、供应链、技术与区域商业变化。中文首页，右侧设英文研究专栏。'))
 series_path='reports/e-invoicing/index.html'
 series_phases=[
  ('第一阶段：建立认知',[
   ('电子发票是什么？PDF 算不算？','/reports/e-invoicing/01-what-is-an-e-invoice.html'),
   ('电子发票从哪里来：从纸票、EDI 到税务数字化','/reports/e-invoicing/02-from-paper-to-digital-reporting.html'),
   ('电子发票为什么重要：效率、合规、征管与数据价值','/reports/e-invoicing/03-why-e-invoicing-matters.html'),
   ('一张电子发票的生命周期：开具、传输、接收、入账与归档','/reports/e-invoicing/04-e-invoice-lifecycle.html')]),
  ('第二阶段：解释技术路线',[
   ('电子发票的技术架构：业务系统、税务平台、服务网络如何协作',''),
   ('发票数据标准：UBL、UN/CEFACT、EN 16931 各解决什么问题？',''),
   ('传输与互联模式：点对点、EDI、平台网络和 Peppol 四角模型',''),
   ('税务监管模式：开具前审批、开具后报送、实时报告和混合模式',''),
   ('电子签名、身份认证、二维码与存证分别解决什么问题？',''),
   ('跨境互操作的难点：数据映射、税制差异、身份和本地规则','')]),
  ('第三阶段：分区域、分国家看实践',[
   ('中国：数电发票推广后，企业流程有哪些变化？',''),
   ('欧洲：ViDA 将怎样推动跨境数字报告和电子发票？',''),
   ('印度：GST e-Invoice 与 IRP 登记机制',''),
   ('新加坡：InvoiceNow、Peppol 网络与分阶段推广',''),
   ('东南亚、拉美、中东和澳大利亚：模式比较','')]),
  ('第四阶段：场景、厂商与落地',[
   ('To G、To B、To C：同样是发票，需求为什么不同？',''),
   ('制造、零售、平台经济、公共采购和跨境贸易场景',''),
   ('企业选型指南：自建、采购、平台接入分别适合什么情况？',''),
   ('电子发票厂商与服务模式：税务平台、网络运营方、软件商和集成商',''),
   ('INOSSEM 专题：目标业务问题、产品能力与企业系统协作','')])
 ]
 roadmap=''
 for phase,items in series_phases:
  rows=''.join('<li>'+('<a href="'+href+'">'+title+'</a>' if href else title)+' <small>'+('已发布' if href else '规划中')+'</small></li>' for title,href in items)
  roadmap+='<h2>'+phase+'</h2><ol>'+rows+'</ol>'
 series_body='<div class="breadcrumb"><a href="/">首页</a> / 电子发票专题</div><article class="prose"><div class="eyebrow">E-INVOICING / KNOWLEDGE SERIES</div><h1>电子发票：从一张票到数字交易基础设施</h1><p>从基础概念、数据标准和传输网络，逐步走向不同国家的监管模式、企业业务场景与实施选择。本系列面向企业财务、税务、IT、采购及出海团队；每篇分别核对适用范围、数据口径与原始来源。</p><p class="notice">第 1 至第 4 篇已发布；其余选题将逐篇核验资料后制作。</p><h2>已发布</h2><p><a class="action" href="/reports/e-invoicing/01-what-is-an-e-invoice.html">第 1 篇：电子发票是什么？PDF 算不算？ →</a></p><p>先区分可阅读的电子文件与可由系统处理的结构化发票数据，再分别观察数据格式、传输机制和当地税务规则。</p><p><a class="action" href="/reports/e-invoicing/02-from-paper-to-digital-reporting.html">第 2 篇：电子发票从哪里来：从纸票、EDI 到税务数字化 →</a></p><p>沿着纸面凭证、EDI、共同标准、互联网络与税务报告，理解全球电子发票如何逐层演进。</p><p><a class="action" href="/reports/e-invoicing/03-why-e-invoicing-matters.html">第 3 篇：电子发票为什么重要：效率、合规、征管与数据价值 →</a></p><p>结合企业调查、欧盟政策评估与秘鲁研究，区分结构化数据的价值机制、观察到的结果和落地限制。</p><p><a class="action" href="/reports/e-invoicing/04-e-invoice-lifecycle.html">第 4 篇：一张电子发票的生命周期：开具、传输、接收、入账与归档 →</a></p><p>追踪交易证据如何变成发票，区分技术回执、监管确认、买方审批、入账、付款和归档，并处理异常与证据留存。</p>'+roadmap+'<h2>编辑说明</h2><p>国家政策和生效日期会变化。涉及现行要求的文章将标注核对日期，并优先引用税务机关、监管机构、标准组织及官方网络资料。本文系列规划不是法律或税务意见。</p></article>'
 write(series_path,shell('电子发票专题：从一张票到数字交易基础设施','电子发票系列：结构化数据、全球标准、传输网络、区域规则与企业落地。','reports/e-invoicing/index.html',series_body,active='/category/digital/',ads=False))
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
  archive_count=sum(1 for r in records if r.get('editorialStatus')=='archive')
  low_quality=sum(1 for r in records if r.get('qualityScore',100)<70)
  active_count=len(records)-archive_count
  body=intro('RESEARCH ARCHIVE','报告目录','通过70分编辑门槛并纳入研究主题的内容出现在首页与栏目。档案保留旧页面地址供查阅，不作为当前研究展示。')+f'<div class="archive-rule"><strong>归档规则 / Editorial threshold</strong><p>低于70分的页面，以及不属于当前研究栏目范围的演示、旧方案和其他历史内容，均从首页、主题栏目、默认搜索结果和站点地图移出；旧地址仍可直接打开。评分检查文章完整度、论证结构、来源与日期口径、结论和风险说明。自动评分用于统一筛查，不能替代事实核验。档案现有 {archive_count} 个页面，其中 {low_quality} 个低于70分；当前研究栏目有 {active_count} 篇。</p></div><form class="search-form" data-search-form role="search"><label>搜索报告<input type="search" name="q" placeholder="例如：仓储、工程机械、ERP" autocomplete="off"></label><label>主题<select name="category"><option value="">当前研究</option>{options}</select></label><button class="action" type="submit">搜索</button></form><p class="search-status" data-search-status aria-live="polite">当前研究 {active_count} 篇 · 档案 {archive_count} 篇 · 第 {n} / {pages} 页</p><div class="collection" data-search-results>'+''.join(card(r) for r in archive_records[(n-1)*48:n*48])+'</div><button type="button" class="search-more" data-search-more hidden>显示更多结果</button><nav class="pagination" data-pagination aria-label="目录分页">'+pagination+'</nav><noscript><p>当前显示静态目录。可通过分页继续浏览全部资料；关键词筛选需要启用JavaScript。</p></noscript>'
  write(path,shell('报告目录'+('' if n==1 else f' · 第{n}页'),'查找全球商业洞察的产业、出海、数字化与历史专题资料。',path,body,active='/archive/',ads=False))
 info={
 'about':('关于全球商业洞察','关于网站的内容方向与使用方式。','''<p>Global Business Insight（全球商业洞察）围绕产业与供应链、企业出海、AI与数字化整理专题资料，并提供美国市场与宏观数据工具。</p><h2>我们希望解决什么问题</h2><p>帮助中文商业读者理解行业背景、比较企业与市场，并找到继续研究的线索。英文精选提供已有英文报告的独立入口。</p><h2>怎样使用资料库</h2><p>从专题页建立阅读顺序，也可以在报告目录中搜索具体行业或公司。历史报告保留原有地址与内容，可能包含过时信息、估计或预测。请结合原始来源与当前情况使用。</p><p>本站不是实时新闻终端，也不提供个性化投资、法律或税务服务。关于来源、AI辅助与更正方式，请阅读<a href="/editorial/">编辑与来源标准</a>。</p><h2>广告与支持</h2><p>部分页面展示Google AdSense广告，广告收入支持网站维护。广告展示不代表本站对广告产品或观点的认可。</p>'''),
 'editorial':('编辑与来源标准','了解历史资料、来源核验、AI辅助与纠错方式。','''<p>读者应能够区分文章中的可核验事实、作者分析、估计和情景预测。以下是本站整理和维护内容时采用的标准。</p><h2>70分编辑门槛</h2><p>主题栏目和首页只展示自动评估达到70分的文章；未达门槛的原文保留在报告目录的档案中。评分从完整度与篇幅（30分）、论证与结构（25分）、证据与可追溯性（30分）、表达清晰度（15分）四部分计算。系统检查标题、分节、有效段落、摘要/结论、风险说明、外部来源、资料日期和可量化数据，并扣除常见套话。它用于统一初筛，无法判断所有事实真伪、来源权威性或论证原创性；编辑仍应核对原始来源。</p><h2>历史资料的状态</h2><p>本站保留不同时期的报告。增加导航、调整样式或重新编排专题，不代表原文事实已经重新核验，也不会被描述为研究内容更新。资料日期与范围以正文为准；缺少出处的数字应作为待核验信息。</p><h2>来源与数据</h2><ul><li>优先引用统计机构、监管机构、公司公告、年报和原始研究。</li><li>标明观察期间、单位、地区、统计口径和来源链接。</li><li>区分实际值、估计值和预测值，预测应解释假设。</li><li>产品、法律和政策内容需要确认版本、适用地区及有效日期。</li></ul><h2>AI辅助与责任</h2><p>内容整理、研究初稿、翻译和交互页面可能使用AI辅助。AI生成本身不是事实依据；关键结论应回到可核验材料。不将自动生成内容冒充实地调查或具名专家审查。</p><h2>更新与纠错</h2><p>内容发生实质修订时，应说明变更内容。读者发现问题，可通过<a href="/contact/">联系与纠错</a>提供文章地址、具体段落和参考来源。</p>'''),
 'privacy':('隐私与广告说明','网站广告、第三方资源、邮件订阅与浏览器本地存储说明。','''<p>本说明适用于Global Business Insight网站及其工具。更新日期：2026年10月21日。</p><h2>Google广告与第三方服务</h2><p>本站部分页面使用Google AdSense。Google及其他第三方广告供应商可能使用Cookie，根据您之前访问本站或其他网站的情况展示广告；Google的广告Cookie可使其及合作伙伴根据浏览活动投放广告。广告服务也可能使用网络信标、IP地址和设备信息。</p><p>您可以访问<a href="https://myadcenter.google.com/">Google广告设置</a>管理个性化广告，或访问<a href="https://optout.aboutads.info/">第三方广告退出工具</a>了解参与供应商的选择。更多信息见<a href="https://policies.google.com/technologies/partner-sites">Google在合作网站上使用数据的说明</a>。退出个性化广告不一定意味着停止所有广告或第三方请求。</p><h2>访问统计</h2><p>本站使用 Google Analytics 4（GA4）分析网站访问情况，但只有在你点击“允许统计”后才加载统计标签。GA4 会记录页面浏览、来源渠道、设备与浏览器类别及大致地区，以帮助我们判断哪些内容有效；本站不会通过该标签收集表单中的姓名或邮箱。Google 说明，GA4 在收集时使用 IP 推断地理位置，随后在数据写入前丢弃 IP 地址。允许后，GA4 会在浏览器中使用分析 Cookie 区分浏览器和访问会话。你可随时点击页面左下角“隐私设置”撤回选择；撤回后不会再发送新的 GA4 统计请求，并会清除可访问的 GA Cookie。统计数据由 Google 处理，详情见<a href="https://support.google.com/analytics/answer/11598602?hl=en-19">GA4 地区数据说明</a>和<a href="https://support.google.com/analytics/answer/6004245?hl=en-GB">Google Analytics 数据保护说明</a>。</p><h2>页面资源与托管</h2><p>网站由GitHub Pages托管。部分历史报告从字体、图表或其他资源提供方加载内容；这些请求可能向提供方传递IP地址和浏览器信息。相关服务按其自身隐私政策处理数据。参阅<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub隐私声明</a>。</p><h2>工具与本地记录</h2><p>英语训练的学习记录与笔记保存在当前浏览器的本地存储中，不通过该工具上传到本站服务器。录音功能需由您授权麦克风，录音在页面内临时保存，可自行下载。清除浏览器数据可能删除学习记录，请先导出备份。市场工具也可能保存界面偏好。</p><h2>邮件订阅</h2><p>订阅表单当前只在浏览器内生成邮件草稿或可复制的申请内容，不向本站专用服务器上传信息。站长收到邮件后会手动维护订阅名单，并仅用于发送读者选择的文章更新；可随时回复退订。Brevo尚未接入，接入后会更新本说明。</p><h2>搜索与反馈</h2><p>报告目录搜索在浏览器内进行，不将搜索词发送到本站专用搜索服务器。目录加载及访问仍会产生正常网页请求。通过GitHub提交的问题会公开显示，请勿填写密码、付款资料或其他敏感信息。</p><h2>您的选择</h2><p>您可以通过浏览器管理Cookie、本地存储及麦克风权限，通过广告提供方管理广告偏好。适用的广告隐私提示与选择以实际显示的界面为准。如需反馈隐私问题，请使用<a href="/contact/">联系入口</a>。</p>'''),
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
 status_by_path={r['path']:r.get('editorialStatus') for r in records}
 for p in sorted(ROOT.rglob('*.html')):
  path=p.relative_to(ROOT).as_posix()
  if path.startswith(('.git/','_site/')) or path=='404.html' or path in aliases or status_by_path.get(path)=='archive':continue
  text=p.read_text(errors='replace')
  if not re.search(r'<title[^>]*>\s*[^<\s]',text,re.I):continue
  locations.append(canonical(path))
 write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+escape(u)+'</loc></url>\n' for u in sorted(set(locations)))+'</urlset>\n')
 robots='User-agent: *\nAllow: /\n\nSitemap: '+BASE+'/sitemap.xml\n';write('robots.txt',robots);write('robot.txt','# Legacy filename. Crawlers should use /robots.txt.\n'+robots)
 low_count=sum(1 for r in records if r.get('qualityScore',100)<70)
 archive_count=sum(1 for r in records if r.get('editorialStatus')=='archive')
 print(f'Built portal, {len(records)} catalog entries ({low_count} below 70; {archive_count} archived), {pages} archive pages and {len(set(locations))} sitemap URLs.')
if __name__=='__main__':generate()
