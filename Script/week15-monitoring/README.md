# PostgreSQL Performance Monitor — Week 15

Dashboard monitoring performa PostgreSQL berbasis Streamlit untuk praktikum **Administrasi Basis Data Pertemuan 15**.

---

## Fitur Dashboard

| Tab | Konten |
|---|---|
| 📊 Ringkasan | Cache hit ratio, total commit/rollback, grafik per database |
| 🔗 Koneksi | Daftar sesi aktif, distribusi status, peringatan query lama |
| 🐢 Query Lambat | Top 15 query terlambat dari `pg_stat_statements` |
| 🗄️ Tabel & Storage | Ukuran tabel, dead tuples, perbandingan full scan vs index scan |
| 🔒 Lock & Deadlock | Proses yang menunggu lock, semua lock aktif |

---

## Prasyarat

- Python 3.9+
- PostgreSQL 13+ sudah berjalan di lokal
- `shared_preload_libraries = 'pg_stat_statements'` sudah ditambahkan di `postgresql.conf`

---

## Cara Menjalankan

### 1. Clone / masuk ke direktori ini

```bash
cd "Script/week15-monitoring"
```

### 2. Buat virtual environment (opsional tapi disarankan)

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependensi

```bash
pip install -r requirements.txt
```

### 4. Siapkan database

Sesuaikan konfigurasi koneksi di file `db.py`:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "db_monitoring_lab",
    "user":     "postgres",
    "password": "password_anda",
}
```

Jalankan script SQL untuk membuat tabel dan data dummy:

```bash
psql -U postgres -c "CREATE DATABASE db_monitoring_lab;"
psql -U postgres -d db_monitoring_lab -f setup.sql
```

### 5. Jalankan dashboard

```bash
streamlit run app.py
```

Buka browser ke **http://localhost:8501**

---

## Struktur File

```
week15-monitoring/
├── app.py            # Aplikasi dashboard utama
├── db.py             # Modul koneksi dan query database
├── setup.sql         # Script persiapan database dan data dummy
├── requirements.txt  # Dependensi Python
└── README.md         # Panduan ini
```

---

## Fitur Simulasi Beban

Di sidebar dashboard terdapat tombol simulasi beban:

| Tombol | Aksi |
|---|---|
| ▶ Beban Baca | Menjalankan query JOIN + GROUP BY besar |
| ▶ Beban Tulis | Memasukkan 1.000 baris baru ke tabel `transaksi` |
| 🔄 Reset Stats | Mereset `pg_stat_statements` dan `pg_stat_database` |

Gunakan tombol ini untuk mengamati perubahan metrik secara langsung di dashboard.

---

## Tugas Praktikum

1. Jalankan dashboard dan catat nilai awal setiap metrik.
2. Klik **Beban Baca** beberapa kali, amati perubahan cache hit ratio dan query lambat.
3. Klik **Beban Tulis** beberapa kali, amati pertumbuhan tabel dan dead tuples.
4. Tangkap screenshot sebelum dan sesudah beban, isi tabel perbandingan di laporan.
5. Interpretasikan perubahan yang paling signifikan.
