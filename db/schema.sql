-- Knowledge base schema, Team 10, Chhattisgarh
-- CS F/U 407 Artificial Intelligence, Class Project
-- Frozen at Phase 1. Changes are recorded in logs/progress_log.md with a reason.
--
-- Four fact tables over two dimension tables, plus a provenance pair.
-- Every fact row carries a foreign key to the document it was extracted from.

PRAGMA foreign_keys = ON;

-- ============================================================ PROVENANCE

CREATE TABLE source (
    source_id         INTEGER PRIMARY KEY,
    source_key        TEXT NOT NULL UNIQUE,   -- matches an id in config/sources.yaml
    source_name       TEXT NOT NULL,
    organisation      TEXT,
    base_url          TEXT,
    modality          TEXT NOT NULL CHECK (modality IN
                        ('api_csv','html_table','digital_pdf','scanned_pdf_ocr')),
    licence           TEXT NOT NULL CHECK (licence IN
                        ('ogl_india','official_unstated','third_party')),
    update_frequency  TEXT
);

CREATE TABLE document (
    document_id            INTEGER PRIMARY KEY,
    source_id              INTEGER NOT NULL REFERENCES source(source_id),
    document_name          TEXT NOT NULL,
    document_url           TEXT NOT NULL,
    page_number            INTEGER,           -- required for the Phase 3 provenance query
    language               TEXT CHECK (language IN ('en','hi','mixed')),
    collected_on           DATE NOT NULL,
    extraction_confidence  TEXT NOT NULL DEFAULT 'medium'
                             CHECK (extraction_confidence IN ('high','medium','low'))
);

-- ============================================================ DIMENSIONS

CREATE TABLE location (
    location_id                INTEGER PRIMARY KEY,
    state                      TEXT NOT NULL DEFAULT 'Chhattisgarh',
    district_code              TEXT NOT NULL,
    district_name              TEXT NOT NULL,
    district_name_hi           TEXT,
    block                      TEXT,
    place_name                 TEXT,
    place_type                 TEXT CHECK (place_type IN
                                 ('mandi','sub_mandi','purchase_centre','godown','society')),
    predecessor_district_code  TEXT   -- maps pre 2022 districts onto the current set
);
CREATE INDEX idx_location_district ON location(district_code);

CREATE TABLE commodity (
    commodity_id            INTEGER PRIMARY KEY,
    commodity_name          TEXT NOT NULL UNIQUE,
    commodity_name_hi       TEXT,
    commodity_group         TEXT CHECK (commodity_group IN
                              ('cereal','pulse','oilseed','vegetable','minor_forest_produce')),
    reporting_unit          TEXT,
    unit_to_quintal_factor  REAL
);

CREATE TABLE commodity_alias (
    alias_id      INTEGER PRIMARY KEY,
    commodity_id  INTEGER NOT NULL REFERENCES commodity(commodity_id),
    alias         TEXT NOT NULL,
    UNIQUE (alias)
);

-- ============================================================ FACTS

CREATE TABLE procurement (
    procurement_id             INTEGER PRIMARY KEY,
    location_id                INTEGER NOT NULL REFERENCES location(location_id),
    commodity_id               INTEGER NOT NULL REFERENCES commodity(commodity_id),
    kms_year                   TEXT NOT NULL,      -- e.g. 2025-26
    season_start_date          DATE,
    season_end_date            DATE,
    quantity_mt                REAL,
    declared_rate_per_quintal  REAL,
    centre_count               INTEGER,
    farmer_count               INTEGER,            -- aggregate only, never identities
    source_id                  INTEGER NOT NULL REFERENCES source(source_id),
    document_id                INTEGER REFERENCES document(document_id)
);

CREATE TABLE prices (
    price_id         INTEGER PRIMARY KEY,
    location_id      INTEGER NOT NULL REFERENCES location(location_id),
    commodity_id     INTEGER NOT NULL REFERENCES commodity(commodity_id),
    price_date       DATE NOT NULL,
    arrivals_tonnes  REAL,
    price_min        REAL,
    price_max        REAL,
    price_modal      REAL,
    source_id        INTEGER NOT NULL REFERENCES source(source_id),
    document_id      INTEGER REFERENCES document(document_id),
    CHECK (price_min IS NULL OR price_modal IS NULL OR price_min <= price_modal),
    CHECK (price_modal IS NULL OR price_max IS NULL OR price_modal <= price_max)
);
CREATE INDEX idx_prices_date ON prices(price_date);

CREATE TABLE storage (
    storage_id     INTEGER PRIMARY KEY,
    location_id    INTEGER NOT NULL REFERENCES location(location_id),
    facility_name  TEXT,
    agency_type    TEXT CHECK (agency_type IN
                     ('state_warehousing','central_warehousing','fci','private_registered')),
    capacity_mt    REAL,
    snapshot_date  DATE NOT NULL,   -- our collection date, not a publication date
    source_id      INTEGER NOT NULL REFERENCES source(source_id),
    document_id    INTEGER REFERENCES document(document_id)
);

CREATE TABLE advisories (
    advisory_id    INTEGER PRIMARY KEY,
    location_id    INTEGER NOT NULL REFERENCES location(location_id),
    commodity_id   INTEGER REFERENCES commodity(commodity_id),   -- nullable
    issue_date     DATE NOT NULL,
    advisory_type  TEXT CHECK (advisory_type IN
                     ('weather','pest','irrigation','sowing','harvest','departmental')),
    language       TEXT,
    summary_text   TEXT,
    source_id      INTEGER NOT NULL REFERENCES source(source_id),
    document_id    INTEGER REFERENCES document(document_id)
);
CREATE INDEX idx_advisories_date ON advisories(issue_date);

-- Optional extension. Built only if the Sentinel-2 indicator work proceeds.
-- Nothing else in the schema depends on it, so it can be dropped cleanly.
CREATE TABLE remote_sensing (
    rs_id             INTEGER PRIMARY KEY,
    location_id       INTEGER NOT NULL REFERENCES location(location_id),
    commodity_id      INTEGER REFERENCES commodity(commodity_id),
    observation_date  DATE NOT NULL,
    ndvi_mean         REAL,
    ndvi_stddev       REAL,
    ndre_mean         REAL,
    evi_mean          REAL,
    cloud_fraction    REAL,
    source_id         INTEGER NOT NULL REFERENCES source(source_id)
);

-- ============================================================ QUARANTINE
-- Rows that fail validation are not discarded. The failure rate is a
-- reportable metric at the Phase 2 and Phase 3 gates.

CREATE TABLE quarantine (
    quarantine_id   INTEGER PRIMARY KEY,
    target_table    TEXT NOT NULL,
    payload_json    TEXT NOT NULL,
    failure_reason  TEXT NOT NULL,
    document_id     INTEGER REFERENCES document(document_id),
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
