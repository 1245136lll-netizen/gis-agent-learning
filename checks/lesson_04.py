"""在项目根目录执行 python -m checks.lesson_04。"""

import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from exercises.lesson_04 import (
    checked_search_nearby,
    validate_features,
    validate_query,
)


def load_features():
    project_dir = Path(__file__).resolve().parents[1]
    path = project_dir / "data" / "places.geojson"
    return json.loads(path.read_text(encoding="utf-8"))["features"]


class QueryChecks(unittest.TestCase):
    def test_valid_values_and_boundaries(self):
        for args in [
            (121.47, 31.23, 1000, "hospital"),
            (-180, -90, 1, "park"),
            (180, 90, 100000, "hospital"),
        ]:
            with self.subTest(args=args):
                self.assertIsNone(validate_query(*args))

    def test_coordinate_ranges(self):
        for lon, lat in [(-180.1, 0), (180.1, 0), (0, -90.1), (0, 90.1)]:
            with self.subTest(lon=lon, lat=lat):
                with self.assertRaises(ValueError) as caught:
                    validate_query(lon, lat, 1000, "hospital")
                self.assertTrue(str(caught.exception).strip())

    def test_radius_range(self):
        for radius in [0, -1, 100000.1]:
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError):
                    validate_query(121.47, 31.23, radius, "hospital")

    def test_numeric_types_and_finite_values(self):
        invalid = [True, False, "1000", None, [], float("nan"), float("inf"), -float("inf")]
        for index in range(3):
            for value in invalid:
                args = [121.47, 31.23, 1000, "hospital"]
                args[index] = value
                with self.subTest(field=index, value=value):
                    with self.assertRaises(ValueError):
                        validate_query(*args)

    def test_supported_category(self):
        for category in [None, 1, [], "", " ", "Hospital", "school"]:
            with self.subTest(category=category):
                with self.assertRaises(ValueError) as caught:
                    validate_query(121.47, 31.23, 1000, category)
                self.assertTrue(str(caught.exception).strip())


class FeatureChecks(unittest.TestCase):
    def test_valid_empty_and_extra_fields(self):
        self.assertIsNone(validate_features([]))
        features = load_features()
        features[0]["extra_note"] = "allowed"
        self.assertIsNone(validate_features(features))

    def test_features_must_be_list(self):
        for data in [None, {}, "features", 1]:
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    validate_features(data)

    def test_feature_object_and_type(self):
        for feature in [None, [], 1, {}, {"type": "Point"}]:
            with self.subTest(feature=feature):
                with self.assertRaises(ValueError):
                    validate_features([feature])

    def test_id(self):
        for value in [None, 1, "", " "]:
            feature = copy.deepcopy(load_features()[0])
            feature["id"] = value
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_features([feature])
        feature = copy.deepcopy(load_features()[0])
        feature.pop("id")
        with self.assertRaises(ValueError):
            validate_features([feature])

    def test_properties_and_required_text(self):
        for value in [None, [], "properties", {}]:
            feature = copy.deepcopy(load_features()[0])
            feature["properties"] = value
            with self.subTest(properties=value):
                with self.assertRaises(ValueError):
                    validate_features([feature])
        feature = copy.deepcopy(load_features()[0])
        feature.pop("properties")
        with self.assertRaises(ValueError):
            validate_features([feature])
        for field in ["name", "category"]:
            for value in [None, 1, "", " "]:
                feature = copy.deepcopy(load_features()[0])
                feature["properties"][field] = value
                with self.subTest(field=field, value=value):
                    with self.assertRaises(ValueError):
                        validate_features([feature])
            feature = copy.deepcopy(load_features()[0])
            feature["properties"].pop(field)
            with self.assertRaises(ValueError):
                validate_features([feature])

    def test_geometry_and_coordinate_shape(self):
        for value in [None, [], {}, {"type": "Point"}, {"type": "LineString", "coordinates": [[0, 0], [1, 1]]}]:
            feature = copy.deepcopy(load_features()[0])
            feature["geometry"] = value
            with self.subTest(geometry=value):
                with self.assertRaises(ValueError):
                    validate_features([feature])
        feature = copy.deepcopy(load_features()[0])
        feature.pop("geometry")
        with self.assertRaises(ValueError):
            validate_features([feature])
        for value in [None, [], [121], [121, 31, 0], "121,31", (121, 31)]:
            feature = copy.deepcopy(load_features()[0])
            feature["geometry"]["coordinates"] = value
            with self.subTest(coordinates=value):
                with self.assertRaises(ValueError):
                    validate_features([feature])

    def test_coordinate_values(self):
        for value in [[181, 31], [121, 91], [True, 31], ["121", 31], [float("nan"), 31], [121, float("inf")]]:
            feature = copy.deepcopy(load_features()[0])
            feature["geometry"]["coordinates"] = value
            with self.subTest(coordinates=value):
                with self.assertRaises(ValueError):
                    validate_features([feature])


class IntegrationChecks(unittest.TestCase):
    def test_valid_query(self):
        results = checked_search_nearby(load_features(), 121.47, 31.23, 1000, "hospital")
        self.assertEqual([item["id"] for item in results], ["poi-001"])
        self.assertAlmostEqual(results[0]["distance_m"], 355.29287867499926, delta=0.01)

    def test_valid_but_empty(self):
        self.assertEqual(checked_search_nearby([], 121.47, 31.23, 1000, "hospital"), [])
        self.assertEqual(checked_search_nearby(load_features(), 121.47, 31.23, 100, "hospital"), [])

    def test_invalid_input_does_not_start_search(self):
        broken = copy.deepcopy(load_features())
        broken[0].pop("properties")
        with patch("exercises.lesson_04.search_nearby") as search:
            with self.assertRaises(ValueError):
                checked_search_nearby(load_features(), 121.47, 31.23, -1, "hospital")
            with self.assertRaises(ValueError):
                checked_search_nearby(broken, 121.47, 31.23, 1000, "hospital")
            search.assert_not_called()

    def test_all_features_checked_and_input_unchanged(self):
        features = load_features()
        before = copy.deepcopy(features)
        checked_search_nearby(features, 121.47, 31.23, 1000, "hospital")
        self.assertEqual(features, before)
        # 公园虽不属于本次查询类别，其错误坐标也必须被报告。
        broken = copy.deepcopy(features)
        broken[1]["geometry"]["coordinates"][0] = 181
        before_broken = copy.deepcopy(broken)
        with self.assertRaises(ValueError):
            checked_search_nearby(broken, 121.47, 31.23, 1000, "hospital")
        self.assertEqual(broken, before_broken)


def main():
    try:
        validate_query(121.47, 31.23, 1000, "hospital")
        validate_features([])
    except NotImplementedError as error:
        print(f"练习待完成：{error}")
        return 1
    unittest.main(verbosity=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
