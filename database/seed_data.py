"""Rebuild reproducible SQLite + DuckDB databases from verified local CSVs."""
from pathlib import Path
import hashlib
import json
import os
import sqlite3
import tempfile
from contextlib import closing
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'


def validate_sources():
    manifest = json.loads((RAW / 'manifest.json').read_text(encoding='utf-8'))
    for name, spec in manifest['files'].items():
        if hashlib.sha256((RAW / name).read_bytes()).hexdigest() != spec['sha256']:
            raise ValueError(f'Checksum sumber berubah: {name}')
    clean = pd.read_csv(RAW / 'penguins.csv')
    raw = pd.read_csv(RAW / 'penguins_raw.csv')
    if len(clean) != 344 or len(raw) != len(clean):
        raise ValueError('Sumber harus memuat 344 observasi berpasangan.')
    # The two upstream files have corresponding rows. Verify this, never assume it.
    pairs = {'island': 'Island', 'bill_length_mm': 'Culmen Length (mm)',
             'bill_depth_mm': 'Culmen Depth (mm)',
             'flipper_length_mm': 'Flipper Length (mm)', 'body_mass_g': 'Body Mass (g)'}
    for a, b in pairs.items():
        pd.testing.assert_series_equal(clean[a], raw[b], check_names=False, check_dtype=False)
    if not clean['species'].eq(raw['Species'].str.split().str[0]).all():
        raise ValueError('Spesies antarsumber tidak selaras.')
    dates = pd.to_datetime(raw['Date Egg'])
    if not clean['year'].eq(dates.dt.year).all():
        raise ValueError('Tahun antarsumber tidak selaras.')
    normalized_sex = raw['Sex'].str.lower().where(raw['Sex'].isin(['MALE', 'FEMALE']))
    pd.testing.assert_series_equal(clean['sex'], normalized_sex, check_names=False)
    return clean, raw


def seed_databases(target=None):
    target = Path(target or os.environ.get('PALMER_DATA_DIR', ROOT / 'data' / 'generated'))
    target.mkdir(parents=True, exist_ok=True)
    clean, raw = validate_sources()
    clean.insert(0, 'observation_id', range(1, len(clean) + 1))
    metadata = raw.rename(columns={
        'studyName': 'study_name', 'Sample Number': 'sample_number',
        'Species': 'species_scientific', 'Island': 'island_source', 'Region': 'region',
        'Stage': 'stage', 'Individual ID': 'individual_id',
        'Clutch Completion': 'clutch_completion', 'Date Egg': 'date_egg',
        'Delta 15 N (o/oo)': 'delta_15n', 'Delta 13 C (o/oo)': 'delta_13c',
        'Comments': 'comments'})
    columns = ['study_name', 'sample_number', 'species_scientific', 'island_source',
               'region', 'stage', 'individual_id', 'clutch_completion', 'date_egg',
               'delta_15n', 'delta_13c', 'comments']
    metadata = metadata[columns].copy()
    metadata.insert(0, 'observation_id', range(1, len(metadata) + 1))
    # Construct fresh files; schema constraints remain intact (no to_sql replace).
    with tempfile.TemporaryDirectory(dir=target) as tmp:
        sqlite_path, duck_path = Path(tmp) / 'measurements.sqlite', Path(tmp) / 'field.duckdb'
        with closing(sqlite3.connect(sqlite_path)) as con:
            with con:
                con.executescript((ROOT / 'database/schema_sqlite.sql').read_text())
                clean.to_sql('measurements', con, if_exists='append', index=False)
        with duckdb.connect(str(duck_path)) as con:
            con.execute((ROOT / 'database/schema_duckdb.sql').read_text())
            con.register('metadata_seed', metadata)
            con.execute('INSERT INTO field_metadata SELECT * FROM metadata_seed')
        os.replace(sqlite_path, target / 'measurements.sqlite')
        os.replace(duck_path, target / 'field.duckdb')
    return target


if __name__ == '__main__':
    print(f'Berhasil: 344 pengukuran SQLite + 344 metadata DuckDB -> {seed_databases()}')
