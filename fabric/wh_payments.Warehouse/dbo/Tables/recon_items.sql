CREATE TABLE [dbo].[recon_items] (
    [end_to_end_id]          VARCHAR (8000) NULL,
    [rail]                   VARCHAR (8000) NULL,
    [ledger_amount_sar]      FLOAT (53)     NULL,
    [rail_amount_sar]        FLOAT (53)     NULL,
    [ledger_settlement_date] DATE           NULL,
    [rail_settlement_date]   DATE           NULL,
    [category]               VARCHAR (17)   NOT NULL
);


GO