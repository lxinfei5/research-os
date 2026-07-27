package main

import "testing"

// Policy no longer denies XHS hosts at the transport layer; keep a smoke check that
// the host-stem list still recognizes known origins (for optional diagnostics).
func TestXHSHostStemsRecognized(t *testing.T) {
	if len(xhsHostStems) == 0 {
		t.Fatal("xhsHostStems empty")
	}
	for _, want := range []string{"xiaohongshu.com", "xhslink.com"} {
		found := false
		for _, s := range xhsHostStems {
			if s == want {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("missing stem %q", want)
		}
	}
}
