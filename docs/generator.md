# Payments Dataset Generator & Reproducibility Verification

## 1. Overview
Synthetic payment data generator (`python/generate_payments.py`) simulating payment hub transactions for a Saudi commercial bank (Psh-style demo bank `PSHB` + 12 participant banks) across three payment rails:
- **IPS (Instant Payment System):** 24/7 instant retail/corporate payments, SAR 20,000 transaction cap.
- **SARIE (Saudi Arabian Riyal Interbank Express RTGS):** High-value interbank settlement, operational Sun–Thu 08:00–15:58 Saudi time (UTC+3).
- **SWIFT:** Cross-border multi-currency wire transfers (USD, EUR, GBP) with 13:00 cutoff.

## 2. Row Counts
- `banks.csv`: 13 rows
- `accounts.csv`: 6,000 rows
- `payments.csv`: 124,283 rows
- `payment_events.csv`: 484,400 rows
- `rail_settlement.csv`: 119,930 rows

## 3. Reproducibility Proof (MD5 Checksums)
Two independent generator runs with fixed seed `SEED = 2026` produced identical cryptographic checksums:

| File | MD5 Checksum | Verified |
|---|---|---|
| `data/payments/accounts.csv` | `067b87ac79628b08cf78eee5394e8b8b` | ✅ Identical |
| `data/payments/banks.csv` | `7e8133ae43b51183a4b648b40b345ec3` | ✅ Identical |
| `data/payments/payment_events.csv` | `6d5c7c13b19fda05370b94ea094f306a` | ✅ Identical |
| `data/payments/payments.csv` | `8ebefa1d57fa94a70885a103570d62f5` | ✅ Identical |
| `data/payments/rail_settlement.csv` | `f5f7394b22e8ddf5f689a098193a368a` | ✅ Identical |
