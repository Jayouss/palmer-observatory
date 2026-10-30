"""Palmer Observatory | Multi-DBMS research dashboard."""
import streamlit as st
import plotly.express as px
from pipeline import load_integrated, filter_data, METRICS, LABELS
from ui import load_styles, hero, statistics, panel_heading, selection_summary, chart, COLORS, SPECIES_ORDER

st.set_page_config(page_title='Palmer Observatory', page_icon='P', layout='wide')
load_styles()


@st.cache_data(show_spinner='Menghubungkan SQLite dan DuckDB...')
def get_data():
    return load_integrated()


try:
    df = get_data()
except Exception:
    st.error('Database belum dapat dimuat. Jalankan python -m database.seed_data, lalu coba kembali.')
    st.stop()

defaults = {'filter_species': sorted(df.species.unique()), 'filter_islands': sorted(df.island.unique()),
            'filter_years': (2007, 2009), 'filter_sexes': ['male', 'female', 'unknown'],
            'filter_complete': False}


def reset_filters():
    for key, value in defaults.items():
        st.session_state[key] = value.copy() if isinstance(value, list) else value


with st.sidebar:
    st.html('<div class="sidebar-brand"><div class="brand-mark" aria-hidden="true">p.</div><div class="brand-name">Palmer<small>Data observatory</small></div></div>')
    species = st.multiselect('Spesies', defaults['filter_species'], default=defaults['filter_species'], key='filter_species')
    islands = st.multiselect('Pulau', defaults['filter_islands'], default=defaults['filter_islands'], key='filter_islands')
    years = st.slider('Rentang tahun', 2007, 2009, (2007, 2009), key='filter_years')
    with st.expander('Filter lanjutan'):
        sexes = st.multiselect('Jenis kelamin', ['male', 'female', 'unknown'], default=defaults['filter_sexes'], key='filter_sexes',
                               format_func=lambda x: {'male':'Jantan', 'female':'Betina', 'unknown':'Tidak tercatat'}[x])
        complete = st.checkbox('Hanya morfologi lengkap', value=False, key='filter_complete',
                               help='Keempat ukuran tubuh terisi. Jenis kelamin boleh tidak tercatat.')
    st.button('Reset semua filter', on_click=reset_filters, width='stretch')
    with st.expander('Tentang dataset'):
        st.caption('344 observasi · 3 spesies · 3 pulau. Data 2007-2009; jumlah sampel bukan estimasi populasi. Sumber: Palmer Penguins, CC0.')
    st.html('<div class="author-mini"><strong>Mohamad Rizal Rahmadi</strong><br>230660121114 · Informatika</div>')

filtered = filter_data(df, species, islands, years, sexes, complete)
hero()
statistics(filtered)
selection_summary(filtered, len(df), species, islands, years, complete)
overview, detail, methodology = st.tabs(['Eksplorasi visual', 'Data & kualitas', 'Arsitektur & sumber'])

with overview:
    if filtered.empty:
        st.info('Tidak ada observasi untuk kombinasi filter ini. Tambahkan spesies, pulau, tahun, atau jenis kelamin.')
    else:
        left, right = st.columns([1.65, 1])
        with left, st.container(border=True, key='scatter-card'):
            panel_heading('01', 'Morfologi', 'Hubungan ukuran tubuh',
                          'Pilih sumbu; arahkan kursor untuk melihat detail observasi.')
            a, b = st.columns(2)
            x = a.selectbox('Sumbu horizontal', METRICS, index=2, format_func=LABELS.get)
            y = b.selectbox('Sumbu vertikal', METRICS, index=3, format_func=LABELS.get)
            valid = filtered.dropna(subset=[x, y])
            fig = px.scatter(valid, x=x, y=y, color='species', symbol='species',
                             color_discrete_map=COLORS, category_orders={'species': SPECIES_ORDER},
                             labels=LABELS, opacity=.8,
                             hover_data=['observation_id', 'island', 'year', 'sex', 'study_name'])
            fig.update_traces(marker=dict(size=8, line=dict(width=.6, color='white')))
            chart(fig, height=300)
            st.caption(f'{len(valid)} dari {len(filtered)} observasi memiliki kedua ukuran. Data kosong tidak diimputasi.')
        with right, st.container(border=True, key='composition-card'):
            panel_heading('02', 'Komposisi', 'Sampel per spesies',
                          'Jumlah observasi dalam filter aktif.')
            counts = filtered.groupby('species').size().reset_index(name='count')
            counts['share'] = counts['count'] / len(filtered) * 100
            fig = px.bar(counts, x='count', y='species', color='species', text='count', orientation='h',
                         color_discrete_map=COLORS, labels=LABELS,
                         category_orders={'species': SPECIES_ORDER}, custom_data=['share'])
            fig.update_layout(showlegend=False)
            fig.update_xaxes(range=[0, counts['count'].max() * 1.2])
            fig.update_traces(textposition='outside', cliponaxis=False,
                              hovertemplate='%{y}<br>%{x} observasi<br>%{customdata[0]:.1f}% dari pilihan<extra></extra>')
            chart(fig, height=350)
            st.caption('Jumlah sampel penelitian, bukan estimasi populasi.')
        a, b = st.columns(2)
        with a, st.container(border=True, key='mass-card'):
            panel_heading('03', 'Distribusi', 'Sebaran massa tubuh',
                          'Kotak menunjukkan kuartil; titik memperlihatkan setiap pengukuran tersedia.')
            fig = px.box(filtered.dropna(subset=['body_mass_g']), x='species', y='body_mass_g',
                         color='species', points='all', color_discrete_map=COLORS,
                         category_orders={'species': SPECIES_ORDER}, labels=LABELS)
            fig.update_layout(showlegend=False)
            fig.update_traces(marker=dict(size=4, opacity=.45), line=dict(width=1.6))
            chart(fig)
        with b, st.container(border=True, key='islands-card'):
            panel_heading('04', 'Lokasi', 'Komposisi sampel per pulau',
                          'Telusuri sebaran sampel antarspesies di lokasi pengambilan data.')
            counts = filtered.groupby(['island', 'species']).size().reset_index(name='count')
            chart(px.bar(counts, x='island', y='count', color='species',
                         barmode='stack', color_discrete_map=COLORS,
                         category_orders={'species': SPECIES_ORDER}, labels=LABELS))
        with st.container(border=True, key='year-card'):
            panel_heading('05', 'Waktu', 'Sampel per tahun',
                          'Perbandingan jumlah sampel penelitian. Perubahan ini tidak menunjukkan laju pertumbuhan populasi.')
            counts = filtered.groupby(['year', 'species']).size().reset_index(name='count')
            fig = px.bar(counts, x='year', y='count', color='species', barmode='group',
                         color_discrete_map=COLORS, category_orders={'species': SPECIES_ORDER}, labels=LABELS)
            fig.update_xaxes(dtick=1)
            chart(fig, height=270)

with detail:
    with st.container(border=True, key='table-card'):
        panel_heading('01', 'Data terintegrasi', 'Transparansi sampai ke baris data',
                      'Telusuri hasil integrasi kedua database. Unduhan CSV mengikuti semua filter aktif.')
        st.download_button('Unduh data terpilih (.csv)', filtered.to_csv(index=False).encode('utf-8-sig'),
                           'palmer_observations.csv', 'text/csv')
        st.dataframe(filtered, hide_index=True, width='stretch')
    with st.container(border=True, key='quality-card'):
        panel_heading('02', 'Kualitas data', 'Apa yang belum tercatat?',
                      'Nilai kosong dipertahankan agar keterbatasan pengukuran tetap terlihat.')
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

st.html('<footer class="credit"><div><strong>Palmer Observatory</strong><br>Visualisasi Data dan Informasi · Informatika · Dosen Irfan Fadil</div><div>Mohamad Rizal Rahmadi · 230660121114<br>Palmer Penguins / Palmer Station LTER · 2007-2009 · CC0</div></footer>')
