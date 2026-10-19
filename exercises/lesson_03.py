"""第三课：在项目根目录用 python -m exercises.lesson_03 运行。"""

import json
from pathlib import Path

from exercises.lesson_01 import select_by_category
from exercises.lesson_02 import distance_m


def result_sort_key(record):
    """提供给 sorted 的排序依据：距离优先，同距离按 ID 排序。"""
    return (record["distance_m"], record["id"])


def search_nearby(features, center_lon, center_lat, radius_m, category):
    """查询指定类别和半径内的地点，返回按距离、ID 升序排列的新结果列表。

    本课假定要素结构完整、ID 为字符串、经纬度合法且半径为正数。
    每条结果需要 id、name、category、coordinates、distance_m 五个字段。
    包含距离等于半径的点；距离使用完整精度；不修改传入的要素。
    空输入或没有匹配项时返回 []。参数校验将在第四课添加。
    """
    # TODO 1：调用第一课函数，得到指定类别的候选要素。
    # TODO 2：准备结果列表，遍历候选要素并取出经纬度。
    # TODO 3：调用第二课函数，计算到查询中心的距离。
    # TODO 4：距离 <= radius_m 时，创建结果字典并添加到列表。
    # TODO 5：使用 result_sort_key 对结果排序，返回排序后的列表。
    cate=select_by_category(features,category)
    result=[]
    for feature in cate:
        coordinate=feature["geometry"]["coordinates"]
        dis=distance_m(center_lon,center_lat,coordinate[0],coordinate[1])
        if dis <= radius_m:
            record={
                "id" : feature["id"],
                "name" : feature["properties"]["name"],
                "category" : feature["properties"]["category"],
                "coordinates" : [coordinate[0],coordinate[1]],
                "distance_m" : dis,
            }
            result.append(record)
    ordered=sorted(result,key=result_sort_key)
    return ordered


def main():
    project_dir = Path(__file__).resolve().parents[1]
    data_path = project_dir / "data" / "places.geojson"
    collection = json.loads(data_path.read_text(encoding="utf-8"))

    center_lon = 121.4700
    center_lat = 31.2300
    radius_m = 1000
    category = "hospital"
    try:
        results = search_nearby(
            collection["features"], center_lon, center_lat, radius_m, category
        )
    except NotImplementedError as error:
        print(f"练习待完成：{error}")
        print("请核对第一、二课的函数，并完成 exercises/lesson_03.py。")
        return 1

    print("数据来源：教学合成数据，不代表真实地点")
    print(f"查询类别：{category}；半径：{radius_m} 米")
    print(f"匹配数量：{len(results)}")
    for record in results:
        print(f"{record['id']} | {record['name']} | {record['distance_m']:.1f} 米")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
