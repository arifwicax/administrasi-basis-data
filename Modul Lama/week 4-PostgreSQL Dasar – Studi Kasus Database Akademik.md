# 📚 PostgreSQL Dasar – Studi Kasus Database Akademik

## 1️⃣ DDL (Data Definition Language)

Digunakan untuk membuat dan mengubah struktur database.

### 📌 Studi Kasus

Database **`kampus`** dengan tabel **`mahasiswa`**:

* `nim` → **Primary Key**
* `nama` → teks
* `email` → unik
* `tanggal_lahir` → date
* `jenis_kelamin` → enum (`'L'`, `'P'`)
* `alamat` → text
* `hobi` → array
* `data_tambahan` → JSONB (fleksibel: prestasi, minat, dsb.)
* `created_at` → timestamp default waktu sekarang

---

### 🔹 CREATE (Membuat Database & Tabel)

```sql
-- Membuat database
CREATE DATABASE kampus;
 
-- Pindah ke database kampus
\c kampus;

-- Membuat enum jenis kelamin
CREATE TYPE gender AS ENUM ('L', 'P');

-- Membuat tabel mahasiswa
CREATE TABLE mahasiswa (
    nim VARCHAR(15) PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    tanggal_lahir DATE,
    jenis_kelamin gender,
    alamat TEXT,
    hobi TEXT[],
    data_tambahan JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 🔹 ALTER (Mengubah Struktur Tabel)

```sql
-- Tambah kolom baru
ALTER TABLE mahasiswa ADD COLUMN ipk NUMERIC(3,2);

-- Ubah panjang kolom nama
ALTER TABLE mahasiswa ALTER COLUMN nama TYPE VARCHAR(150);

-- Hapus kolom alamat
ALTER TABLE mahasiswa DROP COLUMN alamat;
```

---

### 🔹 DROP (Menghapus Database/Tabel)

```sql
DROP TABLE mahasiswa;
DROP TYPE gender;
DROP DATABASE kampus;
```

---

## 2️⃣ DML (Data Manipulation Language)

Digunakan untuk **memasukkan, memperbarui, dan menghapus data**.

### 🔹 INSERT (Tambah Data)

```sql
-- Satu baris
INSERT INTO mahasiswa (nim, nama, email, tanggal_lahir, jenis_kelamin, hobi, data_tambahan, ipk)
VALUES (
  '202501001',
  'Budi Santoso',
  'budi.santoso@example.com',
  '2003-05-12',
  'L',
  ARRAY['Membaca','Olahraga'],
  '{"prestasi": ["Juara 1 Lomba Matematika"], "minat":"Data Science"}',
  3.75
);

-- Banyak baris
INSERT INTO mahasiswa (nim, nama, email, tanggal_lahir, jenis_kelamin, hobi, data_tambahan, ipk)
VALUES
('202501002','Siti Aminah','siti.aminah@example.com','2002-11-20','P',ARRAY['Menyanyi'],'{"minat":"UI/UX"}',3.60),
('202501003','Andi Pratama','andi.pratama@example.com','2003-01-08','L',ARRAY['Coding','Gaming'],'{"prestasi":["Finalis AI Competition"]}',3.40);
```

---

### 🔹 UPDATE (Ubah Data)

```sql
-- Update email
UPDATE mahasiswa
SET email = 'budi.s@example.com'
WHERE nim = '202501001';

-- Tambah hobi
UPDATE mahasiswa
SET hobi = array_append(hobi,'Fotografi')
WHERE nim = '202501002';

-- Update IPK berdasarkan JSONB
UPDATE mahasiswa
SET ipk = ipk + 0.1
WHERE data_tambahan ->> 'minat' = 'Data Science';
```

---

### 🔹 DELETE (Hapus Data)

```sql
-- Hapus satu mahasiswa
DELETE FROM mahasiswa WHERE nim = '202501003';

-- Hapus mahasiswa IPK < 3.0
DELETE FROM mahasiswa WHERE ipk < 3.0;

-- Hapus semua data
DELETE FROM mahasiswa;
```

---

## 3️⃣ SELECT (Membaca Data)

### 🔹 SELECT Dasar

```sql
SELECT * FROM mahasiswa;
SELECT nama, email FROM mahasiswa;
SELECT * FROM mahasiswa WHERE jenis_kelamin = 'P';
```

---

### 🔹 ORDER BY & LIMIT

```sql
-- Urutkan IPK
SELECT nama, ipk FROM mahasiswa ORDER BY ipk DESC;

-- Ambil 2 mahasiswa IPK tertinggi
SELECT nama, ipk FROM mahasiswa ORDER BY ipk DESC LIMIT 2;
```

---

### 🔹 Filter dengan ARRAY

```sql
-- Mahasiswa dengan hobi "Coding"
SELECT nim, nama, hobi FROM mahasiswa WHERE 'Coding' = ANY(hobi);

-- Mahasiswa punya lebih dari 1 hobi
SELECT nim, nama FROM mahasiswa WHERE array_length(hobi,1) > 1;
```

---

### 🔹 Filter dengan JSONB

```sql
-- Minat UI/UX
SELECT nim, nama FROM mahasiswa WHERE data_tambahan ->> 'minat' = 'UI/UX';

-- Punya key "prestasi"
SELECT nim, nama FROM mahasiswa WHERE data_tambahan ? 'prestasi';

-- Punya prestasi tertentu
SELECT nim, nama FROM mahasiswa
WHERE data_tambahan @> '{"prestasi":["Juara 1 Lomba Matematika"]}';
```

---

### 🔹 Agregasi

```sql
SELECT COUNT(*) FROM mahasiswa;
SELECT AVG(ipk) FROM mahasiswa;
SELECT jenis_kelamin, COUNT(*) FROM mahasiswa GROUP BY jenis_kelamin;
```

---

## 4️⃣ JOIN Antar Tabel

Tambahan tabel: **mata\_kuliah** & **krs**

```sql
CREATE TABLE mata_kuliah (
    kode_mk VARCHAR(10) PRIMARY KEY,
    nama_mk VARCHAR(100),
    sks INT
);

CREATE TABLE krs (
    id_krs SERIAL PRIMARY KEY,
    nim VARCHAR(15) REFERENCES mahasiswa(nim) ON DELETE CASCADE,
    kode_mk VARCHAR(10) REFERENCES mata_kuliah(kode_mk) ON DELETE CASCADE,
    semester INT,
    nilai CHAR(2) CHECK (nilai IN ('A','B','C','D','E','F'))
);
```

### 🔹 Contoh JOIN

```sql
-- INNER JOIN
SELECT m.nim, m.nama, mk.nama_mk, k.nilai
FROM mahasiswa m
INNER JOIN krs k ON m.nim = k.nim
INNER JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk;

-- LEFT JOIN
SELECT m.nim, m.nama, mk.nama_mk, k.nilai
FROM mahasiswa m
LEFT JOIN krs k ON m.nim = k.nim
LEFT JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk;
```

---

* **DDL** → membuat/mengubah struktur DB
* **DML** → manipulasi data (`INSERT`, `UPDATE`, `DELETE`)
* **SELECT** → baca data (dengan filter, array, JSONB, agregasi)
* **JOIN** → relasi antar tabel
