# 电子发票系统架构：企业系统、税务平台与传输网络各做什么

电子发票不是一个平台包办所有事情。企业的 ERP 和业务系统产生交易数据；映射与校验服务把内部字段转换成当地接受的格式；集成服务连接不同系统、管理身份认证、消息发送、重试和回执；某些制度要求发票先经过税务机关平台；传输网络负责把结构化发票送到买方。买方收到后，还要把它与订单、收货和合同匹配，再审批和入账。

![电子发票系统架构图](https://globalbusinessinsight.github.io/assets/e-invoice-series/einvoice-architecture.svg)

## 先把税务平台和交换网络分开

税务平台执行法律规定的申报、验证、授权或接收任务。交换网络解决发票如何寻址、安全传输并抵达交易对方。某些国家会把两类功能放在同一平台里，其他地方则分开部署。

巴西 NF-e 是集中授权的例子：企业生成并签名发票后，将其提交给州财政部门（SEFAZ）授权，再按巴西规则向联邦税务环境传递。授权说明发票通过规定的形式检查，并不代表政府核验了交易本身。意大利 SdI 由税务局管理，执行发票检查并把发票交付给接收方。Peppol 则是四角交换网络：发送企业经由服务商和接入点，通过网络送至买方的服务商和接入点。它提供路由和安全交换，本身不等于税务机关的清关平台。

这些例子说明，电子发票没有一条全球通用的系统流水线。是否要实时税务报送、发票是否必须先获授权、企业能否直连买方，都取决于当地制度和交易场景。

## 数据、接口和回执怎样接起来

发票数据来自订单、交付、合同和账务记录。系统需要处理字段映射、税码、金额计算、币种、买卖双方识别码以及当地格式。欧盟 EN 16931 标准提供核心发票数据的语义模型及其语法映射；2026年版已发布，各国迁移安排还在制定中。企业应核对所在国家当前接受的版本。

集成服务负责把ERP与外部接口接起来，记录唯一消息编号，控制重试，保存规则版本，并把平台或网络状态写回业务系统。监控不应只显示“发送成功”，还要能找到等待发送、税务拒绝、买方未处理、订单不匹配及无法归档的发票。

至少要把四类状态分开记录：传输服务的送达回执、税务平台的处理结果、买方的业务审批或异议、付款指令及银行到账。把它们合并成一个绿色勾号，会让财务人员无法知道一张发票卡在哪里。

## 归档不是保存一张PDF

适用法规和审计需要决定保存什么、保存多久。常见证据包括原始结构化发票、可读展示、校验结果、税务回执（如适用）、买方审批、会计凭证、更正关系、时间戳和访问日志。保留原始数据与关联关系，才能在多年后重建发票如何产生、传递和处理。

**文章结论：**企业架构应围绕数据来源、当地规则、传输路径和状态责任来设计。ERP、校验服务、税务平台、交换网络和买方系统可以由不同机构提供，也可能组合部署；系统必须说明每一步由谁负责、结果证明了什么、异常由谁跟进。

完整中英双语文章与架构图：  
[阅读电子发票系统架构研究](https://globalbusinessinsight.github.io/reports/e-invoicing/05-e-invoicing-architecture.html)

**主要资料**

- 欧盟委员会：[What is eInvoicing](https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/pages/467108851/What%2Bis%2BeInvoicing)、[EN 16931合规说明](https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/pages/467108926/Compliance%2Bwith%2BeInvoicing%2Bstandard)、[欧洲电子发票标准版本](https://ec.europa.eu/digital-building-blocks/sites/spaces/DIGITAL/pages/467108661/European%2BStandard%2Band%2BSpecifications)
- OpenPeppol：[互操作框架](https://peppol.org/learn-more/peppol-interoperability-framework/)、[BIS Billing 3.0](https://docs.peppol.eu/poacc/billing/3.0/bis/)
- 巴西国家电子发票门户：[NF-e常见问题](https://www.nfe.fazenda.gov.br/Portal/perguntasFrequentes.aspx?tipoConteudo=auR4yGlWmRY%3D)
- 意大利税务局：[电子发票流程](https://www1.agenziaentrate.gov.it/web_app_entrate/fatturazione_elettronica.html)
- OECD (2026)：[Digital Continuous Transactional Reporting for VAT](https://www.oecd.org/en/publications/digital-continuous-transactional-reporting-for-value-added-tax_34c88c39-en.html)

本文用于解释常见系统职责和特定制度案例，不构成法律、税务或系统实施意见。