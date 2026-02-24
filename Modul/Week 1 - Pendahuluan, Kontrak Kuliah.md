# Modul Pertemuan 1

## Administrasi Basis Data

### Introduction dan Kontrak Kuliah

---

## A. Identitas Mata Kuliah

Nama Mata Kuliah: Administrasi Basis Data
Bobot: 3 SKS
Prasyarat: Basis Data (SQL, ERD, Normalisasi)
DBMS yang digunakan: PostgreSQL

Buku utama:
PostgreSQL Query Optimization – Henrietta Dombrovskaya

---

## B. Tujuan Pertemuan Pertama

Setelah mengikuti pertemuan pertama, mahasiswa diharapkan mampu:

1. Menjelaskan perbedaan Basis Data dan Administrasi Basis Data.
2. Memahami peran dan tanggung jawab Database Administrator (DBA).
3. Menjelaskan perbedaan konsep OLTP dan OLAP.
4. Memahami gambaran umum materi selama satu semester.
5. Memahami sistem penilaian dan aturan perkuliahan.

---

## C. Pengantar Mata Kuliah

Pada mata kuliah Basis Data, mahasiswa telah belajar merancang database dan menulis query SQL yang benar.

Namun dalam praktik profesional, masalah yang sering muncul adalah:

* Mengapa query berjalan lambat?
* Mengapa server database sering overload?
* Mengapa dashboard tidak kunjung selesai dimuat?

Administrasi Basis Data berfokus pada pemahaman cara kerja database secara internal dan bagaimana mengoptimalkannya secara sistematis.

Mata kuliah ini menekankan performance tuning, analisis execution plan, strategi indeks, serta monitoring performa menggunakan PostgreSQL.

---

## D. Peran DBA

Database Administrator bertanggung jawab untuk:

* Menjaga stabilitas sistem database
* Mengoptimalkan performa query
* Mengelola transaksi dan concurrency
* Mengidentifikasi dan memperbaiki bottleneck
* Mengelola backup dan recovery
* Mengatur konfigurasi server database

Mahasiswa diarahkan untuk memiliki kompetensi sebagai junior DBA atau performance engineer pada level awal.

---

## E. Konsep Dasar: OLTP dan OLAP

### OLTP (Online Transaction Processing)

Digunakan untuk transaksi harian yang membutuhkan respons cepat.

Contoh:

* Login sistem
* Transaksi pembayaran
* Pengisian data

Ciri utama:

* Query pendek
* Banyak pengguna bersamaan
* Respons cepat
* Data sering berubah

---

### OLAP (Online Analytical Processing)

Digunakan untuk analisis data dan pelaporan.

Contoh:

* Dashboard manajemen
* Laporan kinerja
* Analisis tren

Ciri utama:

* Query panjang dan kompleks
* Banyak operasi agregasi
* Memproses data dalam jumlah besar

Perbedaan utama:

| Aspek  | OLTP      | OLAP     |
| ------ | --------- | -------- |
| Tujuan | Transaksi | Analisis |
| Query  | Pendek    | Panjang  |
| Fokus  | Kecepatan | Insight  |

---

## F. Materi yang Akan Dipelajari

Mahasiswa akan mempelajari:

* Arsitektur PostgreSQL
* Mekanisme pemrosesan query
* Algoritma akses data dan join
* Analisis EXPLAIN dan EXPLAIN ANALYZE
* Strategi pembuatan indeks
* Optimasi query pendek dan panjang
* Optimasi operasi INSERT, UPDATE, DELETE
* Integrasi aplikasi dan dampak ORM
* Benchmarking performa
* Monitoring dan visualisasi performa menggunakan Grafana

---

## G. Kontrak Kuliah

### Sistem Penilaian

| Komponen                          | Bobot |
| --------------------------------- | ----- |
| Tugas                             | 20%   |
| Kuis                              | 10%   |
| UTS (Analisis Execution Plan)     | 20%   |
| Praktikum                         | 20%   |
| UAS (Proyek)                      | 30%   |

---

## H. Proyek Akhir

Mahasiswa diwajibkan:

1. Menggunakan PostgreSQL.
2. Menggunakan dataset minimal 100.000 record.
3. Mengidentifikasi minimal tiga query lambat.
4. Melakukan optimasi melalui:

   * Perancangan indeks
   * Perbaikan query
   * Penyesuaian konfigurasi
5. Melakukan benchmarking sebelum dan sesudah optimasi.
6. Mengimplementasikan monitoring menggunakan Grafana.
7. Menyajikan hasil dalam bentuk dashboard visual dan laporan teknis.

Output proyek:

* Laporan analisis dan rekomendasi teknis
* Perbandingan performa sebelum dan sesudah tuning
* Dashboard Grafana yang menampilkan metrik database

Dengan proyek ini, mahasiswa tidak hanya melakukan tuning, tetapi juga belajar melakukan observability dan visualisasi performa seperti di lingkungan industri.

---

# Rencana 14 Pertemuan

**Minggu 1**
Pengantar mata kuliah dan kontrak kuliah. Peran DBA, konsep OLTP dan OLAP.

**Minggu 2**
Arsitektur PostgreSQL: proses, shared buffer, WAL, dan MVCC.

**Minggu 3**
Teori pemrosesan query: logical plan dan physical plan.

**Minggu 4**
Algoritma akses data: full scan, index scan, dan join algorithm.

**Minggu 5**
Execution plan (EXPLAIN): memahami cost dan struktur plan.

**Minggu 6**
Execution plan (EXPLAIN ANALYZE): praktik analisis plan nyata.

**Minggu 7**
Optimasi indeks untuk query pendek: selectivity, composite index, partial index.

**Minggu 8**
UTS: analisis execution plan dan rekomendasi optimasi.

**Minggu 9**
Optimasi query panjang: join order dan strategi grouping.

**Minggu 10**
Teknik lanjutan: CTE, materialized view, dan partitioning.

**Minggu 11**
Optimasi data modification: INSERT, UPDATE, DELETE dan dampaknya.

**Minggu 12**
Integrasi aplikasi dan ORM serta dampaknya terhadap performa.

**Minggu 13**
Introduction to Grafana dan monitoring database.
Instalasi dasar, konsep dashboard, metrik PostgreSQL yang perlu dimonitor.

**Minggu 14**
Monitoring lanjutan menggunakan Grafana dan presentasi proyek akhir.

---

## Capaian Akhir Mata Kuliah

Pada akhir semester, mahasiswa mampu:

* Menganalisis dan mengoptimalkan query lambat secara sistematis.
* Membaca execution plan secara profesional.
* Melakukan benchmarking performa database.
* Membangun dashboard monitoring menggunakan Grafana.
* Menyusun laporan performance tuning yang komprehensif.

Jika Anda ingin, saya dapat melanjutkan dengan menyusun RPS formal lengkap berbasis OBE (CPMK, Sub-CPMK, indikator, metode pembelajaran, dan asesmen).
