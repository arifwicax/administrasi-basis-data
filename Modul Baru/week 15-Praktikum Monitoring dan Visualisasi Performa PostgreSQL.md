# Modul Praktikum Pertemuan 15

## Administrasi Basis Data

### Monitoring dan Visualisasi Performa PostgreSQL

---

## A. Identitas Praktikum

| | |
|---|---|
| **Nama Modul** | Monitoring dan Visualisasi Performa PostgreSQL |
| **Pertemuan** | 15 |
| **DBMS** | PostgreSQL |
| **Durasi** | 120 menit |
| **Fokus** | Membangun dashboard monitoring PostgreSQL menggunakan tools visualisasi pilihan mahasiswa |

---

## B. Tujuan Praktikum

Setelah menyelesaikan praktikum ini, mahasiswa mampu:

1. Mengambil metrik performa dari view statistik bawaan PostgreSQL.
2. Memilih dan menggunakan tools visualisasi yang sesuai dengan kemampuan dan lingkungan masing-masing.
3. Membangun dashboard yang menampilkan kondisi performa PostgreSQL secara visual.
4. Menginterpretasikan perubahan metrik saat beban query diberikan ke database.

---

## C. Prasyarat

Pastikan hal berikut sudah tersedia sebelum memulai:

- PostgreSQL sudah terinstal dan berjalan (versi 13 ke atas).
- Mahasiswa memiliki akses ke database PostgreSQL (lokal atau cloud).
- Python 3.9+ terinstal (jika memilih Jalur A — Streamlit).
- Pilih salah satu jalur tools visualisasi pada bagian D.

---

## D. Pilihan Jalur Tools

Mahasiswa bebas memilih salah satu jalur. Setiap jalur menghasilkan luaran yang setara: sebuah dashboard visualisasi performa PostgreSQL.

| Jalur | Tools | Cocok untuk |
|---|---|---|
| **A** | Streamlit (Python) | mahasiswa yang familiar dengan Python |
| **B** | Metabase | mahasiswa yang lebih suka antarmuka visual tanpa kode |
| **C** | Grafana + Prometheus | mahasiswa yang ingin setup stack monitoring produksi |
| **D** | pgAdmin 4 | mahasiswa yang tidak ingin instalasi tools tambahan |

---

## E. Persiapan Database

Kerjakan langkah-langkah ini terlebih dahulu. Berlaku untuk semua jalur.

### E.1 Aktifkan Ekstensi pg_stat_statements

Tambahkan baris berikut ke `postgresql.conf` lalu restart PostgreSQL:

```
shared_preload_libraries = 'pg_stat_statements'
```

Kemudian jalankan perintah SQL berikut:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

### E.2 Buat Database dan Tabel Latihan

```sql
CREATE DATABASE db_monitoring_lab;
```

Hubungkan ke database tersebut, lalu jalankan:

```sql
CREATE TABLE IF NOT EXISTS produk (
    id      SERIAL PRIMARY KEY,
    nama    VARCHAR(100) NOT NULL,
    stok    INTEGER      NOT NULL DEFAULT 0,
    harga   NUMERIC(12, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS transaksi (
    id          SERIAL PRIMARY KEY,
    pelanggan   VARCHAR(100),
    produk      VARCHAR(100),
    jumlah      INTEGER,
    total_harga NUMERIC(12, 2),
    created_at  TIMESTAMP DEFAULT NOW()
);
```

### E.3 Isi Data Dummy

```sql
-- 100 baris produk
INSERT INTO produk (nama, stok, harga)
SELECT
    'Produk-' || i,
    (random() * 100)::INT,
    (random() * 500000 + 10000)::NUMERIC(12, 2)
FROM generate_series(1, 100) AS i;

-- 50.000 baris transaksi
INSERT INTO transaksi (pelanggan, produk, jumlah, total_harga)
SELECT
    'Pelanggan-' || (random() * 1000)::INT,
    'Produk-'    || (random() * 100)::INT,
    (random() * 10 + 1)::INT,
    (random() * 5000000)::NUMERIC(12, 2)
FROM generate_series(1, 50000);

ANALYZE produk;
ANALYZE transaksi;
```

### E.4 Verifikasi

```sql
SELECT 'produk'    AS tabel, COUNT(*) FROM produk
UNION ALL
SELECT 'transaksi' AS tabel, COUNT(*) FROM transaksi;

SELECT * FROM pg_stat_database WHERE datname = 'db_monitoring_lab';
```

---

## F. Query Referensi Metrik

Query berikut digunakan di semua jalur untuk mengambil metrik dari PostgreSQL.

### F.1 Jumlah Koneksi Aktif

```sql
SELECT
    datname                                               AS database,
    count(*)                                              AS total_koneksi,
    count(*) FILTER (WHERE state = 'active')              AS koneksi_aktif,
    count(*) FILTER (WHERE state = 'idle')                AS koneksi_idle
FROM pg_stat_activity
WHERE datname IS NOT NULL
GROUP BY datname
ORDER BY total_koneksi DESC;
```

### F.2 Cache Hit Ratio

```sql
SELECT
    datname                                                     AS database,
    numbackends                                                 AS koneksi,
    xact_commit                                                 AS commit,
    xact_rollback                                               AS rollback,
    ROUND(
        blks_hit::NUMERIC / NULLIF(blks_hit + blks_read, 0) * 100, 2
    )                                                           AS cache_hit_ratio_persen
FROM pg_stat_database
WHERE datname NOT IN ('postgres', 'template0', 'template1')
ORDER BY xact_commit DESC;
```

### F.3 Query Lambat (Top 10)

```sql
SELECT
    LEFT(query, 80)                                AS query,
    calls                                          AS eksekusi,
    ROUND(mean_exec_time::NUMERIC, 2)              AS rata2_ms,
    ROUND(total_exec_time::NUMERIC, 2)             AS total_ms,
    rows
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### F.4 Ukuran dan Kondisi Tabel

```sql
SELECT
    relname                                              AS tabel,
    pg_size_pretty(pg_total_relation_size(relid))        AS ukuran_total,
    n_live_tup                                           AS baris_aktif,
    n_dead_tup                                           AS baris_mati,
    seq_scan                                             AS full_scan,
    idx_scan                                             AS index_scan,
    last_autovacuum
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

### F.5 Query yang Sedang Berjalan

```sql
SELECT
    pid,
    usename                                                           AS pengguna,
    state,
    ROUND(EXTRACT(EPOCH FROM (NOW() - query_start))::NUMERIC, 1)      AS durasi_detik,
    LEFT(query, 100)                                                   AS query
FROM pg_stat_activity
WHERE state != 'idle'
  AND query NOT LIKE '%pg_stat_activity%'
ORDER BY durasi_detik DESC;
```

### F.6 Lock Aktif

```sql
SELECT
    l.pid,
    a.usename     AS pengguna,
    l.mode,
    l.granted,
    LEFT(a.query, 80) AS query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE a.query NOT LIKE '%pg_locks%'
ORDER BY l.granted, l.pid;
```

---

## G. Jalur A — Streamlit

### G.1 Instalasi

```bash
pip install streamlit psycopg2-binary pandas plotly
```

### G.2 Struktur Proyek

File proyek Streamlit tersedia di:

```
Script/week15-monitoring/
├── app.py            ← dashboard utama (5 tab)
├── db.py             ← modul koneksi database
├── setup.sql         ← script persiapan database
├── requirements.txt  ← daftar dependensi
└── README.md         ← panduan menjalankan
```

### G.3 Konfigurasi Koneksi

Buka `db.py` dan sesuaikan nilai berikut:

```python
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "db_monitoring_lab",
    "user":     "postgres",
    "password": "password_anda",   # ← ganti di sini
}
```

### G.4 Menjalankan Dashboard

```bash
cd "Script/week15-monitoring"
streamlit run app.py
```

Buka browser ke `http://localhost:8501`.

### G.5 Fitur Dashboard

| Tab | Konten |
|---|---|
| 📊 Ringkasan | Cache hit ratio, commit, rollback, grafik per database |
| 🔗 Koneksi | Daftar sesi aktif, distribusi status, peringatan query lama |
| 🐢 Query Lambat | Top 15 query terlambat dari `pg_stat_statements` |
| 🗄️ Tabel & Storage | Ukuran tabel, dead tuples, full scan vs index scan |
| 🔒 Lock & Deadlock | Proses yang menunggu lock |

Di sidebar tersedia tombol **simulasi beban** untuk mengamati perubahan metrik secara langsung.

---

## H. Jalur B — Metabase

### H.1 Instalasi via Docker

```bash
docker run -d -p 3000:3000 --name metabase metabase/metabase
```

Atau tanpa Docker, unduh JAR dari [metabase.com](https://www.metabase.com/start/oss/) lalu:

```bash
java -jar metabase.jar
```

### H.2 Konfigurasi Koneksi

1. Buka `http://localhost:3000`.
2. Ikuti wizard setup awal.
3. Pada bagian **Add your data**, pilih **PostgreSQL**.
4. Isi detail koneksi database `db_monitoring_lab`.
5. Klik **Save**.

### H.3 Membuat Panel

1. Klik **+ New → Question → Native Query**.
2. Tempel salah satu query dari bagian F.
3. Klik **Visualize** dan pilih jenis tampilan.
4. Klik **Save**, beri nama panel.
5. Ulangi untuk setiap metrik, lalu gabungkan ke **Dashboard** baru.

### H.4 Panel Wajib

| No | Nama Panel | Query |
|---|---|---|
| 1 | Koneksi Aktif | F.1 |
| 2 | Cache Hit Ratio | F.2 |
| 3 | Query Lambat | F.3 |
| 4 | Ukuran Tabel | F.4 |
| 5 | Query Berjalan | F.5 |

---

## I. Jalur C — Grafana + Prometheus

### I.1 File `docker-compose.yml`

```yaml
version: "3.8"
services:
  postgres_exporter:
    image: prometheuscommunity/postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://postgres:password_anda@host.docker.internal:5432/db_monitoring_lab?sslmode=disable"
    ports:
      - "9187:9187"

  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### I.2 File `prometheus.yml`

```yaml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: "postgres"
    static_configs:
      - targets: ["postgres_exporter:9187"]
```

### I.3 Menjalankan Stack

```bash
docker compose up -d
```

Buka `http://localhost:3000` (admin / admin), tambahkan data source Prometheus, lalu import dashboard ID **9628**.

---

## J. Jalur D — pgAdmin 4

### J.1 Akses

```bash
docker run -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@lab.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  -d dpage/pgadmin4
```

Buka `http://localhost:5050`.

### J.2 Membuat Panel Kustom

1. Hubungkan ke server PostgreSQL.
2. Buka **Tools → Query Tool**.
3. Tempel query dari bagian F dan klik **Execute**.
4. Gunakan grafik bawaan di tab **Dashboard** server untuk monitoring umum.
5. Simpan query yang sering digunakan via **File → Save As**.

---

## K. Simulasi Beban

Jalankan query berikut untuk menciptakan beban dan mengamati perubahan metrik.

### K.1 Beban Baca

```sql
SELECT p.nama, SUM(t.jumlah) AS total_terjual, SUM(t.total_harga) AS pendapatan
FROM transaksi t
JOIN produk p ON p.nama = t.produk
GROUP BY p.nama
ORDER BY pendapatan DESC;
```

### K.2 Beban Tulis

```sql
INSERT INTO transaksi (pelanggan, produk, jumlah, total_harga)
SELECT
    'Pelanggan-' || (random() * 1000)::INT,
    'Produk-'    || (random() * 100)::INT,
    (random() * 10 + 1)::INT,
    (random() * 5000000)::NUMERIC(12, 2)
FROM generate_series(1, 10000);
```

### K.3 Query Lambat Tanpa Indeks

```sql
EXPLAIN ANALYZE
SELECT *
FROM transaksi
WHERE pelanggan = 'Pelanggan-500'
  AND total_harga > 1000000
ORDER BY created_at DESC;
```

### K.4 Tambah Indeks dan Bandingkan

```sql
CREATE INDEX idx_transaksi_pelanggan ON transaksi(pelanggan);
CREATE INDEX idx_transaksi_harga     ON transaksi(total_harga);

EXPLAIN ANALYZE
SELECT *
FROM transaksi
WHERE pelanggan = 'Pelanggan-500'
  AND total_harga > 1000000
ORDER BY created_at DESC;
```

---

## L. Tugas dan Laporan

### L.1 Tugas Individu

Buat laporan yang memuat:

1. **Pilihan tools** dan alasan memilihnya.
2. **Screenshot dashboard** minimal menampilkan 4 panel metrik.
3. **Tabel perbandingan** metrik sebelum dan sesudah beban:

| Metrik | Sebelum Beban | Sesudah Beban | Analisis |
|---|---|---|---|
| Koneksi aktif | | | |
| Cache hit ratio (%) | | | |
| Rata-rata waktu query (ms) | | | |
| Jumlah baris tabel transaksi | | | |
| Dead tuples tabel transaksi | | | |

4. **Interpretasi:** Jelaskan perubahan yang paling signifikan dan penyebabnya.
5. **Refleksi:** Kelebihan dan keterbatasan tools yang dipilih.

### L.2 Kriteria Penilaian

| Kriteria | Bobot |
|---|---|
| Dashboard berjalan dan menampilkan metrik nyata | 30% |
| Kelengkapan panel (minimal 4 metrik) | 20% |
| Tabel perbandingan sebelum/sesudah beban | 20% |
| Ketepatan interpretasi perubahan metrik | 20% |
| Refleksi pemilihan tools | 10% |

---

## M. Pertanyaan Refleksi

1. Metrik mana yang paling berubah saat beban diberikan? Mengapa?
2. Apakah cache hit ratio turun setelah data baru dimasukkan? Jelaskan penyebabnya.
3. Apakah penambahan indeks berdampak pada metrik di dashboard?
4. Jika Anda adalah DBA di lingkungan produksi, tools mana yang akan Anda pilih? Mengapa?

---

## N. Alur Praktikum

```mermaid
flowchart TD
    A[Persiapan Database\nsetup.sql] --> B[Pilih Jalur Tools]
    B --> C1[Jalur A\nStreamlit]
    B --> C2[Jalur B\nMetabase]
    B --> C3[Jalur C\nGrafana]
    B --> C4[Jalur D\npgAdmin]
    C1 & C2 & C3 & C4 --> D[Bangun Dashboard\nMinimal 4 Panel]
    D --> E[Catat Metrik Awal]
    E --> F[Jalankan Simulasi Beban]
    F --> G[Catat Metrik Sesudah Beban]
    G --> H[Interpretasi dan Laporan]
```

---

## O. Referensi

- [pg_stat_database — Dokumentasi PostgreSQL](https://www.postgresql.org/docs/current/monitoring-stats.html)
- [pg_stat_statements — Dokumentasi PostgreSQL](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [Streamlit Documentation](https://docs.streamlit.io)
- [Metabase Documentation](https://www.metabase.com/docs)
- [Grafana Documentation](https://grafana.com/docs)
- [pgAdmin Documentation](https://www.pgadmin.org/docs)
- Proyek Streamlit praktikum ini: `Script/week15-monitoring/`
