"""在项目根目录执行 python -m checks.lesson_03。"""

import copy
import json
from pathlib import Path
import unittest

from exercises.lesson_01 import select_by_category
from exercises.lesson_02 import distance_m
from exercises.lesson_03 import search_nearby


CENTER_LON = 121.4700
CENTER_LAT = 31.2300


def load_features():
    project_dir = Path(__file__).resolve().parents[1]
    path = project_dir / "data" / "places.geojson"
    return json.loads(path.read_text(encoding="utf-8"))["features"]


def query(features, radius_m=1000, category="hospital"):
    return search_nearby(features, CENTER_LON, CENTER_LAT, radius_m, category)


class NearbyChecks(unittest.TestCase):
    def test_hospital_within_1000m(self):
        """一公里内只有教学医院甲，范围内的公园也不能混入。"""
        results = query(load_features())
        self.assertIsInstance(results, list)
        self.assertEqual([item["id"] for item in results], ["poi-001"])

    def test_sorting_within_3000m(self):
        """扩大半径，反转原数据后仍应按距离返回两所医院。"""
        features = list(reversed(load_features()))
        results = query(features, radius_m=3000)
        self.assertEqual([item["id"] for item in results], ["poi-001", "poi-003"])
        self.assertLess(results[0]["distance_m"], results[1]["distance_m"])

    def test_categories_and_empty_results(self):
        """支持不同类别、没有匹配项以及空数据。"""
        parks = query(load_features(), category="park")
        self.assertEqual([item["id"] for item in parks], ["poi-002"])
        self.assertEqual(query(load_features(), category="school"), [])
        self.assertEqual(query(load_features(), radius_m=100), [])
        self.assertEqual(query([]), [])

    def test_radius_boundary_before_rounding(self):
        """包含边界；判断距离时不应先四舍五入。"""
        feature = load_features()[0]
        lon, lat = feature["geometry"]["coordinates"]
        exact = distance_m(CENTER_LON, CENTER_LAT, lon, lat)
        for radius, expected_count in [(exact, 1), (exact - 0.001, 0), (exact + 0.001, 1)]:
            with self.subTest(radius=radius):
                results = query([feature], radius_m=radius)
                self.assertEqual(len(results), expected_count)

    def test_same_distance_sort_by_id(self):
        """同一位置的两个点距离相同，按 ID 升序返回。"""
        first = copy.deepcopy(load_features()[0])
        second = copy.deepcopy(first)
        first["id"] = "test-b"
        second["id"] = "test-a"
        results = query([first, second])
        self.assertEqual([item["id"] for item in results], ["test-a", "test-b"])

    def test_input_is_unchanged(self):
        """查询不应修改原要素或将 distance_m 塞回原数据。"""
        features = load_features()
        before = copy.deepcopy(features)
        results = query(features)
        self.assertEqual(features, before)
        self.assertIsNot(results, features)

    def test_uses_supplied_features(self):
        """处理传入的新地点和新查询中心，不应在函数里读取固定数据文件。"""
        feature = {
            "type": "Feature",
            "id": "new-library",
            "properties": {"name": "教学图书馆", "category": "library"},
            "geometry": {"type": "Point", "coordinates": [120.0, 30.0]},
        }
        results = search_nearby([feature], 120.0, 30.0, 50, "library")
        self.assertEqual([item["id"] for item in results], ["new-library"])
        self.assertAlmostEqual(results[0]["distance_m"], 0, delta=1e-7)

    def test_result_fields_and_full_precision(self):
        """结果字段正确，距离保留数值与完整精度。"""
        feature = load_features()[0]
        results = query([feature])
        record = results[0]
        required = {"id", "name", "category", "coordinates", "distance_m"}
        self.assertTrue(required.issubset(record))
        self.assertEqual(record["id"], feature["id"])
        self.assertEqual(record["name"], feature["properties"]["name"])
        self.assertEqual(record["category"], feature["properties"]["category"])
        self.assertEqual(record["coordinates"], feature["geometry"]["coordinates"])
        self.assertIsInstance(record["distance_m"], (float, int))
        lon, lat = feature["geometry"]["coordinates"]
        expected = distance_m(CENTER_LON, CENTER_LAT, lon, lat)
        self.assertAlmostEqual(record["distance_m"], expected, delta=1e-7)


def main():
    try:
        select_by_category([], "hospital")
        distance_m(0, 0, 0, 0)
        query([])
    except NotImplementedError as error:
        print(f"练习待完成：{error}")
        print("请完成对应课程函数后，再运行本课检查。")
        return 1
    unittest.main(verbosity=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
