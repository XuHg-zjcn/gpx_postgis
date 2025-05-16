#!/usr/bin/env sh
# Copyright (C) 2025  Xu Ruijun
# SPDX-License-Identifier: MIT
echo 'This script is Deprecated, advice using `import_gpx.py`'
for file in $1/*.gpx; do
    echo $file
    ogr2ogr -update -append -f "PostgreSQL" PG:"dbname=gps_routes" \
	-nln tracks_data \
	$file \
	-sql 'SELECT
	    name,
	    "desc" AS descript,
	    type,
	    opentracks_trackid AS uuid,
	    CAST(SUBSTR(gpxtrkx_TrackStatsExtension, INSTR(gpxtrkx_TrackStatsExtension, "<gpxtrkx:Distance>")+18) AS REAL) AS distance,
	    CAST(SUBSTR(gpxtrkx_TrackStatsExtension, INSTR(gpxtrkx_TrackStatsExtension, "<gpxtrkx:MovingTime>")+20) AS REAL) AS time_moving,
	    CAST(SUBSTR(gpxtrkx_TrackStatsExtension, INSTR(gpxtrkx_TrackStatsExtension, "<gpxtrkx:MaxSpeed>")+18) AS REAL) AS speed_max,
	    geometry AS track
	    FROM tracks' \
	-dialect SQLITE
    ogr2ogr -update -append -f "PostgreSQL" PG:"dbname=gps_routes" \
        -nln points_data \
        $file \
        -sql 'SELECT
	    geometry AS point,
	    time,
	    ele,
	    track_seg_id,
	    track_seg_point_id,
	    CAST(SUBSTR(gpxtpx_TrackPointExtension, INSTR(gpxtpx_TrackPointExtension, "<gpxtpx:speed>")+14) AS REAL) AS speed,
	    CAST(SUBSTR(gpxtpx_TrackPointExtension, INSTR(gpxtpx_TrackPointExtension, "<opentracks:accuracy_horizontal>")+32) AS REAL) AS acc_horiz
	    FROM track_points' \
	-dialect SQLITE
done
