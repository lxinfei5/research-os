package main

import "testing"

func TestXHSDeniedURL(t *testing.T) {
	deny := []string{
		"https://www.xiaohongshu.com/explore/abc",
		"https://xiaohongshu.com/search_result?keyword=x",
		"https://xhslink.com/a/abc",
		"https://www.xhs.cn/note/1",
		"https://rednote.com/note/1",
		"https://fe-video-upload.xhscdn.com/foo",
	}
	for _, u := range deny {
		if host, d := xhsDeniedURL(u); !d {
			t.Errorf("expected DENY for %q, got allow", u)
		} else if host == "" {
			t.Errorf("denied but empty host for %q", u)
		}
	}
	allow := []string{
		"https://www.example.com/foo",
		"https://example.com/xiaohongshu-review",  // path contains stem, host does not
		"https://x.com/search?q=x",
		"https://www.douyin.com/search/x",
		"",            // empty -> not a navigation
		"not a url",   // no host -> daemon judges
	}
	for _, u := range allow {
		if _, d := xhsDeniedURL(u); d {
			t.Errorf("expected ALLOW for %q, got deny", u)
		}
	}
}

func TestIsLoopbackAddr(t *testing.T) {
	loopback := []string{"127.0.0.1:18061", "localhost:18061", "[::1]:18061"}
	for _, a := range loopback {
		if !isLoopbackAddr(a) {
			t.Errorf("expected %q to be loopback", a)
		}
	}
	notLoopback := []string{
		"0.0.0.0:18061",  // all interfaces
		":18061",         // empty host == all interfaces
		"192.168.1.5:18061",
		"example.com:18061",
	}
	for _, a := range notLoopback {
		if isLoopbackAddr(a) {
			t.Errorf("expected %q to be NON-loopback (should fatal-exit)", a)
		}
	}
}
