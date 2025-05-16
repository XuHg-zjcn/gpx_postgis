#!/usr/bin/env python3
# Copyright (C) 2025  Xu Ruijun
# SPDX-License-Identifier: MIT
import sys
import os
import psycopg2
from osgeo import ogr
import re


def get_track_dict(feat):
    if feat.geometry().IsEmpty():
        return None  # 跳过空白数据
    d = {}
    if(hasattr(feat, 'opentracks_trackid')):
        uuid = getattr(feat, 'opentracks_trackid')
        d['uuid'] = uuid
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM tracks_data WHERE uuid=%s LIMIT 1;", (uuid,))
        found = cursor.rowcount > 0
        cursor.close()
        if found:
            print('skip')
            return None
    if(hasattr(feat, 'gpxtrkx_TrackStatsExtension')):
        ext = getattr(feat, 'gpxtrkx_TrackStatsExtension')
        m = re.match(r'<gpxtrkx:Distance>(\d+.?\d*)</gpxtrkx:Distance>', ext)
        if(m != None):
            d['distance'] = float(m.group(1))
        m = re.match(r'<gpxtrkx:MovingTime>(\d+.?\d*)</gpxtrkx:MovingTime>', ext)
        if(m != None):
            d['time_moving'] = float(m.group(1))
        m = re.match(r'<gpxtrkx:MaxSpeed>(\d+.?\d*)</gpxtrkx:MaxSpeed>', ext)
        if(m != None):
            d['speed_max'] = float(m.group(1))
    d['track'] = feat.geometry().ExportToWkb()
    d['name'] = feat.name
    d['descript'] = feat.desc
    d['type'] = feat.type
    return d


def import_file(path):
    print(path)
    ds = ogr.Open(path)
    tracks = ds.GetLayerByName('tracks')
    n_tracks = tracks.GetFeatureCount()
    for i in range(n_tracks):
        feat = tracks.GetFeature(i)
        d = get_track_dict(feat)
        if d is None:
            continue
        keys = []
        values = []
        for k, v in d.items():
            keys.append(k)
            values.append(v)
        keys_str = ','.join(keys)
        placeholders = ','.join(['%s']*len(keys))
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO tracks_data({keys_str}) VALUES({placeholders}) RETURNING id;', values)
        _id = None
        for res_id, in cursor:
            _id = res_id
        if _id is None:
            cursor.close()
            continue  # 插入track失败
        else:
            print(_id)
        sql = f'''SELECT
        geometry AS point,
        time,
        ele,
        track_seg_id,
        track_seg_point_id,
        CAST(SUBSTR(gpxtpx_TrackPointExtension, INSTR(gpxtpx_TrackPointExtension, "<gpxtpx:speed>")+14) AS REAL) AS speed,
        CAST(SUBSTR(gpxtpx_TrackPointExtension, INSTR(gpxtpx_TrackPointExtension, "<opentracks:accuracy_horizontal>")+32) AS REAL) AS acc_horiz
        FROM track_points
        WHERE track_fid={i};'''
        data = list(map(lambda x:(x.geometry().ExportToWkb(), i)+tuple(x), ds.ExecuteSQL(sql, dialect='SQLITE')))
        cursor.executemany('INSERT INTO points_data(point,track_id,time,ele,track_seg_id,track_seg_point_id,speed,acc_horiz) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);', data)
        cursor.close()
    connection.commit()


def import_dir(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if(f[-4:] == '.gpx'):
                import_file(os.path.join(root, f))


def import_dir_or_file(path):
    if(os.path.isdir(path)):
        import_dir(path)
    elif(os.path.isfile(path)):
        import_file(path)


if __name__ == '__main__':
    connection = psycopg2.connect("dbname=gps_routes")
    for path in sys.argv[1:]:
        import_dir_or_file(path)
