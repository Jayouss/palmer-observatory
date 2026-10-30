"""Palmer Observatory | Multi-DBMS research dashboard."""
import streamlit as st
import plotly.express as px
from pipeline import load_integrated, filter_data, METRICS, LABELS

st.set_page_config(page_title='Palmer Observatory', page_icon='P', layout='wide')
st.markdown('''<style>
.block-container{padding-top:2rem;max-width:1440px}
h1{letter-spacing:-1.5px;font-weight:750!important}
h2,h3{letter-spacing:-.5px}
[data-testid="stMetric"]{background:white;border:1px solid #DFE7EE;border-radius:14px;padding:18px 22px}
[data-testid="stMetricLabel"]{color:#456075}
.eyebrow{color:#087F8C;font-size:.78rem;letter-spacing:2px;font-weight:700}
.intro{color:#456075;max-width:850px;font-size:1.05rem;line-height:1.65}
.credit{font-size:.8rem;color:#456075;border-top:1px solid #DFE7EE;padding-top:16px;margin-top:24px}
</style>''', unsafe_allow_html=True)
COLORS = {'Adelie': '#087F8C', 'Chinstrap': '#C45B30', 'Gentoo': '#5264BC'}


@st.cache_data(show_spinner='Menghubungkan SQLite dan DuckDB...')
def get_data():
    return load_integrated()


def chart(fig):
    fig.update_layout(font=dict(family='Arial', color='#142D40', size=13),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='white',
                      margin=dict(l=15, r=15, t=25, b=15),
                      legend_title_text='', height=390)
    fig.update_xaxes(gridcolor='#EAF0F5')
    fig.update_yaxes(gridcolor='#EAF0F5')
    st.plotly_chart(fig, width='stretch', config={'displaylogo': False})


try:
    df = get_data()
except Exception:
    st.error('Database belum dapat dimuat. Jalankan python -m database.seed_data, lalu coba kembali.')
    st.stop()

with st.sidebar:
    st.markdown('### PALMER / OBSERVATORY')
    st.caption('Eksplorasi data lapangan Antarktika')
    st.divider()
    st.subheader('Filter observasi')
    species = st.multiselect('Spesies', sorted(df.species.unique()), default=sorted(df.species.unique()))
    islands = st.multiselect('Pulau', sorted(df.island.unique()), default=sorted(df.island.unique()))
    years = st.slider('Rentang tahun', 2007, 2009, (2007, 2009))
    sexes = st.multiselect('Jenis kelamin', ['male', 'female', 'unknown'], default=['male', 'female', 'unknown'],
                           format_func=lambda x: {'male':'Jantan', 'female':'Betina', 'unknown':'Tidak tercatat'}[x])
    complete = st.checkbox('Hanya morfologi lengkap', value=False,
                           help='Keempat ukuran tubuh terisi. Jenis kelamin boleh tidak tercatat.')
    st.divider()
    st.caption('DATA PENELITIAN 2007-2009')
    st.markdown('**SQLite** · Pengukuran individu  \n**DuckDB** · Metadata lapangan  \n**Pandas** · Integrasi satu-ke-satu')
    st.caption('Mohamad Rizal Rahmadi  \n230660121114')

filtered = filter_data(df, species, islands, years, sexes, complete)
st.markdown('<div class="eyebrow">FIELD RESEARCH / ANTARCTICA</div>', unsafe_allow_html=True)
st.title('Palmer Observatory')
st.markdown('<p class="intro">Membaca pola kehidupan penguin melalui data. Telusuri perbedaan ukuran tubuh, komposisi sampel, dan catatan lapangan dari tiga spesies di Kepulauan Palmer.</p>', unsafe_allow_html=True)
st.caption('Visualisasi Data dan Informasi  /  Multi-DBMS Data Pipeline  /  2007-2009')
cols = st.columns(4)
cols[0].metric('Observasi terpilih', f'{len(filtered):,}', help='Jumlah baris penelitian, bukan estimasi populasi.')
cols[1].metric('Spesies teramati', filtered.species.nunique())
cols[2].metric('Rerata massa tubuh', f'{filtered.body_mass_g.mean():,.0f} g' if filtered.body_mass_g.notna().any() else '-')
cols[3].metric('Morfologi lengkap', f'{filtered.complete_morphology.mean():.1%}' if len(filtered) else '-')
st.write('')
overview, detail, methodology = st.tabs(['Eksplorasi visual', 'Data & kualitas', 'Arsitektur & sumber'])

with overview:
    if filtered.empty:
        st.info('Tidak ada observasi untuk kombinasi filter ini. Tambahkan spesies, pulau, tahun, atau jenis kelamin.')
    else:
        left, right = st.columns([1.65, 1])
        with left:
            st.subheader('Bentuk tubuh, pola yang berbeda')
            st.caption('Pilih dua ukuran. Arahkan kursor untuk membaca detail; gunakan zoom untuk menelaah kelompok.')
            a, b = st.columns(2)
            x = a.selectbox('Sumbu horizontal', METRICS, index=2, format_func=LABELS.get)
            y = b.selectbox('Sumbu vertikal', METRICS, index=3, format_func=LABELS.get)
            valid = filtered.dropna(subset=[x, y])
            chart(px.scatter(valid, x=x, y=y, color='species', symbol='species',
                             color_discrete_map=COLORS, labels=LABELS, opacity=.78,
                             hover_data=['observation_id', 'island', 'year', 'sex', 'study_name']))
            st.caption(f'{len(valid)} dari {len(filtered)} observasi memiliki kedua ukuran. Data kosong tidak diimputasi.')
        with right:
            st.subheader('Komposisi sampel')
            st.caption('Jumlah observasi per spesies dalam pilihan filter.')
            counts = filtered.groupby('species').size().reset_index(name='count')
            fig = px.bar(counts, x='species', y='count', color='species', text='count',
                         color_discrete_map=COLORS, labels=LABELS)
            fig.update_layout(showlegend=False)
            chart(fig)
        a, b = st.columns(2)
        with a:
            st.subheader('Sebaran massa tubuh')
            st.caption('Kotak menunjukkan kuartil; titik menunjukkan setiap pengukuran tersedia.')
            chart(px.box(filtered.dropna(subset=['body_mass_g']), x='species', y='body_mass_g',
                         color='species', points='all', color_discrete_map=COLORS, labels=LABELS))
        with b:
            st.subheader('Lokasi pengambilan sampel')
            st.caption('Komposisi spesies di setiap pulau; bukan peta kelimpahan populasi.')
            counts = filtered.groupby(['island', 'species']).size().reset_index(name='count')
            chart(px.bar(counts, x='island', y='count', color='species',
                         barmode='stack', color_discrete_map=COLORS, labels=LABELS))
        st.subheader('Pengamatan dari tahun ke tahun')
        st.caption('Perubahan jumlah sampel mencerminkan pengambilan data, bukan laju pertumbuhan populasi.')
        counts = filtered.groupby(['year', 'species']).size().reset_index(name='count')
        fig = px.bar(counts, x='year', y='count', color='species', barmode='group',
                     color_discrete_map=COLORS, labels=LABELS)
        fig.update_xaxes(dtick=1)
        chart(fig)

with detail:
    st.subheader('Transparansi sampai ke baris data')
    st.caption('Tabel berikut merupakan hasil join SQLite dan DuckDB setelah filter diterapkan.')
    st.download_button('Unduh data terpilih (.csv)', filtered.to_csv(index=False).encode('utf-8-sig'),
                       'palmer_observations.csv', 'text/csv')
    st.dataframe(filtered, hide_index=True, width='stretch')
    st.subheader('Audit nilai kosong')
    quality = filtered[METRICS + ['delta_15n', 'delta_13c']].isna().sum().rename('Nilai kosong').to_frame()
    quality['Terisi'] = len(filtered) - quality['Nilai kosong']
    st.dataframe(quality, width='stretch')
    unknown = int(filtered.sex.eq('unknown').sum())
    st.info(f'{unknown} observasi terpilih memiliki jenis kelamin tidak tercatat. Nilai ini diberi label unknown, tidak ditebak.')

with methodology:
    st.subheader('Dua engine, satu pandangan data')
    st.code('penguins.csv     -> SQLite: measurements ---+\n                                            +-> Pandas merge -> Filter -> Plotly\npenguins_raw.csv -> DuckDB: field_metadata -+', language='text')
    st.markdown('''**Skenario:** tim pemantauan ekologi memisahkan pengukuran individu pada database operasional SQLite dari arsip metadata penelitian pada DuckDB. DuckDB sesuai untuk pembacaan analitik metadata; SQLite menyediakan penyimpanan relasional sederhana untuk pencatatan pengukuran. Untuk ukuran data ini, pemisahan merupakan demonstrasi arsitektur pendidikan, bukan kebutuhan performa.

**Integrasi:** kueri SQLite melalui SQLAlchemy dan kueri DuckDB melalui konektor Python resminya dijalankan terpisah. Pandas melakukan `merge(on="observation_id", validate="one_to_one")`. ID dibuat dari nomor baris sumber setelah kesesuaian spesies, pulau, tahun, jenis kelamin, dan ukuran tubuh diperiksa. Semua 344 observasi harus memperoleh metadata pasangannya.

**Kualitas dan batas interpretasi:** nilai kosong dipertahankan, tanpa imputasi. Rerata memakai nilai tersedia; scatter hanya memakai pasangan ukuran lengkap. Sampel berasal dari penguin dewasa pada tahap satu telur di tiga pulau tahun 2007-2009. Perbandingan bersifat deskriptif; tidak membuktikan sebab-akibat atau jumlah populasi liar.''')
    st.markdown('''#### Data dan referensi
- [Sumber resmi Palmer Penguins](https://allisonhorst.github.io/palmerpenguins/)
- [Dataset pengukuran](https://github.com/allisonhorst/palmerpenguins/blob/main/inst/extdata/penguins.csv)
- [Dataset metadata mentah](https://github.com/allisonhorst/palmerpenguins/blob/main/inst/extdata/penguins_raw.csv)
- [Penelitian Gorman, Williams & Fraser (2014)](https://doi.org/10.1371/journal.pone.0090081)
- [Referensi kode Streamlit](https://github.com/streamlit/streamlit) · [Plotly](https://github.com/plotly/plotly.py) · [DuckDB](https://github.com/duckdb/duckdb) · [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy)

Data dikumpulkan oleh Dr. Kristen Gorman dan Palmer Station LTER; dataset Palmer Penguins oleh Horst, Hill, dan Gorman (2020), lisensi CC0. Implementasi Python proyek ini ditulis untuk tugas ini; repositori di atas merupakan rujukan API dan teknik, bukan klaim salinan kode.''')

st.markdown('<div class="credit">Mohamad Rizal Rahmadi · 230660121114<br>Program Studi Informatika · Visualisasi Data dan Informasi · Dosen Irfan Fadil<br>Sumber: Palmer Penguins / Palmer Station LTER · Data 2007-2009 · CC0</div>', unsafe_allow_html=True)
