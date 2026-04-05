```sql

-- Tabel customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    birthdate DATE
);

COMMENT ON COLUMN customers.birthdate IS 'Tanggal lahir pelanggan';

-- 🔍 Index tambahan
-- Index untuk pencarian cepat berdasarkan nama pelanggan (misal saat filter nama di Streamlit)
CREATE INDEX idx_customers_name ON customers (name);
-- Index untuk pencarian/filter berdasarkan tanggal lahir (jika digunakan analisis umur pelanggan)
CREATE INDEX idx_customers_birthdate ON customers (birthdate);


-- Tabel products
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    stock INT NOT NULL
);

-- 🔍 Index tambahan
-- Untuk pencarian cepat produk berdasarkan nama (misal fitur filter di dashboard)
CREATE INDEX idx_products_name ON products (name);
-- Untuk analisis harga produk (misal histogram harga)
CREATE INDEX idx_products_price ON products (price);

-- Tabel orders
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, --jika tidak diisi, otomatis berisi waktu saat data dimasukkan ke tabel.
    total_amount NUMERIC(10, 2) NOT NULL,
    CONSTRAINT fk_customer --memberi nama aturan relasi (boleh kamu ganti).
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id) --jika data pelanggan dihapus dari tabel customers
        ON DELETE CASCADE
);

-- 🔍 Index tambahan
-- Untuk analisis waktu penjualan (misal line chart penjualan per bulan)
CREATE INDEX idx_orders_order_date ON orders (order_date);
-- Untuk join cepat dengan tabel customers
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
-- Untuk agregasi berdasarkan total_amount
CREATE INDEX idx_orders_total_amount ON orders (total_amount);

-- Tabel order_details
CREATE TABLE IF NOT EXISTS order_details (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) GENERATED ALWAYS AS (quantity * price) STORED, -- hasil quantity * price, GENERATED ALWAYS AS (...) STORED kolom ini selalu dihitung dan disimpan di database
    CONSTRAINT fk_order
        FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_product
        FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);

-- 🔍 Index tambahan
-- Untuk join cepat antara order_details ↔ orders
CREATE INDEX idx_order_details_order_id ON order_details (order_id);
-- Untuk join cepat antara order_details ↔ products
CREATE INDEX idx_order_details_product_id ON order_details (product_id);
-- Untuk analisis jumlah barang terjual
CREATE INDEX idx_order_details_quantity ON order_details (quantity);
-- Untuk analisis harga per produk di detail pesanan
CREATE INDEX idx_order_details_price ON order_details (price);

```