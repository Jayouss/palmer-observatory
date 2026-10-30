"""Presentation components; no data access or data transformation here."""
from html import escape
import base64
from pathlib import Path
import streamlit as st

COLORS = {'Adelie': '#19786D', 'Chinstrap': '#B6613D', 'Gentoo': '#6677B0'}
SPECIES_ORDER = ['Adelie', 'Chinstrap', 'Gentoo']


def load_styles():
    css = (Path(__file__).parent / 'assets/dashboard.css').read_text(encoding='utf-8')
    st.html(f'<style>{css}</style>')


def hero():
    art = base64.b64encode((Path(__file__).parent / 'assets/contours.svg').read_bytes()).decode('ascii')
    st.html(f'''<section class="hero" aria-label="Palmer Observatory">
<div class="hero-kicker">DATA PENGUIN ANTARKTIKA / 2007-2009</div>
<h1>Palmer <em>Observatory.</em></h1>
<p class="hero-description">Eksplorasi morfologi dan sampel penelitian dari tiga pulau di Kepulauan Palmer.</p>
<img class="hero-art" src="data:image/svg+xml;base64,{art}" alt="" aria-hidden="true">
</section>''')


def panel_heading(number, category, title, description):
    st.html(f'<div class="panel-heading"><span class="panel-index">{escape(number)} / {escape(category)}</span><h3>{escape(title)}</h3></div>')
    st.caption(description)


def selection_summary(filtered, total, species, islands, years, complete):
    labels = [f'{len(species)} spesies', f'{len(islands)} pulau', f'{years[0]}-{years[1]}']
    if complete:
        labels.append('Morfologi lengkap')
    badges = ''.join(f'<span>{escape(label)}</span>' for label in labels)
    st.html(f'<div class="selection-summary"><strong>{len(filtered)} dari {total} observasi</strong>{badges}</div>')


def chart(fig, height=290):
    fig.update_layout(
        font=dict(family='Arial, sans-serif', color='#34574D', size=11),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=12, t=34 if fig.layout.showlegend is not False else 16, b=38), height=height,
        legend=dict(title_text='', orientation='h', yanchor='bottom', y=1.02,
                    xanchor='left', x=0, font=dict(size=11)),
        hoverlabel=dict(bgcolor='#FFFFFF', font_size=12, font_color='#142E31'),
        modebar=dict(orientation='h', bgcolor='rgba(255,255,255,.9)', color='#50665F'),
        bargap=.38, dragmode='zoom')
    fig.update_xaxes(gridcolor='#E9EEEA', zeroline=False, linecolor='#DCE4DF',
                     title_font=dict(size=11), automargin=True, tickfont=dict(size=10))
    fig.update_yaxes(gridcolor='#E9EEEA', zeroline=False, title_font=dict(size=11),
                     automargin=True, tickfont=dict(size=10))
    st.plotly_chart(fig, width='stretch', config={
        'displaylogo': False, 'scrollZoom': False, 'responsive': True,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d']})
