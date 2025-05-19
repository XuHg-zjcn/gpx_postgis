#!/usr/bin/env python3
# Copyright (C) 2025  Xu Ruijun
# SPDX-License-Identifier: MIT
import sys
import os
import re
import exiftool
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
    tags = et.get_metadata([path])[0]
    if 'Composite:GPSLongitude' in tags:
        d['lon'] = tags.get('Composite:GPSLongitude')
    if 'Composite:GPSLatitude' in tags:
        d['lat'] = tags.get('Composite:GPSLatitude')
    if 'Composite:GPSAltitude' in tags:
        d['alt'] = tags.get('Composite:GPSAltitude')
    dt = tags.get('Composite:SubSecDateTimeOriginal')
    if dt is not None:
        d['ts'] = datetime.strptime(dt, '%Y:%m:%d %H:%M:%S.%f')

    d['img_width'] = tags.get('File:ImageWidth')
    d['img_height'] = tags.get('File:ImageHeight')
    if 'EXIF:ExposureTime' in tags:
        d['exposure_time'] = tags.get('EXIF:ExposureTime')
    if 'EXIF:FocalLengthIn35mmFormat' in tags:
        d['efl35mm'] = tags.get('EXIF:FocalLengthIn35mmFormat')
    if 'EXIF:ISO' in tags:
        d['iso'] = tags.get('EXIF:ISO')
    if 'EXIF:Make' in tags:
        d['make'] = tags.get('EXIF:Make')
    if 'EXIF:Model' in tags:
        d['model'] = tags.get('EXIF:Model')
    if 'EXIF:GPSImgDirection' in tags:
        d['yaw'] = tags.get('EXIF:GPSImgDirection')
    if 'EXIF:UserComment' in tags:  # exifread库无法正确读取UserComment，改用exiftool
        comment = tags.get('EXIF:UserComment')  # OpenCamera APP的三轴运动信息
        m = re.match(r'^Yaw:(-?\d+\.?\d*),Pitch:(-?\d+\.?\d*),Roll:(-?\d+\.?\d*)$', comment)
        if m is not None:
            d['yaw'] = float(m.group(1))
            d['pitch'] = float(m.group(2))
            d['roll'] = float(m.group(3))
        else:
            print(comment)
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
                path = os.path.join(root, f)
                print(path)
                import_file(path)


def import_dir_or_file(path):
    if(os.path.isdir(path)):
        import_dir(path)
    elif(os.path.isfile(path)):
        import_file(path)


if __name__ == '__main__':
    et = exiftool.ExifToolHelper()
    connection = psycopg2.connect("dbname=gps_routes")
    for path in sys.argv[1:]:
        import_dir_or_file(path)
