import sqlite3
from contextlib import closing
import duckdb
import pandas as pd
import pytest
from database.seed_data import seed_databases, validate_sources
from pipeline import load_integrated, filter_data, METRICS


@pytest.fixture
def integrated(tmp_path):
    seed_databases(tmp_path)
    return tmp_path, load_integrated(tmp_path)


def test_sources_and_full_join(integrated):
    _, df = integrated
    clean, _ = validate_sources()
    assert len(df) == 344
    assert df.observation_id.is_unique
    assert df.study_name.notna().all()
    pd.testing.assert_frame_equal(df[METRICS], clean[METRICS], check_dtype=False)
    assert df.species.value_counts().to_dict() == {'Adelie': 152, 'Gentoo': 124, 'Chinstrap': 68}
    assert df.complete_morphology.sum() == 342
    assert df.sex.eq('unknown').sum() == 11
    assert df.body_mass_g.mean() == pytest.approx(4201.754385964912)


def test_engine_constraints_and_repeatable_seed(integrated):
    folder, before = integrated
    with closing(sqlite3.connect(folder / 'measurements.sqlite')) as con:
        assert con.execute('select count(*) from measurements').fetchone()[0] == 344
        with pytest.raises(sqlite3.IntegrityError):
            con.execute('INSERT INTO measurements (observation_id,species,island,year) VALUES (1,?,?,?)', ('Adelie','Dream',2007))
    with duckdb.connect(str(folder / 'field.duckdb'), read_only=True) as con:
        assert con.execute('select count(*) from field_metadata').fetchone()[0] == 344
    seed_databases(folder)
    pd.testing.assert_frame_equal(before, load_integrated(folder))


def test_filters_and_missing_values(integrated):
    _, df = integrated
    assert filter_data(df, [], ['Dream'], (2007,2009), ['male']).empty
    subset = filter_data(df, ['Adelie'], ['Dream'], (2008,2009), ['female'], True)
    assert not subset.empty
    assert subset.species.eq('Adelie').all()
    assert subset.island.eq('Dream').all()
    assert subset.year.between(2008,2009).all()
    assert subset.sex.eq('female').all()
    assert subset[METRICS].notna().all().all()
    assert df.body_mass_g.isna().sum() == 2


def test_join_rejects_missing_or_wrong_metadata(integrated):
    folder, _ = integrated
    with duckdb.connect(str(folder / 'field.duckdb')) as con:
        con.execute('DELETE FROM field_metadata WHERE observation_id=1')
    with pytest.raises(ValueError, match='metadata tidak lengkap'):
        load_integrated(folder)
    seed_databases(folder)
    with duckdb.connect(str(folder / 'field.duckdb')) as con:
        con.execute("UPDATE field_metadata SET island_source='invalid' WHERE observation_id=1")
    with pytest.raises(ValueError, match='pulau antardatabase'):
        load_integrated(folder)
