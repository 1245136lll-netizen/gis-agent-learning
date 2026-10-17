"""练习：按类别筛选 GeoJSON 要素。只需修改 select_by_category 函数。"""

import json
from pathlib import Path


def select_by_category(features, category):
    """返回类别与 category 完全相同的要素，保持原顺序，不修改输入列表。

    features 是要素列表，单个要素的类别在 feature["properties"]["category"]。
    本课假定每个要素都有该字段；空列表和没有匹配项时返回空列表。
    """
    # TODO：创建结果列表，遍历 features，检查类别，收集匹配项，返回结果。
    # 提示与需要的 Python 语法见 docs/01-first-lesson.md。
    result=[]
    for feature in features:
        if feature["properties"]["category"]==category:
            result.append(feature)
    return result

def main():
    project_dir = Path(__file__).resolve().parents[1]
    data_path = project_dir / "data" / "places.geojson"
    collection = json.loads(data_path.read_text(encoding="utf-8"))

    try:
        hospitals = select_by_category(collection["features"], "hospital")
    except NotImplementedError as error:
        print(f"待完成：{error}。打开 exercises/lesson_01.py 编辑。")
        return 1

    print(f"医院数量：{len(hospitals)}")
    for feature in hospitals:
        print(feature["properties"]["name"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
