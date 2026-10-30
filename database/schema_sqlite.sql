CREATE TABLE IF NOT EXISTS measurements (
    observation_id INTEGER PRIMARY KEY,
    species TEXT NOT NULL,
    island TEXT NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 2007 AND 2009),
    sex TEXT CHECK (sex IN ('male', 'female') OR sex IS NULL),
    bill_length_mm REAL CHECK (bill_length_mm > 0),
    bill_depth_mm REAL CHECK (bill_depth_mm > 0),
    flipper_length_mm REAL CHECK (flipper_length_mm > 0),
    body_mass_g REAL CHECK (body_mass_g > 0)
);
