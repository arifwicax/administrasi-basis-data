# Tugas 2 — Administrasi Basis Data

## Cakupan Materi: Week 5 – Week 7

**Mata Kuliah:** Administrasi Basis Data  
**Bobot:** 100 poin  
**Petunjuk:** Kerjakan semua bagian. Sertakan penjelasan dan query SQL bila diminta.

---

## Bagian A — Pilihan Ganda (20 poin)

*Pilih satu jawaban yang paling tepat.*

**1.** Apa yang dimaksud dengan **execution plan** pada PostgreSQL?

- a. Dokumen catatan log semua query yang pernah dijalankan
- b. Rencana langkah-langkah yang dipilih database untuk menjalankan query
- c. Kumpulan indeks yang tersedia pada suatu tabel
- d. Statistik distribusi data pada setiap kolom tabel

---

**2.** Perhatikan output `EXPLAIN` berikut:

```
Seq Scan on mahasiswa  (cost=0.00..4250.00 rows=200000 width=40)
```

Apa arti angka `4250.00` pada bagian `cost`?

- a. Waktu eksekusi dalam milidetik
- b. Perkiraan total biaya untuk menyelesaikan operasi ini
- c. Jumlah baris yang sudah dibaca dari disk
- d. Ukuran tabel dalam kilobyte

---

**3.** Manakah pernyataan yang benar tentang perbedaan `EXPLAIN` dan `EXPLAIN ANALYZE`?

- a. `EXPLAIN` menjalankan query, `EXPLAIN ANALYZE` tidak menjalankan query
- b. `EXPLAIN` hanya menampilkan rencana tanpa menjalankan query, `EXPLAIN ANALYZE` benar-benar menjalankan query
- c. Keduanya tidak menjalankan query, hanya menampilkan perkiraan
- d. `EXPLAIN ANALYZE` hanya bisa digunakan untuk query `SELECT`

---

**4.** Seorang developer menjalankan `EXPLAIN ANALYZE` dan menemukan perbedaan sangat besar antara perkiraan dan kenyataan:

```
Seq Scan on orders
  (cost=0.00..1500.00 rows=100 width=50)
  (actual rows=85000 ...)
```

Apa kemungkinan penyebab utama perbedaan besar ini?

- a. Query mengandung sintaks yang salah
- b. Statistik data tabel yang digunakan optimizer sudah usang atau kurang akurat
- c. Tidak ada indeks pada kolom yang difilter
- d. Tabel terlalu kecil untuk dianalisis

---

**5.** Dalam struktur tree execution plan, node yang harus dibaca **pertama kali** (operasi paling dasar) berada di...

- a. Bagian paling atas
- b. Bagian tengah
- c. Bagian paling bawah
- d. Sebelah kiri dari setiap baris

---

**6.** Query berikut dijalankan pada tabel `mahasiswa` dengan 500.000 baris:

```sql
SELECT * FROM mahasiswa WHERE jenis_kelamin = 'L';
```

Kolom `jenis_kelamin` hanya berisi nilai `'L'` atau `'P'`. Manakah pernyataan yang paling tepat?

- a. Index B-Tree pada `jenis_kelamin` pasti selalu membantu query ini
- b. Index pada `jenis_kelamin` kemungkinan tidak efektif karena selectivity-nya sangat rendah
- c. Query ini dijamin menggunakan `Index Scan` jika ada indeks
- d. PostgreSQL tidak bisa menjalankan query ini tanpa indeks

---

**7.** Mana dari kondisi berikut yang termasuk contoh **short query** (query selektif)?

- a. `SELECT AVG(ipk) FROM mahasiswa;`
- b. `SELECT COUNT(*) FROM krs GROUP BY semester;`
- c. `SELECT nama FROM mahasiswa WHERE nim = '2310110001';`
- d. `SELECT * FROM mahasiswa;`

---

**8.** Query berikut mengambil hampir 80% dari seluruh baris tabel. Strategi mana yang paling mungkin diterapkan PostgreSQL?

```sql
SELECT * FROM transaksi WHERE tahun >= 2020;
```

- a. `Index Scan` karena selalu lebih cepat dari `Seq Scan`
- b. `Seq Scan` karena membaca sebagian besar tabel lebih efisien dilakukan secara sekuensial
- c. `Bitmap Heap Scan` karena tidak ada cara lain
- d. `Index-Only Scan` karena menghemat I/O

---

**9.** Apa perbedaan utama antara **View** dan **Materialized View** di PostgreSQL?

- a. View untuk tabel kecil, Materialized View untuk tabel besar
- b. View menyimpan hasil query secara fisik, Materialized View tidak
- c. View tidak menyimpan hasil (selalu dijalankan ulang saat diakses), Materialized View menyimpan hasil secara fisik
- d. Keduanya identik, hanya berbeda nama

---

**10.** Kapan penggunaan **CTE (Common Table Expression)** lebih disarankan daripada **Temporary Table**?

- a. Saat hasil antara perlu digunakan berkali-kali oleh beberapa query berbeda
- b. Saat query hanya perlu satu subquery dan tidak perlu diulang berkali-kali dalam satu sesi
- c. Saat tabel memiliki lebih dari 10 juta baris
- d. Saat tidak ada memori tersisa di server

---

## Bagian B — Uraian Singkat (30 poin)

*Jawab dengan ringkas dan tepat. Setiap soal bernilai 6 poin.*

**11.** Jelaskan apa yang dimaksud dengan **cost** dalam output `EXPLAIN` pada PostgreSQL. Mengapa cost bukan satuan waktu, dan bagaimana cara yang benar untuk membandingkan cost antar operasi?

---

**12.** Jelaskan konsep **selectivity** dalam konteks optimasi query pendek. Berikan dua contoh kolom dengan selectivity tinggi dan dua contoh kolom dengan selectivity rendah dari konteks database akademik (mahasiswa, KRS, mata kuliah).

---

**13.** Jelaskan perbedaan antara **Semi-Join** dan **Anti-Join**. Berikan masing-masing satu contoh query SQL yang menggunakan polanya (dengan `EXISTS` atau `NOT EXISTS`).

---

**14.** Seorang DBA menemukan bahwa execution plan untuk query yang sama menghasilkan hasil berbeda setelah beberapa bulan. Sebutkan **tiga faktor** yang dapat menyebabkan execution plan berubah tanpa ada perubahan pada kode SQL.

---

**15.** Jelaskan kapan **Materialized View** lebih tepat digunakan dibandingkan View biasa. Sebutkan juga satu kelemahan utama Materialized View yang perlu diperhatikan.

---

## Bagian C — Analisis Execution Plan (30 poin)

*Baca setiap output `EXPLAIN` atau `EXPLAIN ANALYZE` berikut, lalu jawab pertanyaan yang tersedia.*

---

### Soal 16 — Membaca EXPLAIN Dasar (10 poin)

Perhatikan query dan output `EXPLAIN` berikut:

```sql
EXPLAIN
SELECT m.nama, k.kode_mk, k.nilai
FROM mahasiswa m
JOIN krs k ON m.nim = k.nim
WHERE m.angkatan = 2023;
```

```
Hash Join  (cost=1200.50..6800.75 rows=15000 width=35)
  Hash Cond: (k.nim = m.nim)
  ->  Seq Scan on krs k  (cost=0.00..3500.00 rows=180000 width=20)
  ->  Hash  (cost=900.00..900.00 rows=12000 width=25)
        ->  Index Scan using idx_mahasiswa_angkatan on mahasiswa m  
              (cost=0.43..900.00 rows=12000 width=25)
              Index Cond: (angkatan = 2023)
```

**a.** Gambarkan atau deskripsikan urutan eksekusi plan di atas dari operasi pertama hingga terakhir. *(3 poin)*

**b.** Mengapa PostgreSQL menggunakan `Index Scan` untuk tabel `mahasiswa` tetapi `Seq Scan` untuk tabel `krs`? Berikan alasan yang logis berdasarkan informasi di plan. *(4 poin)*

**c.** Jika developer ingin mengetahui **waktu eksekusi nyata** dan **jumlah baris aktual** yang diproses, apa yang harus diubah dari perintah `EXPLAIN` di atas? Tuliskan perintah yang dimodifikasi. *(3 poin)*

---

### Soal 17 — Membandingkan EXPLAIN dan EXPLAIN ANALYZE (10 poin)

Seorang DBA menjalankan `EXPLAIN ANALYZE` dan mendapatkan hasil berikut:

```
Seq Scan on krs  
  (cost=0.00..5800.00 rows=200 width=30)
  (actual time=0.042..85.312 rows=47500 loops=1)
  Filter: (nilai >= 75)
  Rows Removed by Filter: 152500
Planning Time: 0.312 ms
Execution Time: 89.140 ms
```

**a.** Berapa perkiraan baris (`rows`) yang dihitung optimizer, dan berapa baris aktual yang dihasilkan? Apakah ada kesenjangan yang signifikan? *(3 poin)*

**b.** Apa arti baris `Rows Removed by Filter: 152500`? Apa implikasinya terhadap performa query? *(3 poin)*

**c.** Berdasarkan nilai `actual time=0.042..85.312`, jelaskan arti angka `0.042` dan `85.312` dalam konteks eksekusi query. *(4 poin)*

---

### Soal 18 — Identifikasi Masalah pada Plan (10 poin)

Seorang developer melaporkan query laporan yang berjalan sangat lambat. Output `EXPLAIN ANALYZE`-nya adalah sebagai berikut:

```
Nested Loop  (cost=0.00..9850000.00 rows=3000000 width=60)
  (actual time=0.125..42350.820 rows=3000000 loops=1)
  ->  Seq Scan on transaksi t
        (cost=0.00..15000.00 rows=1000000 width=40)
        (actual time=0.050..1250.000 rows=1000000 loops=1)
  ->  Seq Scan on pelanggan p
        (cost=0.00..150.00 rows=3000 width=30)
        (actual time=0.010..0.030 rows=3 loops=1000000)
```

**a.** Identifikasi **dua masalah utama** yang terlihat pada execution plan di atas. *(4 poin)*

**b.** Algoritma join mana yang lebih cocok untuk menggantikan `Nested Loop Join` pada kasus ini? Jelaskan alasannya. *(3 poin)*

**c.** Tuliskan **satu tindakan konkret** yang bisa dilakukan DBA untuk membantu optimizer memilih algoritma join yang lebih baik, tanpa mengubah query SQL. *(3 poin)*

---

## Bagian D — Studi Kasus dan Implementasi SQL (20 poin)

*Gunakan skema database berikut untuk mengerjakan soal-soal pada bagian ini.*

### Skema Database

```sql
CREATE TABLE dosen (
    id_dosen SERIAL PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    bidang_keahlian VARCHAR(100)
);

CREATE TABLE mata_kuliah (
    kode_mk VARCHAR(10) PRIMARY KEY,
    nama_mk VARCHAR(100) NOT NULL,
    sks INT NOT NULL,
    id_dosen INT REFERENCES dosen(id_dosen)
);

CREATE TABLE mahasiswa (
    nim VARCHAR(12) PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    angkatan INT NOT NULL,
    program_studi VARCHAR(50),
    ipk NUMERIC(3,2)
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

### Soal 19 — Strategi Indeks untuk Short Query (8 poin)

Berikut adalah tiga query yang paling sering dijalankan pada sistem informasi akademik:

**Query A:**
```sql
SELECT nama, program_studi, ipk
FROM mahasiswa
WHERE nim = '2310110042';
```

**Query B:**
```sql
SELECT kode_mk, nilai
FROM krs
WHERE nim = '2310110042' AND semester = '2024/2025-Ganjil';
```

**Query C:**
```sql
SELECT nama, program_studi
FROM mahasiswa
WHERE angkatan = 2023 AND program_studi = 'Informatika';
```

**a.** Untuk setiap query (A, B, C), tentukan kolom mana yang sebaiknya diindeks. Tuliskan perintah `CREATE INDEX` yang paling sesuai untuk masing-masing query. *(5 poin)*

**b.** Pada Query C, apakah memungkinkan untuk membuat indeks agar query dapat menggunakan `Index-Only Scan`? Jika ya, modifikasi perintah `CREATE INDEX` Anda untuk mendukungnya dan jelaskan alasannya. *(3 poin)*

---

### Soal 20 — Optimasi Long Query dengan CTE dan Materialized View (12 poin)

Seorang DBA menemukan query laporan berikut yang berjalan sangat lambat karena memproses data dalam jumlah besar:

```sql
SELECT 
    m.program_studi,
    mk.nama_mk,
    COUNT(k.id_krs) AS jumlah_peserta,
    AVG(k.nilai) AS rata_rata_nilai,
    MAX(k.nilai) AS nilai_tertinggi
FROM krs k
JOIN mahasiswa m ON k.nim = m.nim
JOIN mata_kuliah mk ON k.kode_mk = mk.kode_mk
WHERE k.semester = '2024/2025-Ganjil'
  AND k.nilai IS NOT NULL
GROUP BY m.program_studi, mk.nama_mk
ORDER BY m.program_studi, rata_rata_nilai DESC;
```

**a.** Tulis ulang query di atas menggunakan **CTE** untuk memisahkan tahap filterisasi data `krs` dengan tahap agregasi. Pastikan logika hasilnya tetap sama. *(4 poin)*

**b.** Misalkan laporan ini dibutuhkan setiap hari dan datanya tidak berubah setiap menit. Buat **Materialized View** bernama `mv_rekap_nilai_semester` yang menyimpan hasil query tersebut, lalu tuliskan perintah untuk me-refresh-nya. *(4 poin)*

**c.** Jelaskan **dua keuntungan** penggunaan Materialized View dibandingkan menjalankan query asli berulang kali setiap kali laporan dibutuhkan, serta **satu konsekuensi** yang harus diterima tim developer. *(4 poin)*

---

## Rubrik Penilaian

| Bagian | Poin | Keterangan |
|--------|------|------------|
| A — Pilihan Ganda | 20 | 2 poin per soal |
| B — Uraian Singkat | 30 | 6 poin per soal |
| C — Analisis Execution Plan | 30 | Lihat poin per sub-soal |
| D — Studi Kasus SQL | 20 | Lihat poin per sub-soal |
| **Total** | **100** | |

---

*Tugas dikerjakan secara individu. Cantumkan Nama dan NIM pada lembar jawaban.*
