# **Visualisasi Data untuk Proyek Akhir Administrasi Basis Data**

## **Persiapan Visualisasi**

### **1. Mengapa Memilih Python untuk Visualisasi Data**

Python kini menjadi salah satu bahasa utama dalam **data science** dan **visualisasi data** karena beberapa alasan:

#### a. Pustaka yang Lengkap dan Siap Pakai

Python memiliki berbagai pustaka yang memudahkan pembuatan grafik dan analisis data, misalnya:

* **Matplotlib** → membuat grafik 2D seperti garis, batang, scatter, dll.
* **Seaborn** → grafik statistik yang menarik dan mudah dipahami.
* **Plotly / Bokeh** → untuk grafik interaktif berbasis web.
* **Geopandas, Folium, Kepler.gl, Cartopy** → visualisasi data geospasial.
* **Dash dan Streamlit** → membangun **dashboard interaktif** dengan cepat.

Dengan Python, semua tahap **pengolahan data** — mulai dari pembersihan, analisis, hingga visualisasi — dapat dilakukan dalam satu ekosistem, sehingga proyek akhir Anda menjadi lebih terstruktur.

---

### **2. Mengapa Menggunakan Miniconda atau Anaconda**

Jika hanya menggunakan Python standar, sering muncul kendala:

* Konflik versi pustaka (`numpy`, `pandas`, `matplotlib`).
* Kesulitan menginstal pustaka dengan dependensi sistem (misal `geopandas`, `rasterio`).
* Perbedaan versi Python di setiap proyek (misal proyek A pakai 3.9, proyek B pakai 3.12).

#### Solusi: Miniconda

Miniconda adalah versi ringan dari Anaconda yang berfungsi sebagai **manajer paket** dan **environment manager**, sehingga setiap proyek memiliki lingkungan Python terpisah.

Kelebihannya:

1. **Isolasi Lingkungan (Environment)**
   Setiap proyek dapat menggunakan pustaka dan versi Python berbeda tanpa saling bentrok.

   ```bash
   conda create -n visualisasi python=3.12
   conda activate visualisasi
   ```

2. **Instalasi Pustaka Lebih Mudah**
   Conda otomatis menginstal pustaka beserta dependensinya.

   ```bash
   conda install matplotlib seaborn geopandas
   ```

3. **Kompatibilitas Lintas Platform**
   Lingkungan Python yang sama bisa dijalankan di Windows, Linux, atau macOS.

4. **Integrasi dengan Jupyter Notebook**
   Memudahkan eksplorasi dan visualisasi data interaktif untuk proyek akhir.

---

### **3. Kombinasi Ideal: Miniconda + Python**

| Aspek                             | Python          | Miniconda                 |
| --------------------------------- | --------------- | ------------------------- |
| Bahasa pemrograman                | ✅ Ya            | ❌ Tidak                   |
| Manajemen paket                   | pip (terbatas)  | ✅ Conda lengkap           |
| Isolasi environment               | Terbatas (venv) | ✅ Sempurna                |
| Instalasi pustaka berat (GIS, ML) | ❌ Sering gagal  | ✅ Aman                    |
| Ukuran instalasi                  | Kecil           | Sedang (Miniconda ringan) |

---

## **4. Visualisasi Data Interaktif Menggunakan Streamlit**

### Apa itu Streamlit?

**Streamlit** adalah framework Python yang memungkinkan Anda membuat **aplikasi web interaktif** dengan cepat dan sederhana, tanpa perlu menulis HTML, CSS, atau JavaScript.

Streamlit sangat berguna untuk:

* Analisis **Data Science**
* **Visualisasi Geospasial**
* **Machine Learning**
* Proyek **CSR** atau analisis lingkungan

> Dengan Streamlit, skrip Python biasa dapat langsung diubah menjadi **dashboard interaktif**, cocok untuk **proyek akhir Administrasi Basis Data** yang menampilkan laporan atau visualisasi data dari basis data.

---



# **Proyek Akhir: Visualisasi Data Interaktif dengan Streamlit**

## **2. Instalasi dan Persiapan Lingkungan**

### a. Instalasi Pustaka Pendukung

Pasang paket-paket utama untuk visualisasi dan manipulasi data:

```bash
pip install streamlit pandas matplotlib seaborn plotly
```

### b. Verifikasi Instalasi

Cek apakah Streamlit terpasang dengan benar:

```bash
streamlit hello
```

> Perintah ini akan membuka demo resmi Streamlit di browser.

---

## **3. Struktur Dasar Program**

File Streamlit biasanya sederhana:

```
project/
└── app.py
```

Contoh isi `app.py`:

```python
import streamlit as st

st.title("Aplikasi Visualisasi Data Tanamin 🌱")
st.write("Selamat datang di aplikasi visualisasi data lingkungan!")
```

Jalankan dengan:

```bash
streamlit run app.py
```

Browser akan otomatis membuka `http://localhost:8501`.

---

## **4. Visualisasi Data Dasar**

### Contoh DataFrame

```python
import pandas as pd

data = pd.DataFrame({
    "Kampanye": ["Mangrove Balikpapan", "Pantai Samboja", "Delta Mahakam"],
    "Total Donasi (juta)": [120, 85, 60]
})

st.subheader("📈 Data Donasi Kampanye Lingkungan")
st.dataframe(data)
```

### a. Bar Chart

```python
st.bar_chart(data.set_index("Kampanye"))
```

### b. Line Chart

```python
st.line_chart(data.set_index("Kampanye"))
```

### c. Matplotlib

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.bar(data["Kampanye"], data["Total Donasi (juta)"], color="green")
ax.set_ylabel("Donasi (juta)")
st.pyplot(fig)
```

---

## **5. Menambahkan Interaktivitas**

### a. Dropdown (Selectbox)

```python
tipe = st.selectbox("Pilih jenis grafik:", ["Bar", "Pie"])

if tipe == "Bar":
    st.bar_chart(data.set_index("Kampanye"))
else:
    fig, ax = plt.subplots()
    ax.pie(data["Total Donasi (juta)"], labels=data["Kampanye"], autopct="%1.1f%%")
    st.pyplot(fig)
```

### b. Slider Filter

```python
nilai = st.slider("Tampilkan data dengan donasi minimum:", 0, 150, 50)
st.dataframe(data[data["Total Donasi (juta)"] >= nilai])
```

---

## **6. Visualisasi Geospasial**

Untuk menampilkan sebaran lokasi mangrove:

```python
import pandas as pd
import streamlit as st

st.title("Sebaran Lokasi Penanaman Mangrove 🌿")

data_peta = pd.DataFrame({
    'lokasi': ['Balikpapan', 'Samboja', 'Mahakam'],
    'lat': [-1.27, -1.10, -0.50],
    'lon': [116.83, 117.00, 117.25]
})

st.map(data_peta)
```

---

## **7. Dashboard Sederhana**

Contoh dashboard dengan metrik dan grafik:

```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Dashboard Donasi Lingkungan 🌱")

data = pd.DataFrame({
    "Kampanye": ["Mangrove Balikpapan", "Pantai Samboja", "Delta Mahakam"],
    "Donasi": [120, 85, 60],
    "Target": [150, 100, 90]
})

kampanye = st.selectbox("Pilih kampanye:", data["Kampanye"])
row = data[data["Kampanye"] == kampanye].iloc[0]

st.metric("Donasi Saat Ini", f"{row['Donasi']} juta", delta=row['Donasi'] - row['Target'])
st.progress(row['Donasi'] / row['Target'])

fig, ax = plt.subplots()
ax.bar(data["Kampanye"], data["Donasi"], color="green")
ax.set_ylabel("Donasi (juta)")
st.pyplot(fig)
```

---

## **8. Menambahkan Gambar dan Teks**

```python
st.image("mangrove.jpg", caption="Kegiatan Penanaman Mangrove di Balikpapan")
st.markdown("""
### Tujuan Program
Meningkatkan kesadaran masyarakat terhadap pentingnya ekosistem mangrove.
""")
```

---

## **9. Deploy ke Cloud (Opsional)**

Gunakan **Streamlit Cloud**: [https://share.streamlit.io](https://share.streamlit.io)

Langkah singkat:

1. Buat repository di GitHub.
2. Upload file `app.py` dan `requirements.txt`.
3. Login ke Streamlit Cloud, pilih “New App” → hubungkan ke GitHub.
4. Jalankan aplikasi langsung dari browser.

---

## **10. Kesimpulan**

| Keunggulan    | Keterangan                                        |
| ------------- | ------------------------------------------------- |
| 🚀 Cepat      | Dari Python ke web dalam hitungan menit           |
| 🧠 Mudah      | Tidak perlu HTML/CSS                              |
| 📊 Kuat       | Dukungan Matplotlib, Plotly, Seaborn              |
| 🌍 Interaktif | Cocok untuk visualisasi CSR dan donasi lingkungan |
| 🧩 Fleksibel  | Bisa digabung dengan data real-time dan peta      |

---


# **Materi Dasar Pemrograman Python**

## **Tujuan Pembelajaran**

Setelah mempelajari materi ini, mahasiswa diharapkan mampu:

1. Memahami konsep dasar Python.
2. Menggunakan variabel, tipe data, dan operator.
3. Menulis percabangan dan perulangan.
4. Membuat fungsi sederhana dan fungsi dengan nilai kembali.
5. Mengelola data menggunakan list, tuple, dan dictionary.
6. Melakukan input/output dan membaca/menulis file.

---

## **1. Pengenalan Python**

Python adalah bahasa pemrograman **tingkat tinggi**, mudah dibaca, **open-source**, dan **multiplatform**.
Digunakan luas untuk: web development, data science, AI, automasi, dan visualisasi data.

**Keunggulan:**

* Sintaks mirip bahasa manusia
* Komunitas besar dan pustaka lengkap (misal: NumPy, Pandas, Matplotlib)
* Cocok untuk pemula maupun profesional

**Menjalankan Python:**

* Interpreter: `python`
* File Python: `python nama_file.py`
* Jupyter Notebook: `jupyter notebook`

---

## **2. Variabel dan Tipe Data**

**Variabel** digunakan untuk menyimpan data:

```python
nama = "Arif"
umur = 25
tinggi = 166,5
aktif = True
```

**Tipe data dasar:**

| Tipe Data | Contoh      | Keterangan         |
| --------- | ----------- | ------------------ |
| `int`     | 10, -5      | Bilangan bulat     |
| `float`   | 3.14, 2.5   | Bilangan desimal   |
| `str`     | "Tanamin"   | Teks / string      |
| `bool`    | True, False | Logika benar/salah |

---

## **3. Operator Dasar**

### Aritmatika

```python
a, b = 10, 3
print(a + b)  # Penjumlahan
print(a - b)  # Pengurangan
print(a * b)  # Perkalian
print(a / b)  # Pembagian float
print(a // b) # Pembagian bulat
print(a % b)  # Sisa bagi
print(a ** b) # Pangkat
```

### Perbandingan

```python
print(a == b)  # Sama dengan
print(a != b)  # Tidak sama dengan
print(a > b)   # Lebih besar
print(a < b)   # Lebih kecil
```

### Logika

```python
x, y = True, False
print(x and y)  # AND
print(x or y)   # OR
print(not x)    # NOT
```

---

## **4. Struktur Kontrol**

### Percabangan (if, elif, else)

```python
nilai = 85
if nilai >= 90:
    print("A")
elif nilai >= 75:
    print("B")
else:
    print("C")
```

### Perulangan (for)

```python
for i in range(5):
    print("Perulangan ke-", i)
```

### Perulangan (while)

```python
count = 0
while count < 3:
    print("Iterasi", count)
    count += 1
```

---

## **5. Struktur Data**

### List (dapat diubah)

```python
buah = ["mangga", "apel", "pisang"]
buah.append("jeruk")
print(buah)
```

### Tuple (tidak dapat diubah)

```python
warna = ("merah", "hijau", "biru")
print(warna[1])
```

### Dictionary (kunci-nilai)

```python
donatur = {"nama": "Andi", "jumlah": 500000, "kota": "Balikpapan"}
donatur["status"] = "aktif"
print(donatur)
```

---

## **6. Fungsi**

### Fungsi sederhana

```python
def sapa(nama):
    print(f"Halo {nama}, selamat datang!")

sapa("Arif")
```

### Fungsi dengan return

```python
def luas_persegi(sisi):
    return sisi * sisi

hasil = luas_persegi(4)
print("Luas:", hasil)
```

---

## **7. Input dan Output**

### Input

```python
nama = input("Masukkan nama: ")
print("Halo,", nama)
```

### Output dengan f-string

```python
umur = 25
print(f"Nama saya {nama}, umur {umur} tahun.")
```

---

## **8. Membaca dan Menulis File**

### Menulis

```python
with open("data.txt", "w") as f:
    f.write("Data donasi mangrove\n")
```

### Membaca

```python
with open("data.txt", "r") as f:
    print(f.read())
```

---

## **9. Contoh Mini: Total Donasi**

```python
donasi = [
    {"nama": "Andi", "jumlah": 500000},
    {"nama": "Siti", "jumlah": 750000},
    {"nama": "Budi", "jumlah": 300000}
]

total = sum(d["jumlah"] for d in donasi)
print("Total Donasi:", total)
```

**Output:** `Total Donasi: 1550000`

---

## **10. Latihan Praktik**

1. Hitung **luas dan keliling persegi panjang** dari input pengguna.
2. Tampilkan **angka ganjil 1–100** menggunakan perulangan.
3. Buat daftar `donasi = [100000, 250000, 150000]`, tampilkan total & rata-rata.
4. Buat fungsi untuk cek **bilangan prima**.
5. Simpan semua latihan dalam `.py` dan jalankan via terminal.

---

## **11. Kesimpulan**

| Konsep               | Keterangan                            |
| -------------------- | ------------------------------------- |
| Variabel & Tipe Data | Menyimpan nilai dan informasi         |
| Operator             | Operasi matematika dan logika         |
| Percabangan          | Pengambilan keputusan                 |
| Perulangan           | Menjalankan kode berulang             |
| Fungsi               | Membuat kode terstruktur dan reusable |
| Struktur Data        | Mengelola data dengan efisien         |

---


# **Proyek Akhir Administrasi Basis Data: Visualisasi Data Interaktif**

## **1. Tujuan Proyek**

Setelah menyelesaikan proyek ini, mahasiswa diharapkan dapat:

1. Mengambil data dari database (MySQL / PostgreSQL / SQLite).
2. Mengolah data menggunakan Python.
3. Membuat visualisasi interaktif menggunakan **Streamlit**.
4. Menyajikan data dalam bentuk **dashboard** yang informatif dan mudah dipahami.
5. Memahami alur **ETL (Extract, Transform, Load)** sederhana dalam proyek basis data.

---

## **2. Persiapan Lingkungan**

### **a. Membuat Environment dengan Miniconda**

```bash
conda create -n proyek_db python=3.12
conda activate proyek_db
```

### **b. Instalasi Pustaka yang Dibutuhkan**

```bash
pip install streamlit pandas matplotlib seaborn plotly sqlalchemy mysql-connector-python psycopg2
```

* **streamlit** → membuat dashboard interaktif.
* **pandas** → manipulasi data.
* **matplotlib / seaborn / plotly** → visualisasi.
* **sqlalchemy** → koneksi dan query database.
* **mysql-connector-python / psycopg2** → driver database MySQL/PostgreSQL.

---

## **3. Struktur Proyek**

```
proyek_akhir_db/
├── app.py             # File utama Streamlit
├── config.py          # Konfigurasi database
├── requirements.txt   # Daftar pustaka
└── data/              # Folder untuk file tambahan (opsional)
```

---

## **4. Menghubungkan Streamlit ke Database**

### **a. Contoh config.py**

```python
DB_TYPE = 'mysql'  # mysql / postgresql / sqlite
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'password'
DB_NAME = 'donasi_mangrove'
```

### **b. Membuat koneksi database**

```python
from sqlalchemy import create_engine
import pandas as pd
import config

# Membuat URL koneksi
engine = create_engine(f"{config.DB_TYPE}+mysqlconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}")

# Contoh query
data = pd.read_sql("SELECT * FROM donasi", engine)
```

---

## **5. Membuat Dashboard Streamlit**

### **a. Struktur dasar app.py**

```python
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import config

# Koneksi database
engine = create_engine(f"{config.DB_TYPE}+mysqlconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}")
data = pd.read_sql("SELECT * FROM donasi", engine)

# Judul dashboard
st.title("Dashboard Donasi Lingkungan 🌱")
st.subheader("Visualisasi Data Donasi Berdasarkan Kampanye")
st.dataframe(data)
```

### **b. Visualisasi Bar Chart**

```python
st.bar_chart(data.set_index("kampanye")["jumlah_donasi"])
```

### **c. Visualisasi Line Chart**

```python
st.line_chart(data.set_index("kampanye")["jumlah_donasi"])
```

### **d. Visualisasi Matplotlib**

```python
fig, ax = plt.subplots()
ax.bar(data["kampanye"], data["jumlah_donasi"], color="green")
ax.set_ylabel("Jumlah Donasi")
st.pyplot(fig)
```

---

## **6. Menambahkan Interaktivitas**

### **a. Dropdown untuk memilih kampanye**

```python
kampanye = st.selectbox("Pilih Kampanye:", data["kampanye"].unique())
data_kampanye = data[data["kampanye"] == kampanye]
st.write(data_kampanye)
```

### **b. Slider untuk filter donasi**

```python
nilai_min = st.slider("Tampilkan donasi minimal:", 0, int(data["jumlah_donasi"].max()), 50000)
st.dataframe(data[data["jumlah_donasi"] >= nilai_min])
```

---

## **7. Visualisasi Geospasial (Opsional)**

Jika tabel memiliki **kolom latitude dan longitude**, bisa ditampilkan di peta:

```python
st.map(data[["latitude", "longitude"]])
```

---

## **8. Menambahkan KPI / Metric**

```python
total_donasi = data["jumlah_donasi"].sum()
st.metric("Total Donasi", f"{total_donasi} IDR")
```

---

## **9. Menambahkan Progress / Target Campaign**

```python
kampanye = "Mangrove Balikpapan"
donasi_kampanye = data[data["kampanye"] == kampanye]["jumlah_donasi"].sum()
target = 1500000

st.progress(donasi_kampanye / target)
st.write(f"Progress Kampanye {kampanye}: {donasi_kampanye} / {target}")
```

---

## **10. Deployment**

### **a. Persiapan Repository**

* Buat repository GitHub, upload `app.py`, `config.py`, dan `requirements.txt`.

### **b. Deploy di Streamlit Cloud**

1. Login di [https://share.streamlit.io](https://share.streamlit.io)
2. Pilih **New App**, hubungkan ke GitHub
3. Jalankan dashboard langsung di browser.

---

## **11. Saran Struktur Database Proyek**

| Tabel    | Kolom                                              | Keterangan                       |
| -------- | -------------------------------------------------- | -------------------------------- |
| donasi   | id, nama_donatur, kampanye, jumlah_donasi, tanggal | Data transaksi donasi            |
| kampanye | id, nama_kampanye, target, lokasi                  | Info kampanye penanaman mangrove |

> Dengan struktur ini, mahasiswa bisa menampilkan **dashboard lengkap**, termasuk **total donasi**, **progress per kampanye**, dan **peta lokasi**.

---

## **12. Kesimpulan Proyek Akhir**

* Mahasiswa belajar **integrasi database + visualisasi**.
* Memahami alur **ETL sederhana**: Ambil data → Olah → Visualisasi.
* Dashboard interaktif mempermudah **analisis dan pelaporan data**.
* Cocok untuk **proyek akhir Administrasi Basis Data**, sekaligus mempraktikkan Python, SQL, dan visualisasi interaktif.

---

## **1. Index di Database (SQL)**

Index di database membantu **mempercepat query** ketika mengambil data dari tabel. Contoh:

### a. Index pada kolom yang sering dicari

Misal, tabel `donasi` sering dicari berdasarkan `kampanye`:

```sql
CREATE INDEX idx_kampanye ON donasi(kampanye);
```

* Mempercepat query `SELECT * FROM donasi WHERE kampanye='Mangrove Balikpapan';`
* Tidak mempengaruhi visualisasi, tapi **mengurangi waktu query** saat dashboard Streamlit menampilkan data.

### b. Index unik (Unique Index)

Jika kolom harus **unik**, misal `nama_donatur` per kampanye:

```sql
CREATE UNIQUE INDEX idx_donatur_kampanye ON donasi(nama_donatur, kampanye);
```

* Memastikan tidak ada duplikasi data.
* Berguna untuk **dashboard validasi data**.

---

## **2. Index di Visualisasi (Python / Pandas)**

Di Pandas, **index** bisa digunakan untuk mempermudah pemanggilan data dan visualisasi:

```python
import pandas as pd

# Set kolom 'kampanye' sebagai index
data = pd.read_sql("SELECT * FROM donasi", engine)
data.set_index("kampanye", inplace=True)

# Visualisasi bar chart lebih mudah
st.bar_chart(data["jumlah_donasi"])
```

* Index membantu **labeling grafik otomatis**.
* Bisa digabung dengan filter, misal `data.loc["Mangrove Balikpapan"]`.

---

## **3. Index di Dashboard / KPI**

Untuk proyek akhir, bisa juga membuat **index/indikator performa** seperti:

* **Index donasi** = Total Donasi / Target Kampanye × 100%
* **Index partisipasi** = Jumlah Donatur / Target Donatur × 100%

Contoh di Streamlit:

```python
data["index_donasi"] = (data["jumlah_donasi"] / data["target"]) * 100
st.dataframe(data[["kampanye", "jumlah_donasi", "target", "index_donasi"]])
```

* Mempermudah **visualisasi progress** per kampanye.
* Bisa ditampilkan sebagai **progress bar**, chart, atau metric.

---

