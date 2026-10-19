"""第四课：在项目根目录执行 python -m exercises.lesson_04。"""

import copy
import json
import math
from pathlib import Path

from exercises.lesson_03 import search_nearby


SUPPORTED_CATEGORIES = ("hospital", "park")


def require_number(value, field_name):
    """已提供：只接受有限的 Python int/float，排除 bool 和数字字符串。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} 必须是数字")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{field_name} 必须是有限数值")

def validate_coordinates(coordinates, field_name):
    """已提供：检查本项目的二维 WGS 84 [经度, 纬度] 列表。"""
    if not isinstance(coordinates, list) or len(coordinates) != 2:
        raise ValueError(f"{field_name} 必须是包含经度和纬度的两元素列表")
    longitude, latitude = coordinates
    require_number(longitude, f"{field_name}[0]（经度）")
    require_number(latitude, f"{field_name}[1]（纬度）")
    if not -180 <= longitude <= 180:
        raise ValueError(f"{field_name}[0] 经度必须在 -180 到 180 之间")
    if not -90 <= latitude <= 90:
        raise ValueError(f"{field_name}[1] 纬度必须在 -90 到 90 之间")


def validate_query(center_lon, center_lat, radius_m, category):
    """待实现：校验查询参数；成功返回 None，失败抛出有说明的 ValueError。

    经纬度合法且有限；半径为有限数值，0 < radius_m <= 100000；
    category 为字符串，且属于 SUPPORTED_CATEGORIES。不自动转换输入。
    """
    # TODO：复用 validate_coordinates 检查中心点。
    # TODO：复用 require_number 检查半径，再检查半径范围。
    # TODO：检查 category 的类型和允许值。
    validate_coordinates([center_lon,center_lat],"查询中心")
    require_number(radius_m,"查询半径")
    if not 0 < radius_m <= 100000:
        raise ValueError(f"半径范围超出限制")

    if not isinstance(category,str) or category not in SUPPORTED_CATEGORIES:
        raise ValueError(f"category类型错误")

def validate_features(features):
    """待实现：校验本项目的 Point 要素列表，不修改输入。

    features 为列表，允许 []；每项为 type=Feature 的字典。
    id 为非空字符串；properties 为字典，其 name/category 为非空字符串。
    geometry 为 type=Point 的字典；coordinates 使用已提供的坐标检查。
    允许额外字段。本课不检查 ID 唯一性，不实现通用 GeoJSON 标准校验。
    成功返回 None，发现任何错误时抛出有说明的 ValueError。
    """
    # TODO：检查 features 类型，再遍历每个要素。
    # TODO：先确认每层对象的类型，再读取下一层字段。
    # TODO：检查 type、id、properties、name、category、geometry。
    # TODO：复用 validate_coordinates 检查每项坐标。
    if not isinstance(features,list):
        raise ValueError(f"该要素不为列表")
    for feature in features:
        if not isinstance(feature,dict):
            raise ValueError(f"feature属性必须为字典")
        type = feature.get("type")
        if type != "Feature":
            raise ValueError(f"类型错误")
        if not isinstance(feature.get("id"),str) or not feature.get("id").strip():
            raise ValueError(f"id必须为非空字符串")
        properties=feature.get("properties")
        if not isinstance(properties,dict):
            raise ValueError(f"properties属性必须为字典")
        name = properties.get("name")
        category = properties.get("category")
        if not isinstance(name,str) or not name.strip():
            raise ValueError(f"属性名称必须为非空字符串")
        if not isinstance(category,str) or not category.strip():
            raise ValueError(f"属性类型不为非空字符串")
        geometry=feature.get("geometry")
        if not isinstance(geometry,dict):
            raise ValueError(f"地理属性必须为字典")
        type2 = feature["geometry"].get("type")
        if type2 !="Point":
            raise ValueError(f"地理属性类型必须为点要素")

        validate_coordinates(geometry.get("coordinates"),"坐标值")


def checked_search_nearby(features, center_lon, center_lat, radius_m, category):
    """已提供：先校验全部输入，再复用第三课查询；错误向上传递。"""
    validate_query(center_lon, center_lat, radius_m, category)
    validate_features(features)
    return search_nearby(features, center_lon, center_lat, radius_m, category)


def main():
    project_dir = Path(__file__).resolve().parents[1]
    path = project_dir / "data" / "places.geojson"
    features = json.loads(path.read_text(encoding="utf-8"))["features"]
    broken = copy.deepcopy(features)
    broken[0].pop("properties")
    cases = [
        ("合法查询", features, 1000),
        ("合法查询但无匹配", features, 100),
        ("负数半径", features, -100),
        ("要素缺少 properties", broken, 1000),
    ]
    for label, data, radius in cases:
        print(f"--- {label} ---")
        try:
            results = checked_search_nearby(data, 121.4700, 31.2300, radius, "hospital")
            print(f"查询成功，匹配数量：{len(results)}")
        except NotImplementedError as error:
            print(f"练习待完成：{error}")
            return 1
        except ValueError as error:
            print(f"输入错误：{error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
