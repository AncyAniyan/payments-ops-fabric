CREATE TABLE [dbo].[dim_date] (
    [date]       DATE         NULL,
    [year]       INT          NULL,
    [month_no]   INT          NULL,
    [month_name] VARCHAR (20) NULL,
    [year_month] VARCHAR (7)  NULL,
    [day_no]     INT          NULL,
    [day_name]   VARCHAR (20) NULL,
    [is_weekend] INT          NOT NULL
);


GO