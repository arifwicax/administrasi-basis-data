# Implementasi PostgreSQL - Algoritma Akses Data dan Index-Only Scan

## Week 3 - Administrasi Basis Data

---

## Setup Database dan Tabel

### 1. Membuat Database dan Tabel Mahasiswa

```sql
-- Membuat database (optional, bisa menggunakan database existing)
CREATE DATABASE db_akademik;

-- Menggunakan database
\c db_akademik;

-- Membuat tabel mahasiswa
CREATE TABLE mahasiswa (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    nim VARCHAR(20) UNIQUE NOT NULL,
    angkatan INTEGER NOT NULL,
    jurusan VARCHAR(50) NOT NULL,
    ipk NUMERIC(3,2),
    status VARCHAR(20) DEFAULT 'Aktif'
);
```

### 2. Insert Data Sample

```sql
-- Insert data untuk demonstrasi
INSERT INTO mahasiswa (nama, nim, angkatan, jurusan, ipk, status) VALUES
('Ahmad Rizki', '2021001', 2021, 'Informatika', 3.25, 'Aktif'),
('Sari Dewi', '2021002', 2021, 'Informatika', 3.67, 'Aktif'),
('Budi Santoso', '2022001', 2022, 'Sistem Informasi', 3.45, 'Aktif'),
('Rina Kusuma', '2022002', 2022, 'Informatika', 3.78, 'Aktif'),
('Dani Kurnia', '2023001', 2023, 'Informatika', 3.56, 'Aktif'),
('Lisa Permata', '2023002', 2023, 'Sistem Informasi', 3.89, 'Aktif'),
('Ferry Ahmad', '2023003', 2023, 'Informatika', 3.34, 'Aktif'),
('Nina Sari', '2024001', 2024, 'Informatika', 3.67, 'Aktif'),
('Eko Prasetyo', '2024002', 2024, 'Sistem Informasi', 3.45, 'Aktif'),
('Maya Indah', '2024003', 2024, 'Informatika', 3.78, 'Aktif');

-- Insert lebih banyak data untuk demonstrasi yang lebih realistis
INSERT INTO mahasiswa (nama, nim, angkatan, jurusan, ipk, status)
SELECT 
    'Mahasiswa ' || generate_series,
    '202' || (1 + (generate_series % 4)) || LPAD(generate_series::text, 3, '0'),
    2021 + (generate_series % 4),
    CASE WHEN generate_series % 2 = 0 THEN 'Informatika' ELSE 'Sistem Informasi' END,
    ROUND((2.5 + (random() * 1.5))::numeric, 2),
    'Aktif'
FROM generate_series(11, 1000);
```

---

## Demonstrasi Sequential Scan

### 1. Query Tanpa Index (Sequential Scan)

```sql
-- Query yang akan menggunakan Sequential Scan
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM mahasiswa WHERE angkatan = 2023;

-- Hasil yang diharapkan:
-- Seq Scan on mahasiswa (cost=0.00..xx.xx rows=xx width=xx) (actual time=xx..xx rows=xx loops=1)
--   Filter: (angkatan = 2023)
--   Rows Removed by Filter: xxx
```

### 2. Query dengan Selectivity Tinggi

```sql
-- Query yang mengambil banyak data (Sequential Scan lebih efisien)
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE angkatan IN (2021, 2022, 2023);

-- Menampilkan statistik tabel
SELECT 
    schemaname,
    tablename, 
    n_tup_ins as "Insert",
    n_tup_upd as "Update", 
    n_tup_del as "Delete",
    n_live_tup as "Live Tuples",
    n_dead_tup as "Dead Tuples"
FROM pg_stat_user_tables 
WHERE tablename = 'mahasiswa';
```

---

## Implementasi dan Demonstrasi Index

### 1. Membuat B-Tree Index

```sql
-- Membuat index B-Tree pada kolom angkatan
CREATE INDEX idx_mahasiswa_angkatan ON mahasiswa(angkatan);

-- Membuat index composite untuk Index-Only Scan
CREATE INDEX idx_mahasiswa_angkatan_nama ON mahasiswa(angkatan, nama);

-- Membuat index pada nim (unique)
CREATE INDEX idx_mahasiswa_nim ON mahasiswa(nim);

-- Melihat index yang telah dibuat
\d mahasiswa
```

### 2. Demonstrasi Index Scan

```sql
-- Query yang akan menggunakan Index Scan
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE angkatan = 2023;

-- Query dengan selectivity rendah
EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, nim FROM mahasiswa WHERE angkatan = 2023;

-- Comparing cost dengan dan tanpa index
SET enable_indexscan = OFF;
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE angkatan = 2023;

SET enable_indexscan = ON;
```

### 3. Demonstrasi Index-Only Scan

```sql
-- Query yang berpeluang menggunakan Index-Only Scan
-- (hanya mengambil kolom yang ada di index)
EXPLAIN (ANALYZE, BUFFERS)
SELECT angkatan, nama FROM mahasiswa WHERE angkatan = 2023;

-- Query dengan lebih banyak kolom dari index
EXPLAIN (ANALYZE, BUFFERS)
SELECT angkatan, nama FROM mahasiswa 
WHERE angkatan BETWEEN 2022 AND 2024;

-- Memastikan visibility map up-to-date untuk Index-Only Scan
VACUUM ANALYZE mahasiswa;

-- Test lagi setelah VACUUM
EXPLAIN (ANALYZE, BUFFERS)
SELECT angkatan, nama FROM mahasiswa WHERE angkatan = 2023;
```

---

## Demonstrasi Bitmap Heap Scan

### 1. Query dengan Selectivity Menengah

```sql
-- Query yang akan menggunakan Bitmap Heap Scan
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE angkatan IN (2022, 2023);

-- Bitmap scan dengan multiple conditions
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa 
WHERE angkatan = 2023 AND jurusan = 'Informatika';
```

### 2. Membuat Index untuk Mendukung Bitmap Scan

```sql
-- Index pada jurusan
CREATE INDEX idx_mahasiswa_jurusan ON mahasiswa(jurusan);

-- Test kombinasi index
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa 
WHERE angkatan = 2023 AND jurusan = 'Informatika';
```

---

## Analisis Selectivity

### 1. Melihat Distribusi Data

```sql
-- Analisis distribusi angkatan
SELECT angkatan, COUNT(*) as jumlah_mahasiswa,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM mahasiswa), 2) as persentase
FROM mahasiswa 
GROUP BY angkatan 
ORDER BY angkatan;

-- Analisis distribusi jurusan
SELECT jurusan, COUNT(*) as jumlah_mahasiswa,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM mahasiswa), 2) as persentase
FROM mahasiswa 
GROUP BY jurusan;
```

### 2. Test Query dengan Berbagai Selectivity

```sql
-- Selectivity rendah (sedikit data)
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE nim = '2023001';

-- Selectivity menengah 
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE angkatan = 2023;

-- Selectivity tinggi (banyak data)
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE ipk > 2.0;
```

---

## Perbandingan Performa dengan EXPLAIN ANALYZE

### 1. Benchmark Query Tanpa Index

```sql
-- Disable all index scans temporarily
SET enable_indexscan = OFF;
SET enable_indexonlyscan = OFF;
SET enable_bitmapscan = OFF;

-- Test query performance
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT nama FROM mahasiswa WHERE angkatan = 2023;

-- Re-enable index scans
SET enable_indexscan = ON;
SET enable_indexonlyscan = ON;
SET enable_bitmapscan = ON;
```

### 2. Benchmark Query dengan Index

```sql
-- Test dengan semua optimasi aktif
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT nama FROM mahasiswa WHERE angkatan = 2023;

-- Test Index-Only Scan
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT angkatan, nama FROM mahasiswa WHERE angkatan = 2023;
```

---

---

## Implementasi Hash Index

### 1. Membuat Hash Index

Hash index sangat efisien untuk pencarian equality (=), namun tidak mendukung range query.

```sql
-- 1. Hash index untuk kolom status
CREATE INDEX idx_mahasiswa_status_hash ON mahasiswa USING hash(status);

-- 2. Hash index untuk kolom jenis_kelamin  
CREATE INDEX idx_mahasiswa_gender_hash ON mahasiswa USING hash(jenis_kelamin);

-- 3. Hash index untuk kolom angkatan
CREATE INDEX idx_mahasiswa_angkatan_hash ON mahasiswa USING hash(angkatan);
```

### 2. Testing Efektivitas Hash Index

#### A. Query yang Efisien dengan Hash Index

```sql
-- Test 1: Equality search pada status
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM mahasiswa WHERE status = 'Aktif';

-- Expected: Index Scan using idx_mahasiswa_status_hash

-- Test 2: Equality search pada jenis_kelamin
EXPLAIN (ANALYZE, BUFFERS, TIMING) 
SELECT nim, nama FROM mahasiswa WHERE jenis_kelamin = 'L';

-- Test 3: Multiple equality conditions
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT COUNT(*) FROM mahasiswa 
WHERE status = 'Aktif' AND jenis_kelamin = 'P';
```

#### B. Query yang Tidak Efisien dengan Hash Index

```sql
-- Hash index TIDAK akan digunakan untuk query berikut:

-- 1. Range query
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE angkatan > 2020;

-- 2. Pattern matching
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM mahasiswa WHERE status LIKE 'A%';

-- 3. Inequality conditions
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE status != 'Aktif';

-- 4. Sorting operations
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa ORDER BY status;
```

### 3. Perbandingan Performa Hash vs B-Tree Index

```sql
-- Buat B-Tree index untuk perbandingan
CREATE INDEX idx_mahasiswa_status_btree ON mahasiswa(status);

-- Drop hash index sementara untuk test B-Tree
DROP INDEX idx_mahasiswa_status_hash;

-- Test performa B-Tree
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM mahasiswa WHERE status = 'Aktif';

-- Recreate hash index
CREATE INDEX idx_mahasiswa_status_hash ON mahasiswa USING hash(status);

-- Drop B-Tree index
DROP INDEX idx_mahasiswa_status_btree;

-- Test performa Hash Index
EXPLAIN (ANALYZE, BUFFERS, TIMING) 
SELECT * FROM mahasiswa WHERE status = 'Aktif';
```

### 4. Analisis Hash Index Performance

```sql
-- Monitor hash index usage
SELECT 
    schemaname,
    tablename, 
    indexname,
    idx_scan as "Index Scans",
    idx_tup_read as "Tuples Read",
    idx_tup_fetch as "Tuples Fetched"
FROM pg_stat_user_indexes 
WHERE indexname LIKE '%_hash';

-- Analisis ukuran hash index
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as "Index Size"
FROM pg_indexes 
WHERE indexdef LIKE '%USING hash%'
AND schemaname = 'public';
```

### 5. Demonstrasi Hash Function Concept

```sql
-- Simulasi sederhana hash function menggunakan modulo
-- (untuk pemahaman konsep, bukan implementasi aktual PostgreSQL)

CREATE TEMP TABLE hash_demo AS
SELECT 
    nim,
    nim::integer % 10 as hash_bucket,
    'Bucket ' || (nim::integer % 10) as bucket_label
FROM mahasiswa 
LIMIT 20;

-- Lihat distribusi data ke bucket
SELECT 
    hash_bucket,
    COUNT(*) as record_count,
    array_agg(nim ORDER BY nim) as nims_in_bucket
FROM hash_demo
GROUP BY hash_bucket
ORDER BY hash_bucket;

-- Contoh collision detection
SELECT 
    hash_bucket,
    COUNT(*) as collision_count
FROM hash_demo
GROUP BY hash_bucket
HAVING COUNT(*) > 1
ORDER BY collision_count DESC;
```

### 6. Best Practices Hash Index

```sql
-- 1. Hash index ideal untuk kolom dengan high cardinality dan equality search
SELECT 
    column_name,
    n_distinct,
    most_common_vals,
    most_common_freqs
FROM pg_stats 
WHERE tablename = 'mahasiswa'
AND column_name IN ('status', 'jenis_kelamin', 'angkatan');

-- 2. Monitor query patterns untuk menentukan kandidat hash index
SELECT 
    query,
    calls,
    mean_time,
    rows
FROM pg_stat_statements 
WHERE query LIKE '%WHERE%=%'
AND query NOT LIKE '%>%'
AND query NOT LIKE '%<%'
ORDER BY calls DESC;
```

### 7. Maintenance Hash Index

```sql
-- Rebuild hash index jika perlu
REINDEX INDEX idx_mahasiswa_status_hash;

-- Drop hash index yang tidak terpakai
-- (Analisis dulu dengan pg_stat_user_indexes)
-- DROP INDEX idx_mahasiswa_gender_hash;

-- Vacuum untuk membersihkan space
VACUUM ANALYZE mahasiswa;
```

---

## Monitoring dan Statistik Index

### 1. Melihat Penggunaan Index

```sql
-- Statistik penggunaan index
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    idx_tup_read, 
    idx_tup_fetch,
    idx_scan
FROM pg_stat_user_indexes 
WHERE tablename = 'mahasiswa';

-- Reset statistik untuk monitoring fresh
SELECT pg_stat_reset();
```

### 2. Analisis Ukuran Index

```sql
-- Melihat ukuran tabel dan index
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as "Total Size",
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as "Table Size"
FROM pg_tables 
WHERE tablename = 'mahasiswa';

-- Melihat ukuran individual index
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(schemaname||'.'||indexname)) as "Index Size"
FROM pg_indexes 
WHERE tablename = 'mahasiswa';
```

---

## Praktikum dan Tugas

### 1. Latihan Mandiri

```sql
-- Latihan 1: Buat query dan analisis execution plan
EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, ipk FROM mahasiswa 
WHERE angkatan = 2022 AND ipk > 3.5;

-- Latihan 2: Test different index strategies
-- Drop existing index dan buat composite index berbeda
DROP INDEX idx_mahasiswa_angkatan_nama;
CREATE INDEX idx_mahasiswa_ipk_angkatan ON mahasiswa(ipk, angkatan);

-- Test query lagi
EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, ipk FROM mahasiswa 
WHERE angkatan = 2022 AND ipk > 3.5;
```

### 2. Eksperimen dengan Data Besar

```sql
-- Menambah lebih banyak data untuk test performa
INSERT INTO mahasiswa (nama, nim, angkatan, jurusan, ipk, status)
SELECT 
    'Student ' || generate_series,
    'STU' || LPAD(generate_series::text, 6, '0'),
    2020 + (generate_series % 5),
    CASE 
        WHEN generate_series % 3 = 0 THEN 'Informatika' 
        WHEN generate_series % 3 = 1 THEN 'Sistem Informasi'
        ELSE 'Teknik Komputer'
    END,
    ROUND((2.0 + (random() * 2.0))::numeric, 2),
    CASE WHEN generate_series % 10 = 0 THEN 'Lulus' ELSE 'Aktif' END
FROM generate_series(1001, 10000);

-- Update statistik setelah insert besar
ANALYZE mahasiswa;

-- Test performa dengan data yang lebih besar
EXPLAIN (ANALYZE, BUFFERS)
SELECT nama FROM mahasiswa WHERE angkatan = 2023;
```

---

## Cleanup dan Maintenance

### 1. Maintenance Index

```sql
-- Reindex untuk optimasi
REINDEX TABLE mahasiswa;

-- Vacuum untuk cleanup
VACUUM ANALYZE mahasiswa;

-- Melihat index yang tidak terpakai
SELECT 
    schemaname, 
    tablename, 
    indexname, 
    idx_scan,
    pg_size_pretty(pg_relation_size(schemaname||'.'||indexname)) as size
FROM pg_stat_user_indexes 
WHERE tablename = 'mahasiswa' AND idx_scan = 0;
```

### 2. Drop Index yang Tidak Diperlukan

```sql
-- Contoh drop index yang tidak terpakai
-- DROP INDEX idx_mahasiswa_status_hash;

-- Verifikasi performa setelah drop index
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE status = 'Aktif';
```

---

## Kesimpulan dan Best Practices

### Rangkuman Hasil Eksperimen:

1. **Sequential Scan** cocok untuk:
   - Query yang mengambil sebagian besar data dari tabel
   - Tabel kecil
   - Query tanpa kondisi WHERE yang selektif

2. **Index Scan** cocok untuk:
   - Query dengan kondisi WHERE yang sangat selektif
   - Pencarian berdasarkan primary key atau unique key

3. **Index-Only Scan** cocok untuk:
   - Query yang hanya mengambil kolom yang ada di index
   - Sangat efisien karena tidak perlu mengakses tabel utama

4. **Bitmap Heap Scan** cocok untuk:
   - Query dengan selectivity menengah
   - Kombinasi multiple index

### Tips Optimasi:

```sql
-- Selalu gunakan EXPLAIN ANALYZE untuk verifikasi
-- Perhatikan actual time vs estimated cost
-- Monitor penggunaan index dengan pg_stat_user_indexes
-- Lakukan VACUUM ANALYZE secara berkala
-- Pertimbangkan composite index untuk query kompleks
```

---

**Catatan:** Script ini memberikan implementasi praktis dari konsep-konsep yang dibahas dalam Modul Week 3 tentang Algoritma Akses Data dan Index-Only Scan. Setiap section dapat dijalankan secara bertahap untuk memahami perbedaan performa dan perilaku PostgreSQL dalam memilih algoritma akses data.