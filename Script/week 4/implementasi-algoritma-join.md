# Implementasi PostgreSQL - Algoritma Join pada Database

## Week 4 - Administrasi Basis Data

---

## Setup Database dan Tabel untuk Demonstrasi Join

### 1. Membuat Database dan Tabel

```sql
-- Membuat database untuk demonstrasi join
CREATE DATABASE db_join_demo;

-- Menggunakan database
\c db_join_demo;

-- Membuat tabel mahasiswa
CREATE TABLE mahasiswa (
    nim VARCHAR(15) PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    angkatan INTEGER NOT NULL,
    jurusan VARCHAR(50) NOT NULL,
    ipk NUMERIC(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Membuat tabel mata_kuliah
CREATE TABLE mata_kuliah (
    kode_mk VARCHAR(10) PRIMARY KEY,
    nama_mk VARCHAR(100) NOT NULL,
    sks INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    jenis VARCHAR(20) DEFAULT 'Wajib'
);

-- Membuat tabel krs (Kartu Rencana Studi)
CREATE TABLE krs (
    id_krs SERIAL PRIMARY KEY,
    nim VARCHAR(15) NOT NULL REFERENCES mahasiswa(nim) ON DELETE CASCADE,
    kode_mk VARCHAR(10) NOT NULL REFERENCES mata_kuliah(kode_mk) ON DELETE CASCADE,
    semester_ambil INTEGER NOT NULL,
    tahun_akademik VARCHAR(10) NOT NULL,
    nilai CHAR(2) CHECK (nilai IN ('A','B+','B','C+','C','D','E','F')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Membuat tabel dosen
CREATE TABLE dosen (
    id_dosen SERIAL PRIMARY KEY,
    nama_dosen VARCHAR(100) NOT NULL,
    nidn VARCHAR(20) UNIQUE NOT NULL,
    departemen VARCHAR(50),
    email VARCHAR(100)
);

-- Membuat tabel mengajar (relasi many-to-many dosen dan mata kuliah)
CREATE TABLE mengajar (
    id_mengajar SERIAL PRIMARY KEY,
    id_dosen INTEGER REFERENCES dosen(id_dosen),
    kode_mk VARCHAR(10) REFERENCES mata_kuliah(kode_mk),
    tahun_akademik VARCHAR(10) NOT NULL,
    kelas CHAR(1) DEFAULT 'A'
);
```

### 2. Insert Data Sample untuk Testing Join

```sql
-- Insert mahasiswa
INSERT INTO mahasiswa (nim, nama, angkatan, jurusan, ipk) VALUES
('2021001', 'Ahmad Rizki Pratama', 2021, 'Informatika', 3.45),
('2021002', 'Sari Dewi Lestari', 2021, 'Informatika', 3.72),
('2021003', 'Budi Santoso', 2021, 'Sistem Informasi', 3.28),
('2022001', 'Rina Kusuma Wardani', 2022, 'Informatika', 3.65),
('2022002', 'Dani Kurniawan', 2022, 'Informatika', 3.51),
('2022003', 'Lisa Permata Sari', 2022, 'Sistem Informasi', 3.83),
('2023001', 'Ferry Ahmad Yusuf', 2023, 'Informatika', 3.34),
('2023002', 'Nina Sari Dewi', 2023, 'Informatika', 3.67),
('2023003', 'Eko Prasetyo', 2023, 'Sistem Informasi', 3.45),
('2024001', 'Maya Indah Sari', 2024, 'Informatika', 3.78);

-- Insert mata kuliah
INSERT INTO mata_kuliah (kode_mk, nama_mk, sks, semester, jenis) VALUES
('IF101', 'Algoritma dan Pemrograman', 3, 1, 'Wajib'),
('IF102', 'Matematika Diskrit', 3, 1, 'Wajib'),
('IF201', 'Struktur Data', 3, 2, 'Wajib'),
('IF202', 'Basis Data', 3, 2, 'Wajib'),
('IF301', 'Pemrograman Web', 3, 3, 'Wajib'),
('IF302', 'Jaringan Komputer', 3, 3, 'Wajib'),
('SI101', 'Pengantar Sistem Informasi', 3, 1, 'Wajib'),
('SI201', 'Analisis dan Perancangan Sistem', 3, 2, 'Wajib'),
('MK401', 'Kecerdasan Buatan', 3, 4, 'Pilihan'),
('MK402', 'Machine Learning', 3, 4, 'Pilihan');

-- Insert dosen
INSERT INTO dosen (nama_dosen, nidn, departemen, email) VALUES
('Dr. Agus Wijaya', '0123456789', 'Informatika', 'agus.wijaya@univ.ac.id'),
('Prof. Rita Sari', '0234567890', 'Informatika', 'rita.sari@univ.ac.id'),
('Dr. Bambang Prakoso', '0345678901', 'Sistem Informasi', 'bambang.p@univ.ac.id'),
('Dr. Siti Nurhaliza', '0456789012', 'Informatika', 'siti.n@univ.ac.id'),
('Prof. Andi Pratama', '0567890123', 'Sistem Informasi', 'andi.p@univ.ac.id');

-- Insert pengajaran
INSERT INTO mengajar (id_dosen, kode_mk, tahun_akademik, kelas) VALUES
(1, 'IF101', '2023/2024', 'A'),
(1, 'IF201', '2023/2024', 'A'),
(2, 'IF102', '2023/2024', 'A'),
(2, 'IF202', '2023/2024', 'A'),
(3, 'SI101', '2023/2024', 'A'),
(3, 'SI201', '2023/2024', 'A'),
(4, 'IF301', '2023/2024', 'A'),
(5, 'MK401', '2023/2024', 'A');

-- Insert KRS
INSERT INTO krs (nim, kode_mk, semester_ambil, tahun_akademik, nilai) VALUES
('2021001', 'IF101', 1, '2021/2022', 'B+'),
('2021001', 'IF102', 1, '2021/2022', 'A'),
('2021001', 'IF201', 2, '2021/2022', 'B'),
('2021001', 'IF202', 2, '2021/2022', 'B+'),
('2021002', 'IF101', 1, '2021/2022', 'A'),
('2021002', 'IF102', 1, '2021/2022', 'A'),
('2021002', 'IF201', 2, '2021/2022', 'A'),
('2022001', 'IF101', 1, '2022/2023', 'B+'),
('2022001', 'IF102', 1, '2022/2023', 'B'),
('2022001', 'IF201', 2, '2022/2023', 'A'),
('2023001', 'IF101', 1, '2023/2024', 'B'),
('2023001', 'IF102', 1, '2023/2024', 'C+');

-- Menambah lebih banyak data untuk demonstrasi algoritma join yang lebih jelas
INSERT INTO mahasiswa (nim, nama, angkatan, jurusan, ipk)
SELECT 
    '202' || (1 + (generate_series % 4)) || LPAD((100 + generate_series)::text, 3, '0'),
    'Mahasiswa ' || generate_series,
    2021 + (generate_series % 4),
    CASE WHEN generate_series % 2 = 0 THEN 'Informatika' ELSE 'Sistem Informasi' END,
    ROUND((2.5 + (random() * 1.5))::numeric, 2)
FROM generate_series(1, 500);

-- Menambah banyak data KRS untuk testing join performance
INSERT INTO krs (nim, kode_mk, semester_ambil, tahun_akademik, nilai)
SELECT 
    m.nim,
    (ARRAY['IF101','IF102','IF201','IF202','IF301','SI101','SI201'])[1 + (random() * 6)::int],
    1 + (random() * 4)::int,
    '202' || (1 + (random() * 3)::int) || '/202' || (2 + (random() * 3)::int),
    (ARRAY['A','B+','B','C+','C','D'])[1 + (random() * 5)::int]
FROM mahasiswa m
WHERE m.nim LIKE '202%'
ORDER BY random()
LIMIT 2000;

-- Update statistik untuk optimizer
ANALYZE mahasiswa;
ANALYZE mata_kuliah;
ANALYZE krs;
ANALYZE dosen;
ANALYZE mengajar;
```

---

## Demonstrasi Algoritma Join

### 1. Nested Loop Join

Nested Loop Join cocok untuk data kecil atau ketika salah satu tabel memiliki index yang baik.

```sql
-- Contoh query yang kemungkinan menggunakan Nested Loop Join
-- (tabel mata_kuliah kecil, ada index pada primary key)
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, mk.nama_mk, mk.sks
FROM mata_kuliah mk
JOIN krs k ON mk.kode_mk = k.kode_mk
JOIN mahasiswa m ON k.nim = m.nim
WHERE mk.kode_mk = 'IF101';

-- Analisis hasil:
-- Nested Loop biasanya muncul ketika:
-- 1. Salah satu tabel sangat kecil (seperti mata_kuliah)
-- 2. Ada kondisi WHERE yang sangat selektif
-- 3. Ada index yang mendukung join condition
```

### 2. Memaksa Nested Loop Join

```sql
-- Disable algoritma join lain untuk melihat Nested Loop
SET enable_hashjoin = OFF;
SET enable_mergejoin = OFF;

EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, k.kode_mk, mk.nama_mk
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
WHERE m.angkatan = 2023;

-- Re-enable semua algoritma
SET enable_hashjoin = ON;
SET enable_mergejoin = ON;
```

---

### 3. Hash Join

Hash Join umumnya dipilih untuk join equality pada data yang lebih besar.

```sql
-- Query yang kemungkinan menggunakan Hash Join
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, m.angkatan, COUNT(k.kode_mk) as jumlah_mk
FROM mahasiswa m
LEFT JOIN krs k ON m.nim = k.nim
GROUP BY m.nim, m.nama, m.angkatan
HAVING COUNT(k.kode_mk) > 2;

-- Hash Join cocok untuk:
-- 1. Equality joins (menggunakan = )
-- 2. Data dari ukuran menengah sampai besar
-- 3. Tidak memerlukan urutan khusus
```

### 4. Memaksa Hash Join

```sql
-- Disable algoritma lain untuk melihat Hash Join
SET enable_nestloop = OFF;
SET enable_mergejoin = OFF;

EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, k.nilai, mk.nama_mk
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
WHERE m.angkatan IN (2021, 2022);

-- Re-enable semua algoritma
SET enable_nestloop = ON;
SET enable_mergejoin = ON;
```

---

### 5. Merge Join

Merge Join efisien ketika data sudah terurut atau dapat diurutkan dengan biaya rendah.

```sql
-- Membuat index untuk mendukung Merge Join
CREATE INDEX idx_mahasiswa_nim_sorted ON mahasiswa(nim);
CREATE INDEX idx_krs_nim_sorted ON krs(nim);

-- Query yang berpeluang menggunakan Merge Join
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nim, m.nama, k.kode_mk, k.nilai
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
ORDER BY m.nim;

-- Merge Join cocok untuk:
-- 1. Data yang sudah terurut
-- 2. Join condition yang mendukung ordering
-- 3. Ketika hasil query perlu diurutkan
```

### 6. Memaksa Merge Join

```sql
-- Disable algoritma lain untuk melihat Merge Join
SET enable_nestloop = OFF;
SET enable_hashjoin = OFF;

EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nim, m.nama, k.kode_mk
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
WHERE m.angkatan = 2022
ORDER BY m.nim;

-- Re-enable semua algoritma
SET enable_nestloop = ON;
SET enable_hashjoin = ON;
```

---

## Perbandingan Performa Algoritma Join

### 1. Benchmark dengan Data Set Berbeda

```sql
-- Test 1: Join dengan tabel kecil (Nested Loop optimal)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT mk.nama_mk, d.nama_dosen
FROM mata_kuliah mk
JOIN mengajar mg ON mk.kode_mk = mg.kode_mk
JOIN dosen d ON mg.id_dosen = d.id_dosen;

-- Test 2: Join dengan data besar (Hash/Merge Join optimal)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT m.angkatan, COUNT(*) as total_mahasiswa, 
       AVG(CASE k.nilai 
           WHEN 'A' THEN 4.0 
           WHEN 'B+' THEN 3.5 
           WHEN 'B' THEN 3.0 
           WHEN 'C+' THEN 2.5 
           WHEN 'C' THEN 2.0 
           WHEN 'D' THEN 1.0 
           ELSE 0.0 END) as rata_rata_nilai
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
GROUP BY m.angkatan;
```

### 2. Analisis Cost dan Time

```sql
-- Melihat detailed cost breakdown
EXPLAIN (ANALYZE, BUFFERS, COSTS, TIMING, VERBOSE)
SELECT m.nama, m.jurusan, mk.nama_mk, k.nilai, d.nama_dosen
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
JOIN mengajar mg ON mk.kode_mk = mg.kode_mk
JOIN dosen d ON mg.id_dosen = d.id_dosen
WHERE m.angkatan = 2022;
```

---

## Optimasi Query dengan Join

### 1. Index Strategy untuk Join Optimization

```sql
-- Index untuk mempercepat join operations
CREATE INDEX idx_krs_nim_kode ON krs(nim, kode_mk);
CREATE INDEX idx_krs_kode_nim ON krs(kode_mk, nim);
CREATE INDEX idx_mahasiswa_angkatan_nim ON mahasiswa(angkatan, nim);
CREATE INDEX idx_mengajar_composite ON mengajar(kode_mk, id_dosen);

-- Test performa setelah index
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, mk.nama_mk, k.nilai
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
WHERE m.angkatan = 2023 AND mk.jenis = 'Wajib';
```

### 2. Query Rewriting untuk Optimasi

```sql
-- Query yang kurang optimal (banyak join di awal)
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, mk.nama_mk, d.nama_dosen
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
JOIN mengajar mg ON mk.kode_mk = mg.kode_mk
JOIN dosen d ON mg.id_dosen = d.id_dosen
WHERE m.nim = '2021001';

-- Query yang lebih optimal (filter dulu, baru join)
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, mk.nama_mk, d.nama_dosen
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
JOIN mengajar mg ON mk.kode_mk = mg.kode_mk AND mg.tahun_akademik = '2023/2024'
JOIN dosen d ON mg.id_dosen = d.id_dosen
WHERE m.nim = '2021001';
```

---

## Complex Join Scenarios

### 1. Multi-table Join dengan Agregasi

```sql
-- Query kompleks dengan multiple joins dan aggregation
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    m.jurusan,
    m.angkatan,
    COUNT(DISTINCT m.nim) as jumlah_mahasiswa,
    COUNT(k.id_krs) as total_krs,
    AVG(m.ipk) as rata_ipk,
    COUNT(DISTINCT mk.kode_mk) as jumlah_mk_diambil
FROM mahasiswa m
LEFT JOIN krs k ON m.nim = k.nim
LEFT JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
GROUP BY m.jurusan, m.angkatan
ORDER BY m.angkatan, m.jurusan;
```

### 2. Self Join

```sql
-- Self join untuk mencari mahasiswa satu angkatan
EXPLAIN (ANALYZE, BUFFERS)
SELECT DISTINCT 
    m1.nama as mahasiswa1,
    m2.nama as mahasiswa2,
    m1.angkatan
FROM mahasiswa m1
JOIN mahasiswa m2 ON m1.angkatan = m2.angkatan 
                  AND m1.jurusan = m2.jurusan
                  AND m1.nim < m2.nim
WHERE m1.angkatan = 2022
LIMIT 10;
```

### 3. Subquery vs Join Performance

```sql
-- Menggunakan subquery
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, m.ipk
FROM mahasiswa m
WHERE m.nim IN (
    SELECT k.nim 
    FROM krs k 
    JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
    WHERE mk.nama_mk = 'Algoritma dan Pemrograman'
);

-- Menggunakan join (biasanya lebih efisien)
EXPLAIN (ANALYZE, BUFFERS)
SELECT DISTINCT m.nama, m.ipk
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
WHERE mk.nama_mk = 'Algoritma dan Pemrograman';
```

---

## Monitoring dan Troubleshooting Join Performance

### 1. Identifying Slow Joins

```sql
-- Enable logging untuk monitoring
SET log_statement = 'all';
SET log_min_duration_statement = 100; -- Log queries > 100ms

-- Query untuk melihat statistik join
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

### 2. Index Usage Analysis

```sql
-- Analisis penggunaan index untuk join
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as "Times Used",
    idx_tup_read as "Tuples Read",
    idx_tup_fetch as "Tuples Fetched"
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

---

## Praktikum dan Latihan

### 1. Latihan Join Algorithm Recognition

```sql
-- Latihan 1: Identifikasi algoritma join
-- Jalankan query ini dan identifikasi algoritma yang digunakan
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, COUNT(k.kode_mk) as total_mk
FROM mahasiswa m
LEFT JOIN krs k ON m.nim = k.nim
WHERE m.angkatan BETWEEN 2022 AND 2024
GROUP BY m.nim, m.nama
HAVING COUNT(k.kode_mk) > 0;

-- Pertanyaan: Algoritma join apa yang digunakan? Mengapa?
```

### 2. Optimasi Challenge

```sql
-- Challenge: Optimasi query berikut
-- Query awal (kemungkinan lambat)
SELECT 
    m.nama,
    m.angkatan,
    mk.nama_mk,
    k.nilai,
    d.nama_dosen
FROM mahasiswa m, krs k, mata_kuliah mk, mengajar mg, dosen d
WHERE m.nim = k.nim
  AND k.kode_mk = mk.kode_mk
  AND mk.kode_mk = mg.kode_mk
  AND mg.id_dosen = d.id_dosen
  AND m.angkatan = 2023;

-- TODO: Tulis ulang query dengan JOIN eksplisit dan analisis performance
```

### 3. Eksperimen dengan Work_mem

```sql
-- Test dampak work_mem pada Hash Join
SET work_mem = '1MB';
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, COUNT(k.kode_mk)
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
GROUP BY m.nim, m.nama;

SET work_mem = '10MB';
EXPLAIN (ANALYZE, BUFFERS)
SELECT m.nama, COUNT(k.kode_mk)
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
GROUP BY m.nim, m.nama;

-- Reset ke default
RESET work_mem;
```

---

## Best Practices untuk Join Optimization

### 1. Index Strategy

```sql
-- Pedoman pembuatan index untuk join:
-- 1. Index pada foreign key columns
CREATE INDEX idx_krs_nim ON krs(nim);
CREATE INDEX idx_krs_kode_mk ON krs(kode_mk);
CREATE INDEX idx_mengajar_dosen ON mengajar(id_dosen);

-- 2. Composite index untuk multi-column joins
CREATE INDEX idx_krs_composite ON krs(nim, kode_mk, semester_ambil);

-- 3. Index untuk covering queries (include columns)
-- PostgreSQL doesn't support INCLUDE, but we can use composite index
CREATE INDEX idx_mahasiswa_covering ON mahasiswa(nim, nama, angkatan, ipk);
```

### 2. Query Writing Guidelines

```sql
-- Good practices:

-- 1. Use explicit JOIN syntax
SELECT m.nama, k.nilai
FROM mahasiswa m
INNER JOIN krs k ON m.nim = k.nim;  -- Good

-- Instead of:
-- SELECT m.nama, k.nilai
-- FROM mahasiswa m, krs k
-- WHERE m.nim = k.nim;  -- Avoid

-- 2. Filter early
SELECT m.nama, k.nilai
FROM mahasiswa m
INNER JOIN krs k ON m.nim = k.nim
WHERE m.angkatan = 2023  -- Filter pushed down
  AND k.nilai IN ('A', 'B+');

-- 3. Consider join order for manual optimization
SELECT /*+ USE_HASH(k mk) */ 
    m.nama, mk.nama_mk
FROM mata_kuliah mk  -- Start with smaller table
JOIN krs k ON mk.kode_mk = k.kode_mk
JOIN mahasiswa m ON k.nim = m.nim;
```

---

## Cleanup dan Maintenance

```sql
-- Cleanup test data jika diperlukan
-- TRUNCATE krs;
-- TRUNCATE mengajar;
-- DROP TABLE IF EXISTS mengajar;
-- DROP TABLE IF EXISTS krs;
-- DROP TABLE IF EXISTS mata_kuliah;
-- DROP TABLE IF EXISTS dosen;
-- DROP TABLE IF EXISTS mahasiswa;

-- Maintenance commands
VACUUM ANALYZE;
REINDEX DATABASE db_join_demo;
```

---

## Kesimpulan dan Rangkuman

### Hasil Eksperimen Join Algorithms:

1. **Nested Loop Join** optimal untuk:
   - Tabel kecil (< 1000 rows)
   - Join dengan index yang sangat selektif
   - Kondisi WHERE yang membatasi hasil secara drastis

2. **Hash Join** optimal untuk:
   - Equality joins pada data menengah-besar
   - Join tanpa kebutuhan ordering
   - Saat work_mem cukup untuk hash table

3. **Merge Join** optimal untuk:
   - Data yang sudah terurut
   - Large datasets dengan sort requirement
   - Range joins dengan ordering

### Tips Optimasi:

```sql
-- 1. Selalu gunakan EXPLAIN ANALYZE untuk verifikasi
-- 2. Monitor work_mem usage untuk Hash Joins
-- 3. Buat index yang mendukung join conditions
-- 4. Pertimbangkan join order untuk query kompleks
-- 5. Gunakan covering index ketika memungkinkan
-- 6. Filter data lebih awal dalam execution plan
```

---

**Catatan:** Script ini memberikan implementasi komprehensif dari konsep algoritma join yang dibahas dalam Modul Week 4. Setiap section dapat dijalankan secara bertahap untuk memahami bagaimana PostgreSQL memilih algoritma join yang optimal berdasarkan karakteristik data dan kondisi query.