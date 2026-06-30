# ResearchOS 统一架构设计文档

## 1. 系统概览与核心理念

### 1.1 中心论点

ResearchOS 是一个**面向多研究主题（topic）的个人世界知识系统**。它的中心载体是**「按主题隔离的知识湖」**：每一个研究主题（地缘政治、交易方法论、某项前沿技术……）都是 AStockOS 分层凝练引擎的一个**独立实例**——拥有自己独立的 `knowledge.db`，里面是这个主题专属的一整套 L0/L1/L2/L3 世界知识。因此系统中存在 **N 份世界知识**，而不是一份。这正是与「单一世界知识系统（如 Ace Talk OS）」的本质区别：ResearchOS 不是「一个 topic_id 列」，而是「N 个目录、N 个数据库」。

围绕这个中心，确立四条不可动摇的设计公理（全部继承自 AStockOS 的铁律）：

1. **Python 永不做语义判断、永不调用 LLM。** Python 只负责确定性的编排、计数、校验、持久化；一切语义工作（凝练、可信度、印证质量、相关性、摘要）由 agent + 版本化的 methodology markdown 完成。
2. **物理隔离即世界知识的多副本。** 主题之间永不自动合并；同一来源被两个主题引用时，在各自的 DB 中独立蒸馏出各自的 L3。
3. **检索层是无状态的喂料管道；耐久价值只存在于每个主题的 L0–L3 阶梯。**
4. **凝练 + 唤起（priming）的闭环是系统的发动机。** 每次新检索都被该主题已有的 L0 世界模型 + 未解问题（open questions / facet gaps）唤起并定向；新检索结果又反哺、生长这套阶梯，使图景随时间越来越完整。

围绕「信息抽象轴」的证据阶梯（L0–L3，每行都要求来源 + 可信度）是 MVP 的主干。同时保留 AStockOS「双轴」洞见的第二条**方法车道（method lane，M0/M1，纯逻辑、无来源）**作为可选增量（Phase 2），承载「如何研究这个主题」的耐久方法学，与证据车道物理隔离，使「高密度单源主张」永远无法冒充「被验证的方法学」。

### 1.2 架构总图（ASCII）

```
                              ┌──────────────────────────────────────────────┐
                              │                  ros CLI （唯一受闸命令面）        │
                              │  topic / facet / brief / search / capture /     │
                              │  promote / media / condense / report / gaps /   │
                              │  method / lint / snapshot                        │
                              └───────────────┬──────────────────────────────────┘
   ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
   │  (0) PRIME 唤起                            │                                          │
   │  assembly/{context,gap,stage}.py          ▼                                          │
   │  载入本主题 L0世界模型 + L1视角 +           ┌─────────────┐                              │
   │  facet缺口 + 近期query → 冻结brief ───────▶│  搜索规划 agent │                              │
   └──────────────────────────────────────────└──────┬──────┘                              │
                                                      │ (1) SEARCH （agent 驱动，Python 不抓页面）  │
            ┌─────────────────────────────────────────┼────────────────────────────────────┐  │
            │  PUBLIC web        X / Twitter   Douyin 抖音      Xiaohongshu 小红书            │  │
            │  WebSearch内置 /    kimi-webbridge kimi-webbridge   xiaohongshu-mcp             │  │
            │  zhipu web-search   (用户真实登录)  (用户真实登录)     :18060  ✱禁 kimi-webbridge✱  │  │
            └─────────────┬───────────────────────────────────────────────┬────────────────┘  │
                          │ (2) 媒体→文本                                    │ (3) CAPTURE         │
                          ▼                                                 ▼  policy-gate 校验    │
            ┌────────────────────────────┐                    ┌───────────────────────────────┐ │
            │ media/transcribe.py (视频→文本)│                    │  sources.db （可重放原始侧库）    │ │
            │   whisper.cpp + afconvert    │                    │  source_session / source_item  │ │
            │ media/image_ocr.py (图→文本)  │                    │  content_hash 去重 / inventory   │ │
            │   zai-mcp OCR / vision       │                    └──────────────┬────────────────┘ │
            └──────────────┬───────────────┘                                   │ (4) PROMOTE URL闸 │
                           │  缓存文本写入 library/                              ▼                   │
            ┌──────────────▼────────────────────────────────────────────────────────────────────┐ │
            │  library/sources/<sha256>.json  （全局内容寻址：链接+缓存全文+转写+OCR+referenced_by[]）  │ │
            └──────────────┬────────────────────────────────────────────────────────────────────┘ │
                           │ (5) CONDENSE map-reduce （run/condense.{py,sh}，staleness guard）        │
                           ▼                                                                       │
   ┌───────────────────────────────────────────────────────────────────────────────────────────┐ │
   │  topics/<slug>/knowledge.db  ——  本主题的世界知识（证据车道 + 方法车道，物理隔离）                  │ │
   │                                                                                             │ │
   │   证据车道(信息抽象轴)   distill        aggregate            synthesize                        │ │
   │   observation ──────▶ l3_claim ──────▶ l2_finding ────────▶ l1_viewpoint ──▶ l0_worldview   │ │
   │      (单源)          (单源主张+可信度)  (多源印证, _corroborate)  (主题/子问题视角)   (世界模型, 不可裁剪) │ │
   │                                                                                             │ │
   │   方法车道(逻辑泛化轴, Phase2)   method_rule:  M1 (阶段/facet条件启发式) ── M0 (主题通用方法不变量)      │ │
   │                                                                                             │ │
   │   source_ref(URL闸触发器) · credibility_assessment · knowledge_change_log(审计) ·              │ │
   │   context_snapshot_log(冻结) · facet / open_question(缺口与未解问题) · controlled_vocab          │ │
   └───────────────────────────────────────┬───────────────────────────────────────────────────┘ │
                                            │ (6) RENDER (run/report.py 确定性渲染)                   │
                                            ▼                                                       │
            ┌───────────────────────────────────────────────────┐                                  │
            │  reports/world_model.md (活文档,覆盖重生) +           │  (7) REVIEW / GAPS               │
            │  reports/sessions/<date>_<facet>.md (会话报告,追加)    │  → 暴露稀薄/争议 facet ───────────────┘
            └───────────────────────────────────────────────────┘     反馈进入下一轮 (0) PRIME
```

---

## 2. 顶层目录结构

```
ResearchOS/
├── ros/                                  # Python 引擎（确定性管道，永不推理）
│   ├── __main__.py  cli.py  api.py  paths.py   # ros 命令；api.py 是唯一跨模块导入面
│   ├── topics.py                         # 主题注册/脚手架/别名解析
│   ├── storage/
│   │   ├── knowledge.py                  # 每主题 knowledge.db 读写：upsert_*/_audit/_corroborate/snapshot
│   │   ├── intake.py                     # 每主题 sources.db 侧库：record_capture/promote(URL闸)/inventory
│   │   ├── schema_knowledge.sql          # 冻结 v0 基线（证据车道 + 方法车道 + 闸触发器）
│   │   ├── schema_intake.sql             # 侧库 inline-SCHEMA 基线
│   │   └── migrations/NNNN_*.sql         # 编号迁移，PRAGMA user_version 跟踪
│   ├── assembly/                         # 唤起/上下文装配引擎
│   │   ├── context.py                    # assemble / candidate_packet / 应用裁剪清单 / 冻结
│   │   ├── gap.py                        # 每 facet 确定性覆盖度量（L3/L2 计数、印证深度、时效）
│   │   ├── stage.py                      # TopicStateResolver：研究阶段标签
│   │   ├── curation.py                   # LLM curator → keep-list + 紧凑 brief
│   │   ├── loading_profiles.yaml  modules.yaml
│   ├── search/
│   │   ├── source_capabilities.yaml      # 每源采集策略闸（XHS→xiaohongshu-mcp，禁 kimi-webbridge）
│   │   ├── providers.yaml                # 公网搜索分层（内置→multi-engine→zhipu）
│   │   ├── adapters/{base,web_search,x,douyin,xiaohongshu}.py   # 薄编排适配器（不抓页面）
│   │   └── capability_lint.py            # capture 时校验 collector 是否违反策略
│   ├── lib/
│   │   └── xiaohongshu_mcp_bridge.py     # XHS 非 webbridge 路径（JSON-RPC，loopback，destructive 拦截）
│   ├── media/
│   │   ├── transcribe.py                 # 视频→文本（whisper.cpp + afconvert，工具解析阶梯）
│   │   └── image_ocr.py                  # 图像→文本（zai-mcp，OCR 缺口补齐；本地 fallback）
│   ├── run/
│   │   ├── condense.py  condense.sh      # 4 段 map-reduce 凝练 + staleness guard
│   │   ├── resediment.py                 # 来源被后续转写丰富后的漂移重凝
│   │   └── report.py                     # 从 knowledge.db 确定性渲染报告
│   ├── signals/credibility.py           # 5 轴可信度记录器 + echo-chamber 断路器
│   └── boundary/
│       ├── anti_corruption.md            # 所有闸规则单一来源
│       └── gates/{import_guard,read_guard,agent_mode_lint,
│                  snapshot_provenance_lint,collector_policy_lint}.py
├── control_plane/reasoning/methodology/  # 全部推理 prose（Python 永不内嵌 prompt）
│   ├── knowledge_layering.md             # L0–L3 信息抽象轴 + 印证规则
│   ├── credibility_guide.md              # 5 轴可信度评分
│   ├── l3_distill_protocol.md  l2_aggregate_protocol.md  l1l0_synthesize_protocol.md
│   ├── gap_planning_protocol.md          # 从缺口选择下一步检索
│   ├── xiaohongshu_search_playbook.md    # XHS 风控防御（继承 SocialSearch §2-3）
│   ├── source_health_and_degradation.md  # 信源存活校验 + 渐进式风控降级（通用）
│   └── report_template.md                # 三段式会话报告契约
├── .agents/skills/researchos-{open-topic,search,condense,review,grow,xhs}/SKILL.md
├── .claude/settings.json                 # Stop hook → ros lint
├── .mcp.json                             # xiaohongshu-mcp@18060 + zhipu web-search-prime/web-reader + zai-mcp
├── topics/
│   ├── _index.yaml                       # 全局主题注册（slug/title/aliases/status/last_grown_at/coverage）
│   ├── _shared/method.db                 # 可选：跨主题方法库（仅 M0/M1，opt-in）
│   └── <slug>/                           # ★「世界知识的多副本」每个就是一个主题
│       ├── topic.yaml                    # 主题清单（见 §3.3）
│       ├── knowledge.db                  # 规范层：L0–L3 + 方法车道（gitignore，导出 SQL 快照入 git）
│       ├── sources.db                    # 可重放原始侧库（gitignore）
│       ├── reports/
│       │   ├── world_model.md            # 活文档：覆盖重生的世界模型
│       │   └── sessions/<date>_<facet>.md# 不可变会话报告（追加）
│       ├── cache/<content_hash>.md       # 链接+缓存全文快照（每主题指针，正文在 library）
│       ├── transcripts/<item_id>.{txt,srt,json}   screenshots/<item_id>.png
│       ├── artifacts/condense/{distill,aggregate,synthesize}/<id>.{in,out,err}.json
│       └── snapshots/<date>.sql          # git 提交的 knowledge.db SQL dump（耐久知识）
├── library/
│   ├── sources/<sha256>.json             # 全局内容寻址原文库（链接+缓存全文+转写+OCR+referenced_by_topics[]）
│   └── media/                            # 可再生媒体（mp4/wav）gitignore，转写后删除
├── logs/<source>/{text,jsonl}
└── .ros/active                           # 当前活跃主题指针
```

**Git 策略（解决三方案冲突）：** 实时 SQLite（`knowledge.db`/`sources.db`）一律 **gitignore**——直接提交活动 DB 会被 `git checkout` 覆盖（AStockOS `db_git_safety` 真实教训）。耐久知识通过 `topics/<slug>/snapshots/<date>.sql`（`.dump` 导出）入 git；`reports/*.md` 入 git。`library/media/` gitignore。密钥（`ZHIPU_API_KEY`）只在 env，不入库。

---

## 3. Topic（研究主题）模型与生命周期

### 3.1 多少个 topic 共存，各自一套 L0123

系统中 **N 个 topic = N 个 `topics/<slug>/` 目录 = N 份独立 `knowledge.db` = N 套完整 L0/L1/L2/L3**。没有全局 `topic_id` 列——**物理隔离本身就是「世界知识多副本」需求的实现**，也使任一主题可被原子地归档/分享/删除。主题之间永不自动合并（铁律 #2 的 ACL 跨主题应用）。

跨主题重叠由**三个显式、非合并**的机制处理（绝不复制证据行）：

1. **全局内容寻址原文库** `library/sources/<sha256>.json`：同一 URL 在「地缘政治」和「芯片出口管制」中被抓取时只存一份，带 `referenced_by_topics[]`；昂贵的抓取/转写被共享，而每主题的 provenance（`source_ref`、L3）各自独立。
2. **方法导出/导入**（Phase 2）：`topics/_shared/method.db` 作为任一主题可读取的额外 M0/M1 候选；`ros method export/import` 跨主题复制一条耐久方法规则——但**必须经一次全新凝练**，永不自动行复制。
3. **see-also 边**：`_index.yaml` 中记录 `related: [{slug, relation: shares_source|related_theme|method_overlap}]` 供导航，但不影响知识。

### 3.2 open → search → condense → re-search → grow 闭环

```
ros topic new <slug>        →  脚手架目录 + 空 knowledge.db + sources.db + topic.yaml
ros facet add --question    →  播种「待研究的子问题/侧面」(facet) —— 缺口分析的锚
ros topic open <slug>       →  设 .ros/active；打印世界模型 + 开放 facet + 建议检索
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ ros brief <slug> [--facet f]   ① 唤起：装配并冻结本主题当前 L0+L1+facet缺口+近期query │
  │ ros search <slug> "<query>"     ② 检索：策略闸路由各源，agent 抓取，落 sources.db   │
  │   --source web,x,douyin,xiaohongshu                                          │
  │ ros media transcribe / ocr      ③ 媒体→文本（视频 whisper、图像 zai-mcp）           │
  │ ros capture / ros promote       ④ 入侧库（去重）→ URL 闸提升为 source_ref + 缓存快照  │
  │ ros condense <slug>             ⑤ 凝练：distill→aggregate→synthesize 生长 L0–L3    │
  │ ros report <slug>               ⑥ 渲染 world_model.md（覆盖重生）+ 会话报告（追加）     │
  │ ros review / ros gaps <slug>    ⑦ 暴露仍稀薄/争议的 facet → 反馈进入下一轮 ①           │
  └──────────────────────────────────────────────────────────────────────────┘
```

「今天研究地缘政治、明天研究交易方法论、后天回到地缘政治」之所以无缝：状态全在每主题目录里，重拾地缘政治只需 `ros topic open geopolitics_2026`，`ros brief` 会从**已生长得更丰富的 L0** 出发定向下一次检索。

### 3.3 主题注册（`_index.yaml`）与主题清单（`topic.yaml`）

放弃独立 `registry.db`，改用**人类可读的 YAML 索引 + 别名解析**（兼顾轻量与防分叉）。`ros topic new/open` 在写入前先经 `topics.py` 的别名解析：把用户给的 slug/title/别名匹配到既有主题，避免「geopolitics」与「地缘政治」分叉成两个 DB。

`topics/_index.yaml`：
```yaml
topics:
  - slug: geopolitics_2026
    title: "2026 地缘政治格局"
    aliases: ["地缘政治", "geopolitics", "国际局势"]
    status: open            # open | dormant | archived
    created_at: 2026-06-20
    last_grown_at: 2026-06-28
    coverage: "facet 7/3已饱和; L3=142 L2=38 L1=9 L0=3"
    related:
      - {slug: chip_export_controls, relation: shares_source}
```

`topics/<slug>/topic.yaml`：
```yaml
slug: geopolitics_2026
title: "2026 地缘政治格局"
status: open
created_at: 2026-06-20
facets:                     # 开放问题地图，驱动 gap 分析与唤起
  - {id: f_taiwan, question: "台海军事/外交动向", status: deepening}
  - {id: f_chip,   question: "半导体出口管制升级", status: survey}
media_prompt: "地缘政治 台海 半导体 出口管制 北约 关税"   # whisper 领域偏置 --prompt（每主题可配）
methodology_versions: {layering: v1, credibility: v1}
stage: deepening            # scoping|survey|deepening|corroborating|saturating|mature
schema_user_version: 3
```

主题阶段（`stage.py` 的 `TopicStateResolver`）由确定性度量映射：`scoping`（facet 刚建、L3<10）→ `survey`（有 L3 无 L2）→ `deepening`（L2 在增长、印证浅）→ `corroborating`（cross_platform_count 上升）→ `saturating`（近 N 次检索新增 L3 趋零）→ `mature`。阶段标签用于**门控 M1 候选**与提示 curator，而非硬过滤。

---

## 4. L0/L1/L2/L3 世界知识模型

忠实改编 AStockOS 的**社会/信息抽象轴**（不是核心逻辑泛化轴）：L3=单条原文，L2=多源印证，L1=角色/主题视角，L0=宏观凝练。证据车道每一行都**要求** `source_ref_ids`（NOT NULL）+ `credibility_id`（NOT NULL FK）——这与 AStockOS 核心 L0/L1「纯逻辑无来源」不同，与其社会车道一致。

### 4.1 双车道与四层职责

`knowledge.db` 含两条物理隔离车道：

**(A) 证据车道（信息抽象轴）—— MVP 主干**

| 层 | 表 | 是什么 | 印证 | 来源/可信度 | 可裁剪 |
|----|----|--------|------|------------|--------|
| L3 | `l3_claim` | 单条原文（网页/X 帖/抖音视频转写/小红书笔记/图像 OCR）蒸馏出**一条**主张 | 否（单源） | 必需 | 可 |
| L2 | `l2_finding` | 多源**印证**的事实/发现（印证是 L2 的定义特征） | `corroboration_count`/`cross_platform_count` 机械计算 | 必需 | 可 |
| L1 | `l1_viewpoint` | 按 facet/子问题/角度的综合视角 | 跨 L2 | 必需 | 可 |
| L0 | `l0_worldview` | 主题宏观凝练 / 当前理解状态（唤起下一次检索的东西） | 跨 L1 | 必需 | **不可裁剪** |

**(B) 方法车道（逻辑泛化轴）—— Phase 2，可选**

| 层 | 表 | 是什么 | 来源/可信度 |
|----|----|--------|------------|
| M0 | `method_rule(level='M0')` | 关于「如何研究这个主题」的主题通用方法不变量（纯逻辑） | 无来源、无可信度、不可裁剪 |
| M1 | `method_rule(level='M1')` | 阶段/facet 条件启发式（`valid_if` JSON {stage,facet,condition}），唤起检索用 | 无来源 |

两车道永不合并（ACL）：高密度单源主张永远无法冒充被验证的方法。

### 4.2 精确 on-disk schema（SQL DDL 草图）

多值属性一律用 TEXT 列存 JSON（与 AStockOS 一致）。下面给出证据车道关键 DDL：

```sql
-- L3：单源主张
CREATE TABLE l3_claim (
  id                  TEXT PRIMARY KEY,            -- sc-<hash>
  facet               TEXT,
  proposition         TEXT NOT NULL,               -- 真正论点，非原文截断
  claim_kind          TEXT CHECK(claim_kind IN
                        ('fact','analysis','rumor','breaking','opinion','data','other')),
  source_kind         TEXT CHECK(source_kind IN
                        ('article','post','video','image','forum','paper','other')),
  single_source_ref_id TEXT NOT NULL REFERENCES source_ref(id),   -- URL 闸保证真实
  verbatim_excerpt    TEXT,
  cached_text_hash    TEXT,                         -- → library/sources/<hash>.json
  analysis_note       TEXT,
  filter_trace        TEXT NOT NULL,                -- JSON：独立性/炒作/时效检查
  debate_trace        TEXT,                         -- JSON：正/反/综合回合
  credibility_id      TEXT NOT NULL REFERENCES credibility_assessment(id),
  parent_l2_id        TEXT,
  lifecycle           TEXT,  status TEXT DEFAULT 'active',
  run_id TEXT, context_snapshot_id TEXT, context_hash TEXT,
  created_at TEXT, updated_at TEXT
);

-- L2：多源印证发现
CREATE TABLE l2_finding (
  id                  TEXT PRIMARY KEY,
  facet               TEXT,
  finding_type        TEXT CHECK(finding_type IN ('fact','event','figure','claim','trend')),
  statement           TEXT NOT NULL,
  value_text TEXT, value_num REAL, unit TEXT, valid_from TEXT, valid_to TEXT,
  corroboration_count   INTEGER,                    -- = #独立 source_ref_ids（机械）
  cross_platform_count  INTEGER,                    -- = #不同平台（机械）
  corroboration_sources TEXT,                       -- JSON 列表（_compute_corroboration 写）
  conflict_note       TEXT,                         -- agent 记录矛盾
  source_ref_ids      TEXT NOT NULL,                -- JSON 数组
  credibility_id      TEXT NOT NULL REFERENCES credibility_assessment(id),
  l3_ids              TEXT,  parent_l1_id TEXT,
  status TEXT DEFAULT 'active',
  run_id TEXT, context_snapshot_id TEXT, context_hash TEXT,
  created_at TEXT, updated_at TEXT
);

-- L1：主题/子问题综合视角
CREATE TABLE l1_viewpoint (
  id              TEXT PRIMARY KEY,
  facet           TEXT,  sub_question TEXT,
  viewpoint_scope TEXT,                              -- JSON {angle, role, stance}
  synthesis_kind  TEXT CHECK(synthesis_kind IN ('theme','sub_question','viewpoint','contrarian')),
  narrative       TEXT NOT NULL,
  stance          TEXT CHECK(stance IN ('established','contested','emerging','refuted','uncertain')),
  l2_ids          TEXT, open_questions TEXT,
  confidence      TEXT CHECK(confidence IN ('low','medium','high')),
  source_ref_ids  TEXT NOT NULL,
  credibility_id  TEXT NOT NULL REFERENCES credibility_assessment(id),
  parent_l0_id    TEXT, rank INTEGER, status TEXT DEFAULT 'active',
  run_id TEXT, context_snapshot_id TEXT, context_hash TEXT,
  created_at TEXT, updated_at TEXT
);

-- L0：主题世界模型（不可裁剪）
CREATE TABLE l0_worldview (
  id              TEXT PRIMARY KEY,
  summary_kind    TEXT CHECK(summary_kind IN
                    ('state_of_understanding','consensus','tension','frontier','other')),
  proposition     TEXT NOT NULL,
  scope           TEXT,                              -- JSON
  key_findings    TEXT,                              -- JSON：l2_finding id 数组
  open_questions  TEXT,                              -- JSON：驱动反馈闭环
  confidence      TEXT CHECK(confidence IN ('low','medium','high')),
  supersedes_id   TEXT,                              -- 前一个 worldview（链）
  l1_ids          TEXT, source_ref_ids TEXT NOT NULL,
  credibility_id  TEXT NOT NULL REFERENCES credibility_assessment(id),
  status TEXT DEFAULT 'active',
  run_id TEXT, context_snapshot_id TEXT, context_hash TEXT,
  created_at TEXT, updated_at TEXT
);

-- 方法车道（Phase 2）
CREATE TABLE method_rule (
  id TEXT PRIMARY KEY, level TEXT CHECK(level IN ('M0','M1')),
  proposition TEXT NOT NULL, valid_if TEXT,          -- M1: JSON {stage,facet,condition}; M0: NULL
  wrong_if TEXT, status TEXT DEFAULT 'active',
  created_at TEXT, updated_at TEXT                    -- 无 source_ref_ids / 无 credibility_id
);

-- 来源（URL 闸触发器）
CREATE TABLE source_ref (
  id TEXT PRIMARY KEY, subject_type TEXT, subject_id TEXT,
  platform TEXT NOT NULL, source_kind TEXT NOT NULL,
  url TEXT NOT NULL, author TEXT, title TEXT,
  captured_at TEXT, captured_by TEXT,
  content_hash TEXT, cached_text_path TEXT, media_transcript_path TEXT,
  valid_to TEXT
);
CREATE TRIGGER source_ref_url_gate BEFORE INSERT ON source_ref
BEGIN
  SELECT CASE
    WHEN trim(COALESCE(NEW.url,'')) IN ('','dataset') THEN RAISE(ABORT,'empty/placeholder url rejected')
    WHEN NOT EXISTS (SELECT 1 FROM controlled_vocab WHERE kind='platform'    AND value=NEW.platform)
         THEN RAISE(ABORT,'platform not in controlled_vocab')
    WHEN NOT EXISTS (SELECT 1 FROM controlled_vocab WHERE kind='source_kind' AND value=NEW.source_kind)
         THEN RAISE(ABORT,'source_kind not in controlled_vocab')
  END;
END;

-- 可信度（独立行，L 行 FK 指向；core 不放在 M 方法车道）
CREATE TABLE credibility_assessment (
  id TEXT PRIMARY KEY, subject_type TEXT, subject_id TEXT,
  level TEXT NOT NULL CHECK(level IN ('low','medium','high')),
  rationale TEXT NOT NULL, filter_trace TEXT NOT NULL,
  independence_note TEXT, echo_chamber_flag INTEGER DEFAULT 0,
  calibration_basis TEXT, status TEXT DEFAULT 'active', created_at TEXT
);

-- facet / 未解问题（反馈闭环显式驱动器）
CREATE TABLE facet (
  id TEXT PRIMARY KEY, question TEXT NOT NULL,
  status TEXT CHECK(status IN ('open','survey','deepening','saturating','closed')),
  last_searched_at TEXT, created_at TEXT
);
CREATE TABLE open_question (
  id TEXT PRIMARY KEY, question TEXT NOT NULL, facet_id TEXT,
  status TEXT CHECK(status IN ('open','answered','stale')),
  spawned_from_l_id TEXT, answered_by_l_id TEXT, created_at TEXT
);

-- 审计 / 上下文冻结 / 受控词表
CREATE TABLE knowledge_change_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, table_name TEXT, row_id TEXT,
  change_kind TEXT, old_blob TEXT, new_blob TEXT, diff_summary TEXT,
  changed_by TEXT, changed_at TEXT);          -- 审计表自身永不被审计
CREATE TABLE context_snapshot_log (
  snapshot_id TEXT PRIMARY KEY, payload TEXT, content_hash TEXT,
  freeze_policy TEXT, created_at TEXT);
CREATE TABLE controlled_vocab (kind TEXT, value TEXT, PRIMARY KEY(kind,value));
```

`sources.db`（侧库，inline-SCHEMA + check-then-ALTER 演进，与规范层不同演进模型——刻意保留两套）：`source_session(query,source,collector,capture_kind,raw_tool_status,degraded_reason,run_id)`、`source_item(url,title,content NOT NULL,author,captured_at,raw_metadata JSON,content_hash NOT NULL,needs_review,restricted_reason,promoted_obs_id)`、`source_inventory(PK platform+surface+external_id, first_seen,last_seen)`、`source_delta(status new|seen|missing|untracked)`。

### 4.3 凝练流程（raw → L3 → L2 → L1 → L0）

map-reduce-per-item，统一形态（继承 AStockOS `social_*` runners）：每段 **MAP**（确定性 Python 分组并写 `<id>.in.json`，把 `source_ref_id`/`credibility_id` 前向携带进 `.in.json` 以免 REDUCE 重读 DB）→ **AGENT**（一个上下文隔离的 `claude -p` 任务/项，读 methodology markdown，发出严格 JSON）→ **REDUCE**（校验并经受闸 CLI 写库）。`.out.json` 既是输出也是断点续跑键。

- **Stage 0 backfill→distill（observation→L3）：** 每个已提升的 observation → 一条 `l3_claim` + 一条 `credibility_assessment`（**先写可信度行、拿到真实 `scred-*` id 再写 L3**，规避孤儿/id 错配），附 `filter_trace`/`debate_trace`。distill 子阶段专门重写仍是「原文截断」的 proposition（`content_lint.proposition_violations` 门控）。
- **Stage 1 aggregate（L3→L2 + L1）：** agent 把 L3 按 facet/子问题分桶；REDUCE 对每条 L2 机械计算 `_compute_corroboration`（`corroboration_count` = #独立 source_ref_ids，`cross_platform_count` = #不同平台，`corroboration_sources` 列表），并校验 `credibility.subject_id == record.id`（防 agent 把分组键/PLACEHOLDER 当 id）。矛盾写入 `conflict_note`。
- **Stage 2 synthesize（L1→L0）：** agent 跨切桶合成 `l0_worldview`（`supersedes_id` 链接旧世界模型）并刷新 `open_questions`。

**计数 ≠ 可信度。** `_compute_corroboration` 只计数；计数是否意味着可信由 agent 判断。

### 4.4 增量 UPDATE / 合并 / 去重 / 冲突消解

- **整 blob upsert（不做字段级合并）：** 每个 writer 按主键 SELECT；无则 INSERT，有则 UPDATE **全部列** + `updated_at`。caller 的 payload **完全替换**该行——agent 必须前向携带要保留的字段，否则会被置空。每次写入向 `knowledge_change_log` 追加一行（`change_kind`：insert/update/dedup_skip/archive，`old_blob`/`new_blob`/`diff_summary`）。这给了「免引擎的时间旅行/审计」。
- **去重：** `content_hash = sha256(归一化正文)` 在入库时拒绝完全重复；`source_inventory` PK(platform,surface,external_id) + first/last_seen 给出跨会话 new/seen/missing/untracked 增量；提升用确定性 `obs-<item_id>` id 幂等（崩溃可恢复，不会 PK 冲突）。`library` 内容寻址使同一 hash 跨主题只存一份原文。
- **合并/生长：** 新检索 → URL 闸提升 → distill/aggregate/synthesize **重跑**；upsert 通过在更大来源集上**重算 L2 印证**、重凝 L1/L0 实现「合并」，`supersedes_id` 链接旧世界模型。每轮 `open_questions` 收缩/精化，`corroboration_count` 增长。
- **冲突消解：** 新来源与既有 L2 矛盾时 → 写入 `conflict_note` 并重新辩论，**不静默覆盖**。当两条独立印证的 L2 直接相左：保留两行 + 一条 `synthesis_kind='contrarian'` 的 L1「张力」综合（而非强删一条）。

### 4.5 Provenance、可信度、快照/版本

- **Provenance：** 单一 `source_ref`（URL NOT NULL + BEFORE INSERT 触发器拒空/`dataset`/词表外平台），L 行经 `source_ref_ids` JSON 数组引用。
- **可信度：** agent 判定的 5 轴（独立性/质量密度/内部一致/逻辑契合/时效衰减）成独立 `credibility_assessment` 行，每条证据 L 行 FK 指向；Python 只校验 verdict + 要求非空 rationale，并对 `echo_chamber_flag=1` **机械封顶 level→low**（`[CIRCUIT BREAKER]` 标注，「来源数量不能压过回音室嫌疑」）。清理只软归档（`status='archived'`），永不 DELETE（因 FK NOT NULL）。
- **快照/版本：** 规范层只经编号 `migrations/NNNN_*.sql` 演进，`PRAGMA user_version` 跟踪，`schema_knowledge.sql` 是冻结 v0 基线（DDL 永不改，只加迁移）。`context_snapshot_log` 追加冻结上下文；每条知识写回携带 `run_id`/`context_snapshot_id`/`context_hash` 绑定到 agent 当时看到的确切上下文。`freeze_context_payload` 把信号/原文正文冗余化为 sha256+长度（TTL/版权安全）；migration-style 触发器拒绝「非空 `context_snapshot_id` 但不在 `context_snapshot_log`」的伪造 provenance（AStockOS 真实抓到过的事故）。耐久知识通过 `snapshots/<date>.sql` dump 入 git。

---

## 5. 搜索层（Search Layer）

### 5.1 适配器接口（薄编排，不抓页面）

铁律：Python 永不抓页面；**agent 驱动 MCP/浏览器抓取，Python 编排 + 校验 + 持久化**。`SourceAdapter`（`search/adapters/base.py`）是抽象基类：

```python
@dataclass
class SearchQuery:
    topic_slug: str; keywords: list[str]; source: str
    max_items: int = 10; lookback_hours: int = 48
    prime_brief: str | None = None              # ← 由 ros brief 唤起

@dataclass
class RawItem:
    source: str; external_id: str; url: str | None
    title: str; text: str; author: str | None; captured_at: str  # CST
    media_refs: list[dict]      # [{kind,url,local_path,transcript_path}]
    raw_metadata: dict          # {engagement,tags,xsec_token,restricted_reason,...}
    content_hash: str           # sha256(text)
    needs_review: bool = False; restricted_reason: str | None = None

class SourceAdapter(ABC):
    id: str; collector: str
    def __init__(self): registry.enforce(self)   # ← 构造时即校验策略闸
    @abstractmethod
    def search(self, q: SearchQuery) -> Iterator[RawItem]: ...
    @abstractmethod
    def fetch_detail(self, item: RawItem) -> RawItem: ...   # 触发媒体→文本
    def healthcheck(self) -> dict: ...
```

适配器**不**在 Python 里抓取——它构造 query/URL 并把策略交给 agent（按 skill 驱动浏览器/MCP）。`registry.enforce(self)` 读 `source_capabilities.yaml`，若 `self.collector` 在该源的 `forbidden_search_collectors` 或 `!= required_search_collector` 则**抛错**——这是 XHS 硬约束的不可绕过执行点。agent 抓到后调 `ros capture <payload> --source <s>`，`capability_lint.py` 在 capture 时再次拒绝违规 collector。

爬取预算纪律（继承 SocialSearch）：**同平台串行、跨平台并行**；动作间 2–5s 等待；单平台单任务 ≤10 次页面访问或 48h 回看；遇验证码/强制登出/QR 墙一律 **STOP 不重试**（重试会作废用户登录会话）。

### 5.2 每平台抓取机制表（具体）

| 源 | required collector | 入口 / 机制 | 私有面（favorites/likes） | 媒体 | 禁用 |
|----|-------------------|-------------|--------------------------|------|------|
| **公网 web / Google** | runtime-builtin → multi-search-engine → zhipu | T1 内置 `WebSearch`/`WebFetch`；T2 `multi-search-engine` skill（Bing CN/Sogou，env `ROS_MULTI_SEARCH_SKILL_DIR`）；T3 zhipu `web-search-prime` MCP（`open.bigmodel.cn/api/mcp/web_search_prime/mcp`，Bearer `ZHIPU_API_KEY`）+ `web-reader` 取全文 | — | — | — |
| **X / Twitter** | kimi-webbridge | 公网搜 `https://x.com/search?q={q}`；虚拟滚动累积 tweetId（React 回收 DOM，跨 ~20 轮累积、按页位排序），文本前置过滤 | likes/bookmarks（用户真实登录会话） | — | — |
| **Douyin 抖音** | kimi-webbridge | 搜 `https://www.douyin.com/search/{q}`；从 `performance.getEntriesByType('resource')`+`video.currentSrc` 捕获媒体 URL | 收藏 `#semiTabfavorite_collection` | whisper 转写 | — |
| **Xiaohongshu 小红书** | **xiaohongshu-mcp** | 见 §5.3 | favorites 列表卡片元数据 **仅** 可走 kimi-webbridge；detail 必走 mcp | zai-mcp OCR（图多）+ whisper | **kimi-webbridge / browser 禁用** |

`source_capabilities.yaml`（小红书条目，权威策略）：
```yaml
xiaohongshu:
  required_search_collector: xiaohongshu-mcp
  forbidden_search_collectors: [kimi-webbridge, browser]
  search_entry: "tool:search_feeds"
  favorites_list_collector: kimi-webbridge       # 仅卡片元数据
  favorites_detail_collector: xiaohongshu-mcp
  favorites_browser_detail_allowed: false
  favorites_mcp_restart_on_detail_failure: true
  favorites_new_item_image_recognition_required: true
```

### 5.3 小红书非 kimi-webbridge 路径（硬约束）

**所有 XHS 搜索 + 笔记详情走本地独立运行的 `xiaohongshu-mcp` 服务**（`http://localhost:18060/mcp`，Streamable-HTTP JSON-RPC，proto 2025-03-26，由它持有 XHS 登录/cookie 会话）：

- 首选作为 **native MCP tool**（`.mcp.json` 接入）调用 `search_feeds`、笔记 detail 工具；
- 当 runtime 未暴露该工具时，回退到移植自 AStockOS 的 `ros/lib/xiaohongshu_mcp_bridge.py`（urllib JSON-RPC：`initialize → Mcp-Session-Id → tools/list → tools/call`，**loopback 强制**、destructiveHint 工具拦截、SSE data-frame 解析），命令面 `ros xhs status|tools|call`。端点可经 env `ROS_XHS_MCP_URL` 覆盖。
- **绝不**导航裸 `/explore/{noteId}`（触发「请打开 App 扫码查看」风控墙）——一律经 `search_result`/`xsec_token` 经 MCP。
- MCP 不可用时：降级到列表卡片证据 + `needs_review`（favorites 列表卡片可经 kimi-webbridge 取**元数据**），**绝不**为 detail 回退浏览器。
- 运维：MCP 使用后 `pkill -f 'rod/user-data'` 清理 rod Chrome 孤儿（leakless 看门狗不触发）。
- SEP 的 `xhs_scrape.py`（用 kimi-webbridge 抓 XHS）**明确不移植**。

### 5.4 由既有主题知识唤起 query

`ros brief <slug>` 前置每次检索：`gap.py` 算每 facet 覆盖度量、`stage.py` 贴研究阶段标签、`context.py` **load-all**（载入本主题全部 active L0+L1+open_questions + 阶段门控 M1 + facet 缺口 + 近 N 次 `search_log` query，**Python 不做语义过滤**），冻结为 `context_snapshot.v1`，curator（LLM）在 token 预算内发出 keep-list + 紧凑 brief（**L0/M0 不可裁剪**，预算 ~12k）。brief 告诉检索 agent：已确立什么（跳过重复检索）、该追哪些 `open_questions`/稀薄 facet（永不重跑近期 query）。把 **brief（而非原始候选 JSON）** 交给检索 agent——这就是「用今天的知识唤起明天的检索」。

---

## 6. 抽取与归一化（Extract & Normalize）

### 6.1 原始捕获

agent 抓取后产出 `RawItem`（§5.1 schema）。`ros capture <payload> --topic <slug> --run-id <id>` 经 `capability_lint` 后写 `sources.db`（`source_session`+`source_item`，`content_hash` 去重，`source_inventory`/`source_delta` 增量）。原始浏览器证据（DOM 快照、mcp_details、封面图、转写）作为 tracked artifact 留在 `topics/<slug>/screenshots|transcripts|artifacts/`。

### 6.2 媒体 → 文本（落库前完成，使报告纯文本）

**视频/音频 → 文本（`ros/media/transcribe.py`，几乎逐字移植 AStockOS `lib/media_transcript.py`）：** agent 经 kimi-webbridge 取音频优先媒体 URL（`performance.getEntriesByType('resource')`+`video.currentSrc`，正则 audio 先于 video）→ urllib 下载（UA+referer）→ `afconvert -f WAVE -d LEI16@16000 -c 1` 转 16kHz 单声道 WAV → `whisper-cli ggml-large-v3-turbo -l zh -otxt -osrt -oj --prompt <topic.media_prompt>`（领域偏置 prompt **每主题可配**，泛化自 SEP 写死的金融 prompt）；>20min 自动切 10min 段拼接。返回可审计记录 `{status: transcribed|needs_review|failed, transcript_text, transcript_hash(sha256), char_count, srt/json 路径}`。工具/模型解析阶梯：**显式参数 → env(`ROS_WHISPER_*`) → 默认 → PATH 探测(`shutil.which`) → status:failed**（绝不在错误机器上崩溃）。原始 mp4/wav 转写成功后删除（disk 压力）。

**图像/截图 → 文本（`ros/media/image_ocr.py`，补齐三方都缺的 OCR 能力）：** 包装环境内 `zai-mcp` 的 `extract_text_from_screenshot` / `analyze_image` / `analyze_data_visualization`（图内 K 线/图表/表格）/ `understand_technical_diagram`，把图多的帖子（XHS 常见）转成留存文本；MCP 不可用时回退多模态 agent 直接读截图。**策略：** zai-mcp 是云出口，与参考仓库的本地优先教条有张力——故设为**显式 opt-in 策略开关**（`policy.image_ocr.provider: zai-mcp | paddleocr-local | tesseract-local`），默认 zai-mcp（本环境已具备），本地 OCR 作为替代。

两者产出的文本写入 `library/sources/<hash>.json` 作为缓存快照，并成为 L3 distill 的输入。策略闸阻止「未转写视频 / 未识别图像」入库提升。

### 6.3 去重与归一化记录 schema

`content_hash=sha256(归一化文本)` 是完整性/去重键；跨主题去重经 `library` 内容寻址；身份键按平台（XHS note_id 24-hex / X tweet_id / 抖音 aweme_id / web url）。**不做向量检索**：排序非 Python 打分——印证用 `_compute_corroboration` 机械计数，相关性/可信度由 agent 编辑判断；报告排序/裁剪走 load-all 候选 + 确定性 parent-link reachability（l3→l2→l1→l0）+ curator keep-list（L0 不可裁剪、`candidate_hash` 必须匹配）。归一化记录即 `RawItem`（见 §5.1）。

---

## 7. 原文留存与统一报告

### 7.1 原文三重留存

每条被提升的来源以三种方式留存：

1. **链接：** `source_ref(url NOT NULL)`（URL 闸触发器拒空/`dataset`/词表外）。
2. **缓存文本快照：** 提升时把归一化全文写 `topics/<slug>/cache/<content_hash>.md`，路径存 `source_ref.cached_text_path`——满足「链接 + 缓存文本快照」。
3. **媒体→文本：** 视频转写在 `transcripts/<item_id>.{txt,srt,json}`、图像 OCR 文本，经 `source_ref.media_transcript_path` 引用；原截图在 `screenshots/`。

**全局内容寻址：** 同一 URL 跨主题只存一份 `library/sources/<sha256>.json = {url, fetched_at, platform, author, title, cached_full_text, media_transcript, ocr_text, screenshot_path, referenced_by_topics[]}`。**视频/图像在留存前就已转成文本**，故快照恒为文本。对 TTL/版权敏感源，冻结载荷把全文冗余化为 sha256+长度（`freeze_context_payload`），library 文件是唯一全文副本且 gitignore。KEEP-vs-可再生策略：转写/截图/OCR 文本/封面 tracked；mp4/wav gitignore 且转写后删除。`sources.db` 侧库保留完整可重放 `raw_metadata`，任一来源无需重抓即可重凝。

### 7.2 报告格式与「报告累积成知识」

**两个 markdown 产物，均可引用（解决三方案冲突——确定性渲染 + 会话追加）：**

- **`reports/world_model.md`（活文档，`ros condense` 后由 `run/report.py` 从 `knowledge.db` 确定性覆盖重生）**：语义凝练 prose 由 agent 写进 DB，渲染是纯 Python。固定段落：① 主题概览/Worldview（当前 `l0_worldview` proposition + confidence + supersedes 链）；② 开放问题/Open Questions（聚合 `open_questions` = 检索议程）；③ 分主题综合/Themes（每 `l1_viewpoint` narrative + stance + confidence）；④ 已证实发现/Corroborated Findings（`l2_finding` 表：statement + corroboration_count + cross_platform_count + conflict_note）；⑤ 来源索引/Source Index（`l3_claim`/`source_ref` 表：序号│标题│作者│平台│链接│可信度│缓存路径）；⑥ 待复核/Needs Review（restricted/needs_review）；⑦ facet 覆盖表；⑧ 声明（信息关联非建议）。这是主题不断累积的「越来越完整的图景」。
- **`reports/sessions/<date>_<facet>.md`（不可变会话报告，追加）**：三段式（继承 SEP `report_template.md` + SocialSearch schema）：核心要点 / 论点与证据逻辑链（每条带 provenance）/ 来源索引 + 待人工复核 + 声明。

**累积规则：** `world_model.md` 覆盖重生（当前真相），`sessions/` 追加（历史）。每个 claim 携带 provenance（url + 缓存路径 + 可信度）。

---

## 8. 知识回馈闭环（Feedback Loop）

```
              ┌────────────── 越来越完整的图景（随时间） ──────────────┐
              │                                                      │
   ┌──────────▼──────────┐   brief    ┌───────────┐  raw   ┌─────────┴────────┐
   │  l0_worldview(世界模型)│──────────▶│  新一轮检索  │───────▶│  distill/aggregate │
   │  + open_questions    │ (唤起/定向)  │ (定向稀薄缺口)│ (反哺)  │  /synthesize       │
   │  + facet 缺口报告      │◀──────────│           │◀───────│  upsert + audit    │
   └──────────────────────┘  gap 反馈   └───────────┘ 关闭/  └────────────────────┘
                                                      派生 open_question
```

- **唤起（先验知识 → 新检索）：** `ros brief` 确定性载入本主题当前 L0 + L1 + 阶段门控 M1 + `gap.py` 的 facet 缺口报告 + `search_log` 近 N 次 query，冻结为 `context_snapshot.v1`，交检索规划 agent，agent 提出**定向稀薄/争议 facet** 的排序 query（永不重跑近期 query）。
- **生长（新检索 → 知识）：** 捕获的来源经 E3→E2→E1→E0 凝练，带审计 upsert，`world_model.md` 重生；staleness guard 在 L3 改变时重导下游层。
- **缺口检测（`gap.py`，确定性）：** 每 facet 计算 L3/L2 计数、印证深度（cross_platform_count）、时效（最近来源 `captured_at`）、`last_searched_at`。`ros gaps` 打印度量并建议新建/可关闭 facet。facet 饱和（近 N 轮新增 L3 趋零）→ 阶段升 `saturating/mature`。
- **闭环收口：** 新生长的 L0 + 更新的 facet 覆盖 + 新 `search_log` 成为下一次 `ros brief` 的输入，每轮从严格更丰富的先验出发。`open_question(spawned_from_l_id, answered_by_l_id)` 显式把新检索绑回先验知识——每轮 `open_questions` 收缩/精化、`corroboration_count` 增长。

---

## 9. 复用映射（Reuse Map）

| ResearchOS 组件 | 复用的参考项目代码/模式 | 改编要点 |
|----------------|----------------------|---------|
| `knowledge.db` 证据车道 L0–L3 DDL | AStockOS migrations 0012/0016 `social_l3_claim`/`social_l2_fact`/`social_l2_judgment`/`social_l_rule`（信息抽象轴） | 脱离股票泛化；L0/L1 保留 source_ref_ids+credibility |
| `method_rule`（方法车道 M0/M1，Phase2） | AStockOS `schema.sql` `l_rule`（逻辑泛化轴，纯逻辑无来源） | 改为「研究方法不变量/启发式」 |
| `upsert_*`/`_audit_change`/`_compute_corroboration`/`*_snapshot`/`read_ranked_chain` | AStockOS `data/storage/sqlite.py` | 整 blob upsert + 追加审计 |
| `sources.db` 侧库 + URL 闸幂等提升 + favorites delta + content_hash | AStockOS `data/sidecars/social_knowledge.py` | env 可覆盖路径，每主题一份 |
| `source_ref` URL 拒绝 BEFORE-INSERT 触发器 + controlled_vocab + provenance 触发器 | AStockOS `data/schema.sql` + migration 0020 | 不可绕过 provenance 闸 |
| map-reduce 凝练 runners（MAP per-item .in.json / AGENT 严格 JSON / REDUCE 受闸写）+ queue-delta staleness guard | AStockOS `run/social_{backfill,distill,aggregate,synthesize}.py` + `social_sediment.sh` + `social_resediment.py` | `.out.json` 续跑键 |
| `assembly/{context,gap,stage,curation}.py`（load-all 候选、确定性 parent-link scoping、curator keep-list、L0 非裁、candidate_hash 匹配、研究阶段标签） | AStockOS `control_plane/assembly/context.py` + `curation.py` + `analysis/context/{regime,l1_selector}.py` | regime → 研究阶段 |
| 5 轴可信度 + echo-chamber 断路器 + `credibility_guide.md` | AStockOS `signals/credibility/recorder.py` + methodology | social 要求 filter_trace |
| **XHS 非 webbridge 路径** `lib/xiaohongshu_mcp_bridge.py` + `ros xhs` + source_capabilities 策略 | AStockOS `lib/xiaohongshu_mcp_bridge.py` + `cli.py xhs-mcp` + `source_capabilities.yaml`（forbidden:[kimi-webbridge,browser]） | **逐字移植** |
| `media/transcribe.py`（视频 ASR，工具解析阶梯、长音频切段） | AStockOS `lib/media_transcript.py` | **逐字移植**，仅 prompt 改每主题可配 |
| `media/image_ocr.py`（图像 OCR/vision，补 OCR 缺口） | zai-mcp `extract_text_from_screenshot`/`analyze_image`/`analyze_data_visualization`（**新接线**） | opt-in 云出口策略 + 本地 fallback |
| `search/adapters` + kimi-webbridge 传输（X/Douyin）+ recent_ids 基线 diff | SEP `scripts/browser_session.py` + `x_likes_scrape.py` + `douyin_*` + `inventory_manager.py` | XHS 路径**不**沿用 SEP |
| 公网搜索分层 `providers.yaml` + `.mcp.json` zhipu | AStockOS `search_providers.yaml` + `.mcp.json` web-search-prime/web-reader | — |
| 报告固定段落 + 三段式 + 风控 playbook | SEP `report_template.md` + `douyin_summarize.py` + SocialSearch `README`/`AGENTS.md` schema 与防御 | 渲染改纯 Python（world_model）+ agent 会话报告 |
| boundary gates（import/read/agent_mode/snapshot_provenance/collector_policy）+ Stop hook + DB 触发器 | AStockOS `control_plane/boundary/gates/*` + `anti_corruption.md` + migration 0020 | run/ 在 read_guard 外 → subprocess ACL |
| skills 与命令面 | AStockOS `cli.py` argparse + `.agents/skills/*` + subprocess-ACL 合约 | — |

---

## 10. CLI / 命令面

单一受闸命令面 `ros <noun> <verb>`（`ros/cli.py`，argparse；runners 与 skills 只 shell `ros`，永不裸开 DB）。隐式活跃主题（`.ros/active`），多数命令可省 `<slug>`。

```
# 主题与 facet
ros topic new <slug> [--title T --alias A ...]   # 脚手架 + db-init + 写 _index.yaml（别名解析防分叉）
ros topic open <slug> | resume <slug>            # 设 active；打印世界模型+开放facet+建议检索
ros topic ls | show <slug> | archive <slug>
ros facet add <slug> --question "..."  | facet close <slug> <facet_id>

# 唤起 → 检索 → 抽取 → 提升
ros brief <slug> [--facet f]                     # 装配并冻结唤起 brief，返回 run_id
ros search <slug> "<query>" --source web,x,douyin,xiaohongshu   # 策略闸路由，agent 抓取落 sources.db
ros media transcribe <url|file> [--prompt ...]   # 视频→文本（whisper）
ros media ocr <image|screenshot>                 # 图像→文本（zai-mcp / 本地）
ros capture <payload.json> --topic <slug> --run-id <id> [--auto-promote]   # 入侧库（collector 闸）
ros promote <slug>                               # URL 闸提升 source_item → source_ref + cache/<hash>.md

# 凝练 → 渲染 → 复盘
ros condense <slug> [--stage all|distill|aggregate|synthesize]  # 经 condense.sh，staleness guard
ros report <slug> [--session]                    # 渲染 world_model.md（覆盖）+ 会话报告（追加）
ros review <slug>                                # 世界模型 + 争议 + needs_review 队列
ros gaps <slug>                                  # facet 覆盖度量 + 建议新建/关闭 facet
ros snapshot <slug>                              # 冻结上下文 + 导出 snapshots/<date>.sql（git 耐久）

# XHS / 方法 / 治理
ros xhs status|tools|call                        # xiaohongshu-mcp 桥
ros method export <slug> <rule_id> | method import <slug>   # 跨主题方法（需全新凝练，Phase2）
ros lint                                          # 全部 boundary gates（pre-commit + Stop hook 绑定）
ros db dump|verify <slug>
```

典型一轮：`ros topic open geopolitics_2026` → `ros brief` → `ros search ... --source web,x,xiaohongshu` → `ros media transcribe/ocr` → `ros capture --auto-promote` → `ros condense` → `ros report` → `ros gaps`（→ 下一轮 `ros brief`）。

---

## 11. 实施路线图（Build Roadmap）

**Phase 0 — 地基（1 周）：** `ros` CLI argparse 骨架 + `paths.py`；`schema_knowledge.sql`/`schema_intake.sql` 冻结基线 + migrations 框架（`PRAGMA user_version`）；`storage/knowledge.py`（upsert_* + `_audit_change` + `_compute_corroboration`）+ `storage/intake.py`（record_capture + URL 闸提升）；`source_ref` 触发器 + `controlled_vocab` 种子；`topics.py` 脚手架 + `_index.yaml` 别名解析。**验收：** `ros topic new/open` 建库，手工 `ros capture/promote` 走通 URL 闸。

**Phase 1 — MVP（单主题、公网 + XHS、纯文本，2–3 周）：**
- 搜索：`adapters/web_search.py`（runtime-builtin + zhipu）+ `adapters/xiaohongshu.py`（`xiaohongshu_mcp_bridge.py` 移植 + `ros xhs`）；`source_capabilities.yaml` + `capability_lint`（**先把 XHS 硬约束闸打通**）。
- 凝练：`run/condense.{py,sh}` 四段 map-reduce + staleness guard；`methodology/{layering,l3_distill,l2_aggregate,l1l0_synthesize,credibility_guide}.md`；`signals/credibility.py`。
- 留存与报告：`library/sources/<hash>.json` + `cache/<hash>.md`；`run/report.py` 渲染 `world_model.md`。
- **验收：** 开「地缘政治」主题，跑 web+XHS 检索 → 凝练出 L0–L3 → 渲染 world_model.md，原文链接+缓存文本齐全。

**Phase 2 — 唤起闭环 + 私有媒体（2 周）：** `assembly/{context,gap,stage,curation}.py` + `ros brief`/`gaps`/`review`；`facet`/`open_question` 驱动；`adapters/x.py` + `adapters/douyin.py`（kimi-webbridge）；`media/transcribe.py`（视频 ASR）+ `media/image_ocr.py`（zai-mcp OCR）；会话报告。**验收：** brief 唤起的检索能定向稀薄 facet；视频/图像转文本入库；闭环可见生长。

**Phase 3 — 多主题规模化 + 治理（1–2 周）：** 多主题共存 + `library` 跨主题共享 + `referenced_by_topics[]`；`boundary/gates/*` + Stop hook + pre-commit；`snapshots/<date>.sql` git 流程；`resediment.py` 漂移重凝；providers 分层（multi-engine）。**验收：** 多主题交错研究互不污染；lint 通过；DB gitignore + SQL 快照入 git。

**Phase 4 — 方法车道与高级特性（按需）：** `method_rule` M0/M1 + `topics/_shared/method.db` + `ros method export/import`（全新凝练闸）；阶段阈值标定；规模化时为唤起加 recency/embedding 预过滤；`ros loop`/cron 后台慢生长（登录/daemon 存活脆弱，先手动触发）。

---

## 12. 风险与未决问题

### 12.1 风险（及缓解）

1. **macOS 工具链：** `whisper-cli`+`afconvert` 是 mac/brew 专属、慢（~10–30s/音频分钟），SEP 写死模型路径。缓解：`transcribe.py` 显式→env→默认→PATH 探测→`status:failed` 阶梯，绝不崩溃；非 mac 部署需替换。
2. **外部 daemon 依赖：** `xiaohongshu-mcp` 须独立运行于 :18060（持 XHS 登录），按策略 **XHS detail 无 webbridge 回退**，只降级列表卡片证据 + `needs_review` + `favorites_mcp_restart_on_detail_failure`；用后 `pkill -f 'rod/user-data'`。`kimi-webbridge` :10086 + 真实登录浏览器供 X/Douyin；遇验证码/强制登出/QR 墙 **STOP 不重试**（重试会作废登录会话）。
3. **整 blob upsert 不做字段合并：** REDUCE 漏字段会置空——agent 必须前向携带状态；印证须每轮在全量来源集重算。
4. **缓存按 `.out.json` 存在跳过会静默用旧 rollup：** 必须走 `condense.sh` 的 queue-delta 失效，**绝不**单独跑 aggregate。
5. **每主题 DB 增殖 + 主题身份歧义：** 无严格别名解析则同一研究线分叉成重复 DB——`_index.yaml` 别名表 + `ros topic merge` 逃生舱。
6. **跨主题污染：** 方法提升若自动复制证据则越界——强制「全新凝练」闸，证据行永不跨主题。
7. **伪造 provenance：** 非空 `context_snapshot_id` 不在 `context_snapshot_log` → `snapshot_provenance_lint` + DB 触发器 ABORT（抓到过真实事故）。
8. **agent 发畸形记录**（分组键/PLACEHOLDER 当 id、字段别名错）：REDUCE 必须校验 `subject_id==record.id` + 归一化别名。
9. **zai-mcp OCR 云出口** 与本地优先教条张力：设为显式 opt-in 策略，提供 paddleocr/tesseract 本地替代。
10. **Git 与 SQLite：** 提交活动 DB 有 checkout 覆盖风险（`db_git_safety`）→ DB gitignore，耐久态导出 `snapshots/<date>.sql`。
11. **选择器漂移**（Douyin `#semiTabfavorite_collection`、XHS `.feeds-container`、X 虚拟滚动）静默返回 0 项 → healthcheck 断言 + `needs_review`。
12. **密钥：** `ZHIPU_API_KEY` 只在 env，不入库。

### 12.2 未决问题

1. **主题粒度/身份：** 什么使新检索成为「新主题」而非既有主题的子线（如「AI 芯片」属于「地缘政治」还是独立主题）？需启发式 + `ros topic merge/split`，可能需父/子主题树。
2. **方法车道是否值得：** 个人研究工具中 M0/M1 的额外复杂度是否划算，还是 v1 单证据阶梯 + `open_question` 即足够？（本设计置于 Phase 4 可选）。
3. **规模化唤起：** load-all 候选在主题积累上千 L 行后会超 token 预算——可能需 recency/embedding 预过滤喂候选包（偏离 AStockOS 纯 load-all）。
4. **跨主题来源失效：** 某来源被重抓/更新时，`referenced_by_topics[]` 是否需对 N 个主题各自的漂移检测重凝？
5. **版权/TTL 留存：** 多少全文可合法缓存——默认对敏感源 freeze-redact-to-hash，全文仅对用户自有/许可源。
6. **冲突建模：** 两条独立印证的 L2 直接相左，保留一行 + `conflict_note` 还是两行 + L1「张力」综合？（本设计选后者，待验证）。
7. **search-cache TTL：** facet 多久可「重新检索」（快变主题如地缘政治来源易过期）？
8. **`world_model.md` 真相源：** 从 DB 重生（当前设计）还是可手编再回灌（round-trip 风险）？
9. **多语言报告：** 主题常混中文社媒 + 英文 web——单语报告还是按源语言 + 翻译？
10. **媒体→文本置信度：** 低置信转写/OCR 是否标 `needs_review` 并在印证计数中排除直至复核？
11. **`multi-search-engine` skill** 是外部依赖（`ROS_MULTI_SEARCH_SKILL_DIR`），本环境未必存在——需自建或替换。
12. **后台自动化：** 把 `brief→search→condense` 接入 cron/loop 做慢生长，还是严格用户触发（登录/daemon 存活使无人值守脆弱，建议先手动）？