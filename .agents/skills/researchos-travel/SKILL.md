# researchos-travel — 旅游攻略生成

生成一个包含**吃、住、行**三部分 + **交互地图**的旅游攻略 HTML 页面。

## 触发

用户说"帮我做 XX 的旅游攻略"、"XX 周末怎么玩"、"帮我规划 XX 行程"等。

## 铁律

1. **社媒活人评价 > 平台评分**。大众点评/Trip.com 可被控评，小红书/抖音的活人吐槽不可控——后者权重更高。
2. **每个推荐必须有差评**。只有好评没有差评的餐厅/景点 = 信号可疑，要标注。
3. **排序靠评价质量，不靠星级**。一条带图的差评比 100 条"好吃"更有决策价值。
4. **HTML 必须嵌入 Leaflet 地图**。没有地图的攻略 = 不合格。
5. **小红书搜索只能走 xiaohongshu-mcp**。严禁使用 webbridge-mcp、kimi-webbridge、chrome-devtools 或任何浏览器工具访问 xiaohongshu.com。xiaohongshu-mcp 超时或返回空时，如实记录 `degraded_reason`，不得自行降级到浏览器路径。这是硬约束，违反会导致：①污染用户主浏览器登录态；②触发 XHS 风控（浏览器指纹与 MCP 不一致）；③产出数据被 capture gate 拒绝。

完整方法论见 `methodology/travel_guide_pattern.md`。

## 执行流程

### Phase 1：发现候选（宽搜，并行）

```
同时搜三个维度：
  吃：小红书 + 抖音 + web "<目的地> 美食 推荐 必吃"
  行：小红书 + 抖音 + web "<目的地> 攻略 路线 景点"
  住：web "<目的地> 住宿 民宿 推荐"（轻量搜即可）
```

> ⚠️ **XHS 搜索工具约束**：小红书维度必须且仅能使用 `mcp__xiaohongshu-mcp__search_feeds` +
> `mcp__xiaohongshu-mcp__get_feed_detail`。严禁用 webbridge-mcp / kimi-webbridge 打开
> xiaohongshu.com。若 xiaohongshu-mcp 持续超时，记录 `degraded_reason: "xhs_mcp_timeout"`，
> 不得自行降级到浏览器路径。

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

> ⚠️ **差评搜索的 XHS 部分同样只能走 xiaohongshu-mcp**，约束同 Phase 1。

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
