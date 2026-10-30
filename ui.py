"""Presentation components; no data access or data transformation here."""
from html import escape
from pathlib import Path
import streamlit as st

COLORS = {'Adelie': '#4256BD', 'Chinstrap': '#C37938', 'Gentoo': '#278C8A'}
SPECIES_ORDER = ['Adelie', 'Chinstrap', 'Gentoo']


def load_styles():
    css = (Path(__file__).parent / 'assets/dashboard.css').read_text(encoding='utf-8')
    st.html(f'<style>{css}</style>')


def hero():
    st.html('''<header class="page-heading"><div><div class="page-kicker">PALMER / DATA EXPLORER</div>
<h1>Penguin, dalam data.</h1>
<p>Bandingkan ukuran tubuh dan sampel tiga spesies penguin di Kepulauan Palmer.</p></div>
<div class="archive-stamp"><strong>Arsip 2007-2009</strong>Palmer Penguins · CC0</div></header>''')


def statistics(filtered):
    """Keep each value and its note in one intrinsic-height HTML card."""
    mass = f'{filtered.body_mass_g.mean():,.0f} g' if filtered.body_mass_g.notna().any() else '-'
    quality = f'{filtered.complete_morphology.mean():.1%}' if len(filtered) else '-'
    items = [
        ('observations', 'Observasi terpilih', str(len(filtered)), 'dari 344 catatan lapangan', '#4256BD'),
        ('species', 'Spesies teramati', str(filtered.species.nunique()), f'di {filtered.island.nunique()} pulau terpilih', '#278C8A'),
        ('mass', 'Rerata massa tubuh', mass, f'{filtered.body_mass_g.notna().sum()} pengukuran tersedia', '#C37938'),
        ('quality', 'Morfologi lengkap', quality, f'{filtered.complete_morphology.sum()} catatan lengkap', '#7B6CB2'),
    ]
    cards = ''.join(f'<div class="stat-card" style="--stat-color:{color}"><dt>{escape(label)}</dt>'
                    f'<dd><strong data-stat="{key}">{escape(value)}</strong>'
                    f'<span class="stat-note">{escape(note)}</span></dd></div>'
                    for key, label, value, note, color in items)
    st.html(f'<dl class="stats-grid" aria-label="Ringkasan observasi">{cards}</dl>')


def panel_heading(number, category, title, description):
    st.html(f'<div class="panel-heading"><span class="panel-index">{escape(number)} / {escape(category)}</span>'
            f'<h3>{escape(title)}</h3><p>{escape(description)}</p></div>')


def selection_summary(filtered, total, species, islands, years, complete):
    labels = [f'{len(species)} spesies', f'{len(islands)} pulau', f'{years[0]}-{years[1]}']
    if complete:
        labels.append('Morfologi lengkap')
    badges = ''.join(f'<span>{escape(label)}</span>' for label in labels)
    st.html(f'<div class="selection-summary"><strong>{len(filtered)} dari {total} observasi</strong>{badges}</div>')


def chart(fig, height=290):
    fig.update_layout(
        font=dict(family='Arial, sans-serif', color='#52627B', size=12),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=12, t=34 if fig.layout.showlegend is not False else 16, b=38), height=height,
        legend=dict(title_text='', orientation='h', yanchor='bottom', y=1.02,
                    xanchor='left', x=0, font=dict(size=11)),
        hoverlabel=dict(bgcolor='#FFFFFF', font_size=12, font_color='#182842'),
        modebar=dict(orientation='h', bgcolor='rgba(255,255,255,.9)', color='#52627B'),
        bargap=.38, dragmode='zoom')
    fig.update_xaxes(gridcolor='#EBEEF5', zeroline=False, linecolor='#DCE2ED',
                     title_font=dict(size=11), automargin=True, tickfont=dict(size=10))
    fig.update_yaxes(gridcolor='#EBEEF5', zeroline=False, title_font=dict(size=11),
                     automargin=True, tickfont=dict(size=10))
    st.plotly_chart(fig, width='stretch', config={
        'displaylogo': False, 'scrollZoom': False, 'responsive': True,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
