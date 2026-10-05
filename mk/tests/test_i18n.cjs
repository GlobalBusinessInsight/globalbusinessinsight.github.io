const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'i18n.js'), 'utf8');
function boot(languages, saved, blocked = false) {
  const context = vm.createContext({navigator: {languages}, localStorage: {
    getItem() { if (blocked) throw Error('Storage blocked'); return saved; },
    setItem(key, value) { if (blocked) throw Error('Storage blocked'); saved = value; }
  }});
  vm.runInContext(source, context);
  return {api: context.MarketI18n, navigator: context.navigator, saved: () => saved};
}
for (const [languages, expected] of [
  [['zh-CN'], 'zh'], [['zh-TW'], 'zh'], [['zh-HK', 'en-US'], 'zh'],
  [['en-GB', 'zh-CN'], 'en'], [['fr-FR', 'zh-Hans'], 'zh'],
  [['fr-FR'], 'en'], [[], 'en']
]) assert.equal(boot(languages).api.language, expected, languages.join(','));
const manual = boot(['zh-CN'], 'en');
assert.equal(manual.api.language, 'en');
manual.api.setPreference('zh');
assert.equal(manual.saved(), 'zh');
assert.equal(boot(['en-US'], manual.saved()).api.language, 'zh');
manual.api.setPreference('auto');
manual.navigator.languages = ['en-US'];
manual.api.syncBrowserLanguage();
assert.equal(manual.api.language, 'en');
assert.equal(manual.saved(), 'auto');
assert.equal(boot(['zh-TW'], 'invalid').api.language, 'zh');
const blocked = boot(['zh-CN'], null, true);
blocked.api.setPreference('en');
assert.equal(blocked.api.language, 'en', 'Switching still works with blocked storage');
assert.equal(blocked.api.t('{count} 个月', {count: 24}), '24 months');
// All tagged static copy and dynamic translation/notification keys must have English text.
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(root, 'app.js'), 'utf8');
const keys = [
  ...Array.from(html.matchAll(/data-i18n(?:-aria-label|-content)?="([^"]+)"/g), m => m[1]),
  ...Array.from(app.matchAll(/(?:\bt|\bnotify)\('([^']*)'/g), m => m[1])
];
for (const key of keys) {
  assert.ok(!/[\u4e00-\u9fff]/u.test(blocked.api.t(key)), `Missing English translation: ${key}`);
}
console.log('Language checks passed: browser preference order, Chinese variants, English fallback, persistence, blocked storage, and translation coverage.');
