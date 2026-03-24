# **Fundamental Query Optimization & Tuning di PostgreSQL**

## **1. Apa itu Query?**

Query adalah **perintah untuk meminta data dari database**.

```sql
SELECT nama, jurusan 
FROM mahasiswa
WHERE jurusan = 'Informatika';
```

* `SELECT` → memilih kolom
* `FROM` → tabel sumber
* `WHERE` → kondisi filter

> Query ini meminta database menampilkan semua mahasiswa jurusan Informatika.

---

## **2. Bagaimana Database Menjalankan Query?**

PostgreSQL membuat **rencana eksekusi (execution plan)**:

1. **Planner** → memilih rencana tercepat
2. **Executor** → menjalankan rencana dan mengembalikan hasil

**Analogi:**
Mencari barang di supermarket: jalan langsung (sequential scan) vs. pakai shortcut (index scan).

---

## **3. Mengapa Query Bisa Lambat?**

1. Tabel terlalu besar → scanning semua baris memakan waktu
2. Tidak ada index → harus cek satu per satu
3. Subquery atau join kompleks → banyak perhitungan
4. Statistik tabel tidak up-to-date → rencana eksekusi salah

---

## **4. Cara Membuat Query Lebih Cepat**

### a. **Indexing**

* Seperti daftar isi buku → mempercepat pencarian.

```sql
CREATE INDEX idx_jurusan ON mahasiswa(jurusan);
```

### b. **JOIN Efisien**

* Pastikan kolom join **terindeks**:

```sql
SELECT m.nama, k.nama_kelas
FROM mahasiswa m
JOIN kelas k ON m.kelas_id = k.id;
```

### c. **Hindari Subquery Berat**

* Gunakan **JOIN** atau **CTE (WITH)** daripada subquery di SELECT/WHERE.

### d. **EXPLAIN / EXPLAIN ANALYZE**

* Menunjukkan apa yang dilakukan database di balik layar:

```sql
EXPLAIN ANALYZE
SELECT * FROM mahasiswa WHERE jurusan = 'Informatika';
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

# **Tipe Index di PostgreSQL**

| Tipe    | Keterangan / Kegunaan              |
| ------- | ---------------------------------- |
| B-Tree  | Default, untuk `=`, range, join    |
| Hash    | Exact match (`=`) saja             |
| GiST    | Data geospatial, teks, range       |
| SP-GiST | Efisien untuk data tersebar        |
| BRIN    | Tabel sangat besar, data berurutan |

---
