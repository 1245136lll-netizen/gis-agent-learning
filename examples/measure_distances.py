"""第二课示例：测量查询中心到各教学点的 WGS 84 椭球面距离。"""

import json
from pathlib import Path

from pyproj import Geod


def main():
    project_dir = Path(__file__).resolve().parents[1]
    data_path = project_dir / "data" / "places.geojson"
    collection = json.loads(data_path.read_text(encoding="utf-8"))

    center_lon = 121.4700
    center_lat = 31.2300
    geod = Geod(ellps="WGS84")

    print("数据来源：教学合成数据，不代表真实地点")
    print(f"查询中心：经度={center_lon}，纬度={center_lat}")
    print("距离类型：WGS 84 椭球面测地线距离；单位：米")

    for feature in collection["features"]:
        longitude, latitude = feature["geometry"]["coordinates"]
        forward_azimuth, back_azimuth, meters = geod.inv(
            center_lon, center_lat, longitude, latitude
        )
        properties = feature["properties"]
        print(
            f"- {properties['name']} | {properties['category']} | "
            f"距离={meters:.1f} 米"
        )


if __name__ == "__main__":
    main()
