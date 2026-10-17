"""第一课行为检查：在项目目录执行 python -m checks.lesson_01。"""

import copy
import json
import unittest
from pathlib import Path

from exercises.lesson_01 import select_by_category


def load_features():
    project_dir = Path(__file__).resolve().parents[1]
    path = project_dir / "data" / "places.geojson"
    return json.loads(path.read_text(encoding="utf-8"))["features"]


class CategoryChecks(unittest.TestCase):
    def test_hospitals_keep_original_order(self):
        """医院应筛出 poi-001、poi-003，并保持原顺序。"""
        result = select_by_category(load_features(), "hospital")
        self.assertIsInstance(result, list)
        self.assertEqual([item["id"] for item in result], ["poi-001", "poi-003"])

    def test_other_category(self):
        """应支持查询公园，不能把 hospital 写死。"""
        result = select_by_category(load_features(), "park")
        self.assertEqual([item["id"] for item in result], ["poi-002"])

    def test_no_match(self):
        """没有学校时应返回空列表。"""
        self.assertEqual(select_by_category(load_features(), "school"), [])

    def test_empty_input(self):
        """输入为空时也应返回空列表。"""
        self.assertEqual(select_by_category([], "hospital"), [])

    def test_input_is_unchanged(self):
        """筛选不能删除原数据或把类别改掉。"""
        features = load_features()
        before = copy.deepcopy(features)
        result = select_by_category(features, "hospital")
        self.assertEqual(features, before)
        self.assertIsNot(result, features)

    def test_uses_supplied_data(self):
        """应处理传入的新数据，不能在函数里重新读取固定文件。"""
        feature = {
            "type": "Feature",
            "id": "new-place",
            "properties": {"name": "新教学点", "category": "library"},
            "geometry": {"type": "Point", "coordinates": [120.0, 30.0]},
        }
        self.assertEqual(select_by_category([feature], "library"), [feature])


def main():
    try:
        select_by_category([], "hospital")
    except NotImplementedError:
        print("练习尚未实现。这是初始状态；请先完成 exercises/lesson_01.py。")
        return 1
    unittest.main(verbosity=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
