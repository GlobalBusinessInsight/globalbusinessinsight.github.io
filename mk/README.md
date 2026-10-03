# Market Atlas · 美股与宏观观察

可直接部署到 GitHub Pages 的中文静态网页。HTML + CSS + 原生 JavaScript，无数据库、无前端构建、无浏览器密钥，也不依赖外部图表 CDN。

## 使用

直接双击 `index.html` 可浏览随附真实历史快照；检查线上更新需要 HTTP/HTTPS。

- 1 / 3 / 5 / 10 / 20 年快捷筛选、自定义起止月份（同月也支持）。
- Nasdaq 综合指数、标普 500、QQQ：起点归一化或月度涨跌比较。
- 叠加联邦基金有效利率、2/10 年期国债收益率、非农新增就业或实际 GDP 增速。
- 点击图表/明细行或选择月份，查看同月快照；支持 CSV 导出。
- 选择偏好保存在当前浏览器。数据历史保存在仓库文件，版本修订由 Git 保存。

## 发布到 github.io

1. 新建 GitHub 仓库，将**本目录内的全部文件**放到仓库根目录（不要多套一层文件夹）。务必包含隐藏目录 `.github/workflows/`。默认分支为 `main`；如果使用其他分支，修改工作流中的 `push.branches`。
2. 仓库 Settings → Pages → Build and deployment → Source 选择 **GitHub Actions**。
3. Settings → Actions → General → Workflow permissions，允许 **Read and write permissions**。若分支保护禁止自动写入，需允许 Actions 对数据文件提交，或使用不受保护的部署仓库。
4. Actions → **Update data and deploy Pages** → **Run workflow**。完成后 Pages 页面给出网站地址：`https://用户名.github.io/仓库名/`。也支持 `用户名.github.io` 根站点。
5. 自动更新在 每小时第 23 分钟（UTC） 执行。网页打开时及每分钟检查已发布的新文件。点击“检查更新”不会启动 GitHub 的抓取任务；需要立即抓取时手动运行工作流。

默认 FRED 公共 CSV 不需要密钥。如 CSV 服务限流，可申请 [FRED API key](https://fred.stlouisfed.org/docs/api/api_key.html)，在仓库 Secrets → Actions 添加 `FRED_API_KEY`；仅供更新任务使用，绝不写入网页或数据文件。Yahoo Finance 使用非官方公开 chart 接口，可能限流或变更；没有逐笔行情或接口可用性保证。

GitHub 定时任务不是精确实时服务，可能延迟；公开仓库长期无活动时定时任务可能被禁用。检查 Actions 状态，必要时手动启用。此交付包包含工作流，但在上传并启用前不会自行更新。

## 数据定义

| 内容 | 来源与口径 |
| --- | --- |
| Nasdaq | Yahoo `^IXIC`，综合指数，日收盘取每月最后有效值 |
| 标普 500 | Yahoo `^GSPC`，同上，20 年历史不受 FRED 标普仅 10 年的限制 |
| QQQ | Yahoo `QQQ`，美元收盘价，不计现金分红，不是总回报 |
| 利率 | FRED `FEDFUNDS`，联邦基金有效利率，月均，% |
| 非农 | FRED `PAYEMS`，季调非农就业总量（月）作一阶差分，千人 |
| 国债 | FRED `GS2`、`GS10`，2/10 年期固定期限国债收益率月均，%（不是价格或回报） |
| 实际 GDP 增速 | FRED `GDPC1`，`((本季 / 上季)^4 - 1) × 100`，季环比年化百分比 |
| GDP 总量 | FRED `GDP`，名义 GDP，十亿美元、季调年率；快照换算为万亿美元 |

行情按纽约交易日归月；历史聚合排除当天未完成 K 线，最新报价单独保存时间并标记暂值，避免把盘中价格当作最终收盘。当月优先显示接口最近一次常规交易时段报价（可能延迟），保存报价时间并标记月内暂值；报价不可用时保留已完成交易日数据。不是实时行情推送。月度涨跌以当前/上月收盘计算；相对表现按所选起始月收盘 = 100，因此区间末月 / 起始月 - 1 不包含起始月本身的涨跌。

GDP 是季度数据，同一季度数值映射到三个月，不插值、不声称为月度 GDP。尚未发布的季度留空。所有数据按**观察期**对齐，使用抓取时的最新修订值，未保存完整 ALFRED 发布时点历史，**不能用于“当时已知数据”的无前视回测**。发布后 Git 版本可以追溯本项目后续采集时的快照，但不等于完整历史 vintage 数据。

月度宏观指标有正常发布滞后。页面各系列状态分别列出观察日期与抓取日期，不会拿前月数据填充缺失项。历史从 2005 年开始保存，默认显示截至当前月份的最后 240 个月；更新时保留较早历史。失败的系列保留旧记录、标记过期，并在部署后使工作流报告失败以便排查；首次抓取不完整则拒绝写入。

数据源：[FRED](https://fred.stlouisfed.org/)、[BLS](https://www.bls.gov/ces/)、[BEA](https://www.bea.gov/data/gdp/gross-domestic-product)、[Yahoo Finance](https://finance.yahoo.com/)。市场数据的使用和再分发应遵守供应方条款。

## 本地维护

需要 Python 3.10+，无需安装第三方包：

```sh
python3 scripts/update_data.py
python3 -m unittest discover -s tests
# 若已安装 Node.js，可额外验证计算逻辑：node tests/test_calculations.cjs
python3 -m http.server 8080
```

打开 `http://localhost:8080`。数据更新需要联网；测试只检查本地文件。`data/history.json` 是权威数据包；`data/history.js` 是同内容的离线兼容包。更新脚本会同时重建二者。页面无需数据库与后端服务器；GitHub Actions 只是定时生成静态文件。

文件：`index.html` / `styles.css` / `app.js`，`scripts/update_data.py`，`data/history.json` / `history.js`，`.github/workflows/update-and-deploy.yml`。

GitHub 部署参考：[自定义 Pages 工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)、[定时工作流行为](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)。

## 持续更新至今

时间筛选下方新增“持续更新至今”开关，默认开启并记住选择。结束月份跟随美东当前月份；新月份出现时自动延伸。快捷 1/3/5/10/20 年按固定月数滚动，“全部”保留最早起点。自定义历史区间会关闭跟随；重新开启时保留自定义起点。快照停留在历史月份时不会被刷新跳走，停留在最新月份时则随月份一起前移。

网页每分钟检查静态数据文件，重新回到标签页或网络恢复时也检查。GitHub Actions 每小时抓取并部署，可能存在调度与行情源延迟。开关只控制网页时间范围，不会从浏览器启动 GitHub 任务；本地双击文件仍为随附快照，持续取得新数据需要部署并启用工作流。未发布的宏观数据和当前月份尚无行情时均留空，不把旧月份伪装成当前值。

## 中英文 / Language selection

页面首次打开使用浏览器首选语言列表中第一个支持的语言：`zh-*` 使用简体中文，`en-*` 使用英文；未匹配时使用英文。右上角的 **自动 / 中文 / English** 可随时切换。手动选择保存在当前浏览器中；选择“自动”可恢复跟随浏览器语言。浏览器禁止本地存储时，当前页面仍可切换语言，但不会记住选择。

The first visit uses the first supported language in the browser's ordered language preferences: `zh-*` selects Simplified Chinese and `en-*` selects English, with English as the fallback. Use **Auto / 中文 / English** in the header to switch. Manual choices persist in this browser; Auto restores browser-language detection. Switching preserves the selected date range, focused month, chart mode and overlays. Labels, chart tooltips, status messages, accessibility labels and CSV headers follow the selected language; observation dates and CSV numeric values stay language-neutral. No translation service or database is required.

Translations live in `i18n.js`. Run `node tests/test_calculations.cjs` to verify calculations and language selection/translation coverage.
