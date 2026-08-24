# Travel demo · 周末去不去

ResearchOS 的**宿主草图**，不是第六个支柱，也不是旅游 App 产品。

用来给人**摸到**第一屏：act / hold / flip，审计默认收着。方法正文仍在 `pillars/`。

```bash
python3 demo/travel/server.py
# 打开 http://127.0.0.1:8787
```

- **先看成品** — 合成样本，零 Key。  
- **用我的 Key 现场推** — 本机同源代理 → 你的 LLM（可选 Tavily / Brave 搜索）。

---

## 跨域：网页里 hack 不掉，也不该 hack

浏览器禁止 `https://our-demo` 里的 JS 去打 `https://api.groq.com` 这类源。这是 **CORS**，由**浏览器**执行，不是厂商「忘了开接口」。

| 做法 | 用户 IP | Key 在哪 | 能不能当产品 |
|---|---|---|---|
| 网页 JS 直连厂商 | 是 | 暴露给页面；托管站可被偷 | 多数厂商 CORS 直接失败 |
| 公开 CORS 代理 / `cors-anywhere` | 视代理 | **中间人能拿到 Key** | 不要做 |
| Chrome `--disable-web-security` | 是 | 本机 | 不是产品 |
| **本 demo：127.0.0.1 白名单代理** | **是** | **只在本机，转发到允许的 host** | 展示 / 集成方自己改 |
| 我们托管后端并卖 Key | 否（是我们的 IP） | 我们可见或代持 | 这是 SaaS，和本页信任模型相反 |

本进程：

- 只绑 `127.0.0.1`
- 只转发 allowlist 里的 LLM / 搜索 host
- 不写磁盘、不打 Key 日志、不是任意 URL 的 SSRF 跳板

「用用户本机 IP 调通用接口」**做得到**，条件是：**在用户机器上跑一个同源代理（或浏览器扩展 / 桌面壳）**。  
只丢一个 GitHub Pages 静态站、又要直连 OpenAI / 机票 / 社媒——**做不到**，也没有干净的 hack。

机票 / 小红书 / X 官方 API 同样几乎全无浏览器 CORS。v1 用 **搜索 API 当证据渠道**（discovery 的一格），不把「接某航司」做成产品表面。

---

## 商业模式不要和信任模型打架

- **BYOK + 本机代理**（本页）：我们不碰 Key。抽成只能走厂商邀请链接，不能走「把 Key 填进我们的网站」。
- **卖 Key / 计量**：必须我们做后端代理、风控、账单。用户 IP 不再是卖点；卖点是免配环境。那是另一个产品，不要假装还是本 demo。

---

## Key

LLM（OpenAI 兼容）：[Groq](https://console.groq.com/keys) · [硅基流动](https://cloud.siliconflow.cn/account/ak) · [DeepSeek](https://platform.deepseek.com/api_keys) · [OpenRouter](https://openrouter.ai/keys)

搜索（可选）：[Tavily](https://app.tavily.com/) · [Brave](https://brave.com/search/api/)

没有搜索 Key 时仍可推理，现场事实必须标 UNKNOWN。
