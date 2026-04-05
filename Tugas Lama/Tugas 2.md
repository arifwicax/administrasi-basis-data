# Soal Cerita – Sistem Informasi Rumah Sakit

Sebuah **Rumah Sakit Balikpapan** ingin membangun sebuah sistem informasi yang dapat membantu dalam pengelolaan layanan kesehatan.

Di rumah sakit ini, **pasien** datang untuk berobat baik dengan cara **rawat jalan** maupun **rawat inap**. Setiap pasien yang datang akan **terdaftar** dalam sistem sehingga riwayat kunjungan dan layanannya bisa tercatat dengan baik.

Untuk pasien rawat inap, rumah sakit menyediakan **ruangan-ruangan** yang dapat dihuni sesuai dengan jenis layanan (misalnya VIP atau umum). Setiap ruangan memiliki kapasitas tertentu, sehingga hanya sejumlah pasien yang bisa dirawat di dalamnya.

**Dokter** yang bekerja di rumah sakit memiliki **spesialisasi** dan jadwal praktik tertentu. Dokter bertugas memeriksa pasien, memberikan diagnosa, menentukan tindakan medis, serta memberikan resep obat.

Selain dokter, ada juga **perawat** yang membantu memberikan layanan kepada pasien. Perawat dapat bertugas mendampingi beberapa pasien, dan sebaliknya seorang pasien juga dapat dilayani oleh lebih dari satu perawat.

Untuk mendukung keberlangsungan layanan, rumah sakit juga ingin menyimpan **rekam medis** setiap pasien. Rekam medis ini berisi catatan pemeriksaan, diagnosa, tindakan medis, serta obat yang diberikan. Catatan ini dibuat setiap kali pasien mendapatkan pelayanan dari dokter.

---

## 📌 Tugas Mahasiswa

1. Dari cerita di atas, identifikasi **entitas** apa saja yang perlu dibentuk dalam sistem.
2. Tentukan **atribut penting** untuk setiap entitas.
3. Tentukan **hubungan antar entitas** beserta **kardinalitasnya** (1:1, 1\:N, M\:N).
4. Buatlah **ERD** yang menggambarkan sistem informasi rumah sakit tersebut.
5. Optimalkan ERD agar tidak terjadi redundansi data.
6. Implementasikan ERD tersebut ke dalam **DDL Postgresql**.
