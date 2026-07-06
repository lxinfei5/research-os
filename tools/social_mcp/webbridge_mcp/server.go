package main

import (
	"context"
	"crypto/subtle"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/modelcontextprotocol/go-sdk/mcp"
	"github.com/sirupsen/logrus"
)

// authMiddleware gates /mcp behind a shared-secret bearer token when ROS_WEBBRIDGE_TOKEN is set
// (W-05/#3). webbridge-mcp exposes evaluate (arbitrary JS in any login-gated tab) and cdp (raw
// Chrome DevTools Protocol) against the user's REAL Chrome — without a token any local process
// (malware, a compromised dependency) could drive it and exfiltrate every logged-in session. The
// token is opt-in (loopback binding still applies): set ROS_WEBBRIDGE_TOKEN and mirror it in the
// .mcp.json `headers.Authorization` so MCP clients authenticate. /health stays open for the daemon
// manager's polling.
func authMiddleware() gin.HandlerFunc {
	token := os.Getenv("ROS_WEBBRIDGE_TOKEN")
	if token == "" {
		logrus.Warn("ROS_WEBBRIDGE_TOKEN unset — /mcp is unauthenticated (loopback-only). Set a shared " +
			"secret and mirror it in .mcp.json headers.Authorization to require a bearer token (the " +
			"endpoint exposes evaluate/cdp against the user's REAL logged-in Chrome)")
		return func(c *gin.Context) { c.Next() }
	}
	want := "Bearer " + token
	return func(c *gin.Context) {
		if c.Request.URL.Path == "/health" {
			c.Next()
			return
		}
		if subtle.ConstantTimeCompare([]byte(c.GetHeader("Authorization")), []byte(want)) != 1 {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing or invalid bearer token"})
			return
		}
		c.Next()
	}
}

// WebBridgeMCPServer bundles the MCP server, its HTTP transport, and the proxy
// to the Kimi WebBridge daemon.
type WebBridgeMCPServer struct {
	mcpServer  *mcp.Server
	httpServer *http.Server
	proxy      *WebBridgeProxy
}

func NewWebBridgeMCPServer() *WebBridgeMCPServer {
	s := &WebBridgeMCPServer{proxy: NewWebBridgeProxy()}
	s.mcpServer = mcp.NewServer(
		&mcp.Implementation{Name: "webbridge-mcp", Version: "1.0.0"},
		nil,
	)
	registerTools(s.mcpServer, s.proxy)
	return s
}

// Start serves the MCP endpoint (/mcp) plus a /health probe, and blocks until
// SIGINT/SIGTERM.
func (s *WebBridgeMCPServer) Start(port string) error {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(authMiddleware(), gin.Logger(), gin.Recovery())

	// /health reflects the UNDERLYING WebBridge daemon, not just this process:
	// a healthy webbridge-mcp is useless if :10086 is down or the extension is
	// detached. The daemon manager polls this.
	router.GET("/health", func(c *gin.Context) {
		raw, healthy, err := s.proxy.Status()
		switch {
		case err != nil:
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"status": "degraded", "webbridge": "unreachable", "error": err.Error(),
			})
		case !healthy:
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"status": "degraded", "webbridge": "up_but_extension_detached", "status_raw": raw,
			})
		default:
			c.JSON(http.StatusOK, gin.H{"status": "healthy", "webbridge": "connected"})
		}
	})

	// Streamable HTTP MCP transport. JSONResponse:true returns application/json
	// for POSTs (simplest for agent clients); matches xiaohongshu-mcp.
	mcpHandler := mcp.NewStreamableHTTPHandler(
		func(r *http.Request) *mcp.Server { return s.mcpServer },
		&mcp.StreamableHTTPOptions{JSONResponse: true},
	)
	router.Any("/mcp", gin.WrapH(mcpHandler))
	router.Any("/mcp/*path", gin.WrapH(mcpHandler))

	// ReadHeaderTimeout guards against slowloris on the header read. WriteTimeout is
	// intentionally unset: tool calls can legitimately take up to ~120s (page loads,
	// evaluate) and the transport may stream.
	s.httpServer = &http.Server{Addr: port, Handler: router, ReadHeaderTimeout: 10 * time.Second}
	go func() {
		if err := s.httpServer.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logrus.Fatalf("webbridge-mcp HTTP server error: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	logrus.Info("webbridge-mcp shutting down")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	return s.httpServer.Shutdown(ctx)
}
