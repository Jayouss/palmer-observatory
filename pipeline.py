"""Query each DBMS independently, then integrate at the application layer."""
from pathlib import Path
import os
import duckdb
import pandas as pd
from sqlalchemy import create_engine, text
from database.seed_data import ROOT, seed_databases

METRICS = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
LABELS = {'bill_length_mm': 'Panjang paruh (mm)', 'bill_depth_mm': 'Kedalaman paruh (mm)',
          'flipper_length_mm': 'Panjang sirip (mm)', 'body_mass_g': 'Massa tubuh (g)',
          'species': 'Spesies', 'island': 'Pulau', 'year': 'Tahun', 'sex': 'Jenis kelamin',
          'study_name': 'Studi', 'observation_id': 'ID observasi', 'count': 'Jumlah observasi'}


def load_integrated(target=None):
    folder = Path(target or os.environ.get('PALMER_DATA_DIR', ROOT / 'data/generated'))
    if not all((folder / f).is_file() for f in ['measurements.sqlite', 'field.duckdb']):
        seed_databases(folder)
    engine = create_engine('sqlite:///' + (folder / 'measurements.sqlite').as_posix())
    try:
        with engine.connect() as con:
            measurements = pd.read_sql_query(text('SELECT * FROM measurements ORDER BY observation_id'), con)
    finally:
        engine.dispose()
    with duckdb.connect(str(folder / 'field.duckdb'), read_only=True) as con:
        metadata = con.execute('SELECT * FROM field_metadata ORDER BY observation_id').fetchdf()
    merged = measurements.merge(metadata, on='observation_id', how='left',
                                validate='one_to_one', indicator=True)
    if len(merged) != len(measurements) or not merged['_merge'].eq('both').all():
        raise ValueError('Integrasi gagal: metadata tidak lengkap atau duplikat.')
    if not merged['island'].eq(merged['island_source']).all():
        raise ValueError('Integrasi gagal: pulau antardatabase berbeda.')
    merged = merged.drop(columns=['_merge', 'island_source'])
    merged['sex'] = merged['sex'].fillna('unknown')
    merged['complete_morphology'] = merged[METRICS].notna().all(axis=1)
    return merged


def filter_data(df, species, islands, years, sexes, complete_only=False):
    mask = (df.species.isin(species) & df.island.isin(islands)
            & df.year.between(*years) & df.sex.isin(sexes))
    if complete_only:
        mask &= df.complete_morphology
    return df.loc[mask].copy()
