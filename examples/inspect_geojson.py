"""第一课示例：读取并观察 GeoJSON。运行方式见 docs/01-first-lesson.md。"""

import json
from pathlib import Path


def main():
    # __file__ 是当前脚本路径；parents[1] 是这个脚本所属的项目目录。
    project_dir = Path(__file__).resolve().parents[1]
    data_path = project_dir / "data" / "places.geojson"

    # 将文件里的 JSON 文本转为 Python 字典和列表。
    text = data_path.read_text(encoding="utf-8")
    collection = json.loads(text)
    features = collection["features"]

    print("数据来源：教学合成数据，不代表真实地点")
    print(f"数据类型：{collection['type']}")
    print(f"要素数量：{len(features)}")

    for feature in features:
        properties = feature["properties"]
        longitude, latitude = feature["geometry"]["coordinates"]
        print(
            f"- {properties['name']} | {properties['category']} | "
            f"经度={longitude}, 纬度={latitude}"
        )


if __name__ == "__main__":
    main()
