CREATE TABLE [dbo].[payments_curated] (
    [payment_id]           VARCHAR (8000) NULL,
    [end_to_end_id]        VARCHAR (8000) NULL,
    [direction]            VARCHAR (8000) NULL,
    [rail]                 VARCHAR (8000) NULL,
    [channel]              VARCHAR (8000) NULL,
    [account_id]           VARCHAR (8000) NULL,
    [customer_type]        VARCHAR (8000) NULL,
    [counterparty_bank]    VARCHAR (8000) NULL,
    [currency]             VARCHAR (8000) NULL,
    [amount_original]      FLOAT (53)     NULL,
    [amount_sar]           FLOAT (53)     NULL,
    [initiated_at]         DATETIME2 (6)  NULL,
    [sent_at]              DATETIME2 (6)  NULL,
    [final_status]         VARCHAR (8000) NULL,
    [final_status_at]      DATETIME2 (6)  NULL,
    [reject_reason]        VARCHAR (8000) NULL,
    [hold_reason]          VARCHAR (8000) NULL,
    [is_stp]               BIT            NULL,
    [initiated_date]       DATE           NULL,
    [initiated_hour]       INT            NULL,
    [sarie_outside_window] INT            NOT NULL,
    [is_final_out]         INT            NOT NULL,
    [is_salary_day]        INT            NOT NULL
);


GO