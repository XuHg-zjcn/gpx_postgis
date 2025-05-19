# GPX文件导入PostGIS数据库工具

## 背景
我为了绘制OpenStreetMap，记录了大量GPS轨迹，是用Android上的OpenTracks或OSMTracker APP记录的。（部分精选数据已上传OSM网站[我的GPS轨迹](https://www.openstreetmap.org/user/%E7%A7%91%E6%8A%80%E9%AA%8F%E9%A9%AC/traces))

我经常在QGIS中查看这些轨迹，如果在QGIS里打开全部轨迹文件，QGIS会卡死甚至崩溃，一个个文件手工打开很麻烦。
我觉得应该将数据储存到数据库中，选了PostgreSQL+PostGIS数据库。

## 使用方法
1. 安装依赖 PostgreSQL, PostGIS, GDAL
2. `createdb -E utf8 gps_routes`创建数据库
3. `psql -d gps_routes -f create_tables.sql`
4. `python import_gpx.py /path-to-gpx-dir`选择一些GPX文件或文件夹，文件夹则会递归导入GPX文件，目前只支持OpenTracks的轨迹
5. QGIS浏览器面板中创建PostGIS连接，名称随便起一个，服务不用填，如果用本机的数据库不用填主机，数据库填`gps_routes`，点击确定
6. PostGIS下该连接的public里能看到各种数据，双击就能加载

该方法没有验证过，是按照自己操作的大致过程编写，可能有误

## 现有功能
- 导入OpenTracks记录的GPS轨迹
- 避免重复导入(按OpenTracks的UUID)
- 导入照片的GPS位置、拍摄角度、焦距、设备型号等信息

## 待实现功能
- 用Python程序计算`tracks_data`表中空白字段
- 导入其他程序记录的GPX轨迹
- 记录一张照片（进行真实曝光的）的多个版本，同一版本多个路径
- 使用其他数据库如SQLite+SpatiaLite

## 一些技巧
```sh
ogrinfo -ro -al input.gpx #查看GDAL解析的GPX文件字段
```

## 版权和许可证
Copyright (C) 2025  Xu Ruijun  
SPDX-License-Identifier: MIT  
