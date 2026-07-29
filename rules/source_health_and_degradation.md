---
status: canonical
as_of: 2026-07-29
---

# 信源健康校验与风控降级手册 / Source Health & Degradation Playbook

> 操作层协议（operator 执行检索前/中必读）。社媒信源（小红书 MCP、kimi-webbridge/X/抖音）都依赖
> **用户的真实登录会话**——误判它们的存活状态、或在中途触发风控墙，会浪费检索预算甚至作废登录态。
> 本手册把「怎么判断信源真的活着」「怎么避免中途被风控」「被墙了怎么降级而不丢证据」三件事固化下来。

## 一、检索前：必须用「正确的方式」验证信源存活

**永远不要用裸 `curl` + 看状态码来判断 MCP / daemon 是否存活。** 这些服务用专用传输层，对裸 GET
返回非 200 是**正常**的，把"非 200"当成"没运行"是经典误判。

| 信源 | ✅ 正确的存活校验 | ❌ 错误的判断（会误判为"没运行"） |
|------|------------------|----------------------------------|
| 小红书 `xiaohongshu-mcp` (:18060) | XHS MCP 握手 + `check_login_status`（返回 `✅ 已登录` 即活） | 裸 `curl http://localhost:18060/mcp` → **405 Method Not Allowed 是服务活着的证明**（streamable-HTTP 不接受裸 GET）；只有连接拒绝 / 超时才是真没运行 |
| kimi-webbridge (:10086) | `curl …/command -d list_tabs` → `{"ok":true,...}` 即 daemon 活；再 `navigate` 到目标站 `snapshot` 看是否登录态 | 根本不验证就假设"需要用户确认登录态"——daemon 多数时候已在跑 |
| 智谱 web-search-prime / web-reader | 需要 `.env` 的 `ZHIPU_API_KEY`；缺 key 则该信源本轮不可用，**降级到 runtime `WebSearch`/`WebFetch`** | 假设有 key 就直接调，失败后才回头查 |

**校验失败的唯一正确动作**：对 webbridge，`~/.kimi-webbridge/bin/kimi-webbridge start`（no-op if 已起）；
对 XHS MCP，它在用户浏览器里登录，**不要**试图自己拉起——告诉用户 MCP 未登录即可，不要替用户点登录。
**绝不**为了"绕过"死信源而伪造数据或静默丢槽（该槽写 `UNKNOWN`+`degraded_reason`，其余槽照常）。小红书多路径下换到主 Chrome（webbridge-mcp/kimi-webbridge）取详情是合法路径，见 `xiaohongshu_search_playbook.md`。

> ⚠️ **xhs-mcp 反爬 EOF/超时时的重启纪律（Rosetta 陷阱）**：当 `check_login_status` 秒回但
> `search_feeds` 持续超时（headless 反爬 EOF tell，见 `social_access_playbook.md` §四·3），协议允许
> "一次受控重启"——**但 agent 绝不能从 TRAE SOLO RunCommand 自行 fork xhs-mcp binary**。原因：
> TRAE SOLO 进程本身在 Rosetta 2 下运行（`sysctl.proc_translated=1`），fork 出的 xhs-mcp 及其
> Chrome 子进程都继承 translated 属性，导致 Chrome 读不到已有 profile 登录态、xhs-mcp 弹扫码登录
> （看似"换号陷阱"，实为 Rosetta-translated Chrome 的 profile 解析异常）。**正确做法**：STOP 该信源，
> 提示用户在**原生 arm64 Terminal**（非 TRAE SOLO 终端）跑
> `bash tools/social_mcp/social_mcp_daemon.sh restart xiaohongshu-mcp`，等用户确认后再重试。
> `arch -arm64` 前缀也救不了——translated 父进程下 `arch` 无法逆转翻译状态。

## 二、检索中：预防性风控纪律（社媒尤其关键）

社媒风控是**渐进式**的：先返回空结果 → 再报内部错误 → 最后才弹扫码墙。等到扫码墙出现时，**往往已经
晚了**。所以纪律的核心是**在墙出现前就克制**，而不是墙出现后再停。

1. **首次成功后立即克制。** 一次成功的 `search_feeds` / 搜索页 snapshot 是稀缺资源——拿到结果后**先解析、
   记下高价值条目的 id/token，不要立刻发起第二次同平台调用**。把窗口让给"读"而非"反复搜"。

   > **❌ 反模式（真实踩坑）：search 成功一次后，为了"重新解析一遍结构化输出"又把同一个 `search_feeds`
   > 重跑 2–3 次。** 第一次的返回 JSON 里**已经包含每条 feed 的 `xsecToken`**——手里已有 token，根本不需要
   > 再搜。徒劳的重搜把会话从"健康"推到风控（空结果→EOF→扫码墙），等真正去调 `get_feed_detail` 取正文时
   > 窗口已废，正文 0 条。**正确做法：第一次 search 成功 → 立刻从那份 JSON 解析 token → 马上调
   > `get_feed_detail` 取最高价值笔记的正文，绝不重搜。** 「重跑一次 search 拿结构化输出」是伪需求。

2. **详情配额优先给最高价值条目。** detail（笔记详情 / 展开推文）比 search 更容易触发风控。拿到一批
   search 结果后，**只对 1–3 条最高价值（高互动 / 高信息密度）的取 detail**，串行 + 间隔 5–8s，绝不批量。
3. **空结果 ≠ 没数据，是预警。** 第二次同关键词搜索返回空、或明显少于首次，是风控前的典型信号——
   **不要换关键词硬试**，而是降低频次、或转向其它信源（X/抖音→web）补这块。
4. **遇任何"内部错误 / EOF / 不可访问 / 扫码"字样 → 立即 STOP 该信源，不重试。** 重试只会更早触发
   墙、并作废用户登录会话。这是硬纪律，覆盖一切"再试一次说不定能成"的冲动。
5. **同平台串行**；单任务 ≤10 次页面访问 / 48h 回看（继承 SocialSearch）。**跨平台默认可并行，但有一个硬例外
   （并行窗铁律，实战教训 2026-07-06）：** `xiaohongshu-mcp` 的 `search_feeds` 成功后，go-rod 会话窗口只有几秒
   到十几秒的"热"窗口——必须**立即串行**调 `get_feed_detail`（5–8s 间隔）取完 1–3 篇详情，**期间不得并行任何
   X / web / 其它 MCP 操作**；X 搜索放到 XHS detail 完全结束之后另起一段。违反 = 丢失一次有效 search + 触发
   系统级 cooldown（30 分钟）。XHS 专属细节（xsec_token 流、裸 `/explore/{noteId}` 禁令）见
   `xiaohongshu_search_playbook.md`；**本节是跨平台节奏的唯一源**。

## 三、被墙了：降级而不丢证据

风控触发后，**已经拿到的列表卡片 / 首屏证据仍然有价值**——不要因为"详情没抓全"就丢弃整批。降级路径：

1. **列表卡片 = 有效证据**。search 返回的标题 + 互动数（赞/评/藏）+ 作者 + id + xsec_token，本身就是
   可捕获的 B 类证据。按 XHS playbook：带 `restricted_reason`（说明"详情因风控墙未取"）+ `needs_review`，
   标注正文待补，正常 capture。**详情可换主 Chrome 路径再试，但勿对同一笔记短时间狂刷。**
2. **在 capture 里诚实标注降级**。`degraded_reason` 字段写清"何时、因何墙、缺什么"，让凝练 agent 知道
   这是卡片级而非全文证据，据此下调可信度（社媒卡片起点 medium、单卡可压 low；domain 上限单源见
   `credibility_guide.md` §domain 可信度上限）。
3. **换信源补这块 facet，而非死磕。** 小红书被墙后，同一 facet（如"性价比实测"）可转 V2EX / X / web
   补——这些信源的风控模型不同，通常不受影响。记下"小红书详情待补"作为下一轮（用户登录态恢复后）的待办。
4. **用后清理**。XHS MCP 的 rod Chrome 会留孤儿进程：`pkill -f 'rod/user-data'`。webbridge 用完
   `close_session` 清理 tab 组（除非用户要留页）。

## 四、复盘：把踩过的坑沉淀进 method lane

每次因信源机制（非语义）导致检索降级或失败后，除了修操作文档，还要判断**这条教训是否是可复用的
研究方法**：若是，在对应主题的 method lane 加一条 M0/M1 规则（如"社媒额度类实测，卡片级证据可信度上限
为 low，需跨平台 ≥2 源才能升 medium"）。操作文档解决"怎么做"，method lane 解决"这么判断"。
