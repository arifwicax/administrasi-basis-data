# 📘 Soal Studi Kasus: **Manajemen User & Hak Akses Sistem Perpustakaan**

## 📌 Deskripsi

Anda diminta merancang sistem database **Perpustakaan Kampus** menggunakan PostgreSQL. Sistem ini digunakan oleh mahasiswa, petugas perpustakaan, dan admin. Setiap user memiliki hak akses berbeda sesuai prinsip **least privilege**.

---

## 🧩 Bagian A: Perancangan Database

1. Buatlah **ERD sederhana** dari entitas berikut:

   * **Anggota** (nim, nama, jurusan, angkatan)
   * **Petugas** (id_petugas, nama, jabatan)
   * **Buku** (kode_buku, judul, pengarang, tahun)
   * **Peminjaman** (id_pinjam, nim, kode_buku, tgl_pinjam, tgl_kembali, id_petugas)

   ➝ Gambarkan relasi antar tabel sesuai kebutuhan sistem perpustakaan.

2. Buatlah **DDL SQL** untuk mendefinisikan tabel sesuai ERD di atas dengan kunci primer dan foreign key yang tepat.

---

## 🧩 Bagian B: Manajemen User & Role

1. Buatlah user berikut di PostgreSQL:

   * `mhs_perpus` dengan password `mhs123`
   * `petugas_perpus` dengan password `ptg123`
   * `admin_perpus` dengan password `adm123`

2. Buatlah role berikut dengan hak akses berbeda:

   * **role_mhs** → hanya bisa melihat data buku dan riwayat peminjaman.
   * **role_petugas** → bisa mencatat transaksi peminjaman (INSERT, UPDATE), serta melihat tabel anggota dan buku.
   * **role_admin** → memiliki full access ke semua tabel.

3. Hubungkan masing-masing user dengan role yang sesuai.

---

## 🧩 Bagian C: Uji Coba Hak Akses

1. Login sebagai `mhs_perpus`, lalu uji:

   * Apakah bisa melakukan `SELECT` pada tabel **buku**?
   * Apakah bisa melakukan `INSERT` pada tabel **peminjaman**?

2. Login sebagai `petugas_perpus`, lalu uji:

   * Apakah bisa `INSERT` data pada tabel **peminjaman**?
   * Apakah bisa `DELETE` data pada tabel **buku**?

3. Login sebagai `admin_perpus`, lalu uji:

   * Apakah bisa `DELETE` data pada tabel **buku**?

Tuliskan hasil pengujian Anda.

---

## 🧩 Bagian D: Latihan Mandiri

1. Tambahkan user baru **keuangan_perpus** dengan hak akses hanya untuk melihat tabel **anggota** (misalnya untuk menghitung denda berdasarkan angkatan).
2. Buat role baru **role_kepala_perpus** dengan aturan:

   * Bisa melihat semua tabel.
   * Bisa menghapus data pada tabel **peminjaman** jika ada kesalahan input.
   * Tidak boleh menghapus data pada tabel **anggota** dan **buku**.

---