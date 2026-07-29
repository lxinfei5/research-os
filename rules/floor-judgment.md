---
status: canonical
as_of: 2026-07-29
---

# floor-judgment — 判断与结论地板（可信度/分级/必出结论唯一源）

> 管「证据与库内事实怎么压成带置信的结论」。判断是 agent 的活，Python 不参与（也没有 Python 了）。
> 非门禁：靠自觉 + 人复核。细则唯一源：`credibility_guide.md`。

## L0 · 本域恒真（一次蒸馏）

**第一性目的 = 产出结论。** 给事实判断 + 分级置信 + 依据链，必输出。**诚实 = 说清「有把握到什么程度 + 依据」，不是拒绝输出**——做不到精确给区间 + 置信度 + 依据；连区间都 bound 不了才写「无法判断（无可用锚）」。可信度不挡计算：关键数即使无最硬一手，也须合理推测并代入，禁止「源不够硬→空着不算」。

## 本域会怎么腐

- **拒出结论**：拿「无一手数据」「我们不给建议」当挡箭牌 → 第一性失败。
- **可信度话术刷屏**：把「这可能不准」当结论 → 工作事实默认真，怀疑只留决策分叉。
- **计数冒充可信度**：回音室能放大印证计数 → 计数 ≠ 可信度，由 agent 判。

## 结论分级 S/A/B/C（输出形态）

| 级 | 触发 | 形态 |
|---|---|---|
| **S · 锚定** | 硬信号交叉锚定 | 直述为事实，无前缀 |
| **A · 多源收敛** | ≥2–3 独立软源 / 已标 `[street-consensus]` | 直述为工作事实 |
| **B · 单源线索** | 单条软源未过闸 | `线索：X（单源）`，不单独驱动 |
| **C · anchor-bounded 区间** | 一手点估缺失但锚可 bound | `区间：X∈[下界,上界]` + 一句依据 |
| 真·UNKNOWN | 连锚都 bound 不了 | `无法判断（无可用锚）` |

## 可信度评估（5 轴 + echo-chamber）

每条入库知识带 inline 前缀标签（T0–T4 源阶梯，见 `floor-evidence.md`）+ 视情况 `[echo]` 注记。可信度判断完全留给 agent：系统**不**机械改写你的 level——echo_chamber 标志只作提示，若确属回音室你自己应倾向标 low/medium。5 轴细则（独立性/炒作/时效/…）、领域上限（单源天花板）、calibration 依据，唯一源：`credibility_guide.md`。

## anchor-bounded 估计

做不到精确时，不给「无法判断」反射——给区间：找下界锚与上界锚，代入合理推测，标注置信度与依据。连锚都 bound 不了才允许 UNKNOWN。详例见 `credibility_guide.md` 与 §2.1「关键工作数必算」精神。

## 指针

- 知识怎么落档（三要素/标签/stale）：`floor-corpus.md`
- 信源分档与升格：`floor-evidence.md`
- 凝练三环（distill/aggregate/synthesize 的判断契约）：`l3_distill_protocol.md` / `l2_aggregate_protocol.md` / `l1l0_synthesize_protocol.md`
