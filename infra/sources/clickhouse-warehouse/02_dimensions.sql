CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_id UInt32,
    full_date Date,
    year UInt16,
    month UInt8,
    day UInt8,
    day_name String,
    quarter UInt8
) ENGINE = TinyLog;

CREATE TABLE IF NOT EXISTS warehouse.dim_product (
    tenant_id UInt32,
    product_id UInt32,
    name String,
    category String,
    base_price Decimal(12,2),
    tax_percentage Decimal(5,2)
) ENGINE = ReplacingMergeTree()
ORDER BY (tenant_id, product_id);

CREATE TABLE IF NOT EXISTS warehouse.dim_customer (
    tenant_id UInt32,
    customer_id UInt32,
    segment String,
    city String,
    customer_type String
) ENGINE = ReplacingMergeTree()
ORDER BY (tenant_id, customer_id);

CREATE TABLE IF NOT EXISTS warehouse.dim_employee (
    tenant_id UInt32,
    employee_id UInt32,
    position String,
    sectional_id UInt32
) ENGINE = ReplacingMergeTree()
ORDER BY (tenant_id, employee_id);

CREATE TABLE IF NOT EXISTS warehouse.dim_sectional (
    tenant_id UInt32,
    sectional_id UInt32,
    name String,
    city String
) ENGINE = ReplacingMergeTree()
ORDER BY (tenant_id, sectional_id);

CREATE TABLE IF NOT EXISTS warehouse.dim_payment_method (
    method_id UInt8,
    name String,
    type String
) ENGINE = TinyLog;