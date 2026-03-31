# Modul Pertemuan 8

## Administrasi Basis Data

### UTS: Analisis dan Optimasi Query PostgreSQL

---

## A. Identitas Kegiatan

**Nama Kegiatan:** Ujian Tengah Semester  
**Pertemuan:** 8  
**Bentuk:** ujian tertulis, analisis kasus, dan atau praktik terarah sesuai kebijakan dosen  
**Cakupan Materi:** pertemuan 1 sampai pertemuan 7

---

## B. Tujuan UTS

UTS dirancang untuk mengukur kemampuan mahasiswa dalam:

1. memahami arsitektur dasar PostgreSQL,
2. menjelaskan mekanisme pemrosesan query,
3. membedakan algoritma akses data dan join,
4. membaca `EXPLAIN` dan `EXPLAIN ANALYZE`,
5. menganalisis strategi indeks,
6. membedakan optimasi query pendek dan query panjang.

---

## C. Ruang Lingkup Materi yang Diujikan

Materi UTS mencakup:

1. pengantar administrasi basis data dan arsitektur PostgreSQL,
2. mekanisme pemrosesan query,
3. algoritma akses data dan index-only scan,
4. algoritma join,
5. analisis `EXPLAIN` dan `EXPLAIN ANALYZE`,
6. strategi pembuatan indeks dan optimasi query pendek,
7. optimasi query panjang.

---

## D. Bentuk Soal yang Dapat Digunakan

Soal UTS dapat disusun dalam bentuk:

- soal konsep,
- soal analisis execution plan,
- soal studi kasus optimasi query,
- soal interpretasi strategi akses data,
- soal praktik sederhana menggunakan PostgreSQL.

---

## E. Contoh Kisi-Kisi UTS

| Topik | Contoh kemampuan yang diukur |
| --- | --- |
| Arsitektur PostgreSQL | menjelaskan fungsi shared buffers dan WAL |
| Mekanisme query | menjelaskan parser, optimizer, dan executor |
| Algoritma akses data | membedakan seq scan, index scan, dan index-only scan |
| Algoritma join | memilih nested loop, hash join, atau merge join berdasarkan kasus |
| EXPLAIN | membaca operation, cost, rows, dan actual time |
| Strategi indeks | menentukan apakah indeks tertentu layak dibuat |
| Query panjang | menjelaskan kapan full scan lebih tepat atau kapan materialized view berguna |

---

## F. Persiapan Mahasiswa

Sebelum UTS, mahasiswa disarankan untuk:

1. meninjau ulang semua modul pertemuan 1 sampai 7,
2. berlatih membaca `EXPLAIN` dan `EXPLAIN ANALYZE`,
3. mengulang contoh query pendek dan query panjang,
4. memahami trade-off penggunaan indeks,
5. berlatih menjelaskan alasan teknis secara runtut.

---

## G. Penutup

Pertemuan ini digunakan untuk evaluasi tengah semester. Karena itu, tidak ada materi baru. Fokus utama adalah mengukur pemahaman mahasiswa atas fondasi optimasi PostgreSQL yang sudah dipelajari pada tujuh pertemuan pertama.