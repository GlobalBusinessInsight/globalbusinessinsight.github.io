'use strict';
// Static translations are text only; data and calculation keys stay language-neutral.
(() => {
const english = {
  "Market Atlas · 美股与宏观观察": "Market Atlas · US Markets & Macro",
  "20 年美股与美国宏观数据月度对比。自由选择时间范围，查看利率、非农、GDP、国债收益率与主要指数。": "Compare 20 years of US markets and macroeconomic data by month. Explore interest rates, payrolls, GDP, Treasury yields and major indexes across any date range.",
  "Market Atlas 首页": "Market Atlas home",
  "研究工作台": "RESEARCH DESK",
  "市场与宏观": "Markets & macro",
  "月度数据": "Monthly data",
  "数据与口径": "Sources & methods",
  "跨越周期，观察关联": "Explore connections across cycles",
  "美国市场": "US markets",
  "宏观研究": "Macro research",
  "月度观察": "Monthly view",
  "↻ 检查更新": "↻ Check updates",
  "美股与宏观观察": "US Markets & Macro",
  "在同一条时间线上，比较市场表现与经济周期。": "Compare market performance and economic cycles on one timeline.",
  "正在读取数据": "Loading data",
  "载入历史记录…": "Loading history…",
  "选择时间范围": "Select date range",
  "快捷时间范围": "Quick date ranges",
  "1 年": "1Y",
  "3 年": "3Y",
  "5 年": "5Y",
  "10 年": "10Y",
  "20 年": "20Y",
  "全部": "All",
  "起始": "From",
  "结束": "To",
  "应用": "Apply",
  "持续更新至今": "Follow latest month",
  "结束月份自动延伸到当前月份": "End date follows the current month",
  "每分钟检查新数据": "Checking for updates every minute",
  "读取月度历史数据": "Loading monthly history",
  "按观察期对齐": "Aligned by observation period",
  "最新修订值": "Latest revised values",
  "所选月份概览": "Selected month overview",
  "市场与宏观走势": "Market & macro trends",
  "区间起点 = 100 · 点击图表查看当月": "Start of range = 100 · Click chart to inspect a month",
  "相对表现": "Relative performance",
  "月度涨跌": "Monthly returns",
  "叠加指标": "Overlay",
  "联邦基金利率": "Federal funds rate",
  "10 年期国债": "10-year Treasury",
  "2 年期国债": "2-year Treasury",
  "新增非农就业": "Nonfarm payroll change",
  "实际 GDP 增速": "Real GDP growth",
  "不叠加": "None",
  "所选区间市场与宏观数据图": "Market and macro chart for the selected range",
  "宏观数据": "Macro data",
  "· 右轴": "· Right axis",
  "单月快照": "Monthly snapshot",
  "选择任意月份": "Select a month",
  "沿时间轴选择月份": "Select month on the timeline",
  "月度数据明细": "Monthly data",
  "历史市场数据取月末收盘，当月取最新已取得报价；利率与国债取月均值。空值表示尚未发布或缺失。": "Historical market values use month-end closes; the current month uses the latest available quote. Rates and Treasury yields are monthly averages. Blank values are unavailable or not yet released.",
  "↓ 导出 CSV": "↓ Export CSV",
  "月份": "Month",
  "指数点位": "Index points",
  "标普 500": "S&P 500",
  "美元": "USD",
  "联邦基金": "Fed funds",
  "新增非农": "Payroll change",
  "千人": "Thousand people",
  "季环比年化 %": "Annualized QoQ %",
  "2 年国债": "2Y Treasury",
  "10 年国债": "10Y Treasury",
  "GDP 季度值映射到所属季度的三个月，未做月度插值。": "Quarterly GDP values repeat across their three months; no monthly interpolation is applied.",
  "最新月份在前": "Newest month first",
  "理解数据，才能理解比较。": "Understand the data behind the comparison.",
  "同一个观察期，不代表当时已知。宏观数据会滞后发布并修订，本页适合历史观察，不能作为无前视偏差的回测数据。": "The same observation period does not mean the data was known at that time. Macro data is released with a lag and revised. This page is for historical exploration, not backtesting without look-ahead bias.",
  "数据来源与计算口径": "Sources & calculations",
  "利率：": "Rates: ",
  "月均有效利率。国债：": "monthly average effective rate. Treasuries: ",
  "月均收益率，非债券价格。非农：": "monthly average yields, not bond prices. Payrolls: ",
  "季调就业总量的月度差值，单位千人。": "month-over-month change in seasonally adjusted employment, in thousands.",
  "GDP：": "GDP:",
  "实际 GDP 季环比年化增速；快照同时展示": "annualized quarter-over-quarter real GDP growth; the snapshot also shows",
  "名义总量（年率）。Nasdaq 为综合指数 ^IXIC，标普为 ^GSPC；QQQ 为 ETF。": "nominal GDP at an annual rate. Nasdaq is the Composite (^IXIC), S&P 500 is ^GSPC, and QQQ is an ETF. ",
  "日收盘聚合为月末值；不计现金分红，不代表总回报。": "daily closes are aggregated to month-end values. Cash dividends are excluded; these are not total returns.",
  "更新、历史保存与数据状态": "Updates, history & source status",
  "GitHub Actions 每小时抓取一次，并保存完整历史文件；网页每分钟检查新版本。不是逐笔或分钟行情。当前月份使用最新已取得的常规交易时段报价（可能有延迟），没有可用报价时使用已完成交易日收盘，标记为“月内暂值”。任务可能延迟；抓取失败保留旧值并显示状态。源接口可能限流，Yahoo 接口无可用性保证。": "GitHub Actions fetches data hourly and saves the full history; this page checks for a new version every minute. This is not tick or minute-level streaming. The current month uses the latest available regular-session quote (which may be delayed), or the latest completed trading-day close if no quote is available, and is marked provisional. Scheduled jobs may be delayed. Failed fetches retain previous values and show their status. Sources may rate-limit requests; Yahoo does not guarantee API availability.",
  "月度数据观察 · 非投资建议": "Monthly data exploration · Not investment advice",
  "回到顶部 ↑": "Back to top ↑",
  "点": "Points",
  "数据文件格式不正确": "Invalid data file format",
  "数据文件缺少有效的 {series}": "Missing valid data for {series}",
  "{count} 个来源更新失败": "{count} sources failed to update",
  "数据快照待更新": "Snapshot needs updating",
  "历史数据已载入": "Historical data loaded",
  "抓取于 {time} 美东": "Fetched {time} ET",
  "截至 {date} · {status} · {fetched}": "Through {date} · {status} · {fetched}",
  "抓取成功": "Fetch successful",
  "保留旧值": "Previous values retained",
  "部分来源本次更新失败，已保留上次有效历史数据。请查看下方“更新、历史保存与数据状态”。": "Some sources failed to update. Previous valid history has been retained. See “Updates, history & source status” below.",
  "这是保存的历史快照，最近抓取已超过 48 小时。部署并启用定时更新后将自动取得新数据。": "This saved snapshot was last fetched over 48 hours ago. Deploy the site and enable scheduled updates to fetch new data automatically.",
  "时间范围已固定": "Date range is fixed",
  "{start} — {end} · {count} 个月": "{start} — {end} · {count} months",
  "{count} 个月度观察点": "{count} monthly observations",
  "较上月收盘涨跌 % · 点击图表查看当月": "Change from prior month close % · Click chart to inspect a month",
  "该月尚无已发布数据": "No published data for this month",
  "月内暂值 · {time} 美东": "Provisional · {time} ET",
  "观察期 {month} · 月均": "Period {month} · Monthly average",
  "收盘日期 {date}": "Close date {date}",
  "较上月 · {month}": "vs. prior month · {month}",
  "{value} 千人": "{value} thousand",
  "名义 GDP · 年率": "Nominal GDP · Annual rate",
  "{value} 万亿美元": "US$ {value} trillion",
  "2 年国债收益率": "2-year Treasury yield",
  "10 年国债收益率": "10-year Treasury yield",
  "该月市场数据为最新已取得报价或收盘的月内暂值，并非实时推送。": "Market values for this month are provisional, based on the latest available quote or close, not a live stream. ",
  "GDP 对应 {quarter}，增速为季环比年化。缺失项不使用其他月份的值填充。": "GDP refers to {quarter}; growth is annualized quarter over quarter. Missing values are not filled from other months.",
  "起点 = 100": "Start = 100",
  "月涨跌 %": "Monthly return %",
  "此区间无可绘制的市场数据": "No market data to plot in this range",
  "{start} 至 {end}，{mode}。完整数值见月度明细表。": "{start} to {end}: {mode}. Full values are available in the monthly data table.",
  "归一化市场走势": "indexed market performance",
  "市场月度涨跌": "monthly market returns",
  "（季度）": " (quarterly)",
  "未叠加指标": "No overlay",
  "{count} 个月": "{count} months",
  "查看 {month} 快照": "View snapshot for {month}",
  "月内暂值": "Provisional",
  "请选择有效的起止月份，起始月份不能晚于结束月份。": "Choose valid start and end months. The start cannot be later than the end.",
  "可选范围为 {start} 至 {end}。": "Available range: {start} to {end}.",
  "快照月份需要位于当前选择的时间范围内。": "The snapshot month must be within the selected date range.",
  "本地快照 · 部署后自动更新": "Local snapshot · Updates after deployment",
  "当前为本地文件模式，正在展示随附历史快照。部署到 GitHub Pages 后可检查线上数据更新。": "This local file shows the bundled historical snapshot. Deploy to GitHub Pages to check for online updates.",
  "已检查线上数据，当前已是最新保存版本。数据抓取由定时任务执行。": "Checked online data. This is the latest saved version. New data is fetched by scheduled jobs.",
  "无法检查线上更新，继续显示已保存的历史数据。": "Could not check for updates. Showing saved historical data.",
  "无法载入数据。请确认 data/history.json 和 data/history.js 已随网页一起上传。": "Could not load data. Make sure data/history.json and data/history.js were uploaded with the page.",
  "上次检查 {time} · 每分钟检查": "Last checked {time} · Checks every minute",
  "随附数据文件格式异常，正在尝试读取线上数据。": "The bundled data file is invalid. Trying to load online data.",
  "Nasdaq_点": "Nasdaq_points",
  "SP500_点": "SP500_points",
  "QQQ_USD_不含分红": "QQQ_USD_excluding_dividends",
  "联邦基金利率_%_月均": "Federal_funds_rate_%_monthly_average",
  "新增非农_千人_季调": "Payroll_change_thousands_seasonally_adjusted",
  "实际GDP增速_%_季环比年化": "Real_GDP_growth_%_annualized_QoQ",
  "名义GDP_十亿美元_年率": "Nominal_GDP_USD_billions_annual_rate",
  "实际GDP_十亿2017美元_年率": "Real_GDP_2017_USD_billions_annual_rate",
  "2年国债_%_月均": "Treasury_2Y_%_monthly_average",
  "10年国债_%_月均": "Treasury_10Y_%_monthly_average",
  "GDP所属季度": "GDP_quarter",
  "Nasdaq交易日": "Nasdaq_trading_date",
  "SP500交易日": "SP500_trading_date",
  "QQQ交易日": "QQQ_trading_date",
  "Nasdaq报价时间": "Nasdaq_quote_time",
  "SP500报价时间": "SP500_quote_time",
  "QQQ报价时间": "QQQ_quote_time",
  "界面语言": "Interface language",
  "自动": "Auto"
};
const storageKey = 'market-atlas-language';
const supported = value => ['auto', 'zh', 'en'].includes(value);
function resolveLanguage(preference, languages = []) {
  if (preference === 'zh' || preference === 'en') return preference;
  // Honor the first supported language in the browser's ordered preference list.
  for (const language of languages) {
    if (/^zh(?:-|_|$)/i.test(language)) return 'zh';
    if (/^en(?:-|_|$)/i.test(language)) return 'en';
  }
  return 'en';
}
let preference = 'auto';
try { const saved = localStorage.getItem(storageKey); if (supported(saved)) preference = saved; } catch {}
const browserLanguages = () => globalThis.navigator?.languages?.length
  ? navigator.languages : [globalThis.navigator?.language || 'en'];
let language = resolveLanguage(preference, browserLanguages());
function t(key, params = {}) {
  const text = language === 'en' ? english[key] ?? key : key;
  return text.replace(/\{(\w+)\}/g, (match, name) => params[name] ?? match);
}
function apply(root = document) {
  root.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';
  root.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
  for (const attribute of ['aria-label', 'content']) {
    root.querySelectorAll(`[data-i18n-${attribute}]`).forEach(el => {
      el.setAttribute(attribute, t(el.getAttribute(`data-i18n-${attribute}`)));
    });
  }
  const selector = root.getElementById('language');
  if (selector) selector.value = preference;
}
function setPreference(value) {
  preference = supported(value) ? value : 'auto';
  try { localStorage.setItem(storageKey, preference); } catch {}
  language = resolveLanguage(preference, browserLanguages());
}
function syncBrowserLanguage() { language = resolveLanguage(preference, browserLanguages()); }
globalThis.MarketI18n = { t, apply, setPreference, syncBrowserLanguage, resolveLanguage,
  get language() { return language; }, get preference() { return preference; },
  get locale() { return language === 'zh' ? 'zh-CN' : 'en-US'; }
};
if (globalThis.document) document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';
})();
