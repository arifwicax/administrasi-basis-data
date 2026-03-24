#  Materi Perkuliahan: **Backup dan Recovery Database**

## **Capaian Pembelajaran**

Setelah mengikuti perkuliahan ini, mahasiswa mampu:

1. Menjelaskan konsep dasar backup dan recovery.
2. Menentukan strategi backup yang sesuai dengan kebutuhan organisasi.
3. Melakukan simulasi backup dan recovery pada sistem DBMS (misalnya PostgreSQL/MySQL).
4. Memahami perbedaan antara backup fisik dan logis.
5. Mengimplementasikan restore data dari hasil backup.

---

## **1. Pengantar Backup dan Recovery**

###  Apa itu Backup?

Backup adalah proses **menyalin data dari database utama ke media cadangan** untuk mencegah kehilangan data akibat:

* Kegagalan perangkat keras,
* Kesalahan manusia,
* Serangan siber,
* Bencana alam, dsb.

### Apa itu Recovery?

Recovery adalah proses **mengembalikan database** ke kondisi semula (normal) setelah terjadi kegagalan atau kehilangan data.

---

## **2. Jenis-Jenis Backup**

| Jenis Backup            | Penjelasan                                                     | Kelebihan                         | Kekurangan                         |
| ----------------------- | -------------------------------------------------------------- | --------------------------------- | ---------------------------------- |
| **Full Backup**         | Menyalin seluruh isi database.                                 | Sederhana, lengkap.               | Ukuran besar, waktu lama.          |
| **Incremental Backup**  | Menyimpan hanya perubahan sejak backup terakhir.               | Cepat, hemat ruang.               | Proses recovery lebih kompleks.    |
| **Differential Backup** | Menyimpan perubahan sejak backup penuh terakhir.               | Lebih cepat dari full.            | Ukuran bertambah seiring waktu.    |
| **Logical Backup**      | Menggunakan perintah SQL (misalnya `mysqldump`, `pg_dump`).    | Mudah dipindahkan ke server lain. | Tidak menyimpan konfigurasi fisik. |
| **Physical Backup**     | Menyalin file data dan log database langsung dari sistem file. | Cocok untuk recovery cepat.       | Tidak portabel antar platform.     |

---

## **3. Strategi Backup**

Beberapa strategi umum:

* **Cold Backup (Offline Backup):**

  * Dilakukan ketika database dimatikan.
  * Aman dari perubahan data, tetapi mengganggu layanan.

* **Hot Backup (Online Backup):**

  * Dilakukan saat database masih berjalan.
  * Cocok untuk sistem 24 jam, tapi butuh konfigurasi tambahan (misalnya WAL di PostgreSQL).

* **Scheduled Backup:**

  * Backup otomatis sesuai jadwal (cron job, task scheduler, dsb).

---

## **4. Recovery: Jenis dan Teknik**

| Jenis Recovery                    | Deskripsi                                                   | Contoh                            |
| --------------------------------- | ----------------------------------------------------------- | --------------------------------- |
| **Complete Recovery**             | Mengembalikan database ke keadaan sebelum crash.            | Restore full backup + log.        |
| **Point-in-Time Recovery (PITR)** | Mengembalikan database ke waktu tertentu sebelum kegagalan. | PostgreSQL WAL, Oracle Flashback. |
| **Media Recovery**                | Mengganti file data yang rusak dengan backup terbaru.       | Restore file *.dbf* atau *.mdf*.  |
| **Crash Recovery**                | Pemulihan otomatis setelah sistem restart.                  | Log-based recovery.               |

---

## **5. Implementasi Praktis (Contoh DBMS)**

### **MySQL / MariaDB**

```bash
# Backup database
mysqldump -u root -p nama_database > backup.sql

# Restore database
mysql -u root -p nama_database < backup.sql
```

### **PostgreSQL**

```bash
# Backup (logical)
pg_dump -U postgres -F c -b -v -f backup.dump nama_database

# Restore
pg_restore -U postgres -d nama_database -v backup.dump
```

---

## **6. Best Practices**

1. Gunakan **penamaan backup yang konsisten** (misal: `db_backup_YYYYMMDD.sql`).
2. Simpan backup di **lokasi berbeda** (server lain atau cloud).
3. Lakukan **pengujian recovery secara berkala**.
4. Gunakan **enkripsi** pada file backup.
5. Catat dan dokumentasikan **jadwal backup** dan **lokasi penyimpanan**.

---

## **7. Studi Kasus Diskusi Kelas**

> “Sebuah perusahaan e-commerce kehilangan data transaksi selama 12 jam terakhir karena crash pada server. Mereka memiliki backup full setiap minggu dan incremental setiap 6 jam.
> Bagaimana strategi recovery terbaik yang bisa digunakan?”

Mahasiswa bisa diajak menganalisis langkah-langkah pemulihan data dan menjelaskan konsekuensi tiap pilihan.

---

# 🎯 **1. Konsep Dasar Incremental Backup**

### 🔹 Pengertian

**Incremental Backup** adalah teknik backup yang **menyimpan hanya perubahan data (delta)** sejak backup terakhir, bukan seluruh database.
Artinya:

* Backup pertama = **Full Backup** (seluruh data disalin)
* Backup selanjutnya = hanya **data yang berubah** sejak backup sebelumnya

🧠 Analogi:

> Bayangkan kamu menyalin buku catatan 100 halaman.
>
> * Hari pertama kamu salin semua halaman (Full Backup).
> * Hari berikutnya kamu hanya salin halaman yang berubah (Incremental Backup).

---

# 🧩 **2. Tujuan dan Manfaat**

| Tujuan                                         | Penjelasan                                                                                           |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Efisiensi Waktu**                            | Backup jauh lebih cepat karena hanya data yang berubah yang disimpan.                                |
| **Hemat Ruang Penyimpanan**                    | Mengurangi ukuran file backup dibandingkan backup penuh setiap hari.                                 |
| **Memungkinkan Point-in-Time Recovery (PITR)** | Database dapat dikembalikan ke kondisi pada waktu tertentu, misalnya “kondisi jam 09:35 hari Senin”. |

---

# ⚙️ **3. Mekanisme Incremental Backup di PostgreSQL**

PostgreSQL **tidak memiliki incremental backup bawaan secara langsung**, tapi mendukungnya melalui **Write-Ahead Logging (WAL)**.

### 🔸 Apa itu WAL?

WAL (Write-Ahead Log) adalah file log transaksi di PostgreSQL yang **mencatat semua perubahan data** sebelum disimpan ke disk.

Setiap perubahan (INSERT, UPDATE, DELETE) direkam dalam file WAL di folder:

```
/var/lib/postgresql/<versi>/main/pg_wal/
```

Jadi:

> **Full Backup** + **WAL Logs** = kemampuan melakukan **Incremental Recovery**

---

# 🔁 **4. Alur Incremental Backup**

Berikut urutannya:

1. **Lakukan Full Backup** pertama dengan `pg_basebackup`:

   ```bash
   pg_basebackup -U postgres -D /backup/full -F tar -X fetch
   ```

2. **Aktifkan archiving WAL** di `postgresql.conf`:

   ```
   wal_level = replica
   archive_mode = on
   archive_command = 'cp %p /backup/wal_archive/%f'
   ```

   Ini berarti setiap kali PostgreSQL menghasilkan file WAL baru, file tersebut akan disalin ke `/backup/wal_archive`.

3. **Setiap transaksi baru (INSERT, UPDATE, DELETE)** akan menghasilkan file WAL yang otomatis tersimpan di `/backup/wal_archive/`.

4. **Recovery (pemulihan)** dilakukan dengan:

   * Mengembalikan *full backup* terakhir
   * Lalu menerapkan file-file WAL sampai waktu yang diinginkan (Point-In-Time)

---

# 🧩 **5. Contoh Struktur Folder Backup**

```
/backup/
├── full/
│   ├── base.tar
│   └── pg_wal.tar
└── wal_archive/
    ├── 000000010000000000000001
    ├── 000000010000000000000002
    ├── 000000010000000000000003
```

---

# 🧭 **6. Proses Recovery (Point-In-Time Recovery / PITR)**

Langkah-langkah:

1. **Matikan PostgreSQL**

   ```bash
   sudo systemctl stop postgresql
   ```

2. **Pulihkan Full Backup**

   ```bash
   rm -rf /var/lib/postgresql/16/main/*
   tar -xf /backup/full/base.tar -C /var/lib/postgresql/16/main/
   ```

3. **Salin file WAL yang dibutuhkan**

   ```bash
   cp /backup/wal_archive/* /var/lib/postgresql/16/main/pg_wal/
   ```

4. **Buat file recovery.conf atau recovery.signal (versi baru PostgreSQL)**

   ```bash
   echo "restore_command = 'cp /backup/wal_archive/%f %p'" >> /var/lib/postgresql/16/main/postgresql.conf
   echo "recovery_target_time = '2025-10-06 09:35:00'" >> /var/lib/postgresql/16/main/postgresql.conf
   touch /var/lib/postgresql/16/main/recovery.signal
   ```

5. **Nyalakan kembali PostgreSQL**

   ```bash
   sudo systemctl start postgresql
   ```

💡 PostgreSQL akan otomatis memutar log WAL satu per satu sampai waktu `recovery_target_time` tercapai.

---

# 📊 **7. Kelebihan & Kekurangan**

| Aspek             | Kelebihan                         | Kekurangan                                      |
| ----------------- | --------------------------------- | ----------------------------------------------- |
| **Waktu Backup**  | Cepat setelah full backup pertama | Membutuhkan setup archiving                     |
| **Ruang Disk**    | Lebih hemat                       | Folder WAL bisa membengkak jika tidak dikontrol |
| **Restorasi**     | Bisa recovery ke waktu tertentu   | Lebih kompleks dibanding full backup            |
| **Keamanan Data** | Minim kehilangan data             | Butuh manajemen log yang baik                   |

---

# 💡 **8. Tools Pendukung Incremental Backup**

Beberapa tools pihak ketiga yang mempermudah proses ini:

| Tool                                   | Keterangan                                                               |
| -------------------------------------- | ------------------------------------------------------------------------ |
| **pgBackRest**                         | Tool resmi komunitas PostgreSQL untuk incremental backup & recovery      |
| **Barman (Backup & Recovery Manager)** | Mendukung full + incremental backup dan otomatisasi                      |
| **Wal-G / Wal-E**                      | Backup ke cloud storage (S3, GCS) dengan sistem incremental berbasis WAL |

Contoh pgBackRest:

```bash
pgbackrest --stanza=main --type=incr backup
```

---

# 🔄 **9. Visualisasi Alur Incremental Backup**

```
Hari 1 → Full Backup
Hari 2 → WAL_01 (perubahan sejak Hari 1)
Hari 3 → WAL_02 (perubahan sejak Hari 2)
Hari 4 → WAL_03 (perubahan sejak Hari 3)
...
Recovery = Full Backup + WAL_01 + WAL_02 + WAL_03
```

---

# 🧠 **10. Kesimpulan**

| Konsep                 | Penjelasan                                                    |
| ---------------------- | ------------------------------------------------------------- |
| **Full Backup**        | Salinan lengkap database                                      |
| **Incremental Backup** | Hanya menyimpan perubahan sejak backup terakhir (via WAL)     |
| **WAL Archive**        | Menyimpan semua log perubahan                                 |
| **PITR**               | Dapat mengembalikan database ke waktu tertentu                |
| **Rekomendasi VPS**    | Kombinasikan full backup mingguan + incremental backup harian |

