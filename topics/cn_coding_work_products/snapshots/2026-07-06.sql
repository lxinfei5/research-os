BEGIN TRANSACTION;
CREATE TABLE context_snapshot_log (
    snapshot_id   TEXT PRIMARY KEY,
    payload       TEXT,
    content_hash  TEXT,
    freeze_policy TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE controlled_vocab (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    vocab_name       TEXT NOT NULL,
    canonical_value  TEXT NOT NULL,
    alias            TEXT,
    status           TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','retired')),
    UNIQUE (vocab_name, canonical_value, alias)
);
INSERT INTO "controlled_vocab" VALUES(1,'source_platform','web','web_page','active');
INSERT INTO "controlled_vocab" VALUES(2,'source_platform','web','website','active');
INSERT INTO "controlled_vocab" VALUES(3,'source_platform','web_search','google','active');
INSERT INTO "controlled_vocab" VALUES(4,'source_platform','web_search','bing','active');
INSERT INTO "controlled_vocab" VALUES(5,'source_platform','web_search','sogou','active');
INSERT INTO "controlled_vocab" VALUES(6,'source_platform','web_search','searxng','active');
INSERT INTO "controlled_vocab" VALUES(7,'source_platform','web_search','zhipu','active');
INSERT INTO "controlled_vocab" VALUES(8,'source_platform','news_media','news','active');
INSERT INTO "controlled_vocab" VALUES(9,'source_platform','research_report',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(10,'source_platform','paper','arxiv','active');
INSERT INTO "controlled_vocab" VALUES(11,'source_platform','x','X(Twitter)','active');
INSERT INTO "controlled_vocab" VALUES(12,'source_platform','x','twitter','active');
INSERT INTO "controlled_vocab" VALUES(13,'source_platform','douyin','抖音','active');
INSERT INTO "controlled_vocab" VALUES(14,'source_platform','xiaohongshu','小红书','active');
INSERT INTO "controlled_vocab" VALUES(15,'source_platform','xiaohongshu','rednote','active');
INSERT INTO "controlled_vocab" VALUES(16,'source_platform','wechat','微信','active');
INSERT INTO "controlled_vocab" VALUES(17,'source_platform','bilibili','b站','active');
INSERT INTO "controlled_vocab" VALUES(18,'source_platform','youtube',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(19,'source_platform','manual',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(20,'source_platform','other',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(21,'source_kind','article',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(22,'source_kind','web_page','web','active');
INSERT INTO "controlled_vocab" VALUES(23,'source_kind','search_result',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(24,'source_kind','news',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(25,'source_kind','report',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(26,'source_kind','paper',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(27,'source_kind','post','social_post','active');
INSERT INTO "controlled_vocab" VALUES(28,'source_kind','note',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(29,'source_kind','video',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(30,'source_kind','image','screenshot','active');
INSERT INTO "controlled_vocab" VALUES(31,'source_kind','forum','thread','active');
INSERT INTO "controlled_vocab" VALUES(32,'source_kind','chat',NULL,'active');
INSERT INTO "controlled_vocab" VALUES(33,'source_kind','other',NULL,'active');
CREATE TABLE credibility_assessment (
    id                 TEXT PRIMARY KEY,           -- cred-<hash>
    subject_type       TEXT NOT NULL CHECK (subject_type IN
                         ('l3_claim','l2_finding','l1_viewpoint','l0_worldview')),
    subject_id         TEXT NOT NULL,
    level              TEXT NOT NULL CHECK (level IN ('low','medium','high')),
    rationale          TEXT NOT NULL,
    filter_trace       TEXT NOT NULL,              -- JSON: independence / hype / recency checks
    independence_note  TEXT,
    echo_chamber_flag  INTEGER NOT NULL DEFAULT 0,
    calibration_basis  TEXT,
    status             TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    run_id             TEXT,
    assessed_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "credibility_assessment" VALUES('cred-d7f9d434078e','l3_claim','sc-13eaabcd6f28','medium','来源为产品定价页/官方文档类内容，但具体功能描述需以实际产品为准。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-980624b52b4e','l3_claim','sc-0fa9be3ceee1','high','定价信息为官方发布的数据，可信度高。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-b526b01c430b','l3_claim','sc-9ab98d5be76e','medium','消耗系数为用户实测/官方说明口径，具体数字可能随版本调整。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-735acce35514','l3_claim','sc-1527aea2e249','high','产品时间线和定位来自官方公告和多家科技媒体报道，可信度高。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-80cc5f8210ab','l3_claim','sc-5021cf331a20','medium','国际版改Token制来自IT之家等报道；缩水比例为掘金用户实测推算，非官方数据。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-fd53ea16fee8','l3_claim','sc-ac65832dcadf','high','产品功能描述来自官方文档和用户实测反馈。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-2329f93926a5','l3_claim','sc-542bd42e1250','medium','分析基于产品演进逻辑和行业对比，属于合理推断而非官方声明。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-91b695822cc7','l3_claim','sc-530a69a57ca6','medium','成本结构分析有行业公开数据（Cursor CEO公开信等）支撑，但具体倍数为估算。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-f0ffcf440d6f','l3_claim','sc-034d1a3ee08f','medium','国内版策略为基于市场环境的推断，非官方确认路线图。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-64cef9cae6e0','l3_claim','sc-845d96bb37e5','high','品牌更名和产品矩阵来自阿里云官方公告，可信度高。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-cc92c2494226','l3_claim','sc-d5719f9dd8f0','high','定价数据来自阿里云官方定价页，可信度高。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-0f00c1941574','l3_claim','sc-9e148ff376bf','high','Credits消耗规则来自官方文档，可信度高。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-4060207a25b8','l3_claim','sc-bb22bebce26f','medium','涨价事实来自官方，客户数据来自阿里云宣传，迁移成本分析为行业推断。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-e877a7c15707','l3_claim','sc-89233a8e21cf','high','资源包定价和有效期来自官方购买页，可信度高。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-41f80a92b881','l2_finding','sf-4d23df598921','high','三家产品归属和商业化状态有多方交叉验证。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-a02eda85a8e4','l2_finding','sf-b8f926dc8720','high','WorkBuddy和Qoder都明确采用积分/Credits制，模式高度一致。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-52716b77c2fa','l2_finding','sf-4f462c77ace5','high','次数制vs积分制在三家产品中有明确差异，Trae国际版改Token制有公开报道。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-f0eb902a7b0f','l2_finding','sf-f123152f1479','medium','Qoder国内外价差有明确数据支撑，WorkBuddy和Trae的''免费/低价''策略来自产品现状观察。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-54e7b937f670','l2_finding','sf-3cc90d13d18b','medium','三种计费模式的对比分析基于产品设计逻辑的归纳。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-ecdc8f39c1a3','l2_finding','sf-36b1d2c9eaaf','medium','三家产品都在强调Agent/AI员工能力，成本上升分析基于模型调用次数增长的合理推断。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-3dc5fc43a67b','l1_viewpoint','vp-d64be0150796','medium','观点综合3个来源的定价信息和产品逻辑分析而成，事实部分可信度高，趋势预测部分为合理推断。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
INSERT INTO "credibility_assessment" VALUES('cred-5c328ce48b81','l0_worldview','wv-8843c7643785','medium','世界模型综合3家产品的现有定价信息和行业演进逻辑，事实部分有来源支撑，趋势判断为中等置信度推断。','{"stage": "manual_condense", "agent": "main"}',NULL,0,NULL,'active',NULL,'2026-07-06 12:24:42');
CREATE TABLE facet (
    id               TEXT PRIMARY KEY,              -- f_<slug>
    question         TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'open' CHECK (status IN
                       ('open','survey','deepening','saturating','closed')),
    last_searched_at TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "facet" VALUES('f_ai_coding_work_vs_vs_token','国内AI Coding/Work产品计费模式对比研究（积分制 vs 请求次数制 vs Token制）','survey',NULL,'2026-07-06 12:15:42');
CREATE TABLE knowledge_change_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name    TEXT NOT NULL,
    row_id        TEXT NOT NULL,
    column_name   TEXT NOT NULL,
    change_kind   TEXT NOT NULL CHECK (change_kind IN
                    ('insert','update','dedup_skip','archive','budget_warn','json_warn')),
    old_blob      TEXT,
    new_blob      TEXT,
    diff_summary  TEXT,
    changed_by    TEXT NOT NULL,
    changed_at    TEXT NOT NULL DEFAULT (datetime('now')),
    audit_note    TEXT
);
INSERT INTO "knowledge_change_log" VALUES(1,'l3_claim','sc-13eaabcd6f28','*','insert',NULL,NULL,'kind=fact facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(2,'l3_claim','sc-0fa9be3ceee1','*','insert',NULL,NULL,'kind=data facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(3,'l3_claim','sc-9ab98d5be76e','*','insert',NULL,NULL,'kind=fact facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(4,'l3_claim','sc-1527aea2e249','*','insert',NULL,NULL,'kind=fact facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(5,'l3_claim','sc-5021cf331a20','*','insert',NULL,NULL,'kind=fact facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(6,'l3_claim','sc-ac65832dcadf','*','insert',NULL,NULL,'kind=fact facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(7,'l3_claim','sc-542bd42e1250','*','insert',NULL,NULL,'kind=analysis facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(8,'l3_claim','sc-530a69a57ca6','*','insert',NULL,NULL,'kind=analysis facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(9,'l3_claim','sc-034d1a3ee08f','*','insert',NULL,NULL,'kind=analysis facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(10,'l3_claim','sc-845d96bb37e5','*','insert',NULL,NULL,'kind=fact facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(11,'l3_claim','sc-d5719f9dd8f0','*','insert',NULL,NULL,'kind=data facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(12,'l3_claim','sc-9e148ff376bf','*','insert',NULL,NULL,'kind=fact facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(13,'l3_claim','sc-bb22bebce26f','*','insert',NULL,NULL,'kind=analysis facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(14,'l3_claim','sc-89233a8e21cf','*','insert',NULL,NULL,'kind=fact facet=f_ai_coding_work_vs_vs_token','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(15,'l2_finding','sf-4d23df598921','*','insert',NULL,NULL,'type=trend corrob=3/1','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(16,'l2_finding','sf-b8f926dc8720','*','insert',NULL,NULL,'type=trend corrob=2/1','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(17,'l2_finding','sf-4f462c77ace5','*','insert',NULL,NULL,'type=fact corrob=3/1','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(18,'l2_finding','sf-f123152f1479','*','insert',NULL,NULL,'type=figure corrob=3/1','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(19,'l2_finding','sf-3cc90d13d18b','*','insert',NULL,NULL,'type=claim corrob=3/1','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(20,'l2_finding','sf-36b1d2c9eaaf','*','insert',NULL,NULL,'type=trend corrob=3/1','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(21,'l1_viewpoint','vp-d64be0150796','*','insert',NULL,NULL,'kind=sub_question stance=established','manual_agent','2026-07-06 12:24:42',NULL);
INSERT INTO "knowledge_change_log" VALUES(22,'l0_worldview','wv-8843c7643785','*','insert',NULL,NULL,'kind=state_of_understanding','manual_agent','2026-07-06 12:24:42',NULL);
CREATE TABLE l0_worldview (
    id                  TEXT PRIMARY KEY,           -- wv-<hash>
    summary_kind        TEXT NOT NULL CHECK (summary_kind IN
                          ('state_of_understanding','consensus','tension','frontier','other')),
    proposition         TEXT NOT NULL,
    scope               TEXT,                       -- JSON
    key_findings        TEXT,                       -- JSON: array of l2_finding.id
    open_questions      TEXT,                       -- JSON: drives the feedback loop
    confidence          TEXT CHECK (confidence IN ('low','medium','high')),
    supersedes_id       TEXT,                       -- prior worldview (chain)
    l1_ids              TEXT,                       -- JSON array of l1_viewpoint.id
    source_ref_ids      TEXT NOT NULL,
    credibility_id      TEXT NOT NULL REFERENCES credibility_assessment(id),
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    run_id              TEXT,
    context_snapshot_id TEXT,
    context_hash        TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by          TEXT NOT NULL DEFAULT 'analysis',
    audit_note          TEXT,
    CHECK (source_ref_ids NOT IN ('','[]','null','[ ]'))
);
INSERT INTO "l0_worldview" VALUES('wv-8843c7643785','state_of_understanding','截至2026年7月，国内BAT三家（腾讯WorkBuddy、字节Trae Work、阿里Qoder）在AI Coding/Work工作台赛道已完成商业化起步，形成积分制（WorkBuddy/Qoder）vs 请求次数制（Trae Work国内版）的计费模式分化。积分/Credits制是主流方向，它通过抽象系数层在用户体验简单性和成本精确性之间取得平衡；请求次数制在产品早期/大众市场获客阶段有体验优势，但随着Agent能力增强和token成本上升将面临成本倒挂压力。三家产品均采用''基础功能免费+高阶功能收费''的freemium模式，国内定价约为全球版的40%，企业版在客户锁定后开始涨价变现。未来随着AI Agent从''辅助工具''向''AI员工''演进，计费模式将进一步向细粒度（Token/积分）和任务价值定价方向演化。','{"topic": "cn_coding_work_products", "as_of": "2026-07-06", "geography": "CN"}','["sf-4d23df598921", "sf-b8f926dc8720", "sf-4f462c77ace5", "sf-f123152f1479", "sf-3cc90d13d18b", "sf-36b1d2c9eaaf"]','["Trae Work国内版计费模式何时切换？触发条件是什么？", "豆包MarsCode、文心快码(Comate)、CodeGeeX等其他国产产品的计费模式对比？", "GitHub Copilot、Cursor等国际产品在中国市场的策略如何？", "AI编程工具的计费终局是什么？按任务价值计费还是按算力消耗计费？", "企业版定价权在客户深度集成后能提升到什么程度？", "外接API Key（BYOK）模式的长期生态影响？", "未来产品预留：其他待纳入的国内Coding/Work产品有哪些？"]','medium',NULL,'["vp-d64be0150796"]','["src-909ce9fa7145", "src-fc7ca176df63", "src-815dbcf6d1a6"]','cred-5c328ce48b81','active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
CREATE TABLE l1_viewpoint (
    id                  TEXT PRIMARY KEY,           -- vp-<hash>
    facet               TEXT,
    sub_question        TEXT,
    viewpoint_scope     TEXT,                       -- JSON {angle, role, stance}
    synthesis_kind      TEXT NOT NULL CHECK (synthesis_kind IN
                          ('theme','sub_question','viewpoint','contrarian')),
    narrative           TEXT NOT NULL,
    stance              TEXT CHECK (stance IN
                          ('established','contested','emerging','refuted','uncertain')),
    l2_ids              TEXT,                       -- JSON array of l2_finding.id
    open_questions      TEXT,                       -- JSON array
    confidence          TEXT CHECK (confidence IN ('low','medium','high')),
    source_ref_ids      TEXT NOT NULL,
    credibility_id      TEXT NOT NULL REFERENCES credibility_assessment(id),
    parent_l0_id        TEXT,
    rank                INTEGER,
    status              TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    run_id              TEXT,
    context_snapshot_id TEXT,
    context_hash        TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by          TEXT NOT NULL DEFAULT 'analysis',
    audit_note          TEXT,
    CHECK (source_ref_ids NOT IN ('','[]','null','[ ]'))
);
INSERT INTO "l1_viewpoint" VALUES('vp-d64be0150796','f_ai_coding_work_vs_vs_token','国内AI Coding/Work产品计费模式对比：积分制vs请求次数制vs Token制的演进逻辑',NULL,'sub_question','## 国内AI Coding/Work产品计费模式对比分析

### 一、市场格局与产品定位

2026年中，国内互联网大厂在AI Coding/Work赛道已形成BAT三足鼎立：腾讯WorkBuddy（CodeBuddy品牌）、字节Trae Work、阿里Qoder（原通义灵码）。三家产品均已从早期免费抢用户阶段进入商业化变现阶段，但计费策略选择出现了有趣分化。

### 二、三种计费模式的本质差异

**1. 积分/Credits制（WorkBuddy、Qoder——主流选择）**
积分制本质是一种"加权token抽象层"：用户看到的是统一的"积分"或"Credits"，底层按模型和任务复杂度乘以不同系数扣减。这种设计的好处是：
- 用户无需理解token、上下文窗口等技术概念
- 平台可以灵活调整不同模型的成本权重而不改变定价结构
- 代码补全作为最高频功能普遍免费（降低获客门槛），Agent等高价值功能才消耗积分
- Qoder和WorkBuddy都支持外接自定义API Key，给重度用户提供"自带算力"的逃生通道

**2. 请求次数制（Trae Work国内版——少数派）**
Trae Work国内版是唯一仍坚持对话次数制的产品。这种设计在产品早期有明显的用户体验优势："每周N次"像网盘容量一样直观，不会产生"每句话都在花钱"的Token焦虑。但它的致命缺陷是成本倒挂——在Agent时代，一次"对话"背后可能触发10+次模型调用，消耗几十万token，但用户只付了一次的钱。Trae国际版已经在2026年2月被迫切换到Token制（据用户实测权益缩水到约1/5），Cursor也经历了同样的转变。

**3. 为什么Trae Work国内版还坚持次数制？**
这是一个阶段性的商业策略选择而非技术决策：
- **目标用户更广**：Trae Work面向产品/运营/市场/设计/开发全场景，非技术用户对Token接受度极低
- **成本暂时可控**：Work/Design模式比纯Code模式的token消耗更可控，且字节有豆包自有模型的成本优势
- **国内竞争策略**：主打"免费够用"快速做用户规模，Pro版Fast Pass优先队列是体验差异化而非次数差异化
- **风险**：随着Agent能力增强（自动处理飞书文档、多步自动化），单次"对话"成本会快速上升，这是一颗定时炸弹

### 三、定价策略的中国特色

三家产品都体现了明显的"中国定价"特征：
- Qoder国内Pro ¥59/月仅为全球版$20的约40%
- 普遍提供 generous 的免费额度（代码补全无限免费）
- 资源包有效期短（到期清零），鼓励持续订阅
- 企业版在客户锁定后开始涨价（Qoder企业版涨25%），利用迁移成本变现

### 四、核心矛盾与趋势预测

AI编程工具计费面临一个根本矛盾：**用户体验要求简单（次数/积分），成本结构要求精确（Token）**。积分/Credits制是目前的最优折中——用系数层屏蔽底层复杂性，同时保持成本匹配度。

**趋势判断**：
1. 随着Agent能力增强和上下文窗口继续扩大，请求次数制将越来越难以为继，Trae Work国内版大概率会在未来切换到积分/Credits制或Token制
2. "代码补全免费+Agent功能收费"将成为行业标准分层模式
3. 支持外接自定义API Key会成为标配——既是对重度用户的让利，也是平台成本风险的释放阀
4. 企业版定价将持续走高，因为代码库深度集成后的迁移成本是极强的护城河','established','["sf-4d23df598921", "sf-b8f926dc8720", "sf-4f462c77ace5", "sf-f123152f1479", "sf-3cc90d13d18b", "sf-36b1d2c9eaaf"]','["Trae Work国内版何时会切换计费模式？触发点是什么？", "除了BAT三家，其他国产AI编程工具（如豆包MarsCode、文心快码、CodeGeeX等）的计费模式是什么？", "企业版涨价25%后的客户留存率和续约率如何？", "外接API Key模式对平台生态的长期影响是正面还是负面？"]','medium','["src-909ce9fa7145", "src-fc7ca176df63", "src-815dbcf6d1a6"]','cred-3dc5fc43a67b','wv-8843c7643785',1,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
CREATE TABLE l2_finding (
    id                    TEXT PRIMARY KEY,         -- sf-<hash>
    facet                 TEXT,
    finding_type          TEXT NOT NULL CHECK (finding_type IN
                            ('fact','event','figure','claim','trend')),
    statement             TEXT NOT NULL,
    value_text            TEXT,
    value_num             REAL,
    unit                  TEXT,
    valid_from            TEXT,
    valid_to              TEXT,
    corroboration_count   INTEGER NOT NULL DEFAULT 1,   -- = #independent source_ref_ids (mechanical)
    cross_platform_count  INTEGER NOT NULL DEFAULT 1,   -- = #distinct platforms (mechanical)
    corroboration_sources TEXT,                         -- JSON list (written by _corroborate)
    conflict_note         TEXT,                         -- agent records contradictions
    source_ref_ids        TEXT NOT NULL,                -- JSON array
    credibility_id        TEXT NOT NULL REFERENCES credibility_assessment(id),
    l3_ids                TEXT,                         -- JSON array of l3_claim.id
    parent_l1_id          TEXT,
    status                TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    run_id                TEXT,
    context_snapshot_id   TEXT,
    context_hash          TEXT,
    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by            TEXT NOT NULL DEFAULT 'analysis',
    audit_note            TEXT,
    CHECK (source_ref_ids NOT IN ('','[]','null','[ ]')),
    CHECK (corroboration_count >= 1),
    CHECK (cross_platform_count >= 1)
);
INSERT INTO "l2_finding" VALUES('sf-4d23df598921','f_ai_coding_work_vs_vs_token','trend','国内BAT三家AI Coding/Work产品已形成三足鼎立格局：腾讯WorkBuddy(CodeBuddy)、字节Trae Work、阿里Qoder(原通义灵码)，三家均已完成从免费到商业化收费的转型。',NULL,NULL,NULL,NULL,NULL,3,1,NULL,NULL,'["src-909ce9fa7145", "src-fc7ca176df63", "src-815dbcf6d1a6"]','cred-41f80a92b881','["sc-13eaabcd6f28", "sc-1527aea2e249", "sc-845d96bb37e5"]','vp-d64be0150796','active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l2_finding" VALUES('sf-b8f926dc8720','f_ai_coding_work_vs_vs_token','trend','积分/Credits制是国内AI编程工具的主流计费模式：WorkBuddy用积分（按模型系数消耗）、Qoder用Credits（统一计量单位），两者本质都是''加权积分制''——用抽象单位屏蔽底层模型token差异，用户无需理解技术概念；代码补全作为最高频功能普遍免费，Agent/高阶功能才消耗积分。',NULL,NULL,NULL,NULL,NULL,2,1,NULL,NULL,'["src-909ce9fa7145", "src-815dbcf6d1a6"]','cred-a02eda85a8e4','["sc-9ab98d5be76e", "sc-9e148ff376bf"]','vp-d64be0150796','active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l2_finding" VALUES('sf-4f462c77ace5','f_ai_coding_work_vs_vs_token','fact','Trae Work国内版是三家之中唯一仍采用请求次数制的产品；其国际版已在2026年2月切换为Token制，国内版暂未切换。请求次数制在Agent长上下文时代存在成本倒挂风险（重度用户成本远超付费），国际版和Cursor已为此被迫切换。',NULL,NULL,NULL,NULL,NULL,3,1,NULL,'次数制在产品早期/轻量场景下有用户体验优势，但长期不可持续——这是一个时间维度上的矛盾。','["src-fc7ca176df63", "src-815dbcf6d1a6", "src-909ce9fa7145"]','cred-52716b77c2fa','["sc-5021cf331a20", "sc-530a69a57ca6"]','vp-d64be0150796','active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l2_finding" VALUES('sf-f123152f1479','f_ai_coding_work_vs_vs_token','figure','国内定价显著低于全球定价：Qoder国内Pro ¥59/月约为全球版$20的40%，WorkBuddy和Trae Work也主打免费可用+低价Pro；这反映了中国AI工具市场购买力水平和竞争烈度。','国内Pro价格约为全球版的40%',NULL,NULL,NULL,NULL,3,1,NULL,NULL,'["src-815dbcf6d1a6", "src-909ce9fa7145", "src-fc7ca176df63"]','cred-f0eb902a7b0f','["sc-d5719f9dd8f0"]','vp-d64be0150796','active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l2_finding" VALUES('sf-3cc90d13d18b','f_ai_coding_work_vs_vs_token','claim','AI编程工具计费模式存在一个核心产品-成本矛盾：用户体验要求计费单位简单易懂（次数/积分），但成本结构要求精确匹配token消耗（Token制）。积分/Credits制是折中方案——用抽象系数层在用户体验和成本精确性之间取平衡，不同模型/任务类型有不同消耗系数。',NULL,NULL,NULL,NULL,NULL,3,1,NULL,NULL,'["src-909ce9fa7145", "src-fc7ca176df63", "src-815dbcf6d1a6"]','cred-54e7b937f670','["sc-9ab98d5be76e", "sc-542bd42e1250", "sc-9e148ff376bf"]','vp-d64be0150796','active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l2_finding" VALUES('sf-36b1d2c9eaaf','f_ai_coding_work_vs_vs_token','trend','AI编程工具正在从''辅助补全''向''AI员工/Agent工作台''演进（WorkBuddy的多专家协作、QoderWake 7×24 AI员工、Trae Work的飞书自动化），这一演进带来的token成本跃升是迫使计费模式从粗粒度（次数制）向细粒度（Token/Credits制）转变的根本驱动力。',NULL,NULL,NULL,NULL,NULL,3,1,NULL,NULL,'["src-909ce9fa7145", "src-fc7ca176df63", "src-815dbcf6d1a6"]','cred-ecdc8f39c1a3','["sc-13eaabcd6f28", "sc-530a69a57ca6", "sc-bb22bebce26f"]','vp-d64be0150796','active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
CREATE TABLE l3_claim (
    id                    TEXT PRIMARY KEY,         -- sc-<hash>
    facet                 TEXT,
    proposition           TEXT NOT NULL,            -- the real point, not a verbatim truncation
    claim_kind            TEXT NOT NULL CHECK (claim_kind IN
                            ('fact','analysis','rumor','breaking','opinion','data','other')),
    source_kind           TEXT CHECK (source_kind IN
                            ('article','post','video','image','forum','paper','other')),
    single_source_ref_id  TEXT NOT NULL REFERENCES source_ref(id),
    source_ref_ids        TEXT NOT NULL,            -- JSON array; kept = [single_source_ref_id ∪ ...]
    verbatim_excerpt      TEXT,
    cached_text_hash      TEXT,                     -- → library/sources/<hash>.json
    analysis_note         TEXT,
    filter_trace          TEXT NOT NULL,            -- JSON: independence / hype / recency
    debate_trace          TEXT,                     -- JSON: pro / con / synthesis rounds
    credibility_id        TEXT NOT NULL REFERENCES credibility_assessment(id),
    parent_l2_id          TEXT,
    lifecycle             TEXT,
    status                TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','archived')),
    run_id                TEXT,
    context_snapshot_id   TEXT,
    context_hash          TEXT,
    created_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at            TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by            TEXT NOT NULL DEFAULT 'analysis',
    audit_note            TEXT,
    CHECK (source_ref_ids NOT IN ('','[]','null','[ ]'))
);
INSERT INTO "l3_claim" VALUES('sc-13eaabcd6f28','f_ai_coding_work_vs_vs_token','WorkBuddy是腾讯云CodeBuddy团队推出的桌面AI智能体工作台，非字节跳动产品；核心能力包括本地文件操作、Claw手机远程操控、Skills技能生态、多专家Agent协作，定位是能''干活交付''而非仅聊天的AI工作台。','fact','article','src-909ce9fa7145','["src-909ce9fa7145"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-d7f9d434078e','sf-36b1d2c9eaaf',NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-0fa9be3ceee1','f_ai_coding_work_vs_vs_token','WorkBuddy于2026年7月1日起正式收费，采用积分制计费：标准版4000积分/月，加量包50元/1000积分，新用户首月5000积分体验，支持外接自定义API Key免费用。','data','article','src-909ce9fa7145','["src-909ce9fa7145"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-980624b52b4e',NULL,NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-9ab98d5be76e','f_ai_coding_work_vs_vs_token','WorkBuddy积分按模型系数消耗：MiniMax模型系数0.18（最低），DeepSeek模型系数0.30；简单对话约2-3积分，PDF/PPT/批量处理是消耗大户。','fact','article','src-909ce9fa7145','["src-909ce9fa7145"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-b526b01c430b','sf-3cc90d13d18b',NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-1527aea2e249','f_ai_coding_work_vs_vs_token','Trae产品线分为国际版(trae.ai)和国内版Trae Work(work.trae.cn)：国际版2025年1月发布面向海外开发者，国内版2026年6月9日由Trae Solo升级而来面向全场景知识工作者（产品/运营/市场/设计/开发）。','fact','article','src-fc7ca176df63','["src-fc7ca176df63"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-735acce35514','sf-4d23df598921',NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-5021cf331a20','f_ai_coding_work_vs_vs_token','Trae国际版已于2026年2月24日从请求次数制切换为Token计费（五档套餐Free/Lite/Pro/Pro+/Ultra），据用户测算Pro用户实际权益缩水至原来的约1/5；但国内版Trae Work目前仍采用对话次数制（近期从每日限额改为每周限额）。','fact','article','src-fc7ca176df63','["src-fc7ca176df63"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-80cc5f8210ab','sf-4f462c77ace5',NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-ac65832dcadf','f_ai_coding_work_vs_vs_token','Trae Work国内版免费提供Doubao Seed 2.1 Pro/2.1 Turbo、MiniMax、GLM等模型，Pro版有Fast Pass优先队列（高峰期免费用户排队），支持自定义API Key接入。','fact','article','src-fc7ca176df63','["src-fc7ca176df63"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-fd53ea16fee8',NULL,NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-542bd42e1250','f_ai_coding_work_vs_vs_token','AI编程工具早期采用请求次数制的核心设计逻辑：(1)Token是技术概念普通用户难以理解，''X次/月''符合SaaS订阅心智获客转化率更高；(2)2025年初模型上下文窗口小、Agent能力弱，单次请求token消耗差异不大，按次数大致公平；(3)Cursor早期Pro也是500次快速请求、GitHub Copilot长期无限次，是行业惯例；(4)产品快速迭代期粗粒度计费避免频繁调价；(5)避免用户的''Token焦虑''心理。','analysis','article','src-fc7ca176df63','["src-fc7ca176df63"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-2329f93926a5','sf-3cc90d13d18b',NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-530a69a57ca6','f_ai_coding_work_vs_vs_token','请求次数制不可持续的根本原因（成本倒逼）：上下文窗口从8k/32k扩展到128k-1M+、Agent模式下单请求触发10+次模型调用、不同模型成本差5-10倍、重度用户单次会话token量是轻度用户几十倍，导致重度用户对轻度用户的交叉补贴不可持续——这也是Trae国际版和Cursor改Token制的原因。','analysis','article','src-fc7ca176df63','["src-fc7ca176df63"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-91b695822cc7','sf-36b1d2c9eaaf',NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-034d1a3ee08f','f_ai_coding_work_vs_vs_token','Trae Work国内版暂时保留次数制的原因：目标用户更广泛（非技术用户对Token接受度低）、Work/Design模式单次token消耗比Code模式可控、国内市场主打''免费够用''用户增长策略；但随着Agent能力增强，单次对话实际成本上升，未来可能需要调整计费策略。','analysis','article','src-fc7ca176df63','["src-fc7ca176df63"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-f0ffcf440d6f',NULL,NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-845d96bb37e5','f_ai_coding_work_vs_vs_token','Qoder是阿里巴巴推出的AI智能编程平台，采用国内国际双轨运营；国内版2026年5月20日从''通义灵码''更名为Qoder CN，产品矩阵包括Qoder Desktop(IDE)、QoderWork CN(办公)、Qoder CLI、QoderWake(7×24 AI员工)、JetBrains插件、Mobile端。','fact','article','src-815dbcf6d1a6','["src-815dbcf6d1a6"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-64cef9cae6e0','sf-4d23df598921',NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-d5719f9dd8f0','f_ai_coding_work_vs_vs_token','Qoder全球版定价：Pro $20/月(2000 Credits)，Pro+ $60/月(6000 Credits)，新用户2周Pro试用+1000 Credits；国内版定价约为全球版40%：个人Pro ¥59/月(2000 Credits)，Pro+ ¥169/月(6000 Credits)，企业标准版¥99/席位/月，VPC版¥199/席位/月。','data','article','src-815dbcf6d1a6','["src-815dbcf6d1a6"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-cc92c2494226','sf-f123152f1479',NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-9e148ff376bf','f_ai_coding_work_vs_vs_token','Qoder采用Credits统一计量单位：代码补全和Next Edits全版本无限免费（获客钩子），Inline Chat/Ask/Agent/Quest/Experts/RepoWiki消耗Credits；模型调用失败不扣费；支持多模型切换（GLM/DeepSeek/Kimi/MiniMax等），实际消耗由任务复杂度和模型决定；非高峰期Qwen 3.7享最高80%折扣。','fact','article','src-815dbcf6d1a6','["src-815dbcf6d1a6"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-0f00c1941574','sf-3cc90d13d18b',NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-bb22bebce26f','f_ai_coding_work_vs_vs_token','Qoder 2026年5月更名后企业版涨价约25%（标准版¥79→¥99，VPC版¥159→¥199），个人专业版从限时免费转为¥59/月；涨价逻辑为通义灵码已签约超1万家企业客户（一汽/蔚来/中华财险等）迁移成本高，加上Agent多轮调用算力成本上升。','analysis','article','src-815dbcf6d1a6','["src-815dbcf6d1a6"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-4060207a25b8','sf-36b1d2c9eaaf',NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
INSERT INTO "l3_claim" VALUES('sc-89233a8e21cf','f_ai_coding_work_vs_vs_token','Qoder资源包设计：个人¥40/1000 Credits(1个月有效)，企业¥80/2000 Credits(3个月有效)，到期清零；资源包单价比套餐内Credits单价高，鼓励订阅而非按量购买；跨产品共享Credits(Desktop/JetBrains/QoderWork/CLI/Mobile)。','fact','article','src-815dbcf6d1a6','["src-815dbcf6d1a6"]',NULL,NULL,NULL,'{"stage": "distill", "independence": "single_source", "hype": "filtered"}',NULL,'cred-e877a7c15707',NULL,NULL,'active',NULL,NULL,NULL,'2026-07-06 12:24:42','2026-07-06 12:24:42','manual_agent',NULL);
CREATE TABLE method_rule (
    id           TEXT PRIMARY KEY,                  -- mr-<hash>
    level        TEXT NOT NULL CHECK (level IN ('M0','M1')),
    proposition  TEXT NOT NULL,
    valid_if     TEXT,                              -- M1: JSON {stage, facet, condition}; M0: NULL
    wrong_if     TEXT,
    status       TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active','retired','draft')),
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by   TEXT NOT NULL DEFAULT 'analysis'
);
CREATE TABLE open_question (
    id               TEXT PRIMARY KEY,              -- oq-<hash>
    question         TEXT NOT NULL,
    facet_id         TEXT,
    status           TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','answered','stale')),
    spawned_from_l_id TEXT,
    answered_by_l_id  TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE search_log (
    id           TEXT PRIMARY KEY,                 -- sl-<hash>
    query        TEXT NOT NULL,
    source       TEXT,                             -- web / x / douyin / xiaohongshu / ...
    facet        TEXT,                             -- facet this search targeted (nullable)
    run_id       TEXT,
    result_note  TEXT,                             -- optional: counts / outcome the agent recorded
    searched_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE source_ref (
    id                    TEXT PRIMARY KEY,        -- src-<hash>
    subject_type          TEXT CHECK (subject_type IN
                            ('l3_claim','l2_finding','l1_viewpoint','l0_worldview','pending')),
    subject_id            TEXT,
    platform              TEXT NOT NULL,           -- controlled vocab (source_platform)
    source_kind           TEXT NOT NULL,           -- controlled vocab (source_kind)
    url                   TEXT NOT NULL,           -- real verifiable URL; empty/'dataset' REJECTED
    author                TEXT,
    title                 TEXT,
    content_hash          TEXT,                    -- → library/sources/<hash>.json
    cached_text_path      TEXT,                    -- per-topic cache/<hash>.md snapshot
    media_transcript_path TEXT,                    -- video ASR / image OCR text, if any
    intake_item_id        TEXT,                    -- sources.db source_item this was promoted from
    captured_at           TEXT,
    captured_by           TEXT,
    valid_to              TEXT,
    created_at            TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "source_ref" VALUES('src-909ce9fa7145','pending',NULL,'web','article','https://www.codebuddy.cn/workbuddy',NULL,'WorkBuddy（腾讯云CodeBuddy）定价与计费说明','5fbbf592a4b545bb140afbf775245d48515537bff6abf19a51080348ca8c7f33','topics/cn_coding_work_products/cache/5fbbf592a4b545bb140afbf775245d48515537bff6abf19a51080348ca8c7f33.md',NULL,'ri-83bc822e76c3','2026-07-06 12:18:04','agent',NULL,'2026-07-06 12:18:04');
INSERT INTO "source_ref" VALUES('src-fc7ca176df63','pending',NULL,'web','article','https://work.trae.cn/pricing',NULL,'Trae Work国内版计费模式分析（对话次数制）','7f09ba536dab8566e1820955ea653104d47c4ecd114c0dc666b6a7ced9afa211','topics/cn_coding_work_products/cache/7f09ba536dab8566e1820955ea653104d47c4ecd114c0dc666b6a7ced9afa211.md',NULL,'ri-5e1aba60eb97','2026-07-06 12:18:04','agent',NULL,'2026-07-06 12:18:04');
INSERT INTO "source_ref" VALUES('src-815dbcf6d1a6','pending',NULL,'web','article','https://qoder.com.cn/pricing',NULL,'Qoder（阿里/原通义灵码）定价与Credits计费体系','2e5e79115d3aecd0754b43043d2ea904531a1be813ad886ff61239dd1310de98','topics/cn_coding_work_products/cache/2e5e79115d3aecd0754b43043d2ea904531a1be813ad886ff61239dd1310de98.md',NULL,'ri-5f1066602d04','2026-07-06 12:18:04','agent',NULL,'2026-07-06 12:18:04');
CREATE INDEX idx_vocab_lookup ON controlled_vocab(vocab_name);
CREATE INDEX idx_source_subject ON source_ref(subject_type, subject_id);
CREATE INDEX idx_source_hash ON source_ref(content_hash);
CREATE INDEX idx_cred_subject ON credibility_assessment(subject_type, subject_id);
CREATE INDEX idx_l3_facet ON l3_claim(facet);
CREATE INDEX idx_l3_parent ON l3_claim(parent_l2_id);
CREATE INDEX idx_l2_facet ON l2_finding(facet);
CREATE INDEX idx_l2_parent ON l2_finding(parent_l1_id);
CREATE INDEX idx_l1_facet ON l1_viewpoint(facet);
CREATE INDEX idx_search_log_facet ON search_log(facet, searched_at);
CREATE INDEX idx_search_log_time ON search_log(searched_at);
CREATE INDEX idx_l0_supersedes ON l0_worldview(supersedes_id);
CREATE INDEX idx_l0_status ON l0_worldview(status);
CREATE TRIGGER trg_source_ref_url_gate BEFORE INSERT ON source_ref
BEGIN
    SELECT CASE WHEN NEW.url IS NULL OR trim(NEW.url) = '' OR lower(NEW.url) = 'dataset'
        THEN RAISE(ABORT, 'source_ref.url must be a real verifiable URL (empty/dataset placeholders forbidden)') END;
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM controlled_vocab v
        WHERE v.vocab_name='source_platform' AND v.status='active'
          AND (v.canonical_value=NEW.platform OR v.alias=NEW.platform)
    ) THEN RAISE(ABORT, 'source_ref.platform not in controlled_vocab(source_platform)') END;
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM controlled_vocab v
        WHERE v.vocab_name='source_kind' AND v.status='active'
          AND (v.canonical_value=NEW.source_kind OR v.alias=NEW.source_kind)
    ) THEN RAISE(ABORT, 'source_ref.source_kind not in controlled_vocab(source_kind)') END;
END;
CREATE TRIGGER trg_l3_snapshot_provenance BEFORE INSERT ON l3_claim
WHEN NEW.context_snapshot_id IS NOT NULL AND trim(NEW.context_snapshot_id) <> ''
BEGIN
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM context_snapshot_log s WHERE s.snapshot_id = NEW.context_snapshot_id
    ) THEN RAISE(ABORT, 'l3_claim.context_snapshot_id not found in context_snapshot_log (forged provenance)') END;
END;
CREATE TRIGGER trg_l2_snapshot_provenance BEFORE INSERT ON l2_finding
WHEN NEW.context_snapshot_id IS NOT NULL AND trim(NEW.context_snapshot_id) <> ''
BEGIN
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM context_snapshot_log s WHERE s.snapshot_id = NEW.context_snapshot_id
    ) THEN RAISE(ABORT, 'l2_finding.context_snapshot_id not found in context_snapshot_log (forged provenance)') END;
END;
CREATE TRIGGER trg_l1_snapshot_provenance BEFORE INSERT ON l1_viewpoint
WHEN NEW.context_snapshot_id IS NOT NULL AND trim(NEW.context_snapshot_id) <> ''
BEGIN
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM context_snapshot_log s WHERE s.snapshot_id = NEW.context_snapshot_id
    ) THEN RAISE(ABORT, 'l1_viewpoint.context_snapshot_id not found in context_snapshot_log (forged provenance)') END;
END;
CREATE TRIGGER trg_l0_snapshot_provenance BEFORE INSERT ON l0_worldview
WHEN NEW.context_snapshot_id IS NOT NULL AND trim(NEW.context_snapshot_id) <> ''
BEGIN
    SELECT CASE WHEN NOT EXISTS (
        SELECT 1 FROM context_snapshot_log s WHERE s.snapshot_id = NEW.context_snapshot_id
    ) THEN RAISE(ABORT, 'l0_worldview.context_snapshot_id not found in context_snapshot_log (forged provenance)') END;
END;
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('controlled_vocab',33);
INSERT INTO "sqlite_sequence" VALUES('knowledge_change_log',22);
COMMIT;
