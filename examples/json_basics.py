"""独立示例：在项目根目录执行 python examples/json_basics.py。"""

import json


def main():
    request_text = '{"radius_m": 1000, "category": "hospital"}'
    print("收到的 JSON 文本：", request_text)
    print("文本的 Python 类型：", type(request_text).__name__)

    arguments = json.loads(request_text)
    print("解析后的 Python 类型：", type(arguments).__name__)
    print("读取半径：", arguments["radius_m"])

    response = {
        "ok": True,
        "message": "这是 JSON 转换示例",
        "received": arguments,
        "extra": None,
    }
    response_text = json.dumps(
        response, ensure_ascii=False, indent=2, allow_nan=False
    )
    print("把 Python 字典转回 JSON 文本：")
    print(response_text)
    print("再次解析后，ok 字段为：", json.loads(response_text)["ok"])

    broken_text = '{"radius_m": 1000,}'
    try:
        json.loads(broken_text)
    except json.JSONDecodeError as error:
        print(f"JSON 语法错误示例：第 {error.lineno} 行，第 {error.colno} 列")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
