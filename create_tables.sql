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
    uuid UUID,
    name TEXT,
    descript TEXT,
    type TEXT,
    track GEOMETRY(MULTILINESTRING),
    point_start GEOMETRY(Point, 4326),
    point_end GEOMETRY(Point, 4326),
    bbox GEOMETRY(Polygon, 4326),
    ts_start TIMESTAMP WITH TIME ZONE,
    ts_end TIMESTAMP WITH TIME ZONE,
    time_moving FLOAT,
    distance FLOAT,
    speed_max FLOAT
);
