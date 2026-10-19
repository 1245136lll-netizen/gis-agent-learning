"""第四课独立示例：类型检查、raise 和 try/except，不依赖练习答案。"""


def check_demo_radius(value):
    # bool 是 int 的子类，因此在数字检查时要单独排除。
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("radius_m 必须是数字")
    if not 0 < value <= 100000:
        raise ValueError("radius_m 必须大于 0，且不超过 100000 米")


def main():
    for value in [1000, 0, -10, "1000", True]:
        try:
            check_demo_radius(value)
            print(f"{value!r}：校验通过")
        except ValueError as error:
            print(f"{value!r}：输入错误：{error}")


if __name__ == "__main__":
    main()
