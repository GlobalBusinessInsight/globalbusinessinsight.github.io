# 全球电子发票地图：主要地区、国家路线与企业落地差异

> 本篇按截至 2026 年 11 月 24 日的官方资料，挑选代表性国家和地区，解释制度路线，不把世界简单分成“有电子发票”和“没有电子发票”。

![全球电子发票制度路线示意图](https://globalbusinessinsight.github.io/assets/e-invoice-series/einvoice-global-landscape.svg)

## 五类路线同时存在

电子发票制度可能要求税务机关在开票前授权，可能由中心平台接收并转发，也可能让企业通过 Peppol 等商业网络交换；另一些制度要求开票后持续报送销售或付款数据。过渡期内还可能同时允许纸票、旧版 EDI 或替代渠道。

所以，网络送达、税务受理、买方验收和付款是不同状态。国家也可能同时采用两条以上路径。

### 欧洲：共同标准下，各国时间表不同

- **比利时：**自 2026 年 1 月起，范围内 VAT 企业的 B2B 交易使用结构化发票；Peppol 是默认交换路线。B2C 不在同一强制范围。
- **法国：**2026 年 9 月起先要求各规模企业接收、大型和中型企业开具并进行相关数据报送；2027 年 9 月扩展至中小企业和微型企业。e-invoicing 与 e-reporting 分开规定。
- **德国：**国内企业买方自 2025 年起须能接收；卖方仍在过渡安排内。部分小规模经营者及特定 EDI 流程可过渡到 2027 年底。
- **波兰：**KSeF 2.0 于 2026 年 2 月覆盖大型纳税人，4 月扩展到其他企业；月度发票金额不超过 10,000 兹罗提的小规模纳税人，2026 年底前有暂缓开具安排。
- **意大利：**大量境内 B2B/B2C 发票长期经税务局 SdI 传输。
- **欧盟 ViDA：**跨境 B2B 数字报告计划从 2030 年 7 月起；已有国内实时报告系统的成员国须于 2035 年前对齐。

### 美洲：税务认证是重点

巴西 NF-e 由州财政部门进行前置授权；墨西哥 CFDI 4.0 的 XML 和税务认证链于 2023 年 4 月起成为唯一有效版本。授权或税务认证校验身份、完整性、格式和资格等条件，并不担保底层交易的商业真实性。北美企业还可能使用 EDI 和采购网络，但这些不等于全国统一的税务清关平台。

### 亚太：平台、网络和报送可以叠加

中国数电发票自 2024 年 12 月全国推广，通过税务数字账户和电子发票服务平台流转。新加坡 InvoiceNow 基于 Peppol，并把符合条件企业的发票数据报送给 IRAS；剩余 GST 注册企业计划在 2028—2031 年分阶段纳入。澳大利亚依靠 Peppol 网络推进企业互通和政府采购采用；多数联邦采购机构计划从 2027 年起默认电子发票。

### 中东与非洲：按批次实施

沙特 ZATCA 第二阶段按波次要求企业接入 Fatoora。2026 年公布的第 25 波目标企业须在 2027 年 2 月前完成集成。肯尼亚 KRA 的 eTIMS 则要求广泛的经营者开具电子税务发票；这类税票管理不等于 Peppol 式的跨企业网络。

## 企业需要维护的不是一张“国家打勾表”

每个经营实体都应记录：谁是法定卖方、交易属于 B2B/B2G/B2C 还是跨境；要求的格式和版本是什么；通过税务平台、Peppol、API、EDI 还是门户发送；税务机关和买方分别返回什么状态；过渡期、阈值、离线补传、更正和留档规则是什么。

上线时间也要拆成两张表：**法规生效日**和**技术准备日**。注册证书、修正主数据、服务商配置、财务审批和伙伴测试都需要提前准备。供应商评估则应覆盖国家规则版本、原始数据导出、故障处理和退出迁移，而不只看“支持多少国家”。

**结论：**全球没有一套统一电子发票路径。先定位法律主体与交易场景，再分别确定文件、网络、税务报告、状态和保存义务。

### 官方资料与完整文章

- [阅读中英双语全文](https://globalbusinessinsight.github.io/reports/e-invoicing/07-global-e-invoicing-landscape.html)
- [电子发票专题目录](https://globalbusinessinsight.github.io/reports/e-invoicing/)
- [欧盟 ViDA 时间表](https://taxation-customs.ec.europa.eu/taxation/vat/vat-digital-age-vida_en)
- [法国时间表](https://www.impots.gouv.fr/professionnel/questions/partir-de-quand-suis-je-concerne-par-la-reforme-de-la-facturation) · [比利时 FAQ](https://einvoice.belgium.be/en/FAQ/general-questions-b2b) · [德国 FAQ](https://www.bundesfinanzministerium.de/Content/DE/FAQ/e-rechnung.html) · [波兰 KSeF](https://ksef.podatki.gov.pl/informacje-ogolne-ksef-20/zakres-obowiazkowego-ksef/)
- [中国数电发票公告](https://app.www.gov.cn/govdata/gov/202411/25/522115/article.html) · [新加坡 IRAS](https://www.iras.gov.sg/taxes/goods-services-tax-%28gst%29/gst-invoicenow-requirement) · [澳大利亚 ATO](https://www.ato.gov.au/businesses-and-organisations/einvoicing/einvoicing-for-government)
- [沙特 ZATCA 波次公告](https://www.zatca.gov.sa/en/MediaCenter/News/Pages/Wave25-E-invoicing.aspx) · [肯尼亚 KRA eTIMS](https://www.kra.go.ke/component/kra_faq/faq/653)

*本文是代表性国家样本，不是穷尽清单。制度会变化，实施前请以主管机关当前规则和个体通知为准。*
