# Pengumpulan Tugas Visualisasi Data dan Informasi

**Nama:** Mohamad Rizal Rahmadi  
**NIM:** 230660121114  
**Program Studi:** Informatika  
**Dosen:** Irfan Fadil

**Judul:** Palmer Observatory - Multi-DBMS Data Pipeline dan Visualisasi Interaktif Data Penguin Antarktika

## Tautan pengumpulan

1. **Aplikasi web live:** https://palmer-observatory.streamlit.app/
2. **Repositori GitHub:** https://github.com/Jayouss/palmer-observatory
3. **Sumber dataset asli:**
   - https://allisonhorst.github.io/palmerpenguins/
   - https://github.com/allisonhorst/palmerpenguins/blob/main/inst/extdata/penguins.csv
   - https://github.com/allisonhorst/palmerpenguins/blob/main/inst/extdata/penguins_raw.csv
4. **Referensi kode/proyek:**
   - https://github.com/streamlit/streamlit
   - https://github.com/plotly/plotly.py
   - https://github.com/duckdb/duckdb
   - https://github.com/sqlalchemy/sqlalchemy
   - https://github.com/pandas-dev/pandas

## Ringkasan arsitektur

SQLite menyimpan 344 catatan pengukuran penguin; DuckDB menyimpan 344 metadata lapangan. Kueri dijalankan terpisah melalui SQLAlchemy dan konektor Python DuckDB, kemudian digabungkan dengan Pandas pada `observation_id` menggunakan validasi satu-ke-satu. Streamlit menyajikan KPI, lima grafik Plotly, filter interaktif, audit data kosong, tabel, dan unduhan CSV.

Skema SQL kedua DBMS, skrip seed, dependensi, sumber CSV, checksum, pengujian, dan dokumentasi lengkap tersedia dalam repositori. Data penelitian berasal dari periode 2007-2009; analisis bersifat deskriptif dan tidak menaksir populasi penguin liar.
