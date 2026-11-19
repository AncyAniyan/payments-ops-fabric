# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "c50657c6-dd3a-4403-aa05-79c509e542f6",
# META       "default_lakehouse_name": "lh_payments",
# META       "default_lakehouse_workspace_id": "c5ec6974-346f-4e14-b98a-feb43d84fb9a",
# META       "known_lakehouses": [
# META         {
# META           "id": "c50657c6-dd3a-4403-aa05-79c509e542f6"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

import os
import pandas as pd

# Load the Lakehouse payment files
BASE = "/lakehouse/default/Files/payments/"
pay = pd.read_csv(BASE + "payments.csv", parse_dates=["initiated_at", "sent_at", "final_status_at"])
ev = pd.read_csv(BASE + "payment_events.csv", parse_dates=["event_ts"])
rail = pd.read_csv(BASE + "rail_settlement.csv", parse_dates=["settlement_date"])

print("Payments:", len(pay), "| Events:", len(ev), "| Rail:", len(rail))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

checks = []
def check(check_id, name, failed, total):
    checks.append({
        "check_id": check_id, 
        "check_name": name, 
        "failed_rows": int(failed), 
        "total_rows": int(total),
        "status": "PASS" if failed == 0 else "FAIL"
    })

# Core checks (Appendix D.4)
check("PDQ-01", "payment_id is unique", pay["payment_id"].duplicated().sum(), len(pay))
check("PDQ-02", "amount_sar is positive", (pay["amount_sar"] <= 0).sum(), len(pay))
check("PDQ-03", "IPS amount within the SAR 20,000 cap unless rejected AM02",
      ((pay.rail == "IPS") & (pay.amount_sar > 20000) & (pay.reject_reason != "AM02")).sum(), (pay.rail == "IPS").sum())
check("PDQ-04", "every event belongs to a known payment", (~ev["payment_id"].isin(pay["payment_id"])).sum(), len(ev))

ev_sorted = ev.sort_values(["payment_id", "seq"])
backwards = (ev_sorted.groupby("payment_id")["event_ts"].diff().dt.total_seconds() < 0).sum()
check("PDQ-05", "event timestamps never go backwards within a payment", backwards, len(ev))

last = ev_sorted.groupby("payment_id").tail(1).set_index("payment_id")["status"]
mismatch = (pay.set_index("payment_id")["final_status"] != last.reindex(pay["payment_id"]).values)
check("PDQ-06", "final_status equals the last event",
      (mismatch & ~pay.set_index("payment_id")["final_status"].isin(["PENDING"])).sum(), len(pay))

check("PDQ-07", "rejected payments have a reason code",
      ((pay.final_status == "REJECTED") & pay.reject_reason.isna()).sum(), (pay.final_status == "REJECTED").sum())
check("PDQ-08", "rail report end_to_end_id is unique", rail["end_to_end_id"].duplicated().sum(), len(rail))

# 2 Custom checks
check("PDQ-09", "final_status_at is on or after initiated_at", (pay["final_status_at"] < pay["initiated_at"]).sum(), len(pay))
check("PDQ-10", "SWIFT payment currency is foreign (not SAR)", ((pay.rail == "SWIFT") & (pay.currency == "SAR")).sum(), (pay.rail == "SWIFT").sum())

result = pd.DataFrame(checks)
display(result)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import os
os.makedirs("/lakehouse/default/Files/dq", exist_ok=True)
result.to_csv("/lakehouse/default/Files/dq/dq_results.csv", index=False)
print("Saved dq_results.csv successfully!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Save DataFrame directly as a Delta table in the Lakehouse
spark.createDataFrame(result).write.format("delta").mode("overwrite").saveAsTable("dq_results")
print("Table dq_results created successfully!")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

