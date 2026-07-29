---
status: canonical
as_of: 2026-07-29
---

# floor-evidence — 数据与证据地板（取数/分档/升格/降级唯一入口）

> 管「从哪取、怎么分档、取不到怎么响、何时升格」。本文件只立恒真原则 + 指针；细则唯一源在各 playbook。
> 非门禁：靠自觉执行 + 人复核。要防的腐化 = 把取数纪律又写成 Python 校验闸。

## L0 · 本域恒真（一次蒸馏）

证据是知识的唯一来源。每条知识必带 provenance（见 `floor-corpus.md` 三要素）。信源分软硬阶梯；小道多源是一等输入，不是二等公民；取不到要响亮地空（UNKNOWN + degraded_reason），绝不静默留空或编造。检索必走降级链并记下实际走的 collector 与 fallback_chain。反爬/风控靠节奏与节制，不靠 Python 禁令。

## 本域会怎么腐

- **官方洁癖**：只认官方已验证、其余当噪声 → 永远跟不上盘面/舆论。
- **静默留空**：某源取不到就当它不存在 → 覆盖缺口隐形。
- **记忆冒充现拉**：用训练记忆里的价格/财报/事实 → 一律作废，现场重拉。
- **把访问纪律写成 Python 闸**（搜什么源、记不记 fallback 都 lint）→ 门禁复活，砍。

## 信源阶梯 T0–T4（inline 前缀标签，写在 proposition 前）

| 档 | 标签 | 何时用 |
|---|---|---|
| T0 | （无前缀或 `[official]`） | 官方公告/财报/海关/一手披露 → 主锚 |
| T1 | `[industry-monitor]` | 产业监测 + ≥2 家媒体交叉 → 主锚 |
| T2 | `[street-consensus]` | 过升格四闸的多源小道 → 现算工作事实 |
| T3 | `[low-credibility]` / 线索 | 单帖/单号 → 只作线索，不单独驱动结论 |
| T4 | `[echo]` / 证伪 / 噪音 | 同根转发链 → 按 1 条或剔除 |

## 升格四闸（小道 → T2 工作事实，agent 判，非代码）

四条全过才升，缺一则停 T3：① **多源且独立**（≥2 彼此独立账号/渠道，同社群转发=1 源）② **逻辑充实**（有可核对机制链，非无据喊涨）③ **部分外部锚**（至少一处 T0/T1 同向/同量级/同机制旁证）④ **可证伪细节**（带品级/时点/口径，纯形容词不升）。

## 空槽响亮化

凡声明要取的源/通道，结案前必给结果或写明 `UNKNOWN + degraded_reason`（限流/风控/无可用锚）。只扫主帖不读评论/图 = 材料不合格（社媒通用：主帖 + 评论区 + 图三件套）。

## 各源访问细则（唯一源指针）

- **公网 web**：`web_search_provider_playbook.md` —— 三层降级链（WebSearch→multi-search-engine→webbridge 真 Chrome），fallback_chain 记录，降级判定表。
- **社媒 X/抖音/小红书**：`social_access_playbook.md` —— 控制面隔离、子 agent 可达性、反检测裁决。
- **小红书**：`xiaohongshu_search_playbook.md` —— 多路径（主 Chrome 优先，xiaohongshu-mcp 兜底）+ 防风控节奏。
- **信源健康/降级**：`source_health_and_degradation.md` —— 存活校验 + 渐进式风控 + 跨平台节奏。
- **第一手/用户简报（无公网 url）**：`first_party_empirical_playbook.md` —— `researchos://first-party/<hash>` 何时用、怎么判。

## 媒体 → 文本

视频/图先转文本再入库：whisper 转写、OCR（zai-mcp / 本地兜底）。这是感知不是语义判断，协议见 `.agents/skills/researchos-media/SKILL.md`。
