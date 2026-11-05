# Payments Operations & Reconciliation — Business Requirements Document (BRD)
Version: 0.5 — Draft for Review — 2026-11-05  
Owner: Ancy Aniyan (Data Analytics Consultant)  
Sponsor: Head of Payments Operations (Psh Demo Bank)

---

## 1. Background & Business Problem
Psh Demo Bank operates a high-throughput central payment hub processing approximately 1,350 transactions daily across three primary rails: **IPS** (Instant Payment System), **SARIE** (RTGS), and **SWIFT** (cross-border wires). 

Currently, operations teams lack real-time visibility into pipeline bottlenecks and stuck payments. Treasury struggles to predict end-of-day liquidity buffers due to post-cutoff SARIE queues, Compliance requires auditable hold times on sanctions screening, and Finance spends extensive manual effort investigating monthly reconciliation breaks against rail settlement reports. 

This project delivers a unified enterprise intelligence and control platform on **Microsoft Fabric** (Lakehouse, Warehouse T-SQL, pandas DQ notebooks, and Direct Lake Power BI) to automate operational reporting and daily ledger-vs-rail reconciliation.

---

## 2. Objectives & Measurable Success Criteria

| Objective | Success Criterion | Target Metric |
|---|---|---|
| **Trusted Payments Intelligence** | Centralized semantic model covering all 3 rails (IPS, SARIE, SWIFT) | 100% data model coverage, automated scheduled refresh |
| **Operational Bottleneck Tracking** | Visible status lifecycle from INITIATED to SETTLED/REJECTED | Median & p95 settlement SLA tracked per rail |
| **STP Rate Optimization** | Clear visibility into manual repairs and reason codes | Accurate STP rate baseline across channels and customer tiers |
| **Daily Financial Reconciliation** | Automated break categorization between internal ledger and rail reports | Daily break aging report with 100% accounted variance |
| **Sanctions & Compliance Governance** | Isolated hold tracking with role-restricted access | Dynamic RLS restricting customer-level compliance holds |

---

## 3. Scope

- **In Scope:**
  - Historical payments data spanning 1 Jul – 30 Sep 2026 (92 days, Saudi local time UTC+3).
  - 124,283 payments, 484,400 lifecycle events, 6,000 customer accounts, 13 participant banks, and 119,930 rail settlement rows.
  - Three settlement rails: IPS (instant, 24/7, SAR 20k cap), SARIE (RTGS Sun–Thu 08:00–15:58), and SWIFT (USD, EUR, GBP).
  - End-to-end Microsoft Fabric architecture: OneLake Lakehouse (Delta tables), PySpark/pandas DQ notebook, Fabric Warehouse T-SQL curated models, and Power BI Direct Lake App.
- **Out of Scope:**
  - Real-time Core Banking transaction posting or direct modification of payment gateway engine logic.

---

## 4. Stakeholders & RACI Matrix

| Stakeholder / Persona | Role | R | A | C | I |
|---|---|:---:|:---:|:---:|:---:|
| **Head of Payments Operations** | Executive Sponsor; requires stuck payment visibility & STP rates | | X | X | |
| **Treasury & Liquidity Manager** | Focuses on SARIE hourly outflow & post-cutoff liquidity requirements | | | X | X |
| **Compliance Officer** | Oversees sanctions holds, aging, and customer confidentiality | | | X | X |
| **Finance / Reconciliation Lead** | Requires daily ledger-vs-rail break categorization and aging | | | X | X |
| **BI Platform Owner** | Oversees Fabric DEV/TEST/PROD pipelines, Git, and refresh SLA | X | | X | |

*R = Responsible, A = Accountable, C = Consulted, I = Informed*

---

## 5. Key Performance Indicators (KPIs)

| KPI | Business Definition | Calculation / Grain |
|---|---|---|
| **Payment Volume & Value** | Total count and gross transaction value in SAR | Count / `SUM(amount_sar)` by rail, direction, channel, and hour |
| **Straight-Through Processing (STP)** | Percentage of outgoing payments settled without manual intervention | Outgoing settled/rejected with `is_stp = true` ÷ all outgoing |
| **Rejection Rate** | Proportion of payments failing validation or rail execution | Count of `REJECTED` payments ÷ total payments initiated |
| **Settlement Duration (SLA)** | Turnaround time from transmission to settlement | Seconds between `SENT` and `SETTLED` (median and p95) |
| **Outside-Window Share (SARIE)** | Volume queueing after RTGS cutoff or over weekends | Outgoing SARIE after 15:58 Sun–Thu or Fri/Sat ÷ total SARIE |
| **Compliance Hold Duration** | Time required to review and clear sanctions holds | Minutes between `ON_HOLD (COMPLIANCE)` and `RELEASED` |
| **Reconciliation Breaks** | Unmatched items between internal ledger and clearing rail | Count and value by category (`matched`, `missing_in_rail`, `missing_in_ledger`, `amount_mismatch`, `date_mismatch`, `duplicate_in_rail`) |

---

## 6. Functional Requirements

| ID | Requirement Description | Mapped Ticket |
|---|---|---|
| **FR-01** | Reproducible synthetic payment hub dataset with fixed seed and verifiable checksums | PAY-1 |
| **FR-02** | Lakehouse ingestion in OneLake as Delta tables with exact row count parity | PAY-2 |
| **FR-03** | Automated data quality test suite in a Fabric notebook validating status ordering and caps | PAY-3 |
| **FR-04** | Automated ledger-vs-rail reconciliation model categorizing all settlement discrepancies | PAY-4 |
| **FR-05** | Production curated T-SQL reporting tables (`payments_curated`, `settle_times`) | PAY-5 |
| **FR-06** | Direct Lake semantic model with standardized DAX measures and display folders | PAY-6 |
| **FR-07** | Executive and Operations Power BI App with multi-audience distribution | PAY-7 |
| **FR-08** | Dynamic Row-Level Security restricting compliance hold data to authorized compliance officers | PAY-8 |
| **FR-09** | Reference data maintenance via Dataflow Gen2 | PAY-9 |
| **FR-10** | Version control integration linking Fabric workspace to GitHub repository | PAY-10 |
| **FR-11** | Safe release promotion across DEV → TEST → PROD deployment pipelines | PAY-11 |
| **FR-12** | Documented refresh failure incident runbook and root-cause postmortem | PAY-12 |
| **FR-13** | Formal UAT test execution across ≥ 12 end-to-end test cases | PAY-13 |
| **FR-14** | Complete solution documentation, architecture diagram, and executive video | PAY-14 |

---

## 7. Non-Functional Requirements
- **Performance:** Interactive report page visual rendering < 3 seconds leveraging Fabric Direct Lake engine.
- **Reproducibility:** Pipeline executable end-to-end via versioned SQL and Python scripts with zero manual data entry.
- **Auditability:** Complete timestamp tracking on all payment state transitions in `payment_events`.
