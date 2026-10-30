# Palmer Observatory - arah visual

Dashboard riset web dengan panel modular, identitas editorial, dan kepadatan sedang.
Rujukan: skill UI/UX Pro Max (Data-Dense Dashboard, Bento Box Grid, Chip Collection Reflow)
dan routing Design ke arsitektur token. Pola pemasaran Enterprise Gateway dari pencarian
awal tidak diterapkan karena tidak sesuai dengan dashboard riset.

- Latar stone #F4F6F3; permukaan putih; teks deep forest #142E31.
- Aksen teal #176961; mint #C8E6D5 hanya di atas panel gelap.
- Serif Georgia untuk aksen judul; sans-serif bawaan untuk data dan kontrol.
- Token primitive, semantic, dan component berada di assets/dashboard.css.
- Audit compact: header satu baris, tanpa blok metadata dekoratif berulang.
- Panel: radius 12 px, padding 16 px desktop / 12 px ponsel, gap isi 6 px.
- Grafik 270-350 px, legenda di atas plot, satuan dan tooltip tetap tersedia.
- Judul panel dan nomor disatukan; informasi dataset tambahan dapat dilipat.
- KPI: empat kolom di desktop, dua kolom pada area sempit; label boleh membungkus.
- Filter: nilai jamak boleh membungkus, reset memakai callback state native Streamlit.
- Grafik: urutan dan warna spesies tetap; legenda horizontal; simbol scatter membedakan
  spesies selain warna; satuan pada sumbu; data kosong dijelaskan, tidak diimputasi.
- Semua kontrol tetap native dan dapat dioperasikan lewat keyboard; focus ring terlihat.
- Tanpa animasi dekoratif; prefers-reduced-motion dipatuhi.
- Ilustrasi orbit di panel pembuka bersifat dekoratif dan aria-hidden, bukan peta ilmiah.
