# English, Every Day · 30天英语训练

可直接发布到 GitHub Pages 的纯静态网页。无数据库、无服务器程序、无安装或构建步骤，无需 API Key。包含30天生活英语课程、听读、情景开口、每日组卷、客观题判分、口语自评、错题复习、笔记与备份。

## 最简单的发布方式

1. 解压发布包，把**这个文件夹里面的文件**上传到 GitHub 仓库根目录。上传后，打开仓库首先应能看到 `index.html`，不要再套一层 `english-coach-github` 或 `dist` 文件夹。
2. 打开仓库 **Settings → Pages**。
3. 在 **Build and deployment → Source** 选择 **Deploy from a branch**。
4. 选择 **main**（或你实际上传的分支）和 **/(root)**，点击 **Save**。
5. 等待仓库的 Pages 部署成功，再打开 Settings → Pages 显示的 HTTPS 地址。不要把 GitHub 源代码浏览页面当作网站地址。

GitHub Free 可以使用公开仓库的 Pages；私有仓库的可用性取决于账号方案与组织设置。

官方说明：[配置发布来源](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)、[创建 Pages 网站](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)。

## 需要上传哪些文件

```text
index.html       网页入口，必须在发布目录最上层
style.css        样式
curriculum.js    30天课程和对话材料
app.js           网页功能
.nojekyll        隐藏的空文件，跳过 Jekyll 处理
README.md        本说明
CHECKS.md        检查结果与上线后核对项目
tests/check.cjs  可选：无需额外依赖的自动检查
```

全部上传即可。网站不需要运行 `npm install` 或设置 Actions 构建流程。`.nojekyll` 可能被文件管理器隐藏；请一并上传，或在 GitHub 中新建这个名字的空文件。不要上传整个上级工作目录、`.git`、`.openai`、你的学习备份或录音。

所有样式和脚本使用相对地址，适用于默认个人站点域名和“域名/仓库名/”项目站点，不需要修改仓库名称配置。请保留文件名的大小写。

## 进度迁移与保存

- 学习进度保存在访问者自己的浏览器中，不会上传到 GitHub，也不会跨设备自动同步。
- 从旧本地版或其他网址迁移：先在旧版“学习设置”中导出完整备份，再在新网站导入。
- 更换域名、浏览器、设备或清除网站数据后，需用备份恢复。建议每周备份一次。
- 录音仅在页面内临时保存，需要单独下载；不包含在 JSON 备份中。
- 同一浏览器内、同一个域名下的这款应用副本使用同一进度存储；若需要独立学习档案，请使用不同浏览器配置文件。
- 中文听力判分已修正。未标记为新版判分格式的历史记录，在读取或导入时会重新计算分数，并补入遗漏错题。

## 功能边界

- 每日题目由内置课程、日期、难度和到期错题组合，不是在线大模型无限生成。
- 客观题自动评分；口语分数由使用者按四项量表自评，不是自动发音评分。
- 浏览器负责英语朗读，声音取决于设备是否安装英语语音。
- 录音需要浏览器支持并允许麦克风；上线后使用 HTTPS。未获权限时可以用手机录音后自评。
- GitHub Pages 不会替你创建每日通知。先前在对话中设好的晚上8点提醒仍是独立的对话任务；复制这个仓库不会给其他访问者创建提醒。
- 公开网页的课程代码可以被别人查看；发布包没有个人练习记录、录音或凭据。

## 可选的开发检查

有 Node.js 时，在此文件夹执行：

```sh
node tests/check.cjs
```

用于检查课程组合、判分、历史分数修正、备份和存储异常等。不需要安装依赖。直接双击 `index.html` 可查看页面；录音与保存建议最终在正式 HTTPS 页面测试。
