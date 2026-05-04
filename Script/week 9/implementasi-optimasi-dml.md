# 🚀 Praktikum Week 9: Optimasi Operasi INSERT, UPDATE, DELETE
*"Dari Database Lemot jadi Database Ngebut!"*

---

## 🎯 **Tujuan Praktikum**

Setelah praktikum ini, mahasiswa dapat:
1. **Merasakan langsung** perbedaan performa DML dengan dan tanpa optimasi
2. **Memahami** mengapa INSERT/UPDATE/DELETE bisa lambat (biaya tersembunyi)
3. **Menguasai** teknik optimasi DML yang dipakai developer profesional
4. **Menggunakan** tools monitoring untuk jadi "detektif database"

---

## 🤔 **Kenapa Belajar Optimasi DML Penting?**

### Analogi Sederhana: Restoran Saat Ramadhan
Bayangkan restoran dengan 2 situasi:

**🐌 Situasi LAMBAT (Tanpa Optimasi):**
```
- Pelayan catat pesanan 1-1 di kertas (INSERT lambat)
- Ganti menu harus tulis ulang semua daftar (UPDATE berat)
- Hapus pesanan harus robek kertas, tulis ulang (DELETE ribet)
- Customer antri panjang, bos stress! 😫
```

**⚡ Situasi CEPAT (Dengan Optimasi):**
```
- Pakai sistem POS digital (INDEX membantu)
- Update menu langsung ke semua cabang (batch processing)
- Hapus pesanan tinggal klik (efficient DELETE)
- Customer happy, bos happy! 😎
```

### Dampak di Dunia Nyata:
- **E-commerce Flash Sale**: 10,000 transaksi/detik
- **Sosmed Viral**: Jutaan like/comment/share
- **Gaming Online**: Update skor real-time
- **Banking**: Transfer uang harus akurat & cepat

**Tanpa optimasi = Server hang, user kabur, bisnis rugi! 💸**

---

## 🛠️ **Persiapan Laboratorium**

### 1. Setup Database Khusus
```sql
-- 🏗️ Bikin "lab" khusus untuk experimen
CREATE DATABASE praktikum_dml_optimasi;
\c praktikum_dml_optimasi;

-- ⏱️ Aktifkan stopwatch untuk ngukur kecepatan
\timing on;

-- 📊 Tampilkan memory usage
SHOW shared_buffers;
SHOW work_mem;

-- 🎉 Database siap!
SELECT 'Lab DML Optimasi siap digunakan! 🚀' AS status;
```

### 2. Aktifkan "Mata-mata" Database
```sql
-- 🕵️ Extension untuk monitoring performa
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgstattuple;

-- 📈 Reset statistik untuk fresh start
SELECT pg_stat_statements_reset();
SELECT pg_stat_reset();

-- ✅ Cek extension aktif
\dx
```

---

## 🛒 **Bagian 1: "Drama Flash Sale" - Biaya Tersembunyi INSERT**

### 📚 **Cerita: Shopee vs Tokopedia Flash Sale**

> **Situasi:** 12.12 Flash Sale! iPhone 15 Pro harga Rp 5 juta, stok 1000 unit. Dalam 10 menit, 100,000 orang coba checkout bersamaan. Database kedua platform ngelag berat!

**❓ Pertanyaan Kritis:**
- Kenapa INSERT produk bisa lambat?
- Apa yang terjadi "di balik layar" saat INSERT?
- Bagaimana cara mengoptimalkannya?

**🔬 Mari investigasi dengan experimen!**

### Experimen: Tabel "Ringan" vs Tabel "Berat"

#### 🏃‍♂️ **Setup A: Tabel "Ringan" (Minimal Index)**
```sql
-- Tabel produk "ringan" - hanya primary key
-- Analogi: Gudang tanpa sistem katalog
CREATE TABLE produk_ringan (
    id SERIAL PRIMARY KEY,           -- Index #1 (wajib)
    nama_produk VARCHAR(100),        -- Tanpa index
    kategori VARCHAR(50),            -- Tanpa index
    harga DECIMAL(10,2),             -- Tanpa index
    stok INTEGER,                    -- Tanpa index
    supplier_id INTEGER,             -- Tanpa index
    deskripsi TEXT,                  -- Tanpa index
    created_at TIMESTAMP DEFAULT NOW()
);

-- 📊 Cek ukuran awal
SELECT 
    pg_size_pretty(pg_total_relation_size('produk_ringan')) AS ukuran_total,
    pg_size_pretty(pg_relation_size('produk_ringan')) AS ukuran_data,
    pg_size_pretty(pg_indexes_size('produk_ringan')) AS ukuran_index;
```

#### 🐌 **Setup B: Tabel "Berat" (Over-Indexed)**
```sql
-- Tabel produk "berat" - index di mana-mana
-- Analogi: Gudang dengan 7 sistem katalog berbeda (ribet!)
CREATE TABLE produk_berat (
    id SERIAL PRIMARY KEY,           -- Index #1
    nama_produk VARCHAR(100),        -- Akan ada index #2
    kategori VARCHAR(50),            -- Akan ada index #3  
    harga DECIMAL(10,2),             -- Akan ada index #4
    stok INTEGER,                    -- Akan ada index #5
    supplier_id INTEGER,             -- Akan ada index #6
    deskripsi TEXT,                  -- Akan ada index #7
    created_at TIMESTAMP DEFAULT NOW() -- Akan ada index #8
);

-- 📚 Bikin 7 index tambahan (total 8 index!)
CREATE INDEX idx_produk_nama ON produk_berat(nama_produk);
CREATE INDEX idx_produk_kategori ON produk_berat(kategori);
CREATE INDEX idx_produk_harga ON produk_berat(harga);
CREATE INDEX idx_produk_stok ON produk_berat(stok);
CREATE INDEX idx_produk_supplier ON produk_berat(supplier_id);
CREATE INDEX idx_produk_deskripsi ON produk_berat USING gin(to_tsvector('english', deskripsi));
CREATE INDEX idx_produk_created ON produk_berat(created_at);

-- 🔍 Lihat daftar index
\d+ produk_berat
```

### 🏁 **Tes Kecepatan: Siapa yang Menang?**

#### **Round 1: INSERT ke Tabel "Ringan" 🏃‍♂️**
```sql
-- ⏱️ Test A: INSERT 20,000 produk ke tabel ringan
DO $$
DECLARE
    i INTEGER;
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    categories TEXT[] := ARRAY['Elektronik', 'Fashion', 'Makanan', 'Buku', 'Olahraga'];
BEGIN
    start_time := clock_timestamp();
    RAISE NOTICE '🏃‍♂️ [TABEL RINGAN] Mulai INSERT 20,000 produk...';
    
    FOR i IN 1..20000 LOOP
        INSERT INTO produk_ringan (nama_produk, kategori, harga, stok, supplier_id, deskripsi) 
        VALUES (
            'Produk Flash Sale #' || i,
            categories[1 + (i % 5)],                    -- Random kategori
            (1000 + (RANDOM() * 9000))::DECIMAL(10,2), -- Harga 1K-10K
            (10 + (RANDOM() * 90))::INTEGER,            -- Stok 10-100
            1 + (RANDOM() * 50)::INTEGER,               -- Supplier 1-50
            'Deskripsi produk bagus untuk item #' || i
        );
    END LOOP;
    
    end_time := clock_timestamp();
    RAISE NOTICE '✅ [TABEL RINGAN] SELESAI! Durasi: %', end_time - start_time;
END $$;
```

#### **Round 2: INSERT ke Tabel "Berat" 🐌**
```sql
-- ⏱️ Test B: INSERT 20,000 produk ke tabel berat (sama persis)
DO $$
DECLARE
    i INTEGER;
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    categories TEXT[] := ARRAY['Elektronik', 'Fashion', 'Makanan', 'Buku', 'Olahraga'];
BEGIN
    start_time := clock_timestamp();
    RAISE NOTICE '🐌 [TABEL BERAT] Mulai INSERT 20,000 produk...';
    
    FOR i IN 1..20000 LOOP
        INSERT INTO produk_berat (nama_produk, kategori, harga, stok, supplier_id, deskripsi) 
        VALUES (
            'Produk Flash Sale #' || i,
            categories[1 + (i % 5)],                    -- Data sama persis
            (1000 + (RANDOM() * 9000))::DECIMAL(10,2),
            (10 + (RANDOM() * 90))::INTEGER,
            1 + (RANDOM() * 50)::INTEGER,
            'Deskripsi produk bagus untuk item #' || i
        );
    END LOOP;
    
    end_time := clock_timestamp();
    RAISE NOTICE '😰 [TABEL BERAT] SELESAI! Durasi: %', end_time - start_time;
END $$;
```

### 🕵️ **Analisis Hasil: Detective Mode ON!**

#### **Bandingkan Ukuran & Performa:**
```sql
-- 📊 Laporan lengkap perbandingan
SELECT 
    'TABEL RINGAN (1 index)' AS jenis_tabel,
    COUNT(*) AS jumlah_data,
    pg_size_pretty(pg_total_relation_size('produk_ringan')) AS ukuran_total,
    pg_size_pretty(pg_relation_size('produk_ringan')) AS ukuran_data,
    pg_size_pretty(pg_indexes_size('produk_ringan')) AS ukuran_index,
    (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'produk_ringan') AS jumlah_index
FROM produk_ringan

UNION ALL

SELECT 
    'TABEL BERAT (8 index)' AS jenis_tabel,
    COUNT(*) AS jumlah_data,
    pg_size_pretty(pg_total_relation_size('produk_berat')) AS ukuran_total,
    pg_size_pretty(pg_relation_size('produk_berat')) AS ukuran_data,
    pg_size_pretty(pg_indexes_size('produk_berat')) AS ukuran_index,
    (SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'produk_berat') AS jumlah_index
FROM produk_berat;
```

#### **Detail "Biaya" Setiap Index:**
```sql
-- 💰 Seberapa "mahal" masing-masing index?
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS ukuran_index
FROM pg_stat_user_indexes 
WHERE schemaname = 'public' 
  AND tablename IN ('produk_ringan', 'produk_berat')
ORDER BY tablename, pg_relation_size(indexrelid) DESC;
```

### 🎯 **Kesimpulan Mengejutkan:**

**🏆 Yang Akan Kalian Temukan:**
- ⚡ Tabel ringan: INSERT **3-5x lebih cepat**
- 💾 Tabel berat: Ukuran disk **2-3x lebih besar**  
- 🎭 **Trade-off**: SELECT cepat ↔ INSERT lambat

**📝 Golden Rule:**
> **"Index itu seperti daftar isi buku. Berguna untuk membaca, tapi bikin ribet kalau mau nambah halaman baru!"**

---

## 📦 **Bagian 2: "Masalah Kurir Overload" - Drama UPDATE**

### 📖 **Cerita: Sistem Logistik GoSend Chaos**

> **Situasi:** Senin pagi jam 8, 50,000 paket harus update status dari "pending" → "on_delivery". Database admin GoSend panik karena query UPDATE lambat banget! Customer komplain paket hilang padahal cuma database yang lemot.

### **Root Cause Analysis:**
- 🐌 **UPDATE tanpa WHERE yang tepat** = scan 1 juta baris
- ⚡ **UPDATE dengan index strategis** = langsung ke target

### **Mari simulasikan masalahnya!**

#### **Setup: Sistem Pengiriman E-commerce**
```sql
-- 📦 Tabel pesanan untuk simulasi GoSend/GrabExpress
CREATE TABLE pesanan_pengiriman (
    id SERIAL PRIMARY KEY,
    tracking_code VARCHAR(20) UNIQUE,
    customer_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending',      -- pending → processing → shipped → delivered
    alamat_tujuan TEXT,
    berat_gram INTEGER,
    ongkir DECIMAL(10,2),
    kurir_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 🎯 Generate 100K pesanan untuk test realistis
INSERT INTO pesanan_pengiriman (tracking_code, customer_id, status, alamat_tujuan, berat_gram, ongkir)
SELECT 
    'TRK' || LPAD(i::TEXT, 10, '0'),           -- TRK0000001, TRK0000002, dst
    1 + (RANDOM() * 10000)::INTEGER,           -- Customer ID random
    CASE 
        WHEN i <= 30000 THEN 'pending'
        WHEN i <= 60000 THEN 'processing' 
        WHEN i <= 80000 THEN 'shipped'
        ELSE 'delivered'
    END,
    'Alamat pengiriman untuk pesanan #' || i,
    (100 + RANDOM() * 2000)::INTEGER,          -- Berat 100-2100 gram
    (5000 + RANDOM() * 15000)::DECIMAL(10,2)   -- Ongkir 5K-20K
FROM generate_series(1, 100000) AS i;

-- 📊 Cek distribusi status
SELECT status, COUNT(*) AS jumlah, 
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS persen
FROM pesanan_pengiriman 
GROUP BY status;
```

### **Experimen: UPDATE Tanpa Index vs Dengan Index**

#### **🐌 Test A: UPDATE Tanpa Index (Disaster!)**
```sql
-- ❌ UPDATE tanpa index - LAMBAT BANGET!
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
UPDATE pesanan_pengiriman 
SET status = 'processing', 
    updated_at = NOW(),
    kurir_id = 1001
WHERE status = 'pending';
```

**💭 Prediksi:** Query ini bakal scan seluruh 100K baris untuk cari yang status = 'pending'

#### **⚡ Setup Index Strategis**
```sql
-- 🚀 Bikin index untuk kolom yang sering difilter
CREATE INDEX idx_pesanan_status ON pesanan_pengiriman(status);
CREATE INDEX idx_pesanan_customer ON pesanan_pengiriman(customer_id);
CREATE INDEX idx_pesanan_tracking ON pesanan_pengiriman(tracking_code);

-- 📈 Update statistik agar planner cerdas
ANALYZE pesanan_pengiriman;
```

#### **⚡ Test B: UPDATE Dengan Index (Lightning Fast!)**
```sql
-- ✅ UPDATE dengan index - CEPAT!
EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
UPDATE pesanan_pengiriman 
SET status = 'processing', 
    updated_at = NOW(),
    kurir_id = 1001
WHERE status = 'pending';
```

### **🔬 Analisis: Bedah Query Plan**

```sql
-- 🧪 Bandingkan sebelum dan sesudah index
-- Jalankan ini SEBELUM bikin index
\echo '=== BEFORE INDEX ==='
EXPLAIN (ANALYZE, BUFFERS) 
SELECT COUNT(*) FROM pesanan_pengiriman WHERE status = 'pending';

\echo '=== AFTER INDEX ==='  
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM pesanan_pengiriman WHERE status = 'pending';
```

---

## ⚰️ **Bagian 3: "Misteri Dead Tuple" - Kenapa Database Membengkak?**

### 📖 **Cerita: Aplikasi Chat Yang Membengkak**

> **Masalah:** Database WhatsApp Business API tumbuh dari 10GB jadi 100GB dalam seminggu! Padahal data cuma 50 juta chat. Ternyata masalahnya: **DEAD TUPLE** alias "data zombie"!

### **Apa itu Dead Tuple?**

**Analogi Mudah: Kantor dengan Arsip Berantakan**
```
📄 UPDATE = Buat dokumen baru, simpan yang lama "just in case"
📄 DELETE = Tandai dokumen "DELETED", tapi jangan buang dulu
🗂️ Lama-lama kantor penuh dokumen lama yang ga kepake
🧹 VACUUM = Tukang bersih-bersih yang buang sampah berkala
```

### **Demo: Lihat Dead Tuple Secara Live!**

#### **Setup: Tabel Chat Messages**
```sql
-- 💬 Simulasi tabel chat sederhana
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    room_id INTEGER,
    message TEXT,
    is_edited BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 📊 Insert 50K pesan chat
INSERT INTO chat_messages (user_id, room_id, message)
SELECT 
    1 + (RANDOM() * 1000)::INTEGER,      -- 1000 users
    1 + (RANDOM() * 100)::INTEGER,       -- 100 chat rooms  
    'Pesan chat nomor ' || i || ' ini adalah pesan yang cukup panjang untuk simulasi realistic chat application'
FROM generate_series(1, 50000) AS i;

-- ✅ Cek ukuran awal
SELECT 
    pg_size_pretty(pg_total_relation_size('chat_messages')) AS ukuran_total,
    pg_size_pretty(pg_relation_size('chat_messages')) AS ukuran_data;
```

#### **🧪 Experiment: Bikin Dead Tuple Banyak-banyak**
```sql
-- 👻 Bikin "zombie data" dengan UPDATE massal
DO $$
BEGIN
    RAISE NOTICE '👻 Mulai bikin DEAD TUPLE...';
    
    -- Update 1: Edit 25K pesan (bikin dead tuple)
    UPDATE chat_messages 
    SET message = message || ' [EDITED]',
        is_edited = TRUE,
        updated_at = NOW()
    WHERE id <= 25000;
    
    -- Update 2: Edit lagi 15K pesan (bikin lebih banyak dead tuple)  
    UPDATE chat_messages
    SET message = message || ' [EDITED AGAIN]',
        updated_at = NOW()
    WHERE id <= 15000;
    
    RAISE NOTICE '😈 Dead tuple sudah dibuat!';
END $$;
```

#### **🔍 Detective Mode: Lihat "Mayat" Data**
```sql
-- 🕵️ Analisis kesehatan tabel
SELECT 
    schemaname,
    relname AS table_name,
    n_tup_ins AS total_insert,
    n_tup_upd AS total_update,
    n_tup_del AS total_delete,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows,
    ROUND((n_dead_tup::FLOAT / GREATEST(n_live_tup, 1)) * 100, 2) AS dead_percentage,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables 
WHERE relname = 'chat_messages';
```

#### **🧹 Vacuum: Panggil Tukang Bersih-bersih**
```sql
-- 📊 Ukuran SEBELUM vacuum
\echo '=== BEFORE VACUUM ==='
SELECT 
    pg_size_pretty(pg_total_relation_size('chat_messages')) AS ukuran_sebelum,
    (SELECT n_dead_tup FROM pg_stat_user_tables WHERE relname = 'chat_messages') AS dead_tuples_sebelum;

-- 🧹 VACUUM dengan progress monitoring
VACUUM (VERBOSE, ANALYZE) chat_messages;

-- 📊 Ukuran SESUDAH vacuum  
\echo '=== AFTER VACUUM ==='
SELECT 
    pg_size_pretty(pg_total_relation_size('chat_messages')) AS ukuran_sesudah,
    (SELECT n_dead_tup FROM pg_stat_user_tables WHERE relname = 'chat_messages') AS dead_tuples_sesudah;
```

---

## 🏭 **Bagian 4: "Batch Processing" - Teknik Professional**

### 📖 **Cerita: Migration Data 10 Juta User**

> **Challenge:** Migrasi data user lama ke sistem baru. 10 juta record harus update kolom `account_type` dari 'free' jadi 'premium'. Kalau satu-satu = 3 hari! Pakai batch processing = 3 jam!

### **❌ Cara Newbie (Lambat & Berbahaya):**
```sql
-- 🐌 JANGAN lakukan ini untuk data besar!
-- UPDATE satu query besar = Lock lama, bisa crash sistem
UPDATE users SET account_type = 'premium' 
WHERE registration_date < '2020-01-01';  -- 5 juta baris sekaligus!
```

### **✅ Cara Professional (Cepat & Aman):**

#### **Setup Data untuk Demo**
```sql
-- 👥 Bikin tabel user dengan data realistis
CREATE TABLE user_accounts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    account_type VARCHAR(20) DEFAULT 'free',
    registration_date DATE,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 📊 Generate 500K users (simulasi skala menengah)
INSERT INTO user_accounts (username, email, account_type, registration_date)
SELECT 
    'user_' || i,
    'user' || i || '@example.com',
    CASE WHEN i % 10 = 0 THEN 'premium' ELSE 'free' END,  -- 10% premium user
    DATE '2020-01-01' + (RANDOM() * 1460)::INTEGER        -- Random date 2020-2024
FROM generate_series(1, 500000) AS i;

-- 🎯 Index untuk optimasi batch
CREATE INDEX idx_users_account_type ON user_accounts(account_type);
CREATE INDEX idx_users_registration ON user_accounts(registration_date);
CREATE INDEX idx_users_active ON user_accounts(is_active);

ANALYZE user_accounts;
```

#### **🚀 Batch Update dengan Progress Monitoring**
```sql
-- 🏭 Technique 1: Batch Update dengan Limit
DO $$
DECLARE
    batch_size INTEGER := 5000;  -- Update 5K baris per batch
    total_updated INTEGER := 0;
    batch_updated INTEGER;
    start_time TIMESTAMP;
BEGIN
    start_time := clock_timestamp();
    RAISE NOTICE '🚀 Memulai batch update users account_type...';
    
    LOOP
        -- Update batch kecil (5K rows)
        WITH updated_batch AS (
            UPDATE user_accounts 
            SET account_type = 'premium',
                last_login = NOW()
            WHERE account_type = 'free' 
              AND registration_date < '2022-01-01'
              AND id IN (
                  SELECT id FROM user_accounts 
                  WHERE account_type = 'free' 
                    AND registration_date < '2022-01-01'
                  LIMIT batch_size
              )
            RETURNING id
        )
        SELECT COUNT(*) FROM updated_batch INTO batch_updated;
        
        total_updated := total_updated + batch_updated;
        
        -- Progress report  
        RAISE NOTICE '✅ Batch selesai: % rows updated (Total: %)', 
                     batch_updated, total_updated;
        
        -- Exit kalau sudah tidak ada data
        EXIT WHEN batch_updated = 0;
        
        -- Jeda kecil biar tidak monopoli CPU
        PERFORM pg_sleep(0.1);
    END LOOP;
    
    RAISE NOTICE '🎉 BATCH UPDATE SELESAI! Total: % rows, Durasi: %', 
                 total_updated, clock_timestamp() - start_time;
END $$;
```

#### **🔥 Technique 2: Chunk-based Processing**
```sql
-- 🧩 Update berdasarkan ID range (lebih predictable)
DO $$
DECLARE
    min_id INTEGER;
    max_id INTEGER;
    current_id INTEGER := 0;
    chunk_size INTEGER := 10000;
    updated_count INTEGER;
BEGIN
    -- Dapatkan range ID
    SELECT MIN(id), MAX(id) INTO min_id, max_id FROM user_accounts;
    
    RAISE NOTICE '🎯 Memproses ID range: % to %', min_id, max_id;
    
    current_id := min_id;
    
    WHILE current_id < max_id LOOP
        UPDATE user_accounts 
        SET is_active = CASE 
                           WHEN last_login < NOW() - INTERVAL '1 year' THEN FALSE
                           ELSE TRUE
                       END
        WHERE id >= current_id 
          AND id < current_id + chunk_size;
          
        GET DIAGNOSTICS updated_count = ROW_COUNT;
        
        RAISE NOTICE '📊 Processed chunk ID % to %: % rows', 
                     current_id, current_id + chunk_size - 1, updated_count;
        
        current_id := current_id + chunk_size;
        
        -- Commit implisit setiap chunk (di real app pakai explicit)
        PERFORM pg_sleep(0.05);  -- 50ms break
    END LOOP;
    
    RAISE NOTICE '✨ Chunk processing selesai!';
END $$;
```

---

## 🏥 **Bagian 5: "Database Health Check" - Monitoring & Maintenance**

### **Tools untuk "Medical Check-up" Database**

#### **🩺 Checkup 1: Tabel Mana Yang Sakit?**
```sql
-- 🔍 Analisis kesehatan semua tabel
SELECT 
    schemaname||'.'||relname AS table_name,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows,
    CASE 
        WHEN n_live_tup > 0 THEN 
            ROUND((n_dead_tup::FLOAT / n_live_tup) * 100, 2) 
        ELSE 0 
    END AS dead_percentage,
    CASE
        WHEN n_live_tup > 0 AND (n_dead_tup::FLOAT / n_live_tup) > 0.5 THEN '🚨 CRITICAL'
        WHEN n_live_tup > 0 AND (n_dead_tup::FLOAT / n_live_tup) > 0.2 THEN '⚠️ WARNING'
        ELSE '✅ HEALTHY'
    END AS health_status,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    last_vacuum::DATE AS last_vacuum_date,
    last_autovacuum::DATE AS last_autovacuum_date
FROM pg_stat_user_tables 
ORDER BY n_dead_tup DESC;
```

#### **🩺 Checkup 2: Index Yang Tidak Terpakai (Sampah!)**
```sql
-- 🗑️ Cari index yang jarang/tidak dipakai (kandidat untuk dihapus)
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    CASE 
        WHEN idx_tup_read = 0 THEN '🚨 NEVER USED'
        WHEN idx_tup_read < 100 THEN '⚠️ RARELY USED'  
        ELSE '✅ ACTIVELY USED'
    END AS usage_status
FROM pg_stat_user_indexes
ORDER BY idx_tup_read ASC, pg_relation_size(indexrelid) DESC;
```

#### **🩺 Checkup 3: Query Paling "Nakal" (Resource Hog)**
```sql
-- 🐷 Top 10 query paling boros resource
SELECT 
    LEFT(query, 60) || '...' AS query_sample,
    calls,
    ROUND(total_exec_time::NUMERIC, 2) AS total_time_ms,
    ROUND(mean_exec_time::NUMERIC, 2) AS avg_time_ms,
    ROUND((100 * total_exec_time / SUM(total_exec_time) OVER())::NUMERIC, 2) AS percentage_cpu,
    rows_examined::BIGINT AS rows_examined
FROM pg_stat_statements
WHERE query NOT ILIKE '%pg_stat_statements%'
ORDER BY total_exec_time DESC
LIMIT 10;
```

### **🚨 Automated Health Alerts**
```sql
-- 🤖 Function untuk auto-monitoring (jalankan via cron)
CREATE OR REPLACE FUNCTION database_health_alert()
RETURNS TABLE (
    alert_level TEXT,
    table_name TEXT, 
    issue_description TEXT,
    recommended_action TEXT
) AS $$
BEGIN
    RETURN QUERY
    -- Alert untuk dead tuple tinggi
    SELECT 
        '🚨 CRITICAL' AS alert_level,
        schemaname||'.'||relname AS table_name,
        'Dead tuple ratio: ' || ROUND((n_dead_tup::FLOAT / GREATEST(n_live_tup,1)) * 100, 1) || '%' AS issue_description,
        'VACUUM ANALYZE ' || schemaname||'.'||relname || ';' AS recommended_action
    FROM pg_stat_user_tables
    WHERE n_live_tup > 1000 
      AND (n_dead_tup::FLOAT / GREATEST(n_live_tup,1)) > 0.3
    
    UNION ALL
    
    -- Alert untuk tabel tanpa vacuum lama
    SELECT 
        '⚠️ WARNING' AS alert_level,
        schemaname||'.'||relname AS table_name,
        'No vacuum since: ' || COALESCE(last_vacuum::TEXT, 'NEVER') AS issue_description,
        'Schedule regular VACUUM for this table' AS recommended_action  
    FROM pg_stat_user_tables
    WHERE (last_vacuum IS NULL OR last_vacuum < NOW() - INTERVAL '7 days')
      AND n_tup_upd + n_tup_del > 1000;
END $$ LANGUAGE plpgsql;

-- 🚁 Jalankan health check
SELECT * FROM database_health_alert();
```

---

## 🎖️ **Bagian 6: "Advanced Techniques" - Level Pro**

### **🔥 Technique 1: HOT Update Optimization**

#### **Apa itu HOT Update?**
**HOT = Heap-Only Tuple** = Update yang tidak perlu update semua index

**Analogi:**
```
📚 Buku di perpustakaan (= row)
🏷️ Sticker katalog di buku (= index)

HOT Update = Ganti isi halaman, sticker tetap sama
Normal Update = Ganti isi + update semua sticker
```

#### **Demo: Bikin Tabel HOT-Friendly**
```sql
-- 🔥 Tabel didesain untuk HOT update
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,                -- Index (jarang berubah)
    session_token VARCHAR(128),     -- Index (jarang berubah)
    
    -- Kolom yang SERING berubah (tidak di-index)
    last_activity TIMESTAMP,       -- Sering update, NO INDEX
    page_views INTEGER DEFAULT 0,  -- Sering update, NO INDEX  
    data_usage_mb INTEGER DEFAULT 0, -- Sering update, NO INDEX
    
    created_at TIMESTAMP DEFAULT NOW()
) WITH (fillfactor = 75);  -- Sisakan 25% ruang untuk HOT update

-- Index hanya untuk kolom stabil
CREATE INDEX idx_session_user ON user_sessions(user_id);
CREATE INDEX idx_session_token ON user_sessions(session_token);

-- ❌ JANGAN bikin index untuk kolom yang sering berubah!
-- CREATE INDEX idx_session_activity ON user_sessions(last_activity); -- BURUK!
```

#### **Test HOT vs Normal Update**
```sql
-- 📊 Insert test data
INSERT INTO user_sessions (user_id, session_token)
SELECT 
    1 + (RANDOM() * 1000)::INTEGER,
    'session_' || i || '_' || MD5(RANDOM()::TEXT)
FROM generate_series(1, 10000) AS i;

-- 🔥 HOT Update (hanya kolom non-index)
EXPLAIN (ANALYZE, BUFFERS) 
UPDATE user_sessions 
SET last_activity = NOW(),
    page_views = page_views + 1,
    data_usage_mb = data_usage_mb + 5
WHERE user_id = 123;

-- 🐌 Non-HOT Update (kolom yang ada index-nya)
EXPLAIN (ANALYZE, BUFFERS)
UPDATE user_sessions 
SET session_token = 'new_session_' || MD5(RANDOM()::TEXT)
WHERE user_id = 123;
```

### **🔥 Technique 2: UPSERT (INSERT ... ON CONFLICT)**

```sql
-- 🎯 Demo: E-commerce inventory system dengan UPSERT
CREATE TABLE product_inventory (
    product_id INTEGER PRIMARY KEY,
    stock_count INTEGER,
    last_updated TIMESTAMP DEFAULT NOW(),
    version INTEGER DEFAULT 1
);

-- 🚀 UPSERT: Insert kalau belum ada, Update kalau sudah ada
DO $$
DECLARE
    product_updates INTEGER[];
    product_id_val INTEGER;
    stock_change INTEGER;
BEGIN
    -- Simulasi update inventory dari berbagai sumber
    product_updates := ARRAY[101, 102, 103, 104, 105];
    
    FOREACH product_id_val IN ARRAY product_updates LOOP
        stock_change := -5 + (RANDOM() * 10)::INTEGER;  -- -5 to +5
        
        INSERT INTO product_inventory (product_id, stock_count) 
        VALUES (product_id_val, 100)
        ON CONFLICT (product_id) 
        DO UPDATE SET 
            stock_count = product_inventory.stock_count + stock_change,
            last_updated = NOW(),
            version = product_inventory.version + 1;
            
        RAISE NOTICE 'Product % inventory updated with change %', product_id_val, stock_change;
    END LOOP;
END $$;

-- 📊 Lihat hasil
SELECT * FROM product_inventory ORDER BY product_id;
```

---

## 🏆 **Bagian 7: "Final Challenge" - Comprehensive Test**

### **🥊 Challenge: Sistem E-commerce Lengkap**

```sql
-- 🏪 Bikin mini e-commerce database
CREATE SCHEMA IF NOT EXISTS ecommerce_test;
SET search_path = ecommerce_test, public;

-- Tabel utama
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(50),
    price DECIMAL(10,2),
    stock INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
) WITH (fillfactor = 80);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    unit_price DECIMAL(10,2)
);

-- Strategic indexes
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_stock ON products(stock) WHERE stock > 0;
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
```

### **⚡ Performance Test Suite**
```sql
-- 🧪 Generate realistic test data
DO $$
DECLARE
    i INTEGER;
    customer_id INTEGER;
    product_id INTEGER;
    order_id INTEGER;
    categories TEXT[] := ARRAY['Electronics', 'Fashion', 'Books', 'Home', 'Sports'];
BEGIN
    -- Insert customers
    FOR i IN 1..5000 LOOP
        INSERT INTO customers (name, email, phone)
        VALUES (
            'Customer ' || i,
            'customer' || i || '@email.com',
            '08' || LPAD((RANDOM() * 999999999)::BIGINT::TEXT, 9, '0')
        );
    END LOOP;
    
    -- Insert products  
    FOR i IN 1..2000 LOOP
        INSERT INTO products (name, category, price, stock)
        VALUES (
            'Product ' || i,
            categories[1 + (RANDOM() * 4)::INTEGER],
            (10 + RANDOM() * 990)::DECIMAL(10,2),
            (0 + RANDOM() * 100)::INTEGER
        );
    END LOOP;
    
    -- Insert orders with items
    FOR i IN 1..10000 LOOP
        -- Random customer
        customer_id := 1 + (RANDOM() * 5000)::INTEGER;
        
        INSERT INTO orders (customer_id, status, total_amount)
        VALUES (
            customer_id,
            CASE (RANDOM() * 4)::INTEGER
                WHEN 0 THEN 'pending'
                WHEN 1 THEN 'processing'  
                WHEN 2 THEN 'shipped'
                ELSE 'delivered'
            END,
            (10 + RANDOM() * 500)::DECIMAL(12,2)
        ) RETURNING id INTO order_id;
        
        -- Add 1-5 items per order
        FOR j IN 1..(1 + RANDOM() * 4)::INTEGER LOOP
            product_id := 1 + (RANDOM() * 2000)::INTEGER;
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (
                order_id,
                product_id,
                1 + (RANDOM() * 3)::INTEGER,
                (5 + RANDOM() * 100)::DECIMAL(10,2)
            );
        END LOOP;
    END LOOP;
    
    RAISE NOTICE '✅ Test data generated successfully!';
END $$;
```

### **📊 Final Performance Benchmarks**
```sql
-- 🏆 Ultimate performance test
\echo '=== E-COMMERCE PERFORMANCE BENCHMARK ==='

-- Test 1: Complex SELECT with JOINs
\echo 'Test 1: Complex ORDER query...'
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    c.name AS customer_name,
    o.id AS order_id,
    o.status,
    COUNT(oi.id) AS items_count,
    SUM(oi.quantity * oi.unit_price) AS calculated_total
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE o.status IN ('pending', 'processing')
  AND p.category = 'Electronics'
GROUP BY c.name, o.id, o.status
ORDER BY calculated_total DESC
LIMIT 100;

-- Test 2: Batch UPDATE orders
\echo 'Test 2: Batch UPDATE order status...'
UPDATE orders 
SET status = 'processing', updated_at = NOW()
WHERE status = 'pending' AND id <= 5000;

-- Test 3: Complex DELETE with foreign keys
\echo 'Test 3: Cleanup old orders...'
DELETE FROM order_items 
WHERE order_id IN (
    SELECT id FROM orders 
    WHERE status = 'delivered' 
      AND created_at < NOW() - INTERVAL '1 year'
    LIMIT 1000
);

-- Performance summary
\echo '=== PERFORMANCE SUMMARY ==='
SELECT 
    schemaname,
    relname,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size
FROM pg_stat_user_tables 
WHERE schemaname = 'ecommerce_test'
ORDER BY pg_total_relation_size(relid) DESC;
```

---

## 🎓 **Rangkuman & Best Practices**

### **✅ DOs (Yang HARUS Dilakukan)**

1. **🎯 Index Strategis**
   ```sql
   -- Index kolom yang sering di WHERE/JOIN
   CREATE INDEX idx_orders_status ON orders(status);
   CREATE INDEX idx_orders_customer ON orders(customer_id);
   ```

2. **⚡ Batch Processing**
   ```sql
   -- Update dalam batch kecil, bukan sekaligus besar
   UPDATE table SET col = val WHERE id BETWEEN 1 AND 1000;
   -- Lanjut batch berikutnya: 1001-2000, dst
   ```

3. **🧹 Regular Maintenance**
   ```sql
   -- Schedule vacuum analyze rutin
   VACUUM ANALYZE table_name;
   ```

4. **📊 Monitor Dead Tuples**
   ```sql
   -- Cek kesehatan tabel berkala
   SELECT * FROM pg_stat_user_tables WHERE n_dead_tup > n_live_tup * 0.2;
   ```

### **❌ DON'Ts (Yang JANGAN Dilakukan)**

1. **🚫 Jangan Over-Index**
   ```sql
   -- BURUK: Index di semua kolom
   CREATE INDEX ON table(col1);
   CREATE INDEX ON table(col2);  -- Mungkin tidak perlu
   CREATE INDEX ON table(col3);  -- Probably tidak perlu
   ```

2. **🚫 Jangan Transaksi Lama**
   ```sql
   -- BURUK: Lock dipegang lama
   BEGIN;
   UPDATE big_table SET col = val; -- Lock jutaan baris
   COMMIT;  -- Server hang!
   ```

3. **🚫 Jangan Abaikan VACUUM**
   ```sql
   -- BURUK: Biarkan dead tuple menumpuk
   -- Akibat: Database bengkak, query lambat
   ```

### **🏆 Performance Checklist:**

- [ ] **Index** strategis pada kolom WHERE/JOIN
- [ ] **Batch processing** untuk operasi besar  
- [ ] **Regular VACUUM** untuk cleanup dead tuples
- [ ] **Monitor** dead tuple ratio < 20%
- [ ] **HOT update** friendly table design
- [ ] **UPSERT** untuk insert-or-update patterns
- [ ] **Fillfactor** tuning untuk high-update tables

---

## 🎯 **Tugas Akhir & Evaluasi**

### **💡 Challenge untuk Mahasiswa:**

1. **Analisis Kasus:**
   - Pilih 1 aplikasi yang sering kalian pakai (Instagram, Shopee, dll)
   - Identifikasi 3 operasi DML yang mungkin "berat" (misal: like post, checkout, update profil)
   - Jelaskan strategi optimasi yang mungkin diterapkan

2. **Hands-on Project:**
   - Buat mini-aplikasi database (bebas: toko online, media sosial, dll)
   - Implementasikan optimasi DML yang sudah dipelajari
   - Bandingkan performa sebelum dan sesudah optimasi

3. **Report:**
   - Dokumentasikan hasil experimen (screenshot execution time)
   - Analisis: kenapa optimasi A lebih baik dari B?
   - Kesimpulan & learning points

### **🏅 Grading Criteria:**
- **Pemahaman konsep** (30%): Menjelaskan kenapa DML bisa lambat
- **Implementasi teknik** (40%): Berhasil terapkan optimasi
- **Analisis hasil** (20%): Dapat bandingkan & analisis performa  
- **Creativity** (10%): Ide kreatif untuk kasus unik

---

## 🚀 **Penutup: From Zero to DML Hero!**

Selamat! Kalian sudah menguasai:
- ⚡ **Rahasia** mengapa DML bisa lambat (biaya tersembunyi)  
- 🎯 **Teknik** optimasi INSERT/UPDATE/DELETE seperti pro developer
- 🔍 **Tools** monitoring untuk jadi database detective
- 🏭 **Batch processing** untuk handle data besar
- 🧹 **Maintenance** strategy untuk database sehat

### **Next Level Skills:**
- Advanced indexing strategies (partial, functional, composite)
- Partitioning untuk tabel raksasa  
- Replication & sharding untuk scale horizontal
- Database tuning di production environment

**💪 Remember:** Great developers tidak cuma bisa coding, tapi juga paham database performance!

**🎉 Happy Optimizing! Semoga database kalian selalu ngebut! 🚀**