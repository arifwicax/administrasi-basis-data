# Implementasi PostgreSQL - Strategi Pembuatan Indeks dan Optimasi Query Pendek

## Week 6 - Administrasi Basis Data

---

## Setup Database dan Tabel untuk Demonstrasi Index Strategy

### 1. Membuat Database dan Tabel Sample

```sql
-- Membuat database untuk demonstrasi index strategy
CREATE DATABASE db_index_strategy;

-- Menggunakan database
\c db_index_strategy;

-- Membuat tabel mahasiswa dengan berbagai karakteristik kolom
CREATE TABLE mahasiswa (
    id SERIAL PRIMARY KEY,
    nim VARCHAR(15) UNIQUE NOT NULL,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    angkatan INTEGER NOT NULL,
    jurusan VARCHAR(50) NOT NULL,
    program_studi VARCHAR(100) NOT NULL,
    jenis_kelamin CHAR(1) CHECK (jenis_kelamin IN ('L', 'P')),
    tanggal_lahir DATE,
    ipk NUMERIC(3,2),
    status VARCHAR(20) DEFAULT 'Aktif',
    alamat TEXT,
    no_telepon VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Membuat tabel krs untuk demonstrasi foreign key dan join queries
CREATE TABLE krs (
    id_krs SERIAL PRIMARY KEY,
    nim VARCHAR(15) NOT NULL,
    kode_mk VARCHAR(10) NOT NULL,
    nama_mk VARCHAR(100) NOT NULL,
    dosen_pengampu VARCHAR(100),
    semester_ambil INTEGER NOT NULL,
    tahun_akademik VARCHAR(10) NOT NULL,
    sks INTEGER NOT NULL,
    nilai CHAR(2) CHECK (nilai IN ('A','B+','B','C+','C','D','E','F')),
    tanggal_ambil DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Membuat tabel log_aktivitas untuk demonstrasi data dengan volume besar
CREATE TABLE log_aktivitas (
    id_log BIGSERIAL PRIMARY KEY,
    nim VARCHAR(15),
    aktivitas VARCHAR(100),
    modul VARCHAR(50),
    waktu_akses TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    status_code INTEGER,
    response_time_ms INTEGER
);

-- Membuat tabel dosen untuk demonstrasi index pada berbagai jenis data
CREATE TABLE dosen (
    id_dosen SERIAL PRIMARY KEY,
    nidn VARCHAR(20) UNIQUE NOT NULL,
    nama_dosen VARCHAR(100) NOT NULL,
    email_dosen VARCHAR(100) UNIQUE,
    departemen VARCHAR(50),
    jabatan VARCHAR(50),
    status_dosen VARCHAR(20) DEFAULT 'Aktif',
    gaji_pokok NUMERIC(12,2),
    tanggal_bergabung DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Insert Data dengan Karakteristik Selectivity yang Berbeda

```sql
-- Insert mahasiswa dengan distribusi data yang realistis
INSERT INTO mahasiswa (nim, nama, email, angkatan, jurusan, program_studi, jenis_kelamin, tanggal_lahir, ipk, status, alamat, no_telepon)
SELECT 
    -- NIM yang unik (high selectivity)
    '231' || LPAD(generate_series::text, 7, '0'),
    -- Nama yang relatif unik
    'Mahasiswa ' || generate_series,
    -- Email yang unik (high selectivity)  
    'mhs' || generate_series || '@kampus.ac.id',
    -- Angkatan (medium selectivity - 4 nilai berbeda)
    2020 + (generate_series % 4),
    -- Jurusan (low selectivity - hanya 3 nilai)
    CASE 
        WHEN generate_series % 3 = 0 THEN 'Teknik'
        WHEN generate_series % 3 = 1 THEN 'MIPA' 
        ELSE 'Ekonomi'
    END,
    -- Program studi (medium selectivity - 6 nilai)
    CASE 
        WHEN generate_series % 6 = 0 THEN 'Informatika'
        WHEN generate_series % 6 = 1 THEN 'Sistem Informasi'
        WHEN generate_series % 6 = 2 THEN 'Teknik Elektro'
        WHEN generate_series % 6 = 3 THEN 'Matematika'
        WHEN generate_series % 6 = 4 THEN 'Fisika'
        ELSE 'Akuntansi'
    END,
    -- Jenis kelamin (very low selectivity - hanya 2 nilai)
    CASE WHEN generate_series % 2 = 0 THEN 'L' ELSE 'P' END,
    -- Tanggal lahir
    '1998-01-01'::date + (generate_series % 1095) * interval '1 day',
    -- IPK
    ROUND((2.5 + (random() * 1.5))::numeric, 2),
    -- Status (low selectivity - mayoritas Aktif)
    CASE 
        WHEN generate_series % 50 = 0 THEN 'Lulus'
        WHEN generate_series % 100 = 0 THEN 'Cuti'
        ELSE 'Aktif' 
    END,
    -- Alamat
    'Jl. Contoh No. ' || (generate_series % 1000 + 1),
    -- No telepon
    '08' || LPAD((1000000000 + generate_series % 900000000)::text, 10, '0')
FROM generate_series(1, 50000);

-- Insert data dosen
INSERT INTO dosen (nidn, nama_dosen, email_dosen, departemen, jabatan, status_dosen, gaji_pokok, tanggal_bergabung)
SELECT 
    '11' || LPAD(generate_series::text, 8, '0'),
    'Dosen ' || generate_series,
    'dosen' || generate_series || '@kampus.ac.id',
    CASE 
        WHEN generate_series % 3 = 0 THEN 'Teknik'
        WHEN generate_series % 3 = 1 THEN 'MIPA' 
        ELSE 'Ekonomi'
    END,
    CASE 
        WHEN generate_series % 4 = 0 THEN 'Asisten Ahli'
        WHEN generate_series % 4 = 1 THEN 'Lektor'
        WHEN generate_series % 4 = 2 THEN 'Lektor Kepala'
        ELSE 'Guru Besar'
    END,
    'Aktif',
    4000000 + (random() * 6000000)::numeric(12,2),
    '2000-01-01'::date + (generate_series % 6000) * interval '1 day'
FROM generate_series(1, 500);

-- Insert KRS dengan foreign key relationship
INSERT INTO krs (nim, kode_mk, nama_mk, dosen_pengampu, semester_ambil, tahun_akademik, sks, nilai)
SELECT 
    m.nim,
    'MK' || LPAD((1 + (random() * 200)::int)::text, 3, '0'),
    'Mata Kuliah ' || (1 + (random() * 200)::int),
    d.nama_dosen,
    1 + (random() * 8)::int,
    '202' || (0 + (random() * 4)::int) || '/202' || (1 + (random() * 4)::int),
    (ARRAY[2,3,4])[1 + (random() * 2)::int],
    (ARRAY['A','B+','B','C+','C','D','E'])[1 + (random() * 6)::int]
FROM mahasiswa m 
CROSS JOIN generate_series(1, (2 + (random() * 6)::int)) -- 2-8 mata kuliah per mahasiswa
CROSS JOIN LATERAL (SELECT nama_dosen FROM dosen ORDER BY random() LIMIT 1) d
ORDER BY random()
LIMIT 200000;

-- Insert log aktivitas dalam volume besar
INSERT INTO log_aktivitas (nim, aktivitas, modul, waktu_akses, ip_address, user_agent, status_code, response_time_ms)
SELECT 
    m.nim,
    (ARRAY['Login','Logout','View Transcript','Download Document','Submit Assignment'])[1 + (random() * 4)::int],
    (ARRAY['Portal','E-Learning','Library','Finance','Academic'])[1 + (random() * 4)::int],
    CURRENT_TIMESTAMP - (random() * interval '180 days'),
    ('192.168.' || (1 + (random() * 254)::int) || '.' || (1 + (random() * 254)::int))::inet,
    'Mozilla/5.0 Browser ' || (1 + (random() * 10)::int),
    CASE 
        WHEN random() < 0.9 THEN 200 
        WHEN random() < 0.95 THEN 404
        ELSE 500 
    END,
    50 + (random() * 950)::int
FROM mahasiswa m
CROSS JOIN generate_series(1, (5 + (random() * 15)::int)) -- 5-20 log per mahasiswa
ORDER BY random()
LIMIT 500000;

-- Tambahkan foreign key constraints setelah data diinsert
ALTER TABLE krs ADD CONSTRAINT fk_krs_mahasiswa 
    FOREIGN KEY (nim) REFERENCES mahasiswa(nim);

-- Update statistik untuk optimizer
ANALYZE mahasiswa;
ANALYZE krs;
ANALYZE log_aktivitas; 
ANALYZE dosen;
```

---

## Demonstrasi Short Query vs Long Query

### 1. Contoh Short Query (Query Selektif)

```sql
-- Short Query 1: Pencarian berdasarkan NIM (sangat selektif)
-- Tanpa index terlebih dahulu
EXPLAIN (ANALYZE, BUFFERS) 
SELECT nama, email, program_studi 
FROM mahasiswa 
WHERE nim = '2310000001';

-- Short Query 2: Pencarian berdasarkan email (sangat selektif)
EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, nim, program_studi
FROM mahasiswa
WHERE email = 'mhs1@kampus.ac.id';

-- Short Query 3: Pencarian kombinasi yang selektif
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, k.nama_mk, k.nilai
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
WHERE m.nim = '2310000001' AND k.semester_ambil = 1;

-- Hasil: Kemungkinan menggunakan Sequential Scan karena belum ada index
-- Cost tinggi meski hanya mengambil sedikit data
```

### 2. Contoh Long Query (Query yang Memproses Banyak Data)

```sql
-- Long Query 1: Agregasi pada seluruh tabel (memproses banyak data)
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    jurusan,
    COUNT(*) as total_mahasiswa,
    AVG(ipk) as rata_ipk,
    MIN(ipk) as ipk_terendah,
    MAX(ipk) as ipk_tertinggi
FROM mahasiswa
GROUP BY jurusan;

-- Long Query 2: Join dengan agregasi besar
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    m.program_studi,
    COUNT(DISTINCT m.nim) as jumlah_mahasiswa,
    COUNT(k.id_krs) as total_mata_kuliah,
    ROUND(AVG(k.sks), 2) as rata_sks
FROM mahasiswa m
LEFT JOIN krs k ON m.nim = k.nim
GROUP BY m.program_studi
ORDER BY jumlah_mahasiswa DESC;

-- Long Query 3: Analisis data dengan window function
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    nama,
    ipk,
    jurusan,
    RANK() OVER (PARTITION BY jurusan ORDER BY ipk DESC) as ranking_jurusan,
    PERCENT_RANK() OVER (ORDER BY ipk DESC) as percentile
FROM mahasiswa
WHERE status = 'Aktif';

-- Hasil: Sequential Scan masuk akal karena memproses mayoritas data
-- Index mungkin tidak membantu secara signifikan
```

---

## Analisis Selectivity dan Dampaknya pada Index Strategy

### 1. Menganalisis Distribusi Data (Selectivity Analysis)

```sql
-- Analisis selectivity berbagai kolom
SELECT 'nim' as kolom, COUNT(DISTINCT nim) as unique_values, COUNT(*) as total_rows,
       ROUND(COUNT(DISTINCT nim) * 100.0 / COUNT(*), 2) as selectivity_pct
FROM mahasiswa
UNION ALL
SELECT 'email', COUNT(DISTINCT email), COUNT(*), 
       ROUND(COUNT(DISTINCT email) * 100.0 / COUNT(*), 2)
FROM mahasiswa
UNION ALL  
SELECT 'angkatan', COUNT(DISTINCT angkatan), COUNT(*),
       ROUND(COUNT(DISTINCT angkatan) * 100.0 / COUNT(*), 2)
FROM mahasiswa
UNION ALL
SELECT 'jurusan', COUNT(DISTINCT jurusan), COUNT(*),
       ROUND(COUNT(DISTINCT jurusan) * 100.0 / COUNT(*), 2)
FROM mahasiswa
UNION ALL
SELECT 'program_studi', COUNT(DISTINCT program_studi), COUNT(*),
       ROUND(COUNT(DISTINCT program_studi) * 100.0 / COUNT(*), 2)
FROM mahasiswa
UNION ALL
SELECT 'jenis_kelamin', COUNT(DISTINCT jenis_kelamin), COUNT(*),
       ROUND(COUNT(DISTINCT jenis_kelamin) * 100.0 / COUNT(*), 2)
FROM mahasiswa
UNION ALL
SELECT 'status', COUNT(DISTINCT status), COUNT(*),
       ROUND(COUNT(DISTINCT status) * 100.0 / COUNT(*), 2)
FROM mahasiswa
ORDER BY selectivity_pct DESC;

-- Hasil yang diharapkan (dari high ke low selectivity):
-- nim: ~100% (setiap baris unik)
-- email: ~100% (setiap baris unik) 
-- program_studi: ~16.67% (6 distinct values)
-- angkatan: ~8% (4 distinct values)
-- jurusan: ~6% (3 distinct values)
-- status: ~6% (3 distinct values)
-- jenis_kelamin: ~4% (2 distinct values)
```

### 2. Testing Query Performance pada Different Selectivity

```sql
-- Test 1: High Selectivity (nim) - Ideal untuk index
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM mahasiswa WHERE nim = '2310000001';

-- Test 2: Medium Selectivity (angkatan) - Perlu evaluasi
EXPLAIN (ANALYZE, BUFFERS, TIMING)  
SELECT * FROM mahasiswa WHERE angkatan = 2023;

-- Test 3: Low Selectivity (jenis_kelamin) - Index mungkin tidak efektif
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT * FROM mahasiswa WHERE jenis_kelamin = 'L';

-- Test 4: Very Low Selectivity (status) - Index kemungkinan tidak digunakan
EXPLAIN (ANALYZE, BUFFERS, TIMING) 
SELECT * FROM mahasiswa WHERE status = 'Aktif';
```

---

## Implementasi Index Strategy untuk Short Query

### 1. Primary Key dan Unique Index (Automatically Created)

```sql
-- Melihat index yang sudah ada (otomatis dari PRIMARY KEY dan UNIQUE)
SELECT 
    schemaname, tablename, indexname, indexdef
FROM pg_indexes 
WHERE tablename IN ('mahasiswa', 'dosen', 'krs')
ORDER BY tablename, indexname;

-- Test performa dengan existing indexes
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE id = 12345;

EXPLAIN (ANALYZE, BUFFERS)  
SELECT * FROM mahasiswa WHERE nim = '2310012345';

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM dosen WHERE nidn = '1100000100';
```

### 2. Index untuk High Selectivity Columns

```sql
-- Index pada email (high selectivity, sering digunakan untuk login)
CREATE INDEX idx_mahasiswa_email ON mahasiswa(email);

-- Test performa setelah index
EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, nim, program_studi FROM mahasiswa 
WHERE email = 'mhs12345@kampus.ac.id';

-- Index pada no_telepon (high selectivity)  
CREATE INDEX idx_mahasiswa_telepon ON mahasiswa(no_telepon);

-- Test query
EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, email FROM mahasiswa 
WHERE no_telepon = '08123456789';
```

### 3. Composite Index untuk Multi-column Filters

```sql
-- Composite index untuk kombinasi yang sering diquery bersama
CREATE INDEX idx_mahasiswa_angkatan_prodi ON mahasiswa(angkatan, program_studi);

-- Test composite index
EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, nim, ipk FROM mahasiswa 
WHERE angkatan = 2023 AND program_studi = 'Informatika';

-- Composite index dengan order yang berbeda untuk test
CREATE INDEX idx_mahasiswa_prodi_angkatan ON mahasiswa(program_studi, angkatan);

-- Test untuk melihat mana yang dipilih optimizer
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM mahasiswa 
WHERE program_studi = 'Informatika' AND angkatan = 2023;
```

### 4. Foreign Key Index untuk Join Optimization

```sql
-- Index pada foreign key untuk mempercepat join
CREATE INDEX idx_krs_nim ON krs(nim);

-- Test join performance sebelum dan sesudah index
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, COUNT(k.id_krs) as total_mk
FROM mahasiswa m
LEFT JOIN krs k ON m.nim = k.nim  
WHERE m.angkatan = 2023
GROUP BY m.nim, m.nama
LIMIT 10;
```

### 5. Covering Index untuk Index-Only Scan

```sql
-- Covering index yang menyertakan kolom yang sering di-SELECT
CREATE INDEX idx_mahasiswa_covering_basic ON mahasiswa(nim) 
INCLUDE (nama, email, program_studi);

-- Test index-only scan
EXPLAIN (ANALYZE, BUFFERS)
SELECT nim, nama, email, program_studi FROM mahasiswa 
WHERE nim = '2310012345';

-- Covering index untuk query yang sering digunakan
CREATE INDEX idx_mahasiswa_covering_search ON mahasiswa(email)
INCLUDE (nama, nim, program_studi, angkatan);

EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, nim, program_studi, angkatan FROM mahasiswa
WHERE email = 'mhs12345@kampus.ac.id';
```

---

## Analisis Kapan Index Membantu vs Tidak Membantu

### 1. Kondisi dimana Index Sangat Membantu

```sql
-- Case 1: High selectivity dengan exact match
CREATE INDEX idx_test_high_selectivity ON mahasiswa(nidn) WHERE nidn IS NOT NULL;

-- Test: Pencarian exact match pada kolom unique
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE nim = '2310001000';

-- Case 2: Range query dengan good selectivity
CREATE INDEX idx_mahasiswa_ipk ON mahasiswa(ipk);

EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, nim, ipk FROM mahasiswa 
WHERE ipk BETWEEN 3.5 AND 4.0;

-- Case 3: Join dengan proper foreign key index
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, k.nama_mk FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
WHERE m.nim = '2310001000';
```

### 2. Kondisi dimana Index Kurang Efektif

```sql
-- Case 1: Low selectivity - banyak data yang cocok
-- Index masih dibuat untuk demonstrasi
CREATE INDEX idx_mahasiswa_gender ON mahasiswa(jenis_kelamin);

-- Test: Filter yang menghasilkan ~50% data
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE jenis_kelamin = 'L';

-- PostgreSQL mungkin tetap memilih Sequential Scan

-- Case 2: Function-based query tanpa function index
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE UPPER(nama) LIKE 'MAHASISWA 1%';

-- Case 3: Complex WHERE dengan OR conditions  
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa 
WHERE nama LIKE '%1000%' OR alamat LIKE '%Jakarta%';
```

### 3. Comparison: Forced Index vs Optimizer Choice

```sql
-- Force index scan untuk comparison
SET enable_seqscan = OFF;

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM mahasiswa WHERE jenis_kelamin = 'L';

-- Reset dan lihat pilihan optimizer
SET enable_seqscan = ON;

EXPLAIN (ANALYZE, BUFFERS)  
SELECT * FROM mahasiswa WHERE jenis_kelamin = 'L';

-- Bandingkan mana yang lebih efisien dari segi:
-- - Total cost
-- - Actual time
-- - Buffer usage
```

---

## Optimasi Query Patterns untuk Short Queries

### 1. Login dan Authentication Patterns

```sql
-- Pattern 1: Login by email (very common short query)
CREATE INDEX idx_mahasiswa_email_optimized ON mahasiswa(email) 
WHERE status = 'Aktif'; -- Partial index

-- Test login query
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, nim, nama, program_studi FROM mahasiswa  
WHERE email = 'mhs10000@kampus.ac.id' AND status = 'Aktif';

-- Pattern 2: Session validation
CREATE INDEX idx_mahasiswa_session ON mahasiswa(nim, status);

EXPLAIN (ANALYZE, BUFFERS)
SELECT nama, email, program_studi FROM mahasiswa
WHERE nim = '2310010000' AND status = 'Aktif';
```

### 2. Search dan Lookup Patterns

```sql
-- Pattern 1: Auto-complete search
CREATE INDEX idx_mahasiswa_nama_prefix ON mahasiswa 
USING gin(nama gin_trgm_ops); -- Requires pg_trgm extension

-- Jika pg_trgm tidak tersedia, gunakan B-tree dengan pattern matching
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_mahasiswa_nama_pattern ON mahasiswa(nama varchar_pattern_ops);

-- Test PREFIX search
EXPLAIN (ANALYZE, BUFFERS)
SELECT nim, nama, program_studi FROM mahasiswa
WHERE nama LIKE 'Mahasiswa 100%'
LIMIT 10;

-- Pattern 2: Multi-field search
CREATE INDEX idx_mahasiswa_search_composite ON mahasiswa(program_studi, angkatan, status)
INCLUDE (nim, nama, email);

EXPLAIN (ANALYZE, BUFFERS)
SELECT nim, nama, email FROM mahasiswa
WHERE program_studi = 'Informatika' 
  AND angkatan = 2023 
  AND status = 'Aktif'
ORDER BY nama
LIMIT 20;
```

### 3. Reporting dan Analytics Patterns

```sql
-- Pattern 1: Quick stats lookup
CREATE INDEX idx_mahasiswa_stats ON mahasiswa(program_studi, status)
INCLUDE (ipk);

EXPLAIN (ANALYZE, BUFFERS) 
SELECT program_studi, COUNT(*) as total, AVG(ipk) as avg_ipk
FROM mahasiswa  
WHERE status = 'Aktif'
GROUP BY program_studi;

-- Pattern 2: Time-based queries (untuk log_aktivitas)
CREATE INDEX idx_log_waktu_nim ON log_aktivitas(waktu_akses, nim);

EXPLAIN (ANALYZE, BUFFERS)
SELECT nim, COUNT(*) as total_access FROM log_aktivitas
WHERE waktu_akses >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY nim
ORDER BY total_access DESC
LIMIT 10;
```

---

## Advanced Index Strategies

### 1. Partial Index untuk Conditional Data

```sql
-- Partial index hanya untuk mahasiswa aktif (yang sering diquery)
CREATE INDEX idx_mahasiswa_aktif_nama ON mahasiswa(nama) 
WHERE status = 'Aktif';

CREATE INDEX idx_mahasiswa_aktif_prodi ON mahasiswa(program_studi, angkatan)
WHERE status = 'Aktif';

-- Test partial index
EXPLAIN (ANALYZE, BUFFERS)
SELECT nim, nama FROM mahasiswa 
WHERE status = 'Aktif' AND nama LIKE 'Mahasiswa 200%';

-- Bandingkan dengan query tanpa kondisi status
EXPLAIN (ANALYZE, BUFFERS)  
SELECT nim, nama FROM mahasiswa 
WHERE nama LIKE 'Mahasiswa 200%';
```

### 2. Expression Index untuk Function-based Queries

```sql
-- Expression index untuk pencarian case-insensitive
CREATE INDEX idx_mahasiswa_nama_lower ON mahasiswa(LOWER(nama));

-- Test expression index
EXPLAIN (ANALYZE, BUFFERS)
SELECT nim, nama, email FROM mahasiswa
WHERE LOWER(nama) = 'mahasiswa 12345';

-- Expression index untuk date operations
CREATE INDEX idx_log_date_only ON log_aktivitas(DATE(waktu_akses));

EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM log_aktivitas  
WHERE DATE(waktu_akses) = '2024-01-15';
```

### 3. Multi-column Index Order Optimization

```sql
-- Test index column order impact
CREATE INDEX idx_test_order1 ON mahasiswa(angkatan, program_studi, status);
CREATE INDEX idx_test_order2 ON mahasiswa(status, program_studi, angkatan);

-- Query 1: Filter dimulai dari angkatan
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM mahasiswa 
WHERE angkatan = 2023 AND program_studi = 'Informatika' AND status = 'Aktif';

-- Query 2: Filter dimulai dari status  
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM mahasiswa
WHERE status = 'Aktif' AND program_studi = 'Informatika' AND angkatan = 2023;

-- Lihat index mana yang dipilih optimizer untuk setiap query
```

---

## Performance Monitoring dan Index Maintenance

### 1. Monitoring Index Usage

```sql
-- Statistik penggunaan index
SELECT 
    schemaname,
    tablename, 
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan,
    CASE WHEN idx_scan = 0 THEN 'UNUSED' 
         WHEN idx_scan < 10 THEN 'LOW USAGE'
         ELSE 'ACTIVE' 
    END as usage_status
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Index yang tidak pernah digunakan (kandidat untuk di-drop)
SELECT 
    schemaname, tablename, indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
FROM pg_stat_user_indexes  
WHERE idx_scan = 0 AND schemaname = 'public';
```

### 2. Index Size Analysis

```sql
-- Analisis ukuran index vs table
SELECT 
    t.tablename,
    pg_size_pretty(pg_total_relation_size(t.tablename::regclass)) as total_size,
    pg_size_pretty(pg_relation_size(t.tablename::regclass)) as table_size,
    pg_size_pretty(pg_indexes_size(t.tablename::regclass)) as indexes_size,
    ROUND(pg_indexes_size(t.tablename::regclass) * 100.0 / 
          pg_relation_size(t.tablename::regclass), 2) as index_ratio_pct
FROM pg_tables t
WHERE t.schemaname = 'public'  
ORDER BY pg_total_relation_size(t.tablename::regclass) DESC;

-- Detail ukuran setiap index
SELECT 
    indexname,
    tablename,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as size
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexname::regclass) DESC;
```

### 3. Index Maintenance Operations

```sql
-- Reindex untuk optimasi ruang dan performance
REINDEX INDEX idx_mahasiswa_email;

-- Atau reindex seluruh tabel
REINDEX TABLE mahasiswa;

-- VACUUM untuk cleanup dan update statistics
VACUUM ANALYZE mahasiswa;

-- Monitoring bloat pada index (perkiraan)
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as size,
    CASE 
        WHEN pg_relation_size(indexname::regclass) = 0 THEN 0
        ELSE ROUND(
            100 * (pg_relation_size(indexname::regclass) - 
                   pg_relation_size(indexname::regclass, 'main')) /
            pg_relation_size(indexname::regclass)::numeric, 2
        )
    END as estimated_bloat_pct
FROM pg_indexes 
WHERE schemaname = 'public' AND tablename = 'mahasiswa';
```

---

## Troubleshooting Common Index Issues

### 1. Index Not Being Used

```sql
-- Problem: Index tersedia tapi tidak digunakan
CREATE INDEX idx_debug_status ON mahasiswa(status);

-- Query dengan selectivity rendah - index mungkin tidak digunakan
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT * FROM mahasiswa WHERE status = 'Aktif';

-- Debugging steps:
-- 1. Check cost estimates
-- 2. Force index usage untuk comparison
SET enable_seqscan = OFF;
EXPLAIN (ANALYZE, BUFFERS, COSTS)  
SELECT * FROM mahasiswa WHERE status = 'Aktif';
SET enable_seqscan = ON;

-- 3. Check statistics accuracy
SELECT tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE tablename = 'mahasiswa' AND attname = 'status';
```

### 2. Wrong Index Column Order

```sql
-- Problem: Index column order tidak optimal
CREATE INDEX idx_debug_wrong_order ON krs(semester_ambil, nim, kode_mk);
CREATE INDEX idx_debug_right_order ON krs(nim, kode_mk, semester_ambil);

-- Query yang lebih cocok dengan right_order index
EXPLAIN (ANALYZE, BUFFERS)
SELECT nama_mk, nilai FROM krs  
WHERE nim = '2310001000' AND kode_mk = 'MK001';

-- Lihat index mana yang dipilih
```

### 3. Missing Composite Index

```sql
-- Problem: Query multi-kolom tanpa composite index
-- Current: hanya single column index
-- EXPLAIN query yang membutuhkan filter banyak kolom
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT * FROM mahasiswa 
WHERE angkatan = 2023 
  AND program_studi = 'Informatika' 
  AND status = 'Aktif'
  AND jenis_kelamin = 'L';

-- Solution: Buat composite index dengan urutan yang tepat
CREATE INDEX idx_mahasiswa_multifilter ON mahasiswa(
    angkatan,           -- Highest selectivity first 
    program_studi,      -- Medium selectivity
    status,             -- Lower selectivity
    jenis_kelamin       -- Lowest selectivity
);

-- Test improvement
EXPLAIN (ANALYZE, BUFFERS, COSTS)
SELECT * FROM mahasiswa  
WHERE angkatan = 2023 
  AND program_studi = 'Informatika' 
  AND status = 'Aktif'
  AND jenis_kelamin = 'L';
```

---

## Best Practices Implementation

### 1. Index Naming Convention

```sql
-- Good naming convention untuk index
-- Format: idx_[table]_[columns]_[type]

-- Primary access patterns
CREATE INDEX idx_mahasiswa_nim_lookup ON mahasiswa(nim);
CREATE INDEX idx_mahasiswa_email_lookup ON mahasiswa(email);

-- Join patterns  
CREATE INDEX idx_krs_nim_fk ON krs(nim);
CREATE INDEX idx_krs_nim_mk_composite ON krs(nim, kode_mk);

-- Covering patterns
CREATE INDEX idx_mahasiswa_search_covering ON mahasiswa(program_studi) 
INCLUDE (nim, nama, angkatan);

-- Partial patterns
CREATE INDEX idx_mahasiswa_aktif_partial ON mahasiswa(ipk) 
WHERE status = 'Aktif';
```

### 2. Index Strategy Documentation

```sql
-- Dokumentasi index strategy dalam comment
COMMENT ON INDEX idx_mahasiswa_nim_lookup IS 
'Primary lookup index for student search by NIM - used in 80% of queries';

COMMENT ON INDEX idx_mahasiswa_email_lookup IS
'Authentication and login queries - critical for response time';  

COMMENT ON INDEX idx_krs_nim_fk IS
'Foreign key index for join performance with mahasiswa table';

-- Lihat dokumentasi
SELECT 
    indexname,
    obj_description(indexname::regclass) as index_comment
FROM pg_indexes 
WHERE schemaname = 'public'
  AND obj_description(indexname::regclass) IS NOT NULL;
```

### 3. Performance Testing Framework

```sql
-- Function untuk testing index performance
CREATE OR REPLACE FUNCTION test_query_performance(
    query_description TEXT,
    test_query TEXT,
    expected_rows INTEGER DEFAULT NULL
) RETURNS TABLE (
    description TEXT,
    actual_rows BIGINT,
    execution_time_ms NUMERIC,
    buffer_hits BIGINT,
    buffer_reads BIGINT,
    plan_summary TEXT
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    explain_result TEXT;
BEGIN
    -- Reset statistics
    PERFORM pg_stat_reset();
    
    -- Capture start time
    start_time := clock_timestamp();
    
    -- Execute query (in real implementation, use EXPLAIN ANALYZE)
    -- This is simplified for demonstration
    EXECUTE test_query;
    
    -- Capture end time
    end_time := clock_timestamp();
    
    -- Return results
    RETURN QUERY SELECT 
        query_description,
        0::BIGINT, -- Would be actual row count
        EXTRACT(EPOCH FROM (end_time - start_time)) * 1000,
        0::BIGINT, -- Would be buffer hits
        0::BIGINT, -- Would be buffer reads  
        'Simplified test'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Example usage
-- SELECT * FROM test_query_performance(
--     'NIM lookup test',
--     'SELECT * FROM mahasiswa WHERE nim = ''2310001000''',
--     1
-- );
```

---

## Real-World Application Examples

### 1. Student Information System Queries

```sql
-- Common SIS queries dengan optimized indexes

-- 1. Student login
CREATE INDEX idx_sis_login ON mahasiswa(email, status) 
INCLUDE (id, nim, nama, program_studi);

-- 2. Academic transcript lookup
CREATE INDEX idx_sis_transcript ON krs(nim, semester_ambil)
INCLUDE (nama_mk, sks, nilai);

-- 3. Course enrollment check  
CREATE INDEX idx_sis_enrollment ON krs(kode_mk, tahun_akademik)
INCLUDE (nim, semester_ambil);

-- Test SIS query patterns
EXPLAIN (ANALYZE, BUFFERS)
SELECT nim, nama, program_studi FROM mahasiswa
WHERE email = 'mhs12345@kampus.ac.id' AND status = 'Aktif';

EXPLAIN (ANALYZE, BUFFERS)  
SELECT nama_mk, sks, nilai FROM krs
WHERE nim = '2310012345' 
ORDER BY semester_ambil, nama_mk;
```

### 2. Administrative Reporting Queries

```sql
-- Reporting queries dengan index strategy

-- 1. Quick enrollment stats
CREATE INDEX idx_report_enrollment ON krs(tahun_akademik, semester_ambil)
INCLUDE (nim, sks);

-- 2. Student status summary  
CREATE INDEX idx_report_students ON mahasiswa(status, program_studi)
INCLUDE (angkatan);

-- Test reporting queries
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    program_studi,
    COUNT(*) as total_students,
    COUNT(*) FILTER (WHERE status = 'Aktif') as active_students
FROM mahasiswa  
GROUP BY program_studi;
```

---

## Cleanup dan Maintenance

```sql
-- Drop unused indexes (example - be careful in production!)
-- DROP INDEX IF EXISTS idx_mahasiswa_gender; -- Demonstrated low usage

-- Maintenance queries
VACUUM ANALYZE mahasiswa;
VACUUM ANALYZE krs;
VACUUM ANALYZE log_aktivitas;

-- Reset test parameters
RESET enable_seqscan;
RESET work_mem;
RESET random_page_cost;

-- Final index usage report
SELECT 
    i.indexname,
    i.tablename,
    s.idx_scan as times_used,
    pg_size_pretty(pg_relation_size(i.indexname::regclass)) as size,
    CASE 
        WHEN s.idx_scan = 0 THEN 'Consider dropping'
        WHEN s.idx_scan < 10 THEN 'Low usage'  
        WHEN s.idx_scan < 100 THEN 'Moderate usage'
        ELSE 'High usage'
    END as recommendation
FROM pg_indexes i
LEFT JOIN pg_stat_user_indexes s ON i.indexname = s.indexname  
WHERE i.schemaname = 'public'
ORDER BY s.idx_scan DESC NULLS LAST;
```

---

## Kesimpulan dan Guidelines

### Index Strategy Cheat Sheet:

```sql
-- 1. ALWAYS index Primary Keys dan Unique columns (automatic)
-- 2. Index Foreign Keys untuk join performance
-- 3. Index High Selectivity columns (nim, email, id)
-- 4. Consider Composite Index untuk multi-column filters
-- 5. Use Covering Index untuk query yang sering digunakan
-- 6. Use Partial Index untuk conditional data
-- 7. Monitor index usage dan drop yang tidak terpakai

-- Column Selectivity Guidelines:
-- > 95%  = Excellent for indexing (nim, email)
-- 50-95% = Good for indexing (name combinations)  
-- 10-50% = Consider composite/partial indexing
-- < 10%  = Usually not worth indexing alone

-- Short Query Identification:
-- ✓ WHERE dengan exact match (=)
-- ✓ WHERE dengan range pada high selectivity column
-- ✓ JOIN dengan proper foreign key
-- ✓ LIMIT dengan ORDER BY pada indexed column
-- ✗ Full table aggregations
-- ✗ WHERE pada low selectivity tanpa tambahan filters
-- ✗ Complex OR conditions tanpa index strategy
```

### Performance Monitoring:

```sql
-- Regular monitoring queries untuk production:

-- 1. Unused indexes
SELECT indexname, schemaname 
FROM pg_stat_user_indexes 
WHERE idx_scan = 0;

-- 2. Most expensive queries (requires pg_stat_statements)
-- SELECT query, calls, mean_time, total_time 
-- FROM pg_stat_statements 
-- ORDER BY mean_time DESC LIMIT 10;

-- 3. Index hit ratio
SELECT 
    SUM(idx_blks_hit) * 100.0 / SUM(idx_blks_hit + idx_blks_read) as index_hit_ratio
FROM pg_statio_user_indexes;
```

---

**Catatan:** Script ini memberikan implementasi komprehensif dari konsep strategi index dan optimasi query pendek yang dibahas dalam Modul Week 6. Setiap section mendemonstrasikan bagaimana selectivity mempengaruhi efektivitas index dan cara memilih strategi index yang tepat untuk berbagai pola query.