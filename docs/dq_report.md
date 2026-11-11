# Data-quality report — Payments Ops — run of 2026-11-11
**Bottom line:** Core payments and events data are 100% valid and consistent. Rail settlement contains 25 duplicate records on end_to_end_id (PDQ-08 FAILS), which must be deduplicated in PAY-4 before reconciliation.

| Check | Rule | Failed rows | % failed | Status | Decision |
|---|---|---|---|---|---|
| PDQ-01 | payment_id is unique | 0 | 0.00% | PASS | Accept |
| PDQ-02 | amount_sar is positive | 0 | 0.00% | PASS | Accept |
| PDQ-03 | IPS amount within SAR 20,000 cap unless rejected AM02 | 0 | 0.00% | PASS | Accept |
| PDQ-04 | every event belongs to a known payment | 0 | 0.00% | PASS | Accept |
| PDQ-05 | event timestamps never go backwards within a payment | 0 | 0.00% | PASS | Accept |
| PDQ-06 | final_status equals the last event | 0 | 0.00% | PASS | Accept |
| PDQ-07 | rejected payments have a reason code | 0 | 0.00% | PASS | Accept |
| PDQ-08 | rail report end_to_end_id is unique | 25 | 0.02% | FAIL | Deduplicate by keeping latest settlement_date before PAY-4 |
| PDQ-09 | final_status_at is on or after initiated_at | 0 | 0.00% | PASS | Accept |
| PDQ-10 | SWIFT payment currency is foreign (not SAR) | 0 | 0.00% | PASS | Accept |

## Top 3 issues by business impact
1. Rail settlement duplicate records (PDQ-08) — 25 rows — Duplicate settlement entries cause false reconciliation breaks — Deduplicate in PAY-4 reconciliation logic.
2. Rejected payments missing reason codes (PDQ-07) — 0 rows (monitored) — Missing reasons block customer dispute resolution — Blocking gate on ingest.
3. Event timestamp sequence (PDQ-05) — 0 rows (monitored) — Out-of-order events distort payment turnaround SLA tracking — Monitored on event streams.

## Recommendations
- Run checks PDQ-01 through PDQ-10 automatically on daily lakehouse ingestion.
- Upstream rail settlement ingest should be fixed by integration team to prevent duplicate sends.
- Block the daily reconciliation job if PDQ-01 through PDQ-07 fail.