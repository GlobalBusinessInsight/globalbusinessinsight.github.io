# 电子发票技术路线与交换协议：格式、网络和税务报送如何配合

> 一篇拆开 UBL、CII、Peppol、AS4、API 与“实时清关”的概念图解。先看它们各处在哪一层，再讨论企业如何组合部署。

![电子发票技术路线分层图](https://globalbusinessinsight.github.io/assets/e-invoice-series/einvoice-routes.svg)

“电子发票用什么协议？”这个问题常把好几层混在一起。业务语义说明字段代表什么；UBL、CII、EDIFACT 是载荷格式；CIUS、国家规则、Peppol BIS/PINT 规定一类流程怎样校验；AS4、API、EDI 网络解决消息如何发现收件方并传过去；税务清关或持续报告则由当地制度决定。

## 五层拆解

| 层次 | 解决的问题 | 例子 |
|---|---|---|
| 业务语义 | 买卖双方如何理解发票字段 | EN 16931、UN/CEFACT 业务术语 |
| 载荷语法 | 数据如何机器可读地编码 | UBL XML、CII XML、EDIFACT INVOIC |
| 实施规则 | 必填、税码、流程和校验如何确定 | CIUS、国家规则、Peppol BIS/PINT |
| 发现与传输 | 如何找到对方并安全送达 | Peppol SMP/SML + AS4、双边 API、EDI VAN |
| 税务报送 | 何时向税务机关提交什么 | 开票前授权、集中交换、近实时报告、事后审计 |

欧盟委员会把 EN 16931 的语义模型与语法绑定明确区分。在相关公共采购框架下，UBL 2.1 和 UN/CEFACT CII D16B 是相应合规语法；EDIFACT 有语法绑定，但不能据此认为所有公共机构都必须接收 EDIFACT。Peppol BIS Billing 3.0 是 EN 16931 的一种 CIUS；PINT 为国家化扩展提供国际模型。

Peppol 四角模式中，买卖双方分别连接各自服务商/Access Point。AS4 用于接入点间异步传输，SMP/SML 帮助动态发现端点和能力，网络还规定证书、加密和消息封装要求。AS4 回执只能说明传输层结果，不能证明税务批准、买方接受或钱已到账。

API、EDI 和门户也各有侧重：API 需管理身份认证、幂等、超时与异步查询；EDI VAN 便于延续既有供应链映射，但伙伴接入和异常流程可能各自不同；门户能帮助低频企业起步，却不一定适合自动对账。文件“送达”不等于发票内容合规。

还要把商业送达路径和税务报送路径分开画。某地可能要求开票前授权，另一地可能在开票后近实时报告，还有的以留档、申报和审计为主。采用某个交换网络并不会自动免除当地税务报送义务。OECD 2026 年报告也指出，各地持续交易报告制度发展并不协调，增加了跨境经营的合规复杂度。

**企业选型的顺序：**确认国家和客户要求 → 统一内部业务语义 → 选合规载荷和规则版本 → 确定网络/API/EDI 连接 → 分开监控技术回执、监管状态、买方业务响应和付款状态。

上线前还要确认税号与参与方标识、代码表、币种精度、贷项/更正流程、证书轮换、故障重发、原始文件和回执留存。供应商说“支持某协议”，并不等于覆盖了指定国家的所有规则、时限和审计要求。

**结论：**不存在一种包办所有语义、格式、网络和税务职责的“万能协议”。先按层选型，再为每种状态指定责任人，才能让电子发票真正可互通、可追踪、可审计。

### 延伸阅读

- [阅读完整中英双语文章](https://globalbusinessinsight.github.io/reports/e-invoicing/06-e-invoicing-protocols.html)
- [电子发票专题目录](https://globalbusinessinsight.github.io/reports/e-invoicing/)
- 欧盟委员会：[EN 16931 合规与语法绑定](https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/pages/467108926/Compliance%2Bwith%2BeInvoicing%2Bstandard)、[必需语法](https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/pages/467108934/Required%2Bsyntaxes)
- OpenPeppol：[BIS Billing 3.0](https://docs.peppol.eu/poacc/billing/3.0/bis/)、[PINT](https://docs.peppol.eu/poac/pint/pint/)、[AS4 Profile](https://docs.peppol.eu/edelivery/as4/specification/)
- OECD：[Digital Continuous Transactional Reporting for VAT (2026)](https://www.oecd.org/en/publications/2026/01/digital-continuous-transactional-reporting-for-value-added-tax_09f49627.html)

*本文聚焦结构化 B2B 发票及增值税/商品服务税报告。请以主管机关、标准组织和网络运营方最新规定为准。*
