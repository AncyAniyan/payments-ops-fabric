-- 01_pay_tables.sql : tables for the payments project (schema pay) in your local PostgreSQL
CREATE SCHEMA IF NOT EXISTS pay;
DROP TABLE IF EXISTS pay.banks, pay.accounts, pay.payments, pay.payment_events, pay.rail_settlement CASCADE;

CREATE TABLE pay.banks (bank_code text PRIMARY KEY, bank_name text, is_internal boolean);
CREATE TABLE pay.accounts (account_id text PRIMARY KEY, customer_type text, region text, iban text, opened_date date);
CREATE TABLE pay.payments (
  payment_id text PRIMARY KEY, end_to_end_id text UNIQUE, direction text, rail text, channel text,
  account_id text, customer_type text, counterparty_bank text, currency text,
  amount_original numeric(16,2), amount_sar numeric(16,2), initiated_at timestamp, sent_at timestamp,
  final_status text, final_status_at timestamp, reject_reason text, hold_reason text, is_stp boolean);
CREATE TABLE pay.payment_events (payment_id text, seq int, status text, event_ts timestamp, detail text,
  PRIMARY KEY (payment_id, seq));
-- the rail's report is loaded as received: no primary key, because it may contain duplicates
CREATE TABLE pay.rail_settlement (end_to_end_id text, rail text, direction text,
  settlement_date date, settled_amount_sar numeric(16,2));
