# researchos-travel — 旅游攻略生成

生成一个包含**吃、住、行**三部分 + **交互地图**的旅游攻略 HTML 页面。

## 触发

用户说"帮我做 XX 的旅游攻略"、"XX 周末怎么玩"、"帮我规划 XX 行程"等。

## 铁律

1. **社媒活人评价 > 平台评分**。大众点评/Trip.com 可被控评，小红书/抖音的活人吐槽不可控——后者权重更高。
2. **每个推荐必须有差评**。只有好评没有差评的餐厅/景点 = 信号可疑，要标注。
3. **排序靠评价质量，不靠星级**。一条带图的差评比 100 条"好吃"更有决策价值。
4. **HTML 必须嵌入 Leaflet 地图**。没有地图的攻略 = 不合格。
5. **小红书搜索走多路径**：优先真实主 Chrome（`webbridge-mcp` 子 agent / `kimi-webbridge` 主循环），反爬/EOF 时降级 `xiaohongshu-mcp`；`collector` 记实际用的那个。防风控节奏（首次成功后克制、详情 1–3 条串行 5–8s、空结果=预警、遇 EOF/扫码立即 STOP）见 `methodology/xiaohongshu_search_playbook.md`。capture 允许任一 collector——门禁只对显式 forbidden 列表硬拒，XHS 无 forbidden。

完整方法论见 `methodology/travel_guide_pattern.md`。

## 执行流程

### Phase 1：发现候选（宽搜，并行）

```
同时搜三个维度：
  吃：小红书 + 抖音 + web "<目的地> 美食 推荐 必吃"
  行：小红书 + 抖音 + web "<目的地> 攻略 路线 景点"
  住：web "<目的地> 住宿 民宿 推荐"（轻量搜即可）
```

> ⚠️ **XHS 搜索工具约束（多路径）**：优先真实主 Chrome（`mcp__webbridge-mcp__navigate`+`snapshot`，
> 子 agent 可达；主循环用 `kimi-webbridge` skill）；反爬/EOF 时降级 `mcp__xiaohongshu-mcp__search_feeds`
> + `get_feed_detail`。若持续超时/被墙，记录 `degraded_reason: "xhs_anti_bot"` + 列表卡片仍可降级 capture。
> 节奏铁律见 `methodology/xiaohongshu_search_playbook.md`。

Phase 1 产出：N 个候选餐厅 + M 个候选景点/路线。

### Phase 2：逐候选差评审计（N 组独立搜索）

> ⚠️ 这是最关键的一步，不可省略、不可合并。

**对 Phase 1 产出的每一个候选餐厅，单独发起一组差评搜索**：
```
搜 "<餐厅名> 踩雷"
搜 "<餐厅名> 难吃"
搜 "<餐厅名> 态度差"
搜 "<餐厅名> 不值得"
```

禁止泛搜"XX地 难吃的餐厅"——泛搜返回 SEO 软文，活人差评一定带店名。
N 个候选 = N 组独立搜索，可以并行但搜索词必须是 `<店名> + 负面词`。

> ⚠️ **差评搜索的 XHS 部分约束同 Phase 1（多路径）**：优先真实主 Chrome（`webbridge-mcp` 子 agent / `kimi-webbridge` 主循环），反爬/EOF 时兜底 `xiaohongshu-mcp`；`collector` 记实际用的那个，节奏铁律见 `methodology/xiaohongshu_search_playbook.md`。

### Phase 3：交叉验证 + 评分

- 合并多平台好评 + 逐候选差评审计结果
- 差评中有 🔴硬伤（卫生/食材/短斤缺两）→ 降级或排除
- 差评中只有 🟡槽点（服务/排队）→ 降权但保留
- 零差评的候选 → 标注 `⚠️ 差评样本缺失`
- 按"好评密度 − 差评严重度"排序

### Phase 4：生成 HTML

- 使用 `topics/<slug>/plan.html` 路径
- 遵循 `methodology/travel_visual_style.md` 设计风格
- 嵌入 Leaflet 地图
- 用 `open` 命令在浏览器中打开

## 产出检查

生成后逐条确认 quality checklist（见 methodology 第 4 节）。

## HTML 模板

参考本 skill 目录下的 `template.html`。
