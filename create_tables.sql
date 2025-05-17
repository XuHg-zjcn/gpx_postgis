/*
 * Copyright (C) 2025  Xu Ruijun
 * SPDX-License-Identifier: MIT
 */
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE points_data (
    id SERIAL PRIMARY KEY,
    track_id INTEGER,
    track_seg_id INTEGER,
    track_seg_point_id INTEGER,
    point GEOMETRY(Point, 4326) NOT NULL,
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    ele FLOAT,
    speed FLOAT,
    course FLOAT,
    acc_horiz FLOAT,
    acc_vert FLOAT
);

CREATE TABLE tracks_data (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE,
    name TEXT,
    descript TEXT,
    type TEXT,
    track GEOMETRY(MULTILINESTRING, 4326),
    point_start GEOMETRY(Point, 4326),
    point_end GEOMETRY(Point, 4326),
    bbox GEOMETRY(Polygon, 4326),
    ts_start TIMESTAMP WITH TIME ZONE,
    ts_end TIMESTAMP WITH TIME ZONE,
    time_moving FLOAT,
    distance FLOAT,
    speed_max FLOAT
);

CREATE TABLE photos (
    id SERIAL PRIMARY KEY,
    name TEXT,
    posit GEOMETRY(PointZ, 4326),
    ts TIMESTAMP,
    yaw FLOAT,
    pitch FLOAT,
    roll FLOAT,
    path TEXT UNIQUE NOT NULL,
    sha256 BYTEA UNIQUE NOT NULL
);

/* 用于QGIS中ImportPhotos插件的兼容格式 */
CREATE VIEW qgis_importphotos AS
SELECT id,
    name,
    posit,
    ST_Z(posit) AS altitude,
    ts AS timestamp,
    path,
    TO_CHAR(ts, 'YYYY-MM-DD') AS date,
    TO_CHAR(ts, 'HH24:MI:SS') AS time
FROM photos;
