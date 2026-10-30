# Palmer Observatory - Data Explorer

## Arah visual

Dashboard analitik compact dengan latar slate terang (#F2F4F8), teks navy
(#182842), aksen indigo (#4256BD), dan permukaan putih. Header editorial
menggantikan banner hijau dekoratif. Tipografi sans-serif dipakai konsisten.
Spesies: Adelie indigo, Chinstrap amber, Gentoo teal; scatter juga memakai simbol.

Rujukan: skill UI/UX Pro Max, Data-Dense Dashboard dan Chip Collection Reflow.

## Perbaikan berdasarkan screenshot pengguna

Catatan KPI sebelumnya terpotong di tepi bawah kartu karena styling padding/gap
pada container native tidak sesuai dengan susunan metric dan caption terpisah.
Sekarang empat statistik dirender dalam satu HTML definition list dengan CSS grid.
Label, nilai, dan catatan berada dalam satu kartu berukuran intrinsik; tidak ada
height tetap, overflow tersembunyi, atau posisi absolut untuk teks.

- Empat kolom desktop; dua kolom pada viewport <=1100 px.
- Padding kartu 16x18 px desktop dan 13x12 px ponsel.
- Label 12 px, nilai 27-35 px, catatan 11 px dengan line-height 1.6.
- Catatan dapat membungkus dan menambah tinggi kartu.
- Panel grafik memakai padding/gap native Streamlit; CSS hanya memberi warna dan radius.
- Judul, kategori, dan deskripsi panel disatukan agar urutan vertikalnya alami.
- Kontrol, filter lanjutan, reset, tabel, ekspor, dan dua engine tetap tersedia.
- Focus ring terlihat dan reduced motion dipatuhi; tidak ada animasi dekoratif.

## Pengujian

AppTest membaca nilai pada HTML yang benar-benar dikirim aplikasi. Kasus mencakup
344 observasi awal, filter Gentoo, morfologi lengkap, pilihan kosong, dan reset.
Pengujian pipeline tetap memeriksa integrasi dua DBMS dan validitas sumber.
