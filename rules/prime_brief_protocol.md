---
status: canonical
as_of: 2026-07-29
---

# PRIME / Brief 协议 — 从既有知识唤起检索

> **本阶段在管道的位置：** 凝练三环（distill/aggregate/synthesize）把证据压成知识；**PRIME 走反方向**——
> 把「今天的知识」冻结成「明天的检索 brief」。`ros grow <slug>` 触发：`gap.py` 算每 facet 覆盖度量、
> `stage.py` 贴研究阶段标签、`context.py` load-all 当前主题全部 active L0+L1+open_questions + 阶段门控 M1
> + facet 缺口 + 近 N 次 `search_log` query，冻结为 `context_snapshot.v1`，curator（**LLM agent 步**，非 Python）
> 在 token 预算内发出 keep-list + 紧凑 brief。凝练三环各有 protocol，PRIME 是「系统的发动机」，本文件拥有
> 它的不变量与腐化模式。

## L0 不变量（近恒真——改它 = 改产品定位，须人确认）

用今天的知识唤起明天的检索：brief 告诉检索 agent **已确立什么**（跳过重复检索）、**该追哪些
open_questions / 稀薄 facet**（永不重跑近期 query）。**交出去的是 brief（而非原始候选 JSON）**；
**L0/M0 不可裁剪**（预算 ~12k，先裁 L1/候选，世界观与方法的根永不丢）。

> 改 L0 须人确认；agent 不得以「省 token」架空 L0/M0 不裁剪。

## 本阶段会怎么腐（decay modes）

- **brief 膨胀**：把原始候选 JSON 整包塞给检索 agent，token 爆炸、检索 agent 淹没在噪声——违背「brief 而非原始候选」。
- **query 重跑**：brief 不带近 N 次 `search_log`，检索 agent 重复检索已确立的 facet，浪费预算、不增长。
- **open_questions 不收缩**：凝练产出的 open_questions 一轮轮原样滚动，从不因被回答而关闭——说明凝练没真正回答问题，PRIME 在空转。
- **裁掉根**：为省 token 裁掉 L0 世界模型 / M0 方法——检索 agent 失去世界观锚，产出与既有知识脱节。
- **Python 越权**：用 Python 启发式过滤候选 / 判相关性（违反铁律）——curator 必须是 LLM agent 步，Python 只做确定性 load-all + 覆盖度量。

## key_numbers（可证伪阈值，值现查）

- brief token 预算 ~12k；L0/M0 恒在（裁剪只动 L1/候选）。
- brief 携带近 N 次 `search_log` query 作为「勿重跑」清单（N 由 `context.py` 定，现查不写死）。
- 每轮 brief 的 open_questions 相对上一轮**应减少或更替**（被回答的关闭、新的浮现）。

## break_condition（出现即判 PRIME 腐化）

- **open_questions 连续两轮不收缩**（同一批问题原样滚动，无关闭、无更替）= 凝练没回答问题，PRIME 空转。
- brief 退回原始候选 JSON 整包（无 keep-list 裁剪）。
- 检索 agent 重跑近期已检索的 query（brief 的「勿重跑」清单失效）。
- Python（非 agent）决定了候选取舍 / 相关性。

## 指针

- 唤起装配实现：`ros/assembly/{context,gap,stage}.py`（确定性 load-all + 覆盖度量 + 阶段标签；**不做语义过滤**）。
- open_questions 收缩锚：`methodology/l1l0_synthesize_protocol.md`（synthesize 产出 / 收缩 open_questions）。
- 执行剧本：`.agents/skills/researchos-grow/SKILL.md`（agent 跑 prime→search→capture→condense→report 循环）。
- 阶段→文件映射的机器权威源：`ros/run/condense.py::STAGE_PROTOCOLS`（凝练三环）；PRIME 不走 STAGE_PROTOCOLS，由 grow skill 读本文件。
