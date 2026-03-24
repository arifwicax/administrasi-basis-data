# Week 3

## 📌 SQL Dasar & Manipulasi Data

**Tujuan:** Dapat membuat, membaca, memperbarui, dan menghapus data (CRUD).

---

### 1️⃣ DDL (Data Definition Language)

Digunakan untuk mendefinisikan struktur database dan tabel:

* `CREATE` → Membuat database atau tabel
* `ALTER` → Mengubah struktur tabel (tambah/ubah/hapus kolom)
* `DROP` → Menghapus database atau tabel

---

### 2️⃣ DML (Data Manipulation Language)

Digunakan untuk manipulasi data dalam tabel:

* `INSERT` → Menambahkan data baru
* `UPDATE` → Memperbarui data yang sudah ada
* `DELETE` → Menghapus data

---

### 3️⃣ SELECT Dasar

Digunakan untuk membaca data dari tabel:

* `SELECT *` → Menampilkan semua data
* `WHERE` → Menyaring data berdasarkan kondisi
* `ORDER BY` → Mengurutkan data (ASC/DESC)
* `LIMIT` → Membatasi jumlah data yang ditampilkan

---

### 4️⃣ Operator & Fungsi

Digunakan untuk melakukan pencarian dan perhitungan.

**Operator:**

* `=` (sama dengan)
* `<>` (tidak sama dengan)
* `LIKE` (pencarian pola)
* `IN` (cek dalam himpunan nilai)
* `BETWEEN` (cek dalam rentang nilai)

**Fungsi Agregasi:**

* `COUNT()` → Menghitung jumlah baris
* `SUM()` → Menjumlahkan nilai
* `AVG()` → Menghitung rata-rata

---

### 5️⃣ Kunci Utama & Relasi

Digunakan untuk menghubungkan tabel:

* **Primary Key (PK)** → Identitas unik tiap baris dalam tabel
* **Foreign Key (FK)** → Kunci untuk menghubungkan tabel lain
* **One-to-Many** → Satu data di tabel A terkait dengan banyak data di tabel B
* **Many-to-Many** → Banyak data di tabel A terkait dengan banyak data di tabel B (melalui tabel penghubung)

---

## 📌 Tipe Data dalam PostgreSQL

PostgreSQL menyediakan berbagai macam tipe data untuk menyimpan informasi sesuai kebutuhan.

---

### 1️⃣ Tipe Data Number (Angka)

Digunakan untuk menyimpan bilangan bulat maupun pecahan.

| Tipe Data          | Keterangan                                        | Contoh Nilai   |
| ------------------ | ------------------------------------------------- | -------------- |
| `SMALLINT`         | Bilangan bulat kecil (-32.768 s/d 32.767)         | `123`          |
| `INTEGER` / `INT`  | Bilangan bulat standar (-2 M s/d 2 M)             | `2025`         |
| `BIGINT`           | Bilangan bulat besar                              | `9999999999`   |
| `DECIMAL(p,s)`     | Bilangan desimal dengan presisi                   | `1234.56`      |
| `NUMERIC(p,s)`     | Sama dengan DECIMAL, presisi tinggi               | `100.75`       |
| `REAL`             | Bilangan pecahan presisi tunggal (floating point) | `3.14`         |
| `DOUBLE PRECISION` | Bilangan pecahan presisi ganda                    | `2.718281828`  |
| `SERIAL`           | Auto-increment integer                            | `1, 2, 3, ...` |

**Contoh:**

```sql
CREATE TABLE produk (
  id SERIAL PRIMARY KEY,
  nama VARCHAR(50),
  harga NUMERIC(10,2),
  stok INT
);
```

---

### 2️⃣ Tipe Data String (Teks & Karakter)

| Tipe Data    | Keterangan                            | Contoh Nilai                                |
| ------------ | ------------------------------------- | ------------------------------------------- |
| `CHAR(n)`    | Teks tetap sepanjang n karakter       | `'ABC  '`                                   |
| `VARCHAR(n)` | Teks dengan panjang maksimum n        | `'Laptop'`                                  |
| `TEXT`       | Teks panjang (tanpa batas signifikan) | `'Deskripsi produk yang sangat panjang...'` |

**Contoh:**

```sql
CREATE TABLE user_account (
  username VARCHAR(30) NOT NULL,
  password TEXT NOT NULL
);
```

---

### 3️⃣ Tipe Data Date dan Time

| Tipe Data     | Keterangan                      | Contoh Nilai             |
| ------------- | ------------------------------- | ------------------------ |
| `DATE`        | Menyimpan tanggal               | `2025-09-13`             |
| `TIME`        | Menyimpan waktu (tanpa tanggal) | `14:30:00`               |
| `TIMESTAMP`   | Menyimpan tanggal & waktu       | `2025-09-13 14:30:00`    |
| `TIMESTAMPTZ` | Timestamp dengan zona waktu     | `2025-09-13 14:30:00+07` |
| `INTERVAL`    | Selisih waktu (durasi)          | `2 days 5 hours`         |

**Contoh:**

```sql
CREATE TABLE log_akses (
  id SERIAL PRIMARY KEY,
  user_id INT,
  waktu_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 4️⃣ Tipe Data Boolean

* Hanya menyimpan `TRUE`, `FALSE`, atau `NULL`.
* Alias: bisa menggunakan `'t' / 'f'`, `1 / 0`, `'yes' / 'no'`.

**Contoh:**

```sql
CREATE TABLE siswa (
  id SERIAL PRIMARY KEY,
  nama VARCHAR(50),
  aktif BOOLEAN DEFAULT TRUE
);
```

---

### 5️⃣ Tipe Data Enum

Enum digunakan untuk membuat tipe data dengan daftar nilai terbatas.

**Contoh:**

```sql
-- Buat tipe ENUM
CREATE TYPE status_pesanan AS ENUM ('pending', 'proses', 'selesai', 'batal');

-- Gunakan dalam tabel
CREATE TABLE pesanan (
  id SERIAL PRIMARY KEY,
  produk VARCHAR(50),
  status status_pesanan DEFAULT 'pending'
);
```

---

### 6️⃣ Tipe Data Lainnya yang Sering Digunakan

| Tipe Data        | Keterangan                                     | Contoh Nilai                           |
| ---------------- | ---------------------------------------------- | -------------------------------------- |
| `UUID`           | Universally Unique Identifier                  | `550e8400-e29b-41d4-a716-446655440000` |
| `JSON` / `JSONB` | Menyimpan data JSON (B = binary lebih efisien) | `{"nama": "Arif", "umur": 25}`         |
| `ARRAY`          | Menyimpan array nilai                          | `'{1,2,3,4}'`                          |
| `BYTEA`          | Menyimpan data biner (misal file, gambar)      | `\xDEADBEEF`                           |
| `CIDR`, `INET`   | Menyimpan alamat jaringan/IP                   | `192.168.1.1`                          |
| `MONEY`          | Menyimpan nilai uang (format lokal)            | `Rp1000.00`                            |

**Contoh:**

```sql
CREATE TABLE dokumen (
  id UUID DEFAULT gen_random_uuid(),
  metadata JSONB,
  tags TEXT[],
  file BYTEA
);
```

---

#### 🔹 1. **Array Literal → `{}` (kurung kurawal)**

Kalau kita **langsung menuliskan nilai array** di query SQL, PostgreSQL memakai **kurung kurawal `{}`**.

📌 Contoh:

```sql
-- Membuat tabel dengan kolom array
CREATE TABLE mahasiswa (
    nim VARCHAR(10) PRIMARY KEY,
    nama VARCHAR(50),
    hobi TEXT[]
);

-- Insert data dengan array literal
INSERT INTO mahasiswa (nim, nama, hobi)
VALUES ('M001', 'Budi', '{"Membaca", "Olahraga", "Coding"}');
```

👉 Hasilnya di kolom `hobi` akan tersimpan:

```
{Membaca,Olahraga,Coding}
```

---

#### 🔹 2. **JSON / JSONB Array → `[]` (kurung siku)**

Kalau kita pakai **tipe data JSON/JSONB**, array ditulis dengan **kurung siku `[]`** (sesuai standar JSON).

📌 Contoh:

```sql
-- Tabel dengan kolom JSONB
CREATE TABLE mahasiswa_json (
    nim VARCHAR(10) PRIMARY KEY,
    data JSONB
);

-- Insert data dengan JSON array
INSERT INTO mahasiswa_json (nim, data)
VALUES ('M002', '{"nama": "Siti", "hobi": ["Menyanyi", "Menari", "Fotografi"]}');
```

👉 Hasilnya di kolom `data`:

```json
{
  "nama": "Siti",
  "hobi": ["Menyanyi", "Menari", "Fotografi"]
}
```

---

### 📊 Perbedaan singkat

| Tipe Data    | Simbol Array | Contoh            |
| ------------ | ------------ | ----------------- |
| `ARRAY`      | `{}`         | `{"A", "B", "C"}` |
| `JSON/JSONB` | `[]`         | `["A", "B", "C"]` |

---

👉 Jadi:

* Kalau kolomnya **ARRAY** → pakai `{}`
* Kalau kolomnya **JSON/JSONB** → pakai `[]`


## 📌 Contoh Khusus: ARRAY, JSON, JSONB

### 🔹 ARRAY

Digunakan untuk menyimpan daftar nilai dalam satu kolom.

```sql
CREATE TABLE mahasiswa (
  id SERIAL PRIMARY KEY,
  nama VARCHAR(50),
  hobi TEXT[]
);

INSERT INTO mahasiswa (nama, hobi) VALUES
  ('Andi', ARRAY['Membaca', 'Berenang', 'Coding']),
  ('Budi', ARRAY['Gaming', 'Futsal']);

-- Query
SELECT nama, hobi FROM mahasiswa;
SELECT * FROM mahasiswa WHERE 'Coding' = ANY(hobi);
```

---

### 🔹 JSON

Menyimpan data dalam format teks JSON.

```sql
CREATE TABLE produk (
  id SERIAL PRIMARY KEY,
  nama VARCHAR(50),
  spesifikasi JSON
);

INSERT INTO produk (nama, spesifikasi) VALUES
  ('Laptop', '{"processor": "Intel i7", "ram": "16GB", "storage": "512GB SSD"}'),
  ('HP', '{"merk": "Samsung", "model": "Galaxy A52"}');

-- Query
SELECT * FROM produk;
SELECT nama, spesifikasi ->> 'processor' AS processor FROM produk;
```

---

### 🔹 JSONB

Mirip JSON, tapi lebih efisien (binary), bisa di-*index* dan lebih cepat untuk query.

```sql
CREATE TABLE pesanan (
  id SERIAL PRIMARY KEY,
  detail JSONB
);

INSERT INTO pesanan (detail) VALUES
  ('{"produk": "Laptop", "jumlah": 2, "harga": 15000000}'),
  ('{"produk": "Mouse", "jumlah": 5, "harga": 200000}');

-- Query
SELECT * FROM pesanan;
SELECT detail ->> 'produk' AS produk, (detail ->> 'harga')::INT AS harga FROM pesanan;
SELECT * FROM pesanan WHERE detail ->> 'produk' = 'Laptop';
```

---

✨ **Perbedaan singkat:**

* `ARRAY` → daftar nilai dengan tipe sama.
* `JSON` → format teks JSON, fleksibel tapi query lebih lambat.
* `JSONB` → format binary JSON, lebih cepat & bisa di-*index*.

---