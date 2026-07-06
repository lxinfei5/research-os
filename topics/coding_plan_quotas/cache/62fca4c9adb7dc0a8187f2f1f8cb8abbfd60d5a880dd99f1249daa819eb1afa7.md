# Ollama Pricing — Official Page
<https://registry.ollama.ai/pricing>
`content_hash: 62fca4c9adb7dc0a8187f2f1f8cb8abbfd60d5a880dd99f1249daa819eb1afa7`

# Ollama Pricing — Official Page (fetched 2026-07-06)

## Plans

### Free ($0)
- Run models on your hardware (unlimited)
- Access cloud models (light usage)
- CLI, API, and desktop apps
- 40,000+ community integrations
- Unlimited public models
- Session limits reset every 5 hours; weekly limits reset every 7 days

### Pro ($20/mo or $200/yr)
- Everything in Free
- Access larger, more powerful cloud models
- Run 3 cloud models at a time
- 50x more cloud usage than Free
- Upload and share private models
- Pro and Max users can add extra usage balance
- Day-to-day work: larger models, coding automation, deep research

### Max ($100/mo)
- Everything in Pro
- Run 10 cloud models at a time
- 5x more usage than Pro (i.e., ~250x Free)
- Heavy, sustained usage: continuous agent tasks, multiple concurrent agents, large models over extended sessions

### Team (Coming soon)
- Shared usage across team, centralized billing, SSO, model access controls, MDM installer, priority support + Slack

## Usage Measurement
- Based on GPU time, not token caps or request counts
- Model usage levels: 1 (light, e.g. gpt-oss:20b) to 4 (extra heavy, e.g. deepseek-v4-pro)
- Shorter requests + cached-context prompts consume less
- Concurrency queuing: requests beyond limit are queued; if queue is full, rejected
- 90% email notification (can disable)
- Usage visible at /settings

## Privacy
- Prompt/response data never logged or trained on
- NVIDIA Cloud Providers with no-logging, no-training, zero-data-retention policies
- Hosted primarily in US; may route to Europe/Singapore for capacity

## Model Details
- Native weights; NVFP4 on Blackwell/Vera Rubin architectures
- Tool calling supported
- Full cloud model list: https://ollama.com/search?c=cloud

Source: https://registry.ollama.ai/pricing
