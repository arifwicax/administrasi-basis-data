
# 📌 Tugas Besar Basis Data – PostgreSQL

## Studi Kasus: Sistem Akademik

### 1. ERD (Entity Relationship Diagram)

a. Buatlah **ERD** untuk sistem akademik dengan ketentuan:

* Entitas **Mahasiswa**, **Dosen**, **Mata\_Kuliah**, dan **KRS**.

* Hubungan:

  * Mahasiswa dapat mengambil banyak KRS (One-to-Many).
  * Satu mata kuliah dapat diambil oleh banyak mahasiswa melalui KRS (One-to-Many).
  * Satu dosen dapat mengajar banyak mata kuliah (One-to-Many).
    b. Sertakan **atribut** sesuai deskripsi berikut:

* **Mahasiswa**: nim, nama, email, tanggal\_lahir, jenis\_kelamin, hobi, data\_tambahan, ipk

* **Dosen**: nidn, nama, email, keahlian

* **Mata\_Kuliah**: kode\_mk, nama\_mk, sks, nidn

* **KRS**: id\_krs, nim, kode\_mk, semester, nilai

c. Gambarkan ERD dalam bentuk **diagram** (boleh pakai tools seperti Draw\.io, Lucidchart, dbdiagram.io, atau gambar manual lalu scan/foto).

---

### 2. DDL (Data Definition Language)

a. Buatlah database bernama `akademik`.
b. Buatlah tabel sesuai ERD yang telah Anda rancang, dengan ketentuan:

* **Primary Key** pada masing-masing entitas.
* **Foreign Key** sesuai relasi antar entitas.
* `email` pada mahasiswa & dosen harus **unik**.
* `jenis_kelamin` hanya boleh `'L'` atau `'P'`.
* `ipk` berupa bilangan desimal antara `0.00 – 4.00`.
* `semester` pada KRS hanya boleh 1–14.
* `nilai` hanya boleh `'A','B','C','D','E','F'`.
* Relasi `ON DELETE` harus disesuaikan (contoh: jika mahasiswa dihapus maka data KRS juga ikut terhapus).

---

### 3. DML (Data Manipulation Language)

a. Masukkan minimal **3 data mahasiswa**, **2 data dosen**, dan **3 data mata kuliah**.
b. Tambahkan minimal **3 data KRS** sesuai mahasiswa dan mata kuliah yang ada.
c. Perbarui salah satu data mahasiswa (misalnya ubah `email`).
d. Hapus salah satu mata kuliah, lalu periksa efeknya terhadap tabel KRS.

---

### 4. DQL (Data Query Language – SELECT)

a. Tampilkan semua data mahasiswa.
b. Tampilkan mahasiswa dengan `ipk > 3.50`.
c. Urutkan mahasiswa berdasarkan `nama` secara ascending.
d. Tampilkan hanya **2 mahasiswa pertama**.
e. Hitung jumlah mahasiswa berdasarkan `jenis_kelamin`.
f. Hitung rata-rata `ipk` seluruh mahasiswa.

---

👉 **Output yang dikumpulkan mahasiswa:**

1. Gambar ERD
2. Script SQL (DDL, DML, DQL)
3. Screenshot hasil eksekusi query

---
