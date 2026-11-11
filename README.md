# Global Business Insight

Global Business Insight publishes Chinese-first research on markets, industry and cross-border business, with a dedicated English research column on the right side of the homepage. Original report URLs remain in place.

- Chinese research homepage with a separate English desk: `/`
- 栏目：`/category/industry/`、`/category/global/`、`/category/digital/`
- 市场与工具：`/markets/`，Market Atlas 仍在 `/mk/`
- Research archive and search: `/archive/` (active research is the default; archived material is marked separately)
- 英文精选：`/en/`
- 更多工具：`/tools/`；30天英语训练：`/tools/english/`

## 更新网站

运行 `python3 scripts/build_portal.py`，然后运行 `python3 scripts/check_portal.py`。

生成器在发布构建中生成门户、栏目、专题、静态分页、浏览器内搜索目录、历史报告元数据与导航、站点地图。`scripts/build_portal.py` 对全部报告运行编辑筛查：低于70分或不属于当前研究栏目的页面标记为 Archive，从首页、栏目、默认搜索和站点地图移除，并设为 `noindex,follow`。旧网址保留。筛查只判断结构和研究呈现，不会自动更新正文中的事实。不要手动修改带有 `GBI generated` 标记的门户页；请修改生成器里的内容配置。不要改动 `GBI metadata` 和 `GBI reader` 标记块。

目录归类有自动规则，重要文章以 `FEATURED` 显式配置为准。`DESCS` 可指定准确摘要。`PAIRS` 仅加入正文实际对应的语言版本。新增没有标题的HTML片段不会被自动收入目录。

生成器不会给旧文伪造发布日期或更新时间，不声称历史资料已经逐篇重新核验。站点地图省略无法确认的 `lastmod`。

## 部署与回退

推送 main 后，既有 GitHub Actions 更新 `/mk/` 数据、生成和验证门户、构建整个 Jekyll 网站并发布。PR 运行独立结构检查。站点改动通过 PR 留下可回退记录；回退时撤销对应改版提交，不覆盖此后正常的数据更新。

英语训练继续加载根目录 `app.js`、`curriculum.js` 和 `style.css`。同一域名下保留 `nj-english-v1` 本地存储键，因此原有浏览器可继续使用原学习记录。更换域名、设备或浏览器仍需导出/导入备份。

维护事项与后台接入见 `OPERATIONS.md`。原 Market Atlas 说明见 `mk/README.md`。
