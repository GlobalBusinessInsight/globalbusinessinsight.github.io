'use strict';
// Search stays in the browser. No analytics identifiers or personal data are sent.
(()=>{
 const form=document.querySelector('[data-search-form]');if(!form)return;
 const input=form.querySelector('input'),select=form.querySelector('select');
 const list=document.querySelector('[data-search-results]'),status=document.querySelector('[data-search-status]'),pages=document.querySelector('[data-pagination]');
 const more=document.querySelector('[data-search-more]');let records=null,matches=[],limit=48;
 const params=new URLSearchParams(location.search);input.value=params.get('q')||'';select.value=params.get('category')||'';
 if(select.selectedIndex<0)select.value='';
 const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 function paint(){list.innerHTML=matches.slice(0,limit).map(r=>`<article class="report"><div class="eyebrow">${escape(r.categoryLabel)}</div><h3><a href="${escape(r.url)}">${escape(r.title)}</a></h3><p>${escape(r.description)}</p><small>${escape(r.languageLabel)} · 历史资料，日期与口径见正文</small></article>`).join('')||'<p class="empty">没有找到匹配内容。试试“仓储”“ERP”或公司名称。</p>';status.textContent=`找到 ${matches.length} 篇资料，显示 ${Math.min(limit,matches.length)} 篇`;more.hidden=limit>=matches.length;}
 function search(){if(!records)return;let q=input.value.trim().toLocaleLowerCase();matches=records.filter(r=>(!select.value||r.category===select.value)&&(!q||(r.title+' '+r.description).toLocaleLowerCase().includes(q)));limit=48;pages.hidden=true;paint();const p=new URLSearchParams();if(q)p.set('q',input.value.trim());if(select.value)p.set('category',select.value);history.replaceState(null,'','/archive/'+(p.size?'?'+p:''));}
 async function load(){if(records)return;status.textContent='正在准备全文目录…';try{const response=await fetch('/assets/gbi/catalog.json');if(!response.ok)throw new Error('catalog');records=await response.json();search();}catch{status.textContent='搜索暂时不可用，仍可使用下面的分页目录。';pages.hidden=false;}}
 form.addEventListener('submit',e=>{e.preventDefault();load().then(search)});input.addEventListener('input',()=>load().then(search));select.addEventListener('change',()=>load().then(search));more.addEventListener('click',()=>{limit+=48;paint()});
 if(input.value||select.value)load();
})();

// Homepage social publishing helper: copy bilingual post text for manual publishing.
(()=>{document.addEventListener('click',async e=>{const button=e.target.closest('[data-copy-text]');if(!button)return;const card=button.closest('.share-card'),status=card&&card.querySelector('[data-copy-status]'),value=button.getAttribute('data-copy-text')||'';try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(value)}else{const area=document.createElement('textarea');area.value=value;area.setAttribute('readonly','');area.style.position='fixed';area.style.opacity='0';document.body.appendChild(area);area.select();const ok=document.execCommand('copy');area.remove();if(!ok)throw new Error('copy failed')}button.textContent='已复制 / Copied';if(status)status.textContent='文案已复制，可粘贴到 LinkedIn 或 Facebook。';window.setTimeout(()=>{button.textContent='复制双语文案'},2200)}catch{if(status)status.textContent='自动复制失败，请选择卡片文案手动复制。'}})})();
