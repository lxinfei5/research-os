# tools/social_mcp — 社媒 MCP 收口层

社媒访问的**进程状态 / 使用方式 / 物理路径**单一源。所有私有社媒抓取都经 MCP 工具，
不再散落 `curl :10086` 或各处手动拉起的后台进程。

> 本目录是**执行面工具**（workflow 工具），不是 `ros/**` 业务引擎。它符合铁律：只搬运 / 代理，
> **不做推理、不碰知识档、不调 LLM**。语义判断在 `rules/*.md`。
> Go 二进制 `webbridge_mcp/webbridge-mcp` 是 build 产物，已 gitignore。

## 服务拓扑

| 服务 | 端口 | 连接对象 / 登录态 | 归属 | 谁管生命周期 |
|---|---|---|---|---|
| **xiaohongshu-mcp** | 18060 | 独立 Chrome profile（用户小红书账号，本地 `cookies.json`） | 外部 Go 二进制 `~/Documents/Xiaohongshu/xiaohongshu-mcp/` | `social_mcp_daemon.sh`（**cwd 必须是该目录**，`cookies.json` 按相对路径解析） |
| **webbridge-mcp** | 18061 | 代理 Kimi WebBridge → 用户**真实主 Chrome session** | 本项目 `webbridge_mcp/`（Go） | `social_mcp_daemon.sh` |
| **Kimi WebBridge daemon** | 10086 | 用户真实主 Chrome | 外部（Kimi App / `~/.kimi-webbridge/`） | **不归本管理器管**——只 health-check，永不 start/stop（避免与 Kimi App 争抢） |

**没有独立的 x-mcp。** X 的搜索/读帖全部经 `webbridge-mcp` 走真实主 Chrome
（详见下文「为什么 X 不做独立 MCP」，完整裁决在 `rules/social_access_playbook.md` §四·1）。

## 平台 × 能力 × 工具（能力矩阵）

| 平台 | 搜索 | 帖子详情 | 子 agent 可达 | 说明 |
|---|---|---|---|---|
| **小红书** | **主 Chrome**（`webbridge-mcp`）优先；`xiaohongshu-mcp` 兜底 | 同 | ✅ | 多路径（AStockOSV2 对齐）；`collector` 记实际路径；防风控靠 playbook 非硬禁 |
| **X / Twitter** | `webbridge-mcp` | `webbridge-mcp` | ✅ | 全部经真实主 Chrome session |
| **抖音** | `webbridge-mcp` | `webbridge-mcp` | ✅ | **仅用户显式要求时**加载，不主动搜索；视频先经 researchos-media skill 转文字 |
| **公网（登录墙/JS/反爬）** | — | `webbridge-mcp`（fetch Tier-3） | ✅ | 公网读取链的浏览器兜底；普通页优先 zhipu web-reader / WebFetch |

> **搜索优先级**：小红书 + X 优先；抖音仅显式。策略全文见
> `rules/social_access_playbook.md` 与 `rules/xiaohongshu_search_playbook.md`。

## 进程管理

```bash
tools/social_mcp/social_mcp_daemon.sh start-all      # build(按需) + 起 xiaohongshu-mcp + webbridge-mcp；health-check :10086（不启动它）
tools/social_mcp/social_mcp_daemon.sh stop-all       # 停两个 MCP + 清 rod 孤儿；不动 :10086
tools/social_mcp/social_mcp_daemon.sh status         # 进程/端口/二进制概览
tools/social_mcp/social_mcp_daemon.sh health-check   # 深检（端口 + WebBridge /status 的 extension_connected + 各 MCP /health）；全绿 exit 0
tools/social_mcp/social_mcp_daemon.sh build          # go build webbridge-mcp
tools/social_mcp/social_mcp_daemon.sh start|stop|restart <xiaohongshu-mcp|webbridge-mcp>
tools/social_mcp/social_mcp_daemon.sh logs <name>
tools/social_mcp/social_mcp_daemon.sh cleanup        # 清 rod-Chrome 孤儿（argv-scoped pkill 'rod/user-data'）
```

- **状态落点**：`~/.researchos/social_mcp/{pids,logs}/`（可用 `ROS_SOCIAL_HOME` 覆盖）。不入 git。
- **Kimi WebBridge daemon 掉线**：本管理器只提示 `~/.kimi-webbridge/bin/kimi-webbridge start`，绝不代跑。
- **rod-Chrome 孤儿**：xiaohongshu-mcp 用 rod，反爬 EOF 会留孤儿；`stop-all`/`cleanup` 用
  argv-scoped `pkill -f 'rod/user-data'`（只杀 argv 含 `rod/user-data` 的进程，碰不到主 Chrome / WebBridge /
  chrome-devtools-mcp profile）。**绝不用宽泛 `pkill chrome`**。

## MCP 注册

`.mcp.json`（Claude Code）的 `mcpServers` 带 `webbridge-mcp`（`http://localhost:18061/mcp`）。
注册后，**workflow 子 agent 自动获得 `mcp__webbridge-mcp__*` 与 `mcp__xiaohongshu-mcp__*` 工具**——
这正是把 WebBridge 从 skill 升级为 MCP 的动机：**skill 是建议性 prose，spawned 子 agent 加载不到它，
也加载不到 `curl`**。有了 MCP，X/抖音 抓取不再受限于主 agent 循环，可在多 agent 扇出里下放。

> **端口 :18061 是「webbridge 代理」的约定端口，跨兄弟项目共享**——与 `xiaohongshu-mcp` 的 :18060
> 完全同一个模式（ResearchOS 与 AStockOS 的 `.mcp.json` 早已都指向 :18060）。稀缺资源是**唯一那份真实
> Chrome profile**（:10086），不是代理二进制：`webbridge-mcp` 是**无状态代理**，两个项目各自 build 一份
> 二进制（每个 repo 自足、可独立启动），但运行时**只应有一个实例 bind :18061**，谁先起谁服务两边——
> `social_mcp_daemon.sh start` 见端口已占即视为「已运行」返回，不重复 bind、不 double-open 那份 profile。
> 这满足既定裁决「分开建 OK，只要共享同一 profile、绝不 double-open」。

## webbridge-mcp 工具面（15 个，全暴露）

1:1 透传 Kimi WebBridge 的 14 个 action + 一个 `status` 健康检查。每个工具（`status` 除外）带
required 的 `session`：**一个任务一个 session（= 一个 Chrome tab group），整个任务复用、跨站不换**
（两个并发子 agent 都省略 session 会共用一个 tab 组、互相踩踏，故 session 强制非空）。

`navigate` · `find_tab` · `snapshot` · `click` · `fill` · `evaluate`⚠ · `cdp`⚠ ·
`screenshot` · `network` · `upload` · `save_as_pdf` · `list_tabs` · `close_tab` ·
`close_session` · `status`

> ⚠ `evaluate`（任意 JS）与 `cdp`（DevTools 协议、可注入可信输入）作用于**你的真实登录浏览器**，
> 按决策全部暴露；工具描述里带风险提示，约定「仅在 snapshot/click/fill 无法完成时使用」。
> `screenshot`/`save_as_pdf` 返回**本地文件路径**（非 base64），用 Read 工具打开查看。
>
> **安全边界**：默认只 bind `127.0.0.1:18061`（loopback），因为它 re-expose 用户真实登录 Chrome，
> **绝不可** listen 在 `0.0.0.0`。它只 proxy `:10086` 并 health-check，**从不 start/stop** 那个 daemon。

## 为什么 X 不做独立 MCP（twscrape 已否决）

早期设想过独立 `x-mcp`：**独立 Chrome profile(rod)** 被 X 反爬指纹识别、根本登录不了；
开源 `twscrape`（cookie 直连 X 内部 API）代码审计干净、无 RCE，**但账号层不可控**——同机 / 同住宅
IP / 同设备指纹上「小号跑 twscrape / 主账号跑 WebBridge」是**假隔离**，X 靠 IP + 指纹关联多账号，
烧小号会污染并可能牵连真实主账号。真隔离需专用住宅代理 + 独立设备指纹（持续成本且仍易封）。
而真实检索量（几十~上百 query/天）本就落在 WebBridge 人速可承受范围内。

**裁决 = 降级**：X 走 `webbridge-mcp`（真 Chrome、真 session、真住宅 IP，逐请求检测风险严格低于
twscrape）。twscrape 不入仓库、不启用。完整审计与强约束见 `rules/social_access_playbook.md` §四。
