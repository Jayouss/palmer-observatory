CREATE TABLE IF NOT EXISTS field_metadata (
    observation_id INTEGER PRIMARY KEY,
    study_name VARCHAR NOT NULL,
    sample_number INTEGER NOT NULL,
    species_scientific VARCHAR NOT NULL,
    island_source VARCHAR NOT NULL,
    region VARCHAR NOT NULL,
    stage VARCHAR NOT NULL,
    individual_id VARCHAR NOT NULL,
    clutch_completion VARCHAR,
    date_egg DATE,
    delta_15n DOUBLE,
    delta_13c DOUBLE,
    comments VARCHAR
);
