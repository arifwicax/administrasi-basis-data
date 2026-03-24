# Modul Pertemuan 2

## Administrasi Basis Data

### Optimasi Database: Konsep, Tujuan, dan Praktik

---

## A. Identitas Materi

**Nama Modul:** Optimasi Database
**Pertemuan:** 2
**Prasyarat:** Basis Data, SQL, ERD, Normalisasi
**DBMS:** PostgreSQL
**Buku Utama:** *PostgreSQL Query Optimization* – Henrietta Dombrovskaya

---

## B. Tujuan Pembelajaran

Setelah mengikuti pertemuan ini, mahasiswa diharapkan mampu:

1. Menjelaskan konsep optimasi database dan perbedaannya dengan sekadar membuat query cepat.
2. Memahami perbedaan bahasa deklaratif dan imperatif dalam SQL.
3. Menentukan tujuan optimasi yang terukur dan relevan.
4. Menganalisis desain database yang optimal sesuai kebutuhan bisnis.
5. Memahami peran optimasi dalam siklus hidup aplikasi dan monitoring performa.

---

## C. Pengantar Optimasi Database

Optimasi adalah proses penting agar database bekerja secara efisien dan responsif. Tanpa optimasi yang baik, sistem dapat menjadi lambat, boros sumber daya, dan sulit dikembangkan.

Optimasi tidak hanya berlaku pada query, tetapi juga mencakup:

* Desain database
* Struktur tabel dan relasi
* Arsitektur aplikasi
* Cara aplikasi berinteraksi dengan database

Dalam modul ini, kita akan memahami bagaimana cara berpikir yang benar dalam melakukan optimasi.

---

## D. Apa Itu Optimasi?

Optimasi berarti segala perubahan yang membuat sistem bekerja lebih cepat, lebih efisien, dan lebih hemat sumber daya.

Kesalahan umum dalam pengembangan adalah berpikir:

> “Yang penting jalan dulu, nanti dioptimasi.”

Pendekatan ini berisiko karena:

* Query bisa menjadi lambat dan sulit diperbaiki.
* Struktur database bisa tidak efisien sejak awal.
* Perubahan di tahap akhir menjadi lebih mahal dan kompleks.

Idealnya, optimasi sudah dipikirkan sejak tahap:

* Perancangan database
* Penulisan query
* Perancangan aplikasi

Yang paling penting dalam optimasi bukan hanya teknik, tetapi memahami:

* Bagaimana database memproses query
* Bagaimana query planner memilih execution plan

Prinsip utamanya adalah:

> Berpikirlah seperti database.

Artinya, pahami beban kerja yang harus dilakukan database untuk menjalankan query.

---

## E. Bahasa Deklaratif dan Imperatif

### 1. Bahasa Imperatif (contoh: Java)

Dalam bahasa imperatif:

* Programmer menentukan langkah demi langkah proses.
* Urutan eksekusi ditentukan secara eksplisit.
* Fokus pada bagaimana cara mencapai hasil.

### 2. Bahasa Deklaratif (SQL)

Dalam SQL:

* Kita menyatakan hasil yang diinginkan.
* Kita tidak menentukan langkah-langkah eksekusi.
* Database optimizer memilih cara terbaik menjalankan query.
* Fokus pada apa yang ingin didapatkan.

Karena SQL bersifat deklaratif, dua query yang menghasilkan hasil sama belum tentu memiliki performa yang sama.

Keputusan optimizer dipengaruhi oleh:

* Struktur penyimpanan
* Index
* Statistik data
* Distribusi nilai dalam tabel

---

## F. Contoh Perbedaan Performa Query

Perhatikan dua query berikut:

### Query 1

```sql
SELECT flight_id, departure_airport, arrival_airport
FROM flight
WHERE scheduled_arrival BETWEEN '2020-10-14' AND '2020-10-15';
```

### Query 2

```sql
SELECT flight_id, departure_airport, arrival_airport
FROM flight
WHERE scheduled_arrival::date = '2020-10-14';
```

Kedua query mungkin menghasilkan data yang sama.

Namun perbedaannya:

* Query pertama tidak mengubah tipe data kolom sehingga index dapat digunakan.
* Query kedua melakukan casting (`::date`) sehingga index pada kolom asli bisa tidak digunakan.

Akibatnya, waktu eksekusi dapat berbeda secara signifikan.

Pelajaran penting:
Hasil yang sama tidak berarti performa yang sama.

---

## G. Optimasi dalam Konteks Sistem

Database tidak berdiri sendiri. Ia menjadi dasar berbagai aplikasi.

Pengguna tidak merasakan apakah satu query sudah optimal atau tidak. Yang mereka rasakan adalah performa keseluruhan sistem.

Karena itu, optimasi harus:

* Berdampak pada sistem secara keseluruhan
* Sesuai dengan kebutuhan bisnis
* Tidak dilakukan secara terpisah dari konteks aplikasi

Dalam beberapa kasus, dengan mengevaluasi kembali kebutuhan laporan, beban server bisa dikurangi secara signifikan.

---

## H. OLTP dan OLAP

Database umumnya diklasifikasikan menjadi:

### OLTP (Online Transaction Processing)

* Mendukung operasi harian.
* Biasanya memiliki banyak query pendek.
* Fokus pada response time cepat.

### OLAP (Online Analytical Processing)

* Mendukung analisis dan pelaporan.
* Dapat memiliki query panjang dan kompleks.
* Fokus pada agregasi dan pemrosesan data besar.

Panjang query tidak ditentukan oleh panjang kode SQL, tetapi oleh beban kerja dan waktu eksekusi.

Pendekatan optimasi untuk OLTP dan OLAP berbeda.

---

## I. Desain Database dan Performa

Optimasi seharusnya dimulai sejak tahap desain.

Contoh kasus: penyimpanan nomor telepon.

### Desain Satu Tabel

Semua data akun dan nomor telepon disimpan dalam satu tabel `account`.

Cocok jika:

* Nomor telepon hanya atribut tambahan.
* Tidak digunakan untuk pencarian.

### Desain Dua Tabel

Data akun disimpan di tabel `account`, dan nomor telepon di tabel `phone`.

Cocok jika:

* Satu akun memiliki banyak nomor.
* Nomor digunakan untuk pencarian.
* Dibutuhkan fleksibilitas data.

Pemilihan desain harus mempertimbangkan:

* Cara data digunakan.
* Frekuensi penggunaan.
* Kebutuhan performa.

Desain database sangat memengaruhi performa jangka panjang.

---

## J. Optimasi pada Tingkat Aplikasi

Query dijalankan oleh aplikasi. Masalah performa sering terjadi bukan karena satu query lambat, tetapi karena:

* Terlalu banyak query kecil.
* Pola pemanggilan yang tidak efisien.
* Struktur aplikasi yang kurang optimal.

Contoh:

* Setiap query 0,1 detik.
* Dalam satu halaman ada 100 query.
* Total menjadi 10 detik.

Optimasi harus melihat hubungan antara aplikasi dan database.

---

## K. Optimasi Sepanjang Siklus Hidup Sistem

Optimasi tidak berhenti setelah sistem dirilis.

Performa harus terus dipantau karena:

* Data bertambah.
* Distribusi data berubah.
* Frekuensi query meningkat.
* Versi database diperbarui.

Query yang dahulu cepat bisa menjadi lambat seiring waktu.

Tidak ada sistem yang optimal selamanya.

---

## L. Karakteristik PostgreSQL

Beberapa hal penting dalam PostgreSQL:

1. Tidak menyediakan optimizer hints seperti Oracle.
   Query harus ditulis dengan baik agar optimizer dapat bekerja optimal.

2. Perbedaan antara query terparameter dan dynamic SQL dapat memengaruhi performa.

3. PostgreSQL terus berkembang dengan fitur baru, tipe data baru, dan peningkatan optimizer.

Karena itu, penting untuk selalu mengikuti dokumentasi terbaru.

---

## M. Ringkasan

* SQL adalah bahasa deklaratif, bukan imperatif.
* Optimasi adalah bagian penting dari pengembangan database.
* Optimasi harus dimulai sejak tahap desain.
* Hasil query yang sama belum tentu memiliki performa yang sama.
* Optimasi harus mempertimbangkan sistem secara keseluruhan.
* Performa harus dipantau sepanjang siklus hidup sistem.

Tujuan akhirnya adalah membangun sistem yang efisien, stabil, dan responsif dalam jangka panjang.

