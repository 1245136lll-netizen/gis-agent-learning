"""在项目根目录执行 python -m checks.lesson_05。"""

import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from exercises.lesson_05 import parse_tool_arguments, run_search_tool


def load_features():
    path = Path(__file__).resolve().parents[1] / "data" / "places.geojson"
    return json.loads(path.read_text(encoding="utf-8"))["features"]


def valid_arguments():
    return {
        "center_lon": 121.47,
        "center_lat": 31.23,
        "radius_m": 1000,
        "category": "hospital",
    }


class ArgumentChecks(unittest.TestCase):
    def test_valid_arguments_return_new_dict(self):
        arguments = valid_arguments()
        before = copy.deepcopy(arguments)
        parsed = parse_tool_arguments(arguments)
        self.assertIsInstance(parsed, dict)
        self.assertEqual(parsed, before)
        self.assertIsNot(parsed, arguments)
        parsed["radius_m"] = 1
        self.assertEqual(arguments, before)

    def test_outer_type(self):
        for value in [None, [], "{}", 1, True]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as caught:
                    parse_tool_arguments(value)
                self.assertTrue(str(caught.exception).strip())

    def test_missing_fields(self):
        for field in valid_arguments():
            arguments = valid_arguments()
            arguments.pop(field)
            with self.subTest(field=field):
                with self.assertRaises(ValueError) as caught:
                    parse_tool_arguments(arguments)
                self.assertTrue(str(caught.exception).strip())

    def test_extra_fields(self):
        for field in ["limit", "radius", 1]:
            arguments = valid_arguments()
            arguments[field] = 5
            with self.subTest(field=field):
                with self.assertRaises(ValueError) as caught:
                    parse_tool_arguments(arguments)
                self.assertTrue(str(caught.exception).strip())


class ToolChecks(unittest.TestCase):
    def assert_input_error(self, response):
        self.assertIsInstance(response, dict)
        self.assertEqual(set(response), {"ok", "error"})
        self.assertIs(response["ok"], False)
        self.assertIsInstance(response["error"], dict)
        self.assertEqual(set(response["error"]), {"code", "message"})
        self.assertEqual(response["error"]["code"], "INVALID_INPUT")
        self.assertIsInstance(response["error"]["message"], str)
        self.assertTrue(response["error"]["message"].strip())

    def test_valid_query(self):
        arguments = valid_arguments()
        response = run_search_tool(load_features(), arguments)
        self.assertEqual(set(response), {"ok", "query", "count", "results"})
        self.assertIs(response["ok"], True)
        self.assertEqual(response["query"], arguments)
        self.assertEqual(response["count"], 1)
        self.assertEqual([item["id"] for item in response["results"]], ["poi-001"])
        record = response["results"][0]
        self.assertEqual(record["name"], "教学医院甲")
        self.assertEqual(record["category"], "hospital")
        self.assertEqual(record["coordinates"], [121.4737, 31.2304])
        self.assertAlmostEqual(record["distance_m"], 355.29287867499926, delta=0.000001)

    def test_park_query(self):
        arguments = valid_arguments()
        arguments["category"] = "park"
        response = run_search_tool(load_features(), arguments)
        self.assertIs(response["ok"], True)
        self.assertEqual(response["count"], 1)
        self.assertEqual([item["id"] for item in response["results"]], ["poi-002"])

    def test_valid_but_empty(self):
        small_radius = valid_arguments()
        small_radius["radius_m"] = 100
        for features, arguments in [(load_features(), small_radius), ([], valid_arguments())]:
            with self.subTest(arguments=arguments, features=features):
                response = run_search_tool(features, arguments)
                self.assertIs(response["ok"], True)
                self.assertEqual(response["count"], 0)
                self.assertEqual(response["results"], [])
                self.assertNotIn("error", response)

    def test_argument_errors(self):
        extra = valid_arguments()
        extra["limit"] = 5
        for arguments in [None, [], "{}", {}, extra]:
            with self.subTest(arguments=arguments):
                self.assert_input_error(run_search_tool(load_features(), arguments))

    def test_query_ranges_and_category(self):
        invalid = [
            ("center_lon", 181), ("center_lat", -91),
            ("radius_m", 0), ("radius_m", -1), ("radius_m", 100001),
            ("category", "school"), ("category", "Hospital"),
            ("category", None), ("category", []),
        ]
        for field, value in invalid:
            arguments = valid_arguments()
            arguments[field] = value
            with self.subTest(field=field, value=value):
                self.assert_input_error(run_search_tool(load_features(), arguments))

    def test_numeric_types_and_finite_values(self):
        invalid = [True, False, "1000", None, [], float("nan"), float("inf"), -float("inf")]
        for field in ("center_lon", "center_lat", "radius_m"):
            for value in invalid:
                arguments = valid_arguments()
                arguments[field] = value
                with self.subTest(field=field, value=value):
                    self.assert_input_error(run_search_tool(load_features(), arguments))

    def test_feature_errors(self):
        missing_properties = load_features()
        missing_properties[0].pop("properties")
        invalid_park = load_features()
        invalid_park[1]["geometry"]["coordinates"][0] = 181
        for features in [None, {}, [None], missing_properties, invalid_park]:
            with self.subTest(features=features):
                self.assert_input_error(run_search_tool(features, valid_arguments()))

    def test_bad_structure_does_not_call_search(self):
        with patch("exercises.lesson_05.checked_search_nearby") as search:
            for arguments in [[], {}, dict(valid_arguments(), limit=5)]:
                self.assert_input_error(run_search_tool(load_features(), arguments))
            search.assert_not_called()

    def test_bad_values_and_data_do_not_start_calculation(self):
        broken = load_features()
        broken[0].pop("properties")
        with patch("exercises.lesson_04.search_nearby") as search:
            self.assert_input_error(run_search_tool(load_features(), dict(valid_arguments(), radius_m=-1)))
            self.assert_input_error(run_search_tool(broken, valid_arguments()))
            search.assert_not_called()

    def test_error_serialization(self):
        for arguments in [None, {}, dict(valid_arguments(), radius_m=float("nan"))]:
            with self.subTest(arguments=arguments):
                response = run_search_tool(load_features(), arguments)
                self.assert_input_error(response)
                text = json.dumps(response, ensure_ascii=False, allow_nan=False)
                self.assertEqual(json.loads(text), response)

    def test_success_does_not_change_inputs(self):
        features = load_features()
        arguments = valid_arguments()
        before_features = copy.deepcopy(features)
        before_arguments = copy.deepcopy(arguments)
        response = run_search_tool(features, arguments)
        self.assertIs(response["ok"], True)
        self.assertEqual(features, before_features)
        self.assertEqual(arguments, before_arguments)
        self.assertIsNot(response["query"], arguments)
        response["query"]["radius_m"] = 1
        self.assertEqual(arguments, before_arguments)

    def test_failure_does_not_change_inputs(self):
        for field, value in [("radius_m", -1), ("limit", 5)]:
            features = load_features()
            arguments = valid_arguments()
            arguments[field] = value
            before_features = copy.deepcopy(features)
            before_arguments = copy.deepcopy(arguments)
            self.assert_input_error(run_search_tool(features, arguments))
            self.assertEqual(features, before_features)
            self.assertEqual(arguments, before_arguments)

    def test_programming_errors_propagate(self):
        for error in [TypeError("示例程序错误"), KeyError("示例缺失键"), NotImplementedError("示例未完成")]:
            with self.subTest(error=type(error).__name__):
                with patch("exercises.lesson_05.checked_search_nearby", side_effect=error):
                    with self.assertRaises(type(error)):
                        run_search_tool(load_features(), valid_arguments())

    def test_json_round_trip(self):
        request_text = '{"center_lon":121.47,"center_lat":31.23,"radius_m":1000,"category":"hospital"}'
        arguments = json.loads(request_text)
        response = run_search_tool(load_features(), arguments)
        text = json.dumps(response, ensure_ascii=False, indent=2, allow_nan=False)
        self.assertIn("教学医院甲", text)
        decoded = json.loads(text)
        self.assertEqual(decoded, response)
        self.assertIs(decoded["ok"], True)
        self.assertEqual(decoded["count"], len(decoded["results"]))


def main():
    try:
        parse_tool_arguments(valid_arguments())
        run_search_tool([], valid_arguments())
    except NotImplementedError as error:
        print(f"练习待完成：{error}")
        print("请先确认第四课通过检查，再完成第五课的两个函数。")
        return 1
    unittest.main(verbosity=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
