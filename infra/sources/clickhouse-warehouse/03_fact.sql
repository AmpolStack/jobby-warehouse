CREATE TABLE IF NOT EXISTS warehouse.fact_sales_line (
    tenant_id UInt32,
    line_id UInt64,
    invoice_id UInt32,
    date_id UInt32,
    product_id UInt32,
    customer_id UInt32,
    employee_id UInt32,
    sectional_id UInt32,
    payment_method_id UInt8,
    quantity Decimal(10,2),
    unit_price Decimal(12,2),
    subtotal Decimal(12,2),
    tax Decimal(12,2),
    discount Decimal(12,2),
    total_line Decimal(12,2)
) ENGINE = MergeTree()
ORDER BY (tenant_id, date_id)
PARTITION BY (tenant_id, toYYYYMM(toDate(date_id)));