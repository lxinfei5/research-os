BEGIN TRANSACTION;
CREATE TABLE source_inventory (
    platform      TEXT NOT NULL,
    surface       TEXT NOT NULL,               -- search / favorites / likes / detail / ...
    external_id   TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    last_seen_at  TEXT NOT NULL,
    title         TEXT,
    url           TEXT,
    PRIMARY KEY (platform, surface, external_id)
);
CREATE TABLE source_item (
    id                     TEXT PRIMARY KEY,
    session_id             TEXT NOT NULL REFERENCES source_session(id),
    platform               TEXT,
    source_kind            TEXT,
    url                    TEXT,                -- nullable ONLY when restricted_reason explains why
    title                  TEXT,
    content                TEXT NOT NULL,       -- the captured text (media already transcribed)
    author                 TEXT,
    captured_at            TEXT,
    raw_metadata           TEXT,                -- JSON
    content_hash           TEXT NOT NULL,
    needs_review           INTEGER NOT NULL DEFAULT 1,
    restricted_reason      TEXT,
    promoted_source_ref_id TEXT,               -- set once promoted into knowledge.db
    created_at             TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "source_item" VALUES('ri-703629fb077c','rs-8b0ed31d133d','web','product_pricing','https://www.codebuddy.cn/workbuddy','WorkBuddy（腾讯云CodeBuddy）定价与计费说明','WorkBuddy是腾讯云CodeBuddy团队推出的桌面AI智能体工作台（注意：非字节跳动产品，字节竞品是Trae Work）。核心定位是能干活交付的AI工作台，支持本地文件操作、Claw手机远程操控、Skills技能生态、多专家Agent协作。

【计费模式】积分制
- 2026年7月1日起正式收费
- 标准版：4000积分/月
- 加量包：50元/1000积分
- 新用户首月5000积分体验
- 支持外接自定义API Key免费用

【积分消耗规则】按模型系数计费：
- MiniMax模型系数0.18（最低）
- DeepSeek模型系数0.30
- 简单对话约2-3积分
- PDF/PPT/批量处理是消耗大户

【产品矩阵】属于腾讯CodeBuddy品牌，与Trae Work（字节）、Qoder（阿里）形成国内BAT AI编程工作台三足鼎立格局。',NULL,'2026-07-06 12:17:13',NULL,'ccec42ad631e678279b4df6e68b411b50e7905c9aae1c9f6c4348c01c0fca8eb',1,NULL,NULL,'2026-07-06 12:17:13');
INSERT INTO "source_item" VALUES('ri-5ca98f9c7706','rs-8b0ed31d133d','web','product_pricing','https://work.trae.cn/pricing','Trae Work国内版计费模式分析（对话次数制）','Trae Work是字节跳动推出的AI原生工作台，2026年6月9日由Trae Solo升级而来，面向所有知识工作者（产品/运营/市场/设计/开发）。

【产品线区分】
- Trae国际版（trae.ai）：2025年1月发布，面向海外开发者，2026年2月24日已从请求次数制改为Token计费（五档：Free/Lite/Pro/Pro+/Ultra）
- Trae Work国内版（work.trae.cn）：当前仍采用对话次数制，近期从每日限额改为每周限额

【国内版当前状态】
- 仍采用对话/请求次数制，未跟随国际版切换Token制
- 免费可用：内置Doubao Seed 2.1 Pro/2.1 Turbo、MiniMax、GLM等模型
- Pro版提供优先队列（Fast Pass），高峰期免费用户可能排队
- 支持自定义API Key接入

【早期次数制定价结构（国际版旧方案参考）】
- 免费版：代码补全5000次/月，超级模型快速队列10次/月，慢速队列50次/月
- Pro版（$10/月）：代码补全无限次，快速队列600次/月，慢速队列无限次
- 容量包：$3/100次、$7/300次、$12/600次快速队列

【为什么采用请求次数制——设计逻辑】
1. 用户体验优先：Token是技术概念，普通用户难以理解；"X次/月"符合SaaS订阅心智，类似网盘/视频会员，获客转化率更高
2. 早期成本结构允许：2025年初模型上下文窗口小（8k/32k），Agent能力弱，单次请求token消耗差异不大，按次数"大致公平"
3. 对标竞品行业惯例：Cursor早期Pro版也是500次快速请求，GitHub Copilot长期无限次订阅
4. 产品快速迭代期缓冲：粗粒度但稳定，避免早期频繁调价引发不满；慢速队列无限次平衡成本体验
5. 心理账户优势：避免"Token焦虑"，用户不用每发一句话都算钱，更符合"工具使用"而非"API调用"心智

【为什么国际版后来改为Token制——成本倒逼】
- 上下文窗口从8k/32k→128k/200k/1M+，一次长对话消耗过去10次token量
- Agent模式从单轮→多轮工具调用，一个"请求"背后可能触发10+次模型调用
- 模型差异化（Claude 3.5→Claude 4/Gemini 2.5 Pro）成本差5-10倍
- 重度用户单次会话token量是轻度用户几十倍，次数制下交叉补贴不可持续

【国内版为什么保留次数制】
- 目标用户更广泛（非技术用户对Token接受度低）
- Work/Design模式单次任务token消耗比Code模式更可控
- 国内市场竞争策略：主打"免费够用"，用次数制+限额做用户增长
- 风险点：随着Agent能力增强（自动处理飞书文档、多步自动化），单次"对话"实际token消耗上升，未来可能需要调整',NULL,'2026-07-06 12:17:13',NULL,'829359604d0399ad6be9fd4a994b432959bd1546ae6627145278686be51bbdb5',1,NULL,NULL,'2026-07-06 12:17:13');
INSERT INTO "source_item" VALUES('ri-5601069d867f','rs-8b0ed31d133d','web','product_pricing','https://qoder.com.cn/pricing','Qoder（阿里/原通义灵码）定价与Credits计费体系','Qoder是阿里巴巴推出的AI智能编程平台，采用国内国际双轨运营。2026年5月20日国内版从"通义灵码"更名为Qoder CN，产品矩阵包括Qoder Desktop（IDE）、QoderWork CN（办公）、Qoder CLI、QoderWake（7×24 AI员工）、JetBrains插件、Mobile端。

【计费模式】Credits积分制（统一计量单位）

【全球版定价（qoder.com，美元）】
- Free：免费，有限体验额度，无限代码补全
- Pro：$20/月，2000 Credits/月，含Quest Mode、Repo Wiki、隐私模式
- Pro+：$60/月，6000 Credits/月
- 新用户：2周Pro试用+1000 Credits赠送

【国内版定价（qoder.com.cn，人民币）——约为全球版40%】
- 个人体验版：免费，300 Credits+2周Pro试用，代码补全无限
- 个人专业版Pro：¥59/月，2000 Credits/月
- 个人高级版Pro+：¥169/月，6000 Credits/月
- 企业标准版Teams：¥99/席位/月，3000 Credits/席位/月，1席位起
- 企业VPC版：¥199/席位/月，3000 Credits/席位/月，50席位起

【资源包】
- 个人：¥40/1000 Credits，有效期1个月
- 企业：¥80/2000 Credits，有效期3个月

【Credits消耗规则】
- 消耗Credits：Inline Chat、Ask模式、Agent模式、Quest、Experts专家团、RepoWiki生成
- 不消耗Credits：代码补全和Next Edits（全版本无限免费）
- 模型差异：由任务复杂度和选用模型决定（GLM/DeepSeek/Kimi/MiniMax等）
- 失败不扣费：模型调用失败不扣减
- 消耗优先级：先到期先扣，同到期先扣套餐Credits再扣资源包
- 跨产品共享：个人版Credits可在Desktop/JetBrains/QoderWork/CLI/Mobile间共享
- 国内国际隔离：两套Credits不等价不可互通

【定价策略设计逻辑】
1. 双轨定价：国内Pro ¥59仅为全球$20的40%，适配中国市场购买力
2. Credits抽象层：屏蔽底层多模型token单价差异，用户无需理解技术细节
3. 免费钩子：代码补全全版本无限免费（最高频功能），降低获客门槛
4. 价值收费：Agent/Quest/RepoWiki等高价值智能体功能消耗Credits
5. 企业变现：通义灵码已签约超1万家企业（一汽/蔚来/中华财险等），迁移成本高，2026年5月更名后企业版涨价约25%
6. 资源包设计：到期清零促使用，单价比套餐内高鼓励订阅

【用户反馈】
- 重度用户2000 Credits两三天就清空，需额外买资源包
- 从免费转收费引发"免费时代结束"讨论
- 官方通过工具并行化、上下文压缩使Credits耐用度提升约50%',NULL,'2026-07-06 12:17:13',NULL,'6f60e8830d5aa053e10caed798966809ab94b793f8804d0ef3c19eb1ed70a8a2',1,NULL,NULL,'2026-07-06 12:17:13');
INSERT INTO "source_item" VALUES('ri-83bc822e76c3','rs-0be56b713244','web','article','https://www.codebuddy.cn/workbuddy','WorkBuddy（腾讯云CodeBuddy）定价与计费说明','WorkBuddy是腾讯云CodeBuddy团队推出的桌面AI智能体工作台（注意：非字节跳动产品，字节竞品是Trae Work）。核心定位是能干活交付的AI工作台，支持本地文件操作、Claw手机远程操控、Skills技能生态、多专家Agent协作。

【计费模式】积分制
- 2026年7月1日起正式收费
- 标准版：4000积分/月
- 加量包：50元/1000积分
- 新用户首月5000积分体验
- 支持外接自定义API Key免费用

【积分消耗规则】按模型系数计费：
- MiniMax模型系数0.18（最低）
- DeepSeek模型系数0.30
- 简单对话约2-3积分
- PDF/PPT/批量处理是消耗大户

【产品矩阵】属于腾讯CodeBuddy品牌，与Trae Work（字节）、Qoder（阿里）形成国内BAT AI编程工作台三足鼎立格局。',NULL,'2026-07-06 12:18:04',NULL,'5fbbf592a4b545bb140afbf775245d48515537bff6abf19a51080348ca8c7f33',1,NULL,'src-909ce9fa7145','2026-07-06 12:18:04');
INSERT INTO "source_item" VALUES('ri-5e1aba60eb97','rs-0be56b713244','web','article','https://work.trae.cn/pricing','Trae Work国内版计费模式分析（对话次数制）','Trae Work是字节跳动推出的AI原生工作台，2026年6月9日由Trae Solo升级而来，面向所有知识工作者（产品/运营/市场/设计/开发）。

【产品线区分】
- Trae国际版（trae.ai）：2025年1月发布，面向海外开发者，2026年2月24日已从请求次数制改为Token计费（五档：Free/Lite/Pro/Pro+/Ultra）
- Trae Work国内版（work.trae.cn）：当前仍采用对话次数制，近期从每日限额改为每周限额

【国内版当前状态】
- 仍采用对话/请求次数制，未跟随国际版切换Token制
- 免费可用：内置Doubao Seed 2.1 Pro/2.1 Turbo、MiniMax、GLM等模型
- Pro版提供优先队列（Fast Pass），高峰期免费用户可能排队
- 支持自定义API Key接入

【早期次数制定价结构（国际版旧方案参考）】
- 免费版：代码补全5000次/月，超级模型快速队列10次/月，慢速队列50次/月
- Pro版（$10/月）：代码补全无限次，快速队列600次/月，慢速队列无限次
- 容量包：$3/100次、$7/300次、$12/600次快速队列

【为什么采用请求次数制——设计逻辑】
1. 用户体验优先：Token是技术概念，普通用户难以理解；"X次/月"符合SaaS订阅心智，类似网盘/视频会员，获客转化率更高
2. 早期成本结构允许：2025年初模型上下文窗口小（8k/32k），Agent能力弱，单次请求token消耗差异不大，按次数"大致公平"
3. 对标竞品行业惯例：Cursor早期Pro版也是500次快速请求，GitHub Copilot长期无限次订阅
4. 产品快速迭代期缓冲：粗粒度但稳定，避免早期频繁调价引发不满；慢速队列无限次平衡成本体验
5. 心理账户优势：避免"Token焦虑"，用户不用每发一句话都算钱，更符合"工具使用"而非"API调用"心智

【为什么国际版后来改为Token制——成本倒逼】
- 上下文窗口从8k/32k→128k/200k/1M+，一次长对话消耗过去10次token量
- Agent模式从单轮→多轮工具调用，一个"请求"背后可能触发10+次模型调用
- 模型差异化（Claude 3.5→Claude 4/Gemini 2.5 Pro）成本差5-10倍
- 重度用户单次会话token量是轻度用户几十倍，次数制下交叉补贴不可持续

【国内版为什么保留次数制】
- 目标用户更广泛（非技术用户对Token接受度低）
- Work/Design模式单次任务token消耗比Code模式更可控
- 国内市场竞争策略：主打"免费够用"，用次数制+限额做用户增长
- 风险点：随着Agent能力增强（自动处理飞书文档、多步自动化），单次"对话"实际token消耗上升，未来可能需要调整',NULL,'2026-07-06 12:18:04',NULL,'7f09ba536dab8566e1820955ea653104d47c4ecd114c0dc666b6a7ced9afa211',1,NULL,'src-fc7ca176df63','2026-07-06 12:18:04');
INSERT INTO "source_item" VALUES('ri-5f1066602d04','rs-0be56b713244','web','article','https://qoder.com.cn/pricing','Qoder（阿里/原通义灵码）定价与Credits计费体系','Qoder是阿里巴巴推出的AI智能编程平台，采用国内国际双轨运营。2026年5月20日国内版从"通义灵码"更名为Qoder CN，产品矩阵包括Qoder Desktop（IDE）、QoderWork CN（办公）、Qoder CLI、QoderWake（7×24 AI员工）、JetBrains插件、Mobile端。

【计费模式】Credits积分制（统一计量单位）

【全球版定价（qoder.com，美元）】
- Free：免费，有限体验额度，无限代码补全
- Pro：$20/月，2000 Credits/月，含Quest Mode、Repo Wiki、隐私模式
- Pro+：$60/月，6000 Credits/月
- 新用户：2周Pro试用+1000 Credits赠送

【国内版定价（qoder.com.cn，人民币）——约为全球版40%】
- 个人体验版：免费，300 Credits+2周Pro试用，代码补全无限
- 个人专业版Pro：¥59/月，2000 Credits/月
- 个人高级版Pro+：¥169/月，6000 Credits/月
- 企业标准版Teams：¥99/席位/月，3000 Credits/席位/月，1席位起
- 企业VPC版：¥199/席位/月，3000 Credits/席位/月，50席位起

【资源包】
- 个人：¥40/1000 Credits，有效期1个月
- 企业：¥80/2000 Credits，有效期3个月

【Credits消耗规则】
- 消耗Credits：Inline Chat、Ask模式、Agent模式、Quest、Experts专家团、RepoWiki生成
- 不消耗Credits：代码补全和Next Edits（全版本无限免费）
- 模型差异：由任务复杂度和选用模型决定（GLM/DeepSeek/Kimi/MiniMax等）
- 失败不扣费：模型调用失败不扣减
- 消耗优先级：先到期先扣，同到期先扣套餐Credits再扣资源包
- 跨产品共享：个人版Credits可在Desktop/JetBrains/QoderWork/CLI/Mobile间共享
- 国内国际隔离：两套Credits不等价不可互通

【定价策略设计逻辑】
1. 双轨定价：国内Pro ¥59仅为全球$20的40%，适配中国市场购买力
2. Credits抽象层：屏蔽底层多模型token单价差异，用户无需理解技术细节
3. 免费钩子：代码补全全版本无限免费（最高频功能），降低获客门槛
4. 价值收费：Agent/Quest/RepoWiki等高价值智能体功能消耗Credits
5. 企业变现：通义灵码已签约超1万家企业（一汽/蔚来/中华财险等），迁移成本高，2026年5月更名后企业版涨价约25%
6. 资源包设计：到期清零促使用，单价比套餐内高鼓励订阅

【用户反馈】
- 重度用户2000 Credits两三天就清空，需额外买资源包
- 从免费转收费引发"免费时代结束"讨论
- 官方通过工具并行化、上下文压缩使Credits耐用度提升约50%',NULL,'2026-07-06 12:18:04',NULL,'2e5e79115d3aecd0754b43043d2ea904531a1be813ad886ff61239dd1310de98',1,NULL,'src-815dbcf6d1a6','2026-07-06 12:18:04');
INSERT INTO "source_item" VALUES('ri-4a03d63638cb','rs-21a5fc2d9cea','web','article','http://m.toutiao.com/group/7650866693463409187/','智谱GLM 5.2全量开放！国产新高峰，1M上下文，Coding Plan限额开放','2026年6月13日，智谱宣布GLM-5.2面向GLM Coding Plan全量用户开放，覆盖Lite、Pro、Max和团队版。GLM 5.2是智谱迄今能力最强的开源模型，核心升级点包括：支持真正可用的1M上下文长度；在长程任务中继续保持领先；幻觉极低；指令遵循能力强，400-500K上下文下与Claude差距不大；纯文本模型（不支持多模态）。遵循MIT协议开源。实测表现：稳但慢——在10万行代码项目中排查监控故障全程21分钟（Claude Opus 4.8 fast模式6分钟），过程结果几乎一样但速度差2倍多，这是算力基建差距而非模型能力差距。GLM 5.2在Skill构建方面也让人惊喜，具备支撑复杂自动化流程的能力。最大短板是不支持多模态。智谱Coding Plan是限额的需每天抢，反映国产模型infra和算力差距。API下周上线，模型正式开源。','观察者','2026-07-06 13:15:08',NULL,'945818fc55f83b5ed0f9330db78ecdd6fcb07aeeecf0bf2641b9450bc354be64',1,NULL,'src-ecf96379cac9','2026-07-06 13:15:08');
INSERT INTO "source_item" VALUES('ri-2593b6183da0','rs-21a5fc2d9cea','web','official_doc','https://docs.trae.cn/work_models.md','TRAE Work 模型管理（预置模型与自定义模型）','TRAE Work提供灵活的模型管理功能，既可使用预置模型也可添加自定义模型。预置模型列表——Work模式：TRAE Auto Model、Doubao-Seed-2.1-Pro（仅优速通Express和速通Ultra用户）、Doubao-Seed-2.1-Turbo、MiniMax-M3、MiniMax-M2.7、GLM-5.2、GLM-5-Turbo、GLM-5、DeepSeek-V4-Pro、DeepSeek-V4-Flash、Kimi-K2.7-Code、Kimi-K2.6。Code模式：上述多数加GLM-5.1、GLM-5V-Turbo、Qwen3.7-Plus、Qwen3.6-Plus。使用TRAE Auto Model时系统智能调用合适模型。关键发现：预置模型的上下文窗口大小在官方文档中未明确说明/未公开；仅「添加自定义模型」时允许用户手动配置「上下文窗口-输入」和「上下文窗口-输出」（设置单次请求可接收/响应的最大Token数）。这意味着预置模型（含GLM-5.2）的实际上下文配额由TRAE Work内部管理，不暴露给用户。自定义模型还支持配置工具调用轮次、多模态开关。仅TRAE Work桌面版支持添加自定义模型且仅本地环境使用。','TRAE官方文档','2026-07-06 13:15:08',NULL,'4cc9dab0256d003b7a61fc6bab83d15a56ebce6430c105f0c7091af6a5c0e1ff',1,NULL,NULL,'2026-07-06 13:15:08');
INSERT INTO "source_item" VALUES('ri-f5005e873491','rs-21a5fc2d9cea','web','official_doc','https://docs.trae.cn/ide_context-compaction.md','TRAE Work 上下文压缩（Context Compaction）机制','每个对话都拥有独立的上下文管理进程。随着问询不断发送，对话上下文逐步累积，上下文窗口决定了单个对话可保留和记忆的上下文长度。使用限制：仅适用于SOLO Agent（即TRAE Work）。查看上下文使用率：每轮对话结束后底部显示模型可用的上下文窗口及本轮上下文使用率。压缩上下文：当使用的上下文超过允许的上下文窗口时，系统自动触发一次上下文压缩；也可点击上下文使用率面板上的「压缩」按钮手动触发。通过压缩移除冗余信息仅保留关键内容，确保AI聚焦核心上下文并维持输出质量。开启新会话后先前上下文将被清空。关键推断：Trae Work对每个对话有「允许的上下文窗口」上限，超过即触发compaction而非报错；该上限是否等于模型原生上下文（如GLM-5.2的1M）文档未明确，但compaction机制的存在说明平台对上下文做了一定管理/限制，可能不暴露模型原生完整窗口。','TRAE官方文档','2026-07-06 13:15:08',NULL,'d7c2736a2ede2392117762678d1901fb93acd4289b3a67dc2021ae134ae91fc3',1,NULL,NULL,'2026-07-06 13:15:08');
INSERT INTO "source_item" VALUES('ri-d66a4d935e8b','rs-f75a4ec5300e','web','web_page','https://docs.trae.cn/work_models.md','TRAE Work 模型管理（预置模型与自定义模型）','TRAE Work提供灵活的模型管理功能，既可使用预置模型也可添加自定义模型。预置模型列表——Work模式：TRAE Auto Model、Doubao-Seed-2.1-Pro（仅优速通Express和速通Ultra用户）、Doubao-Seed-2.1-Turbo、MiniMax-M3、MiniMax-M2.7、GLM-5.2、GLM-5-Turbo、GLM-5、DeepSeek-V4-Pro、DeepSeek-V4-Flash、Kimi-K2.7-Code、Kimi-K2.6。Code模式：上述多数加GLM-5.1、GLM-5V-Turbo、Qwen3.7-Plus、Qwen3.6-Plus。使用TRAE Auto Model时系统智能调用合适模型。关键发现：预置模型的上下文窗口大小在官方文档中未明确说明/未公开；仅「添加自定义模型」时允许用户手动配置「上下文窗口-输入」和「上下文窗口-输出」（设置单次请求可接收/响应的最大Token数）。这意味着预置模型（含GLM-5.2）的实际上下文配额由TRAE Work内部管理，不暴露给用户。自定义模型还支持配置工具调用轮次、多模态开关。仅TRAE Work桌面版支持添加自定义模型且仅本地环境使用。','TRAE官方文档','2026-07-06 13:15:51',NULL,'19e4b778919c6fbd2e1732bbf7e0448498c30725aec2496c28d63f8e5aff8afc',1,NULL,'src-5143c8a8edfd','2026-07-06 13:15:51');
INSERT INTO "source_item" VALUES('ri-c62cc2dac4ac','rs-f75a4ec5300e','web','web_page','https://docs.trae.cn/ide_context-compaction.md','TRAE Work 上下文压缩（Context Compaction）机制','每个对话都拥有独立的上下文管理进程。随着问询不断发送，对话上下文逐步累积，上下文窗口决定了单个对话可保留和记忆的上下文长度。使用限制：仅适用于SOLO Agent（即TRAE Work）。查看上下文使用率：每轮对话结束后底部显示模型可用的上下文窗口及本轮上下文使用率。压缩上下文：当使用的上下文超过允许的上下文窗口时，系统自动触发一次上下文压缩；也可点击上下文使用率面板上的「压缩」按钮手动触发。通过压缩移除冗余信息仅保留关键内容，确保AI聚焦核心上下文并维持输出质量。开启新会话后先前上下文将被清空。关键推断：Trae Work对每个对话有「允许的上下文窗口」上限，超过即触发compaction而非报错；该上限是否等于模型原生上下文（如GLM-5.2的1M）文档未明确，但compaction机制的存在说明平台对上下文做了一定管理/限制，可能不暴露模型原生完整窗口。','TRAE官方文档','2026-07-06 13:15:51',NULL,'5c6989a24555f530cd50edb30c6adfaefecab6977afb441cc8ff314eb98871fd',1,NULL,'src-9e1192eb5de0','2026-07-06 13:15:51');
INSERT INTO "source_item" VALUES('ri-32d10ccb741e','rs-e471649ef710','xiaohongshu','note','https://www.xiaohongshu.com/discovery/item/6a325313000000000f030d61','GLM 5.2 编程实测：真实前端工程长链路测试','GLM 5.2 编程实测：真实前端工程长链路测试。互动:赞114 评10 藏49 转7。详情正文因风控墙未取，列表卡片为B类证据。xsec_token=AByrLAvLJKYHAzqoARRzQQtbuPsvL3mayqDglKZ2YM4Ig=','杰森的效率工坊','2026-07-06 13:48:03',NULL,'ea808360ea1ef2b72d32c13cb43d34a908c0b8b4d3f9ef2ed766d5232c11b29b',1,'xhs_anti_bot_wall: get_feed_detail 返回 Page Isn''t Available Right Now + 扫码提示，按 source_health_and_degradation.md §三 降级为列表卡片','src-a7994267d68a','2026-07-06 13:48:03');
INSERT INTO "source_item" VALUES('ri-55fa2c992e10','rs-e471649ef710','xiaohongshu','note','https://www.xiaohongshu.com/discovery/item/698e8766000000001a02fe29','TRAE 国际版计费方案将升级','TRAE官方账号发布国际版计费方案升级公告。互动:赞178 评148 藏44 转79。详情正文因风控墙未取。此条与 facet 直接相关:计费方案升级可能涉及上下文配额调整。xsec_token=ABNmXM3Tme5CEX4qdoD6tEuZx4vSWJfa1nE8b-2S-7PcM=','TRAE','2026-07-06 13:48:03',NULL,'745c457e7eacd722ecfac5908cb098046876a8fc59f3eaae689568e9158f2d98',1,'xhs_anti_bot_wall: 风控墙触发后按协议不取后续detail','src-37f4e8b87ccc','2026-07-06 13:48:03');
INSERT INTO "source_item" VALUES('ri-7dac40d8344a','rs-e471649ef710','xiaohongshu','note','https://www.xiaohongshu.com/discovery/item/69d0e65b000000001f003cdc','尝试了WorkBuddy，我有些话必须说一说','WorkBuddy使用评测。互动:赞635 评44 藏603 转136。详情未取(风控墙)。作为竞品对比参考。xsec_token=ABcVe5PA50BqeYGq_rlFkN2by_NcKJ-OLpihL7qfnSfzQ=','跟着阿亮学AI','2026-07-06 13:48:03',NULL,'88fc619fe99700c5404a3fce2de307c64c13e8ee442005f8ec97a6a4f55f7fcd',1,'xhs_anti_bot_wall','src-41d95da883f6','2026-07-06 13:48:03');
INSERT INTO "source_item" VALUES('ri-9749465f8bef','rs-b8dfbc6a9f4b','x','post','https://x.com/HazardKrypto/status/2073840034336141363','GLM-5.2 参数与上下文窗口规格披露','China just dropped a bombshell: Zhipu AI''s GLM-5.2. 744B total params (40B active per token MoE). 256K context window, 131K output cap. Ranks #1 among open models. Beats Claude Opus 4.8 in multiple coding benchmarks. MIT licensed, free weights. The open-source gap is closing FAST.','HazardKrypto','2026-07-06 13:48:03',NULL,'c31e687f8758c39eda53a4b304f55ed0d7090b2ec25d23ec7322ea262f353a9e',1,NULL,'src-6c703319eb56','2026-07-06 13:48:03');
INSERT INTO "source_item" VALUES('ri-73ca149804bb','rs-b8dfbc6a9f4b','x','post','https://x.com/Nuzanthra/status/2073770838021804506','GLM-5.2 1M context window 可用性确认','SiliconFlow Spotlight: GLM-5.2 is HERE! Z.ai flagship open-source model dengan: 1M context window (benar-benar usable/真正可用), Long-horizon agentic engineering, Near Opus-level coding performance. Builder wajib coba!','Nuzanthra','2026-07-06 13:48:03',NULL,'e05a6442f3433f4555865e9c172fee665f3c820a6c0bc736880fca5c9c4380b4',1,NULL,'src-d4224cf9f130','2026-07-06 13:48:03');
INSERT INTO "source_item" VALUES('ri-0c014318378c','rs-b8dfbc6a9f4b','x','post','https://x.com/myanvoos/status/2073933187651420316','GLM 5.2 本地部署长上下文实测(~100k)','my inability to get 2 more @NVIDIAAI DGX Sparks have led to a truly cursed custom fork of ik-llama-cpp, so that I now have a custom ~3.6 bpw quant of @0xSero''s GLM 5.2 REAP running at 13 decode tok/s with very usable long-context prefill (via DSA) and ~100k context window on just [本地硬件]. 本地部署可跑约100k上下文。','myanvoos','2026-07-06 13:48:03',NULL,'c5c866d49be0f27f89aa823098d4afe6a1e7ff9097d801c3a8755fbf2938783e',1,NULL,'src-762619a5e098','2026-07-06 13:48:03');
INSERT INTO "source_item" VALUES('ri-73557dfef19e','rs-b8dfbc6a9f4b','x','post','https://x.com/AaronRossPreIPO/status/2074093514926006493','GLM-5.2 agentic benchmark 接近 Anthropic','BREAKING: A Chinese open-source model is now landing within roughly 1% of Anthropic''s best on a key agentic benchmark — at about one-fifth the cost. Zhipu AI (now Z.ai) released GLM-5.2 under a permissive open-weight license: 750B parameters, a 1M-token [context window].','AaronRossPreIPO','2026-07-06 13:48:03',NULL,'b48c9f17b97aa22f043a6c53650fe0bd4c98f6e1fd8930ee93abd74ddff40d3d',1,NULL,'src-39a1a72fd163','2026-07-06 13:48:03');
CREATE TABLE source_session (
    id              TEXT PRIMARY KEY,
    query           TEXT NOT NULL,
    source          TEXT NOT NULL,             -- web / x / douyin / xiaohongshu / manual / ...
    collector       TEXT,                      -- which mechanism (web_search / xiaohongshu-mcp / ...)
    capture_kind    TEXT NOT NULL DEFAULT 'search',
    searched_at     TEXT NOT NULL,
    expires_at      TEXT,
    captured_by     TEXT,
    result_count    INTEGER,
    degraded_reason TEXT,
    raw_tool_status TEXT,
    run_id          TEXT,
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "source_session" VALUES('rs-8b0ed31d133d','国内AI Coding/Work产品计费模式对比：WorkBuddy、Trae Work、Qoder定价与积分/次数/Token机制研究','web','agent','research','2026-07-06 12:17:13',NULL,'agent',3,NULL,NULL,NULL,NULL,'2026-07-06 12:17:13');
INSERT INTO "source_session" VALUES('rs-0be56b713244','国内AI Coding/Work产品计费模式对比：WorkBuddy、Trae Work、Qoder定价与积分/次数/Token机制研究','web','agent','research','2026-07-06 12:18:04',NULL,'agent',3,NULL,NULL,NULL,NULL,'2026-07-06 12:18:04');
INSERT INTO "source_session" VALUES('rs-21a5fc2d9cea','Trae Work 预置模型上下文窗口 GLM-5.2 1M context限制','web','web_search','search','2026-07-06 13:15:08',NULL,'agent',3,NULL,NULL,NULL,NULL,'2026-07-06 13:15:08');
INSERT INTO "source_session" VALUES('rs-f75a4ec5300e','Trae Work 预置模型上下文窗口 GLM-5.2 1M context限制','web','web_search','search','2026-07-06 13:15:51',NULL,'agent',2,NULL,NULL,NULL,NULL,'2026-07-06 13:15:51');
INSERT INTO "source_session" VALUES('rs-e471649ef710','Trae Work GLM 上下文 (xhs 社媒观点)','xiaohongshu','xiaohongshu-mcp','search','2026-07-06 13:48:03',NULL,'agent',3,'xhs get_feed_detail 触发风控墙(Page Isn''t Available Right Now+扫码提示)，按协议STOP不重试，仅落列表卡片(B类证据)，详情待下一轮登录态恢复后补',NULL,NULL,NULL,'2026-07-06 13:48:03');
INSERT INTO "source_session" VALUES('rs-b8dfbc6a9f4b','GLM-5.2 context window 1M (x 社媒观点)','x','kimi-webbridge','search','2026-07-06 13:48:03',NULL,'agent',4,NULL,NULL,NULL,NULL,'2026-07-06 13:48:03');
CREATE INDEX idx_source_item_hash ON source_item(content_hash);
CREATE INDEX idx_source_item_promoted ON source_item(promoted_source_ref_id);
COMMIT;
