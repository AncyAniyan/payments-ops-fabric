# Payments Operations Domain Notes
**Project B:** Payments Operations & Reconciliation (Psh-style on Microsoft Fabric)  
**Author:** Ancy Aniyan  
**Date:** 2026-11-05  

---

## 1. The Three Payment Rails

In this payment hub, transactions move across three distinct clearing networks (rails), each governed by specific operational rules, operating hours, and transaction limits:

| Rail | Name & Type | Target Segment | Operating Hours & Schedule | Transaction Cap | Settlement Speed |
|---|---|---|---|---|---|
| **IPS** | Instant Payment System | Retail & low-value corporate | 24 hours / 7 days / 365 days | **SAR 20,000** per payment | Real-time (seconds) |
| **SARIE** | Saudi Arabian Riyal Interbank Express (RTGS) | High-value corporate & interbank | Sunday – Thursday, 08:00 – 15:58 (cut-off) | No upper cap | Same-day (gross settlement during window) |
| **SWIFT** | Society for Worldwide Interbank Financial Telecommunication | Cross-border wires | Global network, business days | No cap (multi-currency) | Multi-hour to T+1/T+2 days |

### SARIE Cut-off & Weekend Window
- **Operating Window:** Sunday to Thursday from 08:00 to 15:58.
- **Outside-Window Handling:** Any SARIE payment initiated **after 15:58** on a business day, or anytime on **Friday or Saturday** (Saudi weekend), cannot settle immediately. It is placed on hold (`ON_HOLD` with reason `CUTOFF` or `WEEKEND`) until 08:00 on the next business morning.
- **Treasury Impact:** Liquidity managers must monitor SARIE queues closely before 15:58 to ensure sufficient central bank (SAMA) reserve balances.

---

## 2. Payment Status Lifecycle & Grain

A payment's lifecycle moves through discrete stages. The data architecture splits this into two tables:

1. **`pay.payments` (Master / Header — 1 row per payment):**
   - Captures the complete payment attributes (`payment_id`, `amount_sar`, `rail`, `direction`, `channel`, etc.) and its **`final_status`** (`SETTLED`, `REJECTED`, etc.).
2. **`pay.payment_events` (Audit Trail / Lifecycle log — multiple rows per payment):**
   - Captures each chronological status change with a sequence number (`seq`), timestamp (`event_ts`), and detail code.

### Lifecycle Flow
```text
                    [ INITIATED ]
                          │
                          ▼
                    [ VALIDATED ] ─── (Validation error) ───► [ REJECTED ]
                          │
            ┌─────────────┴─────────────┐
            │                           │
   (Sanctions / Limit hit)      (Clean transaction)
            ▼                           ▼
       [ ON_HOLD ]                   [ SENT ]
            │                           │
     ┌──────┴──────┐                    │
 (Cleared)    (Blocked)                 │
     ▼             ▼                    ▼
[ RELEASED ]  [ REJECTED ]      ┌───────┴───────┐
     │                          │               │
     └──────────► [ SENT ] ──► [ SETTLED ]   [ REJECTED ]
```

---

## 3. Straight-Through Processing (STP)

- **Definition:** Straight-Through Processing (STP) means a payment flows from initiation to final settlement completely automatically, without manual repair, compliance intervention, or queue stoppage.
- **`is_stp = TRUE`**: Payment moved directly (`INITIATED` → `VALIDATED` → `SENT` → `SETTLED`) with no `ON_HOLD` event.
- **`is_stp = FALSE`**: Payment was delayed by an `ON_HOLD` event (e.g. sanctions alert, SARIE cut-off queue) or required manual repair.
- **Key Metric:** Higher STP rates reduce operational overhead and ensure customer SLA compliance.

---

## 4. Ledger vs. Rail Settlement Reconciliation

Every day, Payments Operations must reconcile the internal bank ledger (`pay.payments`) against the external clearing rail settlement report (`pay.rail_settlement`).

Discrepancies (breaks) occur for five primary operational reasons:

1. **Timing Break (In-Flight across Cut-off / Midnight):**
   The bank sent the payment at 15:57 or 23:58, but the rail settles it on the following calendar/business day.
2. **Amount Variance:**
   The settled amount in the rail differs from the initiated amount due to intermediary bank charges, handling fees, or foreign exchange rate variations.
3. **Missing in Rail (Dropped / Unacknowledged):**
   The internal ledger shows `SENT`, but the rail report contains no matching `end_to_end_id`. Indicates a stuck message or network timeout.
4. **Missing in Ledger (Unposted / Unsolicited Credit):**
   The rail settled funds into the bank's account, but the internal core banking system failed to ingest or post the transaction.
5. **Duplicate Rail Settlement:**
   The rail report contains duplicate settlement rows for the same `end_to_end_id`, requiring investigation with the clearing house.
