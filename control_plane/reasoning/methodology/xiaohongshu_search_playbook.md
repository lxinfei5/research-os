# 小红书检索手册 / Xiaohongshu Search Playbook

> **硬约束（不可绕过）**：小红书的所有**搜索 + 笔记详情**必须走本地 `xiaohongshu-mcp` 服务，**禁止** kimi-webbridge / 浏览器抓取。capture 网关会在写入前拒绝 `source=xiaohongshu` 且 `collector=kimi-webbridge|browser` 的捕获（见 `ros/search/source_capabilities.yaml`）。

## 检索路径

1. **首选 native MCP 工具**：若运行时已暴露 `xiaohongshu-mcp`，直接调用 `search_feeds` 与笔记 detail 工具。
2. **回退到本地桥**：运行时未暴露该工具时，用 `ros xhs` 命令（`ros/lib/xiaohongshu_mcp_bridge.py`）连本地 `http://localhost:18060/mcp`：
   - `ros xhs status`  —— 检查登录态（`check_login_status`）
   - `ros xhs tools`   —— 列出可用工具
   - `ros xhs call --tool search_feeds --args-json '{"keyword":"..."}'`
   - 端点可用 `ROS_XHS_MCP_URL` 覆盖；默认仅允许 loopback。

## 风控纪律（继承 SocialSearch）

- **绝不**导航裸 `/explore/{noteId}`（触发「请打开 App 扫码查看」风控墙）——一律经 `search_feeds` 结果里的 `xsec_token` 走 MCP detail。
- 同平台**串行**，动作间等待 2–5s；单次任务 ≤10 次页面访问或 48h 回看。
- 遇验证码 / 强制登出 / 扫码墙 → **STOP，不重试**（重试会作废用户登录会话）。
- MCP 不可用时：降级为列表卡片证据 + `restricted_reason`，标 `needs_review`；**绝不**为 detail 回退浏览器。
- 用后清理 rod Chrome 孤儿：`pkill -f 'rod/user-data'`。

## 捕获回写

抓到内容后，归一化为 capture payload（`source:"xiaohongshu"`, `collector:"xiaohongshu-mcp"`），图片多的笔记先做 OCR/vision 转文本（Phase 2），再 `ros capture`。无 URL 的列表卡片必须带 `restricted_reason`，留作 raw-only，不会被提升。
