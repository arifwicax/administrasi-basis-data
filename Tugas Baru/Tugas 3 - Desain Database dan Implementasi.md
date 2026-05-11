# Tugas 3: Desain Database dan Implementasi PostgreSQL

## Administrasi Basis Data

**Topik:** Desain Database untuk Performa  
**Bobot:** 20% dari nilai akhir  
**Deadline:** 16 Mei 2026, pukul 23:59  
**Pengumpulan:** File SQL + Dokumen PDF melalui LMS

---

## Deskripsi Tugas

Anda diminta untuk:
1. **Identifikasi masalah** di sekitar Anda yang membutuhkan sistem database
2. **Desain database** dengan mempertimbangkan trade-off performa
3. **Implementasikan** ke PostgreSQL dengan query OLTP dan OLAP
4. **Testing dan optimasi** menggunakan EXPLAIN ANALYZE

---

## Bagian 1: Identifikasi Masalah (15 poin)

### 1.1 Pilih Domain Masalah

Pilih SATU domain dari kehidupan sehari-hari Anda:

**Contoh Domain:**
- Sistem akademik (nilai, absensi, jadwal)
- Toko/warung (inventori, penjualan, pelanggan)
- Klinik/puskesmas (pasien, rekam medis, appointment)
- Kos-kosan (kamar, penyewa, pembayaran)
- Rental (mobil/motor/alat, booking, pembayaran)
- Laundry (customer, order, tracking)
- Event organizer (acara, peserta, tiket)
- Atau domain lain yang Anda pahami

**Dokumentasikan (2-3 halaman):**
1. **Nama sistem** yang akan dibuat
2. **Latar belakang masalah** - Apa masalah yang ingin diselesaikan?
3. **Requirement utama** - Minimal 5 fitur yang harus ada
4. **Kebutuhan OLTP** - Transaksi harian apa saja?
5. **Kebutuhan OLAP** - Laporan/analisis apa yang dibutuhkan?

**Kriteria:**
- Masalah jelas dan realistis (5 poin)
- Requirement lengkap (5 poin)
- Identifikasi OLTP/OLAP tepat (5 poin)

---

## Bagian 2: Desain Database (30 poin)

### 2.1 Entity Relationship Diagram (10 poin)

Buat ERD yang mencakup:
- Minimal 6 entitas utama
- Relasi dengan kardinalitas (1:1, 1:N, N:M)
- Primary key dan foreign key

**Tools:** draw.io, dbdiagram.io, atau gambar tangan

---

### 2.2 Trade-off Analysis (15 poin)

Jelaskan minimal 3 keputusan desain penting:

**Contoh pertanyaan yang harus dijawab:**
- Apakah data yang bisa multiple (telepon, alamat) dipisah tabel?
- Natural key atau surrogate key? Mengapa?
- Ada data yang perlu JSON/JSONB? Kapan gunakan?
- Ada tabel yang sengaja di-denormalisasi? Alasannya?
- Strategi untuk query OLAP: view biasa atau materialized view?

**Format:**
```
Keputusan 1: [Judul keputusan]
- Pilihan: [A atau B]
- Alasan: [Penjelasan]
- Trade-off: [Apa yang dikorbankan]
```

---

### 2.3 Normalisasi (5 poin)

Buktikan desain sudah memenuhi 3NF:
- Pilih 2 tabel sebagai contoh
- Jelaskan singkat mengapa sudah 1NF, 2NF, 3NF

---

## Bagian 3: Implementasi PostgreSQL (35 poin)

### 3.1 DDL - Create Tables (12 poin)

Buat script SQL untuk:
- CREATE DATABASE
- CREATE TABLE dengan constraint (PK, FK, CHECK, UNIQUE)
- CREATE INDEX untuk kolom yang sering di-query

**Minimum:**
- 6 tabel saling berelasi
- Minimal 3 index strategis
- Minimal 2 constraint CHECK

---

### 3.2 DML - Sample Data (8 poin)

Insert data realistis:
- Minimal 20 rows data di tabel utama
- Data harus berelasi dengan benar
- Variasi status/kategori

---

### 3.3 Query OLTP (8 poin)

Buat 3 query untuk transaksi harian:
1. INSERT/UPDATE untuk transaksi utama
2. SELECT dengan JOIN untuk cek data
3. SELECT dengan WHERE kompleks untuk filter

---

### 3.4 Query OLAP (7 poin)

Buat 2 query untuk analytics:
1. Query dengan agregasi (SUM, COUNT, AVG) + GROUP BY
2. Query kompleks dengan subquery atau CTE

---

## Bagian 4: Testing dan Optimasi (15 poin)

### 4.1 EXPLAIN ANALYZE (15 poin)

Pilih 1 query OLAP kompleks:
- Tampilkan EXPLAIN ANALYZE sebelum optimasi
- Buat index baru atau perbaiki query
- Tampilkan EXPLAIN ANALYZE setelah optimasi
- Hitung improvement (waktu/persentase)

---

## Format Pengumpulan

ZIP dengan struktur:

```
NIM_Nama_Tugas3/
├── 01_Dokumentasi.pdf
│   ├── Identifikasi Masalah
│   ├── ERD
│   ├── Trade-off Analysis
│   ├── Bukti Normalisasi
│   └── Hasil EXPLAIN ANALYZE
├── 02_DDL.sql
├── 03_DML.sql
├── 04_Query_OLTP.sql
└── 05_Query_OLAP.sql
```

---

## Rubrik Penilaian

| Komponen | Poin | Detail |
|----------|------|--------|
| Identifikasi Masalah | 15 | Problem statement, requirement, OLTP/OLAP |
| Desain Database | 30 | ERD (10), Trade-off (15), Normalisasi (5) |
| Implementasi PostgreSQL | 35 | DDL (12), DML (8), OLTP (8), OLAP (7) |
| Testing dan Optimasi | 15 | EXPLAIN ANALYZE dan improvement |
| Dokumentasi | 5 | Kelengkapan dan kerapihan dokumen |
| **Total** | **100** | |

---

## Tips Pengerjaan

### 1. Pilih Masalah yang Anda Pahami
- Jangan pilih yang terlalu kompleks
- Pilih yang Anda sering lihat/alami
- Observasi proses bisnis yang ada

### 2. Sketsa ERD Dulu
- Identifikasi entitas utama
- Tentukan relasi
- Pikirkan atribut penting

### 3. Dokumentasikan Keputusan
- Setiap pilihan desain harus ada alasan
- Trade-off apa yang Anda ambil?
- Mengapa pilihan itu lebih baik untuk kasus Anda?

### 4. Test Bertahap
```sql
-- Create 1 tabel, lalu test
-- Create tabel berelasi, test foreign key
-- Insert data, test constraint
-- Buat query, test hasil
```

### 5. Gunakan Transaksi
```sql
BEGIN;
-- Your queries
ROLLBACK; -- untuk test
-- atau COMMIT; -- jika benar
```

---

## Contoh Dokumentasi Trade-off

**Keputusan: Nomor Telepon Customer**

**Pilihan:** Tabel terpisah (customer_phones)

**Alasan:**
- Customer bisa punya > 1 nomor (HP, rumah, kantor)
- Fleksibel tambah tipe nomor baru
- Mudah cari customer by phone number

**Trade-off:**
- Perlu JOIN untuk ambil data lengkap
- Sedikit lebih kompleks
- Tapi: benefit fleksibilitas > cost JOIN

**Alternatif yang dipertimbangkan:**
- Kolom phone1, phone2, phone3 - ditolak karena tidak fleksibel
- JSONB array - ditolak karena sulit di-index

---

## FAQ

**Q: Boleh pakai sistem yang sudah ada?**  
A: Boleh, tapi harus ada modifikasi/improvement dari yang umum.

**Q: Berapa banyak tabel minimal?**  
A: Minimal 6 tabel. Tapi yang penting: sesuai kebutuhan, ternormalisasi.

**Q: Boleh kelompok?**  
A: Tidak, tugas individual.

**Q: Database harus baru atau boleh dari tugas sebelumnya?**  
A: Boleh improve dari tugas sebelumnya, tapi harus ada analisis trade-off yang mendalam.

**Q: Kalau query sudah cepat tanpa index tambahan?**  
A: Tetap tunjukkan EXPLAIN ANALYZE dan jelaskan mengapa sudah optimal.

---

## Kriteria Penilaian Detail

### A (85-100)
- Problem identification jelas dan menarik
- Desain optimal dengan trade-off analysis mendalam
- Implementasi sempurna dengan constraint lengkap
- Query efisien dan kompleks
- Ada optimasi terukur dengan improvement signifikan

### B (70-84)
- Problem jelas
- Desain baik dengan trade-off explanation
- Implementasi lengkap
- Query berfungsi dengan baik
- Ada analisis performa

### C (60-69)
- Problem cukup jelas
- Desain ternormalisasi
- Implementasi ada minor error
- Query basic berfungsi

### D (50-59)
- Problem kurang jelas
- Desain kurang tepat
- Implementasi banyak error

### E (<50)
- Problem tidak jelas
- Desain salah
- Implementasi tidak jalan

---

## Deadline dan Keterlambatan

**Deadline:** 16 Mei 2026, pukul 23:59  
**Pengumpulan:** LMS (Learning Management System)  
**Penalty:** -10% per hari keterlambatan  
**Plagiarism:** Nilai 0 untuk semua pihak

---

## Penutup

Tugas ini menguji kemampuan Anda dalam:
- Identifikasi masalah real-world
- Desain database dengan pertimbangan trade-off
- Implementasi praktis PostgreSQL
- Optimasi berbasis evidence (EXPLAIN ANALYZE)

Ingat: Desain database yang baik lahir dari pemahaman mendalam terhadap masalah bisnis dan trade-off yang diambil dengan sadar. Keputusan desain yang Anda buat hari ini akan mempengaruhi performa sistem untuk jangka panjang.

Selamat mengerjakan.
