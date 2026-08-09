package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

const (
	webbridgeStartHint = "kimi-webbridge start"
	// webbridgeStartHint is surfaced in errors only. We never run it: :10086 is
	// owned by the Kimi app, so auto-starting would fight the app's own daemon.
	commandTimeout = 120 * time.Second
	statusTimeout  = 3 * time.Second
)

func webbridgeBaseURL() string {
	for _, key := range []string{"SOCIAL_MCP_KIMI_URL", "ROS_WEBBRIDGE_URL"} {
		if value := strings.TrimSpace(os.Getenv(key)); value != "" {
			return strings.TrimRight(value, "/")
		}
	}
	port := strings.TrimSpace(os.Getenv("SOCIAL_MCP_KIMI_PORT"))
	if port == "" {
		port = "10086"
	}
	return "http://127.0.0.1:" + port
}

// webBridgeRequest is the daemon's POST /command body. session is a TOP-LEVEL
// field (not inside args) — one task == one session == one Chrome tab group.
type webBridgeRequest struct {
	Action  string                 `json:"action"`
	Args    map[string]interface{} `json:"args,omitempty"`
	Session string                 `json:"session"`
}

// WebBridgeProxy talks to the Kimi WebBridge daemon over HTTP. Stateless: the
// daemon is the source of truth for tab/session state.
type WebBridgeProxy struct {
	client *http.Client
}

func NewWebBridgeProxy() *WebBridgeProxy {
	return &WebBridgeProxy{client: &http.Client{Timeout: commandTimeout}}
}

// Execute POSTs one command and returns the daemon's raw JSON response body
// verbatim. We pass the body through untouched so the agent sees the daemon's
// real envelope ({"ok":...,"data":...}) rather than a lossy re-shape.
func (p *WebBridgeProxy) Execute(session, action string, args map[string]interface{}) (string, error) {
	body, err := json.Marshal(webBridgeRequest{Action: action, Args: args, Session: session})
	if err != nil {
		return "", fmt.Errorf("marshal request: %w", err)
	}

	req, err := http.NewRequest(http.MethodPost, webbridgeBaseURL()+"/command", bytes.NewReader(body))
	if err != nil {
		return "", fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := p.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("WebBridge daemon (:10086) unreachable: %w — start it manually with `%s`, then retry (we never auto-start it: :10086 is owned by the Kimi app)", err, webbridgeStartHint)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("read WebBridge response: %w", err)
	}
	// A non-2xx status is a transport/daemon-level failure (400 malformed, 500 crash,
	// empty body). Surface it as an error instead of passing a non-envelope body through
	// as if it succeeded — responseIsError only understands the {"ok":bool} envelope.
	if resp.StatusCode >= 400 {
		return "", fmt.Errorf("WebBridge daemon returned HTTP %d: %s", resp.StatusCode, string(respBody))
	}
	return string(respBody), nil
}

// responseIsError reports whether a daemon response body signals failure. The
// daemon wraps successes as {"ok":true,...}; a present ok:false means failure.
// Unparseable/other bodies are treated as non-errors (passed through).
func responseIsError(raw string) bool {
	var env struct {
		OK *bool `json:"ok"`
	}
	if err := json.Unmarshal([]byte(raw), &env); err != nil {
		return false
	}
	return env.OK != nil && !*env.OK
}

// Status queries GET /status. It returns the raw status body, whether the
// daemon is fully healthy (up AND browser extension connected), and any
// transport error. Health requires BOTH running and extension_connected —
// commands fail silently when the extension is detached.
func (p *WebBridgeProxy) Status() (raw string, healthy bool, err error) {
	client := &http.Client{Timeout: statusTimeout}
	resp, err := client.Get(webbridgeBaseURL() + "/status")
	if err != nil {
		return "", false, err
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var st struct {
		Running            bool `json:"running"`
		ExtensionConnected bool `json:"extension_connected"`
	}
	_ = json.Unmarshal(body, &st)
	healthy = resp.StatusCode == http.StatusOK && st.Running && st.ExtensionConnected
	return string(body), healthy, nil
}
