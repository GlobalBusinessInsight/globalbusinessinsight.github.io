'use strict';

// Manual subscription flow for the static GitHub Pages site. It never sends
// data to a third-party service: it prepares an email draft or copies it.
(()=>{
 const form=document.querySelector('[data-manual-subscribe]');
 if(!form)return;
 const status=form.querySelector('[data-subscribe-status]');
 const destination=form.dataset.destination||'';
 const copy=async text=>{
  if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(text);return true;}
  const area=document.createElement('textarea');area.value=text;area.setAttribute('readonly','');area.style.position='fixed';area.style.opacity='0';document.body.appendChild(area);area.select();const ok=document.execCommand('copy');area.remove();return ok;
 };
 form.addEventListener('submit',async event=>{
  event.preventDefault();
  const data=new FormData(form);
  if(String(data.get('website')||'').trim())return;
  const email=String(data.get('email')||'').trim();
  const topics=[...form.querySelectorAll('input[name="topics"]:checked')].map(input=>input.parentElement.textContent.trim());
  if(!email||!topics.length){status.textContent='请填写邮箱并至少选择一个板块。';return;}
  const subject='GBI 订阅申请';
  const body=['您好，我想订阅 Global Business Insight 的文章更新。','',`邮箱：${email}`,`感兴趣的板块：${topics.join('、')}`,'','我同意接收所选板块的文章更新，并可随时回复邮件退订。'].join('\n');
  if(destination){
   location.href=`mailto:${destination}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
   status.textContent='已打开邮件客户端，请检查收件地址后发送。';
   return;
  }
  try{
   const copied=await copy(`收件人：网站管理员\n主题：${subject}\n\n${body}`);
   status.textContent=copied?'订阅申请已复制，请粘贴到你的邮件客户端发送。':'请复制页面上的订阅信息，使用邮件客户端发送。';
  }catch{status.textContent='请使用邮件客户端发送订阅申请。';}
 });
})();
