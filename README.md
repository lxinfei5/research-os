# ResearchOS

A personal, multi-topic research system. You open a research **topic**, search many sources
(public web + X / 抖音 / 小红书), and the findings are condensed into that topic's own layered
**L0–L3 world knowledge**. Each topic is physically isolated — **N topics = N knowledge files** —
so today's geopolitics thread and tomorrow's trading-methodology thread never bleed into each
other. Originals are retained (link + cached text; video/image transcribed to text first), and each
new search is primed by what the topic already knows, then feeds back to grow it.

**宪法： [AGENTS.md](AGENTS.md)**（`CLAUDE.md`/`GROK.md` symlink 至此）。设计史见 `DESIGN.md`（旧强门控架构）。

## 形态（2026-07-29 弱门控化 + 去 db 化后）

**一切交给大模型。无门禁、无流程编排、无脚本、无数据库。** 知识即 markdown，git 即审计，品味即门禁。

- 一主题一档 `topics/<slug>/knowledge.md` —— L0 世界观 / L1 视角 / L2 印证事实 / L3 单源主张 + 未决问题 + 信源索引 + facet 覆盖。**L0–L3 是 heading 标签，不是 schema。**
- 写入纪律 = `rules/` 地板（`floor-corpus` 三要素 / `floor-evidence` 信源阶梯 / `floor-judgment` 可信度分级），**自觉执行 + 人复核，不阻断不校验不 fail**。
- 无 Python 引擎、无 13 门禁、无触发器、无迁移、无 credibility 表、无审计表。语义判断全由 agent 现算。

> 历史：本项目曾是「强门控引擎」（3 个 sqlite + 13 lint + 5 触发器 + map-reduce 凝练机）。2026-07-29 按 AStockOSV2 的 V1→V2 路径整体改造：只带知识、剥全部机制，知识从 sqlite 迁入 markdown。迁移对账：7 主题 L1/L2/L3 条数与活库逐一相等。

## 研究回路（无 ros 命令）

由 agent 现算，skill 是执行手册（`.agents/skills/`）：

```
研究一个主题   → 读 topics/<slug>/knowledge.md 唤起（L0+L1+未决+facet 覆盖）
检索补缺       → researchos-search / multi-search-engine / researchos-xhs（多路径）
媒体转文本     → researchos-media（whisper 转写 / OCR）
入库 + 凝练    → 按 rules/floor-corpus + 凝练三环契约,agent 读档写 L3→L2→L1→L0
报告 / 再来    → 更新 facet 覆盖与 _index.yaml;reports/world_model.md 为人读视图
旅行攻略       → researchos-travel → topics/<slug>/plan.html（社媒评价优先）
```

详见 `AGENTS.md` §3。

## 布局

`rules/` 地板纪律 · `topics/<slug>/` 每主题世界知识（knowledge.md + sources/ + captures/ + reports/）· `topics/_shared/methods/` 跨主题方法 · `library/sources/<sha256>.json` 全局内容寻址原文库 · `.agents/skills/` 操作手册。

## 取数通道（地板，非 Python 闸）

- **web**：`WebSearch` → `multi-search-engine` → 真 Chrome `webbridge-mcp`（降级链，记 fallback_chain）
- **X / 抖音**：真 Chrome `webbridge-mcp` / `kimi-webbridge`（用户真实登录）
- **小红书**：多路径——主 Chrome 优先，`xiaohongshu-mcp` 兜底（反爬/EOF 时）

细则：`rules/web_search_provider_playbook.md` / `rules/social_access_playbook.md` / `rules/xiaohongshu_search_playbook.md`。MCP servers 见 `.mcp.json`。
