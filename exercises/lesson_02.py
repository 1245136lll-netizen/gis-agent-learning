"""第二课练习：自己封装一个返回米制距离的函数。"""

from pyproj import Geod


def distance_m(lon1, lat1, lon2, lat2):
    """返回两个 WGS 84 经纬度点之间的椭球面测地线距离，单位为米。

    本课输入为合法的经纬度数值，顺序是：经度1、纬度1、经度2、纬度2。
    返回有限、非负的数值，保留计算精度，不在此函数中四舍五入。
    """
    # TODO：选择 WGS84 椭球，调用 inv，并返回三个返回值中的距离。
    geod=Geod(ellps="WGS84")
    forward,back,meter=geod.inv(lon1,lat1,lon2,lat2)
    return meter


def main():
    try:
        meters = distance_m(121.4700, 31.2300, 121.4737, 31.2304)
    except NotImplementedError as error:
        print(f"待完成：{error}。请编辑 exercises/lesson_02.py。")
        return 1

    print(f"查询中心到教学医院甲：{meters:.1f} 米")
    if meters <= 1000:
        print("教学医院甲位于中心的 1000 米范围内")
    else:
        print("教学医院甲位于中心的 1000 米范围外")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
