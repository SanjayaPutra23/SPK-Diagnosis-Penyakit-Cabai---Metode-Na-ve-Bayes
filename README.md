# 🌶️ SPK Diagnosis Penyakit Cabai - Metode Naïve Bayes

![Flask](https://img.shields.io/badge/Flask-2.3.x-green.svg?logo=flask)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg?logo=mysql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg?logo=bootstrap)

Sistem Pendukung Keputusan (SPK) berbasis web yang dirancang untuk membantu petani dalam mendiagnosis penyakit pada tanaman cabai (*Capsicum annuum* L.) secara cepat, objektif, dan akurat. Sistem ini dibangun menggunakan framework **Flask (Python)** dan mengimplementasikan algoritma **Naïve Bayes** yang dioptimalkan dengan penambahan variabel **Fase Pertumbuhan Tanaman (Vegetatif dan Generatif)**.

---

## 📑 Daftar Isi

1. Latar Belakang dan Kebaruan Sistem
2. Sumber Basis Pengetahuan
3. Arsitektur Algoritma Naïve Bayes
4. Struktur Database (ERD)
5. Fitur Utama Sistem
6. Panduan Instalasi dan Konfigurasi

---

## 1. Latar Belakang dan Kebaruan Sistem

Diagnosis penyakit tanaman cabai secara konvensional masih sangat bergantung pada pengalaman subjektif petani, sehingga sering menimbulkan kesalahan akibat kemiripan gejala antar penyakit. Kondisi ini menyebabkan keterlambatan penanganan dan berpotensi menurunkan produktivitas hasil panen.

Sistem ini dikembangkan sebagai alat bantu diagnosis digital berbasis web yang ringan dan efisien, tanpa memerlukan pemrosesan citra yang kompleks, namun tetap memiliki dasar perhitungan matematis yang kuat.

### Kebaruan (Novelty)

Keunikan utama dari sistem ini terletak pada integrasi **variabel fase pertumbuhan tanaman (vegetatif dan generatif)** ke dalam proses inferensi algoritma Naïve Bayes. Pendekatan ini terbukti mampu meningkatkan kontras probabilitas antar penyakit yang memiliki gejala serupa, sehingga hasil diagnosis menjadi lebih spesifik dan akurat.

---

## 2. Sumber Basis Pengetahuan

Basis pengetahuan yang digunakan dalam sistem ini disusun berdasarkan referensi ilmiah dan pedoman teknis yang telah terverifikasi, antara lain:

* **Kamus Gejala dan Penanganan Penyakit**: Diadaptasi dari pedoman teknis Meilin (2014) yang diterbitkan oleh Balai Pengkajian Teknologi Pertanian Jambi.
* **Nilai Probabilitas Awal (Prior) dan Probabilitas Bersyarat (Likelihood)**: Mengacu pada dataset penelitian Santoso et al. (2025).
* **Logika Pemisahan Fase Pertumbuhan**: Disusun berdasarkan rekomendasi penanganan ambiguitas gejala tanaman dari Lestari (2025).

---

## 3. Arsitektur Algoritma Naïve Bayes

Sistem ini menerapkan algoritma klasifikasi probabilistik **Naïve Bayes** dengan asumsi bahwa setiap gejala bersifat independen secara kondisional terhadap kelas penyakit.

### Perhitungan Numerator (Pembilang)

```
Numerator = P(H) × ∏ P(Eᵢ | H, Fase)
```

Keterangan:

* **P(H)** : Probabilitas awal (prior) dari suatu penyakit.
* **P(Eᵢ | H, Fase)** : Probabilitas kemunculan gejala ke-i pada penyakit tertentu berdasarkan fase pertumbuhan tanaman.

### Perhitungan Posterior (Normalisasi)

```
P(H | E) = Numerator / Σ (seluruh nilai Numerator)
```

Penyakit dengan nilai probabilitas posterior tertinggi (*maximum posterior probability*) ditetapkan sebagai hasil diagnosis akhir.

---

## 4. Struktur Database (ERD)

Sistem ini menggunakan database relasional **MySQL** yang terdiri dari enam tabel utama, yaitu:

1. **users** – Mengelola autentikasi dan otorisasi pengguna dengan pemisahan peran admin dan petani.
2. **penyakit** – Menyimpan data master penyakit beserta nilai prior probability.
3. **gejala** – Menyimpan data indikator gejala fisik tanaman yang dikelompokkan berdasarkan organ (daun, batang, buah, dan akar).
4. **bobot_probabilitas** – Tabel relasi yang menyimpan nilai likelihood antara penyakit, gejala, dan fase pertumbuhan.
5. **rekomendasi** – Menyimpan informasi solusi atau tindakan pengendalian penyakit (relasi satu ke satu dengan tabel penyakit).
6. **diagnosa** – Menyimpan riwayat hasil diagnosis, termasuk nilai posterior, fase pertumbuhan input, dan waktu diagnosis.

---

## 5. Fitur Utama Sistem

### A. Fitur untuk Petani

* **Diagnosis Cepat**: Form input gejala yang dikelompokkan berdasarkan organ tanaman dan fase pertumbuhan.
* **Transparansi Perhitungan**: Menampilkan detail perhitungan Naïve Bayes (prior, likelihood, numerator, dan posterior).
* **Rekomendasi Penanganan**: Memberikan langkah pengendalian penyakit sesuai pedoman pakar.
* **Riwayat Diagnosis**: Menyimpan dan menampilkan hasil diagnosis yang pernah dilakukan.

### B. Fitur untuk Administrator (Pakar)

* **Dashboard Statistik**: Menyajikan data analitik aktivitas diagnosis secara real-time.
* **Manajemen Data Penyakit dan Gejala**: Fitur CRUD untuk basis pengetahuan sistem.
* **Manajemen Bobot Probabilitas**: Pengelolaan nilai likelihood tanpa perlu memodifikasi kode program.
* **Manajemen Rekomendasi**: Penyesuaian solusi penanganan penyakit.
* **Validasi Riwayat Diagnosis**: Monitoring seluruh data diagnosis dari pengguna.

---

## 6. Panduan Instalasi dan Konfigurasi

### Kebutuhan Sistem

* Python versi 3.10 atau lebih baru
* XAMPP atau Laragon (untuk MySQL Server)
* Library Python: Flask, Flask-SQLAlchemy, Flask-Login, PyMySQL, dan bcrypt

### Langkah Instalasi

1. **Clone Repositori**

```
git clone https://github.com/username-anda/spk-cabai-naive-bayes.git
cd spk-cabai-naive-bayes
```

2. **Membuat Virtual Environment (Opsional)**

```
python -m venv venv
venv\Scripts\activate
```

3. **Install Dependency**

```
pip install -r requirements.txt
```

4. **Konfigurasi Database**

* Buat database dengan nama `spk_cabai_db` melalui phpMyAdmin.
* Import file `spk_cabai_db.sql`.
* Sesuaikan koneksi database pada file `.env dan config.py`

5. **Menjalankan Aplikasi**

```
python app.py
```

Aplikasi dapat diakses melalui `http://localhost:5002/`.

### Akun Pengujian

* **Admin** : username `admin` | password `admin123`
* **Petani** : username `petani_cirebon` | password `petani123`

---

Dikembangkan oleh **Kelompok 4 (TI23B)**, Program Studi Teknik Informatika, Universitas Muhammadiyah Cirebon, sebagai pemenuhan Tugas Mata Kuliah **Metode Penelitian** tahun 2026.
