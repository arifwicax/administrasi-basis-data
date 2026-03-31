# Implementasi PostgreSQL - Optimasi Query Panjang

## Week 7 - Administrasi Basis Data

---

## Setup Database untuk Demonstrasi Long Query

### 1. Membuat Database dan Tabel dengan Volume Data Besar

```sql
-- Membuat database untuk demonstrasi long query optimization
CREATE DATABASE db_long_query_demo;

-- Menggunakan database
\c db_long_query_demo;

-- Membuat tabel untuk sistem e-commerce (scenario realistis untuk long query)
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_code VARCHAR(20) UNIQUE NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    city VARCHAR(50),
    country VARCHAR(50),
    registration_date DATE DEFAULT CURRENT_DATE,
    customer_segment VARCHAR(20) DEFAULT 'Regular',
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel orders untuk transaction data
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(30) UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    payment_status VARCHAR(20) DEFAULT 'Pending',
    shipping_status VARCHAR(20) DEFAULT 'Processing',
    sales_rep_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel order_items untuk detail line items
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    discount_percentage NUMERIC(3,2) DEFAULT 0,
    line_total NUMERIC(12,2) NOT NULL
);

-- Tabel untuk sales representatives
CREATE TABLE sales_reps (
    sales_rep_id SERIAL PRIMARY KEY,
    rep_name VARCHAR(100) NOT NULL,
    rep_email VARCHAR(100) UNIQUE,
    department VARCHAR(50),
    hire_date DATE,
    target_annual NUMERIC(12,2),
    region VARCHAR(50)
);

-- Tabel untuk audit log (high volume data)
CREATE TABLE audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    operation VARCHAR(20), -- INSERT, UPDATE, DELETE
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET
);

-- Tabel untuk web analytics (very high volume)
CREATE TABLE web_analytics (
    analytics_id BIGSERIAL PRIMARY KEY,
    customer_id INTEGER,
    session_id VARCHAR(100),
    page_url TEXT,
    referrer_url TEXT,
    user_agent TEXT,
    ip_address INET,
    visit_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    page_load_time INTEGER, -- milliseconds
    bounce_rate BOOLEAN DEFAULT FALSE,
    conversion_event VARCHAR(50)
);
```

### 2. Insert Data dalam Volume Besar untuk Testing

```sql
-- Insert customers (100K records)
INSERT INTO customers (customer_code, customer_name, email, phone, address, city, country, registration_date, customer_segment, status)
SELECT 
    'CUST' || LPAD(generate_series::text, 6, '0'),
    'Customer ' || generate_series,
    'customer' || generate_series || '@email.com',
    '555-' || LPAD((generate_series % 10000)::text, 4, '0'),
    'Address ' || generate_series || ' Street',
    (ARRAY['New York','Los Angeles','Chicago','Houston','Phoenix','Philadelphia','San Antonio','San Diego','Dallas','San Jose'])[1 + (generate_series % 10)],
    (ARRAY['USA','Canada','Mexico','Brazil','UK','Germany','France','Japan','Australia','India'])[1 + (generate_series % 10)],
    '2020-01-01'::date + (generate_series % 1000) * interval '1 day',
    CASE 
        WHEN generate_series % 10 = 0 THEN 'VIP'
        WHEN generate_series % 5 = 0 THEN 'Premium' 
        ELSE 'Regular'
    END,
    CASE WHEN generate_series % 50 = 0 THEN 'Inactive' ELSE 'Active' END
FROM generate_series(1, 100000);

-- Insert sales reps (500 records)
INSERT INTO sales_reps (rep_name, rep_email, department, hire_date, target_annual, region)
SELECT 
    'Sales Rep ' || generate_series,
    'rep' || generate_series || '@company.com',
    (ARRAY['Electronics','Clothing','Books','Home','Sports'])[1 + (generate_series % 5)],
    '2018-01-01'::date + (generate_series % 1500) * interval '1 day',
    50000 + (random() * 100000)::numeric(12,2),
    (ARRAY['North','South','East','West','Central'])[1 + (generate_series % 5)]
FROM generate_series(1, 500);

-- Insert orders (500K records - ini yang akan membuat long query)
INSERT INTO orders (order_number, customer_id, order_date, total_amount, currency, payment_status, shipping_status, sales_rep_id)
SELECT 
    'ORD-' || TO_CHAR(generate_series, 'FM000000'),
    1 + (generate_series % 100000), -- random customer_id
    '2022-01-01'::date + (generate_series % 730) * interval '1 day', -- 2 years of data
    ROUND((10 + (random() * 1990))::numeric, 2), -- $10 to $2000
    CASE WHEN generate_series % 20 = 0 THEN 'EUR' WHEN generate_series % 30 = 0 THEN 'GBP' ELSE 'USD' END,
    CASE 
        WHEN generate_series % 10 = 0 THEN 'Failed'
        WHEN generate_series % 20 = 0 THEN 'Pending'
        ELSE 'Completed'
    END,
    CASE 
        WHEN generate_series % 15 = 0 THEN 'Cancelled'
        WHEN generate_series % 8 = 0 THEN 'Processing'
        WHEN generate_series % 4 = 0 THEN 'Shipped'
        ELSE 'Delivered'
    END,
    1 + (generate_series % 500) -- random sales rep
FROM generate_series(1, 500000);

-- Insert order items (1.5M records - average 3 items per order)
INSERT INTO order_items (order_id, product_id, product_name, category, quantity, unit_price, discount_percentage, line_total)
SELECT 
    1 + (generate_series % 500000), -- order_id
    1000 + (generate_series % 50000), -- product_id
    'Product ' || (1000 + (generate_series % 50000)),
    (ARRAY['Electronics','Clothing','Books','Home','Sports','Beauty','Automotive','Garden','Toys','Health'])[1 + (generate_series % 10)],
    1 + (generate_series % 5), -- quantity 1-5
    ROUND((5 + (random() * 495))::numeric, 2), -- $5 to $500
    CASE WHEN generate_series % 10 = 0 THEN ROUND((random() * 20)::numeric, 2) ELSE 0 END,
    0 -- akan di-update dengan trigger atau computed column
FROM generate_series(1, 1500000);

-- Update line_total
UPDATE order_items 
SET line_total = quantity * unit_price * (1 - discount_percentage/100);

-- Insert audit log (2M records)
INSERT INTO audit_log (table_name, operation, record_id, old_values, new_values, changed_by, changed_at, ip_address)
SELECT 
    (ARRAY['customers','orders','order_items'])[1 + (generate_series % 3)],
    (ARRAY['INSERT','UPDATE','DELETE'])[1 + (generate_series % 3)],
    generate_series,
    CASE WHEN generate_series % 3 = 1 THEN '{"field":"old_value"}'::jsonb ELSE NULL END,
    '{"field":"new_value"}'::jsonb,
    'user' || (1 + (generate_series % 100)),
    CURRENT_TIMESTAMP - (random() * interval '365 days'),
    ('192.168.' || (1 + (random() * 254)::int) || '.' || (1 + (random() * 254)::int))::inet
FROM generate_series(1, 2000000);

-- Insert web analytics (5M records - very high volume)
INSERT INTO web_analytics (customer_id, session_id, page_url, referrer_url, user_agent, ip_address, visit_timestamp, page_load_time, bounce_rate, conversion_event)
SELECT 
    CASE WHEN generate_series % 3 = 0 THEN 1 + (generate_series % 100000) ELSE NULL END,
    'session_' || (generate_series % 1000000),
    'https://shop.com/' || (ARRAY['home','products','cart','checkout','account','search','category','product'])[1 + (generate_series % 8)],
    CASE WHEN generate_series % 4 = 0 THEN 'https://google.com/search' WHEN generate_series % 6 = 0 THEN 'https://facebook.com' ELSE NULL END,
    'Mozilla/5.0 Browser ' || (1 + (generate_series % 50)),
    ('10.0.' || (1 + (random() * 254)::int) || '.' || (1 + (random() * 254)::int))::inet,
    CURRENT_TIMESTAMP - (random() * interval '30 days'),
    100 + (random() * 3000)::int,
    random() < 0.3, -- 30% bounce rate
    CASE 
        WHEN generate_series % 100 = 0 THEN 'purchase'
        WHEN generate_series % 50 = 0 THEN 'add_to_cart'
        WHEN generate_series % 20 = 0 THEN 'signup'
        ELSE NULL
    END
FROM generate_series(1, 5000000);

-- Update statistics untuk optimizer
ANALYZE customers;
ANALYZE orders;
ANALYZE order_items;
ANALYZE sales_reps;
ANALYZE audit_log;
ANALYZE web_analytics;

-- Tampilkan ukuran data yang telah dibuat
SELECT 
    schemaname,
    tablename,
    n_live_tup as "Estimated Rows",
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as "Total Size"
FROM pg_stat_user_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Demonstrasi Short Query vs Long Query

### 1. Short Query Examples (Selective Queries)

```sql
-- Short Query 1: Pencarian customer specific (sangat selektif)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT customer_name, email, city 
FROM customers 
WHERE customer_code = 'CUST000001';

-- Short Query 2: Order lookup specific (selektif)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT o.order_number, o.total_amount, c.customer_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_number = 'ORD-000001';

-- Short Query 3: Recent orders dari specific customer
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT o.order_number, o.order_date, o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id  
WHERE c.customer_code = 'CUST000001'
  AND o.order_date >= '2024-01-01';

-- Hasil: Index scan efektif karena data sedikit
```

### 2. Long Query Examples (Data Processing Intensive)

```sql
-- Long Query 1: Sales summary per bulan (memproses banyak data)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    DATE_TRUNC('month', order_date) as month,
    COUNT(*) as total_orders,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM orders  
WHERE order_date >= '2022-01-01'
  AND payment_status = 'Completed'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Long Query 2: Customer analytics agregasi
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    c.country,
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) as customer_count,
    COUNT(o.order_id) as total_orders,
    COALESCE(SUM(o.total_amount), 0) as total_spent,
    COALESCE(AVG(o.total_amount), 0) as avg_order_value,
    COUNT(o.order_id)::float / COUNT(DISTINCT c.customer_id) as orders_per_customer
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id 
    AND o.payment_status = 'Completed'
GROUP BY c.country, c.customer_segment
ORDER BY total_spent DESC;

-- Long Query 3: Product performance analysis (sangat kompleks)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    i.category,
    i.product_name,
    COUNT(i.item_id) as times_ordered,
    SUM(i.quantity) as total_quantity,
    SUM(i.line_total) as total_revenue,
    AVG(i.unit_price) as avg_price,
    COUNT(DISTINCT o.customer_id) as unique_buyers,
    COUNT(DISTINCT o.order_id) as unique_orders
FROM order_items i
JOIN orders o ON i.order_id = o.order_id
WHERE o.payment_status = 'Completed'
  AND o.order_date >= '2023-01-01'
GROUP BY i.category, i.product_name
HAVING COUNT(i.item_id) >= 10
ORDER BY total_revenue DESC;

-- Hasil: Sequential scan atau hash join lebih optimal untuk data besar
```

---

## Analisis Full Scan vs Index Scan - Tipping Point

### 1. Demonstrasi Tipping Point

```sql
-- Membuat index untuk testing
CREATE INDEX idx_orders_payment_status ON orders(payment_status);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_customers_segment ON customers(customer_segment);

-- Test 1: High selectivity (index optimal)
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT COUNT(*) FROM orders WHERE payment_status = 'Failed'; -- ~10% data

-- Test 2: Medium selectivity (borderline)
EXPLAIN (ANALYZE, BUFFERS, COSTS)  
SELECT COUNT(*) FROM orders WHERE payment_status = 'Pending'; -- ~5% data

-- Test 3: Low selectivity (sequential scan optimal)
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT COUNT(*) FROM orders WHERE payment_status = 'Completed'; -- ~85% data

-- Test 4: Range query dengan varying selectivity
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT * FROM orders WHERE order_date >= '2024-01-01'; -- Recent data (selective)

EXPLAIN (ANALYZE, BUFFERS, COSTS)  
SELECT * FROM orders WHERE order_date >= '2022-01-01'; -- Most data (full scan better)
```

### 2. Work_mem Impact pada Large Queries

```sql
-- Test hash join dengan work_mem berbeda
SET work_mem = '32MB';
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT c.customer_name, COUNT(o.order_id) as order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY order_count DESC
LIMIT 100;

-- Increase work_mem untuk large hash tables
SET work_mem = '256MB';
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT c.customer_name, COUNT(o.order_id) as order_count  
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY order_count DESC
LIMIT 100;

-- Reset work_mem
RESET work_mem;
```

---

## Hash Join, Semi-Join, dan Anti-Join Implementation

### 1. Hash Join Optimization

```sql
-- Hash join pada large dataset (optimal untuk equality joins)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    c.customer_segment,
    sr.region,
    COUNT(*) as total_orders,
    SUM(o.total_amount) as total_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id  -- Hash join likely
JOIN sales_reps sr ON o.sales_rep_id = sr.sales_rep_id -- Hash join likely
WHERE o.order_date >= '2023-01-01'
GROUP BY c.customer_segment, sr.region;
```

### 2. Semi-Join Pattern (EXISTS)

```sql
-- Semi-join: Find customers who have made orders
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT c.customer_name, c.email, c.city
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id 
      AND o.payment_status = 'Completed'
      AND o.order_date >= '2023-01-01'
);

-- Alternative dengan IN (PostgreSQL bisa optimize ke semi-join)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT c.customer_name, c.email, c.city  
FROM customers c
WHERE c.customer_id IN (
    SELECT o.customer_id
    FROM orders o
    WHERE o.payment_status = 'Completed' 
      AND o.order_date >= '2023-01-01'
);

-- Comparison dengan INNER JOIN + DISTINCT (kurang optimal)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT DISTINCT c.customer_name, c.email, c.city
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
WHERE o.payment_status = 'Completed'
  AND o.order_date >= '2023-01-01';
```

### 3. Anti-Join Pattern (NOT EXISTS)

```sql
-- Anti-join: Find customers who haven't made orders recently
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT c.customer_name, c.email, c.registration_date
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id 
      AND o.order_date >= '2023-01-01'
)
  AND c.status = 'Active';

-- Alternative dengan LEFT JOIN + IS NULL
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT c.customer_name, c.email, c.registration_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id 
    AND o.order_date >= '2023-01-01'
WHERE o.customer_id IS NULL
  AND c.status = 'Active';

-- NOT IN pattern (be careful with NULLs!)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT c.customer_name, c.email, c.registration_date
FROM customers c  
WHERE c.customer_id NOT IN (
    SELECT o.customer_id 
    FROM orders o 
    WHERE o.customer_id IS NOT NULL 
      AND o.order_date >= '2023-01-01'
)
  AND c.status = 'Active';
```

---

## CTE vs Temporary Table vs Subquery

### 1. CTE (Common Table Expression)

```sql
-- CTE approach: good for readability, single execution plan
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        SUM(total_amount) as monthly_revenue,
        COUNT(*) as monthly_orders
    FROM orders 
    WHERE payment_status = 'Completed'
      AND order_date >= '2023-01-01'
    GROUP BY DATE_TRUNC('month', order_date)
),
customer_segments AS (
    SELECT 
        customer_segment,
        COUNT(*) as segment_customers
    FROM customers 
    WHERE status = 'Active'
    GROUP BY customer_segment
)
SELECT 
    ms.month,
    ms.monthly_revenue,
    ms.monthly_orders,
    cs.customer_segment,
    cs.segment_customers
FROM monthly_sales ms
CROSS JOIN customer_segments cs
ORDER BY ms.month, cs.customer_segment;
```

### 2. Temporary Table Approach

```sql
-- Temporary table approach: good for reusability dan complex processing
CREATE TEMP TABLE temp_monthly_sales AS
SELECT 
    DATE_TRUNC('month', order_date) as month,
    SUM(total_amount) as monthly_revenue,
    COUNT(*) as monthly_orders,
    COUNT(DISTINCT customer_id) as unique_customers
FROM orders 
WHERE payment_status = 'Completed'
  AND order_date >= '2023-01-01'
GROUP BY DATE_TRUNC('month', order_date);

-- Add index pada temporary table untuk performance
CREATE INDEX idx_temp_monthly_sales_month ON temp_monthly_sales(month);

-- Analisis statistik untuk optimizer
ANALYZE temp_monthly_sales;

-- Use temporary table multiple kali
SELECT 
    month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY month) as prev_month_revenue,
    monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month) as revenue_change
FROM temp_monthly_sales
ORDER BY month;

-- Another usage of same temp table  
SELECT 
    AVG(monthly_revenue) as avg_monthly_revenue,
    MIN(monthly_revenue) as min_monthly_revenue,
    MAX(monthly_revenue) as max_monthly_revenue,
    STDDEV(monthly_revenue) as revenue_stddev
FROM temp_monthly_sales;

-- Cleanup
DROP TABLE temp_monthly_sales;
```

### 3. Subquery Approach

```sql
-- Subquery approach: might be less optimal karena repeated execution
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    o.month,
    o.monthly_revenue,
    o.monthly_orders,
    c.total_customers,
    o.monthly_revenue::float / c.total_customers as revenue_per_customer
FROM (
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        SUM(total_amount) as monthly_revenue,
        COUNT(*) as monthly_orders
    FROM orders 
    WHERE payment_status = 'Completed'
      AND order_date >= '2023-01-01'
    GROUP BY DATE_TRUNC('month', order_date)
) o
CROSS JOIN (
    SELECT COUNT(*) as total_customers 
    FROM customers 
    WHERE status = 'Active'
) c
ORDER BY o.month;
```

---

## View dan Materialized View Implementation

### 1. Regular View

```sql
-- Create view untuk complex query yang sering digunakan
CREATE VIEW v_customer_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    c.city,
    c.country,
    c.customer_segment,
    COUNT(o.order_id) as total_orders,
    COALESCE(SUM(o.total_amount), 0) as total_spent,
    COALESCE(AVG(o.total_amount), 0) as avg_order_value,
    MAX(o.order_date) as last_order_date,
    MIN(o.order_date) as first_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id 
    AND o.payment_status = 'Completed'
GROUP BY c.customer_id, c.customer_name, c.email, c.city, c.country, c.customer_segment;

-- Test view performance (executes underlying query setiap kali)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM v_customer_summary 
WHERE customer_segment = 'VIP' 
  AND total_orders > 5
ORDER BY total_spent DESC
LIMIT 20;
```

### 2. Materialized View

```sql
-- Create materialized view untuk expensive queries
CREATE MATERIALIZED VIEW mv_daily_sales_summary AS
SELECT 
    order_date,
    COUNT(*) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(total_amount) as daily_revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(*) FILTER (WHERE payment_status = 'Completed') as completed_orders,
    COUNT(*) FILTER (WHERE payment_status = 'Failed') as failed_orders,
    SUM(total_amount) FILTER (WHERE payment_status = 'Completed') as completed_revenue
FROM orders
WHERE order_date >= '2022-01-01'
GROUP BY order_date
ORDER BY order_date;

-- Create index pada materialized view
CREATE INDEX idx_mv_daily_sales_date ON mv_daily_sales_summary(order_date);

-- Test materialized view performance (reads pre-computed data)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    DATE_TRUNC('month', order_date) as month,
    SUM(daily_revenue) as monthly_revenue,
    AVG(avg_order_value) as avg_order_value,
    SUM(total_orders) as total_orders
FROM mv_daily_sales_summary
WHERE order_date >= '2023-01-01'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Refresh materialized view (when data changes)
REFRESH MATERIALIZED VIEW mv_daily_sales_summary;

-- Concurrent refresh (non-blocking)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_sales_summary;
```

### 3. Comparison: View vs Materialized View Performance

```sql
-- Compare execution time: View (recalculates setiap kali)
\timing on
SELECT COUNT(*) FROM v_customer_summary WHERE total_orders > 0;

-- vs Materialized View (pre-computed)
SELECT COUNT(*) FROM mv_daily_sales_summary WHERE daily_revenue > 1000;
\timing off

-- Memory dan storage usage comparison
SELECT 
    schemaname, 
    viewname as name,
    'VIEW' as type,
    NULL::text as size
FROM pg_views 
WHERE schemaname = 'public'
UNION ALL
SELECT 
    schemaname, 
    matviewname as name,
    'MATERIALIZED VIEW' as type,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
FROM pg_matviews 
WHERE schemaname = 'public';
```

---

## Partitioning Strategies

### 1. Range Partitioning (by Date)

```sql
-- Create partitioned table untuk large time-series data
CREATE TABLE orders_partitioned (
    order_id SERIAL,
    order_number VARCHAR(30) NOT NULL,
    customer_id INTEGER,
    order_date DATE NOT NULL,
    total_amount NUMERIC(12,2),
    payment_status VARCHAR(20),
    shipping_status VARCHAR(20),
    sales_rep_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (order_date);

-- Create partitions untuk different time ranges
CREATE TABLE orders_2022 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');

CREATE TABLE orders_2023 PARTITION OF orders_partitioned  
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE orders_2024 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Insert some test data
INSERT INTO orders_partitioned (order_number, customer_id, order_date, total_amount, payment_status)
SELECT 
    'PART-' || generate_series,
    1 + (generate_series % 1000),
    '2022-01-01'::date + (generate_series % 1095) * interval '1 day',
    100 + (random() * 900)::numeric(10,2),
    (ARRAY['Completed','Pending','Failed'])[1 + (generate_series % 3)]
FROM generate_series(1, 50000);

-- Test partition pruning
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*), AVG(total_amount) 
FROM orders_partitioned 
WHERE order_date BETWEEN '2023-01-01' AND '2023-12-31';

-- Should only scan orders_2023 partition
```

### 2. Hash Partitioning (by Customer)

```sql
-- Create hash partitioned table untuk even distribution
CREATE TABLE customers_partitioned (
    customer_id SERIAL,
    customer_code VARCHAR(20) NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    city VARCHAR(50),
    country VARCHAR(50),
    registration_date DATE DEFAULT CURRENT_DATE
) PARTITION BY HASH (customer_id);

-- Create hash partitions
CREATE TABLE customers_part_0 PARTITION OF customers_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE customers_part_1 PARTITION OF customers_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE customers_part_2 PARTITION OF customers_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 2); 
CREATE TABLE customers_part_3 PARTITION OF customers_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Test hash partitioning
INSERT INTO customers_partitioned (customer_code, customer_name, email, city, country)
SELECT 
    'HCUST' || generate_series,
    'Hash Customer ' || generate_series,
    'hcust' || generate_series || '@email.com',
    'City ' || (generate_series % 20),
    'Country ' || (generate_series % 5)
FROM generate_series(1, 10000);

-- Check distribution across partitions
SELECT 
    schemaname, tablename, n_live_tup 
FROM pg_stat_user_tables 
WHERE tablename LIKE 'customers_part_%'
ORDER BY tablename;
```

---

## Parallelism Configuration dan Testing

### 1. Configure Parallel Query Settings

```sql
-- Show current parallel settings
SELECT name, setting, unit, short_desc 
FROM pg_settings 
WHERE name LIKE '%parallel%' OR name LIKE '%worker%'
ORDER BY name;

-- Adjust parallel settings untuk testing
SET max_parallel_workers_per_gather = 4;
SET parallel_tuple_cost = 0.1;
SET parallel_setup_cost = 1000;
SET min_parallel_table_scan_size = '8MB';
SET min_parallel_index_scan_size = '512kB';
```

### 2. Test Parallel Query Execution

```sql
-- Query yang bisa diparalelkan (large aggregation)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    country,
    COUNT(*) as customer_count,
    AVG(total_amount) as avg_order_value,
    SUM(total_amount) as total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.payment_status = 'Completed'
GROUP BY country
ORDER BY total_revenue DESC;

-- Force parallel query
SET parallel_tuple_cost = 0;
SET parallel_setup_cost = 0;

EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    category,
    COUNT(*) as item_count,
    SUM(line_total) as total_revenue,
    AVG(unit_price) as avg_price
FROM order_items
GROUP BY category;

-- Reset settings
RESET parallel_tuple_cost;
RESET parallel_setup_cost;
RESET max_parallel_workers_per_gather;
```

---

## Advanced Long Query Optimization Techniques

### 1. Window Functions Optimization

```sql
-- Window functions pada large dataset
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    customer_id,
    order_date,
    total_amount,
    -- Ranking functions
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date) as order_sequence,
    RANK() OVER (PARTITION BY EXTRACT(YEAR FROM order_date) ORDER BY total_amount DESC) as yearly_rank,
    -- Aggregate functions
    SUM(total_amount) OVER (PARTITION BY customer_id) as customer_total,
    AVG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg_3orders,
    -- Lead/Lag functions  
    LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY order_date) as prev_order_amount,
    LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) - order_date as days_to_next_order
FROM orders
WHERE payment_status = 'Completed'
  AND order_date >= '2023-01-01'
ORDER BY customer_id, order_date;
```

### 2. Recursive CTE for Hierarchical Queries

```sql
-- Create hierarchical data structure
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INTEGER REFERENCES categories(category_id),
    level INTEGER DEFAULT 1
);

-- Insert hierarchical category data
INSERT INTO categories (category_name, parent_category_id, level) VALUES
('Electronics', NULL, 1),
('Computers', 1, 2),
('Smartphones', 1, 2),
('Laptops', 2, 3),
('Desktops', 2, 3),
('Gaming Laptops', 4, 4),
('Business Laptops', 4, 4);

-- Recursive CTE untuk category tree traversal
WITH RECURSIVE category_tree AS (
    -- Base case: root categories
    SELECT 
        category_id,
        category_name,
        parent_category_id,
        level,
        category_name as path,
        ARRAY[category_id] as id_path
    FROM categories 
    WHERE parent_category_id IS NULL
    
    UNION ALL
    
    -- Recursive case: child categories
    SELECT 
        c.category_id,
        c.category_name,  
        c.parent_category_id,
        c.level,
        ct.path || ' > ' || c.category_name as path,
        ct.id_path || c.category_id
    FROM categories c
    JOIN category_tree ct ON c.parent_category_id = ct.category_id
)
SELECT * FROM category_tree ORDER BY id_path;
```

### 3. Complex Analytical Queries

```sql
-- Customer cohort analysis (complex analytical query)
WITH customer_cohorts AS (
    SELECT 
        c.customer_id,
        c.registration_date,
        DATE_TRUNC('month', c.registration_date) as cohort_month,
        MIN(o.order_date) as first_order_date,
        DATE_TRUNC('month', MIN(o.order_date)) as first_order_month
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id 
        AND o.payment_status = 'Completed'
    WHERE c.registration_date >= '2022-01-01'
    GROUP BY c.customer_id, c.registration_date
),
cohort_data AS (
    SELECT 
        cc.cohort_month,
        cc.first_order_month,
        EXTRACT(EPOCH FROM (cc.first_order_month - cc.cohort_month)) / (30.44 * 24 * 3600) as months_to_first_order,
        COUNT(*) as customer_count
    FROM customer_cohorts cc
    WHERE cc.first_order_date IS NOT NULL
    GROUP BY cc.cohort_month, cc.first_order_month
)
SELECT 
    cohort_month,
    SUM(customer_count) FILTER (WHERE months_to_first_order <= 0) as month_0,
    SUM(customer_count) FILTER (WHERE months_to_first_order <= 1) as month_1,
    SUM(customer_count) FILTER (WHERE months_to_first_order <= 2) as month_2,
    SUM(customer_count) FILTER (WHERE months_to_first_order <= 3) as month_3,
    SUM(customer_count) as total_converted_customers
FROM cohort_data
GROUP BY cohort_month
ORDER BY cohort_month;
```

---

## Performance Monitoring dan Optimization

### 1. Query Performance Analysis

```sql
-- Enable query timing
\timing on

-- Create function to analyze query performance
CREATE OR REPLACE FUNCTION analyze_long_query_performance(
    query_name TEXT,
    query_sql TEXT
) RETURNS TABLE (
    query_description TEXT,
    execution_time_ms NUMERIC,
    total_cost NUMERIC,
    rows_processed BIGINT,
    buffers_hit BIGINT,
    buffers_read BIGINT,
    temp_files_used BOOLEAN
) AS $$
BEGIN
    -- This is a simplified framework
    -- In real implementation, would use EXPLAIN ANALYZE output parsing
    RETURN QUERY SELECT 
        query_name,
        0.0::NUMERIC,
        0.0::NUMERIC, 
        0::BIGINT,
        0::BIGINT,
        0::BIGINT,
        FALSE;
END;
$$ LANGUAGE plpgsql;

-- Monitor long-running queries
SELECT 
    pid,
    now() - pg_stat_activity.query_start as duration,
    query,
    state
FROM pg_stat_activity
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
  AND state = 'active'
ORDER BY duration DESC;
```

### 2. Index Usage Analysis untuk Long Queries

```sql
-- Analyze index effectiveness untuk long queries
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation,
    most_common_vals[1:3] as top_values,
    most_common_freqs[1:3] as top_frequencies
FROM pg_stats 
WHERE tablename IN ('orders', 'order_items', 'customers')  
  AND n_distinct > 100  -- Focus on good candidates untuk indexes
ORDER BY tablename, n_distinct DESC;

-- Index usage statistics  
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch, 
    idx_scan,
    CASE 
        WHEN idx_scan = 0 THEN 'Never used'
        WHEN idx_scan < 100 THEN 'Low usage' 
        WHEN idx_scan < 1000 THEN 'Medium usage'
        ELSE 'High usage'
    END as usage_category,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### 3. Memory Usage Analysis

```sql
-- Check memory settings untuk long queries
SELECT 
    name,
    setting,
    unit,
    short_desc,
    context
FROM pg_settings 
WHERE name IN (
    'work_mem',
    'maintenance_work_mem', 
    'shared_buffers',
    'effective_cache_size',
    'random_page_cost',
    'seq_page_cost'
)
ORDER BY name;

-- Monitor temp file usage (indicates insufficient work_mem)
SELECT 
    datname,
    temp_files,
    temp_bytes,
    pg_size_pretty(temp_bytes) as temp_size
FROM pg_stat_database 
WHERE datname = current_database();
```

---

## Best Practices dan Troubleshooting

### 1. Long Query Optimization Checklist

```sql
-- 1. Analyze query plan untuk bottlenecks
EXPLAIN (ANALYZE, BUFFERS, TIMING, COSTS, VERBOSE)
SELECT /* your long query here */;

-- 2. Check statistics are up-to-date
SELECT 
    schemaname, tablename, 
    last_analyze, 
    n_live_tup,
    n_dead_tup  
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND (last_analyze < CURRENT_DATE - INTERVAL '7 days' OR last_analyze IS NULL)
ORDER BY n_live_tup DESC;

-- 3. Identify missing indexes
-- Look for Seq Scan pada large tables dalam EXPLAIN output

-- 4. Consider query rewriting
-- Break complex queries into simpler parts
-- Use appropriate join types
-- Filter early dan often
```

### 2. Common Long Query Anti-patterns

```sql
-- Anti-pattern 1: Late filtering (filter setelah expensive operations)
-- Bad:
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.customer_name, total_spent
FROM (
    SELECT customer_id, SUM(total_amount) as total_spent
    FROM orders  
    GROUP BY customer_id  -- Expensive operation pada semua data
) o
JOIN customers c ON o.customer_id = c.customer_id
WHERE c.country = 'USA';  -- Filter applied too late

-- Good: Early filtering
EXPLAIN (ANALYZE, BUFFERS) 
SELECT c.customer_name, SUM(o.total_amount) as total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.country = 'USA'  -- Filter applied early
GROUP BY c.customer_id, c.customer_name;

-- Anti-pattern 2: Unnecessary DISTINCT pada large result sets
-- Bad:
SELECT DISTINCT c.country, o.order_date  
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;

-- Good: Use GROUP BY atau proper normalization
SELECT c.country, o.order_date
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id  
GROUP BY c.country, o.order_date;
```

### 3. Long Query Monitoring Dashboard

```sql
-- Create monitoring view untuk long queries
CREATE VIEW v_long_query_monitor AS
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    now() - query_start as duration,
    now() - state_change as state_duration,
    state,
    LEFT(query, 100) || '...' as query_preview,
    query_start,
    wait_event_type,
    wait_event
FROM pg_stat_activity 
WHERE state = 'active'
  AND (now() - query_start) > interval '30 seconds'
ORDER BY duration DESC;

-- Use monitoring view
SELECT * FROM v_long_query_monitor;

-- Kill long-running problematic queries (careful!)
-- SELECT pg_terminate_backend(pid) FROM v_long_query_monitor WHERE duration > interval '1 hour';
```

---

## Cleanup dan Summary

```sql
-- Cleanup test objects
DROP VIEW IF EXISTS v_long_query_monitor;
DROP VIEW IF EXISTS v_customer_summary;
DROP MATERIALIZED VIEW IF EXISTS mv_daily_sales_summary;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS orders_partitioned CASCADE;
DROP TABLE IF EXISTS customers_partitioned CASCADE;

-- Performance summary
SELECT 
    'Table' as object_type,
    tablename as object_name,
    n_live_tup as rows,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_stat_user_tables
WHERE schemaname = 'public'
UNION ALL
SELECT 
    'Index' as object_type,
    indexname as object_name, 
    0 as rows,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as size
FROM pg_stat_user_indexes 
WHERE schemaname = 'public' 
  AND idx_scan > 0  -- Only show used indexes
ORDER BY object_type, object_name;

-- Reset all parameters
RESET ALL;

-- Final recommendations summary
/*
LONG QUERY OPTIMIZATION GUIDELINES:

1. DATA PROCESSING STRATEGY:
   ✓ Filter early dan often
   ✓ Use appropriate join algorithms (Hash Join untuk large equality joins)
   ✓ Consider Semi-Join/Anti-Join untuk EXISTS/NOT EXISTS patterns
   ✓ Leverage Sequential Scan untuk high selectivity queries

2. MEMORY MANAGEMENT:
   ✓ Increase work_mem untuk complex sorts dan hash operations
   ✓ Monitor temp file usage
   ✓ Consider parallel processing untuk CPU-intensive operations

3. QUERY STRUCTURE:
   ✓ Use CTE untuk readability, Temp Tables untuk reusability
   ✓ Materialized Views untuk expensive recurring calculations
   ✓ Partitioning untuk very large time-series data

4. MONITORING:
   ✓ Regular ANALYZE to keep statistics current
   ✓ Monitor long-running queries
   ✓ Track index usage dan effectiveness
   ✓ Use EXPLAIN ANALYZE untuk systematic optimization

5. WHEN TO USE WHAT:
   - CTE: Single-use complex logic, readability
   - Temp Tables: Multi-use intermediate results
   - Materialized Views: Expensive recurring analytical queries
   - Partitioning: Time-series data > 100M rows
   - Parallel Queries: CPU-intensive aggregations on large datasets
*/
```

---

**Catatan:** Script ini memberikan implementasi komprehensif dari konsep optimasi query panjang yang dibahas dalam Modul Week 7. Fokus utama adalah pada query yang memproses volume data besar dengan teknik optimasi yang berbeda dari query selektif, termasuk penggunaan full scan, hash join, CTE, materialized view, partitioning, dan parallelism.