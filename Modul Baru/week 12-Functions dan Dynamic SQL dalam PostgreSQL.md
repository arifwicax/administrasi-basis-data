# Modul Pertemuan 12

## Administrasi Basis Data

### Functions dan Dynamic SQL dalam PostgreSQL

---

## A. Identitas Materi

**Nama Modul:** Functions dan Dynamic SQL dalam PostgreSQL  
**Pertemuan:** 12  
**Prasyarat:** integrasi aplikasi dan performa, desain database, optimasi query, keamanan query  
**DBMS:** PostgreSQL  
**Fokus Materi:** memahami fungsi dalam PostgreSQL, kapan function membantu aplikasi, serta bagaimana dynamic SQL digunakan secara aman dan tepat

---

## B. Tujuan Pembelajaran

Setelah mengikuti pertemuan ini, mahasiswa diharapkan mampu:

1. Menjelaskan apa itu function di PostgreSQL.
2. Membedakan function PostgreSQL dengan function di bahasa pemrograman umum.
3. Menjelaskan struktur dasar `CREATE FUNCTION`.
4. Menjelaskan kapan function membantu dan kapan justru memperlambat sistem.
5. Menjelaskan apa itu dynamic SQL dan kapan digunakan.
6. Menjelaskan perbedaan static SQL, prepared statement, dan dynamic SQL.
7. Menjelaskan risiko SQL injection dan cara menguranginya.
8. Menggunakan function dan dynamic SQL secara lebih hati-hati dalam aplikasi.

---

## C. Keterkaitan dengan Pertemuan Sebelumnya

Pada pertemuan sebelumnya, kita membahas bagaimana aplikasi berinteraksi dengan database dan bagaimana ORM atau pola akses data dapat memengaruhi performa.

Pada pertemuan ini, kita melihat dua fitur PostgreSQL yang sering dipakai untuk menjembatani kebutuhan aplikasi dan database, yaitu function dan dynamic SQL. Keduanya bisa sangat berguna, tetapi juga bisa menimbulkan masalah jika digunakan tanpa memahami dampaknya terhadap performa dan keamanan.

---

## D. Peta Materi

1. pengertian function,
2. struktur dasar function,
3. PL/pgSQL dan output function,
4. function dan performa,
5. function vs procedure,
6. pengertian dynamic SQL,
7. static SQL vs dynamic SQL,
8. keamanan query,
9. best practice, praktikum, dan latihan.

---

## E. Pengantar

Function di PostgreSQL dapat dipahami sebagai program kecil yang disimpan di dalam database. Function dapat menerima input, memproses data, lalu mengembalikan output.

Sementara itu, dynamic SQL adalah teknik membangun query saat runtime. Teknik ini berguna ketika bentuk query belum diketahui sepenuhnya sejak awal.

Kedua konsep ini penting karena sering muncul pada aplikasi nyata. Namun mahasiswa perlu memahami satu hal sejak awal:

> Function dan dynamic SQL tidak otomatis membuat sistem lebih cepat. Keduanya hanya membantu jika digunakan pada konteks yang tepat.

---

## F. Function dalam PostgreSQL

### 1. Apa itu function?

Function adalah objek di PostgreSQL yang:

- menerima parameter,
- menjalankan logika tertentu,
- mengembalikan hasil.

### 2. Perbandingan dengan function di bahasa pemrograman

| Function di bahasa pemrograman | Function di PostgreSQL |
| --- | --- |
| fokus pada logika aplikasi | fokus pada logika yang dekat dengan data |
| berjalan di sisi aplikasi | berjalan di sisi database |
| tidak selalu terkait query | sangat erat dengan query dan struktur data |

### 3. Struktur dasar function

```sql
CREATE FUNCTION tambah(a int, b int)
RETURNS int AS $$
BEGIN
   RETURN a + b;
END;
$$ LANGUAGE plpgsql;
```

### 4. Menjalankan function

```sql
SELECT tambah(2, 3);
```

---

## G. PL/pgSQL dan Function dengan Output Kompleks

PL/pgSQL adalah bahasa prosedural yang paling umum dipakai untuk membuat function di PostgreSQL.

Dengan PL/pgSQL, kita dapat memakai:

- variabel,
- percabangan,
- loop,
- penanganan exception.

### Contoh sederhana

```sql
CREATE FUNCTION status_nilai(nilai int)
RETURNS text AS $$
BEGIN
   IF nilai >= 60 THEN
      RETURN 'Lulus';
   ELSE
      RETURN 'Tidak Lulus';
   END IF;
END;
$$ LANGUAGE plpgsql;
```

Function juga dapat mengembalikan:

- satu nilai,
- satu record,
- sekumpulan baris (`SETOF`).

---

## H. Kapan Function Membantu?

Function bermanfaat jika:

- logika dipakai berulang,
- aplikasi ingin mengurangi roundtrip,
- database perlu mengembalikan hasil yang sudah lebih siap pakai,
- aturan bisnis tertentu lebih aman ditempatkan dekat dengan data.

Contoh pemakaian yang masuk akal:

- validasi sederhana,
- pembungkusan beberapa langkah query,
- menghasilkan satu set data untuk aplikasi.

---

## I. Kapan Function Bisa Merugikan Performa?

Masalah muncul jika function dipanggil berulang untuk setiap baris pada tabel besar.

Contoh pola yang kurang baik:

```sql
SELECT flight_id, num_passengers(flight_id)
FROM flight;
```

Jika `num_passengers` melakukan query lagi di dalam function, maka akan terjadi overhead berulang.

### Pendekatan yang sering lebih baik

```sql
SELECT flight_id, COUNT(*)
FROM boarding_pass
GROUP BY flight_id;
```

### Prinsip penting

Yang perlu dihindari bukan function itu sendiri, tetapi penggunaan function yang membuat pola kerja per baris padahal masalahnya bisa diselesaikan dengan satu query berbasis set.

---

## J. Function vs Procedure

Mahasiswa sering menyamakan function dan procedure. Keduanya mirip, tetapi tidak identik.

| Function | Procedure |
| --- | --- |
| dipanggil dalam `SELECT` atau ekspresi | dipanggil dengan `CALL` |
| biasanya mengembalikan nilai | tidak harus mengembalikan nilai |
| cocok untuk komputasi atau hasil data | cocok untuk alur kerja prosedural tertentu |

Dalam praktik PostgreSQL modern, procedure berguna ketika logika prosedural dan kontrol transaksi perlu dipisahkan dari function.

---

## K. Dynamic SQL

### 1. Apa itu dynamic SQL?

Dynamic SQL adalah SQL yang dibentuk sebagai teks atau string, lalu baru dieksekusi saat runtime.

```sql
DECLARE
   v_sql text;
   cnt int;
BEGIN
   v_sql := 'SELECT count(*) FROM booking';
   EXECUTE v_sql INTO cnt;
END;
```

### 2. Kapan dynamic SQL diperlukan?

Dynamic SQL digunakan ketika bentuk query itu sendiri dapat berubah, misalnya:

- kondisi filter opsional,
- nama tabel ditentukan saat runtime,
- urutan `ORDER BY` berubah,
- query builder dinamis.

---

## L. Static SQL, Prepared Statement, dan Dynamic SQL

| Static SQL | Prepared Statement | Dynamic SQL |
| --- | --- | --- |
| bentuk query tetap | bentuk query tetap, nilai parameter berubah | bentuk query bisa berubah |
| paling sederhana | cocok untuk query berulang | cocok untuk query fleksibel |
| mudah diuji | efisien pada pola tertentu | lebih kompleks |

### Pelajaran penting

Dynamic SQL bukan pengganti semua query. Static SQL tetap menjadi pilihan default jika bentuk query tidak perlu berubah.

---

## M. Risiko Keamanan dan SQL Injection

Dynamic SQL sangat mudah disalahgunakan jika input pengguna langsung digabung ke string query.

### Contoh berbahaya

```sql
v_sql := 'SELECT * FROM users WHERE username = ''' || user_input || '''';
```

### Cara mengurangi risiko

Gunakan fungsi PostgreSQL yang tepat seperti:

- `quote_literal()` untuk literal,
- `format()` dengan `%I` untuk identifier dan `%L` untuk literal.

### Contoh lebih aman

```sql
v_sql := format(
    'SELECT * FROM passenger WHERE passenger_id = %L',
    v_id
);
EXECUTE v_sql;
```

---

## N. Best Practice

1. Gunakan function jika memang membantu logika yang dekat dengan data.
2. Hindari function yang menjalankan query berulang untuk setiap baris besar.
3. Gunakan static SQL sebagai pilihan utama jika query tidak perlu berubah.
4. Gunakan dynamic SQL hanya ketika fleksibilitas bentuk query memang dibutuhkan.
5. Jangan pernah membangun dynamic SQL dari input pengguna tanpa sanitasi yang benar.
6. Uji function dan dynamic SQL dengan contoh nyata, bukan hanya berdasarkan sintaks yang berhasil dibuat.

---

## O. Ringkasan

1. Function di PostgreSQL berguna untuk logika yang dekat dengan data.
2. Function bisa membantu performa, tetapi juga bisa merusaknya jika memicu pola query berulang.
3. Dynamic SQL adalah teknik membentuk query saat runtime, bukan jaminan performa lebih cepat.
4. Static SQL, prepared statement, dan dynamic SQL dipakai untuk masalah yang berbeda.
5. Keamanan sangat penting, terutama pada dynamic SQL.

---

## P. Praktikum

1. Buat satu function sederhana yang menerima dua input dan mengembalikan satu hasil.
2. Buat satu function PL/pgSQL dengan `IF` sederhana.
3. Buat contoh dynamic SQL aman menggunakan `format()`.
4. Bandingkan pendekatan function per baris dengan query agregasi biasa secara konseptual.

### Contoh latihan

```sql
CREATE FUNCTION tambah(a int, b int)
RETURNS int AS $$
BEGIN
   RETURN a + b;
END;
$$ LANGUAGE plpgsql;
```

---

## Q. Latihan

### Soal Konsep

1. Apa yang dimaksud dengan function di PostgreSQL?
2. Mengapa function di database tidak sama persis dengan function di bahasa pemrograman umum?
3. Apa perbedaan static SQL dan dynamic SQL?
4. Mengapa SQL injection menjadi risiko besar pada dynamic SQL?

### Soal Analisis

5. Jelaskan kapan function dapat membantu mengurangi roundtrip aplikasi.
6. Mengapa function yang dipanggil untuk setiap baris dapat memperlambat sistem?
7. Jelaskan kapan prepared statement lebih tepat daripada dynamic SQL.

### Soal Praktis

8. Buat contoh function sederhana yang mengembalikan teks status kelulusan.
9. Buat contoh dynamic SQL aman dengan `format()`.
10. Jelaskan perbedaan pemanggilan function dan procedure secara singkat.

---

## R. Penutup

Pertemuan ini menekankan bahwa function dan dynamic SQL adalah alat yang sangat berguna dalam PostgreSQL, tetapi keduanya harus dipakai dengan disiplin. Mahasiswa perlu melihatnya bukan sebagai trik, melainkan sebagai bagian dari desain akses data yang harus aman, efisien, dan sesuai kebutuhan aplikasi.
