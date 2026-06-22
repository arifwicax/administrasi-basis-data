-- ============================================================
-- setup.sql
-- Persiapan database untuk praktikum Week 15
-- Administrasi Basis Data — Monitoring dan Visualisasi
-- ============================================================

-- Langkah 1: Buat database (jalankan sebagai superuser di luar database ini)
-- CREATE DATABASE db_monitoring_lab;
-- \c db_monitoring_lab

-- Langkah 2: Aktifkan ekstensi pg_stat_statements
-- (Pastikan shared_preload_libraries = 'pg_stat_statements' di postgresql.conf)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Langkah 3: Buat tabel
CREATE TABLE IF NOT EXISTS produk (
    id      SERIAL PRIMARY KEY,
    nama    VARCHAR(100) NOT NULL,
    stok    INTEGER      NOT NULL DEFAULT 0,
    harga   NUMERIC(12, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS transaksi (
    id          SERIAL PRIMARY KEY,
    pelanggan   VARCHAR(100),
    produk      VARCHAR(100),
    jumlah      INTEGER,
    total_harga NUMERIC(12, 2),
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Langkah 4: Isi data produk (100 baris)
INSERT INTO produk (nama, stok, harga)
SELECT
    'Produk-' || i,
    (random() * 100)::INT,
    (random() * 500000 + 10000)::NUMERIC(12, 2)
FROM generate_series(1, 100) AS i
ON CONFLICT DO NOTHING;

-- Langkah 5: Isi data transaksi (50.000 baris)
INSERT INTO transaksi (pelanggan, produk, jumlah, total_harga)
SELECT
    'Pelanggan-' || (random() * 1000)::INT,
    'Produk-'    || (random() * 100)::INT,
    (random() * 10 + 1)::INT,
    (random() * 5000000)::NUMERIC(12, 2)
FROM generate_series(1, 50000);

-- Langkah 6: Update statistik
ANALYZE produk;
ANALYZE transaksi;

-- ============================================================
-- Verifikasi
-- ============================================================
SELECT 'produk'    AS tabel, COUNT(*) AS jumlah_baris FROM produk
UNION ALL
SELECT 'transaksi' AS tabel, COUNT(*) AS jumlah_baris FROM transaksi;
