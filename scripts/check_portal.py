#!/usr/bin/env python3
"""Release checks for generated routes, metadata, catalog, and migration integrity."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote, quote
import json, re, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self,s):
  super().__init__();self.refs=[];self.canon=[];self.ids=[];self.ads=0;self.feed(s)
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if t=='a' and 'href' in a:self.refs.append(a['href'])
  if t in ('script','img') and a.get('src'):self.refs.append(a['src'])
  if t=='link' and a.get('rel')=='stylesheet':self.refs.append(a.get('href',''))
  if t=='link' and a.get('rel')=='canonical':self.canon.append(a.get('href'))
  if t=='script' and 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' in a.get('src',''):self.ads+=1

def main():
 errors=[];catalog=json.loads((ROOT/'assets/gbi/catalog.json').read_text());paths=set()
 def require(cond,msg):
  if not cond:errors.append(msg)
 def exists(u):
  p=ROOT/unquote(urlparse(u).path).lstrip('/')
  return p.is_file() or (p/'index.html').is_file()
 for r in catalog:
  require(r['path'] not in paths,'Duplicate catalog path: '+r['path']);paths.add(r['path']);p=ROOT/r['path'];require(p.is_file(),'Missing report: '+r['path']);s=p.read_text();h=Page(s)
  require(len(h.canon)==1,'Canonical count: '+r['path']);require(h.ads<=1,'Duplicate AdSense: '+r['path']);require(s.count('id="gbi-reader"')==1,'Missing reading navigation: '+r['path'])
  for u in re.findall(r'href="(/[^"#]*)"',s.split('<!-- GBI reader start -->')[-1].split('<!-- GBI reader end -->')[0]):require(exists(u),'Broken reading link: '+u)
 require(len(catalog)>400,'Catalog unexpectedly lost reports')
 generated=[]
 for p in ROOT.rglob('*.html'):
  if '_site' in p.parts or '.git' in p.parts:continue
  s=p.read_text(errors='replace')
  if '<!-- GBI generated -->' not in s:continue
  generated.append(p);h=Page(s);require(len(h.ids)==len(set(h.ids)),'Duplicate IDs: '+str(p));require(len(h.canon)==1,'Missing canonical: '+str(p));require(h.ads<=1,'Duplicate advertising: '+str(p))
  for u in h.refs:
   if u.startswith('/') and not u.startswith('//'):require(exists(u),'Broken portal link: '+str(p.relative_to(ROOT))+' -> '+u)
  require('<h1>' in s,'Missing heading: '+str(p))
 urls=[v.text for v in ET.parse(ROOT/'sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')];require(len(urls)==len(set(urls)),'Duplicate sitemap URLs')
 for u in urls:
  require(u.startswith('https://globalbusinessinsight.github.io/'),'Wrong sitemap origin: '+u);require(exists(u),'Sitemap route missing: '+u)
 for path in paths:
  route=quote(path,safe='/');route=route.removesuffix('index.html') if path.endswith('/index.html') else route
  require('https://globalbusinessinsight.github.io/'+route in urls,'Report sitemap coverage: '+path)
 robots=(ROOT/'robots.txt').read_text();require('Disallow: /' not in robots,'Site crawling blocked');require('Allow: /' in robots,'Missing crawl permission')
 english=(ROOT/'tools/english/index.html').read_text();require('src="/app.js"' in english and 'src="/curriculum.js"' in english,'English migration asset paths');require("KEY='nj-english-v1'" in (ROOT/'app.js').read_text(),'English progress storage changed')
 require('English, Every Day' not in (ROOT/'index.html').read_text(),'Root homepage is still English app');require(not (ROOT/'index.md').exists(),'Two root homepage sources');require(not (ROOT/'about.md').exists(),'Two about page sources')
 for cn,en in [('50909us3pl.html','50909us3plen.html'),('aierp.html','aierpen.html')]:
  for path in [cn,en]:
   s=(ROOT/path).read_text();require('hreflang="zh-CN"' in s and 'hreflang="en"' in s,'Missing reciprocal language pair: '+path)
 if errors:raise SystemExit('\n'.join(errors))
 print(f'PASS: {len(catalog)} reports, {len(generated)} portal pages, {len(urls)} sitemap routes; internal links, metadata, ads, language pairs and English migration.')
if __name__=='__main__':main()
