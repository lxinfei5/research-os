# TravelOS（本地版）设计

> Root: `<local-travelos-path>`
> 源内容暂存于 `_hermes_export/.../Hermes_LifeOS/TravelOS/`（~50 个 md，320KB，无代码）
> 设计日期：2026-06-28。本文是经多智能体分析 + 两轮对抗式评审收敛后的最终设计。

---

## 0. 一句话

把 hermes 里那套**纯 markdown 的旅行运营系统**原样搬到本地，并接上三件只有本地能干的事：用**真实登录的浏览器**抓小红书/抖音原文、做**可视化**、未来给相册照片**回填 GPS**。claude 是唯一的脑，python 只做机械胶水，整体**刻意保持轻**。

---

## 1. 定位与两条原则

TravelOS 是**文档为中心、单用户、本地优先**的旅行系统，覆盖 `想去 → 立框架 → 长期补细节 → 临场执行 → 复盘` 全过程。

**原则一（与 AStockOS 一致，只取这一条）：claude = 唯一 reasoner，python = 机械胶水。**
所有 LLM 对话、判断、归纳、摘要、相关性判断都由 agent 做；python 只做：文件 IO、把 agent 抓到的数据落盘、HTML→文本清洗、渲染可视化、读写 EXIF。**python 里不出现任何 LLM API 调用，也不存放"如何推理/如何写卡"的长 prompt 常量。** 唯一护栏是一个 ~15 行的 grep lint。

**原则二（与 AStockOS 相反，用户明确要求）：刻意轻量、保持灵活。**
不建合约层、注册表、生命周期治理、schema 迁移机器、向量库、一堆 lint。markdown 继续当数据库。任何"加一条记录"必须**近乎零仪式**——用户随时可能说"补一个 2019 年的历史旅行"或"记一下今天去了哪"，这两件事都不能有门槛。

---

## 2. 数据模型 / 目录结构

### 2.1 继承 hermes 分类法的决定

| hermes 分类 | 决定 | 理由 |
|---|---|---|
| `Trips/{Candidate,Active,Completed}/` | **保留** | 生命周期=文件夹位置，零状态机。Active 互斥靠"目录里只有一个"自然保证。 |
| `Places/{Visited,Wishlist}/` | **保留**（Visited/Wishlist 也只是文件夹位置） | 地点卡是可视化和"博主同款"复用的主键资产。 |
| `Routes/` | **保留** | 可复用半日/全日组合，被 Trip 引用。 |
| `Research/` | **精简**：删长期空的 `Airfare_Watch`、`Creator_Watchlist`；保留 `Destination_Research/`（抓取产物落点）和 `Playbooks/`（真有内容）。 | 过度预留的 Research 层正是 hermes 烂掉原因之一。 |
| `Models/` | **保留**：`Travel_Preferences.md` / `Open_Questions.md` / `Research_Sources.md` | 偏好/口味是 agent 做判断的输入。 |
| `Templates/` | **保留但收敛到 3 个模板**（见 2.3）；旧模板不进新仓。 | 防 template drift（hermes 的头号病）。 |
| `Inbox/` | **保留** | "先收进去再结构化"的入口。 |
| — | **新增** `Captures/` | 抓取原始落地的临时暂存区（仅放"还没归属到某趟 trip"的散抓）。 |
| — | **新增** `travelos/`（python 胶水）+ `.agents/skills/` + `AGENTS.md` | 本地化新增的工程层。 |

### 2.2 目标磁盘布局

```
TravelOS/
├── AGENTS.md                  # agent 操作手册（唯一 constitution；CLAUDE.md 软链到它）
├── README.md                  # L0：怎么跑
├── DESIGN.md                  # 本文
│
├── Trips/
│   ├── Candidate/  2026_新疆北疆.md           # 候选可以就一个 md
│   ├── Active/                                 # 互斥：永远 0 或 1 个目录
│   │   └── 2026-06_河池都安/
│   │       ├── Trip.md         # 主卡（YAML frontmatter + 自由正文，见 2.3）
│   │       ├── Assets/         # 原始截图（机票/酒店/聊天/路线/攻略）— 按需懒创建
│   │       ├── Evidence/       # 截图的结构化 md 摘录 — 按需懒创建
│   │       └── Viz/            # 生成的可视化 html — 按需懒创建
│   └── Completed/
│       └── 2026-05_五一温州宁波/              # 结构同 Active，整目录搬过来
│
├── Places/{Visited,Wishlist}/  *.md           # 地点卡（YAML frontmatter 带 geo）
├── Routes/                     *.md
├── Research/
│   ├── Destination_Research/2026-06_河池荔波/  # 抓取/研究产物（md + 附原始 html）
│   └── Playbooks/                              # browser_first / asset_archiving
├── Models/      Travel_Preferences.md  Open_Questions.md  Research_Sources.md
├── Templates/   trip.md  place.md  note.md     # 仅 3 个
├── Inbox/
│
├── Captures/                                   # 散抓暂存（已归属的不放这）
│   └── 2026-06-28_xhs_<postid>/
│       ├── raw.json            # agent 抓到的 note 元数据/正文/图链（python 落盘）
│       ├── content.md          # html→clean text
│       └── img_*.jpg           # 下载的全部图（含轮播图，供 vision 逐张读）
│
├── travelos/                   # python 胶水层（零 LLM）
│   ├── cli.py                  # argparse，≤8 子命令，唯一 python 入口
│   ├── capture.py  htmlclean.py  archive.py  viz.py  lint.py
│   └── (exif.py — phase 3 才加)
└── .agents/skills/
    ├── travelos-trip/SKILL.md          # /trip-add /trip-status
    ├── travelos-extract/SKILL.md       # /extract-xhs /extract-douyin /research-dest
    ├── travelos-archive/SKILL.md       # /archive-screenshot
    └── travelos-viz/SKILL.md           # /viz-trip
```

### 2.3 模板：从 8 个收敛到 3 个，且大幅瘦身

hermes 的 `active_trip_template` 有 ~70 行、9 个治理段（P0/P1/P2、决策日志、下一轮推进…）。给"记一下今天"盖这个章 = 一张几乎全空的 70 行骨架 = 仪式 = hermes 烂掉的家具。**只留真正需要的层**：

**`Templates/trip.md`（~15 行）**
```markdown
---
dest: <城市/区域>
dates: <YYYY-MM-DD ~ YYYY-MM-DD 或留空>
companions: [<姓名…> 或 独自]
budget: <金额或待定>
tags: []
---
# <目的地> — <时间段>

## 稳定框架
<不太会变：日期窗、目的地、硬约束>

## 已锁定事项
<每条：内容 / 证据链接 / 是否已支付 / 是否可改>

## 开放变量
<还没定的：路线、餐厅、某天去哪>

## 材料归档
<指向 Assets/Evidence/Viz 的链接>
```
> `日程草案`、`实际执行记录`、`复盘/感受` 等都是**可选**段，需要时 agent 现加（completed trip 那种很长的逐日叙事就是这样长出来的，不预先塞进模板）。生命周期靠文件夹，frontmatter **不放 state**（避免双真相源漂移）。

**`Templates/place.md`**：合并 Visited/Wishlist（去没去=文件夹位置）。frontmatter 带 `name / city / geo: [lat,lon] / tags`，正文是体验/评价/复用建议。

**`Templates/note.md`**：合并 evidence / research / route，用一行 `type:` 区分。

### 2.4 markdown 是真理；**不建常驻索引**

继续用 markdown 当数据库，**不引入 SQLite，也不建 `_index.json` 常驻索引**。
原设计想加一个 `cli reindex` 生成的索引，但评审指出：要填 geo/dates 它必须**解析自由格式 md**，那个 parser 本身就是 schema 耦合——卡片措辞一漂移就静默给错值，**就是 hermes 索引烂掉的同一个病**，只是换了名字。

**唯一的"结构化"让步：卡片头部的极简 YAML frontmatter**（就 2.3 里那几个字段）。可视化要 geo、要 dates 时，python 在**渲染那一刻**读 frontmatter 进一个内存 dict，**用完即弃、从不落盘当真理**。冲突永远以正文/文件夹为准。这是"最小的 schema"，不是"schema 机器"。

抓取去重：靠 `Captures/<postid>/` 目录是否存在 + 卡片里是否已链过该 url，不需要索引表。

### 2.5 为什么"加历史 trip"和"记今天 trip"都零仪式

- **加历史**：`/trip-add 2019-10 川西 --completed` → 从 `trip.md` 模板 stamp 一个目录，frontmatter 填俩字段即可，正文随便写两句。"先收进去，再慢慢结构化。"
- **记今天**：一句"记一下今天去了 XX" → agent 建目录、把今天的截图丢进 `Assets/`（懒创建），Evidence 之后补。**零强制字段**。
- **反向操作**：把 Candidate 提为 Active = `mv` 一个目录。生命周期=文件夹位置，没有迁移脚本、没有状态校验门。唯一的轻不变量：`/trip-status` 发现 `Active/` 下超过 1 个目录就提醒一句。

---

## 3. Python 胶水层（小而美，零 LLM）

一个 `travelos/cli.py`（argparse，**≤8 子命令**），每个能力一个小模块。读=JSON 输出，写=stdin JSON（沿用 AStockOS 约定）。

| 模块 | 子命令 | 机械职责（绝无 LLM、且**绝不驱动浏览器**，见第 4 节） |
|---|---|---|
| `capture.py` | `cli capture` | 把 agent **已经抓到并通过 stdin 交进来的** note JSON / 图片 url 列表落盘到 `Captures/<id>/`：写 `raw.json`、下载**全部**图片到 `img_*.jpg`。纯落盘 + 下载，零语义、零浏览器。 |
| `htmlclean.py` | `cli clean` | html/raw → clean text，产出 `content.md`（stdlib `html.parser` + 轻正则）。 |
| `archive.py` | `cli archive-shot` | 截图归档：原图→当前 trip 的 `Assets/`（懒创建），返回相对链接给 agent 回填 Trip.md。`--kind flight/hotel/chat/route/guide`。 |
| `viz.py` | `cli viz` | 读卡片 frontmatter / Evidence 里**已结构化**的字段，用模板生成**单个 html** 到 trip 的 `Viz/`。见第 5 节。 |
| `lint.py` | `cli lint` | **唯一护栏**：~15 行 grep，扫 `travelos/` 禁止 `import (openai\|anthropic\|litellm\|dashscope\|zhipuai\|…)` 和 `.messages.create` / `.chat.completions`。 |
| `exif.py` | （phase 3 才加） | EXIF 扫描/回填。现在**不写空壳**，留到 phase 3。 |

> 所有"如何归纳/如何写卡/抓取纪律"都在 `SKILL.md` / `AGENTS.md` 里，**不进 python**。

---

## 4. 能力一 — 小红书/抖音原文抓取（headline feature）

### 4.1 浏览器机制：agent 驱动，python 永不碰浏览器

本机已有一套生产可用的"驱动真实登录浏览器"栈（三个兄弟项目在用，现在就活着）。**采用 AStockOS 的 Pattern B = agent 驱动**（AStockOS `signals/adapters/douyin.py` 明文写着："Social scraping is AGENT-driven, NOT a Python adapter; Python must not orchestrate browsing/logins/anti-bot — rule #8"）。这同时**化解了原设计自相矛盾**（"agent 驱动"vs"python 照搬 browser_session.py 来驱动"不可能同时成立），也**消灭了 session 交接 bug**（python 根本不连 :10086/:18060）。

**双 collector 路由：**

| 平台 | 机制 | 端点 | 真实登录？ |
|---|---|---|---|
| **小红书** | **多路径**：首选 `webbridge-mcp`/`kimi-webbridge`（你日常 Chrome 的真实登录）；反爬/EOF 时降级 `xiaohongshu-mcp`（go-rod 独立 Chrome，QR 持久化 XHS 会话，`127.0.0.1:18060/mcp`，调 `search_feeds`/`get_feed_detail(xsec_token)` 拿结构化 note JSON） | 主 Chrome :10086 / mcp :18060 | 是。主 Chrome 用你日常登录面；mcp 兜底是单独 QR 会话（cookie 独立、会过期）。路径与节奏见 `xiaohongshu_search_playbook.md`。 |
| **抖音 / X / 一般网页** | `kimi-webbridge`（守护进程 + Chrome 扩展，**跑在你真实的 Chrome 里**） | `127.0.0.1:10086` | 是，**就是你日常 Chrome 的真实登录**。agent 用 `navigate/snapshot/evaluate/click/screenshot`。 |

**不用 chrome-devtools / playwright MCP**：二者默认起**全新隔离 Chrome（无任何登录）**，对 XHS/抖音风控指纹弱。**也不自建 mitmproxy/CDP/9222 抓包器**——三个参考项目都没走这条，rule #8 也禁止 python 编排登录/反爬。

**诚实地说清"真实登录"**：抖音/X/网页 + 小红书**首选**都走 webbridge-mcp/kimi-webbridge = 真的是你本人 Chrome 的登录态；小红书反爬/EOF 时降级 xiaohongshu-mcp = 一个**单独 QR 扫一次**种下的 XHS 会话（cookie 独立、会过期）。都能拿全文，机制不同。

### 4.2 复用的到底是什么（诚实版）

不是照搬 python 抓取脚本（那会让 python 驱动浏览器，违背原则一）。复用的是：
1. **`xiaohongshu-mcp` 服务本身**（在 `.mcp.json` 加一条 http 入口即可）。
2. **反爬"铁则"播放本**——写进 `AGENTS.md` / SKILL 给 **agent** 遵守，不写进 python：站内搜索拿 `xsec_token`、点卡片别直接 navi `/explore/{id}`、每步等 2-3s、单平台 ≤10 次访问、同平台串行、命中风控就**停下来降级到封面/截图 OCR、绝不暴力重试**。
3. **materials-package 边界**（SocialExtractPipeline 的 `materials.md`→LLM→report 那条缝）：python 产出"材料包"（raw.json + content.md + 图片路径），agent 读包做语义、写卡。

### 4.3 标准抓取循环

```
agent 选目标、驱动浏览器（xiaohongshu-mcp 工具 / webbridge-mcp 工具）
        ↓ 拿到结构化 note JSON 或 a11y snapshot 文本 + 全部图链
agent 把抓到的数据 stdin 交给 → cli capture  → 落 Captures/<id>/{raw.json,img_*.jpg}
                              → cli clean    → content.md
        ↓ python 产出材料包（零语义、零浏览器）
agent 读材料包；图文 note 要 **逐张** 跑 vision MCP（zai analyze_image）读轮播图
        ↓ agent 做语义：去重纠错、判相关、抽要点
agent 写卡：落成 Place / Route / Research / Evidence 卡（直接写进对应 trip 或 Places）
```

> **关键修正（评审）：小红书图文 note 的实质内容常常烤在多张轮播图里，正文很短。** 所以必须从 `get_feed_detail` 取**全部**图链、`cli capture` 全下载、agent **逐张** vision 读，再并进 `content.md`。"只读封面 OCR"是**降级路径**，不是默认。

### 4.4 两个真实用例

**A：把这条"都安包车"小红书抽进当前 trip**
1. `/extract-xhs <url 或 "都安包车那条">`，指明"进当前 trip"。
2. agent `xiaohongshu-mcp.get_feed_detail` 取 note JSON + 全部图链 → `cli capture` 落 `Captures/...`；`cli clean` 出 `content.md`；agent 逐张 `analyze_image` 读图（联系方式常在图里）。
3. agent 判断="包车师傅联系方式 + 路线"，写两份产物：`Trips/Active/2026-06_河池都安/Evidence/2026-06-28_都安包车师傅.md`（结构化，含来源 url、`paid?`/`changeable?`）+ 在 `Trip.md` 的"已锁定事项/开放变量"加一行链过去。
4. 封面/关键图 promote 进该 trip 的 `Assets/`；散图留在 `Captures/`。

**B：搜"荔波攻略"建一张 Destination_Research 卡**
1. `/research-dest 荔波`。
2. agent `xiaohongshu-mcp.search_feeds(荔波攻略)`（抖音补充走 kimi-webbridge），守 ≤10 访问、串行、2-3s。
3. 命中的 N 条逐条 `cli capture` + `cli clean`。
4. agent 读 N 个材料包，归纳成 `Research/Destination_Research/2026-06_河池荔波/libo_overview.md`：天窗/景点清单、博主同款餐厅、路线雏形、**来源索引表**、**needs-review 清单**（命中/受限/待审计数，沿用 SocialSearch 报告口径）。
5. 值得复用的（餐厅/路线）spin-off 成 `Places/Wishlist/*.md`、`Routes/*.md`，互相链接。原始 html 附在研究目录留底。

### 4.5 登录健康 & 风控现实（评审补的缺口）

- 本机有一条已知记忆 `xhs-webbridge-account-drift.md`：**账号会漂移/过期**。所以 AGENTS.md 要求抓取前先做轻量自检：`xiaohongshu-mcp` 的 login-status；kimi-webbridge `GET /status`（守护进程是否在、扩展版本是否漂移）。失效就**提示用户重新扫码/更新扩展**，不硬失败。
- XHS 服务端风控会挡裸 `/explore/{id}`、部分内容强制"打开 App"。**预期会有一部分 `restricted/needs_review`**，不奢望 100% 全文——这正是优先用 `get_feed_detail` 结构化路的原因。
- kimi-webbridge 是 Kimi 出的外部二进制+扩展，**不是我们维护的**；扩展/守护进程版本漂移是主要外部故障源。`webbridge-mcp` 代理对"守护进程没起/扩展没连"返回结构化错误（`proxy.go`），agent 容错——`travelos/` python 不碰这些进程。

### 4.6 基建增补（2026-07-03）：webbridge-mcp 子 agent 可达性

原设计里抖音/X 走 **kimi-webbridge 技能 + `curl :10086`**。这在**多 agent 编排**下有一个硬缺口：**只有 `mcp__*` 工具会传播到 spawned 子 agent**，技能（prose）和 `curl` 都传不进去——所以子 agent 抓不了抖音/X，`/research-dest` 之类的并行扇出对这两个平台静默失效。用户明确要并行抓抖音/X，且定了原则"**业务逻辑做轻，但基建逻辑不能省，否则功能无法有效实现**"。

**决定**：从 AStockOS 移植 `webbridge-mcp`——一个把 kimi-webbridge daemon(:10086) 包成**代理 MCP server**(:18061) 的 Go 二进制（~600 行，gin + 官方 MCP go-sdk，1:1 透传 14 个 action + status），落在 `tools/social_mcp/`，由 `social_mcp_daemon.sh` 管理。注册进 `.mcp.json` 后，workflow 子 agent 自动获得 `mcp__webbridge-mcp__*`，抖音/X 遂可跨平台并行（同平台仍串行，反爬铁则 #2）。

**与铁律 #1 的关系（重要，别误读成违规）**：铁律说的是 **`travelos/` 这层 python 胶水**不碰浏览器、不连 daemon、不做推理——这条**仍然成立**：webbridge-mcp 是**独立的 Go 进程**，不是 python，`cli lint` 只扫 `travelos/`、碰不到它；它只做**传输代理**（把 MCP 调用透传给 :10086），**零语义、零反爬编排**，浏览决策仍全在 agent。所以这是"**基建层**"（`tools/social_mcp/`），与"**胶水层**"（`travelos/`）分开——§10 里"不让 python 驱动浏览器"针对胶水层，本增补不违背它。落库 collector 仍 `kimi-webbridge`（webbridge-mcp 只是传输壳）。这是对§1 原则二「保持轻」的一次**有原则的例外**：业务逻辑继续轻，但让 headline feature 在并行编排下真能跑的这一小块基建，不省。

---

## 5. 能力二 — 可视化

**画什么**（agent 针对当前 trip 决定）：天窗/景点**地图**（leaflet 点位 + 包车路线连线）、逐日**时间线**、**预算**分解（交通/住宿/餐饮/包车）、跨 trip 的**已访地点地图**（汇总 `Places/Visited` 的 geo）。

**怎么做**（文件式、轻量）：`cli viz --trip <dir> --type map|timeline|budget` 由 `viz.py` 用 **leaflet + Jinja 模板**生成**单个 html** 到 `Viz/`，双击打开。数据来源是卡片 frontmatter / Evidence 里**已由 agent 填好**的 geo/日程/金额——python 只读取渲染，**不解析自然语言、不判断**。缺坐标时 agent 先用浏览器/地图查到坐标写回 frontmatter，再 `cli viz`。

> **诚实声明（评审）**：leaflet 的 js/css 和地图瓦片默认走 CDN/瓦片服务器，所以严格说**不是离线自包含**——首版接受"单 html，看地图需要联网"；若以后要做离线旅行档案，再内联 js/css + 打包离线瓦片。产物进 git。不起 server、不搞前端工程。

---

## 6. 能力三 — 照片 GPS 回填（🅿️ 长期搁置，暂不做）

> **状态（2026-06-28 决定）**：这是一件很长期的事，**暂时不做**。以下设计仅作留缝保留，将来真要做再启；现在不写任何 `exif.py` 代码、不加 cli 子命令。

**届时**才加 `exif.py`（连空壳都不提前写——空 `NotImplementedError` 也是要维护的仪式）。机械设计（python 全程不判断位置）：

1. `cli exif-scan --album <dir> [--trip <dir>]` → 读每张照片 EXIF，输出 `[{path, datetime_original, has_gps}]`，列出缺 GPS 的。
2. **agent 推断位置**（判断归 agent）：结合该 trip 的日期/行程/已访地点 + 照片时间戳 + 必要时 `analyze_image` 看画面，给每张 `(lat, lon)` + 置信度。
3. `cli exif-write --map gps.json` → python 写回 GPS（先备份原图）。
> **技术承诺（评审）**：iPhone 相册默认 **HEIC**，piexif 写 HEIC GPS 不可靠——**用 `exiftool`**（JPEG 才退回 piexif）。时间戳→trip 当天的匹配要**带时区**，用 trip 的日期范围对齐。

---

## 7. 用户交互界面（"你以后可以直接这样说"）

claude-code skills / slash-commands（~8 个），背后都是 agent 编排 + cli 机械执行；**自然语言优先**，不记命令也行。

- `/trip-add <YYYY-MM 目的地> [--candidate|--active|--completed]` — 零仪式建 trip。"记一下今天去了 XX""补个 2019 的历史旅行"都走这条。
- `/extract-xhs <url|描述>` — 抓单条小红书原文 → 结构化成卡。
- `/extract-douyin <url|描述>` — 同上，走 kimi-webbridge；视频口播可选 whisper.cpp 本地转写（本地 subprocess，非 LLM）。
- `/research-dest <目的地>` — 搜小红书/抖音建 Destination_Research 卡（用例 B）。
- `/archive-screenshot <图|"剪贴板这张">` — 截图归档进当前 trip + 提 Evidence + 回填 Trip.md。
- `/viz-trip [--type map|timeline|budget]` — 生成可视化 html。
- `/add-place <名字>`、`/add-route <名字>` — 建地点/路线卡（常是 extract 的下游）。
- `/trip-status` — 读 Active/Trip.md，汇报已锁定/开放变量/缺口，并检查 Active 唯一性。
- （phase 3）`/backfill-gps <album>`。

---

## 8. 迁移计划（把 `_hermes_export` 搬进新结构，顺手修旧伤）

源根：`_hermes_export/home/lighthouse/Hermes_LifeOS/TravelOS/`

1. **整目录搬运**：`Trips/Active/2026-06_河池都安/`、`Trips/Completed/2026-05_五一温州宁波/`（含 Trip.md/Evidence/Archive）、`Places/Visited/*`、`Routes/*`、`Models/*`、`Inbox/*`、`Research/Playbooks/*`、`Research/Destination_Research/2026-06_河池荔波/`（含 `libo_wiki.html`）原样搬。
2. **给已搬卡片补极简 frontmatter**：trip 卡补 `dest/dates/companions`，place 卡补 `name/city/geo(若已知)`。只补这几个字段，正文不动。
3. **修 template drift（轻）**：旧模板 `Archive/Legacy_Templates/{planning,confirmed}_trip_template.md` **不进新仓**；`Templates/` 只放新的 3 个。
4. **删长期空 stub**：`Research/Airfare_Watch/`、`Research/Creator_Watchlist/`。
5. **legacy 残留**：`legacy_planning_snapshot.md`、`hechi_duan_itinerary_LEGACY_README.md` 等留各自 `Archive/` 内可回溯，但不在活跃层引用。
6. **索引去手维护**：手维护的 `Trips/INDEX.md`/`Evidence_Index.md` 不再当"真理"（可留作人读目录）；机器读靠 frontmatter。
7. **建工程层**：`AGENTS.md`、`travelos/`、`.agents/skills/`、`README.md`、空 `Captures/`、`git init`。
8. **验收**：`cli lint` 通过（无 LLM import）+ Active 唯一 + 一张 trip 能 `cli viz` 出图。

> 迁移**不做**大规模重写卡片内容——只搬 + 补 frontmatter + 删残留。

---

## 9. AGENTS.md 提纲

- 一句话定位 + 三大本地目标。
- **铁律 #1（唯一硬规则）**：python 纯机械、agent 唯一 reasoner；python 禁 LLM import/seam/prompt 常量、**禁驱动浏览器**；违例由 `cli lint` 拦。
- **目录语义**：生命周期=文件夹位置；Active 互斥；Trip.md 4 层；frontmatter 只放 geo/dates 等机器读字段，**不放 state**；markdown 是真理。
- **抓取路由 + 铁则**：XHS/抖音/X/网页**首选** webbridge-mcp(:18061，代理 kimi-webbridge :10086；子 agent 可达)真实主 Chrome；XHS 反爬/EOF 时降级 xiaohongshu-mcp(:18060)。不用 chrome-devtools/playwright 做登录态。站内搜索拿 xsec_token、点卡不直 navi、2-3s、≤10 访问、同平台串行（XHS search_feeds 后须先串行取完 detail 再并行其它平台）、命中风控即停降级、绝不暴力重试。图文 note **逐张 vision 读**。抓前查登录健康，失效提示用户。
- **标准抓取循环**：agent 浏览 → `cli capture/clean` 落 Captures → agent 读包写卡。
- **cli 子命令清单**（读=JSON out，写=stdin JSON）。
- **零仪式原则**：加历史/今日 trip 的入口；首版不必完整。
- **可视化约定**：数据先进 frontmatter，`cli viz` 只渲染；地图需联网。
- **依赖容错**：kimi-webbridge/xiaohongshu-mcp 是外部进程，可能没起/版本漂移，结构化报错、别硬失败。
- 进度披露：L0 README → L1 AGENTS.md → L2 各 SKILL/Playbook，不互相重复。

---

## 10. 明确不做的事（anti-over-engineering ledger）

刻意跳过的 AStockOS 重型机器：

| 跳过 | 理由 |
|---|---|
| 合约层（24 JSON schema + negotiator） | 单用户、无版本协商；需要时就地校验 JSON 形状。 |
| 声明式注册表 / 装配 / DI | 适配器就几个，直接 import。 |
| SQLite + schema.sql + 20 migrations | md 当库，greenfield 直接改文件。 |
| 常驻 `_index.json` + reindex 模块 | 解析自由 md = hermes 索引漂移的同一个病；改用 frontmatter + 渲染时临时读。 |
| 15 个 lint / wash | 只留 1 个 ~15 行 grep（禁 python 调 LLM）。 |
| 双正交防腐分类（T0–T3 × A–E） | solo 工具上两套分类是教条过度工程。 |
| 生命周期治理 / MDR / methodology_lifecycle | 一个 AGENTS.md + 几个 SKILL 足够。 |
| 三 runtime 中立（.codex/.opencode + symlink farm） | 本地只面向 claude-code。 |
| 股票域机器（force 分解、verify CI、credibility cap、chain-state） | 与旅行无关。 |
| 向量库 / 嵌入检索 | ~50 文件，grep 足矣。 |
| python 驱动浏览器 / browser_session.py 抓取脚本 | 违背 rule #8；agent 驱动 + xiaohongshu-mcp 更稳更一致。（注：后加的 `webbridge-mcp` 是**独立 Go 传输代理**、非 python、非胶水层，只透传不编排——见 §4.6，不违背本条。） |
| map-reduce 多 driver 全家桶 | 默认交互式逐条；"一次 20+条"成常态再引入单骨架。 |
| 云备份（Tencent COS） | 与"本地优先"冲突。 |

---

## 11. 分阶段构建顺序

**Phase 0 — 脚手架 + 迁移（先能跑、能记 trip）**
- 建 `AGENTS.md` / `README.md` / `travelos/cli.py` 骨架 + `lint.py`(`lint`)；`git init`。
- 执行第 8 节迁移；建 3 个模板、空 `Captures/`。
- 落 `/trip-add`、`/trip-status` 两个 skill —— 此时"加历史/今日 trip"已可用。
- 验收：`cli lint` 过、Active 唯一。

**Phase 1 — 抓取（headline）**
- `.mcp.json` 接 `xiaohongshu-mcp`；确认 kimi-webbridge 守护进程在；抓取铁则进 AGENTS.md。
- `capture.py` + `htmlclean.py` + `archive.py`；skills：`/extract-xhs`、`/extract-douyin`、`/research-dest`、`/archive-screenshot`、`/add-place`、`/add-route`。跑通用例 A、B。
- （可选）抖音视频口播 whisper.cpp 转写。
- （可选末尾）批量需求出现再引入 `social_distill.py` 那种 map-reduce 单骨架。

**Phase 2 — 可视化**
- `viz.py`（leaflet + Jinja）；`/viz-trip`（map/timeline/budget）。约定 geo/日程/预算先进 frontmatter 再渲染。

**Phase 3 — 照片 GPS 回填（🅿️ 长期搁置，暂不做）**
- 设计留缝见第 6 节；现阶段不实现 `exif.py` / `/backfill-gps`，将来再启。

---

*最小可行、markdown 为库、claude 为脑、python 为机械胶水。当前落地 Phase 0–2；照片 GPS 回填长期搁置。*
