#!/usr/bin/env python3
# Copyright (C) 2025  Xu Ruijun
# SPDX-License-Identifier: MIT
import sys
import os
import exifread
import psycopg2
import hashlib
from datetime import datetime


def calc_sha256(path):
    with open(path, 'rb') as f:
        obj = hashlib.sha256()
        while True:
            data = f.read(8192)
            if len(data) == 0:
                return obj.digest()
            obj.update(data)

def get_exif_dict(path):
    d = {}
    with open(path, 'rb') as f:
        tags = exifread.process_file(f)
    lon_dms = tags.get('GPS GPSLongitude')
    if lon_dms is not None:
        lon = lon_dms.values[0]+lon_dms.values[1]/60.0+lon_dms.values[2]/3600.0
        if tags.get('GPS GPSLongitudeRef').values == 'W':
            lon *= -1
        d['lon'] = lon

    lat_dms = tags.get('GPS GPSLatitude')
    if lat_dms is not None:
        lat = lat_dms.values[0]+lat_dms.values[1]/60.0+lat_dms.values[2]/3600.0
        if tags.get('GPS GPSLatitudeRef').values == 'S':
            lat *= -1
        d['lat'] = lat

    alt = tags.get('GPS GPSAltitude')
    if alt is not None:
        altv = alt.values[0]
        if tags.get('GPS GPSAltitudeRef').values[0] == 1:
            altv *= -1
        d['alt'] = float(altv)

    dt = tags.get('Image DateTime')
    if dt is not None:
        dt2 = datetime.strptime(dt.values, '%Y:%m:%d %H:%M:%S')
        d['ts'] = dt2
    return d


def import_file(path):
    cursor = connection.cursor()
    cursor.execute("SELECT 1 FROM photos WHERE path=%s LIMIT 1;", (path,));
    found = cursor.rowcount > 0
    if found:
        cursor.close()
        return None
    sha256 = calc_sha256(path)
    cursor.execute("SELECT 1 FROM photos WHERE sha256=%s LIMIT 1;", (sha256,));
    found = cursor.rowcount > 0
    if found:
        cursor.close()
        return None
    try:
        d = get_exif_dict(path)
    except Exception as e:
        print(e)
        cursor.close()
        return None
    if 'lat' not in d or 'lon' not in d:
        return
    lat = d.pop('lat')
    lon = d.pop('lon')
    if 'alt' in d:
        alt = d.pop('alt')
    else:
        alt = 'Nan'
    d['name'] = os.path.basename(path)
    d['path'] = os.path.abspath(path)
    d['sha256'] = sha256
    keys = []
    values = []
    for k, v in d.items():
        keys.append(k)
        values.append(v)
    keys_str = ','.join(keys)
    placeholders = ','.join(['%s']*len(keys))
    if len(keys) > 0:
        placeholders = ','+placeholders
    cursor.execute(f'''INSERT INTO photos(posit, {keys_str})
    VALUES(ST_MakePoint(%s,%s,%s){placeholders})
    ON CONFLICT DO NOTHING
    RETURNING id;''', [lon,lat,alt]+values)
    cursor.close()
    connection.commit()


def import_dir(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if(f[-4:] == '.jpg'):
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
