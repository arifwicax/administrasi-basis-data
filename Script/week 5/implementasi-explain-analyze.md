# Implementasi PostgreSQL - Analisis EXPLAIN dan EXPLAIN ANALYZE

## Week 5 - Administrasi Basis Data

---

## Setup Database dan Tabel untuk Analisis Execution Plan

### 1. Membuat Database dan Tabel Sample

```sql
-- Membuat database untuk analisis execution plan
CREATE DATABASE db_explain_demo;

-- Menggunakan database
\c db_explain_demo;

-- Membuat tabel mahasiswa dengan data yang cukup untuk analisis
CREATE TABLE mahasiswa (
    nim VARCHAR(15) PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    angkatan INTEGER NOT NULL,
    jurusan VARCHAR(50) NOT NULL,
    ipk NUMERIC(3,2),
    alamat TEXT,
    tanggal_lahir DATE,
    status VARCHAR(20) DEFAULT 'Aktif',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Membuat tabel krs yang akan di-join dengan mahasiswa
CREATE TABLE krs (
    id_krs SERIAL PRIMARY KEY,
    nim VARCHAR(15) NOT NULL REFERENCES mahasiswa(nim),
    kode_mk VARCHAR(10) NOT NULL,
    nama_mk VARCHAR(100) NOT NULL,
    sks INTEGER NOT NULL,
    semester_ambil INTEGER NOT NULL,
    tahun_akademik VARCHAR(10) NOT NULL,
    nilai CHAR(2) CHECK (nilai IN ('A','B+','B','C+','C','D','E','F')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Membuat tabel nilai_detail untuk demonstrasi join kompleks
CREATE TABLE nilai_detail (
    id_nilai SERIAL PRIMARY KEY,
    id_krs INTEGER REFERENCES krs(id_krs),
    jenis_tugas VARCHAR(20), -- 'UTS', 'UAS', 'Tugas', 'Quiz'
    nilai NUMERIC(5,2),
    bobot NUMERIC(3,2),
    tanggal_nilai DATE DEFAULT CURRENT_DATE
);

-- Membuat tabel log_akses untuk demonstrasi data besar
CREATE TABLE log_akses (
    id_log BIGSERIAL PRIMARY KEY,
    nim VARCHAR(15),
    waktu_akses TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modul VARCHAR(50),
    aktivitas TEXT,
    ip_address INET,
    user_agent TEXT
);
```

### 2. Insert Data Sample dalam Jumlah Besar

```sql
-- Insert mahasiswa dengan data realistis
INSERT INTO mahasiswa (nim, nama, angkatan, jurusan, ipk, alamat, tanggal_lahir, status)
SELECT 
    '202' || (1 + (generate_series % 4)) || LPAD((generate_series)::text, 4, '0'),
    'Mahasiswa ' || generate_series,
    2021 + (generate_series % 4),
    CASE 
        WHEN generate_series % 3 = 0 THEN 'Informatika'
        WHEN generate_series % 3 = 1 THEN 'Sistem Informasi'
        ELSE 'Teknik Komputer'
    END,
    ROUND((2.5 + (random() * 1.5))::numeric, 2),
    'Jl. Contoh No. ' || (1 + (generate_series % 100)),
    '2000-01-01'::date + (generate_series % 1095) * interval '1 day',
    CASE WHEN generate_series % 20 = 0 THEN 'Lulus' ELSE 'Aktif' END
FROM generate_series(1, 5000);

-- Insert KRS dengan variasi data
INSERT INTO krs (nim, kode_mk, nama_mk, sks, semester_ambil, tahun_akademik, nilai)
SELECT 
    m.nim,
    'MK' || LPAD((1 + (random() * 50)::int)::text, 3, '0'),
    'Mata Kuliah ' || (1 + (random() * 50)::int),
    CASE WHEN random() < 0.6 THEN 3 ELSE (ARRAY[2,4])[1 + (random())::int] END,
    1 + (random() * 8)::int,
    '202' || (1 + (random() * 4)::int) || '/202' || (2 + (random() * 4)::int),
    (ARRAY['A','B+','B','C+','C','D','E'])[1 + (random() * 6)::int]
FROM mahasiswa m
CROSS JOIN generate_series(1, (2 + (random() * 8)::int)) -- Setiap mahasiswa ambil 2-10 mata kuliah
ORDER BY random()
LIMIT 25000;

-- Insert nilai detail
INSERT INTO nilai_detail (id_krs, jenis_tugas, nilai, bobot)
SELECT 
    k.id_krs,
    (ARRAY['UTS','UAS','Tugas','Quiz','Praktikum'])[1 + (random() * 4)::int],
    ROUND((50 + (random() * 50))::numeric, 2),
    ROUND((0.1 + (random() * 0.4))::numeric, 2)
FROM krs k
CROSS JOIN generate_series(1, (1 + (random() * 4)::int)) -- 1-5 komponen nilai per KRS
ORDER BY random()
LIMIT 75000;

-- Insert log akses dalam jumlah besar untuk demonstrasi
INSERT INTO log_akses (nim, waktu_akses, modul, aktivitas, ip_address, user_agent)
SELECT 
    m.nim,
    CURRENT_TIMESTAMP - (random() * interval '365 days'),
    (ARRAY['Portal','E-Learning','Perpustakaan','Keuangan','Akademik'])[1 + (random() * 4)::int],
    'Login ke sistem',
    ('192.168.' || (1 + (random() * 254)::int) || '.' || (1 + (random() * 254)::int))::inet,
    'Mozilla/5.0 User Agent ' || (1 + (random() * 100)::int)
FROM mahasiswa m
CROSS JOIN generate_series(1, (5 + (random() * 20)::int)) -- 5-25 log per mahasiswa
ORDER BY random()
LIMIT 100000;

-- Update statistik untuk optimizer
ANALYZE mahasiswa;
ANALYZE krs;
ANALYZE nilai_detail;
ANALYZE log_akses;
```

---

## Dasar-Dasar EXPLAIN dan EXPLAIN ANALYZE

### 1. Perbedaan EXPLAIN dan EXPLAIN ANALYZE

```sql
-- EXPLAIN: Hanya menampilkan rencana eksekusi (tidak menjalankan query)
EXPLAIN
SELECT * FROM mahasiswa WHERE angkatan = 2023;

-- EXPLAIN ANALYZE: Menjalankan query dan menampilkan waktu eksekusi nyata
EXPLAIN ANALYZE
SELECT * FROM mahasiswa WHERE angkatan = 2023;

-- EXPLAIN dengan opsi tambahan untuk informasi lebih detail
EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE)
SELECT * FROM mahasiswa WHERE angkatan = 2023;
```

### 2. Membaca Komponen Dasar Execution Plan

```sql
-- Contoh 1: Sequential Scan
EXPLAIN ANALYZE
SELECT nama, ipk 
FROM mahasiswa 
WHERE status = 'Aktif';

-- Output yang diharapkan:
-- Seq Scan on mahasiswa (cost=0.00..XX.XX rows=XXXX width=XX) (actual time=X.XXX..X.XXX rows=XXXX loops=1)
--   Filter: ((status)::text = 'Aktif'::text)
--   Rows Removed by Filter: XXX

-- Penjelasan:
-- - cost=0.00..XX.XX: biaya awal..biaya total
-- - rows=XXXX: estimasi jumlah baris
-- - width=XX: estimasi rata-rata ukuran baris (bytes)
-- - actual time=X.XXX..X.XXX: waktu nyata awal..akhir (ms)
-- - rows=XXXX: jumlah baris yang benar-benar dikembalikan
-- - loops=1: berapa kali operasi ini dijalankan
```

---

## Demonstrasi Berbagai Jenis Scan Operations

### 1. Sequential Scan vs Index Scan

```sql
-- Tanpa index - akan menggunakan Sequential Scan
EXPLAIN ANALYZE
SELECT * FROM mahasiswa WHERE angkatan = 2023;

-- Membuat index
CREATE INDEX idx_mahasiswa_angkatan ON mahasiswa(angkatan);

-- Dengan index - kemungkinan menggunakan Index Scan atau Bitmap Index Scan
EXPLAIN ANALYZE
SELECT * FROM mahasiswa WHERE angkatan = 2023;

-- Perbandingan performa
EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, ipk FROM mahasiswa WHERE angkatan = 2023;
```

### 2. Index-Only Scan

```sql
-- Membuat covering index untuk Index-Only Scan
CREATE INDEX idx_mahasiswa_covering ON mahasiswa(angkatan, nama, ipk);

-- Query yang hanya menggunakan kolom dalam index
EXPLAIN ANALYZE
SELECT angkatan, nama, ipk 
FROM mahasiswa 
WHERE angkatan = 2023;

-- Bandingkan dengan query yang membutuhkan akses tabel
EXPLAIN ANALYZE
SELECT angkatan, nama, ipk, alamat 
FROM mahasiswa 
WHERE angkatan = 2023;
```

### 3. Bitmap Index Scan dan Bitmap Heap Scan

```sql
-- Membuat index tambahan
CREATE INDEX idx_mahasiswa_jurusan ON mahasiswa(jurusan);

-- Query dengan kondisi yang memicu Bitmap Scan
EXPLAIN ANALYZE
SELECT * FROM mahasiswa 
WHERE angkatan IN (2022, 2023) OR jurusan = 'Informatika';

-- Kombinasi multiple index conditions
EXPLAIN ANALYZE
SELECT * FROM mahasiswa 
WHERE angkatan = 2023 AND jurusan IN ('Informatika', 'Sistem Informasi');
```

---

## Analisis Algoritma Join dalam Execution Plan

### 1. Nested Loop Join

```sql
-- Query yang kemungkinan menggunakan Nested Loop Join (tabel kecil)
EXPLAIN ANALYZE
SELECT m.nama, COUNT(k.id_krs) as jumlah_mk
FROM mahasiswa m
LEFT JOIN krs k ON m.nim = k.nim
WHERE m.angkatan = 2024  -- Filter yang sangat selektif
GROUP BY m.nim, m.nama
LIMIT 10;
```

### 2. Hash Join

```sql
-- Query dengan Hash Join (tabel cukup besar)
EXPLAIN ANALYZE
SELECT m.nama, m.angkatan, k.nama_mk, k.nilai
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
WHERE m.angkatan BETWEEN 2022 AND 2023;

-- Hash Join dengan kondisi kompleks
EXPLAIN ANALYZE
SELECT m.jurusan, AVG(k.sks) as rata_sks
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
WHERE m.status = 'Aktif'
GROUP BY m.jurusan;
```

### 3. Merge Join

```sql
-- Membuat data yang terurut untuk Merge Join
CREATE INDEX idx_mahasiswa_nim_sorted ON mahasiswa(nim);
CREATE INDEX idx_krs_nim_sorted ON krs(nim);

-- Query yang berpeluang menggunakan Merge Join
EXPLAIN ANALYZE
SELECT m.nim, m.nama, k.nama_mk
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
ORDER BY m.nim
LIMIT 100;
```

---

## Analisis Operasi Sorting dan Agregasi

### 1. Sort Operations

```sql
-- Sort dalam memory (work_mem cukup)
SET work_mem = '50MB';
EXPLAIN ANALYZE
SELECT * FROM mahasiswa 
ORDER BY nama, angkatan
LIMIT 100;

-- Sort dengan disk (work_mem kecil)
SET work_mem = '1MB';
EXPLAIN ANALYZE
SELECT * FROM mahasiswa 
ORDER BY nama, angkatan
LIMIT 100;

-- Reset work_mem
RESET work_mem;
```

### 2. Aggregate Operations

```sql
-- HashAggregate
EXPLAIN ANALYZE
SELECT angkatan, COUNT(*) as jumlah, AVG(ipk) as rata_ipk
FROM mahasiswa 
GROUP BY angkatan;

-- GroupAggregate (dengan ORDER BY)
EXPLAIN ANALYZE
SELECT angkatan, COUNT(*) as jumlah, AVG(ipk) as rata_ipk
FROM mahasiswa 
GROUP BY angkatan
ORDER BY angkatan;

-- Aggregate dengan HAVING
EXPLAIN ANALYZE
SELECT jurusan, COUNT(*) as jumlah
FROM mahasiswa
GROUP BY jurusan
HAVING COUNT(*) > 1000;
```

---

## Analisis Query Kompleks dengan Multiple Operations

### 1. Complex Multi-table Join

```sql
-- Query kompleks dengan banyak join dan agregasi
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    m.jurusan,
    m.angkatan,
    COUNT(DISTINCT m.nim) as jumlah_mahasiswa,
    COUNT(k.id_krs) as total_mata_kuliah,
    AVG(n.nilai) as rata_nilai_detail,
    SUM(k.sks) as total_sks
FROM mahasiswa m
LEFT JOIN krs k ON m.nim = k.nim
LEFT JOIN nilai_detail n ON k.id_krs = n.id_krs
WHERE m.status = 'Aktif'
GROUP BY m.jurusan, m.angkatan
HAVING COUNT(k.id_krs) > 5
ORDER BY m.angkatan DESC, rata_nilai_detail DESC
LIMIT 20;
```

### 2. Subquery vs Join Performance

```sql
-- Menggunakan subquery (mungkin kurang efisien)
EXPLAIN ANALYZE
SELECT m.nama, m.ipk
FROM mahasiswa m
WHERE m.nim IN (
    SELECT k.nim 
    FROM krs k 
    WHERE k.nilai IN ('A', 'B+')
    GROUP BY k.nim
    HAVING COUNT(*) >= 5
);

-- Menggunakan join (biasanya lebih efisien)
EXPLAIN ANALYZE
SELECT DISTINCT m.nama, m.ipk
FROM mahasiswa m
JOIN (
    SELECT k.nim
    FROM krs k 
    WHERE k.nilai IN ('A', 'B+')
    GROUP BY k.nim
    HAVING COUNT(*) >= 5
) excellent_students ON m.nim = excellent_students.nim;
```

### 3. Window Functions dalam Execution Plan

```sql
-- Query dengan window function
EXPLAIN ANALYZE
SELECT 
    nim, nama, ipk,
    RANK() OVER (PARTITION BY angkatan ORDER BY ipk DESC) as ranking,
    AVG(ipk) OVER (PARTITION BY jurusan) as avg_ipk_jurusan
FROM mahasiswa
WHERE status = 'Aktif';
```

---

## Troubleshooting Query Performance

### 1. Identifying Performance Bottlenecks

```sql
-- Query dengan performa buruk untuk analisis
EXPLAIN (ANALYZE, BUFFERS, TIMING, COSTS)
SELECT 
    l.nim,
    COUNT(*) as total_akses,
    DATE_TRUNC('month', l.waktu_akses) as bulan,
    m.nama,
    m.jurusan
FROM log_akses l
JOIN mahasiswa m ON l.nim = m.nim
WHERE l.waktu_akses >= '2024-01-01'
GROUP BY l.nim, DATE_TRUNC('month', l.waktu_akses), m.nama, m.jurusan
ORDER BY total_akses DESC;

-- Analisis penyebab lambat:
-- 1. Perhatikan operasi dengan cost tertinggi
-- 2. Cek estimasi vs actual rows (bila jauh berbeda = statistik buruk)
-- 3. Perhatikan apakah ada Sequential Scan pada tabel besar
-- 4. Lihat operasi sort/hash yang menggunakan disk (temp files)
```

### 2. Optimasi dengan Index

```sql
-- Sebelum optimasi - catat performance baseline
EXPLAIN (ANALYZE, BUFFERS)
SELECT l.nim, COUNT(*) 
FROM log_akses l 
WHERE l.waktu_akses BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY l.nim;

-- Membuat index untuk optimasi
CREATE INDEX idx_log_akses_waktu ON log_akses(waktu_akses);
CREATE INDEX idx_log_akses_nim_waktu ON log_akses(nim, waktu_akses);

-- Setelah optimasi - bandingkan performance
EXPLAIN (ANALYZE, BUFFERS)
SELECT l.nim, COUNT(*) 
FROM log_akses l 
WHERE l.waktu_akses BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY l.nim;
```

### 3. Analyzing Different Query Approaches

```sql
-- Approach 1: Subquery dengan EXISTS
EXPLAIN ANALYZE
SELECT m.nama, m.angkatan
FROM mahasiswa m
WHERE EXISTS (
    SELECT 1 FROM krs k 
    WHERE k.nim = m.nim AND k.nilai = 'A'
);

-- Approach 2: JOIN dengan DISTINCT
EXPLAIN ANALYZE
SELECT DISTINCT m.nama, m.angkatan
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
WHERE k.nilai = 'A';

-- Approach 3: Menggunakan IN
EXPLAIN ANALYZE
SELECT m.nama, m.angkatan
FROM mahasiswa m
WHERE m.nim IN (
    SELECT nim FROM krs WHERE nilai = 'A'
);
```

---

## Monitoring dan Profiling Advanced

### 1. Using Different EXPLAIN Options

```sql
-- EXPLAIN dengan semua opsi untuk analisis detail
EXPLAIN (
    ANALYZE true,
    VERBOSE true,
    COSTS true,
    BUFFERS true,
    TIMING true,
    FORMAT JSON
)
SELECT m.nama, k.nama_mk, n.nilai
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
JOIN nilai_detail n ON k.id_krs = n.id_krs
WHERE m.angkatan = 2023 AND n.jenis_tugas = 'UAS';
```

### 2. Analyzing Buffer Usage

```sql
-- Query untuk melihat penggunaan buffer (shared buffers, temp files)
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    m.jurusan,
    COUNT(*) as total_mahasiswa,
    STRING_AGG(DISTINCT k.nama_mk, ', ' ORDER BY k.nama_mk) as mata_kuliah
FROM mahasiswa m
LEFT JOIN krs k ON m.nim = k.nim
GROUP BY m.jurusan;

-- Perhatikan output:
-- - Shared Hit: data yang sudah ada di buffer
-- - Shared Read: data yang dibaca dari disk
-- - Temp Read/Written: penggunaan temporary files
```

### 3. Cost Model Analysis

```sql
-- Melihat parameter cost model PostgreSQL
SELECT name, setting, unit, short_desc 
FROM pg_settings 
WHERE name LIKE '%cost%' OR name LIKE '%page%'
ORDER BY name;

-- Test pengaruh perubahan cost parameters
SET seq_page_cost = 1.0;
SET random_page_cost = 4.0;
EXPLAIN SELECT * FROM mahasiswa WHERE angkatan = 2023;

SET seq_page_cost = 1.0;
SET random_page_cost = 1.1; -- SSD setting
EXPLAIN SELECT * FROM mahasiswa WHERE angkatan = 2023;

-- Reset ke default
RESET seq_page_cost;
RESET random_page_cost;
```

---

## Statistik dan Histogram Analysis

### 1. Analyzing Table Statistics

```sql
-- Melihat statistik tabel untuk optimizer
SELECT 
    schemaname, tablename, n_live_tup, n_dead_tup,
    last_vacuum, last_autovacuum, last_analyze, last_autoanalyze
FROM pg_stat_user_tables
WHERE tablename IN ('mahasiswa', 'krs', 'log_akses');

-- Melihat statistik kolom
SELECT 
    tablename, attname, n_distinct, correlation,
    most_common_vals, most_common_freqs
FROM pg_stats 
WHERE tablename = 'mahasiswa'
  AND attname IN ('angkatan', 'jurusan', 'status');
```

### 2. Impact of Outdated Statistics

```sql
-- Simulasi statistik yang tidak akurat
-- Tambah banyak data baru tanpa ANALYZE
INSERT INTO mahasiswa (nim, nama, angkatan, jurusan, ipk)
SELECT 
    'NEW' || LPAD(generate_series::text, 6, '0'),
    'New Student ' || generate_series,
    2025, -- Semua angkatan baru
    'Informatika',
    3.5
FROM generate_series(1, 2000);

-- Query sebelum ANALYZE (estimasi mungkin tidak akurat)
EXPLAIN ANALYZE
SELECT * FROM mahasiswa WHERE angkatan = 2025;

-- Update statistik
ANALYZE mahasiswa;

-- Query setelah ANALYZE (estimasi lebih akurat)
EXPLAIN ANALYZE
SELECT * FROM mahasiswa WHERE angkatan = 2025;
```

---

## Praktikum Troubleshooting Real-World Scenarios

### 1. Case Study: Slow Reporting Query

```sql
-- Query laporan yang lambat
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    EXTRACT(YEAR FROM l.waktu_akses) as tahun,
    EXTRACT(MONTH FROM l.waktu_akses) as bulan,
    m.jurusan,
    l.modul,
    COUNT(*) as total_akses,
    COUNT(DISTINCT l.nim) as unique_users,
    AVG(EXTRACT(EPOCH FROM (l.waktu_akses - LAG(l.waktu_akses) 
        OVER (PARTITION BY l.nim ORDER BY l.waktu_akses)))) as avg_session_gap
FROM log_akses l
JOIN mahasiswa m ON l.nim = m.nim
WHERE l.waktu_akses >= '2024-01-01'
GROUP BY 1, 2, 3, 4
ORDER BY total_akses DESC;

-- Identifikasi masalah:
-- 1. Sequential scan pada tabel besar
-- 2. Expensive window function
-- 3. Complex aggregation
-- 4. Large result set sorting
```

### 2. Optimization Steps

```sql
-- Step 1: Index untuk filtering
CREATE INDEX idx_log_akses_waktu_nim ON log_akses(waktu_akses, nim);
CREATE INDEX idx_log_akses_modul_waktu ON log_akses(modul, waktu_akses);

-- Step 2: Simplify query atau break into parts
-- Part 1: Basic aggregation
EXPLAIN ANALYZE
SELECT 
    DATE_TRUNC('month', l.waktu_akses) as bulan,
    m.jurusan,
    l.modul,
    COUNT(*) as total_akses,
    COUNT(DISTINCT l.nim) as unique_users
FROM log_akses l
JOIN mahasiswa m ON l.nim = m.nim
WHERE l.waktu_akses >= '2024-01-01'
GROUP BY 1, 2, 3
ORDER BY total_akses DESC;

-- Step 3: Use materialized view untuk laporan berkala
CREATE MATERIALIZED VIEW mv_monthly_access_stats AS
SELECT 
    DATE_TRUNC('month', l.waktu_akses) as bulan,
    m.jurusan,
    l.modul,
    COUNT(*) as total_akses,
    COUNT(DISTINCT l.nim) as unique_users
FROM log_akses l
JOIN mahasiswa m ON l.nim = m.nim
GROUP BY 1, 2, 3;

-- Refresh materialized view secara berkala
REFRESH MATERIALIZED VIEW mv_monthly_access_stats;

-- Query dari materialized view (jauh lebih cepat)
EXPLAIN ANALYZE
SELECT * FROM mv_monthly_access_stats
WHERE bulan >= '2024-01-01'
ORDER BY total_akses DESC;
```

---

## Best Practices dan Guidelines

### 1. Reading Execution Plans Systematically

```sql
-- Template untuk analisis sistematis execution plan
-- 1. Jalankan EXPLAIN ANALYZE dengan opsi lengkap
EXPLAIN (ANALYZE, BUFFERS, TIMING, COSTS, VERBOSE)
SELECT /* Your query here */;

-- 2. Checklist analisis:
--    a. Node cost tertinggi (bottleneck)
--    b. Estimasi vs actual rows (akurasi statistik)
--    c. Operasi scan (seq scan pada tabel besar = merah)
--    d. Join algorithms (nested loop pada data besar = merah)
--    e. Sort operations (external sort = kuning)
--    f. Buffer usage (banyak disk read = kuning)
--    g. Timing (operasi > 50% total time = fokus optimasi)
```

### 2. Index Strategy Based on Execution Plans

```sql
-- Berdasarkan analisis execution plan, buat index yang tepat

-- Untuk WHERE clause frequent
CREATE INDEX idx_table_filter_col ON table_name(filter_column);

-- Untuk JOIN operations
CREATE INDEX idx_table_join_col ON table_name(join_column);

-- Untuk ORDER BY operations
CREATE INDEX idx_table_sort_cols ON table_name(sort_col1, sort_col2);

-- Untuk covering queries (include semua kolom yang diperlukan)
CREATE INDEX idx_table_covering ON table_name(filter_col, join_col) 
INCLUDE (select_col1, select_col2);

-- Untuk partial index (kondisi specific)
CREATE INDEX idx_table_partial ON table_name(column)
WHERE condition = 'specific_value';
```

---

## Advanced Analysis Tools

### 1. Using pg_stat_statements untuk Query Monitoring

```sql
-- Enable pg_stat_statements extension (perlu restart PostgreSQL)
-- Tambahkan di postgresql.conf: shared_preload_libraries = 'pg_stat_statements'
-- CREATE EXTENSION pg_stat_statements;

-- Contoh query untuk monitoring (jika extension tersedia)
/*
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
*/
```

### 2. Custom Analysis Functions

```sql
-- Function untuk analisis cepat query performance
CREATE OR REPLACE FUNCTION analyze_query_performance(query_text TEXT)
RETURNS TABLE(
    operation TEXT,
    total_cost NUMERIC,
    rows_estimate BIGINT,
    analysis TEXT
) AS $$
BEGIN
    -- Simplified analysis framework
    -- Dalam implementasi nyata, ini bisa lebih kompleks
    RETURN QUERY
    SELECT 
        'Analysis'::TEXT,
        0.0::NUMERIC,
        0::BIGINT,
        'Run EXPLAIN (ANALYZE, BUFFERS) on your query for detailed analysis'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Penggunaan
SELECT * FROM analyze_query_performance('SELECT * FROM mahasiswa WHERE angkatan = 2023');
```

---

## Cleanup dan Maintenance

```sql
-- Cleanup indexes yang tidak perlu
-- DROP INDEX IF EXISTS idx_mahasiswa_covering;
-- DROP INDEX IF EXISTS idx_log_akses_waktu_nim;

-- Maintenance commands
VACUUM ANALYZE mahasiswa;
VACUUM ANALYZE krs;
VACUUM ANALYZE log_akses;

-- Reindex untuk optimasi
REINDEX TABLE mahasiswa;
REINDEX TABLE krs;

-- Drop materialized view
-- DROP MATERIALIZED VIEW IF EXISTS mv_monthly_access_stats;

-- Reset semua parameter ke default
RESET ALL;
```

---

## Kesimpulan dan Cheat Sheet

### Quick Reference untuk Membaca Execution Plan:

```sql
-- 1. SELALU gunakan EXPLAIN ANALYZE untuk data nyata
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

-- 2. Fokus pada node dengan cost/time tertinggi
-- 3. Perhatikan estimasi vs actual rows (jika jauh berbeda = statistik buruk)
-- 4. Red flags yang perlu diperhatikan:
--    - Seq Scan pada tabel > 10K rows
--    - Nested Loop Join pada data besar (> 1000 rows)
--    - Sort operation dengan temp files
--    - Hash operation dengan batches > 1
--    - Buffer misses tinggi (banyak disk reads)

-- 5. Hierarchy optimasi (dari yang paling impactful):
--    a. Index untuk eliminating Seq Scan
--    b. Join order optimization
--    c. Work_mem tuning untuk sorts/hashes
--    d. Query rewriting
--    e. Materialized views untuk complex aggregations
```

### Common Patterns dan Solutions:

```sql
-- Pattern: Seq Scan pada WHERE clause
-- Solution: CREATE INDEX ON table(column);

-- Pattern: Nested Loop pada data besar  
-- Solution: Ensure proper indexes pada join columns

-- Pattern: Sort dengan disk usage
-- Solution: Increase work_mem atau optimize ORDER BY

-- Pattern: Hash Join dengan multiple batches
-- Solution: Increase work_mem atau rethink query

-- Pattern: Inaccurate row estimates
-- Solution: ANALYZE table; atau increase statistics target
```

---

**Catatan:** Script ini memberikan implementasi komprehensif dari konsep analisis EXPLAIN dan EXPLAIN ANALYZE yang dibahas dalam Modul Week 5. Setiap section dapat dijalankan secara bertahap untuk memahami cara membaca dan menganalisis execution plan PostgreSQL untuk optimasi performa query.