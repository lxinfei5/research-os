---
status: canonical
as_of: 2026-07-29
---

# method-shape-rule — 方法形状 + knowledge.md 模板规范

> 定位：`floor-corpus.md` 的操作细则附录。原则核在 floor 文件，本文件给样板/形状/命名规范。
> 两类对象：① 方法车道 M0/M1（怎么研究，纯逻辑无源）② knowledge.md 单档模板。

## 1. 方法形状（M0/M1）

方法是「怎么研究这个主题」的耐久不变量，纯逻辑、无来源（与证据车道物理隔离）。存于 `topics/_shared/methods/<id>.md`（跨主题共享）或主题内引用。

每条方法必带：
- **proposition**：一句可证伪的方法陈述。
- **`key_numbers`**：可证伪的数字阈值（现查不写死）。**永远成立的方法 = 没有方法。**
- **`break_condition`** / `wrong_if`：可观察的失效/反转条件。
- `level: M0`（主题通用不变量）| `M1`（阶段/facet 条件启发式，带 `valid_if`）。

子 agent 严禁改方法——哪怕事实印证了某条，也只进 knowledge.md 作案例；改方法需人复审。

## 2. knowledge.md 单档模板（ topics/<slug>/knowledge.md ）

frontmatter（最小集）：
```yaml
---
slug: <slug>
title: <title>
status: open | closed
stage: scoping | surveying | deepening | saturating | mature
coverage: L0=.. L1=.. L2=.. L3=.. src=..   # 派生快照,以正文为准
last_grown_at: <date>
---
```

正文骨架（heading 即层标签，顺序固定；空层写 `_(空)_`）：
```
# <title> — 世界知识
> 本档只存带 provenance+valid_until 的客观知识…(定位 epigraph)

## L0 世界观(恒真;首段 active,历史下沉,git 即版本链)
### active · <date>
- **(<summary_kind> · confidence:<S/A/B/C>)** <proposition>

## L1 视角(慢变,人复审)
### <facet 或 桶名>
- **(<synthesis_kind> · <stance> · confidence:<..>)** <narrative>

## L2 印证事实(多源互证)
### <facet 或 桶名>
- **[<T0–T4> · 多源×N · 跨平台×M]** <statement> *(provenance: …; valid_until: …)*

## L3 单源主张(一条 source 一条)
### <facet 或 桶名>
- **[<T0–T4> · <claim_kind> · 单源]** <proposition> *(source: `sources/<hash>.md`)*

## 未决问题
- [ ] <question>   /   - [x] <已答> → 答于 <何处>

## 信源索引
| content_hash | platform | kind | url | captured | valid_to |

## facet 覆盖(派生快照,以正文为准)
- <facet question> (`<facet_id>`): L3=.. L2=.. · thin/developing/corroborated · last_search <date>
```

## 3. 命名与归属

- facet/桶名：L 行的 `facet` 字段原样落为 `### <名>` 节标题；注册的 facet 问题在 `## facet 覆盖` 以 `(`<facet_id>`)` 关联。即席桶（`_unfileted` 等）如实落档，下轮 grow 时由 agent 重归组。
- 一主题一档，主题物理隔离 = N 个 knowledge.md，永不自动合并。
- 跨档引用只走相对路径 + 锚 heading，不复制目标内容。

## 4. 纯度护栏（见即砍）

给 knowledge.md / L 层 / 方法加 schema、id、受控词表、引擎、lint、DB、迁移编号 = V1 绑死那套复活，**砍**。发现 = 目录 + heading + grep，这就够了。
