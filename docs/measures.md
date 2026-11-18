# DAX Measures Reference: Payments Operations (`sm_payments_ops`)

## Storage Mode: Direct Lake (Microsoft Fabric)
This semantic model queries physical tables in OneLake via Direct Lake mode, eliminating refresh schedules while maintaining in-memory VertiPaq speeds.

---

### Folder: 01 Volume & Value

#### `Payments`
Total volume of payments recorded.
```DAX
Payments = COUNTROWS ( payments_curated )
```

#### `Value SAR`
Total value of payments in Saudi Riyals (SAR).
```DAX
Value SAR = SUM ( payments_curated[amount_sar] )
```

#### `Final Outgoing`
Count of outgoing payments that have reached a final state (`SETTLED`, `REJECTED`, or `RETURNED`). Evaluates to 87,042 payments.
```DAX
Final Outgoing = CALCULATE ( [Payments], payments_curated[is_final_out] = 1 )
```

#### `Settled Value OUT`
Total value in SAR of outgoing payments that cleared successfully with final status `SETTLED`. Evaluates to 3,772,851,729.60 SAR (self-check N32).
```DAX
Settled Value OUT =
CALCULATE ( [Value SAR], payments_curated[direction] = "OUT", payments_curated[final_status] = "SETTLED" )
```

---

### Folder: 02 Performance & SLA

#### `STP Rate`
Straight-Through Processing (STP) rate for final outgoing payments. Measures the percentage of outgoing transfers executed end-to-end without manual intervention or holds. Evaluates to 96.5% (self-check N31).
```DAX
STP Rate = DIVIDE ( CALCULATE ( [Final Outgoing], payments_curated[is_stp] = TRUE () ), [Final Outgoing] )
```
*Format: Percentage, 1 decimal place.*

#### `Rejected`
Count of payments terminated with final status `REJECTED`.
```DAX
Rejected = CALCULATE ( [Payments], payments_curated[final_status] = "REJECTED" )
```

#### `Rejection Rate`
Percentage of total payments rejected across all rails. Evaluates to 3.2% (self-check N31).
```DAX
Rejection Rate = DIVIDE ( [Rejected], [Payments] )
```
*Format: Percentage, 1 decimal place.*

#### `Median Settle Seconds`
Median turnaround time (in seconds) between payment initiation (`SENT`) and final settlement (`SETTLED`). Evaluates to 8s on IPS, 660s on SARIE (self-check N34).
```DAX
Median Settle Seconds = MEDIAN ( settle_times[seconds_to_settle] )
```

#### `P95 Settle Seconds`
95th percentile turnaround time (in seconds). Captures tail latency and operational queue bottlenecks. Evaluates to 15s on IPS, 1,140s on SARIE.
```DAX
P95 Settle Seconds = PERCENTILE.INC ( settle_times[seconds_to_settle], 0.95 )
```

#### `SARIE Outside-Window Share`
Proportion of outgoing SARIE payments submitted outside the SARIE clearing window (Fridays, Saturdays, or after 15:58 cut-off Sun–Thu). Evaluates to 42.4% (drill S56).
```DAX
SARIE Outside-Window Share =
DIVIDE (
    CALCULATE ( [Payments], payments_curated[sarie_outside_window] = 1 ),
    CALCULATE ( [Payments], payments_curated[rail] = "SARIE", payments_curated[direction] = "OUT" )
)
```
*Format: Percentage, 1 decimal place.*

---

### Folder: 03 Reconciliation

#### `Recon Items`
Total reconciliation records evaluated between core banking ledger and payment rails. Evaluates to 120,016 items.
```DAX
Recon Items = COUNTROWS ( recon_items )
```

#### `Recon Breaks`
Count of reconciliation breaks (records where category is not `matched`). Includes `missing_in_rail` (295), `date_mismatch` (239), `amount_mismatch` (167), `missing_in_ledger` (40), and `duplicate_in_rail` (25). Total breaks: 766 items (self-check N33).
```DAX
Recon Breaks = CALCULATE ( [Recon Items], recon_items[category] <> "matched" )
```

---

### Self-Check Validation Evidence
- **N31 (STP & Rejection Rates):** STP Rate = 96.5%, Rejection Rate = 3.2% -> PASS
- **N32 (Settled Outgoing Value):** 3,772,851,729.60 SAR -> PASS
- **N33 (Reconciliation Counts):** Matched: 119,459 | Breaks: 766 -> PASS
- **N34 (Median Turnaround Seconds):** IPS: 8s | SARIE: 660s -> PASS
