---
status: canonical
as_of: 2026-07-29
---

# 方法车道协议 / Method Lane Protocol (M0/M1) — Phase 4

方法车道与证据车道**物理隔离**：它承载「**如何研究这个主题**」的耐久方法学，是纯逻辑、**无来源、无可信度**。这样「高密度单源主张」永远无法冒充「被验证的方法」。

| 层 | 是什么 | valid_if |
|----|--------|----------|
| **M0** | 主题通用方法不变量（任何阶段都成立的研究原则） | 无（NULL） |
| **M1** | 阶段/facet 条件启发式（在某 stage/facet 下才适用） | JSON `{stage, facet, condition}` |

## 何时写方法规则

当你从一轮研究中提炼出**可复用的研究方法教训**时（不是关于世界的事实，而是关于「该怎么查/怎么判断」的逻辑）。例如：
- M0：「地缘政治主题：官方表态与一线行动常背离，必须交叉验证行动而非声明。」
- M1：`{stage: corroborating}` 「进入印证期后，新增单源 L3 的边际价值下降，应转向跨平台印证。」

## 命令

```
ros method add <slug> --level M0 --proposition "..."                 # M0 不变量
ros method add <slug> --level M1 --proposition "..." --valid-if '{"stage":"corroborating"}'
ros method ls <slug> [--level M0|M1] [--status active|draft]
ros method export <slug> <rule_id>      # 复制到 topics/_shared/method.db（跨主题候选）
ros method import <slug> <rule_id>      # 从共享库导入 —— 落为 draft（fresh-condense 闸）
```

## 跨主题复用纪律（fresh-condense 闸）

`ros method import` **永不**自动行复制为 active：导入的规则落为 `status='draft'`。借用主题的 agent 必须在本主题语境下**重新审视**该方法是否成立，确认后才 `ros method add ... --status active`（或编辑后启用）。证据行永远不跨主题复制，只有纯逻辑方法可经此闸、且需重新凝练。
