import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
from db import run_query, run_command

# ─── Konfigurasi Halaman ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="PostgreSQL Monitor",
    page_icon="🐘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS Kustom ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stMetric"] { background: #1e1e2e; border-radius: 10px; padding: 12px; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem; color: #a6adc8; }
    [data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; padding: 8px 16px; }
    hr { margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.title("🐘 PostgreSQL Performance Monitor")
st.caption("Dashboard monitoring performa PostgreSQL — Administrasi Basis Data · Pertemuan 15")
st.divider()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Pengaturan")
    auto_refresh = st.toggle("Auto Refresh", value=False)
    if auto_refresh:
        interval = st.slider("Interval (detik)", 5, 60, 10)
    st.divider()
    st.subheader("🧪 Simulasi Beban")
    beban_baca = st.button("▶ Jalankan Beban Baca", use_container_width=True)
    beban_tulis = st.button("▶ Jalankan Beban Tulis (1.000 baris)", use_container_width=True)
    reset_stats = st.button("🔄 Reset pg_stat_statements", use_container_width=True)
    st.divider()
    st.info(
        "Data diambil langsung dari:\n"
        "- `pg_stat_database`\n"
        "- `pg_stat_activity`\n"
        "- `pg_stat_user_tables`\n"
        "- `pg_stat_statements`"
    )

# ─── Eksekusi Simulasi Beban ─────────────────────────────────────────────────
if beban_baca:
    with st.spinner("Menjalankan beban baca..."):
        run_query("""
            SELECT p.nama, SUM(t.jumlah) AS total_terjual, SUM(t.total_harga) AS total_pendapatan
            FROM transaksi t
            JOIN produk p ON p.nama = t.produk
            GROUP BY p.nama
            ORDER BY total_pendapatan DESC;
        """)
    st.toast("✅ Beban baca selesai dijalankan.", icon="✅")

if beban_tulis:
    with st.spinner("Memasukkan 1.000 baris baru..."):
        run_command("""
            INSERT INTO transaksi (pelanggan, produk, jumlah, total_harga)
            SELECT
                'Pelanggan-' || (random() * 1000)::INT,
                'Produk-'    || (random() * 100)::INT,
                (random() * 10 + 1)::INT,
                (random() * 5000000)::NUMERIC(12,2)
            FROM generate_series(1, 1000);
        """)
    st.toast("✅ 1.000 baris berhasil ditambahkan.", icon="✅")

if reset_stats:
    run_command("SELECT pg_stat_reset();")
    run_command("SELECT pg_stat_statements_reset();")
    st.toast("🔄 Statistik berhasil direset.", icon="🔄")

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Ringkasan",
    "🔗 Koneksi",
    "🐢 Query Lambat",
    "🗄️ Tabel & Storage",
    "🔒 Lock & Deadlock",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RINGKASAN
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Ringkasan Performa Database")

    sql_summary = """
        SELECT
            datname                                         AS database,
            numbackends                                     AS koneksi,
            xact_commit                                     AS commit,
            xact_rollback                                   AS rollback,
            blks_hit,
            blks_read,
            ROUND(
                blks_hit::NUMERIC / NULLIF(blks_hit + blks_read, 0) * 100, 2
            )                                               AS cache_hit_persen
        FROM pg_stat_database
        WHERE datname NOT IN ('postgres', 'template0', 'template1')
        ORDER BY xact_commit DESC;
    """
    df_summary = run_query(sql_summary)

    if not df_summary.empty:
        # Metrik utama — baris pertama (database aktif)
        row = df_summary.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Database", row["database"])
        c2.metric("Koneksi Aktif", int(row["koneksi"]))
        c3.metric("Total Commit", f"{int(row['commit']):,}")
        c4.metric("Total Rollback", f"{int(row['rollback']):,}")
        cache = row["cache_hit_persen"] if row["cache_hit_persen"] is not None else 0
        c5.metric("Cache Hit Ratio", f"{cache}%", delta="ideal ≥ 95%")

        st.divider()

        # Grafik cache hit ratio semua database
        fig = px.bar(
            df_summary.dropna(subset=["cache_hit_persen"]),
            x="database",
            y="cache_hit_persen",
            color="cache_hit_persen",
            color_continuous_scale="RdYlGn",
            range_y=[0, 100],
            title="Cache Hit Ratio per Database (%)",
            labels={"cache_hit_persen": "Cache Hit (%)"},
        )
        fig.add_hline(
            y=95, line_dash="dash", line_color="red",
            annotation_text="Ambang batas ideal (95%)",
            annotation_position="top left",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Data Lengkap")
        st.dataframe(df_summary, use_container_width=True)
    else:
        st.warning("Tidak ada data database yang dapat ditampilkan.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — KONEKSI
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Sesi dan Koneksi Aktif")

    sql_koneksi = """
        SELECT
            pid,
            usename                                                         AS pengguna,
            datname                                                         AS database,
            state,
            ROUND(EXTRACT(EPOCH FROM (NOW() - query_start))::NUMERIC, 1)   AS durasi_detik,
            wait_event_type,
            wait_event,
            LEFT(query, 120)                                                AS query
        FROM pg_stat_activity
        WHERE datname IS NOT NULL
          AND query NOT LIKE '%pg_stat_activity%'
        ORDER BY durasi_detik DESC NULLS LAST;
    """
    df_koneksi = run_query(sql_koneksi)

    if not df_koneksi.empty:
        ca, cb, cc = st.columns(3)
        ca.metric("Total Sesi", len(df_koneksi))
        cb.metric("Aktif", len(df_koneksi[df_koneksi["state"] == "active"]))
        cc.metric("Idle",  len(df_koneksi[df_koneksi["state"] == "idle"]))

        # Distribusi status
        state_counts = df_koneksi["state"].value_counts().reset_index()
        state_counts.columns = ["state", "jumlah"]
        fig_pie = px.pie(
            state_counts, values="jumlah", names="state",
            title="Distribusi Status Koneksi",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.subheader("Daftar Sesi")
        st.dataframe(df_koneksi, use_container_width=True)

        # Peringatan koneksi lama
        lama = df_koneksi[
            (df_koneksi["durasi_detik"].notna()) &
            (df_koneksi["durasi_detik"] > 30) &
            (df_koneksi["state"] == "active")
        ]
        if not lama.empty:
            st.warning(f"⚠️ Terdapat **{len(lama)} query aktif** yang berjalan lebih dari 30 detik.")
            st.dataframe(lama[["pid", "pengguna", "durasi_detik", "query"]], use_container_width=True)
    else:
        st.success("✅ Tidak ada sesi aktif saat ini.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — QUERY LAMBAT
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Query Paling Lambat (pg_stat_statements)")

    sql_slow = """
        SELECT
            LEFT(query, 100)                        AS query,
            calls                                   AS eksekusi,
            ROUND(mean_exec_time::NUMERIC, 2)       AS rata2_ms,
            ROUND(min_exec_time::NUMERIC, 2)        AS min_ms,
            ROUND(max_exec_time::NUMERIC, 2)        AS max_ms,
            ROUND(total_exec_time::NUMERIC, 2)      AS total_ms,
            rows
        FROM pg_stat_statements
        WHERE query NOT LIKE '%pg_stat%'
        ORDER BY mean_exec_time DESC
        LIMIT 15;
    """
    df_slow = run_query(sql_slow)

    if not df_slow.empty:
        fig_slow = px.bar(
            df_slow.head(10),
            x="rata2_ms",
            y="query",
            orientation="h",
            title="Top 10 Query Lambat — Rata-rata Waktu Eksekusi (ms)",
            labels={"rata2_ms": "Rata-rata (ms)", "query": "Query"},
            color="rata2_ms",
            color_continuous_scale="Reds",
        )
        fig_slow.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_slow, use_container_width=True)
        st.dataframe(df_slow, use_container_width=True)
    else:
        st.info("ℹ️ Tidak ada data. Pastikan ekstensi `pg_stat_statements` sudah aktif.")
        st.code("CREATE EXTENSION IF NOT EXISTS pg_stat_statements;", language="sql")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — TABEL & STORAGE
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Statistik Tabel dan Storage")

    sql_tabel = """
        SELECT
            relname                                             AS tabel,
            pg_size_pretty(pg_total_relation_size(relid))      AS ukuran_total,
            pg_size_pretty(pg_relation_size(relid))            AS ukuran_data,
            pg_size_pretty(pg_indexes_size(relid))             AS ukuran_indeks,
            n_live_tup                                         AS baris_aktif,
            n_dead_tup                                         AS baris_mati,
            seq_scan                                           AS full_scan,
            idx_scan                                           AS index_scan,
            last_vacuum,
            last_autovacuum
        FROM pg_stat_user_tables
        ORDER BY pg_total_relation_size(relid) DESC;
    """
    df_tabel = run_query(sql_tabel)

    if not df_tabel.empty:
        # Peringatan dead tuples tinggi
        dead_high = df_tabel[df_tabel["baris_mati"] > 1000]
        if not dead_high.empty:
            st.warning(f"⚠️ **{len(dead_high)} tabel** memiliki dead tuples > 1.000. Pertimbangkan VACUUM ANALYZE.")

        # Grafik perbandingan baris aktif vs mati
        fig_dead = px.bar(
            df_tabel.head(10),
            x="tabel",
            y=["baris_aktif", "baris_mati"],
            barmode="group",
            title="Baris Aktif vs Dead Tuples per Tabel",
            labels={"value": "Jumlah Baris", "variable": "Tipe"},
            color_discrete_map={"baris_aktif": "#4ade80", "baris_mati": "#f87171"},
        )
        st.plotly_chart(fig_dead, use_container_width=True)

        # Grafik full scan vs index scan
        fig_scan = px.bar(
            df_tabel.head(10),
            x="tabel",
            y=["full_scan", "index_scan"],
            barmode="group",
            title="Full Scan vs Index Scan per Tabel",
            labels={"value": "Jumlah Scan", "variable": "Tipe Scan"},
            color_discrete_map={"full_scan": "#fb923c", "index_scan": "#60a5fa"},
        )
        st.plotly_chart(fig_scan, use_container_width=True)

        st.dataframe(df_tabel, use_container_width=True)
    else:
        st.info("Belum ada tabel pengguna yang tercatat.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — LOCK & DEADLOCK
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Lock dan Antrian Menunggu")

    sql_lock = """
        SELECT
            l.pid,
            a.usename                           AS pengguna,
            a.datname                           AS database,
            l.mode,
            l.granted,
            l.locktype,
            a.state,
            LEFT(a.query, 100)                  AS query
        FROM pg_locks l
        JOIN pg_stat_activity a ON l.pid = a.pid
        WHERE a.query NOT LIKE '%pg_locks%'
        ORDER BY l.granted, l.pid;
    """
    df_lock = run_query(sql_lock)

    if df_lock.empty:
        st.success("✅ Tidak ada lock yang terdeteksi saat ini.")
    else:
        menunggu = df_lock[df_lock["granted"] == False]
        if not menunggu.empty:
            st.error(f"🔴 Terdapat **{len(menunggu)} proses** yang sedang menunggu lock!")
            st.dataframe(menunggu, use_container_width=True)
        else:
            st.success("✅ Tidak ada proses yang menunggu lock.")

        with st.expander("Lihat semua lock yang aktif"):
            st.dataframe(df_lock, use_container_width=True)

# ─── Auto Refresh ─────────────────────────────────────────────────────────────
if auto_refresh:
    st.caption(f"🔄 Halaman akan diperbarui dalam {interval} detik...")
    time.sleep(interval)
    st.rerun()
