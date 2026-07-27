package main

// Historical note: this file used to hard-block navigate/find_tab to Xiaohongshu hosts
// ("crown-jewel" transport denylist). That policy was removed — ResearchOS now follows
// AStockOSV2: main Chrome login surface is the primary path for XHS; xiaohongshu-mcp is
// a soft fallback on anti-bot. Browser access is capability, not a ban.
//
// Host-stem list remains available for optional diagnostics / future soft warnings only.
// It is NOT enforced on navigate.

var xhsHostStems = []string{"xiaohongshu.com", "xhslink.com", "xhs.cn", "rednote.com", "xhscdn.com"}
