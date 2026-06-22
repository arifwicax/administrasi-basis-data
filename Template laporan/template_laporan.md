# LAPORAN PROYEK BESAR
## Mata Kuliah Administrasi Basis Data
### Program Studi Sistem Informasi

---

<div align="center">

**[JUDUL PROYEK]**

*Contoh: Sistem Informasi Manajemen Perpustakaan menggunakan PostgreSQL*

</div>

---

## Identitas Kelompok

| Keterangan       | Isi                            |
|------------------|--------------------------------|
| Mata Kuliah      | Administrasi Basis Data        |
| Program Studi    | Sistem Informasi               |
| Semester / Tahun | Genap / 20XX–20XX              |
| Dosen Pengampu   | [Nama Dosen]                   |

### Anggota Kelompok

| No | NIM | Nama Lengkap | 
|----|-----|--------------|
| 1  |     |              |       
| 2  |     |              |       
| 3  |     |              |       

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Deskripsi Sistem](#2-deskripsi-sistem)
3. [Perancangan Basis Data (ERD)](#3-perancangan-basis-data-erd)
4. [Implementasi PostgreSQL](#4-implementasi-postgresql)
5. [Strategi Penggunaan Indeks](#5-strategi-penggunaan-indeks)
6. [Analisis Query dengan EXPLAIN](#6-analisis-query-dengan-explain)
7. [Kesimpulan](#7-kesimpulan)
8. [Referensi](#8-referensi)
9. [Lampiran](#9-lampiran)

---

## 1. Pendahuluan

### 1.1 Latar Belakang

> Jelaskan konteks dan alasan pemilihan topik proyek ini. Uraikan masalah nyata yang ingin diselesaikan, mengapa basis data relasional diperlukan, dan relevansinya dengan bidang Sistem Informasi.

### 1.2 Rumusan Masalah

1. Bagaimana merancang struktur basis data yang optimal untuk [domain sistem]?
2. Bagaimana mengimplementasikan skema tersebut menggunakan PostgreSQL?
3. Bagaimana strategi indeks yang tepat untuk meningkatkan performa query?
4. Bagaimana hasil analisis `EXPLAIN ANALYZE` menunjukkan efisiensi query sebelum dan sesudah optimasi?

### 1.3 Tujuan

- Merancang ERD yang merepresentasikan kebutuhan data sistem [nama sistem].
- Mengimplementasikan skema basis data pada PostgreSQL.
- Menerapkan indeks yang sesuai berdasarkan pola akses data.
- Menganalisis dan mengoptimasi performa query menggunakan `EXPLAIN ANALYZE`.

### 1.4 Batasan Proyek

> Cantumkan batasan ruang lingkup proyek, misalnya: jumlah tabel, volume data dummy, fitur yang dicakup, dll.

---

## 2. Deskripsi Sistem

### 2.1 Gambaran Umum Sistem

> Deskripsikan sistem yang dibangun secara singkat: fungsi utama, pengguna yang terlibat, dan alur kerja umum.

### 2.2 Kebutuhan Data (Requirement Analysis)

> Uraikan entitas-entitas utama yang terlibat beserta atribut pentingnya. Bisa menggunakan format daftar atau tabel.

**Entitas yang diidentifikasi:**

| Entitas | Deskripsi | Atribut Utama |
|---------|-----------|---------------|
| [Entitas 1] | | |
| [Entitas 2] | | |
| [Entitas 3] | | |

**Relasi antar entitas:**

| Relasi | Entitas A | Entitas B | Kardinalitas |
|--------|-----------|-----------|--------------|
| [Relasi 1] | | | 1:N / M:N / 1:1 |
| [Relasi 2] | | | |

---

## 3. Perancangan Basis Data (ERD)

### 3.1 Entity Relationship Diagram (ERD)

> Sisipkan gambar ERD di bawah ini. Gunakan notasi crow's foot atau notasi Chen. Tools yang disarankan: draw.io, dbdiagram.io, Lucidchart, atau pgModeler.

```
[Sisipkan gambar ERD di sini]
```

*Gambar 3.1 — Entity Relationship Diagram [Nama Sistem]*

### 3.2 Penjelasan ERD

> Jelaskan setiap entitas, atribut kunci, dan relasi yang ada pada ERD beserta alasan desain tersebut dipilih.

**Entitas dan Atribut:**

- **[Nama Tabel]**: primary key `[pk]`, atribut `[atribut1]`, `[atribut2]`, ...
- **[Nama Tabel]**: primary key `[pk]`, foreign key `[fk]` merujuk ke `[tabel_lain]`, ...

**Relasi:**

- `[Tabel A]` — `[Tabel B]`: relasi **[one-to-many / many-to-many]**, karena [alasan bisnis].
- `[Tabel B]` — `[Tabel C]`: relasi **[one-to-one]**, karena [alasan bisnis].

### 3.3 Normalisasi

> Jelaskan bahwa skema telah memenuhi minimal bentuk normal ketiga (3NF) atau BCNF. Sertakan penjelasan singkat per tabel jika perlu.

Skema basis data ini telah memenuhi **Third Normal Form (3NF)** karena:
- Setiap tabel memiliki primary key yang jelas.
- Tidak terdapat dependensi parsial (sesuai 2NF).
- Tidak terdapat dependensi transitif (sesuai 3NF).

---

## 4. Implementasi PostgreSQL

### 4.1 Lingkungan dan Versi

| Komponen | Versi / Keterangan |
|----------|--------------------|
| PostgreSQL | v1x.x |
| OS | [Windows / macOS / Linux] |
| Tools | psql / pgAdmin / DBeaver |

### 4.2 Pembuatan Database dan Skema

```sql
-- Membuat database
CREATE DATABASE nama_database;

-- Menghubungkan ke database
\c nama_database;

-- Membuat schema (opsional)
CREATE SCHEMA IF NOT EXISTS nama_schema;
```

### 4.3 Definisi Tabel (DDL)

> Tuliskan seluruh perintah DDL (CREATE TABLE) secara lengkap dengan constraint.

```sql
-- ============================================================
-- TABEL: [nama_tabel_1]
-- Deskripsi: [fungsi tabel ini]
-- ============================================================
CREATE TABLE nama_tabel_1 (
    id          SERIAL PRIMARY KEY,
    kolom_a     VARCHAR(100)    NOT NULL,
    kolom_b     TEXT,
    created_at  TIMESTAMP       DEFAULT NOW()
);

-- ============================================================
-- TABEL: [nama_tabel_2]
-- Deskripsi: [fungsi tabel ini]
-- ============================================================
CREATE TABLE nama_tabel_2 (
    id          SERIAL PRIMARY KEY,
    fk_tabel_1  INT             NOT NULL REFERENCES nama_tabel_1(id) ON DELETE CASCADE,
    kolom_c     NUMERIC(10, 2)  NOT NULL,
    kolom_d     DATE
);

-- Tambahkan tabel lainnya...
```

### 4.4 Data Dummy (DML)

> Sertakan contoh data dummy yang cukup representatif (minimal 5–10 baris per tabel utama) untuk keperluan pengujian query.

```sql
-- Mengisi data tabel [nama_tabel_1]
INSERT INTO nama_tabel_1 (kolom_a, kolom_b) VALUES
    ('Nilai A1', 'Deskripsi 1'),
    ('Nilai A2', 'Deskripsi 2'),
    ('Nilai A3', 'Deskripsi 3');

-- Mengisi data tabel [nama_tabel_2]
INSERT INTO nama_tabel_2 (fk_tabel_1, kolom_c, kolom_d) VALUES
    (1, 150000.00, '2024-01-15'),
    (1, 75000.00,  '2024-02-20'),
    (2, 200000.00, '2024-03-10');
```

### 4.5 Query Operasional (DML)

> Tuliskan query-query utama yang digunakan dalam sistem, lengkap dengan penjelasan fungsinya.

#### Query 1 — [Deskripsi Query]

```sql
-- Deskripsi: [apa yang dilakukan query ini]
SELECT
    t1.kolom_a,
    t2.kolom_c,
    t2.kolom_d
FROM nama_tabel_1 t1
JOIN nama_tabel_2 t2 ON t1.id = t2.fk_tabel_1
WHERE t2.kolom_d BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY t2.kolom_d DESC;
```

#### Query 2 — [Deskripsi Query]

```sql
-- Deskripsi: [apa yang dilakukan query ini]
SELECT
    kolom_a,
    COUNT(*) AS jumlah,
    SUM(t2.kolom_c) AS total
FROM nama_tabel_1 t1
JOIN nama_tabel_2 t2 ON t1.id = t2.fk_tabel_1
GROUP BY kolom_a
HAVING SUM(t2.kolom_c) > 100000;
```

> Tambahkan query lainnya sesuai kebutuhan sistem...

---

## 5. Strategi Penggunaan Indeks

### 5.1 Analisis Pola Akses Data

> Sebelum membuat indeks, identifikasi kolom mana yang sering digunakan pada klausa `WHERE`, `JOIN`, `ORDER BY`, dan `GROUP BY`.

| Kolom | Tabel | Digunakan pada | Kandidat Indeks |
|-------|-------|----------------|-----------------|
| `kolom_d` | `nama_tabel_2` | `WHERE`, `ORDER BY` | Ya |
| `fk_tabel_1` | `nama_tabel_2` | `JOIN` | Ya (otomatis FK) |
| `kolom_a` | `nama_tabel_1` | `WHERE` filter teks | Pertimbangkan |

### 5.2 Pembuatan Indeks

```sql
-- ============================================================
-- INDEKS: idx_nama_tabel_2_kolom_d
-- Tujuan: Mempercepat filter dan pengurutan berdasarkan tanggal
-- Tipe: B-Tree (default)
-- ============================================================
CREATE INDEX idx_nama_tabel_2_kolom_d
    ON nama_tabel_2 (kolom_d);

-- ============================================================
-- INDEKS: idx_nama_tabel_1_kolom_a
-- Tujuan: Mempercepat pencarian berdasarkan kolom_a
-- Tipe: B-Tree
-- ============================================================
CREATE INDEX idx_nama_tabel_1_kolom_a
    ON nama_tabel_1 (kolom_a);

-- ============================================================
-- INDEKS KOMPOSIT: idx_nama_tabel_2_fk_kolom_d
-- Tujuan: Mempercepat query JOIN + filter tanggal secara bersamaan
-- ============================================================
CREATE INDEX idx_nama_tabel_2_fk_kolom_d
    ON nama_tabel_2 (fk_tabel_1, kolom_d);

-- Tambahkan indeks lain sesuai kebutuhan...
```

### 5.3 Justifikasi Pemilihan Indeks

| Nama Indeks | Tipe | Alasan Pembuatan |
|-------------|------|------------------|
| `idx_nama_tabel_2_kolom_d` | B-Tree | Kolom `kolom_d` sering difilter pada rentang tanggal |
| `idx_nama_tabel_1_kolom_a` | B-Tree | Kolom `kolom_a` digunakan sebagai filter pencarian |
| `idx_nama_tabel_2_fk_kolom_d` | Komposit B-Tree | Memanfaatkan index-only scan saat JOIN + filter tanggal |

### 5.4 Memverifikasi Indeks yang Dibuat

```sql
-- Melihat semua indeks pada tabel
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('nama_tabel_1', 'nama_tabel_2')
ORDER BY tablename, indexname;
```

---

## 6. Analisis Query dengan EXPLAIN

### 6.1 Metodologi Pengujian

> Jelaskan pendekatan pengujian yang digunakan:
> - Query diuji menggunakan `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)`.
> - Setiap query diuji **sebelum** dan **sesudah** pembuatan indeks.
> - Data dummy yang digunakan berjumlah [X] baris per tabel.
> - PostgreSQL `shared_buffers` disetel ke [nilai] (atau default).

```sql
-- Template perintah EXPLAIN yang digunakan
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
[query yang dianalisis];
```

---

### 6.2 Analisis Query 1 — [Nama/Deskripsi Query]

**Query:**

```sql
SELECT
    t1.kolom_a,
    t2.kolom_c,
    t2.kolom_d
FROM nama_tabel_1 t1
JOIN nama_tabel_2 t2 ON t1.id = t2.fk_tabel_1
WHERE t2.kolom_d BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY t2.kolom_d DESC;
```

#### Sebelum Indeks

```
[Tempel output EXPLAIN ANALYZE di sini]

Contoh output:
Hash Join  (cost=15.00..45.00 rows=100 width=32) (actual time=0.500..2.300 rows=87 loops=1)
  Hash Cond: (t2.fk_tabel_1 = t1.id)
  ->  Seq Scan on nama_tabel_2 t2  (cost=0.00..25.00 rows=100 width=20) (actual time=0.010..1.200 rows=100 loops=1)
        Filter: ((kolom_d >= '2024-01-01'::date) AND (kolom_d <= '2024-12-31'::date))
        Rows Removed by Filter: 13
  ->  Hash  (cost=10.00..10.00 rows=50 width=20) (actual time=0.200..0.200 rows=50 loops=1)
        ->  Seq Scan on nama_tabel_1 t1  (cost=0.00..10.00 rows=50 width=20) (actual time=0.010..0.100 rows=50 loops=1)
Planning Time: 0.300 ms
Execution Time: 2.500 ms
```

**Analisis Sebelum Indeks:**

| Metrik | Nilai |
|--------|-------|
| Metode Join | Hash Join |
| Metode Scan | Sequential Scan |
| Estimated Cost | [cost=X..Y] |
| Actual Execution Time | X ms |
| Rows Removed by Filter | X |

> Jelaskan temuan: mengapa PostgreSQL memilih Seq Scan, apakah ada masalah performa, dsb.

#### Sesudah Indeks

```
[Tempel output EXPLAIN ANALYZE sesudah indeks dibuat di sini]

Contoh output:
Nested Loop  (cost=0.28..20.00 rows=87 width=32) (actual time=0.050..0.400 rows=87 loops=1)
  ->  Index Scan using idx_nama_tabel_2_kolom_d on nama_tabel_2 t2  (cost=0.14..10.00 rows=87 width=20) (actual time=0.020..0.200 rows=87 loops=1)
        Index Cond: ((kolom_d >= '2024-01-01'::date) AND (kolom_d <= '2024-12-31'::date))
  ->  Index Scan using nama_tabel_1_pkey on nama_tabel_1 t1  (cost=0.14..0.20 rows=1 width=20) (actual time=0.001..0.001 rows=1 loops=87)
        Index Cond: (id = t2.fk_tabel_1)
Planning Time: 0.400 ms
Execution Time: 0.500 ms
```

**Analisis Sesudah Indeks:**

| Metrik | Nilai |
|--------|-------|
| Metode Join | Nested Loop |
| Metode Scan | Index Scan |
| Estimated Cost | [cost=X..Y] |
| Actual Execution Time | X ms |
| Indeks yang Digunakan | `idx_nama_tabel_2_kolom_d` |

#### Perbandingan Performa Query 1

| Metrik | Sebelum Indeks | Sesudah Indeks | Peningkatan |
|--------|---------------|----------------|-------------|
| Execution Time | X ms | X ms | ~X× lebih cepat |
| Scan Method | Seq Scan | Index Scan | - |
| Rows Examined | X | X | - |

> Simpulkan dampak indeks terhadap performa query ini.

---

### 6.3 Analisis Query 2 — [Nama/Deskripsi Query]

**Query:**

```sql
-- Tempelkan query di sini
```

#### Sebelum Indeks

```
[Output EXPLAIN ANALYZE sebelum indeks]
```

**Analisis Sebelum Indeks:**

| Metrik | Nilai |
|--------|-------|
| Execution Time | ms |
| Scan Method | |
| Estimated Cost | |

#### Sesudah Indeks

```
[Output EXPLAIN ANALYZE sesudah indeks]
```

**Analisis Sesudah Indeks:**

| Metrik | Nilai |
|--------|-------|
| Execution Time | ms |
| Scan Method | |
| Indeks Digunakan | |

#### Perbandingan Performa Query 2

| Metrik | Sebelum Indeks | Sesudah Indeks | Peningkatan |
|--------|---------------|----------------|-------------|
| Execution Time | ms | ms | ~X× |
| Scan Method | | | |

> Tambahkan sub-bagian serupa untuk setiap query yang dianalisis...

---

### 6.4 Ringkasan Hasil Analisis EXPLAIN

| Query | Sebelum (ms) | Sesudah (ms) | Scan Sebelum | Scan Sesudah | Speedup |
|-------|-------------|-------------|--------------|--------------|---------|
| Query 1 — [Nama] | | | Seq Scan | Index Scan | x |
| Query 2 — [Nama] | | | Seq Scan | Index Scan | x |
| Query 3 — [Nama] | | | Seq Scan | Bitmap Scan | x |

### 6.5 Temuan dan Diskusi

> Tuliskan diskusi menyeluruh berdasarkan semua hasil EXPLAIN, seperti:
> - Kapan PostgreSQL memilih Seq Scan meskipun indeks tersedia (tabel kecil, statistik stale, dll)?
> - Efektivitas indeks komposit dibanding indeks tunggal.
> - Trade-off penggunaan indeks: performa baca vs. overhead tulis.
> - Dampak `VACUUM` / `ANALYZE` terhadap planner statistics.

---

## 7. Kesimpulan

### 7.1 Kesimpulan

> Tuliskan minimal 3–5 poin kesimpulan yang menjawab rumusan masalah:

1. Skema ERD yang dirancang berhasil merepresentasikan kebutuhan data [nama sistem] dengan [X] entitas dan [Y] relasi, memenuhi bentuk normal 3NF.
2. Implementasi pada PostgreSQL berhasil dilakukan dengan [X] tabel, [Y] constraint, dan [Z] baris data dummy.
3. Penerapan [N] indeks (B-Tree / komposit) mampu meningkatkan performa query rata-rata sebesar [X]× dibandingkan tanpa indeks.
4. Analisis `EXPLAIN ANALYZE` menunjukkan bahwa indeks paling efektif digunakan pada [kolom / kondisi tertentu].

### 7.2 Saran dan Rekomendasi

> Tuliskan saran pengembangan lebih lanjut, misalnya:

- Penerapan **partial index** untuk kondisi filter spesifik yang sering digunakan.
- Penggunaan **materialized view** untuk query agregasi berat yang diakses berulang.
- Penjadwalan rutin `VACUUM ANALYZE` untuk menjaga statistik query planner tetap akurat.
- Monitoring performa berkelanjutan menggunakan `pg_stat_user_indexes` dan `pg_stat_user_tables`.

---

## 8. Referensi

> Gunakan format APA atau IEEE. Cantumkan minimal 5 referensi.

1. PostgreSQL Global Development Group. (2024). *PostgreSQL 16 Documentation*. https://www.postgresql.org/docs/16/
2. Momjian, B. (2001). *PostgreSQL: Introduction and Concepts*. Addison-Wesley.
3. [Penulis]. ([Tahun]). [Judul Buku / Artikel]. [Penerbit / Jurnal].
4. [Penulis]. ([Tahun]). [Judul]. Diakses dari [URL].
5. [Penulis]. ([Tahun]). [Judul]. Diakses dari [URL].

---

## 9. Lampiran

### Lampiran A — Script DDL Lengkap

> Tempelkan seluruh script pembuatan tabel dan constraint di sini (jika belum tercantum di Bab 4).

```sql
-- [Script DDL lengkap]
```

### Lampiran B — Script Pembuatan Indeks Lengkap

```sql
-- [Script CREATE INDEX lengkap]
```

### Lampiran C — Data Dummy Lengkap

```sql
-- [Script INSERT data lengkap]
```

### Lampiran D — Screenshot Output EXPLAIN ANALYZE

> Sertakan screenshot dari terminal psql / pgAdmin untuk setiap hasil EXPLAIN yang dianalisis.

*Gambar D.1 — Output EXPLAIN ANALYZE Query 1 (Sebelum Indeks)*

*Gambar D.2 — Output EXPLAIN ANALYZE Query 1 (Sesudah Indeks)*

*dst...*

### Lampiran E — Screenshot Skema Database (pgAdmin / DBeaver)

> Sertakan tangkapan layar diagram skema database dari tools GUI yang digunakan.

---

*Laporan ini dibuat sebagai pemenuhan tugas proyek besar mata kuliah Administrasi Basis Data, Program Studi Sistem Informasi.*
