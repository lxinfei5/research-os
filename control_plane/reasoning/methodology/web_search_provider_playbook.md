# 公网检索三层降级手册 / Web Search Provider Playbook

> 操作层协议（检索**公开网页 / 新闻**前必读）。本手册固化「用哪个 provider、额度耗尽怎么逐层降级、
> 每层失败怎么留证」。**社媒**（小红书 / X / 抖音）走另一套（登录态 + 风控），见
> `xiaohongshu_search_playbook.md` 与 `social_access_playbook.md`；被墙/存活校验共性见
> `source_health_and_degradation.md`。本文件只讲公网/新闻。
>
> **铁律**：Python 永不搜索、不抓页面、不摘要、不调外部 LLM。agent 用工具/MCP/skill 检索，归一化后经
> `ros capture` 写回；Python 只做 collector 门禁 + 记账。provider / 搜索引擎**不是新 source**，只写
> `collector` + `raw_tool_status`，不进任何 registry。

## 一、两条降级链(搜索 + 读取)

搜索先拿候选 URL/标题/摘要，再读取正文。两段各有独立的三层降级链，**每层只试一次，成功即停，全部失败
→ 写 degraded capture(绝不静默丢)**。

**搜索链(search mode)** — 找候选 URL：

| Tier | Provider | 工具(Claude Code) | 额度 | `collector` 落库值 |
|------|----------|-------------------|------|-------------------|
| 1 | 智谱 MCP | `mcp__web-search-prime__web_search_prime` | 需 `ZHIPU_API_KEY` | `zhipu` |
| 2 | Runtime 内置 | `WebSearch` | runtime 配额 | `runtime-builtin` |
| 3 | **multi-search-engine** skill | `WebFetch` → 引擎结果页 URL | **免额度** | `multi-search-engine` |

**读取链(fetch mode)** — 搜到候选 URL 后取正文：

| Tier | Provider | 工具(Claude Code) | 何时 | `collector` 落库值 |
|------|----------|-------------------|------|-------------------|
| 1 | 智谱 MCP | `mcp__web-reader__webReader` | 默认 | `web-reader` |
| 2 | Runtime 内置 | `WebFetch` | 智谱 reader 额度耗尽 | `runtime-builtin` |
| 3 | Kimi WebBridge（真实主 Chrome） | 子 agent：`mcp__webbridge-mcp__navigate`+`snapshot`；主循环：`kimi-webbridge` skill | **仅** JS 渲染 / 反爬壳 / 需登录态的页面 | `webbridge-mcp` 或 `kimi-webbridge` |

> `collector` 写**实际产出被捕获条目的那一层**（tier-3 刮到的写 `multi-search-engine`；智谱读到的写
> `web-reader`；浏览器兜底读到的写用的那个传输——`webbridge-mcp`（经 MCP）或 `kimi-webbridge`（经 skill））。
> 完整链路进 `raw_tool_status.fallback_chain`。这些值都在 `web` 源的 `required_search_collector` 白名单内
> （见 `ros/search/source_capabilities.yaml`），门禁放行；写别的值会被 `ros capture` 拒。
>
> **读取链 Tier-3 的边界**：只对**真的需要浏览器**的页面（SPA/动态加载、Cloudflare/验证码反爬壳、需登录态）
> 用真实主 Chrome 桥。其余抓不到就**跳过 Tier-3、给 item 标 `restricted_reason`**，不硬抓。
> ✅ **子 agent 可达性已补齐**：`webbridge-mcp`（:18061，MCP）会传播到 spawned 子 agent，故浏览器兜底读取
> **不再受限于主循环**——workflow 子 agent 可直接 `mcp__webbridge-mcp__navigate`+`snapshot`。`kimi-webbridge`
> 仍是 **skill（不传播）**，作主循环等价物。二者打同一个真实主 Chrome（:10086）。详见
> `social_access_playbook.md` §二。

## 二、失败信号 → 降级判断(agent 逐层判)

| 信号 | 判为 | 行为 |
|------|------|------|
| HTTP 429/402 / "quota exceeded" / "额度不足" | `quota_exhausted` | 降下一层，记 `quota_status` |
| HTTP 5xx / timeout / "service unavailable" | `provider_error` | 降下一层 |
| 0 results(空结果) | `empty_result` | **不是** quota 问题——多半 query 太窄；换 query 重试**当前层 1 次**，仍空才降 |
| 403 / "access denied" | `access_denied` | 降下一层 |
| tool not found / 缺 `ZHIPU_API_KEY` | `tool_unavailable` | **跳过**该层(runtime 不支持/未配置)，直接降下一层 |

**额度记忆(跨请求，不持久化)**：同一 session 内某层确认 `quota_exhausted` 后，后续搜索**可从下一可用层
起**(agent 判断，非机制强制)；**不写盘**——下次会话仍从 Tier 1 起(额度可能已恢复)。

## 三、每次搜索必写 `fallback_chain`(留证形状)

`ros capture` 的 `raw_tool_status` 是自由 JSON，凝练 agent 靠它分辨「真没结果」与「被挡了」。**每次公网
搜索(成功或失败)都要在 `raw_tool_status` 里写完整 `fallback_chain`**。

```json
{
  "query": "乌克兰 停火 谈判 2026",
  "source": "web",
  "collector": "multi-search-engine",
  "capture_kind": "search",
  "result_count": 4,
  "items": [
    {"platform": "web", "source_kind": "search_result", "needs_review": true,
     "url": "https://…", "title": "…", "content": "agent 摘取的要点(未读原文=线索)"}
  ],
  "raw_tool_status": {
    "provider_id": "multi_search_engine", "fetch_tool": "WebFetch", "actual_runtime": "claude_code",
    "fallback_chain": [
      {"tier": 1, "provider": "web-search-prime", "status": "quota_exhausted", "error": "429"},
      {"tier": 2, "provider": "WebSearch", "status": "failed", "error": "0 results for 3 queries"},
      {"tier": 3, "provider": "multi-search-engine", "status": "partial"}
    ],
    "quota_status": {"zhipu_search": "exhausted", "zhipu_reader": "available"},
    "engines_attempted": ["Baidu", "Bing CN", "Sogou", "Toutiao"],
    "engines_succeeded": ["Baidu", "Bing CN"],
    "engines_failed": {"Sogou": "403 anti-bot", "Toutiao": "empty result"}
  }
}
```

| 字段 | 何时写 | 含义 |
|------|--------|------|
| `fallback_chain: [{tier,provider,status,error?}]` | **每次搜索** | 完整降级链，最高层 success 后不试下层。status ∈ {success, partial, quota_exhausted, provider_error, empty_result, failed, tool_unavailable, skipped, all_failed} |
| `quota_status: {zhipu_search, zhipu_reader}` | 搜索/读取后 | 各 provider 感知额度：available / exhausted / unknown |
| `engines_attempted / engines_succeeded / engines_failed` | **仅**用 multi-search-engine 时 | 尝试/成功的引擎名，及失败引擎→原因(对象) |

## 四、线索 vs 原文 · promote 门(与社媒同纪律)

- **搜索摘要 ≠ 已读原文**：搜索结果只有标题+摘要 → **线索**。`source_kind: "search_result"` +
  `needs_review: true`，报告里只作 `clue_only`；读到正文后升 `web_page`/`article`、`capture_kind:"fetch"`
  才可 promote。
- **promote 是显式 URL 门(代码强制)**：无真实 URL 的 item 必带 `restricted_reason`，只留 raw intake，
  `ros promote` 不会提升它(`intake.py` 抛错)。
- `source` 公网只用 `web`(或别名 `web_search`)；`capture_kind` 用 `search`(拿到候选) / `fetch`(读到正文)——
  这两个 kind 才触发 collector 门禁校验。

## 五、全 provider 失败 → degraded capture，绝不静默丢

搜索链三层全失败也要留证：`degraded_reason: "all_search_providers_exhausted"` +
**完整 `fallback_chain` / `engines_attempted` / `engines_failed`**。静默丢会掩盖「你正被限流」，污染下游
覆盖度核算。

> ⚠️ **`ros capture` 拒「静默」空 `items: []`**（无 `degraded_reason` 时拒）——允许
> `items: []` + `degraded_reason` 作为响亮空槽；也可挂一条 url-less placeholder。留证至少二选一：
> **一条 url-less 占位 item** 上：给它 `restricted_reason`（说明为何无 URL）+ `source_kind` + `content` +
> `needs_review`，`degraded_reason` 写在 session 层。无 URL 的 item 经 promote 门天然只留 raw、永不提升，
> 正是「留证但不当证据」。这与 `source_health_and_degradation.md` / `xiaohongshu_search_playbook.md` 的社媒
> 被墙留证同一形状。

响亮空槽（推荐，不必造假 item）：

```json
{
  "query": "乌克兰 停火 谈判 2026", "source": "web", "collector": "multi-search-engine",
  "capture_kind": "search", "result_count": 0,
  "degraded_reason": "all_search_providers_exhausted",
  "items": [],
  "raw_tool_status": {
    "fallback_chain": [
      {"tier": 1, "provider": "web-search-prime", "status": "quota_exhausted", "error": "429"},
      {"tier": 2, "provider": "WebSearch", "status": "failed", "error": "no results"},
      {"tier": 3, "provider": "multi-search-engine", "status": "all_failed"}
    ]
  }
}
```

或挂一条 url-less placeholder（旧形状，仍合法）：

```json
{
  "query": "…", "source": "web", "collector": "multi-search-engine",
  "degraded_reason": "all_search_providers_exhausted",
  "items": [
    {"platform": "web", "source_kind": "search_result", "needs_review": true,
     "restricted_reason": "all_search_providers_exhausted",
     "content": "三层搜索链全失败；留证用，非线索。"}
  ]
}
```

## 六、执行顺序(含降级)

1. **Preflight**：先看本主题已有的新鲜覆盖(`ros topic open` / `ros gaps` / brief 里「recent queries」)。
   已有可解释的原文级材料就**别重搜**，把预算花在稀薄 facet。
2. **Search**：按 §一 搜索链执行，生成少量目标明确的 query，先拿候选 URL/标题/摘要(只作线索)。
3. **Fetch**：按 §一 读取链执行，只对正式要用的候选 URL 取正文。
4. **Capture**：成功与失败都 `ros capture`(带 `fallback_chain`)，`ros condense` 只读回放，不再搜。

## 七、复盘沉淀

每次因 provider 机制(非语义)降级/失败后，除修操作文档，判断是否是可复用研究方法：若是，在该主题 method
lane 加一条 M0/M1(如「某类实时事件，公网搜索优先英文源 + 时间过滤，中文源常滞后」)。操作文档解决「怎么做」，
method lane 解决「怎么判断」。
