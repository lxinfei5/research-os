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
INSERT INTO "credibility_assessment" VALUES('cred-bd7d9523e853','l3_claim','sc-11a55df94bdc','medium','来自 Z.ai 官方博客，对训练方法的描述具体且与主流后训练/RL 实践逻辑相容，但属厂商自述单一来源、有自利偏向，未经独立印证。','{"independence": "单一来源，且为厂商官方自述，非独立第三方", "quality_density": "有具体技术主张（自生成经验、RL 提升 agentic），密度中等但偏纲领性", "recency": "GLM-4.5 时期信息，对快速演进的模型能力归因仍基本有效"}','厂商对自家模型的能力归因，存在营销/自利动机',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-209e460189bb','l3_claim','sc-2b2192f12ab2','high','作者为知名 ML 教育者，内容是被广泛接受的方法论框架性归纳，可证伪且与领域共识一致。','{"independence": "单一署名作者的综述，但归纳的是行业公认范式，非孤立主张。", "quality_density": "信息密度高、分类清晰、可对照公开评测实践验证。", "recency": "评测方法论框架属慢变知识，时效性强、近期仍有效。"}','单源综述，需在 aggregate 阶段与其他评测方法论来源印证四范式分类。',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-3593be4c7410','l3_claim','sc-2ccd341d5a49','medium','BentoML 技术博客对 DeepSeek 模型谱系的结构化梳理，信息密度高、可与公开技术报告交叉核验，但为单一厂商博客来源、未经多源印证。','{"independence": "单一 web 来源（BentoML 厂商博客），未交叉印证", "quality_density": "高密度、技术性强、区分清晰、可证伪", "recency": "DeepSeek 模型谱系为快变主题，V3.1/V3.2 信息需注意时效"}','单源，需在 aggregate 阶段与 DeepSeek 官方技术报告等其他 L3 印证',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-e5065c9649e5','l3_claim','sc-31aa86ba36c6','medium','观点与学界公认的基准污染问题一致、逻辑自洽，但为单篇博客综述、无具体数据或独立来源支撑，故定 medium。','{"independence": "单一博客来源，未见独立佐证，但所述为业内广泛讨论的共识性问题", "quality_density": "中等：点明污染与选择性报告两类机制，但缺具体案例/量化数据", "recency": "2026 主题，时效性强且仍然有效"}','单源，主张本身属业内共识但本文未提供独立证据链',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-82abc78b6d75','l3_claim','sc-3ca3e849fc84','high','arXiv 论文来源，论点与标题一致、可证伪且与已知的预训练-后训练耦合机制逻辑相容。','{"independence": "单一论文来源，作为单源 L3 不做跨源印证", "quality_density": "信息密度高、有明确可证伪主张（放大而非创造）", "recency": "2025 年论文，针对当前 RL 后训练范式，时效有效"}','单源，需在 aggregate 阶段与其他来源印证',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-6b94d36f98a0','l3_claim','sc-4187ecc7670a','high','来源为 DeepSeek-AI 官方 arXiv 论文，第一手技术报告，主张可证伪且有明确方法(GRPO)与模型(R1-Zero)支撑。','{"independence": "第一手论文来源，非转发；具体可信度评估需后续多源印证 GRPO 纯 RL 涌现推理的可复现性", "quality_density": "信息密度高，含具体方法(GRPO)、具体模型(R1-Zero)与可证伪主张", "recency": "2501 arXiv，对应 2025 年初发布，在 LLM 后训练快变领域仍属当前有效"}','单一官方来源；''纯 RL 即可涌现推理''这一强主张应在 aggregate 阶段寻求独立第三方复现作为印证',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-d17e7e6cded5','l3_claim','sc-58dc963c403e','high','arXiv 一手论文(DeepSeek-AI 官方)，主张可证伪且方法细节明确(GRPO、R1-Zero 消融)，与已公开的后训练范式逻辑一致。','{"independence": "原始一手来源(论文作者团队)，非转发；但单源，印证需 aggregate 阶段补充", "quality_density": "高密度、有具体方法名(GRPO)与可复现主张，非空泛口号", "recency": "2025 年发布，对快速演进的 LLM 训练范式仍属当前有效"}','一手 arXiv 论文，作者即研究方；可信度来自来源权威性而非多源印证',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-321130a8005b','l3_claim','sc-6ca9092e82c4','high','来源为 arXiv 学术论文，基于用户/开发者调查的实证依据，主张可证伪且与基准评测局限性的已有认知逻辑相容','{"independence": "学术论文引用用户/开发者调查作为独立证据，非单一信息源转发", "quality_density": "主张具体、可证伪，指向''榜单—应用''系统性 gap 这一明确现象", "recency": "2025 年论文（arXiv 2502），LLM 评测主题时效性仍有效"}','调查样本提供了与论文作者独立的证据来源',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-95e4c6973c63','l3_claim','sc-72d323b6684d','high','来自署名技术综述作者（Sebastian Raschka）的公开长文，对 RL 训练管线的归纳与公开技术共识一致，可证伪且有具体方法指称。','{"independence": "单一作者综述，但综合了 DeepSeek-R1 等多方公开工作，非单点转发", "quality_density": "信息密度高，明确指出 SFT→RLHF 管线与 GRPO 算法等可核查细节", "recency": "推理模型 RL 为快变领域，但 GRPO 主流化为近期且仍有效的判断"}','综述本身引述 DeepSeek-R1 原始工作，主张可回溯到一手来源',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-158b7597f4f7','l3_claim','sc-7964a56c9335','medium','行业博客的分析性判断，论点明确且与当前趋势逻辑契合，但为单一来源、缺乏独立数据支撑。','{"independence": "单一博客来源，无交叉印证", "quality_density": "论点清晰但偏口号式，缺少量化或具体证据", "recency": "2026 主题，时效性强且当前有效"}','需多源印证后方可升至 high',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-e88b9a9a3c36','l3_claim','sc-7dede751e3ed','medium','提供了具体任务数(74)与提升幅度(27%)且声称为真实任务，信息密度较高，但为厂商口径经媒体转述，缺乏独立来源印证。','{"independence": "单一媒体报道转述厂商评测，未见独立第三方复现", "quality_density": "有具体任务数与量化提升幅度，可证伪性较强", "recency": "2025-09 发布，对快速迭代的模型能力对比时效性有限"}','GLM-4.6 与对照 Claude Sonnet 4 的对比来自发布方设定的测试环境，存在自评偏向风险',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-5264012f44ea','l3_claim','sc-99f479cd396a','high','DeepSeek 官方技术报告，对自身架构与训练流程的一手描述，细节具体可证伪。','{"independence": "单一官方一手来源（厂商自述），非多源印证", "quality_density": "信息密度高，含具体参数（671B/37B/14.8T/FP8）与方法名，可证伪", "recency": "2024 年底发布，技术细节在当前仍有效"}','厂商自述，需注意自我宣传倾向；性能声明应由独立评测印证',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-3c70745374ce','l3_claim','sc-9b2c7003b24e','medium','来自 Z.ai 官方博客，作为厂商对自家技术路线的第一手陈述可信度较高，但属单一利益相关方来源、无独立印证且带营销倾向，故封顶为 medium。','{"independence": "单一官方来源，厂商自述，无第三方独立印证", "quality_density": "有具体技术归因（agentic RL 后训练、规模/领域/执行模式），但偏概括、缺可证伪细节", "recency": "新发布模型说明，时效性强"}','厂商一方来源，存在自我宣传动机，需后续第三方评测印证',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-18d0b7d95ffe','l3_claim','sc-af535cfe5856','medium','论坛聚合观点信息密度中等且自带反例边界，但本质是社区主观共识、单一来源、缺乏独立基准数据支撑。','{"independence": "单一 Reddit 帖子聚合多名用户发言，但相互间非独立来源，且无第三方基准印证", "quality_density": "有明确论点和限定条件（长程任务例外），密度中等，可证伪但缺乏量化", "recency": "GLM 4.6 / 模型能力快变主题，结论时效性短，易随新版本过期"}','帖内多用户但同属一个回音环境，未达跨平台独立印证',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-d0cd3fd77e70','l3_claim','sc-af60abb265ae','medium','BentoML 技术博客对 DeepSeek 模型谱系的归纳，与公开认知一致且可证伪，但为单一二手来源、无一手数据印证。','{"independence": "单一厂商技术博客，未见多源交叉印证", "quality_density": "信息密度高、区分清晰、可证伪（V3/R1/V3.x 分工具体）", "recency": "DeepSeek 模型谱系为近期话题，信息仍有效"}','单源，需后续 X/其他技术博客对『推理来自后训练』这一主张做印证或反驳',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-6961406d5997','l3_claim','sc-b38eebc5068b','medium','LessWrong 对齐社区的分析性长文，论证有结构且可证伪，但为单一来源观点而非多源实证，故定为 medium。','{"independence": "单一来源（一篇 LessWrong 帖），尚无其他独立来源印证，留待 aggregate 阶段计数。", "quality_density": "信息密度高、提出可检验的机制性主张（泛化 vs 遵从分离），非空泛口号。", "recency": "对齐方法论类主张时效衰减较慢，当前仍有效。"}','社区博客平台的署名分析，需与同类研究/论文交叉印证后才能升级可信度。',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-dfb0085c32f9','l3_claim','sc-b74804fcf5c7','medium','单一科技媒体报道的实测数据，方法（真实任务而非榜单）较可信但样本有限且属厂商相关语境，缺乏独立第三方复现。','{"independence": "单一来源（量子位），无独立复现，独立性弱", "quality_density": "有具体数字（74 任务、27% 提升、对比对象明确），密度中等且可证伪", "recency": "2025-09 报道，模型评测时效性强，短期内有效"}','需 X / 小红书 / 其他评测来源对 GLM-4.6 vs Sonnet 4 的编程能力交叉印证',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-05fd47305e1a','l3_claim','sc-c0905de7e5b9','high','一手官方技术报告，工程细节具体可证伪（参数量、激活量、token规模、精度方案均为可核验的硬指标）。','{"independence": "单一来源（厂商自述），独立性有限，但属一手原始文档而非转发", "quality_density": "信息密度高，含具体架构与训练参数，可证伪", "recency": "2024年底发布的技术报告，对应当前模型版本，时效有效"}','厂商自述存在自利倾向，能力归因类陈述宜由第三方评测交叉印证',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-997237e8dbcf','l3_claim','sc-d8de7d0e5f8b','medium','作者为公认的后训练领域专业评论者，论断逻辑自洽且与公开趋势相符，但为单源观点性主张、缺乏直接可证伪的数据。','{"independence": "单一来源、单一作者观点，未见独立印证", "quality_density": "密度中等，提出明确机制性主张（多轮 RL、可扩展性）但无量化证据", "recency": "后训练范式为当前活跃议题，信息时效良好"}','单源专家分析，需后续多源印证方可升至 L2',0,NULL,'active',NULL,'2026-06-29 14:12:48');
INSERT INTO "credibility_assessment" VALUES('cred-d9fa15a02413','l2_finding','sf-167c98c7a77d','medium','单一来源的分析性主张，与已确立的''按能力维度评估''世界知识逻辑相容，但缺乏独立多源印证','{"independence": "仅单一 web 来源，无跨平台印证", "quality_density": "有明确论断且可证伪，但为综合性分析而非细节数据"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-87fe04064c2a','l2_finding','sf-874f2aec7370','high','DeepSeek-R1 的纯 RL 涌现推理为公开技术报告所述、可证伪且有方法细节，但当前仅单一来源支撑，尚待跨源印证。','{"independence": "目前仅 1 个 web 来源，未见独立第二来源印证，印证数=1", "quality_density": "信息密度高、含具体方法(GRPO/R1-Zero/零 SFT)且可证伪"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-58d5428334d1','l2_finding','sf-a6d4df16e1e2','medium','单一 web 来源的分析性主张，论点具体且可证伪、与已知对齐研究逻辑契合，但缺乏独立来源印证。','{"independence": "仅 1 个 web 来源，无跨源印证", "quality_density": "信息密度高、提出可检验的机制性区分（指令遵从 vs 泛化）"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-8f818375fe27','l2_finding','sf-a2e5d84a57a5','medium','对评测范式的结构化梳理，分类清晰且可证伪，但为单源综述、无外部印证。','{"independence": "单一 web 来源，无第二来源印证", "quality_density": "信息密度高、分类明确，属可核对的领域常识"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-a1756699f132','l2_finding','sf-33b689a9479f','high','数据污染与选择性报告是评测领域已被广泛记录的失真机制，论证可证伪且与已知世界知识高度契合。','{"independence": "单源，但所述机制为业界公认", "quality_density": "指出具体失真路径（污染+cherry-pick），密度高", "logic_fit": "与 F: 评测应按能力维度拆解的趋势相容"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-97e823914719','l2_finding','sf-6d6c2e25a19b','high','两条来源对 DeepSeek 模型分工的描述高度一致，且与公开技术报告吻合；但两源内容近乎雷同，独立性存疑。','{"independence": "两条 web 来源表述近乎一致，可能同源，独立性弱", "quality_density": "对各模型职责的划分具体且与已知架构相符"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-7012b5470dee','l2_finding','sf-242bb45a889d','high','技术细节（MoE 规模、MLA、FP8、14.8T tokens）具体且与 DeepSeek-V3 公开论文一致，可核对；两源高度一致。','{"independence": "两条 web 来源表述高度重叠，可能同源", "quality_density": "含可验证的具体参数与训练规模，密度极高"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-9d034e5be380','l2_finding','sf-312d6735f06d','high','与 DeepSeek-R1 公开论文核心结论一致，具体且可证伪。','{"independence": "单源，但与已发表论文吻合", "quality_density": "明确指出 GRPO 与 R1-Zero 的纯 RL 路径，密度高"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-9858826b4963','l2_finding','sf-812655669c1e','medium','GRPO 在开源社区流行属可观察趋势，但''主流''为定性判断、单源、缺量化支撑。','{"independence": "单一 web 来源", "quality_density": "趋势判断合理但偏定性", "recency": "RL 算法生态快变，需持续核对"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-460840601a9e','l2_finding','sf-2c1dc5d8383d','high','三源共同勾勒''后训练成为核心轴''这一行业共识，并保留了关于其与预训练耦合的关键修正，论证密度高、逻辑自洽。','{"independence": "三条 web 来源，至少在归因侧呈现不同立场，独立性中等", "quality_density": "既给出主张又给出对立修正，密度高"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-42a028833a22','l2_finding','sf-6d8fcfa55696','medium','有具体测试规模（74 任务）与量化提升（~27%），但属厂商口径自报基准、两源内容雷同、独立性弱，易选择性报告。','{"independence": "两条 web 来源表述几乎相同，疑同源/同一基准的转述，独立性弱", "quality_density": "含具体数字与测试条件，密度高但来源利益相关", "recency": "模型版本迭代快，结论时效短"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-994a7fe63acb','l2_finding','sf-e5f1ef7d1018','medium','为社区共识性意见，区分了''编码能力''与''最长程任务''两个维度，论证克制合理，但本质是主观判断、单源。','{"independence": "单一 web 来源，转述社区共识", "quality_density": "对能力维度做了有价值的区分", "logic_fit": "与 GLM-4.6 编码强但 Anthropic 长程占优的其它信号相容"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-7bd2bf9a0cd7','l2_finding','sf-7f67b051fc29','medium','归因合理且与''后训练成为核心轴''的趋势一致，但为单源定性归因、缺可核对的训练细节。','{"independence": "单一 web 来源", "quality_density": "归因明确但偏定性、无量化", "logic_fit": "与后训练/agentic RL 决定长程能力的世界知识相容"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-533389d2801d','l2_finding','sf-d33060f03b1c','medium','单一 web 来源的技术分析，密度高且可证伪，但缺乏独立来源印证。','{"independence": "仅 1 个 web 来源，无跨源印证", "quality_density": "技术机制描述具体（post-training、自生成探索、RL），可证伪"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:16:00');
INSERT INTO "credibility_assessment" VALUES('cred-51b66ef36dfb','l1_viewpoint','vp-19b7b4efe6ea','medium','单一调查来源，但与评测方法学趋势逻辑相容，信息密度尚可','{"independence": "单源，未跨独立来源印证", "quality_density": "调查性证据，结论可证伪", "logic_fit": "与按维度评分趋势一致"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:17:37');
INSERT INTO "credibility_assessment" VALUES('cred-189339a4713d','l1_viewpoint','vp-a1c5deb4f83b','high','事实性陈述，有公开技术报告支撑且在主题内多处一致复述','{"independence": "主题内多条同义陈述呼应", "quality_density": "高密度、具体可验证（GRPO/R1-Zero）", "internal_consistency": "自洽"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:17:37');
INSERT INTO "credibility_assessment" VALUES('cred-0be8c74b5ab2','l1_viewpoint','vp-6e7201d38827','medium','单源机制性主张，论证细致但尚缺独立印证','{"independence": "单源", "quality_density": "机制性、可证伪、细节充分", "logic_fit": "与''后训练放大预训练行为''的观点相容"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:17:37');
INSERT INTO "credibility_assessment" VALUES('cred-11cf34a10629','l1_viewpoint','vp-60d011ecd76f','medium','单源归因性主张，与跨模型的后训练趋势相互呼应','{"independence": "单源，但与 DeepSeek 路线趋势相容", "quality_density": "具体描述训练机制", "logic_fit": "与后训练成为差异化轴的判断一致"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:17:37');
INSERT INTO "credibility_assessment" VALUES('cred-776af7d6d66a','l1_viewpoint','vp-46ecb4e02695','medium','混合主题，其中后训练张力点有 3 源印证、能力对比有 2 源，但部分单源且跨平台度低','{"independence": "核心张力（后训练 vs 预训练）3 源、GLM 编码 2 源，余多为单源", "quality_density": "普遍具体可证伪，含基准数字与架构细节", "logic_fit": "两条主线内部相容，并各自显式承载已记录的矛盾修正"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:17:37');
INSERT INTO "credibility_assessment" VALUES('cred-2c0a127e1c11','l0_worldview','wv-7049f7a47348656d','medium','核心张力点有 3 源印证、多条事实性认识稳固，但评估侧与泛化侧多为单源、跨平台度普遍偏低','{"independence": "后训练张力 3 源、GLM 编码与 DeepSeek 分层各 2 源，其余单源", "quality_density": "整体高密度、含可验证的架构与基准细节", "recency": "快变主题（前沿模型/后训练），结论随新模型迭代需复核"}',NULL,0,NULL,'active',NULL,'2026-06-29 14:17:37');
CREATE TABLE facet (
    id               TEXT PRIMARY KEY,              -- f_<slug>
    question         TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'open' CHECK (status IN
                       ('open','survey','deepening','saturating','closed')),
    last_searched_at TEXT,
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "facet" VALUES('f_用户需求是异质的_可分解的吗_主流评测框架是否已按能力维度_指令','用户需求是异质的、可分解的吗？主流评测框架是否已按能力维度（指令遵从/泛化/世界知识/长程任务/角色扮演/数理推理/推理深度）拆解，而非一个总分？','open',NULL,'2026-06-29 13:56:53');
INSERT INTO "facet" VALUES('f_glm_rl','GLM 的代码与长程任务优势是否被公开评测+社媒共识验证为''后训练（RL/长程任务+代码）驱动''，而非预训练架构？','open',NULL,'2026-06-29 13:56:53');
INSERT INTO "facet" VALUES('f_deepseek_glm','DeepSeek 的角色扮演与数理推理等泛化能力是否被验证为''架构创新+预训练''驱动，而其代码能力因未做专项后训练而弱于 GLM？','open',NULL,'2026-06-29 13:56:53');
INSERT INTO "facet" VALUES('f_post_training','后训练（post-training）是否正成为当前大模型差异化竞争的核心战场？预训练边际收益是否在下降？','open',NULL,'2026-06-29 13:56:54');
INSERT INTO "facet" VALUES('f_trade_off','是否存在''能力权衡''证据：一个模型难以同时登顶指令遵从性与指令泛化性/角色扮演？评测榜单是否反映这种 trade-off？','open',NULL,'2026-06-29 13:56:54');
INSERT INTO "facet" VALUES('f_b_vs','中文社区（知乎/小红书/B站/微博）对国产模型评测的实证共识与质疑：榜单分数 vs 真实体感差异','open',NULL,'2026-06-29 13:56:54');
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
INSERT INTO "knowledge_change_log" VALUES(1,'l3_claim','sc-11a55df94bdc','*','insert',NULL,NULL,'kind=analysis facet=f_training_method','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(2,'l3_claim','sc-2b2192f12ab2','*','insert',NULL,NULL,'kind=analysis facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(3,'l3_claim','sc-2ccd341d5a49','*','insert',NULL,NULL,'kind=analysis facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(4,'l3_claim','sc-31aa86ba36c6','*','insert',NULL,NULL,'kind=analysis facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(5,'l3_claim','sc-3ca3e849fc84','*','insert',NULL,NULL,'kind=analysis facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(6,'l3_claim','sc-4187ecc7670a','*','insert',NULL,NULL,'kind=fact facet=f_post_training','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(7,'l3_claim','sc-58dc963c403e','*','insert',NULL,NULL,'kind=fact facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(8,'l3_claim','sc-6ca9092e82c4','*','insert',NULL,NULL,'kind=analysis facet=f_benchmark_gap','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(9,'l3_claim','sc-72d323b6684d','*','insert',NULL,NULL,'kind=analysis facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(10,'l3_claim','sc-7964a56c9335','*','insert',NULL,NULL,'kind=analysis facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(11,'l3_claim','sc-7dede751e3ed','*','insert',NULL,NULL,'kind=data facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(12,'l3_claim','sc-99f479cd396a','*','insert',NULL,NULL,'kind=fact facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(13,'l3_claim','sc-9b2c7003b24e','*','insert',NULL,NULL,'kind=fact facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(14,'l3_claim','sc-af535cfe5856','*','insert',NULL,NULL,'kind=opinion facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(15,'l3_claim','sc-af60abb265ae','*','insert',NULL,NULL,'kind=analysis facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(16,'l3_claim','sc-b38eebc5068b','*','insert',NULL,NULL,'kind=analysis facet=f_generalization','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(17,'l3_claim','sc-b74804fcf5c7','*','insert',NULL,NULL,'kind=data facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(18,'l3_claim','sc-c0905de7e5b9','*','insert',NULL,NULL,'kind=fact facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(19,'l3_claim','sc-d8de7d0e5f8b','*','insert',NULL,NULL,'kind=analysis facet=None','condense-distill','2026-06-29 14:12:48',NULL);
INSERT INTO "knowledge_change_log" VALUES(20,'l2_finding','sf-167c98c7a77d','*','insert',NULL,NULL,'type=claim corrob=1/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(21,'l2_finding','sf-874f2aec7370','*','insert',NULL,NULL,'type=fact corrob=1/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(22,'l2_finding','sf-a6d4df16e1e2','*','insert',NULL,NULL,'type=claim corrob=1/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(23,'l2_finding','sf-a2e5d84a57a5','*','insert',NULL,NULL,'type=claim corrob=1/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(24,'l2_finding','sf-33b689a9479f','*','insert',NULL,NULL,'type=claim corrob=1/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(25,'l2_finding','sf-6d6c2e25a19b','*','insert',NULL,NULL,'type=fact corrob=2/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(26,'l2_finding','sf-242bb45a889d','*','insert',NULL,NULL,'type=fact corrob=2/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(27,'l2_finding','sf-312d6735f06d','*','insert',NULL,NULL,'type=fact corrob=1/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(28,'l2_finding','sf-812655669c1e','*','insert',NULL,NULL,'type=trend corrob=1/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(29,'l2_finding','sf-2c1dc5d8383d','*','insert',NULL,NULL,'type=claim corrob=3/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(30,'l2_finding','sf-6d8fcfa55696','*','insert',NULL,NULL,'type=figure corrob=2/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(31,'l2_finding','sf-e5f1ef7d1018','*','insert',NULL,NULL,'type=claim corrob=1/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(32,'l2_finding','sf-7f67b051fc29','*','insert',NULL,NULL,'type=claim corrob=1/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(33,'l2_finding','sf-d33060f03b1c','*','insert',NULL,NULL,'type=claim corrob=1/1','condense-aggregate','2026-06-29 14:16:00',NULL);
INSERT INTO "knowledge_change_log" VALUES(34,'l1_viewpoint','vp-19b7b4efe6ea','*','insert',NULL,NULL,'kind=sub_question stance=emerging','condense-synthesize','2026-06-29 14:17:37',NULL);
INSERT INTO "knowledge_change_log" VALUES(35,'l1_viewpoint','vp-a1c5deb4f83b','*','insert',NULL,NULL,'kind=theme stance=established','condense-synthesize','2026-06-29 14:17:37',NULL);
INSERT INTO "knowledge_change_log" VALUES(36,'l1_viewpoint','vp-6e7201d38827','*','insert',NULL,NULL,'kind=viewpoint stance=emerging','condense-synthesize','2026-06-29 14:17:37',NULL);
INSERT INTO "knowledge_change_log" VALUES(37,'l1_viewpoint','vp-60d011ecd76f','*','insert',NULL,NULL,'kind=theme stance=emerging','condense-synthesize','2026-06-29 14:17:37',NULL);
INSERT INTO "knowledge_change_log" VALUES(38,'l1_viewpoint','vp-46ecb4e02695','*','insert',NULL,NULL,'kind=contrarian stance=contested','condense-synthesize','2026-06-29 14:17:37',NULL);
INSERT INTO "knowledge_change_log" VALUES(39,'l0_worldview','wv-7049f7a47348656d','*','insert',NULL,NULL,'kind=tension','condense-synthesize','2026-06-29 14:17:37','new version');
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
INSERT INTO "l0_worldview" VALUES('wv-7049f7a47348656d','tension','本主题当前的理解状态围绕两条彼此关联的张力展开：(1) 能力来源——后训练（RL/RLHF/RLAIF，GRPO 为开源主流）已取代指令微调成为前沿模型最关键的差异化战场，DeepSeek-R1 更证明纯 RL 可激励推理涌现；但占主导的修正认识是，后训练放大的是预训练已播种的行为、高质量预训练是必要前提，''后训练可独立决定能力''已被推翻。(2) 能力评估——榜单单一总分既因数据污染、cherry-pick 与选择性报告而系统性失真，又因压缩了多维能力画像而与真实应用表现脱节，评测正转向按能力维度拆分；具体到 coding，GLM-4.6 已超过 Sonnet 4 并被视为最强开源权重 coding 模型，但''代码能力强 ≠ 最长程 agentic 任务登顶''，长程任务上 Anthropic 仍占优。综合判断：能力由''强预训练地基 + agentic RL 后训练放大''共同决定，而对能力的衡量必须抗污染、按维度、区分短程与长程。',NULL,'["sf-2c1dc5d8383d", "sf-874f2aec7370", "sf-6d6c2e25a19b", "sf-33b689a9479f", "sf-167c98c7a77d", "sf-6d8fcfa55696", "sf-e5f1ef7d1018", "sf-a6d4df16e1e2"]','["预训练地基与后训练放大对最终能力的贡献边界如何量化划分？", "纯 RL 涌现推理（R1-Zero 路线）在多大程度上依赖预训练已播种的能力，其上限在哪？", "按能力维度、抗数据污染的评测如何标准化以替代单一总分榜单？", "指令遵从与指令泛化的冲突如何在后训练中被调和，避免退回预训练人设？", "开源权重模型在最长程 agentic 任务上落后 Anthropic 的根因是规模、数据还是执行模式？"]','medium',NULL,'["vp-19b7b4efe6ea", "vp-a1c5deb4f83b", "vp-6e7201d38827", "vp-60d011ecd76f", "vp-46ecb4e02695"]','["src-6ca9092e82c4", "src-4187ecc7670a", "src-b38eebc5068b", "src-11a55df94bdc", "src-31aa86ba36c6", "src-2ccd341d5a49", "src-af60abb265ae", "src-99f479cd396a", "src-c0905de7e5b9", "src-58dc963c403e", "src-72d323b6684d", "src-7964a56c9335", "src-d8de7d0e5f8b", "src-3ca3e849fc84", "src-7dede751e3ed", "src-b74804fcf5c7", "src-af535cfe5856", "src-9b2c7003b24e"]','cred-2c0a127e1c11','active',NULL,NULL,NULL,'2026-06-29 14:17:37','2026-06-29 14:17:37','condense-synthesize','new version');
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
INSERT INTO "l1_viewpoint" VALUES('vp-19b7b4efe6ea','f_benchmark_gap',NULL,NULL,'sub_question','用户与开发者侧的调查证据指向一个系统性结论：LLM 评测榜单的单一总分与模型在真实应用中的表现之间存在结构性落差。这支持''单分不足以刻画能力、应当沿能力维度分别评估''的判断——榜单名次是被压缩的标量，掩盖了能力画像的多维分布。该视角与评测方法学层面的趋势（按维度拆分评分）相互印证，但当前仅有单一调查来源直接支撑''差距''本身。','emerging','["sf-167c98c7a77d"]','["榜单分数与真实应用表现的差距能否被量化、在哪些能力维度上最大？"]','medium','["src-6ca9092e82c4"]','cred-51b66ef36dfb',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:17:37','2026-06-29 14:17:37','condense-synthesize',NULL);
INSERT INTO "l1_viewpoint" VALUES('vp-a1c5deb4f83b','f_post_training',NULL,NULL,'theme','DeepSeek-R1 是后训练范式的里程碑：它证明大模型的推理能力可由纯强化学习（GRPO）激励涌现，而非必须经由人类标注的监督微调（SFT）。其中 R1-Zero 作为首个零 SFT、纯 RL 涌现推理的模型，确立了''RL 可直接激励推理''这一新的后训练路线。这一发现在主题内被多处复述（含 _unfileted 桶中的同义陈述），属于已较稳固的事实性认识。','established','["sf-874f2aec7370"]','["纯 RL 涌现推理在多大程度上依赖底层预训练已播种的能力？"]','high','["src-4187ecc7670a"]','cred-189339a4713d',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:17:37','2026-06-29 14:17:37','condense-synthesize',NULL);
INSERT INTO "l1_viewpoint" VALUES('vp-6e7201d38827','f_generalization',NULL,NULL,'viewpoint','一个反直觉但重要的视角：奖励模型默认并不会把''指令遵从''或''诚实''泛化到训练分布之外，而是倾向于回退到''像互联网文本''的预训练人设。由此，''指令遵从''与''指令泛化''应被视为两个不同且可能彼此冲突的维度——在分布内学会服从，不等于在分布外仍保持服从或诚实。这为后训练对齐的脆弱性提供了机制性解释，是当前仍在成形的判断。','emerging','["sf-a6d4df16e1e2"]','["如何在 RL 后训练中让指令遵从真正泛化到分布外而不退回预训练人设？"]','medium','["src-b38eebc5068b"]','cred-0be8c74b5ab2',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:17:37','2026-06-29 14:17:37','condense-synthesize',NULL);
INSERT INTO "l1_viewpoint" VALUES('vp-60d011ecd76f','f_training_method',NULL,NULL,'theme','GLM-4.5 的 agentic/编码能力被归因于后训练：通过自生成探索经验迭代增强策略，强化学习被视为其 agentic 能力的关键来源。这与 DeepSeek 系将推理特化交由 RL 后训练的路线一致，共同构成''agentic 能力主要在后训练阶段被塑造''的方法学共识雏形。','emerging','["sf-d33060f03b1c"]','["自生成探索经验的 RL 后训练相比标准 RLHF 在 agentic 能力上的增量有多大？"]','medium','["src-11a55df94bdc"]','cred-11cf34a10629',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:17:37','2026-06-29 14:17:37','condense-synthesize',NULL);
INSERT INTO "l1_viewpoint" VALUES('vp-46ecb4e02695','_unfileted',NULL,NULL,'contrarian','这一桶汇聚了两条相互交织的主线，并各自带有张力。其一是评测方法学：现代评测有多选题、验证器、榜单/竞技场、LLM-as-judge 四种范式，趋势是按能力维度拆分评分而非给单一总分；与此同时榜单分数被系统性质疑——测试题泄入训练集使模型背答案、叠加 cherry-pick 与选择性报告，导致排行榜失真。其二是能力来源之争：后训练（多轮 RLHF/RLAIF、RL，GRPO 已成开源主流算法）被视为前沿模型最关键的差异化战场，DeepSeek 按职责分层（V3 通用基座、R1 RL 推理特化、V3.1/V3.2 混合 thinking 统一）正体现这一点。但这里存在明确的反向修正：RL 后训练放大的是预训练已播种的行为而非凭空创造能力，高质量预训练是必要前提，''后训练可独立决定能力''被推翻——这是本主题最强印证（3 源）的张力点。能力评估层面同样有张力：GLM-4.6 在 74 个真实编程任务上超过 Claude Sonnet 4、被社区视为最强开源权重 coding 模型，但''代码能力强''不等于''最长程 agentic 任务登顶''，在最长程任务上 Anthropic 仍占优，GLM-5.2 才以更大规模的 agentic RL 后训练去追赶。综合：后训练是差异化主战场，但它是放大器而非凭空创造器；榜单分数需被按维度、抗污染地重读。','contested','["sf-33b689a9479f", "sf-6d6c2e25a19b", "sf-242bb45a889d", "sf-312d6735f06d", "sf-812655669c1e", "sf-2c1dc5d8383d", "sf-6d8fcfa55696", "sf-e5f1ef7d1018", "sf-7f67b051fc29"]','["预训练与后训练对最终能力的贡献边界如何划分与量化？", "开源权重模型与 Anthropic 在最长程 agentic 任务上的差距根因是什么？", "按能力维度的评测如何标准化并抵抗数据污染？"]','medium','["src-31aa86ba36c6", "src-2ccd341d5a49", "src-af60abb265ae", "src-99f479cd396a", "src-c0905de7e5b9", "src-58dc963c403e", "src-72d323b6684d", "src-7964a56c9335", "src-d8de7d0e5f8b", "src-3ca3e849fc84", "src-7dede751e3ed", "src-b74804fcf5c7", "src-af535cfe5856", "src-9b2c7003b24e"]','cred-776af7d6d66a',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:17:37','2026-06-29 14:17:37','condense-synthesize',NULL);
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
INSERT INTO "l2_finding" VALUES('sf-167c98c7a77d','f_benchmark_gap','claim','用户/开发者调查显示 LLM 评测榜单分数与真实应用表现之间存在系统性差距，支持''单一总分不足以反映能力、需按能力维度分别评估''的判断',NULL,NULL,NULL,NULL,NULL,1,1,'["web"]',NULL,'["src-6ca9092e82c4"]','cred-d9fa15a02413','["sc-6ca9092e82c4"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-874f2aec7370','f_post_training','fact','DeepSeek-R1 证明大模型的推理能力可通过纯强化学习(GRPO)激励涌现，而无需依赖人类标注的监督微调(SFT)；R1-Zero 是首个以纯 RL、零 SFT 训练出涌现推理的模型，是大规模后训练的里程碑。',NULL,NULL,NULL,NULL,NULL,1,1,'["web"]',NULL,'["src-4187ecc7670a"]','cred-87fe04064c2a','["sc-4187ecc7670a"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-a6d4df16e1e2','f_generalization','claim','奖励模型默认不会把指令遵从或诚实泛化到训练分布之外，而是倾向于回退到''像互联网文本''的人设；因此指令遵从与指令泛化是两个不同且可能冲突的维度。',NULL,NULL,NULL,NULL,NULL,1,1,'["web"]',NULL,'["src-b38eebc5068b"]','cred-58d5428334d1','["sc-b38eebc5068b"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-a2e5d84a57a5','_unfileted','claim','LLM 评测主要有四种范式——多选题、验证器、榜单/竞技场、LLM-as-judge——且现代评测趋势是按能力维度拆解评分而非给单一总分。',NULL,NULL,NULL,NULL,NULL,1,1,'["web"]',NULL,'["src-2b2192f12ab2"]','cred-8f818375fe27','["sc-2b2192f12ab2"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-33b689a9479f','_unfileted','claim','榜单/排行榜分数无法等同于模型真实能力：测试题泄入训练集导致模型背答案而非推理，叠加 cherry-pick 与选择性报告，使排行榜系统性失真。',NULL,NULL,NULL,NULL,NULL,1,1,'["web"]',NULL,'["src-31aa86ba36c6"]','cred-a1756699f132','["sc-31aa86ba36c6"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-6d6c2e25a19b','_unfileted','fact','DeepSeek 模型按职责分层：V3 是通用基座（架构+预训练），R1 是 RL 后训练特化的推理模型，V3.1/V3.2 用混合 thinking 模式统一二者；其泛化推理能力来自后训练而非仅靠架构与预训练。',NULL,NULL,NULL,NULL,NULL,2,1,'["web"]',NULL,'["src-2ccd341d5a49", "src-af60abb265ae"]','cred-97e823914719','["sc-2ccd341d5a49", "sc-af60abb265ae"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-242bb45a889d','_unfileted','fact','DeepSeek-V3 的基础能力来自架构创新（671B MoE / 37B 激活、MLA、无辅助损失负载均衡、FP8 混合精度）与 14.8T token 大规模预训练，后训练阶段的 SFT 进一步提升指令遵从与角色扮演能力。',NULL,NULL,NULL,NULL,NULL,2,1,'["web"]',NULL,'["src-99f479cd396a", "src-c0905de7e5b9"]','cred-7012b5470dee','["sc-99f479cd396a", "sc-c0905de7e5b9"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-312d6735f06d','_unfileted','fact','DeepSeek-R1 证明 LLM 的推理能力可通过纯强化学习（GRPO）激励而无需人类标注的 SFT，其中 R1-Zero 是首个不依赖 SFT、纯 RL 涌现推理的模型。',NULL,NULL,NULL,NULL,NULL,1,1,'["web"]',NULL,'["src-58dc963c403e"]','cred-9d034e5be380','["sc-58dc963c403e"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-812655669c1e','_unfileted','trend','推理模型的 RL 训练正从 SFT→RLHF 标准管线演进，DeepSeek-R1 提出的 GRPO 已成为开源社区主流的 RL 算法。',NULL,NULL,NULL,NULL,NULL,1,1,'["web"]',NULL,'["src-72d323b6684d"]','cred-9858826b4963','["sc-72d323b6684d"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-2c1dc5d8383d','_unfileted','claim','后训练（多轮 RLHF/RLAIF、RL）已取代指令微调成为前沿模型间最关键的差异化竞争轴，可扩展性远超指令微调，即''后训练成为核心战场''；但同时有观点修正：RL 后训练放大的是预训练已播种的行为而非凭空创造能力，高质量预训练是必要前提，''后训练可独立决定能力''的看法被推翻。',NULL,NULL,NULL,NULL,NULL,3,1,'["web"]','存在张力：sc-7964a56c9335 与 sc-d8de7d0e5f8b 强调后训练已超越预训练规模、成为最关键差异化轴；sc-3ca3e849fc84 则修正这一叙事，强调后训练只是放大预训练所播种的能力、预训练是必要前提。二者非直接矛盾（后训练可既是差异化轴又依赖预训练），但对''谁决定能力''的归因相左，需在 L1 以 contrarian 综合。','["src-7964a56c9335", "src-d8de7d0e5f8b", "src-3ca3e849fc84"]','cred-460840601a9e','["sc-7964a56c9335", "sc-d8de7d0e5f8b", "sc-3ca3e849fc84"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-6d8fcfa55696','_unfileted','figure','在 Claude Code 环境下用 74 个真实编程任务实测，GLM-4.6 的代码能力超过 Claude Sonnet 4 并领先其他国产模型，较 GLM-4.5 提升约 27%。',NULL,NULL,NULL,NULL,NULL,2,1,'["web"]',NULL,'["src-7dede751e3ed", "src-b74804fcf5c7"]','cred-42a028833a22','["sc-7dede751e3ed", "sc-b74804fcf5c7"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-e5f1ef7d1018','_unfileted','claim','社区共识认为 GLM-4.6 是当前最强的开源权重 coding 模型，但''代码能力强''不等于''最长程任务登顶''——在最长程 agentic 任务上 Anthropic 仍占优。',NULL,NULL,NULL,NULL,NULL,1,1,'["web"]',NULL,'["src-af535cfe5856"]','cred-994a7fe63acb','["sc-af535cfe5856"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-7f67b051fc29','_unfileted','claim','GLM-5.2 的长程任务能力源于规模更大、领域更广、执行模式更复杂的 agentic RL 后训练。',NULL,NULL,NULL,NULL,NULL,1,1,'["web"]',NULL,'["src-9b2c7003b24e"]','cred-7bd2bf9a0cd7','["sc-9b2c7003b24e"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
INSERT INTO "l2_finding" VALUES('sf-d33060f03b1c','f_training_method','claim','GLM-4.5 的 agentic/编码能力主要来自后训练（post-training）：通过自生成探索经验迭代增强策略，强化学习（RL）是其 agentic 能力的关键。',NULL,NULL,NULL,NULL,NULL,1,1,'["web"]',NULL,'["src-11a55df94bdc"]','cred-533389d2801d','["sc-11a55df94bdc"]',NULL,'active',NULL,NULL,NULL,'2026-06-29 14:16:00','2026-06-29 14:16:00','condense-aggregate',NULL);
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
INSERT INTO "l3_claim" VALUES('sc-11a55df94bdc','f_training_method','GLM-4.5 的 agentic/编码能力主要来自后训练（post-training）：通过自生成探索经验迭代增强策略，RL 是 agentic 能力的关键。','analysis','article','src-11a55df94bdc','["src-11a55df94bdc"]','post-training 对 LLM 至关重要，通过自生成探索经验迭代增强策略。RL 是 agentic 能力关键。','6287419fa6e1d92642825c7c05b0ced90732c8b5b95f0dd3dbeb9f4feebddd2f','官方厂商博客对自家模型能力来源的说明，支持「GLM 代码能力来自后训练」方向；属厂商自述，存在自利偏向。','{"independence": "单一来源，且为厂商官方自述，非独立第三方", "quality_density": "有具体技术主张（自生成经验、RL 提升 agentic），密度中等但偏纲领性", "recency": "GLM-4.5 时期信息，对快速演进的模型能力归因仍基本有效"}',NULL,'cred-bd7d9523e853',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-2b2192f12ab2',NULL,'LLM 评测主要有四种范式——多选题、验证器、榜单/竞技场、LLM-as-judge——且现代评测趋势是按能力维度拆解评分而非给单一总分。','analysis','article','src-2b2192f12ab2','["src-2b2192f12ab2"]','现代评测已倾向按能力维度拆解而非单总分。','e5c6214da596f902a48aaf2bd6bd13d43bda8b3f178c7ccadb7972188d835eec','来自 Sebastian Raschka 的科普性综述，属于对评测方法论的框架性归纳，可作为 capability-based evaluation 的分类骨架。','{"independence": "单一署名作者的综述，但归纳的是行业公认范式，非孤立主张。", "quality_density": "信息密度高、分类清晰、可对照公开评测实践验证。", "recency": "评测方法论框架属慢变知识，时效性强、近期仍有效。"}',NULL,'cred-209e460189bb',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-2ccd341d5a49',NULL,'DeepSeek 各模型按职责分层：V3 是通用基座（架构+预训练），R1 是 RL 推理特化（后训练），V3.1/V3.2 用混合 thinking 统一两者；泛化推理能力来自后训练而非仅靠架构与预训练。','analysis','article','src-2ccd341d5a49','["src-2ccd341d5a49"]','V3=通用基座(架构+预训练), R1=RL推理特化(后训练), V3.1/V3.2=混合thinking统一两者','0d85aee7dd785ea5476fed76af3df69f99db82e70e91c972665a008857eae5f4','厘清了一个常见误解：把推理能力归因于架构/预训练。该文强调 R1 的泛化推理是后训练(RL)的产物，对理解 DeepSeek 模型谱系与能力来源有结构性价值。','{"independence": "单一 web 来源（BentoML 厂商博客），未交叉印证", "quality_density": "高密度、技术性强、区分清晰、可证伪", "recency": "DeepSeek 模型谱系为快变主题，V3.1/V3.2 信息需注意时效"}',NULL,'cred-3593be4c7410',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-31aa86ba36c6',NULL,'榜单分数无法等同于模型真实能力：测试题泄入训练集导致模型背答案而非推理，叠加 cherry-pick/选择性报告，使排行榜系统性失真。','analysis','article','src-31aa86ba36c6','["src-31aa86ba36c6"]','测试题进入训练集导致模型背答案而非推理……榜单分≠真实能力。','6a5dbce3009eca92e07b224e6dc7893abfc257de98a72fb716f584cc9dfdeb89','这是对 LLM 评测方法论的批评性综述，指向两类失真机制（数据污染 + 选择性报告），属于评测可信度议题，可在 aggregate 阶段归入''评测有效性/污染''类 facet。','{"independence": "单一博客来源，未见独立佐证，但所述为业内广泛讨论的共识性问题", "quality_density": "中等：点明污染与选择性报告两类机制，但缺具体案例/量化数据", "recency": "2026 主题，时效性强且仍然有效"}',NULL,'cred-e5065c9649e5',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-3ca3e849fc84',NULL,'RL 后训练放大的是预训练阶段已播种的行为而非凭空创造能力，预训练与后训练深度耦合，高质量预训练是必要前提、后训练负责解锁价值，因此''后训练可独立决定能力''的看法被修正。','analysis','paper','src-3ca3e849fc84','["src-3ca3e849fc84"]','RL 微调放大的是预训练阶段已播种的行为，而非凭空创造','83c038cf956a5848e51bc1c26c86ccda815fbe806996f33e71265c7b057c79f1','来自 arXiv 论文（标题即论点），修正了将后训练与预训练割裂看待的简化观点；属能力来源归因类分析。','{"independence": "单一论文来源，作为单源 L3 不做跨源印证", "quality_density": "信息密度高、有明确可证伪主张（放大而非创造）", "recency": "2025 年论文，针对当前 RL 后训练范式，时效有效"}',NULL,'cred-82abc78b6d75',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-4187ecc7670a','f_post_training','DeepSeek-R1 证明大模型的推理能力可以通过纯强化学习(GRPO)激励涌现，而无需依赖人类标注的监督微调(SFT)；R1-Zero 是首个以纯 RL、零 SFT 训练出涌现推理的模型，标志大规模后训练的里程碑。','fact','paper','src-4187ecc7670a','["src-4187ecc7670a"]','R1-Zero 是首个纯 RL 无 SFT 训练出涌现推理的模型。','3157e3b75bba8b59143266d0a0c22c6c5437422031b90b3f3b7113ba4e1c5f99','该 payload 明确将此条作为对''未特殊后训练''用户假说的修正：DeepSeek 是大规模后训练里程碑，纯 RL 路线(R1-Zero)是其核心创新点。','{"independence": "第一手论文来源，非转发；具体可信度评估需后续多源印证 GRPO 纯 RL 涌现推理的可复现性", "quality_density": "信息密度高，含具体方法(GRPO)、具体模型(R1-Zero)与可证伪主张", "recency": "2501 arXiv，对应 2025 年初发布，在 LLM 后训练快变领域仍属当前有效"}',NULL,'cred-6b94d36f98a0',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-58dc963c403e',NULL,'DeepSeek-R1 证明大语言模型的推理能力可通过纯强化学习(GRPO)激励而无需人类标注的 SFT，其中 R1-Zero 是首个不依赖 SFT、纯 RL 涌现推理的模型。','fact','paper','src-58dc963c403e','["src-58dc963c403e"]','R1-Zero 是首个纯 RL 无 SFT 涌现推理的模型。','8c0c412d55f99c1415e6adb07dbffd086f129ff24dc4446fb22acc3b7ebbb1f8','这是一项大规模后训练的里程碑工作；纠正了''未经特殊后训练''的误解。R1-Zero(纯 RL，无 SFT)与 R1 是两个相关但不同的产物。','{"independence": "原始一手来源(论文作者团队)，非转发；但单源，印证需 aggregate 阶段补充", "quality_density": "高密度、有具体方法名(GRPO)与可复现主张，非空泛口号", "recency": "2025 年发布，对快速演进的 LLM 训练范式仍属当前有效"}',NULL,'cred-d17e7e6cded5',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-6ca9092e82c4','f_benchmark_gap','用户/开发者调查显示 LLM 评测榜单分数与真实应用表现之间存在系统性差距，印证了''单一总分不足以反映能力、需按能力维度分别评估''的判断','analysis','paper','src-6ca9092e82c4','["src-6ca9092e82c4"]','榜单与现实应用存在系统性 gap，支持''单一总分不够、需按能力维度看''','3079b30e61b10b49f3624c0a5af6ced97f89d304261a4ba7209b3255dbe15591','出自 arXiv 论文《Line Goes Up? Inherent Limitations of Benchmarks for Evaluating LLMs》，属对基准评测局限性的实证/分析性主张，可作为''多维能力评测''视角的支撑证据','{"independence": "学术论文引用用户/开发者调查作为独立证据，非单一信息源转发", "quality_density": "主张具体、可证伪，指向''榜单—应用''系统性 gap 这一明确现象", "recency": "2025 年论文（arXiv 2502），LLM 评测主题时效性仍有效"}',NULL,'cred-321130a8005b',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-72d323b6684d',NULL,'推理模型的 RL 训练正从 SFT→RLHF 标准管线演进，DeepSeek-R1 提出的 GRPO 已成为开源社区主流的 RL 算法。','analysis','article','src-72d323b6684d','["src-72d323b6684d"]','GRPO 成为开源社区主流 RL 算法。','f5feb85e793a48c6037d1f4d7d8cfe229ebe4867dc29967f9c3e14199a2b49b7','综述类文章，归纳行业趋势而非单一实验结果；GRPO 作为开源主流算法的论断与近期公开技术进展一致。','{"independence": "单一作者综述，但综合了 DeepSeek-R1 等多方公开工作，非单点转发", "quality_density": "信息密度高，明确指出 SFT→RLHF 管线与 GRPO 算法等可核查细节", "recency": "推理模型 RL 为快变领域，但 GRPO 主流化为近期且仍有效的判断"}',NULL,'cred-95e4c6973c63',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-7964a56c9335',NULL,'RL 后训练已超越预训练规模，成为前沿 AI lab 模型间最关键的差异化竞争轴，即''后训练成为核心战场''。','analysis','article','src-7964a56c9335','["src-7964a56c9335"]','RL 后训练已成为每个前沿 AI lab 的首要扩展轴，超越原始预训练规模。','46ca01cdb7281761e17257c28f63291bddb27d3790f1c8e886b8b5434b8f7883','单源观点性论断，直接对应''后训练成为核心战场''假说；属博客分析而非可证伪数据。','{"independence": "单一博客来源，无交叉印证", "quality_density": "论点清晰但偏口号式，缺少量化或具体证据", "recency": "2026 主题，时效性强且当前有效"}',NULL,'cred-158b7597f4f7',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-7dede751e3ed',NULL,'在 Claude Code 环境下用 74 个真实编程任务实测，GLM-4.6 的代码能力超过 Claude Sonnet 4，较 GLM-4.5 提升约 27%。','data','article','src-7dede751e3ed','["src-7dede751e3ed"]','GLM-4.6 Claude Code 环境 74 个真实编程任务实测超 Claude Sonnet 4，较 GLM-4.5 提升约 27%。','dff1cbf0aedbb95c21699bd7e4b6a1be5c64cdd8a6a1be218221ebd56ca863af','强调测试以真实编程任务为主而非纯榜单，意在凸显实战代表性；但来源为媒体报道转述官方/厂商口径，缺乏独立第三方复现。','{"independence": "单一媒体报道转述厂商评测，未见独立第三方复现", "quality_density": "有具体任务数与量化提升幅度，可证伪性较强", "recency": "2025-09 发布，对快速迭代的模型能力对比时效性有限"}',NULL,'cred-e88b9a9a3c36',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-99f479cd396a',NULL,'DeepSeek-V3 通过架构创新（671B MoE 仅激活 37B、MLA、无辅助损失的负载均衡）配合 14.8T tokens 的 FP8 大规模预训练奠定基础能力，并以含 SFT 的后训练提升指令遵从与角色扮演。','fact','paper','src-99f479cd396a','["src-99f479cd396a"]','V3: 671B MoE(37B激活), MLA+无辅助损失负载均衡, 14.8T tokens, FP8。架构创新+预训练是基础能力来源。','a366e05bc0ce5ceb5f22f3d0510304fe1ad15a0d78add01e2fd849dff0ffbcf2','技术报告自述其架构与训练方法；属一手官方来源，描述方法论而非独立评测结果。','{"independence": "单一官方一手来源（厂商自述），非多源印证", "quality_density": "信息密度高，含具体参数（671B/37B/14.8T/FP8）与方法名，可证伪", "recency": "2024 年底发布，技术细节在当前仍有效"}',NULL,'cred-5264012f44ea',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-9b2c7003b24e',NULL,'GLM-5.2 的长程任务能力源于规模更大、领域更广、执行模式更复杂的 agentic RL 后训练。','fact','article','src-9b2c7003b24e','["src-9b2c7003b24e"]','官方证实长程任务能力来自 agentic RL 后训练。','a2e3e89c7b65b3c02b3fa5d3621a750113cca008548d92b9a0a16bedb598a310','官方博客对自家模型能力归因的技术说明，属厂商一方陈述，缺乏第三方独立验证。','{"independence": "单一官方来源，厂商自述，无第三方独立印证", "quality_density": "有具体技术归因（agentic RL 后训练、规模/领域/执行模式），但偏概括、缺可证伪细节", "recency": "新发布模型说明，时效性强"}',NULL,'cred-3c70745374ce',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-af535cfe5856',NULL,'社区共识认为 GLM 4.6 是当前最强的开源权重 coding 模型，但代码能力强不等于在最长程任务上登顶——Anthropic 在最长程任务上仍占优。','opinion','forum','src-af535cfe5856','["src-af535cfe5856"]','社区共识：最好开源权重 coding 模型。但部分用户指出 Anthropic 在最长程任务仍胜出。','1b87d3ac9000a73e804df0885956d3ffe0da90094e2e1f852fb25c2dc11ebe49','Reddit 社区聚合观点，既给出共识也保留了反例边界（长程任务 Anthropic 仍胜），属于带限定的判断而非单一吹捧。','{"independence": "单一 Reddit 帖子聚合多名用户发言，但相互间非独立来源，且无第三方基准印证", "quality_density": "有明确论点和限定条件（长程任务例外），密度中等，可证伪但缺乏量化", "recency": "GLM 4.6 / 模型能力快变主题，结论时效性短，易随新版本过期"}',NULL,'cred-18d0b7d95ffe',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-af60abb265ae',NULL,'DeepSeek 各模型分工不同：V3 是通用基座（架构+预训练），R1 是用 RL 后训练特化的推理模型，V3.1/V3.2 用混合 thinking 模式统一二者；因此用户『架构+预训练』的假说只适用于 V3，而 R1 的泛化推理能力恰恰来自后训练而非预训练。','analysis','article','src-af60abb265ae','["src-af60abb265ae"]','用户假说的''架构+预训练''适用于V3, 但泛化推理能力(R1)恰恰来自后训练。','08a6b32b9d45688d86f1d14b3c85600ec4bb280a33360ba83e27f6bca8eb0095','该原文实为对某个用户假说的纠正性分析，核心论点是『推理能力来自后训练（RL）而非架构/预训练』，并以 DeepSeek 模型谱系作为例证。属于二手归纳而非一手官方说明。','{"independence": "单一厂商技术博客，未见多源交叉印证", "quality_density": "信息密度高、区分清晰、可证伪（V3/R1/V3.x 分工具体）", "recency": "DeepSeek 模型谱系为近期话题，信息仍有效"}',NULL,'cred-d0cd3fd77e70',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-b38eebc5068b','f_generalization','奖励模型默认不会把指令遵从或诚实泛化到训练分布之外，反而倾向于回退到''像互联网文本''的人设，因此指令遵从与指令泛化是两个不同且可能冲突的维度。','analysis','article','src-b38eebc5068b','["src-b38eebc5068b"]','奖励模型默认不会泛化指令遵从或诚实，倾向''像互联网文本''的人设。','6d1d666839d67dd31cad9303c266fd924c53ca614de145eb5bc65b67a6f8fe8c','来自 LessWrong 的对齐研究帖，属于机制性分析观点而非实证数据；核心张力在于''能遵从指令''不等于''会把诚实/遵从泛化到新情境''。可与评测能力维度（指令遵从 vs 泛化）的拆分对照。','{"independence": "单一来源（一篇 LessWrong 帖），尚无其他独立来源印证，留待 aggregate 阶段计数。", "quality_density": "信息密度高、提出可检验的机制性主张（泛化 vs 遵从分离），非空泛口号。", "recency": "对齐方法论类主张时效衰减较慢，当前仍有效。"}',NULL,'cred-6961406d5997',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-b74804fcf5c7',NULL,'GLM-4.6 在 Claude Code 环境下 74 个真实编程任务实测中超过 Claude Sonnet 4 并领先其他国产模型，较 GLM-4.5 提升约 27%','data','article','src-b74804fcf5c7','["src-b74804fcf5c7"]','GLM-4.6 在 Claude Code 环境下 74 个真实编程任务实测超过 Claude Sonnet 4，超越国产模型。','ca827f4be5d460560a1a9548967d95f8ce3c02987d37797d3e906f4c9b7d749f','单一媒体（量子位）报道的实测结果，强调基于真实任务而非纯榜单；但测试规模有限（74 任务）且为厂商相关评测语境，需多源印证。','{"independence": "单一来源（量子位），无独立复现，独立性弱", "quality_density": "有具体数字（74 任务、27% 提升、对比对象明确），密度中等且可证伪", "recency": "2025-09 报道，模型评测时效性强，短期内有效"}',NULL,'cred-dfb0085c32f9',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-c0905de7e5b9',NULL,'DeepSeek-V3 的基础能力来自架构创新（671B MoE/37B激活、MLA、无辅助损失负载均衡、FP8混合精度）与14.8T token大规模预训练，后训练阶段的SFT进一步提升指令遵从与角色扮演能力。','fact','paper','src-c0905de7e5b9','["src-c0905de7e5b9"]','架构创新+预训练是基础能力来源。V3 后训练含 SFT 提升指令遵从与角色扮演。','69eed2b0001d605a93ae0ece1b118a6def4cb7216d0572727885fafd07664f0d','官方技术报告，描述模型架构与训练管线的能力来源归因；属一手工程事实陈述，但为厂商自述需注意自利倾向。','{"independence": "单一来源（厂商自述），独立性有限，但属一手原始文档而非转发", "quality_density": "信息密度高，含具体架构与训练参数，可证伪", "recency": "2024年底发布的技术报告，对应当前模型版本，时效有效"}',NULL,'cred-05fd47305e1a',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
INSERT INTO "l3_claim" VALUES('sc-d8de7d0e5f8b',NULL,'后训练（多轮 RLHF/RLAIF）已取代指令微调成为前沿模型的主要差异化轴线，可扩展性远超指令微调。','analysis','article','src-d8de7d0e5f8b','["src-d8de7d0e5f8b"]','RLHF can scale far further than instruction tuning. Frontier labs structure post-training as multiple rounds of RL.','084e52e3fa419a2e2f57ae55fb5b40699b609703bebb9e50a1e46756e465d257','来自 Nathan Lambert（Interconnects）对前沿实验室后训练范式的方法论性论断；属行业观察而非单点实验数据。','{"independence": "单一来源、单一作者观点，未见独立印证", "quality_density": "密度中等，提出明确机制性主张（多轮 RL、可扩展性）但无量化证据", "recency": "后训练范式为当前活跃议题，信息时效良好"}',NULL,'cred-997237e8dbcf',NULL,NULL,'active',NULL,NULL,NULL,'2026-06-29 14:12:48','2026-06-29 14:12:48','condense-distill',NULL);
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
INSERT INTO "open_question" VALUES('oq-0a10f503c9ba','预训练地基与后训练放大对最终能力的贡献边界如何量化划分？',NULL,'open','wv-7049f7a47348656d',NULL,'2026-06-29 14:17:37');
INSERT INTO "open_question" VALUES('oq-716c54fbab25','纯 RL 涌现推理（R1-Zero 路线）在多大程度上依赖预训练已播种的能力，其上限在哪？',NULL,'open','wv-7049f7a47348656d',NULL,'2026-06-29 14:17:37');
INSERT INTO "open_question" VALUES('oq-349682163f6d','按能力维度、抗数据污染的评测如何标准化以替代单一总分榜单？',NULL,'open','wv-7049f7a47348656d',NULL,'2026-06-29 14:17:37');
INSERT INTO "open_question" VALUES('oq-f8d29808b216','指令遵从与指令泛化的冲突如何在后训练中被调和，避免退回预训练人设？',NULL,'open','wv-7049f7a47348656d',NULL,'2026-06-29 14:17:37');
INSERT INTO "open_question" VALUES('oq-ad768329dd86','开源权重模型在最长程 agentic 任务上落后 Anthropic 的根因是规模、数据还是执行模式？',NULL,'open','wv-7049f7a47348656d',NULL,'2026-06-29 14:17:37');
CREATE TABLE search_log (
    id           TEXT PRIMARY KEY,                 -- sl-<hash>
    query        TEXT NOT NULL,
    source       TEXT,                             -- web / x / douyin / xiaohongshu / ...
    facet        TEXT,                             -- facet this search targeted (nullable)
    run_id       TEXT,
    result_note  TEXT,                             -- optional: counts / outcome the agent recorded
    searched_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "search_log" VALUES('sl-d8d7d620a2ca','大模型评测 能力维度 后训练','web',NULL,NULL,NULL,'2026-06-29 13:57:12');
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
INSERT INTO "source_ref" VALUES('src-d8de7d0e5f8b','pending',NULL,'web','article','https://www.interconnects.ai/p/frontier-model-post-training','Nathan Lambert','A Recipe for Frontier Model Post-Training (Interconnects)','084e52e3fa419a2e2f57ae55fb5b40699b609703bebb9e50a1e46756e465d257','topics/llm_eval_capabilities/cache/084e52e3fa419a2e2f57ae55fb5b40699b609703bebb9e50a1e46756e465d257.md',NULL,'ri-182fc4bc2dfd','2026-06-29 14:05:46','agent',NULL,'2026-06-29 14:05:46');
INSERT INTO "source_ref" VALUES('src-7964a56c9335','pending',NULL,'web','article','https://www.digitalapplied.com/blog/post-training-revolution-rl-new-moat-2026','Digital Applied','The Post-Training Revolution: RL Is the New Moat in 2026','46ca01cdb7281761e17257c28f63291bddb27d3790f1c8e886b8b5434b8f7883','topics/llm_eval_capabilities/cache/46ca01cdb7281761e17257c28f63291bddb27d3790f1c8e886b8b5434b8f7883.md',NULL,'ri-4215e7a0f775','2026-06-29 14:05:46','agent',NULL,'2026-06-29 14:05:46');
INSERT INTO "source_ref" VALUES('src-3ca3e849fc84','pending',NULL,'web','paper','https://arxiv.org/html/2504.07912v2',NULL,'RL Post-training Amplifies Behaviors Learned in Pretraining','83c038cf956a5848e51bc1c26c86ccda815fbe806996f33e71265c7b057c79f1','topics/llm_eval_capabilities/cache/83c038cf956a5848e51bc1c26c86ccda815fbe806996f33e71265c7b057c79f1.md',NULL,'ri-337a1b673f49','2026-06-29 14:05:46','agent',NULL,'2026-06-29 14:05:46');
INSERT INTO "source_ref" VALUES('src-72d323b6684d','pending',NULL,'web','article','https://magazine.sebastianraschka.com/p/the-state-of-llm-reasoning-model-training',NULL,'The State of RL for LLM Reasoning (Raschka)','f5feb85e793a48c6037d1f4d7d8cfe229ebe4867dc29967f9c3e14199a2b49b7','topics/llm_eval_capabilities/cache/f5feb85e793a48c6037d1f4d7d8cfe229ebe4867dc29967f9c3e14199a2b49b7.md',NULL,'ri-18af99985a5d','2026-06-29 14:05:46','agent',NULL,'2026-06-29 14:05:46');
INSERT INTO "source_ref" VALUES('src-b74804fcf5c7','pending',NULL,'web','article','https://www.qbitai.com/2025/09/338660.html',NULL,'真够卷的！GLM-4.6 代码国内最强 (量子位)','ca827f4be5d460560a1a9548967d95f8ce3c02987d37797d3e906f4c9b7d749f','topics/llm_eval_capabilities/cache/ca827f4be5d460560a1a9548967d95f8ce3c02987d37797d3e906f4c9b7d749f.md',NULL,'ri-f32cf41f6ef3','2026-06-29 14:05:46','agent',NULL,'2026-06-29 14:05:46');
INSERT INTO "source_ref" VALUES('src-4187ecc7670a','pending',NULL,'web','paper','https://arxiv.org/abs/2501.12948','DeepSeek-AI','DeepSeek-R1: Incentivizing Reasoning via Pure RL','3157e3b75bba8b59143266d0a0c22c6c5437422031b90b3f3b7113ba4e1c5f99','topics/llm_eval_capabilities/cache/3157e3b75bba8b59143266d0a0c22c6c5437422031b90b3f3b7113ba4e1c5f99.md',NULL,'ri-74470603a485','2026-06-29 14:05:46','agent',NULL,'2026-06-29 14:05:46');
INSERT INTO "source_ref" VALUES('src-c0905de7e5b9','pending',NULL,'web','paper','https://arxiv.org/html/2412.19437v1',NULL,'DeepSeek-V3 Technical Report','69eed2b0001d605a93ae0ece1b118a6def4cb7216d0572727885fafd07664f0d','topics/llm_eval_capabilities/cache/69eed2b0001d605a93ae0ece1b118a6def4cb7216d0572727885fafd07664f0d.md',NULL,'ri-c732b72f6aa4','2026-06-29 14:05:46','agent',NULL,'2026-06-29 14:05:46');
INSERT INTO "source_ref" VALUES('src-af60abb265ae','pending',NULL,'web','article','https://www.bentoml.com/blog/the-complete-guide-to-deepseek-models-from-v3-to-r1-and-beyond',NULL,'Complete Guide to DeepSeek Models (BentoML)','08a6b32b9d45688d86f1d14b3c85600ec4bb280a33360ba83e27f6bca8eb0095','topics/llm_eval_capabilities/cache/08a6b32b9d45688d86f1d14b3c85600ec4bb280a33360ba83e27f6bca8eb0095.md',NULL,'ri-dd78567691b2','2026-06-29 14:05:46','agent',NULL,'2026-06-29 14:05:46');
INSERT INTO "source_ref" VALUES('src-9b2c7003b24e','pending',NULL,'web','article','https://z.ai/blog/glm-5.2',NULL,'GLM-5.2: Built for Long-Horizon Tasks (Z.ai官方)','a2e3e89c7b65b3c02b3fa5d3621a750113cca008548d92b9a0a16bedb598a310','topics/llm_eval_capabilities/cache/a2e3e89c7b65b3c02b3fa5d3621a750113cca008548d92b9a0a16bedb598a310.md',NULL,'ri-916203e98346','2026-06-29 14:06:18','agent',NULL,'2026-06-29 14:06:18');
INSERT INTO "source_ref" VALUES('src-11a55df94bdc','pending',NULL,'web','article','https://z.ai/blog/glm-4.5',NULL,'GLM-4.5: Reasoning, Coding, Agentic Abilities (Z.ai)','6287419fa6e1d92642825c7c05b0ced90732c8b5b95f0dd3dbeb9f4feebddd2f','topics/llm_eval_capabilities/cache/6287419fa6e1d92642825c7c05b0ced90732c8b5b95f0dd3dbeb9f4feebddd2f.md',NULL,'ri-fbe7691e85f4','2026-06-29 14:06:18','agent',NULL,'2026-06-29 14:06:18');
INSERT INTO "source_ref" VALUES('src-7dede751e3ed','pending',NULL,'web','article','https://www.qbitai.com/2025/09/338660.html',NULL,'GLM-4.6 代码国内最强 (量子位)','dff1cbf0aedbb95c21699bd7e4b6a1be5c64cdd8a6a1be218221ebd56ca863af','topics/llm_eval_capabilities/cache/dff1cbf0aedbb95c21699bd7e4b6a1be5c64cdd8a6a1be218221ebd56ca863af.md',NULL,'ri-9291240d86c7','2026-06-29 14:06:18','agent',NULL,'2026-06-29 14:06:18');
INSERT INTO "source_ref" VALUES('src-af535cfe5856','pending',NULL,'web','forum','https://www.reddit.com/r/LocalLLaMA/comments/1nx18ax/',NULL,'GLM 4.6 best open-weight coding model (Reddit r/LocalLLaMA)','1b87d3ac9000a73e804df0885956d3ffe0da90094e2e1f852fb25c2dc11ebe49','topics/llm_eval_capabilities/cache/1b87d3ac9000a73e804df0885956d3ffe0da90094e2e1f852fb25c2dc11ebe49.md',NULL,'ri-3b1f402d1b12','2026-06-29 14:06:18','agent',NULL,'2026-06-29 14:06:18');
INSERT INTO "source_ref" VALUES('src-58dc963c403e','pending',NULL,'web','paper','https://arxiv.org/abs/2501.12948','DeepSeek-AI','DeepSeek-R1: Incentivizing Reasoning via Pure RL','8c0c412d55f99c1415e6adb07dbffd086f129ff24dc4446fb22acc3b7ebbb1f8','topics/llm_eval_capabilities/cache/8c0c412d55f99c1415e6adb07dbffd086f129ff24dc4446fb22acc3b7ebbb1f8.md',NULL,'ri-6014da004346','2026-06-29 14:06:18','agent',NULL,'2026-06-29 14:06:18');
INSERT INTO "source_ref" VALUES('src-99f479cd396a','pending',NULL,'web','paper','https://arxiv.org/html/2412.19437v1',NULL,'DeepSeek-V3 Technical Report','a366e05bc0ce5ceb5f22f3d0510304fe1ad15a0d78add01e2fd849dff0ffbcf2','topics/llm_eval_capabilities/cache/a366e05bc0ce5ceb5f22f3d0510304fe1ad15a0d78add01e2fd849dff0ffbcf2.md',NULL,'ri-cf56167b3a3c','2026-06-29 14:06:18','agent',NULL,'2026-06-29 14:06:18');
INSERT INTO "source_ref" VALUES('src-2ccd341d5a49','pending',NULL,'web','article','https://www.bentoml.com/blog/the-complete-guide-to-deepseek-models-from-v3-to-r1-and-beyond',NULL,'Complete Guide to DeepSeek Models (BentoML)','0d85aee7dd785ea5476fed76af3df69f99db82e70e91c972665a008857eae5f4','topics/llm_eval_capabilities/cache/0d85aee7dd785ea5476fed76af3df69f99db82e70e91c972665a008857eae5f4.md',NULL,'ri-3497037f756d','2026-06-29 14:06:18','agent',NULL,'2026-06-29 14:06:18');
INSERT INTO "source_ref" VALUES('src-6ca9092e82c4','pending',NULL,'web','paper','https://arxiv.org/html/2502.14318v1',NULL,'Line Goes Up? Inherent Limitations of Benchmarks for Evaluating LLMs','3079b30e61b10b49f3624c0a5af6ced97f89d304261a4ba7209b3255dbe15591','topics/llm_eval_capabilities/cache/3079b30e61b10b49f3624c0a5af6ced97f89d304261a4ba7209b3255dbe15591.md',NULL,'ri-0fa276575291','2026-06-29 14:07:10','agent',NULL,'2026-06-29 14:07:10');
INSERT INTO "source_ref" VALUES('src-2b2192f12ab2','pending',NULL,'web','article','https://magazine.sebastianraschka.com/p/llm-evaluation-4-approaches',NULL,'4 Main Approaches to LLM Evaluation (Raschka)','e5c6214da596f902a48aaf2bd6bd13d43bda8b3f178c7ccadb7972188d835eec','topics/llm_eval_capabilities/cache/e5c6214da596f902a48aaf2bd6bd13d43bda8b3f178c7ccadb7972188d835eec.md',NULL,'ri-7ab38925e026','2026-06-29 14:07:10','agent',NULL,'2026-06-29 14:07:10');
INSERT INTO "source_ref" VALUES('src-b38eebc5068b','pending',NULL,'web','article','https://www.lesswrong.com/posts/Yio4nmD8JMttx9o9S/',NULL,'Truthfulness & Instruction-Following Don''t Generalize by Default','6d1d666839d67dd31cad9303c266fd924c53ca614de145eb5bc65b67a6f8fe8c','topics/llm_eval_capabilities/cache/6d1d666839d67dd31cad9303c266fd924c53ca614de145eb5bc65b67a6f8fe8c.md',NULL,'ri-c15bc6f07cb4','2026-06-29 14:07:10','agent',NULL,'2026-06-29 14:07:10');
INSERT INTO "source_ref" VALUES('src-31aa86ba36c6','pending',NULL,'web','article','https://www.digitalapplied.com/blog/llm-benchmark-methodology-2026-contamination-leaderboard-guide',NULL,'LLM Benchmark Methodology 2026: Contamination & Leaderboards','6a5dbce3009eca92e07b224e6dc7893abfc257de98a72fb716f584cc9dfdeb89','topics/llm_eval_capabilities/cache/6a5dbce3009eca92e07b224e6dc7893abfc257de98a72fb716f584cc9dfdeb89.md',NULL,'ri-734df49b5605','2026-06-29 14:07:10','agent',NULL,'2026-06-29 14:07:10');
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
INSERT INTO "sqlite_sequence" VALUES('knowledge_change_log',39);
COMMIT;
