# 私有社媒访问手册 / Social Access Playbook（防风控裁决 + 架构依赖）

> 操作层协议。私有社媒（小红书 / X / 抖音）访问连**真实登录浏览器**，最贵的事故不是软件 bug，是**账号被封**。
> 本手册固化「用哪个控制面、为什么、怎么不被封」。**搜索执行技巧 + 渐进式风控纪律**见
> `xiaohongshu_search_playbook.md` 与 `source_health_and_degradation.md`；**公网检索**走
> `web_search_provider_playbook.md`。经验源自 AStockOS 多轮真实采集复盘 + 安全审计，非推断。
>
> **两条第一性原则**：① 抓取 100% 由 agent 用浏览器/MCP 完成，**Python 永不抓社媒/网页/调反爬**，只做
> collector 门禁 + sidecar 回放；② 易变原文先落**可重放 intake**(`ros capture` → sources.db)，凝练只读回放，
> 绝不直接抓——抓取与消费物理隔离，是这套经验长期不腐化的根基。

## 一、控制面隔离矩阵（用错控制面 = 读到错账号 = 整批作废）

ResearchOS 当前的社媒/浏览器工具面：

| 控制面 | 命名空间 | 连接的 Chrome / 登录态 | 承载 | 传播到子 agent? | 收尾清理 |
|--------|----------|------------------------|------|-----------------|----------|
| **xiaohongshu-mcp** (:18060) | `mcp__xiaohongshu-mcp__*` / `ros xhs` | 独立 profile = 用户小红书账号（本地 `cookies.json`） | **仅**小红书搜索 `search_feeds` + 详情 `get_feed_detail` | ✅ 是 MCP，传播 | `pkill -f 'rod/user-data'`（清 rod 孤儿） |
| **webbridge-mcp** (:18061) | `mcp__webbridge-mcp__*` | 代理 Kimi WebBridge → 用户**真实主 Chrome** 真实登录 session | X（搜索/读帖）· 抖音（仅显式）· 需登录态的公网页面 | ✅ **是 MCP，传播**（见 §二） | `close_session`（关本任务 tab 组） |
| **kimi-webbridge** (skill) | `kimi-webbridge` **skill** | 同 webbridge-mcp（同一 :10086 / 同一真实主 Chrome） | 同 webbridge-mcp，但**仅主循环**可用 | ❌ skill 不传播——是 webbridge-mcp 的主循环等价物 | skill 内 `close_session` |
| **chrome-devtools-mcp** | `mcp__chrome-devtools__*` | **独立 throwaway profile**，与用户无关 | 仅**无需登录**的公开页（性能/UI 测试） | ✅ 是 MCP | 独立，互不干扰 |

> ⚠️ **铁律**：任何**登录态**社媒页面**严禁**用 `chrome-devtools-mcp` 读——它是**独立隔离 profile**，
> 与用户日常 Chrome 是两个浏览器，读到的很可能是**未登录/错误账号**，整批作废（见 §四·2 换号陷阱）。
> 登录态读取只走 kimi-webbridge（真实主 Chrome）或 xiaohongshu-mcp（用户小红书账号）。

### 派单矩阵（注意账号纪律）

| 平台 | 搜索 | 帖子详情 | 入口 / 要点 |
|------|------|----------|-------------|
| **小红书** | `xiaohongshu-mcp` | `xiaohongshu-mcp` | `search_feeds(keyword, filters?)`；**禁** kimi-webbridge/webbridge-mcp/浏览器（门禁硬拒） |
| **X / Twitter** | `webbridge-mcp`（子 agent 可达）或 `kimi-webbridge` skill（主循环） | 同 | `https://x.com/search?q=<urlenc>&src=typed_query&f=live`；X **无独立 x-mcp**，走真实主 Chrome |
| **抖音** | `webbridge-mcp` 或 `kimi-webbridge` skill | 同 | `https://www.douyin.com/search/<urlenc>`；**仅用户显式要求时**，不主动搜 |

- **优先级**：小红书 + X 优先；**抖音仅显式**。
- **collector 落库值 = 实际用的那个传输**：小红书=`xiaohongshu-mcp`；X/抖音= `webbridge-mcp`（子 agent 或
  主循环经 MCP）**或** `kimi-webbridge`（主循环经 skill）——两者打同一个真实主 Chrome，门禁都放行。
  `ros capture` 门禁(`ros/search/capabilities.py`)硬校验、`ros lint`（含 `webbridge_mcp_registry` gate）
  复审——**约束塞进可绕过的 prose = 没有约束**。

## 二、为什么是 MCP，不是 skill / curl（子 agent 可达性 — ultracode 下尤其关键）

**只有 `mcp__*` 工具会传播到 spawned 子 agent。** skill 是建议性 prose，`curl`/shell 是本地调用——**两者都
不进**子 agent 的 tool inventory。这条决定了在 ResearchOS 多 agent 编排（workflow / Agent 子 agent）里谁能抓什么：

- **小红书**：`xiaohongshu-mcp` 是 MCP → 子 agent **能**调 `search_feeds`/`get_feed_detail`。✅ 可下放到子 agent。
- **X / 抖音 / 需登录态的公网读取**：现在有两条等价传输打同一个真实主 Chrome——
  **`webbridge-mcp`（:18061，MCP）→ 子 agent 能调 `mcp__webbridge-mcp__*`**（✅ 已可下放到子 agent 扇出）；
  **`kimi-webbridge`（skill）→ 只有主循环能调**（子 agent 调不到）。二者代理的是同一个 Kimi WebBridge
  daemon（:10086）、同一份真实登录 Chrome，只是可达面不同。
  - workflow 子 agent 直接抓 X/抖音：用 `mcp__webbridge-mcp__navigate`+`snapshot`（每个子 agent 取任务级
    `session`，跨调用复用）。**不再被迫**「主抓→子凝练」。
  - 「主循环抓 → `ros capture` 落 intake → 子 agent 读回放凝练」仍是**推荐纪律**：抓取与消费物理隔离、可重放，
    是这套经验不腐化的根基（见开头第一性原则②）。子 agent 直抓适合「扇出对同一 query 多路交叉」，落库仍走 intake。
- **公网搜索**：zhipu MCP（web-search-prime / web-reader）+ runtime WebSearch/WebFetch 都对子 agent 可用；
  读取链 Tier-3 的浏览器兜底现在也子 agent 可达（`webbridge-mcp`），主循环则可用 `kimi-webbridge` skill
  （见 `web_search_provider_playbook.md` §一）。

> **可移植教训（已落地）**：要让「多 agent 编排 + 浏览器桥接」成立，浏览器访问必须做成 **MCP server**，不能停在
> skill。**2026-07-03 参考 AStockOS 已在 ResearchOS 建成 `webbridge-mcp`**（Go 代理 :10086 → :18061，
> `tools/social_mcp/webbridge_mcp/`，15 工具全暴露），登记进 `.mcp.json`，由 `ros lint` 的
> `webbridge_mcp_registry` gate 守护（含皇冠珠宝不变量：xiaohongshu 恒禁 webbridge-mcp）。至此 X/抖音 抓取
> **不再受限于主循环**，capability matrix 补全。`kimi-webbridge` skill 保留为主循环等价物 + 降级路径。
> `webbridge-mcp` 是**无状态代理**：只 proxy :10086 + health-check，从不 start/stop 那个 daemon
> （它归 Kimi App）；默认只 bind loopback :18061（re-expose 真实浏览器，绝不 0.0.0.0）。进程管理见
> `tools/social_mcp/social_mcp_daemon.sh`，端口共享约定见 `tools/social_mcp/README.md`。

## 三、统一存活校验（检索前必用「正确方式」，别裸 curl 看状态码）

MCP/daemon 用专用传输层，对裸 GET 返非 200 是**正常**的。判活方式见
`source_health_and_degradation.md` §一。要点：
- 小红书 `xiaohongshu-mcp` (:18060)：`ros xhs status`（MCP 握手 + `check_login_status`）；裸 curl **405 = 活着**。
- 真实主 Chrome 桥：子 agent / 主循环用 `mcp__webbridge-mcp__status`（它 health-check 底层 :10086，
  `extension_connected=false` 即便 daemon 在跑命令也会失败）；主循环用 skill 时 `list_tabs` 返回 `{"ok":true}`
  = daemon 活。再 `navigate`+`snapshot` 看目标站登录态。webbridge-mcp 进程可 `tools/social_mcp/social_mcp_daemon.sh
  health-check`。掉线只提示用户 `~/.kimi-webbridge/bin/kimi-webbridge start`，**别替用户点登录、别代跑 :10086**。
- **绝不**为「绕过」死信源违反铁律（如小红书回退 browser / kimi-webbridge / webbridge-mcp）。

## 四、防风控裁决（私有社媒访问的核心资产——每条都是可移植第一性原则）

### 1. ★ twscrape / 独立 x-mcp 被否决：软件干净 ≠ 账号安全
X 没有**专用** x-mcp（`webbridge-mcp` 是通用真实浏览器代理，非 X 专用 API 客户端）。两条更快的自动化路径都
评估过、都否决：**独立 Chrome profile(rod)** 被 X 反爬指纹识别、根本登录不了；**twscrape**(cookie 直连 X 内部
API)代码审计干净、无 RCE，但**账号层不可控**——同机/同住宅 IP/同设备指纹上「小号跑 twscrape + 主号跑浏览器」
是**假隔离**，X 按 IP+指纹聚类账号，烧小号会牵连不可替代的主号。**裁决**：X 走真实主 Chrome——`webbridge-mcp`
（子 agent 可达）或 `kimi-webbridge` skill（主循环），真 session、真住宅 IP，逐请求检测风险严格低于任何 API
直连。**可移植教训**：把「软件安全」与「账号封禁风险」分开评估——代码审计干净的库照样能让你号被封。

### 2. 独立 profile = 静默换号陷阱（整批作废）
`chrome-devtools-mcp` 自启一个全新 Chrome（`--user-data-dir=~/.cache/chrome-devtools-mcp/…`），登录态与
用户日常 Chrome **完全隔离**——曾用它读小红书，读到的是**被封/未登录账号**而非用户主账号，agent 差点误判成
「Chrome 没登录」。
- **判别器**：`ps aux | grep 'Google Chrome' | grep user-data-dir` —— 路径含 `chrome-devtools-mcp/chrome-profile`
  = 隔离实例；**无显式 `--user-data-dir`** = 用户真实 Chrome。
- **规则**：登录态读取**必须**走 kimi-webbridge / xiaohongshu-mcp；**信任任何一批数据前先核对活动账号身份**
  （小红书详情里确认作者/主页 id == 目标账号）。一次读错号会让整批作废，且极易被误诊成「登录 bug」。

### 3. 无头浏览器被指纹识别、被静默掐断（EOF panic）
`xiaohongshu-mcp` 跑 `-headless` 时小红书反爬**直接掐断连接**（daemon 日志 `panic=EOF` 于 `MustWaitLoad`，
每次 `/mcp` 跑满 30s 返 204）。这是**平台识别无头浏览器**，非 rod/MCP 缺陷。
- **诊断 tell**：`check_login_status`（不触达平台）**秒回**，而 `search_feeds`/`get_feed_detail`（触达平台）
  **必 timeout** = 反爬，不是代码坏了。
- **纪律**：① 一次**受控重启**清损坏 rod 实例并重试（重启后首条通常恢复）；② 仍高频失败 → **不硬刷**，切
  公网/新闻「当日复盘」渠道（不受该平台反爬），写 `degraded_reason:"headless_anti_bot_eof"`。

### 4. 限流/反爬是 STOP 信号：失败必留证，绝不静默丢
限流/被标记是 **STOP** 信号，不是 retry-until-it-works——狂刷正是把软限流升级成硬封的元凶。**退避 + 降级到
别渠道**。每次采集(成功或失败)都写 session + 显式 `degraded_reason`。⚠️ **注意**：ResearchOS 的 `ros capture`
门禁**硬拒空 `items: []`**（`intake.py` 要求 items 非空，与 AStockOS 的允许不同）——降级/被墙时**仍必须落至少
1 条 item**：一张无 URL 的占位/列表卡片，带 `restricted_reason` + `needs_review`（见 §五 与
`source_health_and_degradation.md`），`degraded_reason` 写在 session 层。**绝不**把失败搜索静默丢或悄悄改写成
更软的 `fallback_reason`。

### 5. 账号价值分层隔离
别把所有自动化跑在一个账号下。按账号价值 + 每动作的逐请求 ban 风险分层：把不可替代的**主账号**藏在**唯一
最低风险、用户自有、只读**动作后（如小红书主账号只读自己的收藏）；重复的、像搜索的、更易检测的流量推给隔离
profile 的**一次性子账号**。子号烧了，主号不动。（ResearchOS 当前小红书搜索/详情都走 xiaohongshu-mcp 账号；
若未来引入主账号收藏读取，收藏走 kimi-webbridge 主 Chrome **只读**，搜索/详情仍走 xiaohongshu-mcp。）

### 6. 自动化浏览器孤儿：按 argv/profile 精准回收，别用裸 pkill
无头反爬 EOF 会留下 rod Chrome 孤儿（无窗口不可见，每实例 ~7 进程/数百 MB）。清理**只用 argv-scoped 匹配**：
`pkill -f 'rod/user-data'` —— 只杀 argv 含 `rod/user-data` 的 Chrome，**永不误杀**用户主 Chrome / kimi-webbridge /
chrome-devtools-mcp profile（它们的 user-data-dir 都不含该 token）。**绝不用宽泛 `pkill chrome`**（会连用户真
浏览器一起杀）。杀常驻 MCP daemon 必须 SIGKILL（SIGTERM 等 10s 杀不掉）；别指望库自带 leak 看门狗（它只在
daemon 进程真死时才触发，常驻 daemon 任务结束不死则永不触发）。

### 7. 最低 ban 风险 = 与真人不可区分
只碰**用户自有 surface**（自己的收藏/likes）、只碰**浏览器正常可见**页面；**不调隐藏/逆向 API、不抓他人私密页、
不绕登录/限流**。架构显式选**更慢的真实浏览器路径**而非 API 直连，理由：ResearchOS 真实检索量（几十~上百
query/天）本就落在人速浏览可承受范围，更快的路径只买来更易被检测的足迹与封号敞口。**先确认真实需求是否真的
超出人速**——若没有，别为不需要的吞吐去冒封号风险。

## 五、被墙了：降级而不丢证据（详见 `source_health_and_degradation.md` §三）

列表卡片（标题 + 互动数 + id + xsec_token）是有效 B 类证据：带 `restricted_reason` + `needs_review` 正常
`ros capture`，标正文待补，留下一轮（用户登录态恢复后）待办。**绝不**为补 detail 回退浏览器。同一 facet 可
换信源（小红书被墙 → X/web），不同风控模型通常互不影响。

## 六、抓取后去噪（各平台噪声指纹）

判定原则：**「只要某段文字换个帖子照样成立，它就是噪声」**；实质内容一定与该帖具体论点绑定。工具层结构 marker
（如小红书导航条 `精选 推荐 搜索 关注 朋友 我的 直播`、抖音页脚 `京ICP/©抖音`、成串 `#话题`）可硬编码丢弃；
平台专属**用户内容**噪声不硬编码，留凝练 agent 语义判断。高互动 ≠ 高信号（最高赞常是教程/广告）；高密度
≠ 自动可信（非独立来源堆高印证 = 回声室，置 `echo_chamber_flag`，可信度按多轴判低）。
