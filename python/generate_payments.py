"""
generate_payments.py : synthetic payment data for a Saudi bank's payment hub (Psh-style).
Rails: IPS (instant, 24/7, SAR 20,000 cap), SARIE RTGS (Sun-Thu, cut-off 15:58), SWIFT (cross-border).
Everything is generated with Python's `random` module and a fixed seed, so every run is identical.

Run:    python generate_payments.py
Output: data/payments/banks.csv, accounts.csv, payments.csv, payment_events.csv, rail_settlement.csv
Times are Saudi local time (UTC+3). Amounts are in SAR (SWIFT also keeps the original currency).
NOTE: the hold times, SWIFT cut-off (13:00) and failure rates are DESIGN ASSUMPTIONS for practice data.
"""
import csv
import math
import os
import random
from datetime import date, datetime, time, timedelta

SEED = 2026
START = date(2026, 7, 1)
DAYS = 92                                   # 1 Jul - 30 Sep 2026
END_TS = datetime(2026, 9, 30, 23, 59, 59)
OUT_DIR = "data/payments"
IPS_CAP = 20000.00
SARIE_OPEN, SARIE_CUTOFF = time(8, 0), time(15, 58)
SWIFT_CUTOFF = time(13, 0)
FX = {"USD": 3.75, "EUR": 4.10, "GBP": 4.75}

random.seed(SEED)
os.makedirs(OUT_DIR, exist_ok=True)

BANKS = [("PSHB", "Psh Demo Bank (us)", True)] + [
    (f"BK{i:02d}", n, False) for i, n in enumerate(
        ["Alpha National Bank", "Desert Commercial Bank", "Red Sea Bank", "Najd Investment Bank",
         "Gulf Unity Bank", "Hijaz Savings Bank", "Eastern Trade Bank", "Oasis Islamic Bank",
         "Summit Bank", "Crescent Bank", "Palm Finance Bank", "Horizon Bank"], start=1)]
REGIONS = ["Riyadh", "Makkah", "Eastern Province", "Madinah", "Qassim", "Asir", "Tabuk", "Jazan"]
REGION_W = [32, 26, 16, 8, 6, 5, 4, 3]


def pick(options, weights):
    return random.choices(options, weights=weights, k=1)[0]


def lognormal(median, sigma):
    return median * math.exp(random.gauss(0, sigma))


def is_business_day(d):           # Saudi weekend: Friday (4) and Saturday (5)
    return d.weekday() not in (4, 5)


def next_open(ts, open_t, cutoff_t):
    """Earliest moment the rail accepts a payment initiated at ts."""
    d = ts.date()
    if is_business_day(d) and open_t <= ts.time() <= cutoff_t:
        return ts, None
    reason = "CUTOFF" if is_business_day(d) and ts.time() > cutoff_t else ("WEEKEND" if not is_business_day(d) else "BEFORE_OPEN")
    if not (is_business_day(d) and ts.time() < open_t):
        d += timedelta(days=1)
    while not is_business_day(d):
        d += timedelta(days=1)
    return datetime.combine(d, open_t) + timedelta(minutes=random.randint(0, 25)), reason


# ---------- accounts ----------
accounts = []
for i in range(1, 6001):
    ctype = "CORPORATE" if random.random() < 0.15 else "RETAIL"
    accounts.append({"account_id": f"A{i:05d}", "customer_type": ctype, "region": pick(REGIONS, REGION_W),
                     "iban": "SA" + "".join(random.choices("0123456789", k=22)),
                     "opened_date": (date(2015, 1, 1) + timedelta(days=random.randint(0, 4000))).isoformat()})

# ---------- payments + events ----------
payments, events = [], []
pid = 0
for day in range(DAYS):
    d = START + timedelta(days=day)
    base = 1400 if is_business_day(d) else 900
    if d.day in (25, 26, 27):
        base *= 1.7
    n_today = int(base * random.uniform(0.9, 1.1))
    for _ in range(n_today):
        pid += 1
        acc = random.choice(accounts)
        corp = acc["customer_type"] == "CORPORATE"
        direction = "OUT" if random.random() < 0.70 else "IN"
        rail = pick(["IPS", "SARIE", "SWIFT"], [40, 45, 15] if corp else [82, 12, 6])
        if direction == "OUT":
            channel = pick(["CORPORATE_API", "WEB", "BRANCH"], [55, 40, 5]) if corp else pick(["MOBILE", "WEB", "BRANCH"], [70, 25, 5])
        else:
            channel = "NETWORK"
        hour = pick(list(range(24)), ([1] * 7 + [4, 9, 10, 10, 9, 8, 7, 6, 4, 2, 1] + [1] * 6) if corp else
                    [1, 1, 1, 1, 1, 2, 3, 5, 7, 8, 8, 8, 7, 6, 6, 6, 6, 6, 7, 8, 8, 7, 4, 2])
        init = datetime.combine(d, time(hour, random.randint(0, 59), random.randint(0, 59)))
        currency, amount_orig = "SAR", None
        if rail == "IPS":
            amt = lognormal(4000 if corp else 450, 0.9)
            if random.random() < 0.015 and direction == "OUT":
                amt = random.uniform(20000.01, 60000)       # customer tries to exceed the IPS cap
            elif amt > IPS_CAP:
                amt = random.uniform(5000, IPS_CAP)
        elif rail == "SARIE":
            amt = lognormal(250000 if corp else 25000, 1.0)
        else:
            currency = pick(["USD", "EUR", "GBP"], [70, 20, 10])
            amount_orig = round(lognormal(60000 if corp else 8000, 0.9), 2)
            amt = amount_orig * FX[currency]
        amt = round(max(amt, 1.0), 2)
        bank = random.choice(BANKS[1:])[0]
        p = {"payment_id": f"P{pid:08d}", "end_to_end_id": f"E2E{pid:010d}", "direction": direction, "rail": rail,
             "channel": channel, "account_id": acc["account_id"], "customer_type": acc["customer_type"],
             "counterparty_bank": bank, "currency": currency,
             "amount_original": amount_orig if amount_orig is not None else amt, "amount_sar": amt,
             "initiated_at": init, "is_stp": True, "hold_reason": None, "reject_reason": None,
             "sent_at": None, "final_status": None, "final_status_at": None}
        ev = []

        def add(status, ts, detail=None):
            ev.append((p["payment_id"], len(ev) + 1, status, ts, detail))

        t = init
        if direction == "OUT":
            add("INITIATED", t)
            t += timedelta(seconds=random.randint(1, 4))
            r = random.random()
            reject = None
            if rail == "IPS" and amt > IPS_CAP:
                reject = "AM02"                                   # amount exceeds allowed maximum
            elif r < 0.008:
                reject = "AC01"                                   # incorrect account number
            elif r < 0.011:
                reject = "AC04"                                   # closed account
            elif r < 0.026:
                reject = "AM04"                                   # insufficient funds
            elif r < 0.028:
                reject = "DUPL"                                   # duplicate payment
            if reject:
                add("REJECTED", t, reject)
                p.update(reject_reason=reject, final_status="REJECTED", final_status_at=t)
            else:
                add("VALIDATED", t)
                # manual repair (not straight-through)
                if random.random() < {"IPS": 0.02, "SARIE": 0.06, "SWIFT": 0.15}[rail]:
                    p["is_stp"] = False
                    add("ON_HOLD", t, "REPAIR")
                    t += timedelta(minutes=random.randint(20, 120))
                    add("RELEASED", t, "REPAIR")
                # compliance / sanctions screening hold
                if random.random() < {"IPS": 0.001, "SARIE": 0.005, "SWIFT": 0.04}[rail]:
                    p["hold_reason"] = "COMPLIANCE"
                    add("ON_HOLD", t, "COMPLIANCE")
                    t += timedelta(minutes=max(5, int(lognormal(180, 0.8))))
                    if t > END_TS:
                        p.update(final_status="PENDING", final_status_at=ev[-1][3])
                    else:
                        add("RELEASED", t, "COMPLIANCE")
                if p["final_status"] is None:
                    # rail operating hours
                    if rail in ("SARIE", "SWIFT"):
                        opened, why = next_open(t, SARIE_OPEN, SARIE_CUTOFF if rail == "SARIE" else SWIFT_CUTOFF)
                        if why:
                            p["hold_reason"] = p["hold_reason"] or why
                            add("ON_HOLD", t, why)
                            t = opened
                            add("RELEASED", t, why)
                    if t > END_TS:
                        p.update(final_status="PENDING", final_status_at=ev[-1][3])
                    else:
                        t += timedelta(seconds=random.randint(1, 3) if rail == "IPS" else random.randint(20, 300))
                        add("SENT", t)
                        p["sent_at"] = t
                        rail_reject = random.random() < {"IPS": 0.006, "SARIE": 0.003, "SWIFT": 0.01}[rail]
                        if rail == "IPS":
                            t += timedelta(seconds=random.randint(2, 15))
                        elif rail == "SARIE":
                            t += timedelta(minutes=random.randint(1, 20))
                        else:
                            t += timedelta(hours=random.randint(2, 40))
                            while not is_business_day(t.date()):
                                t += timedelta(days=1)
                        if t > END_TS:
                            p.update(final_status="SENT", final_status_at=p["sent_at"])
                        elif rail_reject:
                            code = pick(["AC01", "AC04", "RR04"], [50, 30, 20])
                            add("REJECTED", t, code)
                            p.update(reject_reason=code, final_status="REJECTED", final_status_at=t)
                        else:
                            add("SETTLED", t)
                            p.update(final_status="SETTLED", final_status_at=t)
                            if random.random() < 0.003:
                                rt = t + timedelta(days=random.randint(1, 5), hours=random.randint(0, 8))
                                if rt <= END_TS:
                                    add("RETURNED", rt, pick(["AC04", "MD07", "CUST"], [40, 30, 30]))
                                    p.update(final_status="RETURNED", final_status_at=rt)
        else:  # incoming
            add("RECEIVED", t)
            t += timedelta(seconds=random.randint(1, 5))
            if random.random() < 0.005:
                code = pick(["AC01", "AC04"], [60, 40])
                add("REJECTED", t, code)
                p.update(reject_reason=code, final_status="REJECTED", final_status_at=t)
            else:
                add("VALIDATED", t)
                t += timedelta(seconds=random.randint(1, 30))
                add("SETTLED", t)
                p.update(final_status="SETTLED", final_status_at=t)
        payments.append(p)
        events.extend(ev)

# ---------- rail settlement report (what the rail / correspondent says) ----------
manifest = {"missing_in_rail": 0, "extra_in_rail": 0, "amount_mismatch": 0, "date_mismatch": 0, "duplicate_in_rail": 0}
rail_rows = [p for p in payments if p["final_status"] in ("SETTLED", "RETURNED")]
settled_at = {}
for (payment_id, seq, status, ts, detail) in events:
    if status == "SETTLED":
        settled_at[payment_id] = ts
report = []
for p in rail_rows:
    r = random.random()
    sdate = settled_at[p["payment_id"]].date()
    amount = p["amount_sar"]
    if r < 0.0025:
        manifest["missing_in_rail"] += 1
        continue
    elif r < 0.0040:
        amount = round(amount - random.randint(15, 75), 2)
        manifest["amount_mismatch"] += 1
    elif r < 0.0060:
        sdate = sdate + timedelta(days=1)
        manifest["date_mismatch"] += 1
    report.append({"end_to_end_id": p["end_to_end_id"], "rail": p["rail"], "direction": p["direction"],
                   "settlement_date": sdate.isoformat(), "settled_amount_sar": f"{amount:.2f}"})
for i in range(40):
    manifest["extra_in_rail"] += 1
    report.append({"end_to_end_id": f"E2E9{i:09d}", "rail": pick(["IPS", "SARIE", "SWIFT"], [70, 20, 10]),
                   "direction": "IN", "settlement_date": (START + timedelta(days=random.randint(0, DAYS - 1))).isoformat(),
                   "settled_amount_sar": f"{random.uniform(100, 50000):.2f}"})
for row in random.sample(report[:-40], 25):
    manifest["duplicate_in_rail"] += 1
    report.append(dict(row))
random.shuffle(report)


# ---------- write files ----------
def ts(v):
    return v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime) else ("" if v is None else v)


def write(name, header, rows):
    with open(f"{OUT_DIR}/{name}", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


write("banks.csv", ["bank_code", "bank_name", "is_internal"], [(c, n, str(i).lower()) for c, n, i in BANKS])
write("accounts.csv", list(accounts[0].keys()), [a.values() for a in accounts])
pay_cols = ["payment_id", "end_to_end_id", "direction", "rail", "channel", "account_id", "customer_type",
            "counterparty_bank", "currency", "amount_original", "amount_sar", "initiated_at", "sent_at",
            "final_status", "final_status_at", "reject_reason", "hold_reason", "is_stp"]
write("payments.csv", pay_cols, [[ts(p[c]) if not isinstance(p[c], bool) else str(p[c]).lower() for c in pay_cols]
                                 for p in payments])
write("payment_events.csv", ["payment_id", "seq", "status", "event_ts", "detail"],
      [(a, b, c, ts(d), e or "") for a, b, c, d, e in events])
write("rail_settlement.csv", ["end_to_end_id", "rail", "direction", "settlement_date", "settled_amount_sar"],
      [r.values() for r in report])
print(f"payments {len(payments):,} | events {len(events):,} | rail report rows {len(report):,}")
