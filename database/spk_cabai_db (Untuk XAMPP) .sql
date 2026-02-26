-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3307
-- Generation Time: Feb 26, 2026 at 02:46 PM
-- Server version: 8.0.30
-- PHP Version: 8.3.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `spk_cabai_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `bobot_probabilitas`
--

CREATE TABLE `bobot_probabilitas` (
  `id` int NOT NULL,
  `penyakit_id` int DEFAULT NULL,
  `gejala_id` int DEFAULT NULL,
  `nilai_probabilitas` decimal(5,4) NOT NULL,
  `fase_pertumbuhan` enum('vegetatif','generatif') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bobot_probabilitas`
--

INSERT INTO `bobot_probabilitas` (`id`, `penyakit_id`, `gejala_id`, `nilai_probabilitas`, `fase_pertumbuhan`) VALUES
(1, 1, 1, 0.9000, 'vegetatif'),
(2, 2, 3, 0.8500, 'vegetatif'),
(3, 2, 4, 0.9500, 'generatif'),
(4, 3, 5, 0.9500, 'generatif'),
(5, 4, 6, 0.9000, 'vegetatif');

-- --------------------------------------------------------

--
-- Table structure for table `diagnosa`
--

CREATE TABLE `diagnosa` (
  `id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `penyakit_id` int DEFAULT NULL,
  `gejala_input` text,
  `fase_input` enum('vegetatif','generatif') DEFAULT NULL,
  `nilai_posterior` decimal(5,4) DEFAULT NULL,
  `tanggal_diagnosa` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `diagnosa`
--

INSERT INTO `diagnosa` (`id`, `user_id`, `penyakit_id`, `gejala_input`, `fase_input`, `nilai_posterior`, `tanggal_diagnosa`) VALUES
(1, 2, 2, '[3, 4, 5, 2]', 'vegetatif', 0.8095, '2026-02-25 20:06:36');

-- --------------------------------------------------------

--
-- Table structure for table `gejala`
--

CREATE TABLE `gejala` (
  `id` int NOT NULL,
  `kode_gejala` varchar(10) NOT NULL,
  `nama_gejala` text NOT NULL,
  `kategori_organ` enum('daun','batang','buah','akar') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `gejala`
--

INSERT INTO `gejala` (`id`, `kode_gejala`, `nama_gejala`, `kategori_organ`, `created_at`) VALUES
(1, 'G01', 'Daun menguning dan layu mulai dari bagian bawah', 'daun', '2026-02-26 02:05:05'),
(2, 'G02', 'Jaringan vaskuler akar dan batang menjadi coklat', 'akar', '2026-02-26 02:05:05'),
(3, 'G03', 'Tanaman layu mendadak namun daun tetap hijau', 'daun', '2026-02-26 02:05:05'),
(4, 'G04', 'Keluar cairan keruh koloni bakteri dari potongan batang', 'batang', '2026-02-26 02:05:05'),
(5, 'G05', 'Bercak mengkilap, terbenam, dan berair pada buah', 'buah', '2026-02-26 02:05:05'),
(6, 'G06', 'Tulang daun menebal dan daun menggulung ke atas', 'daun', '2026-02-26 02:05:05');

-- --------------------------------------------------------

--
-- Table structure for table `penyakit`
--

CREATE TABLE `penyakit` (
  `id` int NOT NULL,
  `kode_penyakit` varchar(10) NOT NULL,
  `nama_penyakit` varchar(100) NOT NULL,
  `prior_probability` decimal(5,4) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `penyakit`
--

INSERT INTO `penyakit` (`id`, `kode_penyakit`, `nama_penyakit`, `prior_probability`, `created_at`) VALUES
(1, 'P01', 'Layu Fusarium', 0.2000, '2026-02-26 02:05:05'),
(2, 'P02', 'Layu Bakteri (Ralstonia)', 0.2000, '2026-02-26 02:05:05'),
(3, 'P03', 'Busuk Buah Antraknosa', 0.2500, '2026-02-26 02:05:05'),
(4, 'P04', 'Virus Kuning (Gemini Virus)', 0.2000, '2026-02-26 02:05:05'),
(5, 'P05', 'Bercak Daun Cercospora', 0.1500, '2026-02-26 02:05:05');

-- --------------------------------------------------------

--
-- Table structure for table `rekomendasi`
--

CREATE TABLE `rekomendasi` (
  `id` int NOT NULL,
  `penyakit_id` int DEFAULT NULL,
  `prosedur_penanganan` text NOT NULL,
  `sumber_literatur` varchar(100) DEFAULT 'Meilin (2014)'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `rekomendasi`
--

INSERT INTO `rekomendasi` (`id`, `penyakit_id`, `prosedur_penanganan`, `sumber_literatur`) VALUES
(1, 1, 'Manfaatkan agen antagonis Trichoderma spp. pada pupuk dasar.', 'Meilin (2014)'),
(2, 2, 'Lakukan pergiliran tanaman dan cabut tanaman yang terinfeksi.', 'Meilin (2014)'),
(3, 3, 'Musnahkan buah terserang dan hindari penggunaan alat semprot terkontaminasi.', 'Meilin (2014)'),
(4, 4, 'Kendalikan vektor kutu kebul (Bemisia tabaci) dengan predator alami.', 'Meilin (2014)'),
(5, 5, 'Perbaiki drainase lahan dan musnahkan sisa tanaman sakit.', 'Meilin (2014)');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `nama_lengkap` varchar(100) DEFAULT NULL,
  `role` enum('admin','petani') NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `nama_lengkap`, `role`, `created_at`) VALUES
(1, 'admin', 'admin123', 'Yafa Emayda', 'admin', '2026-02-26 02:05:05'),
(2, 'petani_cirebon', 'petani123', 'Faulan Petani', 'petani', '2026-02-26 02:05:05');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bobot_probabilitas`
--
ALTER TABLE `bobot_probabilitas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `penyakit_id` (`penyakit_id`),
  ADD KEY `gejala_id` (`gejala_id`);

--
-- Indexes for table `diagnosa`
--
ALTER TABLE `diagnosa`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `penyakit_id` (`penyakit_id`);

--
-- Indexes for table `gejala`
--
ALTER TABLE `gejala`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `kode_gejala` (`kode_gejala`);

--
-- Indexes for table `penyakit`
--
ALTER TABLE `penyakit`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `kode_penyakit` (`kode_penyakit`);

--
-- Indexes for table `rekomendasi`
--
ALTER TABLE `rekomendasi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `penyakit_id` (`penyakit_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bobot_probabilitas`
--
ALTER TABLE `bobot_probabilitas`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `diagnosa`
--
ALTER TABLE `diagnosa`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `gejala`
--
ALTER TABLE `gejala`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `penyakit`
--
ALTER TABLE `penyakit`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `rekomendasi`
--
ALTER TABLE `rekomendasi`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bobot_probabilitas`
--
ALTER TABLE `bobot_probabilitas`
  ADD CONSTRAINT `bobot_probabilitas_ibfk_1` FOREIGN KEY (`penyakit_id`) REFERENCES `penyakit` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `bobot_probabilitas_ibfk_2` FOREIGN KEY (`gejala_id`) REFERENCES `gejala` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `diagnosa`
--
ALTER TABLE `diagnosa`
  ADD CONSTRAINT `diagnosa_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `diagnosa_ibfk_2` FOREIGN KEY (`penyakit_id`) REFERENCES `penyakit` (`id`);

--
-- Constraints for table `rekomendasi`
--
ALTER TABLE `rekomendasi`
  ADD CONSTRAINT `rekomendasi_ibfk_1` FOREIGN KEY (`penyakit_id`) REFERENCES `penyakit` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
