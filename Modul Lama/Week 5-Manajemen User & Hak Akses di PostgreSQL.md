# 📘 Materi: **Manajemen User & Hak Akses dalam Database**

## 🎯 **Capaian Pembelajaran**

Setelah mengikuti pertemuan ini, mahasiswa mampu:

1. Membuat dan mengelola akun pengguna di PostgreSQL.
2. Menjelaskan pentingnya manajemen user dan hak akses pada DBMS.
3. Membuat dan mengelola akun pengguna.
4. Memberikan privilege sesuai kebutuhan (SELECT, INSERT, UPDATE, DELETE, EXECUTE).
5. Menggunakan **roles** untuk mengelompokkan hak akses.
6. Menerapkan prinsip **least privilege** agar keamanan database tetap terjaga.

---

## 🧩 **Pendahuluan**

* Database sering digunakan oleh banyak pihak: admin, dosen, mahasiswa, staf, dll.
* Tidak semua user boleh melakukan hal yang sama → **perlu pembatasan hak akses**.
* Tujuan manajemen user & hak akses:

  * **Keamanan data** (data tidak sembarangan diubah/dihapus).
  * **Kontrol akses** (siapa boleh melakukan apa).
  * **Audit & akuntabilitas** (setiap user bertanggung jawab atas tindakannya).

---


## 🧩 1. Persiapan

* DBMS: **PostgreSQL** (≥ v13).
* Database: `db_kuliah`.
* Tools: **psql** atau **pgAdmin**.

Buat database:

```sql
CREATE DATABASE db_kuliah;
\c db_kuliah;
```

---

## 🧩 2. Skema Database

Kita gunakan skema sederhana sistem perkuliahan:

```
mahasiswa(nim, nama, jurusan, angkatan)
dosen(nidn, nama, prodi)
matakuliah(kode_mk, nama_mk, sks)
perkuliahan(id, nim, kode_mk, nidn, nilai)
```

### SQL: Buat Tabel

```sql
-- Tabel Mahasiswa
CREATE TABLE mahasiswa (
    nim VARCHAR(10) PRIMARY KEY,        -- Nomor Induk Mahasiswa
    nama VARCHAR(100) NOT NULL,         -- Nama lengkap
    jurusan VARCHAR(50) NOT NULL,       -- Program studi/jurusan
    angkatan INT NOT NULL,              -- Tahun angkatan
    tanggal_lahir DATE,                 -- Tanggal lahir mahasiswa
    email VARCHAR(100) UNIQUE,          -- Email mahasiswa, harus unik
    no_hp VARCHAR(15),                  -- Nomor handphone
    alamat TEXT,                        -- Alamat lengkap
    ipk NUMERIC(3,2) DEFAULT 0.00,      -- Indeks Prestasi Kumulatif
    status VARCHAR(20) DEFAULT 'Aktif', -- Status: Aktif, Cuti, Lulus, D.O
    created_at TIMESTAMP DEFAULT NOW(), -- Tanggal data dibuat
    updated_at TIMESTAMP DEFAULT NOW()  -- Tanggal terakhir diperbarui
);

-- Tabel Dosen
CREATE TABLE dosen (
    nidn VARCHAR(10) PRIMARY KEY,           -- Nomor Induk Dosen Nasional
    nama VARCHAR(100) NOT NULL,             -- Nama lengkap dosen
    prodi VARCHAR(50) NOT NULL,             -- Program studi dosen
    email VARCHAR(100) UNIQUE,              -- Email dosen
    no_hp VARCHAR(15),                      -- Nomor handphone
    jabatan VARCHAR(50),                    -- Jabatan akademik (Asisten Ahli, Lektor, dsb.)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabel Matakuliah
CREATE TABLE matakuliah (
    kode_mk VARCHAR(10) PRIMARY KEY,        -- Kode unik mata kuliah
    nama_mk VARCHAR(100) NOT NULL,          -- Nama mata kuliah
    sks INT NOT NULL CHECK (sks > 0),       -- Jumlah SKS
    semester INT CHECK (semester BETWEEN 1 AND 14), -- Semester ditawarkan
    prodi VARCHAR(50) NOT NULL,             -- Program studi pemilik mata kuliah
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);


-- Tabel Perkuliahan (menghubungkan mahasiswa, dosen, dan matakuliah)
CREATE TABLE perkuliahan (
    id SERIAL PRIMARY KEY,                  -- ID unik perkuliahan
    nim VARCHAR(10) REFERENCES mahasiswa(nim) ON DELETE CASCADE,
    kode_mk VARCHAR(10) REFERENCES matakuliah(kode_mk) ON DELETE CASCADE,
    nidn VARCHAR(10) REFERENCES dosen(nidn) ON DELETE SET NULL,
    tahun_akademik VARCHAR(9) NOT NULL,     -- Format: 2024/2025
    semester VARCHAR(6) CHECK (semester IN ('Ganjil','Genap')),
    nilai CHAR(2) CHECK (nilai IN ('A','B','C','D','E','T')), -- Nilai huruf
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```
---

## 🧩 3. Membuat User

Kita buat 3 jenis user sesuai kebutuhan:

```sql
-- User mahasiswa
CREATE USER mahasiswa WITH PASSWORD 'mhs123';

-- User dosen
CREATE USER dosen WITH PASSWORD 'dsn123';

-- User admin akademik
CREATE USER adminakademik WITH PASSWORD 'adm123';
```

---

## 🧩 4. Memberikan Privilege

### 4.1 User Mahasiswa (❌ Tidak boleh ubah data, hanya lihat nilai & matakuliah)

```sql
-- Memberikan izin kepada role mahasiswa untuk terhubung (connect) ke database db_kuliah
GRANT CONNECT ON DATABASE db_kuliah TO mahasiswa;
-- Memberikan izin kepada mahasiswa untuk mengakses objek (tabel, view, fungsi, dll.) yang berada di schema public.
GRANT USAGE ON SCHEMA public TO mahasiswa;
GRANT SELECT (nim, nama, jurusan, angkatan) ON mahasiswa TO mahasiswa;
GRANT SELECT (kode_mk, nama_mk, sks) ON matakuliah TO mahasiswa;
GRANT SELECT (nim, kode_mk, nilai) ON perkuliahan TO mahasiswa;
```

### 4.2 User Dosen (✅ Boleh input & update nilai, lihat data mahasiswa)

```sql
GRANT CONNECT ON DATABASE db_kuliah TO dosen;
GRANT USAGE ON SCHEMA public TO dosen;
GRANT SELECT ON mahasiswa TO dosen;
GRANT SELECT ON matakuliah TO dosen;
GRANT SELECT, INSERT, UPDATE ON perkuliahan TO dosen;
```

### 4.3 User Admin Akademik (✅ Full access)

```sql
GRANT CONNECT ON DATABASE db_kuliah TO adminakademik;
GRANT USAGE ON SCHEMA public TO adminakademik;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO adminakademik;
```

---

## 🧩 5. Menggunakan Roles

Jika banyak user dengan peran sama, gunakan **roles**.

```sql
-- Role Mahasiswa
CREATE ROLE mahasiswa_role;
GRANT SELECT ON mahasiswa, matakuliah, perkuliahan TO mahasiswa_role;
GRANT mahasiswa_role TO mahasiswa;

-- Role Dosen
CREATE ROLE dosen_role;
GRANT SELECT ON mahasiswa, matakuliah TO dosen_role;
GRANT SELECT, INSERT, UPDATE ON perkuliahan TO dosen_role;
GRANT dosen_role TO dosen;

-- Role Admin Akademik
CREATE ROLE adminakademik_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO adminakademik_role;
GRANT adminakademik_role TO adminakademik;
```

---

## 🧩 6. Uji Coba Hak Akses

### 6.1 Login sebagai Mahasiswa

```bash
psql -U mahasiswa -d db_kuliah
```

Uji:

```sql
SELECT * FROM perkuliahan; -- ✅ Bisa
INSERT INTO perkuliahan(nim, kode_mk, nidn, nilai) VALUES ('2023001','MK001','D001',90); -- ❌ Ditolak
```

### 6.2 Login sebagai Dosen

```bash
psql -U dosen -d db_kuliah
```

Uji:

```sql
SELECT * FROM mahasiswa; -- ✅ Bisa
INSERT INTO perkuliahan(nim, kode_mk, nidn, nilai) VALUES ('2023001','MK001','D001',90); -- ✅ Bisa
DELETE FROM perkuliahan WHERE id=1; -- ❌ Ditolak
```

### 6.3 Login sebagai Admin Akademik

```bash
psql -U adminakademik -d db_kuliah
```

Uji:

```sql
INSERT INTO mahasiswa VALUES ('2023001','Budi','Informatika',2023); -- ✅ Bisa
DELETE FROM mahasiswa WHERE nim='2023001'; -- ✅ Bisa
```

---

## 🧩 7. Prinsip Least Privilege

* Mahasiswa → **hanya SELECT**.
* Dosen → **SELECT, INSERT, UPDATE** pada nilai.
* Admin Akademik → **full access**.
  ➡️ **Tidak ada user yang punya lebih banyak hak dari yang dibutuhkan**.

---

## 📌 Latihan Mandiri

1. Buat user baru: **operator** dengan hak akses **SELECT & INSERT** pada `mahasiswa`.
2. Buat role baru: **keuangan_role** dengan akses hanya ke tabel `mahasiswa` (untuk melihat angkatan).
3. Uji coba login sebagai operator, lalu coba `INSERT` dan `DELETE`.

---

## 🧩 8. Kesimpulan

* Manajemen user & hak akses penting untuk **keamanan database**.
* PostgreSQL mendukung **GRANT, REVOKE, ROLE** untuk kontrol akses.
* Prinsip **least privilege** memastikan keamanan & stabilitas sistem.

---


# PERINTAH TERMINAL


## 🔑 **1. Login ke PostgreSQL via Terminal (`psql`)**

### ✅ Perintah Umum
```bash
psql -U <user> -d <database> -h <host> -p <port>
```

| Opsi | Keterangan |
|------|-----------|
| `-U` | Username (role) PostgreSQL |
| `-d` | Nama database tujuan |
| `-h` | Host server (`localhost` untuk lokal) |
| `-p` | Port (default: `5432`) |

### 🟢 Contoh Praktis
```bash
# Login sebagai mahasiswa ke database db_kuliah
psql -U mahasiswa -d db_kuliah -h localhost
```
> Anda akan diminta password (`mhs123`).

### 💡 Tambahan Penting:
- **Tanpa `-h`**: Di Linux/macOS, koneksi via Unix socket (sering pakai autentikasi `peer`, **tidak minta password**).  
  → Untuk user buatan seperti `mahasiswa`, **selalu gunakan `-h localhost`** agar autentikasi password berjalan.
- **Langsung jalankan query**:
  ```bash
  psql -U mahasiswa -d db_kuliah -h localhost -c "SELECT current_user;"
  ```
- **Jalankan skrip SQL dari file**:
  ```bash
  psql -U mahasiswa -d db_kuliah -h localhost -f cek_hak.sql
  ```

---

## 👤 **2. Identifikasi User dan Sesi yang Sedang Aktif**

Jalankan di dalam `psql`:
```sql
-- Role aktif
SELECT current_user;

-- Database aktif
SELECT current_database();

-- Informasi koneksi lengkap
SELECT inet_client_addr() AS client_ip, 
       inet_server_addr() AS server_ip,
       pg_backend_pid() AS session_id;
```

---

## 🔍 **3. Periksa Hak Akses User Saat Ini**

### ✅ a. Hak Akses ke Database
```sql
-- Cek hak CONNECT ke database saat ini
SELECT has_database_privilege(current_database(), 'CONNECT') AS can_connect;

-- Cek hak CREATE (membuat objek di database)
SELECT has_database_privilege(current_database(), 'CREATE') AS can_create;
```

> 💡 Catatan: Perintah `\l` **sering tidak berfungsi** untuk user terbatas karena butuh akses ke katalog sistem. Gunakan query di atas sebagai gantinya.

---

### ✅ b. Hak Akses ke Schema `public`
```sql
-- Cek USAGE (akses objek di schema)
SELECT has_schema_privilege('public', 'USAGE') AS can_use_schema;

-- Cek CREATE (membuat objek di schema)
SELECT has_schema_privilege('public', 'CREATE') AS can_create_in_schema;
```

---

### ✅ c. Hak Akses ke Tabel
#### i. Lihat semua tabel yang bisa diakses:
```sql
\dp
```
> Simbol hak akses:  
> - `r` = SELECT  
> - `a` = INSERT  
> - `w` = UPDATE  
> - `d` = DELETE  
> - `D` = DROP  
> - `x` = REFERENCES  

#### ii. Cek hak spesifik ke satu tabel:
```sql
SELECT has_table_privilege('mahasiswa', 'SELECT') AS can_select;
```

#### iii. Daftar hak akses per tabel (format rapi):
```sql
SELECT 
    table_name,
    string_agg(privilege_type, ', ') AS privileges
FROM information_schema.role_table_grants
WHERE grantee = current_user
GROUP BY table_name;
```

---

### ✅ d. Hak Akses ke Kolom (Column-Level Privileges)
```sql
SELECT 
    table_name,
    column_name,
    privilege_type
FROM information_schema.column_privileges
WHERE grantee = current_user
ORDER BY table_name, column_name;
```

---

### ✅ e. Hak Akses ke Sequence (penting untuk `SERIAL`)
```sql
SELECT 
    sequence_name,
    has_sequence_privilege(sequence_name, 'USAGE') AS can_use
FROM information_schema.sequences
WHERE sequence_schema = 'public';
```

> 🔒 Jika Anda ingin user bisa `INSERT` ke tabel dengan `id SERIAL`, **wajib berikan**:
> ```sql
> GRANT USAGE ON SEQUENCE nama_tabel_id_seq TO mahasiswa;
> ```

---

## 🛠️ **4. Perintah Debugging & Informasi Tambahan**

### ✅ a. Cek apakah koneksi aktif
```sql
-- Ping sederhana
SELECT 1 AS connected;
```

### ✅ b. Lihat versi PostgreSQL
```sql
SELECT version();
```

### ✅ c. Cek apakah Row-Level Security (RLS) aktif di suatu tabel
```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' AND tablename = 'perkuliahan';
```

### ✅ d. Lihat semua role yang tersedia (hanya nama, tanpa detail)
```sql
SELECT rolname FROM pg_roles;
```
> ⚠️ User biasa **tidak bisa lihat atribut role** (gunakan `\du` sebagai superuser).

---

## 🧪 **5. Contoh Alur Lengkap di Terminal**

```bash
# 1. Login
psql -U mahasiswa -d db_kuliah -h localhost

# 2. Di dalam psql:
db_kuliah=> SELECT current_user, current_database();
db_kuliah=> \dp
db_kuliah=> SELECT has_table_privilege('perkuliahan', 'SELECT');
db_kuliah=> SELECT column_name FROM information_schema.column_privileges 
           WHERE table_name = 'mahasiswa' AND grantee = current_user;
db_kuliah=> \q
```

---

## 📌 **6. Catatan Penting & Best Practice**

| Topik | Penjelasan |
|------|-----------|
| **`\l` tidak muncul?** | Normal untuk user terbatas. Gunakan `SELECT current_database();` sebagai gantinya. |
| **Meta-command vs SQL** | Perintah seperti `\dp`, `\du`, `\dn+` adalah fitur `psql`, bukan SQL. Tidak bisa dipakai di aplikasi. |
| **Hanya lihat hak diri sendiri** | User biasa tidak bisa melihat hak user lain. Untuk audit penuh, login sebagai `postgres`. |
| **Password di CLI?** | Hindari `-W` atau password di command line (tercatat di history). Gunakan `.pgpass` untuk otomatisasi aman. |
| **File `.pgpass` (opsional)** | Simpan kredensial di `~/.pgpass` (Linux/macOS) atau `%APPDATA%\postgresql\pgpass.conf` (Windows) dengan format:  
`hostname:port:database:username:password`  
Lalu set permission: `chmod 600 ~/.pgpass` |

---

## ✅ **Kapan Harus Login sebagai Superuser?**
Gunakan akun `postgres` jika Anda perlu:
- Melihat semua database (`\l`)
- Melihat semua role (`\du`)
- Memberikan/mencabut hak akses (`GRANT`/`REVOKE`)
- Melihat hak akses semua user
- Membuat/menghapus database atau role

Contoh:
```bash
psql -U postgres -d postgres
```
