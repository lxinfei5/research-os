package main

import (
	"context"
	"fmt"
	"runtime/debug"

	"github.com/modelcontextprotocol/go-sdk/mcp"
	"github.com/sirupsen/logrus"
)

// This file registers the MCP tool surface. Every WebBridge daemon action is
// exposed 1:1 (per the "expose everything" decision), INCLUDING the strong
// escape hatches evaluate/cdp — they run against the user's REAL logged-in
// browser, so their descriptions carry explicit risk notes.
//
// Every tool takes a required `session` string: one task == one session == one
// Chrome tab group. Pick a task-named session at the start and reuse it across
// every call (even across sites); switching mid-task fragments the tab group.

// ---- shared helpers ----

func boolPtr(b bool) *bool { return &b }

// withPanicRecovery turns a panicking handler into an IsError result instead of
// crashing the server (mirrors xiaohongshu-mcp).
func withPanicRecovery[T any](
	tool string,
	h func(context.Context, *mcp.CallToolRequest, T) (*mcp.CallToolResult, any, error),
) func(context.Context, *mcp.CallToolRequest, T) (*mcp.CallToolResult, any, error) {
	return func(ctx context.Context, req *mcp.CallToolRequest, args T) (result *mcp.CallToolResult, resp any, err error) {
		defer func() {
			if r := recover(); r != nil {
				logrus.WithFields(logrus.Fields{"tool": tool, "panic": r}).Error("tool handler panicked")
				logrus.Errorf("stack:\n%s", debug.Stack())
				result = errResult(fmt.Sprintf("webbridge-mcp tool %s panicked: %v", tool, r))
				resp, err = nil, nil
			}
		}()
		return h(ctx, req, args)
	}
}

func errResult(msg string) *mcp.CallToolResult {
	return &mcp.CallToolResult{
		Content: []mcp.Content{&mcp.TextContent{Text: msg}},
		IsError: true,
	}
}

func textResult(raw string) *mcp.CallToolResult {
	return &mcp.CallToolResult{
		Content: []mcp.Content{&mcp.TextContent{Text: raw}},
		IsError: responseIsError(raw),
	}
}

// call proxies one action to the daemon and wraps the verbatim response.
// An empty session is rejected rather than defaulted: two concurrent sub-agents that
// both omit it would otherwise share one Chrome tab group and clobber each other's tabs.
func call(p *WebBridgeProxy, session, action string, args map[string]interface{}) (*mcp.CallToolResult, any, error) {
	if session == "" {
		return errResult("session is required and must be non-empty — one task = one session = one Chrome tab group; pick a task-named session and reuse it across the whole task"), nil, nil
	}
	raw, err := p.Execute(session, action, args)
	if err != nil {
		return errResult(err.Error()), nil, nil
	}
	return textResult(raw), nil, nil
}

// ---- tool argument structs (json+jsonschema tags drive the MCP input schema) ----

type NavigateArgs struct {
	Session    string `json:"session" jsonschema:"任务级会话名。一个任务一个 session（等于一个 Chrome tab group），整个任务所有调用都用它、跨站也不换。按任务命名(如 xhs-collection-scan)而非按站点命名"`
	URL        string `json:"url" jsonschema:"要打开的 URL"`
	NewTab     bool   `json:"new_tab,omitempty" jsonschema:"新开一个并存的标签页；省略或 false 则把当前标签页重定向到该 URL"`
	GroupTitle string `json:"group_title,omitempty" jsonschema:"标签组的可见标签，用用户语言，只在任务第一次 navigate 时设置"`
}

type FindTabArgs struct {
	Session string `json:"session" jsonschema:"任务级会话名，与本任务其它调用一致"`
	URL     string `json:"url" jsonschema:"要选中的已打开标签页的完整 URL(取自 list_tabs 或之前 navigate 的结果，别用裸域名)"`
	Active  bool   `json:"active,omitempty" jsonschema:"选中用户当前正在看的标签页(传 true)；否则最左匹配。返回 no open tab found 时改用 navigate 的 new_tab"`
}

type SessionOnlyArgs struct {
	Session string `json:"session" jsonschema:"任务级会话名，与本任务其它调用一致"`
}

type ClickArgs struct {
	Session  string `json:"session" jsonschema:"任务级会话名"`
	Selector string `json:"selector" jsonschema:"@e 引用(取自 snapshot)或 CSS 选择器。合成 click(isTrusted=false)，严格校验 isTrusted 的银行/验证码页会忽略；提交表单=点提交按钮(无回车工具)"`
}

type FillArgs struct {
	Session  string `json:"session" jsonschema:"任务级会话名"`
	Selector string `json:"selector" jsonschema:"@e 引用或 CSS 选择器"`
	Value    string `json:"value" jsonschema:"要填入的文本。清空并插入(替换原内容)，对 input/textarea 与 contenteditable 富文本都生效"`
}

type EvaluateArgs struct {
	Session string `json:"session" jsonschema:"任务级会话名"`
	Code    string `json:"code" jsonschema:"⚠强力工具：在用户真实登录的浏览器标签里执行任意 JS(支持 async/await)，可读写任意页面状态与该页 cookie 可及数据。仅当 snapshot/@e 无法完成时用。用 IIFE 包裹(共享 JS realm，重复声明 const/let 会 SyntaxError)，返回紧凑 JSON.stringify(勿美化缩进)"`
}

type CDPArgs struct {
	Session string                 `json:"session" jsonschema:"任务级会话名"`
	Method  string                 `json:"method" jsonschema:"⚠最强力也最危险的逃生舱：经 chrome.debugger 直发 CDP 方法名(如 Network.getCookies)到用户真实浏览器，可注入可信输入、发任意协议调用。仅在 snapshot/click/fill/evaluate 全部失败后作为最后手段"`
	Params  map[string]interface{} `json:"params,omitempty" jsonschema:"CDP 方法参数对象"`
}

type ScreenshotArgs struct {
	Session  string `json:"session" jsonschema:"任务级会话名"`
	Format   string `json:"format,omitempty" jsonschema:"png(默认)或 jpeg"`
	Quality  int    `json:"quality,omitempty" jsonschema:"仅 jpeg，0-100"`
	Selector string `json:"selector,omitempty" jsonschema:"@e 或 CSS，只截该元素；省略则截当前标签可视区"`
	Path     string `json:"path,omitempty" jsonschema:"输出路径(逐字生效，父目录自动建，同名覆盖，建议唯一文件名)；省略则 daemon 落 OS 临时目录"`
}

type NetworkArgs struct {
	Session   string `json:"session" jsonschema:"任务级会话名"`
	Cmd       string `json:"cmd" jsonschema:"网络抓包生命周期：start|stop|list|detail"`
	Filter    string `json:"filter,omitempty" jsonschema:"list 时的过滤串"`
	RequestID string `json:"request_id,omitempty" jsonschema:"当 cmd 为 detail 时必填的请求 id"`
}

type UploadArgs struct {
	Session  string   `json:"session" jsonschema:"任务级会话名"`
	Selector string   `json:"selector" jsonschema:"页面上的 file input 选择器"`
	Files    []string `json:"files" jsonschema:"要上传的本地文件绝对路径列表"`
}

type SaveAsPDFArgs struct {
	Session         string   `json:"session" jsonschema:"任务级会话名"`
	PaperFormat     string   `json:"paper_format,omitempty" jsonschema:"letter(默认)|a4|legal|a3|tabloid"`
	Landscape       bool     `json:"landscape,omitempty" jsonschema:"横向，默认 false"`
	Scale           *float64 `json:"scale,omitempty" jsonschema:"缩放，默认 1.0，范围 0.1-2.0"`
	PrintBackground *bool    `json:"print_background,omitempty" jsonschema:"打印背景，默认 true"`
	Path            string   `json:"path,omitempty" jsonschema:"输出路径，语义同 screenshot；省略则落 OS 临时目录。解码后 >100MB 会被拒(降 scale 或拆页)"`
}

// ---- registration ----

func registerTools(server *mcp.Server, p *WebBridgeProxy) {
	// navigate
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "navigate",
			Description: "在用户真实 Chrome(带真实登录态)里打开一个 URL。一个任务一个 session；任务首次 navigate 用 group_title 设置标签组可见名(用户语言)。new_tab=true 并存标签，省略则重定向当前标签",
			Annotations: &mcp.ToolAnnotations{Title: "Navigate", ReadOnlyHint: true},
		},
		withPanicRecovery("navigate", func(ctx context.Context, req *mcp.CallToolRequest, a NavigateArgs) (*mcp.CallToolResult, any, error) {
			args := map[string]interface{}{"url": a.URL}
			if a.NewTab {
				args["newTab"] = true
			}
			if a.GroupTitle != "" {
				args["group_title"] = a.GroupTitle
			}
			return call(p, a.Session, "navigate", args)
		}),
	)

	// find_tab
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "find_tab",
			Description: "把一个已打开的标签页选为当前标签(传完整 URL)。active=true 选用户当前在看的标签；返回 no open tab found 时改用 navigate new_tab=true",
			Annotations: &mcp.ToolAnnotations{Title: "Find Tab", ReadOnlyHint: true},
		},
		withPanicRecovery("find_tab", func(ctx context.Context, req *mcp.CallToolRequest, a FindTabArgs) (*mcp.CallToolResult, any, error) {
			args := map[string]interface{}{"url": a.URL}
			if a.Active {
				args["active"] = true
			}
			return call(p, a.Session, "find_tab", args)
		}),
	)

	// snapshot
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "snapshot",
			Description: "取当前标签的无障碍树(带 @e 引用)。读页面内容、定位元素的首选方式；@e 引用比 CSS class hash 更稳。仅 top frame，跨源 iframe 需直接 navigate 到其 URL",
			Annotations: &mcp.ToolAnnotations{Title: "Snapshot", ReadOnlyHint: true},
		},
		withPanicRecovery("snapshot", func(ctx context.Context, req *mcp.CallToolRequest, a SessionOnlyArgs) (*mcp.CallToolResult, any, error) {
			return call(p, a.Session, "snapshot", nil)
		}),
	)

	// click
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "click",
			Description: "点击 @e 引用或 CSS 选择器指向的元素",
			Annotations: &mcp.ToolAnnotations{Title: "Click"},
		},
		withPanicRecovery("click", func(ctx context.Context, req *mcp.CallToolRequest, a ClickArgs) (*mcp.CallToolResult, any, error) {
			return call(p, a.Session, "click", map[string]interface{}{"selector": a.Selector})
		}),
	)

	// fill
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "fill",
			Description: "向 input/textarea/contenteditable 填入文本(清空并插入)",
			Annotations: &mcp.ToolAnnotations{Title: "Fill"},
		},
		withPanicRecovery("fill", func(ctx context.Context, req *mcp.CallToolRequest, a FillArgs) (*mcp.CallToolResult, any, error) {
			return call(p, a.Session, "fill", map[string]interface{}{"selector": a.Selector, "value": a.Value})
		}),
	)

	// evaluate (strong)
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "evaluate",
			Description: "⚠在用户真实登录浏览器标签里执行任意 JS(async/await 可用)。可读写任意页面状态与该页可及数据。仅当 snapshot/@e 无法完成时使用；用 IIFE 包裹并返回紧凑 JSON.stringify",
			Annotations: &mcp.ToolAnnotations{Title: "Evaluate JS"},
		},
		withPanicRecovery("evaluate", func(ctx context.Context, req *mcp.CallToolRequest, a EvaluateArgs) (*mcp.CallToolResult, any, error) {
			return call(p, a.Session, "evaluate", map[string]interface{}{"code": a.Code})
		}),
	)

	// cdp (strongest)
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "cdp",
			Description: "⚠经 chrome.debugger 直发原始 CDP 方法到用户真实浏览器——最强力最危险的逃生舱(可注入可信输入/任意协议调用)。仅在 snapshot/click/fill/evaluate 全部失败后作为最后手段",
			Annotations: &mcp.ToolAnnotations{Title: "CDP Passthrough"},
		},
		withPanicRecovery("cdp", func(ctx context.Context, req *mcp.CallToolRequest, a CDPArgs) (*mcp.CallToolResult, any, error) {
			args := map[string]interface{}{"method": a.Method}
			if a.Params != nil {
				args["params"] = a.Params
			}
			return call(p, a.Session, "cdp", args)
		}),
	)

	// screenshot (path passthrough)
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "screenshot",
			Description: "截图当前标签或某元素。返回本地文件路径(非 base64)——MCP 客户端是本机 agent，用 Read 工具打开该 path 查看图片",
			Annotations: &mcp.ToolAnnotations{Title: "Screenshot", ReadOnlyHint: true},
		},
		withPanicRecovery("screenshot", func(ctx context.Context, req *mcp.CallToolRequest, a ScreenshotArgs) (*mcp.CallToolResult, any, error) {
			args := map[string]interface{}{}
			if a.Format != "" {
				args["format"] = a.Format
			}
			if a.Quality > 0 {
				args["quality"] = a.Quality
			}
			if a.Selector != "" {
				args["selector"] = a.Selector
			}
			if a.Path != "" {
				args["path"] = a.Path
			}
			return call(p, a.Session, "screenshot", args)
		}),
	)

	// network
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "network",
			Description: "当前标签的网络抓包：start→浏览→list(带 filter)→detail(request_id)→stop",
			Annotations: &mcp.ToolAnnotations{Title: "Network Capture", ReadOnlyHint: true},
		},
		withPanicRecovery("network", func(ctx context.Context, req *mcp.CallToolRequest, a NetworkArgs) (*mcp.CallToolResult, any, error) {
			args := map[string]interface{}{"cmd": a.Cmd}
			if a.Filter != "" {
				args["filter"] = a.Filter
			}
			if a.RequestID != "" {
				args["requestId"] = a.RequestID
			}
			return call(p, a.Session, "network", args)
		}),
	)

	// upload
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "upload",
			Description: "把本地文件挂到页面的 file input 上",
			Annotations: &mcp.ToolAnnotations{Title: "Upload"},
		},
		withPanicRecovery("upload", func(ctx context.Context, req *mcp.CallToolRequest, a UploadArgs) (*mcp.CallToolResult, any, error) {
			files := make([]interface{}, len(a.Files))
			for i, f := range a.Files {
				files[i] = f
			}
			return call(p, a.Session, "upload", map[string]interface{}{"selector": a.Selector, "files": files})
		}),
	)

	// save_as_pdf (path passthrough)
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "save_as_pdf",
			Description: "把当前标签渲染成 PDF，返回本地文件路径(用 Read 工具查看)。解码后 >100MB 会被拒",
			Annotations: &mcp.ToolAnnotations{Title: "Save as PDF", ReadOnlyHint: true},
		},
		withPanicRecovery("save_as_pdf", func(ctx context.Context, req *mcp.CallToolRequest, a SaveAsPDFArgs) (*mcp.CallToolResult, any, error) {
			args := map[string]interface{}{}
			if a.PaperFormat != "" {
				args["paper_format"] = a.PaperFormat
			}
			if a.Landscape {
				args["landscape"] = true
			}
			if a.Scale != nil {
				args["scale"] = *a.Scale
			}
			if a.PrintBackground != nil {
				args["print_background"] = *a.PrintBackground
			}
			if a.Path != "" {
				args["path"] = a.Path
			}
			return call(p, a.Session, "save_as_pdf", args)
		}),
	)

	// list_tabs
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "list_tabs",
			Description: "列出本 session 标签组内的标签(新 session 返回空数组)。返回的完整 URL 可喂给 find_tab",
			Annotations: &mcp.ToolAnnotations{Title: "List Tabs", ReadOnlyHint: true},
		},
		withPanicRecovery("list_tabs", func(ctx context.Context, req *mcp.CallToolRequest, a SessionOnlyArgs) (*mcp.CallToolResult, any, error) {
			return call(p, a.Session, "list_tabs", nil)
		}),
	)

	// close_tab
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "close_tab",
			Description: "关闭本 session 的当前标签",
			Annotations: &mcp.ToolAnnotations{Title: "Close Tab", DestructiveHint: boolPtr(true)},
		},
		withPanicRecovery("close_tab", func(ctx context.Context, req *mcp.CallToolRequest, a SessionOnlyArgs) (*mcp.CallToolResult, any, error) {
			return call(p, a.Session, "close_tab", nil)
		}),
	)

	// close_session
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "close_session",
			Description: "关闭本 session 标签组里的所有标签。任务结束且用户不再需要这些页面时调用；若可能有后续追问，先给出答案再关",
			Annotations: &mcp.ToolAnnotations{Title: "Close Session", DestructiveHint: boolPtr(true)},
		},
		withPanicRecovery("close_session", func(ctx context.Context, req *mcp.CallToolRequest, a SessionOnlyArgs) (*mcp.CallToolResult, any, error) {
			return call(p, a.Session, "close_session", nil)
		}),
	)

	// status (health of the underlying daemon) — no session
	mcp.AddTool(server,
		&mcp.Tool{
			Name:        "status",
			Description: "健康检查底层 Kimi WebBridge daemon(:10086)。任务前先查：extension_connected=false 时命令会失败即便 daemon 在运行。本 MCP 只 health-check，从不 start/stop daemon",
			Annotations: &mcp.ToolAnnotations{Title: "WebBridge Status", ReadOnlyHint: true},
		},
		withPanicRecovery("status", func(ctx context.Context, req *mcp.CallToolRequest, _ any) (*mcp.CallToolResult, any, error) {
			raw, healthy, err := p.Status()
			if err != nil {
				return errResult(fmt.Sprintf("WebBridge daemon (:10086) unreachable: %v — start it manually with `%s`", err, webbridgeStartHint)), nil, nil
			}
			if !healthy {
				return errResult(fmt.Sprintf("WebBridge daemon up but not fully healthy (extension may be detached): %s", raw)), nil, nil
			}
			return textResult(raw), nil, nil
		}),
	)

	logrus.Info("webbridge-mcp: registered 15 tools (14 WebBridge actions + status)")
}
