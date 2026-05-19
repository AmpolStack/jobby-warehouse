
GET_ANNUAL_GROWTH_QUERY = """
WITH yearly_sales AS (
    SELECT 
        d.year,
        SUM(f.total_line) AS total_sales
    FROM fact_sales_line f
    JOIN dim_date d ON f.date_id = d.date_id
    GROUP BY d.year
)
SELECT 
    current.year,
    current.total_sales,
    prev.total_sales AS prev_year_sales,
    (current.total_sales - prev.total_sales) / NULLIF(prev.total_sales, 0) * 100 AS growth_percent
FROM yearly_sales current
LEFT JOIN yearly_sales prev ON current.year = prev.year + 1
ORDER BY current.year
"""

GET_CONTRIBUTION_PER_SECTIONAL_QUERY = """
SELECT 
    s.name AS sectional_name,
    SUM(f.total_line) AS total_sales,
    (SUM(f.total_line) / SUM(SUM(f.total_line)) OVER()) * 100 AS contribution_percent
FROM fact_sales_line f
JOIN dim_sectional s ON f.sectional_id = s.sectional_id AND f.tenant_id = s.tenant_id
GROUP BY s.name
ORDER BY total_sales DESC;
"""

GET_PRODUCTIVITY_PER_EMPLOYEE_QUERY = """
SELECT 
    e.employee_id,
    e.position,
    COUNT(DISTINCT f.invoice_id) AS num_invoices,
    SUM(f.total_line) AS total_sales,
    AVG(f.total_line) AS avg_ticket_per_sale
FROM fact_sales_line f
JOIN dim_employee e ON f.employee_id = e.employee_id AND f.tenant_id = e.tenant_id
GROUP BY e.employee_id, e.position
ORDER BY total_sales DESC
LIMIT 50;
"""

GET_MONTHLY_EVOLUTION_QUERY = """
SELECT 
    d.year,
    d.month,
    SUM(f.total_line) AS monthly_sales
FROM fact_sales_line f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year, d.month
ORDER BY d.year, d.month;
"""

GET_TOP_PRODUCTS_QUERY = """
SELECT 
    p.name AS product_name,
    p.category,
    SUM(f.total_line) AS revenue,
    SUM(f.quantity) AS units_sold
FROM fact_sales_line f
JOIN dim_product p ON f.product_id = p.product_id AND f.tenant_id = p.tenant_id
GROUP BY p.name, p.category
ORDER BY revenue DESC
LIMIT 10;
"""

GET_POPULAR_PAYMENT_METHODS_QUERY = """
SELECT 
    pm.name AS payment_method,
    pm.type,
    COUNT(DISTINCT f.invoice_id) AS transaction_count,
    SUM(f.total_line) AS total_amount
FROM fact_sales_line f
JOIN dim_payment_method pm ON f.payment_method_id = pm.method_id
GROUP BY pm.name, pm.type
ORDER BY total_amount DESC;
"""

GET_AVERAGE_TICKET_PER_SECTIONAL_AND_MONTH_QUERY = """
SELECT 
    s.name AS sectional,
    d.year,
    d.month,
    AVG(f.total_line) AS avg_ticket,
    SUM(f.total_line) / COUNT(DISTINCT f.invoice_id) AS avg_per_invoice
FROM fact_sales_line f
JOIN dim_sectional s ON f.sectional_id = s.sectional_id AND f.tenant_id = s.tenant_id
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY s.name, d.year, d.month
ORDER BY s.name, d.year, d.month;
"""