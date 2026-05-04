# **Query Optimization & Tuning di PostgreSQL**
*"Membuat Database Bekerja Lebih Cerdas, Bukan Lebih Keras"*

---

## **Mengapa Belajar Optimasi Query?**

Bayangkan Anda punya restoran dengan 1000 meja, tapi pelayan harus cek satu-satu untuk mencari meja kosong. Lama, kan? 

Begitu juga database - tanpa optimasi, PostgreSQL akan "cek satu-satu" semua data. Dengan optimasi, database punya "shortcut" untuk langsung ke data yang dibutuhkan!

**Real Impact:**
- Query lambat 30 detik → jadi 0.1 detik ⚡
- Aplikasi web loading 10 detik → jadi 1 detik 🚀
- Server hang karena query berat → jadi smooth 😎

---

## **1. Dasar-Dasar: Apa itu Query?**

Query adalah **perintah untuk meminta data dari database**.

```sql
SELECT nama, jurusan 
FROM mahasiswa
WHERE jurusan = 'Informatika';
```

**Membaca query seperti membaca kalimat:**
* `SELECT` → "Ambilkan saya..."
* `FROM` → "...dari tabel..."
* `WHERE` → "...yang memenuhi syarat..."

> **Terjemahan:** "Ambilkan saya nama dan jurusan dari tabel mahasiswa yang jurusannya Informatika"

### **Jenis-jenis Query berdasarkan Fungsi**

| Jenis Query | Fungsi | Contoh | Dampak Performa |
|-------------|--------|--------|------------------|
| **DQL** (SELECT) | Ambil data | `SELECT * FROM mahasiswa` | Medium - tergantung filter |
| **DML** (INSERT/UPDATE/DELETE) | Ubah data | `INSERT INTO mahasiswa...` | High - harus update index |
| **DDL** (CREATE/ALTER) | Ubah struktur | `CREATE INDEX...` | Very High - rebuild struktur |

---

## **2. Bagaimana Database "Berpikir"?**

### **The PostgreSQL Brain: Query Planner**

PostgreSQL punya "otak" yang disebut **Query Planner**. Sebelum menjalankan query, dia berpikir:

```
🤔 "Hmm, user minta data mahasiswa jurusan Informatika...
   Opsi 1: Baca semua 100,000 mahasiswa satu-satu (30 detik)
   Opsi 2: Pakai index jurusan, langsung ke Informatika (0.1 detik)
   Pilih opsi 2! 🚀"
```

**Proses di PostgreSQL:**
1. **Parser** → "Apakah SQL-nya benar?"
2. **Planner** → "Cara mana yang paling cepat?"
3. **Executor** → "Jalankan rencana terpilih!"
4. **Result** → "Ini datanya!"

### **Analogi Kehidupan Sehari-hari**

| Situasi | Cara Lambat | Cara Cepat |
|---------|-------------|-------------|
| Cari nomor telepon | Baca buku telepon dari A-Z | Pakai daftar isi |
| Cari buku perpustakaan | Keliling semua rak | Pakai katalog |
| Cari mahasiswa | Baca semua data | Pakai **INDEX!** |

---

## **3. 7 Penyebab Utama Query Lambat (dan Solusinya!)**

### **🐌 Problem #1: "Full Table Scan" - Membaca Semua Data**
**Masalah:** Seperti membaca novel 1000 halaman untuk cari 1 kalimat
```sql
-- LAMBAT: Baca semua 1 juta mahasiswa
SELECT * FROM mahasiswa WHERE nim = '2023001';
```
**✅ Solusi:** Buat index pada kolom yang sering dicari!

### **🤯 Problem #2: Index Tidak Ada atau Salah**
**Masalah:** Seperti perpustakaan tanpa katalog
```sql
-- Database: "Mana index untuk 'nama'? Ga ada? Ya udah baca semua deh..." 😭
SELECT * FROM mahasiswa WHERE nama LIKE '%Budi%';
```
**✅ Solusi:** `CREATE INDEX idx_nama ON mahasiswa(nama);`

### **🔗 Problem #3: JOIN Tanpa Index**
**Masalah:** Seperti menjodohkan 1000 orang tanpa biodata
```sql
-- LAMBAT: JOIN tanpa index di foreign key
SELECT m.nama, k.nama_kelas 
FROM mahasiswa m 
JOIN kelas k ON m.kelas_id = k.id;
```
**✅ Solusi:** Index pada kolom JOIN!

### **📊 Problem #4: Statistik Basi**
**Masalah:** Database punya data lama → salah estimasi
**Contoh:** Database pikir tabel cuma 1000 baris, padahal sudah 1 juta!
**✅ Solusi:** `ANALYZE` rutin untuk update statistik

### **💀 Problem #5: Dead Tuples (Data Zombie)**
**Masalah:** Data yang sudah dihapus/diupdate masih "menghantu" di disk
**✅ Solusi:** `VACUUM` untuk bersih-bersih

### **🔄 Problem #6: Transaksi Terlalu Lama**
**Masalah:** Lock yang lama → antrian panjang
**✅ Solusi:** Batch processing dan transaksi pendek

### **🌪️ Problem #7: Query Complexity**
**Masalah:** Subquery bersarang, WHERE kompleks
```sql
-- KOMPLEKS DAN LAMBAT
SELECT * FROM mahasiswa 
WHERE id IN (
    SELECT mahasiswa_id FROM nilai 
    WHERE nilai > (
        SELECT AVG(nilai) FROM nilai WHERE mata_kuliah = 'Algoritma'
    )
);
```
**✅ Solusi:** Pecah jadi query sederhana atau pakai CTE/JOIN

---

## **4. Arsenal Senjata Optimasi Query 🛠️**

### **🎯 Senjata #1: INDEXING - The Ultimate Speed Booster**

**Konsep:** Index seperti **daftar isi buku** - langsung loncat ke halaman yang tepat!

```sql
-- Tanpa index: baca 100,000 mahasiswa satu-satu (😴 lambat)
-- Dengan index: langsung ke mahasiswa Informatika (⚡ cepat)
CREATE INDEX idx_jurusan ON mahasiswa(jurusan);
```

**Kapan Pakai Index:**
- ✅ Kolom di WHERE clause
- ✅ Kolom di JOIN condition  
- ✅ Kolom di ORDER BY
- ✅ Foreign key columns

**Kapan JANGAN Pakai Index:**
- ❌ Tabel kecil (<1000 baris)
- ❌ Kolom yang jarang diquery
- ❌ Terlalu banyak INSERT/UPDATE

### **🔗 Senjata #2: JOIN Strategy**

**Golden Rule:** Kolom JOIN **HARUS** ada index-nya!

```sql
-- SEBELUM: JOIN lambat
SELECT m.nama, k.nama_kelas
FROM mahasiswa m
JOIN kelas k ON m.kelas_id = k.id;  -- kelas_id belum ada index!

-- SESUDAH: Buat index dulu
CREATE INDEX idx_mahasiswa_kelas ON mahasiswa(kelas_id);
-- Sekarang JOIN jadi super cepat! 🚀
```

### **🧠 Senjata #3: Smart Query Writing**

#### **A. Hindari SELECT \* (Pemborosan Bandwidth)**
```sql
-- ❌ BURUK: Ambil semua kolom (boros)
SELECT * FROM mahasiswa WHERE nim = '2023001';

-- ✅ BAIK: Ambil yang perlu saja
SELECT nama, jurusan FROM mahasiswa WHERE nim = '2023001';
```

#### **B. WHERE Clause Optimization**
```sql
-- ❌ BURUK: Function di WHERE (index tidak terpakai)
SELECT * FROM mahasiswa WHERE UPPER(nama) = 'BUDI';

-- ✅ BAIK: Hindari function, pakai index
SELECT * FROM mahasiswa WHERE nama = 'Budi';
```

#### **C. Subquery vs JOIN**
```sql
-- 😴 LAMBAT: Subquery
SELECT nama FROM mahasiswa 
WHERE id IN (SELECT mahasiswa_id FROM nilai WHERE nilai >= 80);

-- ⚡ CEPAT: JOIN
SELECT DISTINCT m.nama 
FROM mahasiswa m 
JOIN nilai n ON m.id = n.mahasiswa_id 
WHERE n.nilai >= 80;
```

### **🔍 Senjata #4: EXPLAIN - Database Detective Tool**

**EXPLAIN** = mata-mata yang ngeliat apa yang dilakukan database!

```sql
-- Lihat rencana eksekusi
EXPLAIN SELECT * FROM mahasiswa WHERE jurusan = 'Informatika';

-- Lihat eksekusi real + timing
EXPLAIN ANALYZE SELECT * FROM mahasiswa WHERE jurusan = 'Informatika';
```

**Cara Baca EXPLAIN:**
- **Seq Scan** = 😴 Baca semua data (lambat)
- **Index Scan** = ⚡ Pakai index (cepat)  
- **Cost** = Estimasi "biaya" operasi
- **Actual Time** = Waktu eksekusi real

### **🧹 Senjata #5: Database Maintenance**

#### **VACUUM - Bersih-bersih Data Zombie**
```sql
-- Bersihkan dead tuples
VACUUM mahasiswa;

-- Full vacuum (lebih thorough)
VACUUM FULL mahasiswa;
```

#### **ANALYZE - Update Statistik**
```sql
-- Update statistik tabel untuk planner
ANALYZE mahasiswa;

-- Analyze semua tabel
ANALYZE;
```

---

## **5. Ringkasan Fundamental**

| Konsep              | Penjelasan Singkat                            |
| ------------------- | --------------------------------------------- |
| **Query**           | Perintah ambil data                           |
| **Execution Plan**  | Rencana database menjalankan query            |
| **Index**           | Shortcut untuk pencarian cepat                |
| **JOIN/Subquery**   | Gabungkan atau filter data; bisa bikin lambat |
| **EXPLAIN/ANALYZE** | Lihat bagaimana query dijalankan              |

---

# **Contoh Praktis: Mahasiswa & Nilai**

## **1. Struktur Tabel**

```sql
CREATE TABLE mahasiswa (
    id SERIAL PRIMARY KEY,
    nama VARCHAR(50),
    jurusan VARCHAR(50)
);

CREATE TABLE nilai (
    id SERIAL PRIMARY KEY,
    mahasiswa_id INT REFERENCES mahasiswa(id),
    mata_kuliah VARCHAR(50),
    nilai INT
);
```

## **2. Data Contoh**

```sql
INSERT INTO mahasiswa (nama, jurusan) VALUES
('Andi', 'Informatika'), ('Budi', 'Informatika'),
('Citra', 'Sistem Informasi'), ('Dewi', 'Informatika');

INSERT INTO nilai (mahasiswa_id, mata_kuliah, nilai) VALUES
(1, 'Matematika', 85), (1, 'Algoritma', 90),
(2, 'Matematika', 70), (3, 'Algoritma', 88),
(4, 'Matematika', 95);
```

## **3. Query Lambat**

```sql
SELECT nama
FROM mahasiswa
WHERE id IN (
    SELECT mahasiswa_id
    FROM nilai
    WHERE nilai >= 80
);
```

* Harus cek semua baris tabel nilai → lambat jika besar.

## **4. Query Lebih Cepat dengan JOIN**

```sql
SELECT DISTINCT m.nama
FROM mahasiswa m
JOIN nilai n ON m.id = n.mahasiswa_id
WHERE n.nilai >= 80;
```

* JOIN langsung → lebih efisien, terutama jika **mahasiswa_id terindeks**.

## **5. Optimasi dengan Index**

```sql
CREATE INDEX idx_nilai_mahasiswa ON nilai(mahasiswa_id);
CREATE INDEX idx_nilai_nilai ON nilai(nilai);
```

## **6. Analisis Query**

```sql
EXPLAIN ANALYZE
SELECT DISTINCT m.nama
FROM mahasiswa m
JOIN nilai n ON m.id = n.mahasiswa_id
WHERE n.nilai >= 80;
```

* Akan terlihat apakah **Index Scan** dipakai → query cepat.

---

# **Konsep Index dan Primary Key**

### **Apa itu Index?**

* Struktur data untuk mempercepat pencarian.
* Analogi: daftar isi buku → langsung ke halaman yang relevan.

### **Contoh di PostgreSQL**

```sql
CREATE INDEX idx_jurusan ON mahasiswa(jurusan);
```

### **Cek Index Digunakan**

```sql
EXPLAIN
SELECT * FROM mahasiswa WHERE jurusan = 'Informatika';
```

* Index Scan → database pakai index
* Seq Scan → membaca seluruh tabel

### **Primary Key vs Index**

| Konsep      | Keterangan                                   |
| ----------- | -------------------------------------------- |
| Primary Key | Unik, tidak boleh NULL, otomatis terindex    |
| Index       | Bisa di kolom manapun, mempercepat pencarian |

---

# **Contoh Tabel Relasi & Index**

### **Struktur Tabel**

```sql
CREATE TABLE jurusan (
    id_jurusan SERIAL PRIMARY KEY,
    nama_jurusan VARCHAR(50) NOT NULL
);

CREATE TABLE mahasiswa (
    id_mahasiswa SERIAL PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    nim VARCHAR(20) NOT NULL,
    id_jurusan INT NOT NULL REFERENCES jurusan(id_jurusan)
);

CREATE INDEX idx_nim ON mahasiswa(nim);
CREATE INDEX idx_mahasiswa_jurusan ON mahasiswa(id_jurusan);
```

### **Query Memanfaatkan Index**

1. Cari mahasiswa berdasarkan NIM:

```sql
SELECT * FROM mahasiswa WHERE nim = '12345';
```

2. Join mahasiswa & jurusan:

```sql
SELECT m.nama, m.nim, j.nama_jurusan
FROM mahasiswa m
JOIN jurusan j ON m.id_jurusan = j.id_jurusan
WHERE j.nama_jurusan = 'Sistem Informasi';
```

### **EXPLAIN untuk Join**

```sql
EXPLAIN
SELECT m.nama, m.nim, j.nama_jurusan
FROM mahasiswa m
JOIN jurusan j ON m.id_jurusan = j.id_jurusan
WHERE j.nama_jurusan = 'Sistem Informasi';
```

* Index Scan digunakan → join cepat.

---

# **🚀 Optimasi Operasi DML (INSERT, UPDATE, DELETE)**

## **Mengapa DML Bisa Lambat?**

DML berbeda dari SELECT - tidak cuma "baca" data, tapi "ubah" data + semua index-nya!

**Analogi:** 
- **SELECT** = Fotokopi buku (cepat)
- **INSERT** = Tulis buku baru + update semua katalog (lambat)
- **UPDATE** = Edit buku + update katalog (lebih lambat)
- **DELETE** = Hapus buku tapi katalog masih ada (bikin "sampah")

## **💡 Strategi Optimasi DML**

### **1. INSERT Optimization**
```sql
-- ❌ LAMBAT: Insert satu-satu
INSERT INTO mahasiswa (nama, jurusan) VALUES ('Budi', 'Informatika');
INSERT INTO mahasiswa (nama, jurusan) VALUES ('Ani', 'Informatika');
-- ... 10,000 kali

-- ✅ CEPAT: Batch insert
INSERT INTO mahasiswa (nama, jurusan) VALUES 
('Budi', 'Informatika'),
('Ani', 'Informatika'),
('Citra', 'Sistem Informasi');
-- ... semua sekaligus dalam 1 transaksi

-- 🚀 SUPER CEPAT: COPY dari file
\COPY mahasiswa(nama, jurusan) FROM 'data.csv' CSV HEADER;
```

### **2. UPDATE Optimization**
```sql
-- ❌ LAMBAT: Update tanpa index di WHERE
UPDATE mahasiswa SET status = 'aktif' WHERE nama = 'Budi';  -- full scan!

-- ✅ CEPAT: WHERE clause pakai index
CREATE INDEX idx_mahasiswa_nama ON mahasiswa(nama);
UPDATE mahasiswa SET status = 'aktif' WHERE nama = 'Budi';  -- index scan!

-- 🎯 HOT Update: Update kolom yang tidak di-index
UPDATE mahasiswa SET alamat = 'Jakarta' WHERE id = 123;  -- HOT update jika 'alamat' tidak di-index
```

### **3. DELETE Optimization**
```sql
-- ❌ BERMASALAH: DELETE banyak data
DELETE FROM log_aktivitas WHERE tanggal < '2023-01-01';  -- bikin banyak "dead tuple"

-- ✅ SOLUSI: VACUUM setelah DELETE besar
DELETE FROM log_aktivitas WHERE tanggal < '2023-01-01';
VACUUM log_aktivitas;  -- bersihkan "dead tuple"
```

### **4. Transaction Strategy**
```sql
-- ❌ LAMBAT: Transaksi per operasi
BEGIN;
INSERT INTO orders (customer_id, total) VALUES (1, 100000);
COMMIT;
BEGIN;
INSERT INTO orders (customer_id, total) VALUES (2, 200000);
COMMIT;
-- Overhead commit tinggi!

-- ✅ CEPAT: Batch transaction
BEGIN;
INSERT INTO orders (customer_id, total) VALUES 
(1, 100000),
(2, 200000),
(3, 150000);
COMMIT;
-- Satu commit untuk banyak operasi!
```

---

# **📊 Tipe Index di PostgreSQL**

| Tipe Index | Kegunaan | Best For | Contoh Use Case |
|------------|----------|----------|------------------|
| **B-Tree** (Default) | `=`, `<`, `>`, `BETWEEN`, `ORDER BY` | General purpose, primary key | `WHERE id = 123` |
| **Hash** | Hanya `=` (exact match) | Fast equality lookup | `WHERE status = 'active'` |
| **GIN** | Array, JSON, full-text search | Complex data types | `WHERE tags @> '{postgresql}'` |
| **GiST** | Geometric, range types | Spatial data, ranges | `WHERE location <-> point(0,0) < 100` |
| **BRIN** | Range data, very large tables | Time series, sequential data | `WHERE created_at BETWEEN ...` |

### **Kapan Pakai Index Apa?**
```sql
-- B-Tree: Untuk hampir semua kasus
CREATE INDEX idx_tanggal ON orders(created_at);  -- range queries

-- Hash: Untuk lookup exact value (rare use)
CREATE INDEX USING hash idx_status ON users(status);  -- hanya untuk =

-- GIN: Untuk JSON/Array
CREATE INDEX idx_tags ON products USING gin(tags);  -- WHERE tags @> '{electronics}'

-- BRIN: Untuk tabel huge dengan data sequential
CREATE INDEX idx_log_time ON access_logs USING brin(timestamp);  -- hemat space
```

---
