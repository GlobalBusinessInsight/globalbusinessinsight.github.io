(function () {
  "use strict";

  const measurementId = "G-N155D97KSW";
  const storageKey = "gbi_analytics_consent_v1";
  const isEnglish = /^en\b/i.test(document.documentElement.lang || "");
  let banner;

  const styles = document.createElement("style");
  styles.textContent = `
    .gbi-privacy-choice{position:fixed;left:14px;bottom:14px;z-index:10000;border:1px solid #b7c7c0;border-radius:4px;background:#fff;color:#17363d;padding:9px 12px;font:600 13px/1.3 system-ui,sans-serif;box-shadow:0 2px 10px #17363d22;cursor:pointer}
    .gbi-consent-panel{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:10001;width:min(700px,calc(100vw - 28px));box-sizing:border-box;background:#fffdf8;border:1px solid #b7c7c0;border-top:4px solid #176b57;padding:20px 22px;box-shadow:0 8px 30px #132f3533;color:#17363d;font:15px/1.55 system-ui,sans-serif}
    .gbi-consent-panel[hidden]{display:none}
    .gbi-consent-panel h2{font:700 20px/1.25 system-ui,sans-serif;margin:0 0 8px;color:#17363d}
    .gbi-consent-panel p{margin:0 0 14px}
    .gbi-consent-panel a{color:#176b57;text-decoration:underline}
    .gbi-consent-actions{display:flex;justify-content:flex-end;gap:10px;flex-wrap:wrap}
    .gbi-consent-actions button{border:1px solid #17363d;border-radius:3px;background:#fff;color:#17363d;padding:10px 14px;font:700 14px system-ui,sans-serif;cursor:pointer}
    .gbi-consent-actions button[data-accept]{background:#17363d;color:#fff}
    .gbi-consent-panel button:focus-visible,.gbi-privacy-choice:focus-visible{outline:3px solid #d67636;outline-offset:2px}
    @media(max-width:520px){.gbi-consent-panel{bottom:10px;padding:16px}.gbi-consent-actions{display:grid;grid-template-columns:1fr 1fr}.gbi-consent-actions button{padding:10px 8px}.gbi-privacy-choice{left:10px;bottom:10px}}
  `;
  (document.head || document.documentElement).appendChild(styles);

  function loadAnalytics() {
    if (window.__gbiAnalyticsLoaded) return;
    window.__gbiAnalyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", measurementId);
    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(measurementId);
    script.onerror = function () { window.__gbiAnalyticsLoaded = false; };
    document.head.appendChild(script);
  }

  function clearAnalyticsCookies() {
    document.cookie.split(";").forEach(function (item) {
      const name = item.trim().split("=")[0];
      if (!/^_ga(?:_|$)/.test(name)) return;
      document.cookie = name + "=; Max-Age=0; path=/; SameSite=Lax";
      document.cookie = name + "=; Max-Age=0; path=/; domain=" + location.hostname + "; SameSite=Lax";
      if (location.hostname.endsWith("github.io")) {
        document.cookie = name + "=; Max-Age=0; path=/; domain=github.io; SameSite=Lax";
      }
    });
  }

  function saveChoice(choice) {
    try { localStorage.setItem(storageKey, choice); } catch (_) {}
    if (choice === "accepted") loadAnalytics();
    else clearAnalyticsCookies();
    if (banner) banner.hidden = true;
  }

  function showBanner() {
    if (!banner) return;
    banner.hidden = false;
    const accept = banner.querySelector("[data-accept]");
    if (accept) accept.focus();
  }

  function buildUi() {
    const settings = document.createElement("button");
    settings.type = "button";
    settings.className = "gbi-privacy-choice";
    settings.textContent = isEnglish ? "Privacy choices" : "隐私设置";
    settings.setAttribute("aria-label", isEnglish ? "Change analytics privacy choices" : "更改访问统计隐私选择");
    settings.addEventListener("click", showBanner);
    document.body.appendChild(settings);

    banner = document.createElement("section");
    banner.className = "gbi-consent-panel";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-labelledby", "gbi-consent-title");
    banner.setAttribute("aria-describedby", "gbi-consent-description");
    banner.innerHTML = isEnglish
      ? '<h2 id="gbi-consent-title">Help us improve this site</h2><p id="gbi-consent-description">With your permission, Google Analytics will measure visits, referring sources, approximate region, and device/browser categories. We do not send names or email addresses through this analytics tag. You can change your choice at any time in <a href="/privacy/">Privacy &amp; advertising</a>.</p><div class="gbi-consent-actions"><button type="button" data-reject>Reject analytics</button><button type="button" data-accept>Allow analytics</button></div>'
      : '<h2 id="gbi-consent-title">帮助我们改进网站</h2><p id="gbi-consent-description">获得你的同意后，Google Analytics 会统计访问量、来源渠道、大致地区及设备/浏览器类别。此统计标签不会发送姓名或邮箱。你可以随时通过<a href="/privacy/">隐私与广告说明</a>中的“隐私设置”更改选择。</p><div class="gbi-consent-actions"><button type="button" data-reject>拒绝统计</button><button type="button" data-accept>允许统计</button></div>';
    banner.hidden = true;
    banner.querySelector("[data-accept]").addEventListener("click", function () { saveChoice("accepted"); });
    banner.querySelector("[data-reject]").addEventListener("click", function () { saveChoice("rejected"); });
    document.body.appendChild(banner);
    let choice = null;
    try { choice = localStorage.getItem(storageKey); } catch (_) {}
    if (choice === "accepted") loadAnalytics();
    else if (choice !== "rejected") showBanner();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", buildUi, { once: true });
  else buildUi();
})();