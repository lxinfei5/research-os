# 小红书检索手册 / Xiaohongshu Search Playbook

> **硬约束（不可绕过）**：小红书的所有**搜索 + 笔记详情**必须走本地 `xiaohongshu-mcp` 服务，**禁止** kimi-webbridge / 浏览器抓取。capture 网关会在写入前拒绝 `source=xiaohongshu` 且 `collector=kimi-webbridge|browser` 的捕获（见 `ros/search/source_capabilities.yaml`）。

## 检索路径

1. **首选 native MCP 工具**：若运行时已暴露 `xiaohongshu-mcp`，直接调用 `search_feeds` 与笔记 detail 工具。
2. **回退到本地桥**：运行时未暴露该工具时，用 `ros xhs` 命令（`ros/lib/xiaohongshu_mcp_bridge.py`）连本地 `http://localhost:18060/mcp`：
   - `ros xhs status`  —— 检查登录态（`check_login_status`）
   - `ros xhs tools`   —— 列出可用工具
   - `ros xhs call --tool search_feeds --args-json '{"keyword":"..."}'`
   - 端点可用 `ROS_XHS_MCP_URL` 覆盖；默认仅允许 loopback。

## 风控纪律（继承 SocialSearch + `source_health_and_degradation.md`）

小红书风控是**渐进式**的：先返回空结果 → 再报内部错误（EOF）→ 最后才弹扫码墙。等到扫码墙出现时往往
已晚，所以纪律的核心是**墙出现前就克制**，而非墙出现后再停。

- **首次成功后立即克制。** 一次成功的 `search_feeds` 是稀缺资源——拿到结果后先解析、记下高价值条目的
  id + xsec_token，**不要立刻发起第二次同平台搜索**。换关键词重搜往往会返回空（风控前兆）。
- **❌ 反模式（真实踩坑）：search 成功后为了"重新解析结构化输出"重跑 `search_feeds`。** 第一次返回的
  JSON 里**已含每条 feed 的 `xsecToken`**（camelCase），手里已有 token，无需再搜。徒劳重搜会把会话推向
  风控（空→EOF→扫码墙），等调 `get_feed_detail` 时窗口已废、正文 0 条。**正确序列：search 成功一次 →
  从那份 JSON 解析 xsec_token → 立刻调 `get_feed_detail` 取 1–3 篇最高价值笔记正文，绝不重搜。**
- **❌ 并行是 XHS 的死敌（实战教训 2026-07-06）**：曾尝试 search_feeds 成功后**并行**跑 X 搜索
  /navigate/snapshot/evaluate + 查 xhs tools schema，十几秒后才调 get_feed_detail，结果吃风控墙
  （"Page Isn't Available Right Now" + 扫码）。xhs-mcp 的 go-rod 会话窗口**有时效**（约几秒到十几秒），
  search 后窗口"热"，拖久了窗口"废"，detail 必吃墙。**铁律：search_feeds 成功后，立即串行
  get_feed_detail（5–8s 间隔），期间不得并行任何 X/web/其他 MCP 操作。** X 搜索放到 XHS detail
  完全结束之后另起一段。违反此纪律 = 丢失一次有效 search + 触发系统级 cooldown（30 分钟）。
- **详情配额优先给最高价值条目。** `get_feed_detail` 比 `search_feeds` 更容易触发风控。一批结果里**只对
  1–3 条最高互动 / 最高信息密度的取 detail**，串行 + 间隔 5–8s，绝不批量。
- **空结果 ≠ 没数据，是预警。** 第二次同关键词搜索返回空 / 明显少于首次 → **不要换词硬试**，降低频次
  或转其它信源（X/抖音→web）补这块 facet。
- **绝不**导航裸 `/explore/{noteId}`（触发「请打开 App 扫码查看」风控墙）——一律经 `search_feeds` 结果
  里的 `xsec_token` 走 MCP detail。
- 同平台**串行**，动作间等待 5–8s（详情） / 2–5s（搜索）；单次任务 ≤10 次页面访问或 48h 回看。
- 遇**任何**「内部错误 / EOF / 不可访问 / 扫码 / 请打开 App」字样 → **立即 STOP 该信源，不重试**
  （重试只会更早触发墙、作废用户登录会话）。
- **被墙后不丢证据**：已拿到的列表卡片（标题 + 互动数 + id + xsec_token）仍是有价值的 B 类证据，带
  `restricted_reason`（说明详情因风控未取）+ `needs_review` 正常 capture；标正文待补，留作下一轮（用户
  登录态恢复后）待办。**绝不**为补 detail 回退 browser/kimi-webbridge。
- 用后清理 rod Chrome 孤儿：`pkill -f 'rod/user-data'`。
- 用后清理 rod Chrome 孤儿：`pkill -f 'rod/user-data'`。

## 捕获回写

抓到内容后，归一化为 capture payload（`source:"xiaohongshu"`, `collector:"xiaohongshu-mcp"`），图片多的笔记先做 OCR/vision 转文本（Phase 2），再 `ros capture`。无 URL 的列表卡片必须带 `restricted_reason`，留作 raw-only，不会被提升。
