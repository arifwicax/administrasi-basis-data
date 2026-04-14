# Tugas 1 — Administrasi Basis Data

## Cakupan Materi: Week 1 – Week 4

**Mata Kuliah:** Administrasi Basis Data  
**Bobot:** 100 poin  
**Petunjuk:** Kerjakan semua bagian. Sertakan penjelasan dan contoh SQL bila diminta.

---

## Bagian A — Pilihan Ganda (20 poin)

*Pilih satu jawaban yang paling tepat.*

**1.** Seorang DBA menemukan query yang berjalan lambat pada jam sibuk. Tindakan mana yang paling tepat sebagai langkah awal investigasi?

- a. Langsung tambah indeks pada semua kolom tabel
- b. Jalankan `EXPLAIN ANALYZE` untuk membaca execution plan query tersebut
- c. Hapus tabel dan buat ulang dengan struktur baru
- d. Tingkatkan RAM server sebagai solusi utama

---

**2.** Sistem informasi akademik yang digunakan mahasiswa untuk isi KRS setiap semester adalah contoh dari...

- a. OLAP, karena memproses banyak data historis
- b. OLTP, karena membutuhkan respons cepat untuk transaksi harian
- c. Data Warehouse, karena menyimpan data dalam skala besar
- d. Batch Processing, karena dijalankan hanya satu kali sehari

---

**3.** Komponen PostgreSQL yang bertugas menyimpan halaman data di memori agar tidak selalu dibaca dari disk adalah...

- a. WAL (Write-Ahead Log)
- b. Background Process
- c. Shared Buffers
- d. Client Process

---

**4.** Perhatikan query berikut:

```sql
SELECT nama FROM mahasiswa WHERE angkatan = 2023;
```

Pada tahap apa PostgreSQL memeriksa apakah kolom `nama` benar-benar ada di tabel `mahasiswa`?

- a. Parsing
- b. Validasi (Analyzer)
- c. Query Rewrite
- d. Eksekusi

---

**5.** Optimizer PostgreSQL memilih strategi eksekusi berdasarkan estimasi biaya. Faktor mana yang **tidak** dipertimbangkan oleh optimizer?

- a. Ukuran tabel
- b. Ketersediaan indeks
- c. Nama pengguna yang menjalankan query
- d. Statistik distribusi data

---

**6.** Index B-Tree **tidak** cocok digunakan untuk kondisi filter mana?

- a. `WHERE angkatan = 2023`
- b. `WHERE nilai BETWEEN 70 AND 90`
- c. `WHERE nama LIKE '%ali%'`
- d. `WHERE ipk > 3.5`

---

**7.** Index Hash cocok digunakan secara khusus untuk kondisi...

- a. `WHERE nilai BETWEEN 60 AND 80`
- b. `WHERE nim = '123456789'`
- c. `WHERE nama LIKE 'A%'`
- d. `WHERE angkatan >= 2020`

---

**8.** PostgreSQL memilih `Seq Scan` (Sequential Scan) alih-alih `Index Scan`. Kondisi mana yang paling mungkin menyebabkan hal ini?

- a. Tabel hanya berisi 10 baris
- b. Query mengembalikan 95% dari total baris tabel
- c. Tidak ada kondisi `WHERE` pada query
- d. Semua jawaban di atas benar

---

**9.** `Index-Only Scan` dapat dilakukan hanya apabila...

- a. Tabel memiliki lebih dari satu indeks
- b. Semua kolom yang dibutuhkan query sudah tersedia di dalam indeks itu sendiri
- c. Tabel menggunakan tipe data teks
- d. Query menggunakan `ORDER BY`

---

**10.** Tabel `mahasiswa` berisi 500.000 baris dan tabel `krs` berisi 2.000.000 baris. Kedua tabel di-join dengan kondisi `ON mahasiswa.nim = krs.nim`. Algoritma join mana yang paling mungkin dipilih PostgreSQL?

- a. Nested Loop Join, karena paling sederhana
- b. Merge Join, karena data sudah pasti terurut
- c. Hash Join, karena efisien untuk equality join pada tabel besar
- d. Cross Join, karena menggabungkan semua kombinasi

---

## Bagian B — Soal Uraian Singkat (30 poin)

*Jawab dengan ringkas dan tepat. Setiap soal bernilai 6 poin.*

**11.** Jelaskan perbedaan antara OLTP dan OLAP menggunakan satu contoh konkret untuk masing-masing dari konteks sistem informasi universitas.

---

**12.** Sebutkan dan jelaskan secara singkat **lima tahapan** pemrosesan query pada PostgreSQL, dari query dikirim oleh pengguna sampai hasil dikembalikan.

---

**13.** Jelaskan apa yang dimaksud dengan **selectivity** dalam konteks pemilihan algoritma akses data. Mengapa selectivity tinggi cenderung membuat PostgreSQL memilih `Index Scan`, sedangkan selectivity rendah cenderung mengarah ke `Seq Scan`?

---

**14.** Sebuah tabel `produk` berisi kolom `id`, `nama`, `kategori`, dan `harga`. Jelaskan dalam kondisi apa `Index-Only Scan` bisa terjadi pada query berikut, dan apa yang harus dipersiapkan agar scan tersebut bisa dilakukan:

```sql
SELECT nama, harga FROM produk WHERE kategori = 'Elektronik';
```

---

**15.** Bandingkan `Nested Loop Join` dan `Hash Join` dari sisi:
- kompleksitas pemrosesan,
- kebutuhan memori,
- kondisi join yang didukung,
- skenario terbaik penggunaannya.

---

## Bagian C — Analisis Execution Plan (25 poin)

*Baca output `EXPLAIN` berikut dan jawab pertanyaan yang tersedia.*

### Soal 16 (10 poin)

Perhatikan output `EXPLAIN` berikut:

```
Seq Scan on mahasiswa  (cost=0.00..3210.00 rows=100000 width=50)
  Filter: (angkatan = 2023)
```

**a.** Apa yang dimaksud dengan `cost=0.00..3210.00`? Jelaskan nilai awal dan nilai akhir. *(3 poin)*

**b.** Mengapa PostgreSQL memilih `Seq Scan` dan bukan `Index Scan`? Berikan **dua kemungkinan alasan**. *(4 poin)*

**c.** Tuliskan perintah SQL yang dapat digunakan untuk membuat indeks pada kolom `angkatan` agar PostgreSQL berpotensi beralih ke `Index Scan`. *(3 poin)*

---

### Soal 17 (15 poin)

Perhatikan output `EXPLAIN` berikut:

```
Hash Join  (cost=1500.00..8200.00 rows=50000 width=30)
  Hash Cond: (krs.nim = mahasiswa.nim)
  ->  Seq Scan on krs  (cost=0.00..4000.00 rows=200000 width=15)
  ->  Hash  (cost=800.00..800.00 rows=50000 width=20)
        ->  Seq Scan on mahasiswa  (cost=0.00..800.00 rows=50000 width=20)
```

**a.** Algoritma join apa yang digunakan? Jelaskan secara singkat cara kerjanya berdasarkan output ini. *(4 poin)*

**b.** Tabel mana yang dijadikan **build side** (pihak yang membangun hash table) dan tabel mana yang menjadi **probe side**? Mengapa? *(4 poin)*

**c.** Jelaskan apa itu `Hash Cond` dan apa artinya baris `Hash Cond: (krs.nim = mahasiswa.nim)` pada konteks ini. *(3 poin)*

**d.** Jika pada tabel `mahasiswa` terdapat sangat sedikit baris (misalnya hanya 50 baris) dan tabel `krs` sangat besar (2 juta baris), algoritma join mana yang lebih mungkin dipilih PostgreSQL? Jelaskan alasannya. *(4 poin)*

---

## Bagian D — Studi Kasus dan Implementasi SQL (25 poin)

*Gunakan skema database berikut untuk mengerjakan soal-soal pada bagian ini.*

### Skema Database

```sql
CREATE TABLE fakultas (
    id_fakultas SERIAL PRIMARY KEY,
    nama_fakultas VARCHAR(100) NOT NULL
);

CREATE TABLE mahasiswa (
    nim VARCHAR(12) PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    angkatan INT NOT NULL,
    ipk NUMERIC(3,2),
    id_fakultas INT REFERENCES fakultas(id_fakultas)
);

CREATE TABLE mata_kuliah (
    kode_mk VARCHAR(10) PRIMARY KEY,
    nama_mk VARCHAR(100) NOT NULL,
    sks INT NOT NULL
);

CREATE TABLE krs (
    id_krs SERIAL PRIMARY KEY,
    nim VARCHAR(12) REFERENCES mahasiswa(nim),
    kode_mk VARCHAR(10) REFERENCES mata_kuliah(kode_mk),
    nilai NUMERIC(5,2),
    semester VARCHAR(10)
);
```

---

### Soal 18 — Query dan Join (10 poin)

Tuliskan query SQL untuk setiap kebutuhan berikut. Gunakan tipe join yang paling sesuai dan jelaskan alasan pemilihan join tersebut.

**a.** Tampilkan `nim`, `nama`, dan `nama_fakultas` untuk seluruh mahasiswa, **termasuk** mahasiswa yang belum memiliki data fakultas. *(3 poin)*

**b.** Tampilkan `nama` mahasiswa dan `nama_mk` mata kuliah yang mereka ambil, **hanya** untuk mahasiswa angkatan 2022 yang sudah memiliki nilai. *(4 poin)*

**c.** Tampilkan seluruh mata kuliah beserta jumlah mahasiswa yang mengambilnya (termasuk mata kuliah yang belum diambil siapapun). Kelompokkan hasilnya dan urutkan dari mata kuliah paling banyak diambil. *(3 poin)*

---

### Soal 19 — Strategi Indeks (8 poin)

Diberikan query yang sering dijalankan pada sistem:

```sql
SELECT nim, nama, ipk
FROM mahasiswa
WHERE angkatan = 2023 AND ipk >= 3.5;
```

**a.** Tentukan tipe indeks yang paling tepat dan kolom mana yang harus diindeks. Tuliskan perintah `CREATE INDEX` yang sesuai. *(3 poin)*

**b.** Dalam kondisi apa query di atas berpotensi menggunakan `Index-Only Scan`? Modifikasi perintah `CREATE INDEX` Anda dari poin (a) agar mendukung `Index-Only Scan` untuk query tersebut. *(3 poin)*

**c.** Jelaskan satu risiko yang perlu dipertimbangkan jika tabel `mahasiswa` sering mengalami operasi `INSERT` dan `UPDATE`. *(2 poin)*

---

### Soal 20 — Analisis Performa Komprehensif (7 poin)

Seorang DBA menemukan laporan bahwa query berikut berjalan sangat lambat (>30 detik) pada database produksi dengan 5 juta baris di tabel `krs`:

```sql
SELECT m.nama, mk.nama_mk, k.nilai
FROM krs k
JOIN mahasiswa m ON k.nim = m.nim
JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
WHERE k.semester = '2024/2025-Ganjil'
  AND k.nilai >= 75;
```

**a.** Sebutkan **tiga langkah investigasi** yang akan dilakukan DBA sebelum mengambil tindakan optimasi, sesuai peran DBA yang dipelajari pada week 1. *(3 poin)*

**b.** Berdasarkan pemahaman Anda tentang arsitektur PostgreSQL (week 1) dan algoritma akses data (week 3), identifikasi **dua potensi bottleneck** pada query ini dan usulan perbaikannya. *(4 poin)*

---

## Rubrik Penilaian

| Bagian | Poin | Keterangan |
|--------|------|------------|
| A — Pilihan Ganda | 20 | 2 poin per soal |
| B — Uraian Singkat | 30 | 6 poin per soal |
| C — Analisis Execution Plan | 25 | Lihat poin per sub-soal |
| D — Studi Kasus SQL | 25 | Lihat poin per sub-soal |
| **Total** | **100** | |

---

*Tugas dikerjakan secara individu. Cantumkan Nama dan NIM pada lembar jawaban.*
