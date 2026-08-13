# Incident memo (do not ship as the user surface)

Synthetic checkout 5xx after a deploy. Same facts as `incident.ship.md`.

## 1. Problem restatement

Users cannot complete payment. Error rate on `POST /checkout` rose after 14:02.

## 2. Context / timeline

- 13:40 — CI green on payment-svc 1.14.2  
- 14:02 — canary then full roll  
- 14:06 — p99 200ms → 2.1s  
- 14:11 — on-call paged (synthetic)

## 3. Evidence (unsorted)

- Deploy of **payment-svc 1.14.2** at 14:02 (artifact: release diff).  
- Retry count on inventory client changed **1 → 5** (interface: config / OpenAPI timeout 800ms).  
- Logs: `inventory-client timeout` dominating 5xx (live).  
- Redis CPU ~40%, not saturated (live).  
- Primary DB connections in normal band (live).  
- Last-quarter similar shape was an inventory lock (library; dated).  

## 4. Hypotheses (equal weight)

1. Database saturation  
2. Redis eviction  
3. Bad deploy / code bug  
4. Inventory service outage  
5. Retry amplification  
6. Client-side double submit  
7. TLS / ingress  
8. “Could be all of the above”

## 5. Metrics dump

Error rate, p50/p95/p99, sat, CPU, memory, GC, QPS — all listed, none used to pick a lever.

## 6. Suggested next steps

- Keep gathering dashboards  
- Ask inventory team if they see load  
- Consider a rollback *or* a config change *or* a scale-up  
- Write a longer postmortem later  

## 7. Residuals

Many. None marked as flip vs noise.

## 8. Sources

Twelve links to graphs and log queries.

**Why this fails the contract:** the reader still has to name the key problem and the act.
