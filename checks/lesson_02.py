"""在项目根目录执行 python -m checks.lesson_02。"""

import math
import unittest

from exercises.lesson_02 import distance_m


class DistanceChecks(unittest.TestCase):
    def test_same_point(self):
        """相同点距离为零。"""
        self.assertAlmostEqual(distance_m(121.47, 31.23, 121.47, 31.23), 0, delta=1e-7)

    def test_one_degree_on_equator(self):
        """独立参考：赤道一度弧长等于 2πa/360，WGS 84 的 a=6378137 米。"""
        expected = 2 * math.pi * 6378137 / 360
        self.assertAlmostEqual(distance_m(0, 0, 1, 0), expected, delta=0.01)

    def test_reverse_direction(self):
        """A 到 B 与 B 到 A 的距离相同。"""
        forward = distance_m(121.47, 31.23, 121.49, 31.24)
        backward = distance_m(121.49, 31.24, 121.47, 31.23)
        self.assertAlmostEqual(forward, backward, delta=1e-6)

    def test_longitude_degree_changes_with_latitude(self):
        """相同经度差在不同纬度的距离不同，不能统一乘以固定米数。"""
        equator = distance_m(0, 0, 1, 0)
        latitude_60 = distance_m(0, 60, 1, 60)
        self.assertGreater(latitude_60, equator * 0.4)
        self.assertLess(latitude_60, equator * 0.6)

    def test_teaching_hospitals(self):
        """检查真实课程坐标的单位、经纬度顺序和半径判断。"""
        near = distance_m(121.4700, 31.2300, 121.4737, 31.2304)
        far = distance_m(121.4700, 31.2300, 121.4900, 31.2400)
        self.assertTrue(math.isfinite(near))
        self.assertTrue(math.isfinite(far))
        self.assertGreater(near, 300)
        self.assertLess(near, 400)
        self.assertGreater(far, 2000)
        self.assertLess(far, 2400)
        self.assertLessEqual(near, 1000)
        self.assertGreater(far, 1000)

    def test_crossing_antimeridian(self):
        """赤道上跨越 ±180 度，经度相差 0.2 度的短距离。"""
        expected = 2 * math.pi * 6378137 * 0.2 / 360
        self.assertAlmostEqual(distance_m(179.9, 0, -179.9, 0), expected, delta=0.01)


def main():
    try:
        distance_m(0, 0, 0, 0)
    except NotImplementedError:
        print("第二课练习尚未实现，请先完成 exercises/lesson_02.py。")
        return 1
    unittest.main(verbosity=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
