# Reconciliation report — Ledger vs Rail Settlement — run of 2026-11-12
**Bottom line:** 99.3% of settled payments (119,459 items) match perfectly between the bank ledger and rail clearing statements. 766 break items were identified, categorized, and flagged for operational exception handling before executive reporting.

## Method
Compared internal bank ledger settled payments against central clearing rail reports (SARIE, IPS, SWIFT) using a FULL OUTER JOIN on `end_to_end_id`. Settlement dates were standardized to date format and duplicate rail reports were ranked and isolated.

## Results
| Category | Number of Items | Description / Action |
|---|---|---|
| matched | 119,459 | 100% agreement on amount and settlement date. Fully reconciled. |
| missing_in_rail | 295 | Marked settled in bank ledger but missing in rail report. Tracing required with clearing house. |
| date_mismatch | 239 | Amounts agree, but dates differ by 1 business day (intraday / cut-off transit timing). |
| amount_mismatch | 167 | Amounts differ between ledger and rail. Tracing bank fees and partial settlements. |
| missing_in_ledger | 40 | Cleared by rail network but unrecorded in bank ledger. Investigating unposted transactions. |
| duplicate_in_rail | 25 | Duplicate settlement records received from rail network (identified via PDQ-08). |
| **Total Items** | **120,225** | |

## Breaks by Category & Root Cause
1. **Missing in Rail (295 items):** Payments where bank ledger logged settlement but the rail settlement file did not confirm. Likely causes include delayed rail clearing files or network dropouts during batch generation.
2. **Date Mismatch (239 items):** Transactions initiated near the 15:58 cut-off window where bank ledger recorded date T and rail settlement cleared on T+1.
3. **Amount Mismatch (167 items):** Discrepancies primarily due to correspondent bank fee deductions on international SWIFT transfers.
4. **Missing in Ledger (40 items):** Rail clearing records without corresponding payment IDs, requiring investigation for unposted incoming transfers.
5. **Duplicate in Rail (25 items):** Upstream retry/re-transmission bugs from external rail partners creating duplicate records.

## Recommendations
- Automate daily T-SQL reconciliation in Microsoft Fabric Warehouse (`wh_payments.dbo.recon_items`) immediately after daily ingestion.
- Route `missing_in_rail` and `amount_mismatch` breaks into automated ticketing queues for Operations triage.
- Introduce automated date-tolerance rules (+1 business day) for after-hours transfers to reduce false operational noise.